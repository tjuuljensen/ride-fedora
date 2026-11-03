#!/usr/bin/env bash
# Purpose:
#   Select an allowed ExpressVPN location and optionally request a connection.
#
# Behavior:
#   Read a newline-delimited location allowlist, choose a location other than
#   the last successful request when possible, and call the current
#   expressvpnctl connect command. Never disconnect first. A successful CLI
#   exit means the request was accepted; it does not verify route or DNS state.
#
# Compatibility:
#   Bash 4.4+ on Linux with ExpressVPN's current Linux app and GNU coreutils.
#   ExpressVPN documents Fedora 39+ on 64-bit systems.
#
# Usage:
#   tools/expressvpn-rotate.sh [--dry-run | --rotate] [--config FILE]
#       [--client FILE] [--help | --version]
#   Default mode is --dry-run. Use --rotate to submit a connection request.
#
# Inputs / environment:
#   Config defaults to $XDG_CONFIG_HOME/ride/expressvpn-rotate.conf, or
#   ~/.config/ride/expressvpn-rotate.conf. Each nonblank, noncomment line is
#   one exact ExpressVPN location name. State is kept in
#   $XDG_STATE_HOME/ride/expressvpn-rotate, or ~/.local/state/ride/...
#
# Outputs / side effects:
#   Dry run prints the selected location. --rotate invokes
#   `expressvpnctl connect LOCATION` and records that request after a zero exit.
#   It does not install packages, enable background mode, disconnect, schedule
#   itself, change VPN settings, or verify network recovery.
#
# Prerequisites:
#   An activated ExpressVPN Linux app; connection commands require the GUI to
#   be running or ExpressVPN background mode to already be enabled. GNU flock,
#   shuf, and a writable user config/state directory are required.
#
# Ownership:
#   User-scoped utility. It does not manage system or server schedules.
#
# Provenance:
#   Uses ExpressVPN's documented `expressvpnctl connect "LOCATION"` interface;
#   see docs/migrations/system-security-vpn-automation.md.
#
# Version:
#   0.1.0
#
# Changelog:
#   0.1.0: Replace the v2 disconnect-first randomizer with explicit locations.

set -Eeuo pipefail
SCRIPT_VERSION=0.1.0

usage() {
  cat <<'EOF'
Usage: expressvpn-rotate.sh [--dry-run | --rotate] [--config FILE]
                            [--client FILE] [--help | --version]

Read an explicit location allowlist and choose one location. By default,
print the choice without changing the VPN. Use --rotate to request a connection.

Options:
  --dry-run       Select and print a location (default)
  --rotate        Run expressvpnctl connect LOCATION
  --config FILE   Read allowed locations from FILE
  --client FILE   Use FILE instead of finding expressvpnctl on PATH
  --help          Show this help
  --version       Show the tool version

The config file contains one exact location name per line. Blank lines and
lines beginning with # are ignored. At least two unique locations are needed.
EOF
}

fail() {
  printf 'expressvpn-rotate: %s\n' "$*" >&2
  exit 1
}

mode=dry-run
mode_seen=false
config_file="${XDG_CONFIG_HOME:-${HOME:?HOME is not set}/.config}/ride/expressvpn-rotate.conf"
client_path=
while (($#)); do
  case "$1" in
    --dry-run|--rotate)
      [[ "$mode_seen" == false ]] || fail 'Choose only one of --dry-run and --rotate.'
      mode_seen=true
      [[ "$1" == --rotate ]] && mode=rotate
      shift
      ;;
    --config|--client)
      (($# >= 2)) || fail "Missing value for $1."
      if [[ "$1" == --config ]]; then
        config_file=$2
      else
        client_path=$2
      fi
      shift 2
      ;;
    --help)
      usage
      exit 0
      ;;
    --version)
      printf 'expressvpn-rotate %s\n' "$SCRIPT_VERSION"
      exit 0
      ;;
    *) fail "Unknown option: $1" ;;
  esac
done

[[ -f "$config_file" && -r "$config_file" ]] || fail "Location list is not readable: $config_file"
locations=()
while IFS= read -r line || [[ -n "$line" ]]; do
  line=${line%$'\r'}
  [[ -z "$line" || "$line" == \#* ]] && continue
  [[ "$line" == *$'\t'* || "$line" == *$'\n'* ]] && fail 'Location entries may not contain tabs or newlines.'
  locations+=("$line")
done < "$config_file"

declare -A seen=()
for location in "${locations[@]}"; do
  [[ -n "$location" ]] || fail 'Location entries may not be empty.'
  [[ "$location" == "${location# }" && "$location" == "${location% }" ]] || \
    fail "Location has leading or trailing spaces: '$location'"
  [[ -z "${seen[$location]+x}" ]] || fail "Duplicate location: $location"
  seen[$location]=1
done
((${#locations[@]} >= 2)) || fail 'At least two unique locations are required.'

state_dir="${XDG_STATE_HOME:-${HOME:?HOME is not set}/.local/state}/ride/expressvpn-rotate"
if [[ "$mode" == rotate ]]; then
  [[ ! -L "$state_dir" ]] || fail "State directory must not be a symlink: $state_dir"
  mkdir -p -- "$state_dir"
  [[ ! -L "$state_dir" ]] || fail "State directory must not be a symlink: $state_dir"
  owner=$(stat -c '%u' -- "$state_dir")
  [[ "$owner" == "$EUID" ]] || fail "State directory is not owned by uid $EUID: $state_dir"
  chmod 700 -- "$state_dir"
  lock_file="$state_dir/lock"
  [[ ! -L "$lock_file" ]] || fail "Lock path must not be a symlink: $lock_file"
  [[ ! -e "$lock_file" || ( -f "$lock_file" && -O "$lock_file" ) ]] || \
    fail "Lock path is not a regular file owned by uid $EUID: $lock_file"
  umask 077
  exec {lock_fd}>"$lock_file"
  flock -n "$lock_fd" || fail 'Another rotation request is already running.'
fi

last_location=
if [[ -r "$state_dir/last-location" ]]; then
  IFS= read -r last_location < "$state_dir/last-location" || true
fi
choices=()
for location in "${locations[@]}"; do
  [[ "$location" == "$last_location" ]] || choices+=("$location")
done
((${#choices[@]})) || choices=("${locations[@]}")
selected=$(printf '%s\n' "${choices[@]}" | shuf -n 1)
[[ -n "$selected" ]] || fail 'Could not select a location.'

if [[ "$mode" == dry-run ]]; then
  printf 'Selected location: %s\n' "$selected"
  exit 0
fi

if [[ -z "$client_path" ]]; then
  client_path=$(command -v expressvpnctl || true)
  [[ -n "$client_path" ]] || client_path=/opt/expressvpn/bin/expressvpnctl
fi
[[ -x "$client_path" ]] || fail "expressvpnctl is not executable: $client_path"

printf 'Requesting ExpressVPN location: %s\n' "$selected"
if ! "$client_path" connect "$selected"; then
  fail "ExpressVPN rejected the connection request for '$selected'; last-location state was not changed."
fi

state_tmp=$(mktemp "$state_dir/.last-location.XXXXXX")
trap 'rm -f -- "$state_tmp"' EXIT
chmod 600 -- "$state_tmp"
printf '%s\n' "$selected" > "$state_tmp"
mv -f -- "$state_tmp" "$state_dir/last-location"
trap - EXIT
printf 'ExpressVPN accepted the request. Route and DNS recovery were not checked.\n'
