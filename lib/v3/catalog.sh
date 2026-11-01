#!/usr/bin/env bash

ride_validate_catalog() {
  [[ -r "$RIDE_CATALOG" ]] || ride_die "catalog not readable: $RIDE_CATALOG"
  jq -e '
    def valid_variant_targets:
      .status as $status | .targets |
      type == "object" and length > 0 and all(.[];
        if has("variantIds") then
          (.variantIds | type == "array" and length > 0 and
            all(.[]; type == "string" and test("^[a-z0-9_-]+$")))
        else $status != "supported" end);
    .schemaVersion == 3 and (.operations | type == "array" and length > 0) and
    ([.operations[].id] | length == (unique | length)) and
    all(.operations[];
      (.id | type == "string" and test("^(package|setting|artifact|system)\\.[a-z0-9.-]+$")) and
      (.kind | IN("package", "setting", "artifact", "system")) and
      (.name | type == "string" and length > 0) and
      (.handler | IN("dnf-package", "systemd-service", "github-asset", "python-venv", "pinned-script", "pinned-zip", "gsettings-boolean", "ibus-emoji-hotkey", "gsettings-string", "upower-threshold", "wireguard-keypair", "flatpak-remote")) and
      (.scope | IN("system", "user")) and
      (.status | IN("candidate", "supported")) and
      (.recovery | IN("remove-new-install", "exact-state", "none")) and
      (if .kind == "package" then
         ((.states == ["installed", "absent"] and .recovery == "remove-new-install") or
          (.states == ["installed"] and .recovery == "none"))
       elif .kind == "setting" then .recovery == "exact-state"
       elif .kind == "artifact" then .recovery == "none"
       else true end) and
      (.states | type == "array" and length > 0 and all(.[]; type == "string")) and
      valid_variant_targets and
      (.productUri | type == "string" and startswith("https://")) and
      (.sourceUri | type == "string" and startswith("https://")) and
      (.licenseUri | type == "string" and startswith("https://")) and
      (if .kind == "package" then
        .distribution == "installed" and .deploymentId == "local-installed" and
        (.artifactFormat | IN("rpm", "wheel", "script", "zip", "sdist")) and
        (.sourceId | type == "string" and test("^[a-z0-9-]+$")) and
        (.sourceId as $defaultSource | (.sourceProviders // []) | type == "array" and
          ([.[].sourceId] | length == (unique | length)) and
          all(.[];
            (.sourceId | type == "string" and test("^[a-z0-9-]+$")) and
            .handler == "dnf-package" and
            .scope == null and
            .artifactFormat == "rpm" and
            (.status | IN("candidate", "supported")) and
            .recovery == "remove-new-install" and
            valid_variant_targets and
            (.sourceUri | type == "string" and startswith("https://")) and
            .verification == "fedora-repository-gpg" and
            (.packageName | type == "string" and test("^[A-Za-z0-9+_.-]+$"))
          ) and all(.[]; .sourceId != $defaultSource)) and
        (([.packageName] + [.sourceProviders[]?.packageName] | map(select(. != null))) |
          length == (unique | length))
       else .distribution == null and .deploymentId == null and .artifactFormat == null and
         .sourceId == null and .sourceProviders == null end) and
      (if .handler == "dnf-package" then (.kind == "package" and .artifactFormat == "rpm" and
        (.packageName | type == "string" and test("^[A-Za-z0-9+_.-]+$")))
       elif .handler == "systemd-service" then (.kind == "setting" and (.serviceName | type == "string" and test("^[A-Za-z0-9_.@-]+\\.service$")))
       elif .handler == "gsettings-boolean" then (.kind == "setting" and .scope == "user" and
         .states == ["enabled", "disabled"] and
         (.id | IN("setting.gnome-clock-date", "setting.gnome-calendar-week-numbers", "setting.gnome-primary-paste", "setting.gnome-location", "setting.gnome-problem-reporting")))
       elif .handler == "ibus-emoji-hotkey" then (.kind == "setting" and .scope == "user" and
         .id == "setting.ibus-emoji-hotkey" and .states == ["enabled"] and
         .recovery == "exact-state" and .verification == "local-gsettings-state")
       elif .handler == "gsettings-string" then (.kind == "setting" and .scope == "user" and
         .states == ["configured"] and .recovery == "exact-state" and
         .verification == "local-gsettings-state" and
         (if .id == "setting.gnome-region" then .valueKind == "locale" and .allowedValues == null
          elif .id == "setting.gnome-window-buttons" then .valueKind == "window-buttons" and
            .allowedValues == [":minimize,maximize,close", ":appmenu:close", "close,minimize,maximize:"]
          else false end))
       elif .handler == "upower-threshold" then (.kind == "setting" and .scope == "system" and
         .id == "setting.upower-percentage-low" and .states == ["configured"] and
         .valueKind == "percentage-low" and .recovery == "exact-state" and
         .verification == "local-upower-config")
       elif .handler == "wireguard-keypair" then (.kind == "setting" and .scope == "system" and
         .id == "setting.wireguard-keypair" and .states == ["configured", "absent"] and
         .recovery == "exact-state" and .verification == "local-wireguard-keypair")
       elif .handler == "flatpak-remote" then (.kind == "setting" and .scope == "system" and
         .id == "setting.flathub-system-remote" and .states == ["configured", "absent"] and
         .recovery == "exact-state" and .verification == "local-flatpak-remote")
       elif .handler == "python-venv" then (.kind == "package" and
         (if .id == "package.chepy" then
           .scope == "user" and .artifactFormat == "sdist" and .sourceId == "pypi-sdist-venv" and
           .verification == "pypi-sdist-sha256" and
           .sourceUri == "https://files.pythonhosted.org/packages/3f/4c/b8bc1607c96e1df206912e4db82ace5adfb2fe9dce5926fd7860d265fa58/chepy-7.6.0.tar.gz" and
           .sourceSha256 == "f6084689e43d128748c18f79c79d75539abb67ac8245e950b678cfa0da2f5010"
          else .artifactFormat == "wheel" and (.id | IN("package.volatility3", "package.dfir-unfurl")) end))
       elif .handler == "pinned-script" then (.kind == "package" and .id == "package.asn" and
         .scope == "user" and .artifactFormat == "script" and
         .sourceId == "github-raw-pinned" and .verification == "github-commit-sha256-observed" and
         (.sourceUri | test("^https://raw[.]githubusercontent[.]com/nitefood/asn/[0-9a-f]{40}/asn$")) and
         (.licenseUri | test("^https://raw[.]githubusercontent[.]com/nitefood/asn/[0-9a-f]{40}/LICENSE$")) and
         (.sourceUri | split("/")[5]) == (.licenseUri | split("/")[5]) and
         (.sourceSha256 | type == "string" and test("^[0-9a-f]{64}$")) and
         (.licenseSha256 | type == "string" and test("^[0-9a-f]{64}$")))
       elif .handler == "pinned-zip" then (.kind == "package" and .id == "package.cyberchef" and
         .scope == "system" and .artifactFormat == "zip" and
         .sourceId == "github-release-pinned" and .verification == "github-release-api-sha256" and
         .sourceUri == "https://github.com/gchq/CyberChef/releases/download/v11.5.0/CyberChef_8cd426dd4f40f1423912d5fad91b578a86a65112.zip" and
         .licenseUri == "https://raw.githubusercontent.com/gchq/CyberChef/v11.5.0/LICENSE" and
         .sourceSha256 == "f6478925d3eaa16ec08626a85f5b85eed10d531a5e18700615fed7ecb024cccf" and
         .licenseSha256 == "58d1e17ffe5109a7ae296caafcadfdbe6a7d176f0bc4ab01e12a689b0499d8bd")
       else (.kind == "artifact" and (.githubRepository | type == "string" and test("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")) and
             (.assetSuffix | type == "string" and test("^-[A-Za-z0-9_.-]+$")) and
             (.maxBytes | type == "number" and . > 0 and . <= 104857600)) end)
    )
  ' "$RIDE_CATALOG" >/dev/null || ride_die "invalid v3 operation catalog"
  local dependency
  while IFS= read -r dependency; do
    [[ -z "$dependency" ]] && continue
    ride_entry "$dependency" >/dev/null || ride_die "catalog has unknown dependency: $dependency"
  done < <(jq -r '.operations[] | .dependencies[]?' "$RIDE_CATALOG")
  local evidence supported_id
  while IFS=$'\t' read -r supported_id evidence; do
    [[ "$evidence" == "docs/acceptance/$supported_id.md" && -f "$RIDE_ROOT/$evidence" ]] ||
      ride_die "supported catalog entry lacks acceptance evidence: $supported_id"
  done < <(jq -r '.operations[] | select(.status == "supported") | [.id, (.acceptanceEvidence // "MISSING")] | @tsv' "$RIDE_CATALOG")
  local source_id
  while IFS=$'\t' read -r supported_id source_id evidence; do
    [[ "$evidence" == "docs/acceptance/$supported_id.$source_id.md" && -f "$RIDE_ROOT/$evidence" ]] ||
      ride_die "supported source lacks acceptance evidence: $supported_id/$source_id"
  done < <(jq -r '.operations[] | .id as $id | .sourceProviders[]? | select(.status == "supported") |
    [$id, .sourceId, (.acceptanceEvidence // "MISSING")] | @tsv' "$RIDE_CATALOG")
}

ride_entry() {
  local id=$1
  jq -ce --arg id "$id" '.operations[] | select(.id == $id)' "$RIDE_CATALOG"
}

ride_entry_or_die() {
  local id=$1 requested=${2:-} value=${3:-} base selected
  base=$(ride_entry "$id") || ride_die "unknown catalog ID: $id"
  if [[ "$(jq -r '.kind' <<< "$base")" != package ]]; then
    [[ -z "$requested" ]] || ride_die "source selection requires a package: $id"
    if [[ -n "$value" ]]; then
      [[ "$(jq -r '.handler' <<< "$base")" == gsettings-string || "$(jq -r '.handler' <<< "$base")" == upower-threshold ]] ||
        ride_die "value selection requires a configurable setting: $id"
      ride_setting_value_valid "$base" "$value" || ride_die "invalid value for $id: $value"
      jq -c --arg value "$value" '. + {selectedValue:$value}' <<< "$base"
      return
    fi
    printf '%s\n' "$base"
    return
  fi
  [[ -z "$value" ]] || ride_die "value selection requires a configurable setting: $id"
  selected=${requested:-$(jq -r '.sourceId' <<< "$base")}
  if [[ "$selected" == "$(jq -r '.sourceId' <<< "$base")" ]]; then
    jq -c 'del(.sourceProviders)' <<< "$base"
    return
  fi
  jq -ce --arg selected "$selected" '
    . as $base | (.sourceProviders[]? | select(.sourceId == $selected)) as $source |
    ($base | del(.handler, .packageName, .artifactFormat, .status, .recovery,
                 .targets, .sourceUri, .verification, .sourceProviders)) + $source
  ' <<< "$base" || ride_die "unknown source $selected for $id"
}

ride_setting_value_valid() {
  local entry=$1 value=$2
  case "$(jq -r '.id' <<< "$entry")" in
    setting.gnome-region)
      [[ "$value" =~ ^[a-z]{2,3}_[A-Z]{2}\.UTF-8$ ]]
      ;;
    setting.gnome-window-buttons)
      jq -e --arg value "$value" '.allowedValues | index($value) != null' <<< "$entry" >/dev/null
      ;;
    setting.upower-percentage-low)
      [[ "$value" =~ ^([6-9]|[1-4][0-9]|50)$ ]]
      ;;
    *) return 1 ;;
  esac
}

ride_provider_conflict() {
  local entry=$1 id selected source alternative observed
  [[ "$(jq -r '.kind' <<< "$entry")" == package ]] || return 0
  id=$(jq -r '.id' <<< "$entry")
  selected=$(jq -r '.sourceId' <<< "$entry")
  while IFS= read -r source; do
    [[ "$source" == "$selected" ]] && continue
    alternative=$(ride_entry_or_die "$id" "$source")
    if ! ride_target_matches "$alternative"; then
      continue
    fi
    observed=$(ride_observe "$alternative")
    [[ "$observed" != installed ]] || { printf '%s\n' "$source"; return 0; }
  done < <(jq -r '.sourceId, .sourceProviders[]?.sourceId' <<< "$(ride_entry "$id")")
}

ride_source_signature() {
  local version=${2:-2} fields
  case "$version" in
    1) fields='{id, sourceId, handler, packageName, serviceName, scope, sourceUri, verification, targets, recovery}' ;;
    2) fields='if (.handler | IN("gsettings-string", "upower-threshold")) then
         {id, handler, scope, sourceUri, verification, targets, recovery, valueKind, allowedValues, selectedValue}
       elif (.handler | IN("pinned-script", "pinned-zip")) or .id == "package.chepy" then
         {id, distribution, deploymentId, sourceId, handler, packageName, artifactFormat, serviceName,
          scope, sourceUri, sourceSha256, licenseUri, licenseSha256, verification, targets, recovery}
       else
         {id, distribution, deploymentId, sourceId, handler, packageName, artifactFormat, serviceName,
          scope, sourceUri, verification, targets, recovery}
       end' ;;
    *) ride_die "unsupported source signature version: $version" ;;
  esac
  jq -cS "$fields" <<< "$1" |
    sha256sum | cut -d' ' -f1
}

ride_profile_path() {
  local profile=${1:-default}
  if [[ "$profile" == */* || "$profile" == *.json ]]; then
    printf '%s\n' "$profile"
  else
    printf '%s/profiles/%s.json\n' "$RIDE_ROOT" "$profile"
  fi
}

ride_validate_profile() {
  local profile=$1 id state source value entry handler
  [[ -r "$profile" ]] || ride_die "profile not readable: $profile"
  jq -e '
    .schemaVersion == 1 and (.id | type == "string" and test("^[a-z0-9-]+$")) and
    (.operations | type == "array") and
    ([.operations[].id] | length == (unique | length)) and
    all(.operations[]; (.id | type == "string") and (.state | type == "string") and
      (.value == null or (.value | type == "string" and length > 0 and length <= 80)) and
      (.source == null or (.source | type == "string" and test("^[a-z0-9-]+$"))))
  ' "$profile" >/dev/null || ride_die "invalid v3 profile: $profile"
  while IFS=$'\t' read -r id state source value; do
    [[ -z "$id" ]] && continue
    [[ "$source" != '~' ]] || source=
    [[ "$value" != '~' ]] || value=
    entry=$(ride_entry_or_die "$id" "$source" "$value")
    [[ "$(jq -r '.kind' <<< "$entry")" != artifact ]] || ride_die "download-only artifact cannot appear in a profile: $id"
    jq -e --arg state "$state" '.states | index($state) != null' <<< "$entry" >/dev/null ||
      ride_die "invalid state $state for $id"
    handler=$(jq -r '.handler' <<< "$entry")
    if [[ "$handler" == gsettings-string || "$handler" == upower-threshold ]]; then
      [[ -n "$value" ]] || ride_die "configurable setting requires a profile value: $id"
    else
      [[ -z "$value" ]] || ride_die "profile value is not valid for $id"
    fi
  done < <(jq -r '.operations[] | [.id, .state, (.source // "~"), (.value // "~")] | @tsv' "$profile")
}

ride_dependencies_ready() {
  local entry=$1 dependency dependency_entry current
  while IFS= read -r dependency; do
    [[ -z "$dependency" ]] && continue
    dependency_entry=$(ride_entry_or_die "$dependency")
    current=$(ride_observe "$dependency_entry")
    if [[ "$current" != installed ]]; then
      ride_error "dependency is not installed: $dependency"
      return 1
    fi
  done < <(jq -r '.dependencies[]?' <<< "$entry")
}
