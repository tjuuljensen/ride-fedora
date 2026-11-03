#!/usr/bin/env bash

ride_keyfile_mounts_mapper() {
  local entry=$1 value
  value=$(jq -r '.selectedValue // ""' <<< "$entry")
  [[ "$value" =~ ^[A-Za-z0-9][A-Za-z0-9_.+-]{0,63}$ ]] ||
    ride_die 'keyfile mount operation requires --value with one mapper name'
  printf '%s\n' "$value"
}

ride_keyfile_mounts_call() {
  local action=$1 mapper=$2
  ride_require_command python3
  python3 "$RIDE_ROOT/tools/keyfile-mount-state.py" "$action" --mapper "$mapper"
}

ride_keyfile_mounts_observe() {
  local entry=$1 mapper
  if ! jq -e 'has("selectedValue")' <<< "$entry" >/dev/null; then
    printf 'selection-required\n'
    return 0
  fi
  mapper=$(ride_keyfile_mounts_mapper "$entry") || return 1
  ride_keyfile_mounts_call observe "$mapper"
}

ride_keyfile_mounts_change() {
  local entry=$1 state=$2 mapper
  mapper=$(ride_keyfile_mounts_mapper "$entry") || return 1
  case "$state" in
    absent) ride_keyfile_mounts_call remove "$mapper" ;;
    configured) ride_keyfile_mounts_call restore "$mapper" ;;
    *) ride_die "invalid keyfile mount state: $state" ;;
  esac
}
