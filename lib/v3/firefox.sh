#!/usr/bin/env bash

ride_firefox_preferences_files() {
  printf '%s\n' \
    /usr/lib64/firefox/mozilla.cfg \
    /usr/lib64/firefox/defaults/pref/autoconfig.js \
    /usr/lib64/firefox/browser/override.ini
}

ride_firefox_preferences_manifest() {
  printf '%s\n' /var/lib/ride-fedora/owned-firefox/setting.firefox-preferences.json
}

ride_firefox_preferences_content() {
  case "${1##*/}" in
    mozilla.cfg)
      cat <<'EOF'
// RIDE-managed Firefox preferences. Values follow the kept v2 defaults.
pref("network.dns.disablePrefetch", true);
pref("network.prefetch-next", false);
pref("browser.rights.3.shown", true);
pref("browser.startup.homepage_override.mstone", "ignore");
pref("browser.newtabpage.introShown", false);
pref("startup.homepage_welcome_url.additional", "https://www.google.com");
pref("browser.usedOnWindows10", true);
pref("browser.startup.homepage", "https://www.google.com");
pref("browser.newtabpage.pinned", "https://www.google.com");
pref("datareporting.healthreport.service.enabled", false);
pref("datareporting.healthreport.uploadEnabled", false);
pref("datareporting.policy.dataSubmissionEnabled", false);
pref("toolkit.crashreporter.enabled", false);
pref("services.sync.enabled", false);
pref("media.peerconnection.enabled", false);
pref("middlemouse.paste", false);
pref("extensions.pocket.enabled", false);
EOF
      ;;
    autoconfig.js)
      cat <<'EOF'
pref("general.config.obscure_value", 0);
pref("general.config.filename", "mozilla.cfg");
EOF
      ;;
    override.ini)
      cat <<'EOF'
[XRE]
EnableProfileMigrator=false
EOF
      ;;
    *) ride_die "unknown RIDE Firefox preference path" ;;
  esac
}

ride_firefox_preferences_manifest_valid() {
  local manifest=$1 actual paths_json
  paths_json=$(ride_firefox_preferences_files | jq -R . | jq -s .) || return 1
  jq -e --argjson expectedPaths "$paths_json" 'type == "object" and .schemaVersion == 1 and
    (.files | type == "array" and length == 3) and
    ([.files[].path] | sort == ($expectedPaths | sort)) and
    all(.files[]; (.sha256 | type == "string" and test("^[0-9a-f]{64}$")))' \
    "$manifest" >/dev/null || return 1
  while IFS=$'\t' read -r expected path; do
    [[ -n "$path" ]] || continue
    [[ -f "$path" && ! -L "$path" ]] || return 1
    actual=$(sha256sum -- "$path") || return 1
    actual=${actual%% *}
    [[ "$actual" == "$expected" ]] || return 1
  done < <(jq -r '.files[] | [.sha256,.path] | @tsv' "$manifest")
}

ride_firefox_preferences_observe() {
  local manifest path existing=0
  manifest=$(ride_firefox_preferences_manifest)
  [[ ! -L "$manifest" ]] || ride_die "Firefox preference ownership record is a symlink"
  if [[ -e "$manifest" ]]; then
    ride_firefox_preferences_manifest_valid "$manifest" ||
      ride_die "Firefox preference files or ownership record changed; preserving them"
    printf 'configured\n'
    return 0
  fi
  while IFS= read -r path; do
    [[ ! -L "$path" ]] || ride_die "Firefox preference path is a symlink: $path"
    if [[ -e "$path" ]]; then existing=1; fi
  done < <(ride_firefox_preferences_files)
  ((existing == 0)) || ride_die "unowned Firefox preference files exist; refusing to claim them"
  printf 'absent\n'
}

ride_firefox_preferences_change() {
  local state=$1 manifest parent path temporary sha files_json='[]' manifest_tmp
  local -a created=() staged=()
  manifest=$(ride_firefox_preferences_manifest)
  parent=${manifest%/*}
  case "$state" in
    configured)
      if [[ -e "$manifest" || -L "$manifest" ]]; then
        [[ ! -L "$manifest" ]] || ride_die "Firefox preference ownership record is a symlink"
        ride_firefox_preferences_manifest_valid "$manifest" ||
          ride_die "Firefox preference files or ownership record changed; preserving them"
        return 0
      fi
      while IFS= read -r path; do
        [[ ! -L "$path" ]] || ride_die "Firefox preference path is a symlink: $path"
        [[ ! -e "$path" ]] || ride_die "unowned Firefox preference file exists: $path"
        [[ -d "${path%/*}" && ! -L "${path%/*}" ]] ||
          ride_die "Firefox preference directory is missing or unsafe: ${path%/*}"
      done < <(ride_firefox_preferences_files)
      [[ ! -L "$parent" ]] || ride_die "Firefox ownership state directory is a symlink"
      if [[ -e "$parent" ]]; then
        [[ -d "$parent" ]] || ride_die "Firefox ownership state path is not a directory"
      else
        mkdir -m 0700 -- "$parent" || ride_die "cannot create Firefox ownership state directory"
      fi
      while IFS= read -r path; do
        temporary=$(mktemp "${path%/*}/.ride-firefox.XXXXXXXX") || {
          for path in "${staged[@]}"; do rm -f -- "$path"; done
          ride_die "cannot stage Firefox preference file"
        }
        ride_firefox_preferences_content "$path" > "$temporary" || {
          rm -f -- "$temporary"
          for path in "${staged[@]}"; do rm -f -- "$path"; done
          ride_die "cannot write Firefox preference content"
        }
        chmod 0644 -- "$temporary" || ride_die "cannot set Firefox preference mode"
        staged+=("$temporary:$path")
        sha=$(sha256sum -- "$temporary"); sha=${sha%% *}
        files_json=$(jq -c --arg path "$path" --arg sha "$sha" '. + [{path:$path,sha256:$sha}]' <<< "$files_json") ||
          ride_die "cannot record Firefox preference hash"
      done < <(ride_firefox_preferences_files)
      manifest_tmp=$(mktemp "$parent/.setting.firefox-preferences.XXXXXXXX") ||
        ride_die "cannot stage Firefox preference ownership record"
      jq -n --argjson files "$files_json" '{schemaVersion:1,files:$files}' > "$manifest_tmp" ||
        ride_die "cannot serialize Firefox preference ownership record"
      chmod 0600 -- "$manifest_tmp" || ride_die "cannot set Firefox ownership record mode"
      local staged_item source destination created_file
      for staged_item in "${staged[@]}"; do
        source=${staged_item%%:*}
        destination=${staged_item#*:}
        ln -T -- "$source" "$destination" || {
          for created_file in "${created[@]}"; do rm -f -- "$created_file"; done
          rm -f -- "$manifest_tmp"
          ride_die "cannot install Firefox preference file: $destination"
        }
        rm -- "$source" || ride_die "cannot remove staged Firefox preference file"
        created+=("$destination")
      done
      ln -T -- "$manifest_tmp" "$manifest" || {
        for path in "${created[@]}"; do rm -f -- "$path"; done
        rm -f -- "$manifest_tmp"
        ride_die "cannot install Firefox ownership record"
      }
      rm -- "$manifest_tmp" || ride_die "cannot remove staged Firefox ownership record"
      ;;
    absent)
      [[ ! -L "$manifest" ]] || ride_die "Firefox preference ownership record is a symlink"
      [[ -e "$manifest" ]] || return 0
      ride_firefox_preferences_manifest_valid "$manifest" ||
        ride_die "Firefox preference files changed; preserving files and ownership record"
      while IFS= read -r path; do rm -- "$path" || ride_die "cannot remove Firefox preference file: $path"; done \
        < <(jq -r '.files[].path' "$manifest")
      rm -- "$manifest" || ride_die "cannot remove Firefox ownership record"
      ;;
    *) ride_die "invalid Firefox preference state: $state" ;;
  esac
}

ride_firefox_extensions_tool() {
  local tool="$RIDE_ROOT/tools/manage-firefox-global-xpis.py"
  [[ -f "$tool" && ! -L "$tool" ]] || ride_die "Firefox extension policy helper is missing or unsafe: $tool"
  printf '%s\n' "$tool"
}

ride_firefox_extensions_observe() {
  local tool
  tool=$(ride_firefox_extensions_tool)
  ride_require_command python3
  python3 "$tool" --manifest "$RIDE_ROOT/policies/firefox-extensions.json" \
    --target '/usr/lib64/mozilla/extensions/{ec8030f7-c20a-464f-9b0e-13a3a9e97384}' \
    --policy /etc/firefox/policies/policies.json \
    --state /var/lib/ride-fedora/firefox-global-xpis.json \
    --backup-dir /var/lib/ride-fedora/firefox-global-xpi-removal observe
}

ride_firefox_extensions_change() {
  local state=$1 tool
  tool=$(ride_firefox_extensions_tool)
  ride_require_command python3
  python3 "$tool" --manifest "$RIDE_ROOT/policies/firefox-extensions.json" \
    --target '/usr/lib64/mozilla/extensions/{ec8030f7-c20a-464f-9b0e-13a3a9e97384}' \
    --policy /etc/firefox/policies/policies.json \
    --state /var/lib/ride-fedora/firefox-global-xpis.json \
    --backup-dir /var/lib/ride-fedora/firefox-global-xpi-removal set-state "$state"
}
