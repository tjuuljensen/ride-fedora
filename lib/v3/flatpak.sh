#!/usr/bin/env bash

ride_flathub_name() { printf 'flathub\n'; }
ride_flathub_url() { printf 'https://dl.flathub.org/repo/\n'; }
ride_flathub_repo_file() { printf 'https://dl.flathub.org/repo/flathub.flatpakrepo\n'; }
ride_flathub_marker_dir() { printf '/var/lib/ride-fedora/owned-remotes\n'; }
ride_flathub_marker() { printf '%s/system-flathub.json\n' "$(ride_flathub_marker_dir)"; }

ride_flathub_marker_content() {
  printf '{"schemaVersion":1,"installation":"system","name":"flathub","url":"https://dl.flathub.org/repo/","gpgVerify":true}\n'
}

ride_flathub_marker_metadata_ok() {
  [[ "$(stat -c '%u:%g:%a:%h' -- "$1")" == 0:0:600:1 ]]
}

ride_flathub_marker_dir_ok() {
  [[ -d "$1" && ! -L "$1" && "$(stat -c '%u:%g:%a' -- "$1")" == 0:0:700 ]]
}

ride_flathub_remote_json() {
  flatpak remotes --system --columns=name,url,options --json
}

ride_flathub_apps_json() {
  flatpak list --system --columns=application,origin --json
}

ride_flathub_marker_valid() {
  local marker
  marker=$(ride_flathub_marker)
  [[ -f "$marker" && ! -L "$marker" ]] && ride_flathub_marker_metadata_ok "$marker" &&
    cmp -s -- "$marker" <(ride_flathub_marker_content)
}

ride_flathub_remote_state() {
  local remotes marker_count url options
  remotes=$(ride_flathub_remote_json) || return 1
  marker_count=$(jq '[.[] | select(.name == "flathub")] | length' <<< "$remotes") || return 1
  marker=$(ride_flathub_marker)
  if [[ "$marker_count" == 0 ]]; then
    if [[ ! -e "$marker" && ! -L "$marker" ]]; then printf 'absent\n'; else printf 'unowned\n'; fi
    return
  fi
  [[ "$marker_count" == 1 ]] || { printf 'unowned\n'; return; }
  url=$(jq -r '.[] | select(.name == "flathub") | .url' <<< "$remotes") || return 1
  options=$(jq -r '.[] | select(.name == "flathub") | .options' <<< "$remotes") || return 1
  if [[ "$url" == "$(ride_flathub_url)" && "$options" != *no-gpg-verify* ]] && ride_flathub_marker_valid; then
    printf 'configured\n'
  else
    printf 'unowned\n'
  fi
}

ride_flathub_has_apps() {
  local apps
  apps=$(flatpak list --system --columns=application,origin --json) || return 2
  [[ -n "$apps" ]] || apps='[]'
  jq -e 'any(.[]; .origin == "flathub")' <<< "$apps" >/dev/null
}

ride_flathub_preflight() {
  local desired=$1 state marker_dir
  ride_require_command flatpak
  state=$(ride_flathub_remote_state) || ride_die "cannot inspect system Flatpak remotes"
  if [[ "$desired" == configured ]]; then
    [[ "$state" == absent || "$state" == configured ]] ||
      ride_die "system Flathub remote already exists or is not RIDE-owned"
  else
    [[ "$state" == configured || "$state" == absent ]] || ride_die "system Flathub remote is not owned by RIDE"
    if [[ "$state" == configured ]]; then
      if ride_flathub_has_apps; then
        ride_die "cannot remove the RIDE Flathub remote while system apps use it"
      else
        local app_status=$?
        [[ "$app_status" == 1 ]] || ride_die "cannot inspect system Flatpak applications"
      fi
    fi
  fi
  marker_dir=$(ride_flathub_marker_dir)
  if [[ -e "$marker_dir" ]]; then
    ride_flathub_marker_dir_ok "$marker_dir" ||
      ride_die "RIDE Flatpak marker directory is not private and root-owned"
  fi
}

ride_flathub_write_marker() {
  local dir marker temp
  dir=$(ride_flathub_marker_dir)
  marker=$(ride_flathub_marker)
  if [[ ! -e "$dir" ]]; then install -d -o root -g root -m 0700 -- "$dir" || return 1; fi
  [[ ! -e "$marker" && ! -L "$marker" ]] || return 1
  temp=$(mktemp "$dir/.system-flathub.XXXXXXXX") || return 1
  if ! ride_flathub_marker_content > "$temp" || ! chmod 0600 -- "$temp" ||
      ! chown root:root -- "$temp" || ! mv -T -- "$temp" "$marker"; then
    rm -f -- "$temp"
    return 1
  fi
}

ride_flathub_change() {
  local state=$1 current marker
  [[ "$state" == configured || "$state" == absent ]] || ride_die "invalid Flathub remote state"
  ride_flathub_preflight "$state"
  current=$(ride_flathub_remote_state) || ride_die "cannot inspect system Flathub remotes"
  [[ "$current" != "$state" ]] || return 0
  marker=$(ride_flathub_marker)
  if [[ "$state" == configured ]]; then
    flatpak remote-add --system flathub "$(ride_flathub_repo_file)" || return 1
    if ! ride_flathub_write_marker; then
      if ride_flathub_has_apps; then :; else
        local app_status=$?
        if [[ "$app_status" == 1 ]]; then
          flatpak remote-delete --system flathub || ride_error "Flathub rollback failed after marker error"
        fi
      fi
      rmdir -- "$(ride_flathub_marker_dir)" 2>/dev/null || true
      return 1
    fi
    [[ "$(ride_flathub_remote_state)" == configured ]] || {
      if ride_flathub_has_apps; then :; else
        local app_status=$?
        if [[ "$app_status" == 1 ]]; then flatpak remote-delete --system flathub; fi
      fi
      rm -f -- "$marker"
      ride_die "Flathub remote verification failed"
    }
  else
    flatpak remote-delete --system flathub || return 1
    rm -f -- "$marker"
  fi
}
