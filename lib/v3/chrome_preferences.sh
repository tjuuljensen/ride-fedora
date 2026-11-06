#!/usr/bin/env bash
# Purpose: own recommended Chrome policy defaults for the Chrome Flatpak wrapper.
# Behavior: install one fixed JSON policy file without replacing existing policy or profiles.
# Compatibility: Bash 5, jq, sha256sum, and Fedora 44 Workstation x86_64.
# Usage: called by the RIDE v3 provider dispatcher.
# Inputs: selectedValue contains a JSON array of fixed policy IDs.
# Side effects: writes /etc/opt/chrome/policies/recommended/ride-fedora.json and ownership state.
# Prerequisites: the Flathub Chrome Flatpak wrapper imports host Chrome policies.
# Ownership: RIDE owns only its exact policy file and hash manifest.
# Provenance: Google Chrome Enterprise policy documentation and Flathub Chrome wrapper.
# Version: 3.0

ride_chrome_policy_file() { printf '%s\n' "${RIDE_CHROME_POLICY_FILE:-/etc/opt/chrome/policies/recommended/ride-fedora.json}"; }
ride_chrome_policy_manifest() { printf '%s\n' "${RIDE_CHROME_POLICY_MANIFEST:-/var/lib/ride-fedora/owned-chrome/setting.chrome-preferences.json}"; }

ride_chrome_policy_payload() {
  local selected=$1
  jq -ce '
    . as $ids |
    reduce $ids[] as $id ({}; . + (
      if $id == "homepage" then {HomepageLocation:"https://www.google.com"}
      elif $id == "homepage-not-newtab" then {HomepageIsNewTabPage:false}
      elif $id == "home-button" then {ShowHomeButton:true}
      elif $id == "no-default-browser-prompt" then {DefaultBrowserSettingEnabled:false}
      elif $id == "disable-safe-browsing" then {SafeBrowsingEnabled:false}
      elif $id == "no-safe-browsing-reporting" then {SafeBrowsingExtendedReportingEnabled:false}
      elif $id == "disable-network-prediction" then {NetworkPredictionOptions:2}
      elif $id == "bookmark-bar" then {BookmarkBarEnabled:true}
      else error("unknown Chrome policy selection") end
    ))' <<< "$selected"
}

ride_chrome_policy_manifest_valid() {
  local file=$1 manifest=$2 expected actual
  [[ -f "$manifest" && ! -L "$manifest" && -f "$file" && ! -L "$file" ]] || return 1
  expected=$(jq -er 'select(.schemaVersion == 1) | .sha256 | select(test("^[0-9a-f]{64}$"))' "$manifest") || return 1
  actual=$(sha256sum -- "$file") || return 1
  [[ "$expected" == "${actual%% *}" ]]
}

ride_chrome_preferences_observe() {
  local entry=${1:-} file manifest selected payload
  file=$(ride_chrome_policy_file); manifest=$(ride_chrome_policy_manifest)
  [[ ! -L "$file" && ! -L "$manifest" ]] || ride_die "Chrome policy ownership path is a symlink"
  if [[ -e "$file" || -e "$manifest" ]]; then
    ride_chrome_policy_manifest_valid "$file" "$manifest" ||
      ride_die "Chrome policy file or ownership record changed; preserving it"
    if [[ -n "$entry" ]] && jq -e 'has("selectedValue")' <<< "$entry" >/dev/null; then
      selected=$(jq -r '.selectedValue' <<< "$entry")
      payload=$(ride_chrome_policy_payload "$selected") || ride_die "invalid Chrome policy selection"
      [[ "$(cat -- "$file")" == "$payload" ]] ||
        ride_die "owned Chrome policy differs from the selected configuration; unset it before applying a different selection"
    fi
    printf 'configured\n'
  else
    printf 'absent\n'
  fi
}

ride_chrome_preferences_change() {
  local entry=$1 state=$2 selected file manifest file_parent manifest_parent payload tmp policy_sha manifest_tmp
  file=$(ride_chrome_policy_file); manifest=$(ride_chrome_policy_manifest)
  file_parent=${file%/*}; manifest_parent=${manifest%/*}
  case "$state" in
    configured)
      selected=$(jq -r '.selectedValue' <<< "$entry")
      payload=$(ride_chrome_policy_payload "$selected") || ride_die "invalid Chrome policy selection"
      [[ ! -L "$file_parent" && ! -L "$manifest_parent" && ! -L "$file" && ! -L "$manifest" ]] ||
        ride_die "Chrome policy path is a symlink"
      if [[ -e "$file" || -e "$manifest" ]]; then
        ride_chrome_policy_manifest_valid "$file" "$manifest" ||
          ride_die "unowned or modified Chrome policy path exists; preserving it"
        [[ "$(cat -- "$file")" == "$payload" ]] || ride_die "Chrome policy selection differs from owned content; remove before changing it"
        return 0
      fi
      mkdir -p -- "$file_parent" "$manifest_parent" || ride_die "cannot create Chrome policy directories"
      [[ ! -L /etc && ! -L /etc/opt && ! -L /etc/opt/chrome &&
         ! -L /etc/opt/chrome/policies && ! -L "$file_parent" &&
         ! -L /var && ! -L /var/lib && ! -L /var/lib/ride-fedora &&
         ! -L /var/lib/ride-fedora/owned-chrome && ! -L "$manifest_parent" ]] ||
        ride_die "Chrome policy directory path contains a symlink"
      tmp=$(mktemp "$file_parent/.ride-fedora.XXXXXXXX") || ride_die "cannot stage Chrome policy file"
      printf '%s\n' "$payload" > "$tmp" || { rm -f -- "$tmp"; ride_die "cannot write Chrome policies"; }
      chmod 0644 -- "$tmp" || { rm -f -- "$tmp"; ride_die "cannot set Chrome policy permissions"; }
      policy_sha=$(sha256sum -- "$tmp"); policy_sha=${policy_sha%% *}
      manifest_tmp=$(mktemp "$manifest_parent/.setting.chrome-preferences.XXXXXXXX") || { rm -f -- "$tmp"; ride_die "cannot stage Chrome policy ownership"; }
      jq -n --arg sha "$policy_sha" '{schemaVersion:1,sha256:$sha}' > "$manifest_tmp" || {
        rm -f -- "$tmp" "$manifest_tmp"; ride_die "cannot create Chrome policy ownership record";
      }
      chmod 0600 -- "$manifest_tmp" || { rm -f -- "$tmp" "$manifest_tmp"; ride_die "cannot protect Chrome ownership record"; }
      mv -- "$tmp" "$file" || { rm -f -- "$tmp" "$manifest_tmp"; ride_die "cannot install Chrome policy file"; }
      if ! mv -- "$manifest_tmp" "$manifest"; then
        rm -f -- "$file" "$manifest_tmp"
        ride_die "cannot install Chrome policy ownership record"
      fi
      ;;
    absent)
      if [[ ! -e "$file" && ! -e "$manifest" ]]; then return 0; fi
      ride_chrome_policy_manifest_valid "$file" "$manifest" ||
        ride_die "Chrome policy file or ownership record changed; preserving it"
      rm -- "$file" || ride_die "cannot remove owned Chrome policy file"
      rm -- "$manifest" || ride_die "cannot remove Chrome policy ownership record"
      ;;
    *) ride_die "invalid Chrome policy state: $state" ;;
  esac
}
