#!/usr/bin/env bash

ride_vpn_profiles_connection_dir() {
  if [[ "${RIDE_TEST_MODE:-0}" == 1 && -n "${RIDE_VPN_PROFILES_TEST_CONNECTION_DIR:-}" ]]; then
    printf '%s\n' "$RIDE_VPN_PROFILES_TEST_CONNECTION_DIR"
  else
    printf '%s\n' /etc/NetworkManager/system-connections
  fi
}

ride_vpn_profiles_state_root() {
  if [[ "${RIDE_TEST_MODE:-0}" == 1 && -n "${RIDE_VPN_PROFILES_TEST_STATE_ROOT:-}" ]]; then
    printf '%s\n' "$RIDE_VPN_PROFILES_TEST_STATE_ROOT"
  else
    printf '%s\n' /var/lib/ride-fedora/owned-tools/setting.networkmanager-vpn-profiles
  fi
}

ride_vpn_profiles_helper() {
  printf '%s/tools/networkmanager-vpn-state.py\n' "$RIDE_ROOT"
}

ride_vpn_profiles_selection() {
  local entry=$1 value uuid index
  local -A seen=()
  value=$(jq -r '.selectedValue // ""' <<< "$entry")
  [[ -n "$value" && ${#value} -le 2048 ]] ||
    ride_die 'VPN profile operation requires --value with one or more selected UUIDs'
  IFS=',' read -r -a RIDE_VPN_PROFILE_UUIDS <<< "$value"
  (( ${#RIDE_VPN_PROFILE_UUIDS[@]} > 0 && ${#RIDE_VPN_PROFILE_UUIDS[@]} <= 32 )) ||
    ride_die 'select between one and 32 NetworkManager VPN UUIDs'
  for index in "${!RIDE_VPN_PROFILE_UUIDS[@]}"; do
    uuid=${RIDE_VPN_PROFILE_UUIDS[$index]}
    [[ "$uuid" =~ ^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$ ]] ||
      ride_die "invalid NetworkManager UUID: $uuid"
    uuid=${uuid,,}
    [[ -z "${seen[$uuid]+present}" ]] || ride_die "duplicate NetworkManager UUID: $uuid"
    seen[$uuid]=1
    RIDE_VPN_PROFILE_UUIDS[index]=$uuid
  done
}

ride_vpn_profiles_selection_dir() {
  local entry=$1 uuid joined hash root
  ride_vpn_profiles_selection "$entry"
  printf -v joined '%s\n' "${RIDE_VPN_PROFILE_UUIDS[@]}"
  hash=$(printf '%s' "$joined" | LC_ALL=C sort -u | sha256sum | cut -d' ' -f1)
  root=$(ride_vpn_profiles_state_root)
  printf '%s/selections/%s\n' "$root" "$hash"
}

ride_vpn_profiles_present() {
  local uuid=$1 kind
  kind=$(nmcli -g connection.type connection show "$uuid" 2>/dev/null) || return 1
  [[ "$kind" == vpn ]]
}

ride_vpn_profiles_ready() {
  local running
  running=$(nmcli -g RUNNING general 2>/dev/null) ||
    ride_die 'cannot inspect NetworkManager daemon state'
  [[ "$running" == running ]] || ride_die 'NetworkManager is not running'
}

ride_vpn_profiles_active() {
  local uuid=$1 active
  active=$(nmcli -g UUID connection show --active 2>/dev/null) ||
    ride_die 'cannot inspect active NetworkManager connections'
  grep -Fxiq -- "$uuid" <<< "$active"
}

ride_vpn_profiles_all_present() {
  local uuid
  for uuid in "${RIDE_VPN_PROFILE_UUIDS[@]}"; do
    ride_vpn_profiles_present "$uuid" || return 1
  done
}

ride_vpn_profiles_rollback() {
  local connection_dir=$1 state_dir=$2
  shift 2
  ride_vpn_profiles_call_helper restore --connection-dir "$connection_dir" \
    --state-dir "$state_dir" "$@" >/dev/null &&
    nmcli connection reload >/dev/null &&
    ride_vpn_profiles_all_present || return 1
  ride_vpn_profiles_call_helper discard --connection-dir "$connection_dir" \
    --state-dir "$state_dir" "$@" >/dev/null
}

ride_vpn_profiles_call_helper() {
  python3 "$(ride_vpn_profiles_helper)" "$@"
}

ride_vpn_profiles_observe() {
  local entry=$1 uuid present=0 absent=0
  ride_require_command nmcli
  local selected
  selected=$(jq -r '.selectedValue // ""' <<< "$entry")
  [[ -n "$selected" ]] || { printf 'selection-required\n'; return 0; }
  ride_vpn_profiles_ready
  ride_vpn_profiles_selection "$entry"
  for uuid in "${RIDE_VPN_PROFILE_UUIDS[@]}"; do
    if ride_vpn_profiles_present "$uuid"; then
      ((present+=1))
    else
      ((absent+=1))
    fi
  done
  if (( present == ${#RIDE_VPN_PROFILE_UUIDS[@]} )); then
    printf 'configured\n'
  elif (( absent == ${#RIDE_VPN_PROFILE_UUIDS[@]} )); then
    printf 'absent\n'
  else
    printf 'conflict\n'
  fi
}

ride_vpn_profiles_change() {
  local entry=$1 desired=$2 uuid state_dir connection_dir deleted=0
  local -a helper_args=()
  ride_require_command nmcli
  ride_require_command python3
  ride_vpn_profiles_ready
  ride_vpn_profiles_selection "$entry"
  for uuid in "${RIDE_VPN_PROFILE_UUIDS[@]}"; do helper_args+=(--uuid "$uuid"); done
  state_dir=$(ride_vpn_profiles_selection_dir "$entry")
  connection_dir=$(ride_vpn_profiles_connection_dir)

  case "$desired" in
    absent)
      for uuid in "${RIDE_VPN_PROFILE_UUIDS[@]}"; do
        ride_vpn_profiles_present "$uuid" || ride_die "selected VPN UUID is not present: $uuid"
        if ride_vpn_profiles_active "$uuid"; then
          ride_die "refusing to remove active VPN profile: $uuid"
        fi
      done
      ride_vpn_profiles_call_helper snapshot --connection-dir "$connection_dir" \
        --state-dir "$state_dir" "${helper_args[@]}" >/dev/null ||
        ride_die 'could not create private exact-state VPN profile snapshot'
      for uuid in "${RIDE_VPN_PROFILE_UUIDS[@]}"; do
        if ! ride_vpn_profiles_call_helper check-live --connection-dir "$connection_dir" \
             --state-dir "$state_dir" --uuid "$uuid" >/dev/null; then
          if (( deleted == 0 )); then
            ride_vpn_profiles_call_helper discard --connection-dir "$connection_dir" \
              --state-dir "$state_dir" "${helper_args[@]}" >/dev/null || true
          elif ! ride_vpn_profiles_rollback "$connection_dir" "$state_dir" "${helper_args[@]}"; then
            ride_die "selected VPN profile changed during removal; rollback needs recovery from $state_dir"
          fi
          ride_die "selected VPN profile changed before removal: $uuid"
        fi
        if ride_vpn_profiles_active "$uuid"; then
          if (( deleted == 0 )); then
            ride_vpn_profiles_call_helper discard --connection-dir "$connection_dir" \
              --state-dir "$state_dir" "${helper_args[@]}" >/dev/null || true
          elif ! ride_vpn_profiles_rollback "$connection_dir" "$state_dir" "${helper_args[@]}"; then
            ride_die "VPN profile became active during removal; rollback needs recovery from $state_dir"
          fi
          ride_die "refusing to remove active VPN profile: $uuid"
        fi
        if ! nmcli connection delete uuid "$uuid" >/dev/null; then
          if ride_vpn_profiles_rollback "$connection_dir" "$state_dir" "${helper_args[@]}"; then
            ride_die "removing VPN profile $uuid failed; the partial change was rolled back"
          fi
          ride_die "removing VPN profile $uuid failed and exact rollback needs recovery from $state_dir"
        fi
        ((deleted+=1))
      done
      if ! nmcli connection reload >/dev/null; then
        if ride_vpn_profiles_rollback "$connection_dir" "$state_dir" "${helper_args[@]}"; then
          ride_die 'NetworkManager reload failed after VPN profile removal; the change was rolled back'
        fi
        ride_die "NetworkManager reload failed and VPN profile rollback needs recovery from $state_dir"
      fi
      for uuid in "${RIDE_VPN_PROFILE_UUIDS[@]}"; do
        if ride_vpn_profiles_present "$uuid"; then
          if ride_vpn_profiles_rollback "$connection_dir" "$state_dir" "${helper_args[@]}"; then
            ride_die "NetworkManager retained VPN profile $uuid after removal; the change was rolled back"
          fi
          ride_die "NetworkManager retained VPN profile $uuid and rollback needs recovery from $state_dir"
        fi
      done
      ;;
    configured)
      ride_vpn_profiles_call_helper verify --connection-dir "$connection_dir" \
        --state-dir "$state_dir" "${helper_args[@]}" >/dev/null ||
        ride_die 'exact VPN profile recovery state is unavailable'
      for uuid in "${RIDE_VPN_PROFILE_UUIDS[@]}"; do
        if ride_vpn_profiles_present "$uuid"; then
          ride_die "refusing to overwrite an existing VPN profile UUID: $uuid"
        fi
      done
      ride_vpn_profiles_call_helper restore --connection-dir "$connection_dir" \
        --state-dir "$state_dir" "${helper_args[@]}" >/dev/null ||
        ride_die 'VPN profile restore failed; saved exact state remains available for retry'
      nmcli connection reload >/dev/null ||
        ride_die "VPN profiles were restored to disk but NetworkManager reload failed; retry using recovery state at $state_dir"
      for uuid in "${RIDE_VPN_PROFILE_UUIDS[@]}"; do
        ride_vpn_profiles_present "$uuid" || ride_die "NetworkManager did not restore VPN profile $uuid"
      done
      ride_vpn_profiles_call_helper discard --connection-dir "$connection_dir" \
        --state-dir "$state_dir" "${helper_args[@]}" >/dev/null ||
        ride_die "VPN profiles restored but private recovery cleanup failed: $state_dir"
      ;;
    *) ride_die "invalid VPN profile state: $desired" ;;
  esac
}
