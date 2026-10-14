#!/usr/bin/env bash
# GitHub release metadata cache. No asset or credential is stored in this cache.

ride_github_header() {
  local header_file=$1 header_name=$2
  awk -F: -v name="$header_name" '
    tolower($1) == name { sub(/^[[:space:]]*/, "", $2); gsub(/\r/, "", $2); value=$2 }
    END { print value }
  ' "$header_file"
}

ride_github_prune_cache() {
  local directory=$1 now=$2 file expiry retrieved oldest oldest_time modified
  local -a files
  shopt -s nullglob
  files=("$directory"/release-*.json)
  for file in "${files[@]}"; do
    expiry=$(jq -r '.provenance.expiresAtEpoch // 0' "$file" 2>/dev/null) || expiry=0
    retrieved=$(jq -r '.provenance.retrievedAtEpoch // 0' "$file" 2>/dev/null) || retrieved=0
    if [[ ! "$expiry" =~ ^[0-9]+$ || ! "$retrieved" =~ ^[0-9]+$ || "$expiry" -le "$now" || "$retrieved" -gt "$now" ]]; then
      rm -f "$file"
    fi
  done
  files=("$directory"/release-*.json)
  while (( ${#files[@]} > 64 )); do
    oldest=${files[0]}
    oldest_time=$(stat -c %Y "$oldest")
    for file in "${files[@]:1}"; do
      modified=$(stat -c %Y "$file")
      if (( modified < oldest_time )); then oldest=$file; oldest_time=$modified; fi
    done
    rm -f "$oldest"
    files=("$directory"/release-*.json)
  done
  shopt -u nullglob
}

ride_github_latest() {
  local repository=$1 url mode key auth_key directory cache_file backoff_file now until
  local body headers code bytes remaining reset retry deadline token=
  [[ "$repository" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || ride_die "invalid GitHub repository"
  ride_require_command curl
  ride_require_command sha256sum
  url="https://api.github.com/repos/$repository/releases/latest"
  mode=Anonymous
  if [[ -n "${RIDE_GITHUB_TOKEN:-}" ]]; then
    [[ "$RIDE_GITHUB_TOKEN" =~ ^[A-Za-z0-9_]+$ ]] || ride_die "invalid GitHub token format"
    token=$RIDE_GITHUB_TOKEN
    mode=PAT
  fi
  directory="$(ride_cache_dir)/github"
  umask 077
  mkdir -p "$directory" || ride_die "cannot create GitHub cache"
  chmod 700 "$directory"
  # The key separates credential contexts without persisting a token or its raw hash.
  key=$(printf '%s|%s|%s' "$url" "$mode" "$token" | sha256sum | cut -d' ' -f1)
  auth_key=$(printf '%s|%s' "$mode" "$token" | sha256sum | cut -d' ' -f1)
  cache_file="$directory/release-$key.json"
  backoff_file="$directory/backoff-$auth_key"
  now=$(date +%s)
  if [[ -f "$cache_file" ]] && jq -e --argjson now "$now" \
      '.provenance.retrievedAtEpoch <= $now and .provenance.expiresAtEpoch > $now and (.release.tag_name | type == "string")' \
      "$cache_file" >/dev/null 2>&1; then
    jq '.provenance.acquisitionKind = "DiskCache"' "$cache_file"
    return
  fi
  if [[ -r "$backoff_file" ]]; then
    read -r until < "$backoff_file" || until=0
    if [[ "$until" =~ ^[0-9]+$ && "$until" -gt "$now" ]]; then
      ride_die "GitHub release discovery deferred by rate limit until epoch $until"
    fi
  fi
  body=$(mktemp "$directory/body.XXXXXXXX") || ride_die "cannot create GitHub response file"
  headers=$(mktemp "$directory/headers.XXXXXXXX") || { rm -f "$body"; ride_die "cannot create GitHub header file"; }
  if [[ -n "$token" ]]; then
    if ! code=$(printf 'header = "Authorization: Bearer %s"\n' "$token" |
      curl --config - --silent --show-error --max-time 30 --proto '=https' --tlsv1.2 \
        --header 'Accept: application/vnd.github+json' --header 'User-Agent: ride-linux-v3' \
        --dump-header "$headers" --output "$body" --write-out '%{http_code}' "$url"); then
      rm -f "$body" "$headers"
      ride_die "GitHub release request failed for $repository"
    fi
  elif ! code=$(curl --silent --show-error --max-time 30 --proto '=https' --tlsv1.2 \
      --header 'Accept: application/vnd.github+json' --header 'User-Agent: ride-linux-v3' \
      --dump-header "$headers" --output "$body" --write-out '%{http_code}' "$url"); then
    rm -f "$body" "$headers"
    ride_die "GitHub release request failed for $repository"
  fi
  remaining=$(ride_github_header "$headers" x-ratelimit-remaining)
  reset=$(ride_github_header "$headers" x-ratelimit-reset)
  retry=$(ride_github_header "$headers" retry-after)
  if [[ "$code" == 429 || ( "$code" == 403 && ( "$remaining" == 0 || -n "$retry" ) ) ]]; then
    deadline=$((now + 60))
    if [[ "$retry" =~ ^[0-9]+$ && $((now + retry)) -gt $deadline ]]; then deadline=$((now + retry)); fi
    if [[ "$reset" =~ ^[0-9]+$ && $((reset + 1)) -gt $deadline ]]; then deadline=$((reset + 1)); fi
    printf '%s\n' "$deadline" > "$backoff_file"
    rm -f "$body" "$headers"
    ride_die "GitHub release discovery deferred by rate limit until epoch $deadline"
  fi
  if [[ "$code" != 200 ]]; then
    rm -f "$body" "$headers"
    ride_die "GitHub release request returned HTTP $code for $repository"
  fi
  bytes=$(wc -c < "$body")
  if (( bytes > 2097152 )) || ! jq -e '
    (.tag_name | type == "string" and length > 0) and
    (.assets | type == "array") and
    all(.assets[]; (.name | type == "string") and (.browser_download_url | type == "string"))
  ' "$body" >/dev/null; then
    rm -f "$body" "$headers"
    ride_die "invalid or oversized GitHub release metadata for $repository"
  fi
  local temp
  temp=$(mktemp "$directory/release.XXXXXXXX") || ride_die "cannot create GitHub cache entry"
  jq -n --slurpfile release "$body" --arg url "$url" --arg mode "$mode" \
    --arg remaining "$remaining" --arg reset "$reset" --argjson now "$now" \
    '{release:$release[0], provenance:{apiUri:$url, acquisitionKind:"Network", authenticationMode:$mode,
      retrievedAtEpoch:$now, expiresAtEpoch:($now + 300), remainingQuota:(if $remaining == "" then null else $remaining end),
      resetAtEpoch:(if $reset == "" then null else $reset end)}}' > "$temp" || ride_die "cannot serialize GitHub response"
  chmod 600 "$temp"
  mv -f "$temp" "$cache_file"
  rm -f "$body" "$headers"
  if [[ "$remaining" == 0 && "$reset" =~ ^[0-9]+$ ]]; then printf '%s\n' "$((reset + 1))" > "$backoff_file"; fi
  ride_github_prune_cache "$directory" "$now"
  cat "$cache_file"
}

ride_github_download_asset() {
  local entry=$1 destination=$2 repository suffix maximum metadata count asset name url digest size tag
  local target temporary actual sidecar sidecar_temp product
  repository=$(jq -r '.githubRepository' <<< "$entry")
  suffix=$(jq -r '.assetSuffix' <<< "$entry")
  maximum=$(jq -r '.maxBytes' <<< "$entry")
  metadata=$(ride_github_latest "$repository")
  count=$(jq --arg suffix "$suffix" '[.release.assets[] | select(.name | endswith($suffix))] | length' <<< "$metadata")
  [[ "$count" == 1 ]] || ride_die "expected one Linux asset ending $suffix; found $count"
  asset=$(jq -c --arg suffix "$suffix" '.release.assets[] | select(.name | endswith($suffix))' <<< "$metadata")
  name=$(jq -r '.name' <<< "$asset")
  url=$(jq -r '.browser_download_url' <<< "$asset")
  digest=$(jq -r '.digest // empty' <<< "$asset")
  size=$(jq -r '.size' <<< "$asset")
  tag=$(jq -r '.release.tag_name' <<< "$metadata")
  [[ "$name" =~ ^[A-Za-z0-9._-]+$ && "$tag" =~ ^[A-Za-z0-9._-]+$ ]] || ride_die "invalid GitHub asset name or tag"
  [[ "$url" == "https://github.com/$repository/releases/download/$tag/$name" ]] || ride_die "unexpected publisher asset URL"
  [[ "$digest" =~ ^sha256:[0-9a-fA-F]{64}$ ]] || ride_die "publisher API provides no SHA-256 digest for $name"
  [[ "$size" =~ ^[0-9]+$ && "$size" -le "$maximum" ]] || ride_die "asset exceeds declared size limit"
  ride_require_command curl
  ride_require_command sha256sum
  umask 077
  mkdir -p "$destination/$tag"
  target="$destination/$tag/$name"
  temporary=$(mktemp "$destination/$tag/.download.XXXXXXXX") || ride_die "cannot create asset temporary file"
  if ! curl --fail --silent --show-error --location --max-time 300 --proto '=https' --tlsv1.2 \
      --proto-redir '=https' --max-filesize "$maximum" --output "$temporary" "$url"; then
    rm -f "$temporary"
    ride_die "asset download failed: $name"
  fi
  actual=$(sha256sum "$temporary" | cut -d' ' -f1)
  if [[ "$actual" != "${digest#sha256:}" ]]; then
    rm -f "$temporary"
    ride_die "asset SHA-256 differs from GitHub release metadata: $name"
  fi
  if [[ -e "$target" ]]; then
    if [[ -f "$target" && ! -L "$target" && "$(sha256sum "$target" | cut -d' ' -f1)" == "$actual" ]]; then
      rm -f "$temporary"
    else
      rm -f "$temporary"
      ride_die "verified asset destination already exists with different content: $target"
    fi
  else
    mv "$temporary" "$target"
  fi
  sidecar="$target.ride.json"
  product=$(jq -r '.productId' <<< "$entry")
  if [[ -e "$sidecar" || -L "$sidecar" ]]; then
    if [[ ! -f "$sidecar" || -L "$sidecar" ]] || ! jq -e --arg digest "$actual" --arg source "$url" --arg product "$product" \
        '.sha256 == $digest and .sourceUri == $source and .productId == $product' "$sidecar" >/dev/null 2>&1; then
      ride_die "artifact sidecar already exists with different evidence: $sidecar"
    fi
    printf '%s\n' "$target"
    return
  fi
  sidecar_temp=$(mktemp "$destination/$tag/.provenance.XXXXXXXX") || ride_die "cannot create artifact provenance file"
  jq -n --arg product "$product" --arg version "$tag" \
    --arg url "$url" --arg digest "$actual" --argjson provenance "$(jq -c '.provenance' <<< "$metadata")" \
    '{schemaVersion:1, productId:$product, version:$version, sourceUri:$url, sha256:$digest,
      verification:"GitHub API digest and local SHA-256; no independent publisher signature", releaseMetadata:$provenance}' > "$sidecar_temp"
  chmod 600 "$sidecar_temp"
  mv "$sidecar_temp" "$sidecar"
  printf '%s\n' "$target"
}
