#!/usr/bin/env bash

# The trusted handler owns only the two legacy key paths and its marker.
ride_wireguard_dir() { printf '/etc/wireguard\n'; }

ride_wireguard_owner_ok() {
  [[ "$(stat -c '%u:%g' -- "$1")" == 0:0 ]]
}

ride_wireguard_marker_content() {
  printf 'RIDE v3 managed: setting.wireguard-keypair\nprivate_sha256=%s\npublic_sha256=%s\n' "$1" "$2"
}

ride_wireguard_file_state() {
  local dir private public marker private_hash public_hash extra
  dir=$(ride_wireguard_dir)
  private=$dir/privatekey
  public=$dir/publickey
  marker=$dir/.ride-owned-keypair
  if [[ ! -e "$private" && ! -L "$private" && ! -e "$public" && ! -L "$public" &&
        ! -e "$marker" && ! -L "$marker" ]]; then
    printf 'absent\n'
    return
  fi
  if [[ ! -f "$private" || -L "$private" || ! -f "$public" || -L "$public" ||
        ! -f "$marker" || -L "$marker" ]]; then
    printf 'unowned\n'
    return
  fi
  for extra in "$private" "$public" "$marker"; do
    if ! ride_wireguard_owner_ok "$extra" || [[ "$(stat -c '%a:%h' -- "$extra")" != 600:1 ]]; then
      printf 'unowned\n'
      return
    fi
  done
  private_hash=$(sha256sum -- "$private") || return 1
  public_hash=$(sha256sum -- "$public") || return 1
  private_hash=${private_hash%% *}
  public_hash=${public_hash%% *}
  if cmp -s -- "$marker" <(ride_wireguard_marker_content "$private_hash" "$public_hash"); then
    printf 'configured\n'
  else
    printf 'unowned\n'
  fi
}

ride_wireguard_observe() {
  ride_wireguard_file_state
}

ride_wireguard_preflight() {
  local dir state extra mode
  dir=$(ride_wireguard_dir)
  [[ ! -L "$dir" ]] || ride_die "WireGuard directory is a symlink"
  if [[ -e "$dir" ]]; then
    mode=$(stat -c '%a' -- "$dir")
    [[ -d "$dir" ]] && ride_wireguard_owner_ok "$dir" &&
      (( (8#$mode & 8#022) == 0 )) ||
      ride_die "WireGuard directory is writable by an untrusted user"
    extra=$(find "$dir" -mindepth 1 -maxdepth 1 \
      ! -name privatekey ! -name publickey ! -name .ride-owned-keypair -print -quit)
    [[ -z "$extra" ]] || ride_die "WireGuard directory contains unowned configuration"
  fi
  state=$(ride_wireguard_file_state) || ride_die "cannot observe WireGuard key pair"
  [[ "$state" != unowned ]] || ride_die "WireGuard keys are not owned by RIDE"
}

ride_wireguard_change() {
  local state=$1 dir private public marker temp_private temp_public temp_marker
  local private_hash public_hash current
  [[ "$state" == configured || "$state" == absent ]] || ride_die "invalid WireGuard key-pair state"
  ride_wireguard_preflight
  current=$(ride_wireguard_file_state) || ride_die "cannot observe WireGuard key pair"
  [[ "$current" != "$state" ]] || return 0
  dir=$(ride_wireguard_dir)
  private=$dir/privatekey
  public=$dir/publickey
  marker=$dir/.ride-owned-keypair
  if [[ "$state" == absent ]]; then
    [[ "$current" == configured ]] || ride_die "WireGuard key pair is not owned by RIDE"
    rm -f -- "$private" "$public" "$marker"
    return
  fi
  [[ "$current" == absent && -d "$dir" ]] || ride_die "WireGuard key directory is unavailable"
  ride_require_command rpm
  ride_require_command wg
  rpm -q --quiet wireguard-tools || ride_die "wireguard-tools is not installed"
  temp_private=$(mktemp "$dir/.ride-wireguard-private.XXXXXXXX") || return 1
  temp_public=$(mktemp "$dir/.ride-wireguard-public.XXXXXXXX") || { rm -f -- "$temp_private"; return 1; }
  temp_marker=$(mktemp "$dir/.ride-wireguard-marker.XXXXXXXX") || {
    rm -f -- "$temp_private" "$temp_public"
    return 1
  }
  if ! (umask 077; wg genkey > "$temp_private" && wg pubkey < "$temp_private" > "$temp_public") ||
      ! chmod 0600 -- "$temp_private" "$temp_public" "$temp_marker"; then
    rm -f -- "$temp_private" "$temp_public" "$temp_marker"
    return 1
  fi
  private_hash=$(sha256sum -- "$temp_private") || return 1
  public_hash=$(sha256sum -- "$temp_public") || return 1
  private_hash=${private_hash%% *}
  public_hash=${public_hash%% *}
  if ! ride_wireguard_marker_content "$private_hash" "$public_hash" > "$temp_marker" ||
      ! cmp -s -- "$temp_public" <(wg pubkey < "$temp_private"); then
    rm -f -- "$temp_private" "$temp_public" "$temp_marker"
    return 1
  fi
  if ! mv -T -- "$temp_private" "$private" ||
      ! mv -T -- "$temp_public" "$public" ||
      ! mv -T -- "$temp_marker" "$marker"; then
    rm -f -- "$temp_private" "$temp_public" "$temp_marker" "$private" "$public" "$marker"
    return 1
  fi
  [[ "$(ride_wireguard_file_state)" == configured ]] || ride_die "WireGuard key-pair verification failed"
}
