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

ride_flatpak_halloy_remote_valid() {
  local remotes
  remotes=$(flatpak remotes --system --columns=name,url,options --json) || return 1
  jq -e '
    [.[] | select(.name == "flathub")] as $rows |
    ($rows | length) == 1 and
    $rows[0].url == "https://dl.flathub.org/repo/" and
    (($rows[0].options // "") | contains("no-gpg-verify") | not)
  ' <<< "$remotes" >/dev/null
}

ride_flatpak_app_id() { jq -r '.applicationId' <<< "$1"; }

ride_flatpak_app_state() {
  local entry=$1 app_id apps rows count origin
  app_id=$(ride_flatpak_app_id "$entry")
  apps=$(flatpak list --system --columns=application,origin --json) || return 1
  [[ -n "$apps" ]] || apps='[]'
  rows=$(jq --arg id "$app_id" '[.[] | select((.application_id // .application) == $id)]' <<< "$apps") || return 1
  count=$(jq 'length' <<< "$rows") || return 1
  if [[ "$count" == 0 ]]; then
    printf 'absent\n'
    return
  fi
  [[ "$count" == 1 ]] || { printf 'unowned\n'; return; }
  origin=$(jq -r '.[0].origin // ""' <<< "$rows") || return 1
  [[ "$origin" == flathub ]] || { printf 'unowned\n'; return; }
  printf 'installed\n'
}

ride_flatpak_app_preflight() {
  local entry=$1 desired=$2 current app_id rpm_status
  ride_require_command flatpak
  app_id=$(ride_flatpak_app_id "$entry")
  current=$(ride_flatpak_app_state "$entry") || ride_die "cannot inspect system Flatpak application"
  [[ "$current" != unowned ]] || ride_die "Flatpak application is installed from an unexpected origin"
  if [[ "$desired" == installed && "$current" == absent ]]; then
    ride_flatpak_halloy_remote_valid ||
      ride_die "a GPG-verified system Flathub remote is required for this application"
    if [[ "$app_id" == it.mijorus.gearlever ]]; then
      ride_require_command rpm
      if rpm -q --quiet appimagelauncher; then
        ride_die "AppImageLauncher RPM is installed; remove it before installing Gear Lever to avoid competing AppImage handlers"
      else
        rpm_status=$?
        [[ "$rpm_status" == 1 ]] || ride_die "cannot determine whether the AppImageLauncher RPM is installed"
      fi
    fi
  fi
}

ride_flatpak_app_change() {
  local entry=$1 state=$2 app_id
  app_id=$(ride_flatpak_app_id "$entry")
  ride_flatpak_app_preflight "$entry" "$state"
  case "$state" in
    installed) flatpak install --system --noninteractive flathub "$app_id" ;;
    absent) flatpak uninstall --system --noninteractive "$app_id" ;;
    *) ride_die "invalid Flatpak application state" ;;
  esac
}

ride_flatpak_halloy_entry() {
  printf '%s\n' '{"applicationId":"org.squidowl.halloy"}'
}

ride_flatpak_halloy_state() { ride_flatpak_app_state "$(ride_flatpak_halloy_entry)"; }
ride_flatpak_halloy_preflight() { ride_flatpak_app_preflight "$(ride_flatpak_halloy_entry)" "$1"; }
ride_flatpak_halloy_change() { ride_flatpak_app_change "$(ride_flatpak_halloy_entry)" "$1"; }
