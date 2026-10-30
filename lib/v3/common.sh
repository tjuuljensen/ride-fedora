#!/usr/bin/env bash

ride_error() { printf 'RIDE: %s\n' "$*" >&2; }
ride_die() { ride_error "$*"; exit 2; }

ride_require_command() {
  command -v "$1" >/dev/null 2>&1 || ride_die "required command is unavailable: $1"
}

ride_platform() {
  local os_file=/etc/os-release line
  if [[ "$EUID" -ne 0 && "${RIDE_TEST_MODE:-0}" == 1 && -n "${RIDE_OS_RELEASE_FILE:-}" ]]; then
    os_file=$RIDE_OS_RELEASE_FILE
  fi
  [[ -r "$os_file" ]] || ride_die "cannot read $os_file"
  RIDE_OS_ID=
  RIDE_OS_VERSION=
  RIDE_OS_VARIANT=
  while IFS= read -r line; do
    case "$line" in
      ID=*) RIDE_OS_ID=${line#ID=} ;;
      VERSION_ID=*) RIDE_OS_VERSION=${line#VERSION_ID=} ;;
      VARIANT_ID=*) RIDE_OS_VARIANT=${line#VARIANT_ID=} ;;
    esac
  done < "$os_file"
  RIDE_OS_ID=${RIDE_OS_ID#\"}; RIDE_OS_ID=${RIDE_OS_ID%\"}
  RIDE_OS_VERSION=${RIDE_OS_VERSION#\"}; RIDE_OS_VERSION=${RIDE_OS_VERSION%\"}
  RIDE_OS_VARIANT=${RIDE_OS_VARIANT#\"}; RIDE_OS_VARIANT=${RIDE_OS_VARIANT%\"}
  [[ "$RIDE_OS_ID" =~ ^[a-z0-9_-]+$ && "$RIDE_OS_VERSION" =~ ^[0-9]+(\.[0-9]+)?$ &&
     "$RIDE_OS_VARIANT" =~ ^[a-z0-9_-]*$ ]] ||
    ride_die "unrecognized operating system in $os_file"
  RIDE_ARCH=$(uname -m)
  [[ "$RIDE_ARCH" =~ ^[A-Za-z0-9_]+$ ]] || ride_die "unrecognized CPU architecture"
}

ride_state_dir() {
  if [[ -n "${RIDE_STATE_DIR:-}" && "$EUID" -ne 0 ]]; then
    printf '%s\n' "$RIDE_STATE_DIR"
  elif [[ "$EUID" -eq 0 ]]; then
    printf '%s\n' /var/lib/ride-fedora/runs
  else
    printf '%s\n' "${XDG_STATE_HOME:-$HOME/.local/state}/ride-fedora/runs"
  fi
}

ride_cache_dir() {
  if [[ -n "${RIDE_CACHE_DIR:-}" && "$EUID" -ne 0 ]]; then
    printf '%s\n' "$RIDE_CACHE_DIR"
  elif [[ "$EUID" -eq 0 ]]; then
    printf '%s\n' /var/cache/ride-fedora
  else
    printf '%s\n' "${XDG_CACHE_HOME:-$HOME/.cache}/ride-fedora"
  fi
}

ride_require_privilege() {
  local entry=$1 scope
  scope=$(jq -r '.scope' <<< "$entry")
  if [[ "$scope" == system && "$EUID" -ne 0 ]]; then
    ride_die "this operation needs root; rerun with sudo"
  fi
  if [[ "$scope" == user && "$EUID" -eq 0 ]]; then
    ride_die "this operation is per-user; run it from the intended non-root account"
  fi
}

ride_target_matches() {
  local entry=$1
  jq -e --arg os "$RIDE_OS_ID" --arg arch "$RIDE_ARCH" --arg release "$RIDE_OS_VERSION" \
    --arg variant "$RIDE_OS_VARIANT" '
    .targets[$os] as $t |
    $t != null and ($t.releases | index($release) != null) and
    ($t.architectures | index($arch) != null) and
    (($t.variantIds // null) as $variants |
      $variants == null or ($variants | index($variant) != null))
  ' <<< "$entry" >/dev/null
}

ride_require_target() {
  ride_target_matches "$1" ||
    ride_die "operation is not declared for $RIDE_OS_ID $RIDE_OS_VERSION $RIDE_ARCH variant ${RIDE_OS_VARIANT:-unknown}"
}

ride_require_accepted() {
  local entry=$1 status
  status=$(jq -r '.status' <<< "$entry")
  if [[ "$status" != supported && "${RIDE_ALLOW_CANDIDATE:-0}" != 1 ]]; then
    ride_die "operation is a candidate without VM acceptance; pass --allow-candidate for explicit development use"
  fi
}
