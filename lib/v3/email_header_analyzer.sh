#!/usr/bin/env bash
# RIDE v3.0 email header analyzer deployment and observation.

ride_email_header_app_dir() {
  printf '%s/.local/share/ride-fedora/apps/email-header-analyzer\n' "$HOME"
}

ride_email_header_manifest() {
  printf '%s/.local/share/ride-fedora/owned-tools/package.email-header-analyzer.json\n' "$HOME"
}

ride_email_header_launcher() {
  printf '%s/.local/bin/ride-email-header-analyzer\n' "$HOME"
}

ride_email_header_tree_sha256() {
  ride_require_command python3
  python3 "$RIDE_ROOT/tools/ride-email-header-analyzer.py" --tree-sha256 "$1"
}

ride_email_header_paths_safe() {
  local path
  for path in "$HOME" "$HOME/.local" "$HOME/.local/share" "$HOME/.local/share/ride-fedora" \
    "$HOME/.local/share/ride-fedora/apps" "$HOME/.local/share/ride-fedora/owned-tools" \
    "$HOME/.local/bin"; do
    [[ ! -L "$path" ]] || return 1
  done
}

ride_observe_email_header_analyzer() {
  local app manifest launcher content_sha launcher_sha expected_uid
  app=$(ride_email_header_app_dir)
  manifest=$(ride_email_header_manifest)
  launcher=$(ride_email_header_launcher)
  if [[ ! -e "$app" && ! -L "$app" && ! -e "$manifest" && ! -L "$manifest" &&
        ! -e "$launcher" && ! -L "$launcher" ]]; then
    printf 'absent\n'; return 0
  fi
  ride_email_header_paths_safe || { printf 'unowned\n'; return 0; }
  [[ -d "$app" && ! -L "$app" && -f "$app/dist/spa/index.html" &&
     -f "$manifest" && ! -L "$manifest" && -f "$launcher" && ! -L "$launcher" && -x "$launcher" ]] || {
    printf 'unowned\n'; return 0;
  }
  expected_uid=$(id -u)
  [[ "$(stat -c '%u:%g:%a:%h' -- "$manifest")" == "$(id -u):$(id -g):600:1" &&
     "$(stat -c '%u:%a' -- "$app")" == "$expected_uid:700" ]] || {
    printf 'unowned\n'; return 0;
  }
  jq -e --arg dest "$app" --arg launcher "$launcher" '
    .schemaVersion == 1 and .id == "package.email-header-analyzer" and
    .destination == $dest and .launcher == $launcher and
    (.sourceCommit | type == "string" and test("^[0-9a-f]{40}$")) and
    (.sourceTree | type == "string" and test("^[0-9a-f]{40}$")) and
    (.contentSha256 | type == "string" and test("^[0-9a-f]{64}$")) and
    (.launcherSha256 | type == "string" and test("^[0-9a-f]{64}$"))
  ' "$manifest" >/dev/null 2>&1 || { printf 'unowned\n'; return 0; }
  content_sha=$(jq -r '.contentSha256' "$manifest") || return 1
  launcher_sha=$(jq -r '.launcherSha256' "$manifest") || return 1
  [[ "$(ride_email_header_tree_sha256 "$app")" == "$content_sha" &&
     "$(sha256sum -- "$launcher" | cut -d' ' -f1)" == "$launcher_sha" ]] || {
    printf 'unowned\n'; return 0;
  }
  printf 'installed\n'
}

ride_change_email_header_analyzer() {
  local entry=$1 state=$2 id commit tree lock_blob repo app manifest launcher current temporary source_dir frontend stage
  local app_parent manifest_parent launcher_parent content_sha launcher_sha manifest_temp node_version major minor
  id=$(jq -r '.id' <<< "$entry")
  commit=$(jq -r '.sourceCommit' <<< "$entry")
  tree=$(jq -r '.sourceTree' <<< "$entry")
  lock_blob=$(jq -r '.lockfileBlobSha1' <<< "$entry")
  repo=$(jq -r '.sourceUri' <<< "$entry")
  [[ "$id" == package.email-header-analyzer &&
     "$commit" == ccaf044dfe964215656966013feaaea705726048 &&
     "$tree" == 69ec6b8a3c078a0f952e04ddea47f0a0ebf3ce49 &&
     "$lock_blob" == 7e8a00e275c2253e6ffe29f42a9aac8dc00aee41 &&
     "$repo" == https://github.com/mailtower-app/email-header-analyzer ]] ||
    ride_die "unrecognized email header analyzer source pin"
  app=$(ride_email_header_app_dir)
  manifest=$(ride_email_header_manifest)
  launcher=$(ride_email_header_launcher)
  app_parent=$(dirname "$app")
  manifest_parent=$(dirname "$manifest")
  launcher_parent=$(dirname "$launcher")
  current=$(ride_observe_email_header_analyzer) || ride_die "cannot inspect email header analyzer files"
  case "$state" in
    installed)
      [[ "$current" != unowned ]] || ride_die "email header analyzer destination is modified or not RIDE-owned"
      [[ "$current" != installed ]] || return 0
      ride_email_header_paths_safe || ride_die "email header analyzer path contains a symbolic link"
      ride_require_command git
      ride_require_command npm
      ride_require_command node
      ride_require_command python3
      ride_require_command sha256sum
      node_version=$(node -p 'process.versions.node') || ride_die "cannot inspect Node.js version"
      IFS=. read -r major minor _ <<< "$node_version"
      [[ "$major" =~ ^[0-9]+$ && "$minor" =~ ^[0-9]+ ]] || ride_die "unrecognized Node.js version: $node_version"
      (( major >= 26 || major == 24 || (major == 22 && minor >= 12) )) ||
        ride_die "MailTower build requires Node.js 22.12+, 24.x, or 26+; found $node_version"
      temporary=$(mktemp -d "${TMPDIR:-/tmp}/ride-email-header-analyzer.XXXXXXXX") || return 1
      source_dir="$temporary/source"
      if ! git clone --quiet "$repo" "$source_dir" >"$temporary/git.log" 2>&1 ||
         ! git -C "$source_dir" checkout --quiet --detach "$commit" >>"$temporary/git.log" 2>&1 ||
         [[ "$(git -C "$source_dir" rev-parse HEAD 2>/dev/null)" != "$commit" ||
            "$(git -C "$source_dir" rev-parse 'HEAD^{tree}' 2>/dev/null)" != "$tree" ||
            "$(git -C "$source_dir" rev-parse "$commit:src/Frontend/package-lock.json" 2>/dev/null)" != "$lock_blob" ]]; then
        tail -n 12 "$temporary/git.log" >&2 || true
        rm -rf -- "$temporary"
        ride_die "could not verify pinned MailTower source and dependency lock"
      fi
      frontend="$source_dir/src/Frontend"
      if ! (cd "$frontend" && npm ci --ignore-scripts --no-audit --no-fund) >"$temporary/npm-ci.log" 2>&1; then
        tail -n 20 "$temporary/npm-ci.log" >&2 || true
        rm -rf -- "$temporary"
        ride_die "MailTower locked dependencies could not be installed"
      fi
      if [[ ! -x "$frontend/node_modules/.bin/quasar" ]] ||
         ! (cd "$frontend" && ./node_modules/.bin/quasar prepare --silent) >"$temporary/quasar.log" 2>&1 ||
         ! (cd "$frontend" && npm_config_ignore_scripts=true npm run build) >"$temporary/build.log" 2>&1 ||
         [[ ! -f "$frontend/dist/spa/index.html" || -L "$frontend/dist/spa" ]]; then
        tail -n 20 "$temporary/quasar.log" "$temporary/build.log" >&2 2>/dev/null || true
        rm -rf -- "$temporary"
        ride_die "MailTower static app build failed"
      fi
      stage="$temporary/install"
      mkdir -p "$stage/dist" || { rm -rf -- "$temporary"; return 1; }
      cp -a -- "$frontend/dist/spa" "$stage/dist/spa" || { rm -rf -- "$temporary"; return 1; }
      chmod -R u+rwX,go-rwx -- "$stage"
      content_sha=$(ride_email_header_tree_sha256 "$stage") || { rm -rf -- "$temporary"; return 1; }
      cp -- "$RIDE_ROOT/tools/ride-email-header-analyzer.py" "$temporary/launcher" || {
        rm -rf -- "$temporary"; return 1;
      }
      chmod 0755 "$temporary/launcher"
      launcher_sha=$(sha256sum -- "$temporary/launcher" | cut -d' ' -f1)
      mkdir -p -- "$app_parent" "$manifest_parent" "$launcher_parent" || {
        rm -rf -- "$temporary"; return 1;
      }
      [[ ! -e "$app" && ! -L "$app" && ! -e "$manifest" && ! -L "$manifest" &&
         ! -e "$launcher" && ! -L "$launcher" ]] || {
        rm -rf -- "$temporary"; ride_die "email header analyzer destination appeared during install"
      }
      mv -T -- "$stage" "$app" || { rm -rf -- "$temporary"; return 1; }
      if ! mv -T -- "$temporary/launcher" "$launcher"; then
        rm -rf -- "$app" "$temporary"; return 1
      fi
      umask 077
      manifest_temp=$(mktemp "$manifest_parent/.package.email-header-analyzer.XXXXXXXX") || {
        rm -f -- "$launcher"; rm -rf -- "$app" "$temporary"; return 1;
      }
      if ! jq -nc --arg id "$id" --arg commit "$commit" --arg tree "$tree" \
        --arg app "$app" --arg launcher "$launcher" --arg content "$content_sha" \
        --arg launcher_sha "$launcher_sha" \
        '{schemaVersion:1,id:$id,sourceCommit:$commit,sourceTree:$tree,destination:$app,launcher:$launcher,contentSha256:$content,launcherSha256:$launcher_sha}' > "$manifest_temp" ||
        ! chmod 0600 "$manifest_temp" || ! mv -T -- "$manifest_temp" "$manifest"; then
        rm -f -- "$manifest_temp" "$launcher"; rm -rf -- "$app" "$temporary"; return 1
      fi
      rm -rf -- "$temporary"
      [[ "$(ride_observe_email_header_analyzer)" == installed ]] ||
        ride_die "installed email header analyzer failed its ownership check"
      ;;
    absent)
      [[ "$current" != unowned ]] || ride_die "refusing to remove modified or unowned email header analyzer files"
      [[ "$current" == installed ]] || return 0
      ride_require_command flock
      # These environment variables are expanded by the child Bash command.
      # shellcheck disable=SC2016
      if ! EMAIL_HEADER_LAUNCHER="$launcher" EMAIL_HEADER_MANIFEST="$manifest" \
        EMAIL_HEADER_APP="$app" flock -n "$app/.ride-running.lock" bash -c \
        'rm -f -- "$EMAIL_HEADER_LAUNCHER" "$EMAIL_HEADER_MANIFEST"; rm -rf -- "$EMAIL_HEADER_APP"' \
        ; then
        ride_die "email header analyzer is running; stop its local server before removal"
      fi
      ;;
    *) ride_die "invalid email header analyzer state: $state" ;;
  esac
}
