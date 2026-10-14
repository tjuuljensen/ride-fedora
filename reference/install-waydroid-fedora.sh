#!/usr/bin/env bash
###############################################################################
# Script Name: install-waydroid-fedora.sh
# Status:
#   REFERENCE ONLY - NOT TESTED END TO END ON A CLEAN FEDORA INSTALLATION.
# Purpose:
#   Provide a reference installer for Waydroid on a mutable Fedora workstation
#   with optional firewalld networking configuration.
#
# Behavior:
#   - Verifies that the host is a mutable Fedora installation.
#   - Installs the Fedora waydroid package and enables its container service.
#   - Initializes GAPPS and MAINLINE images from the official OTA channels.
#   - Skips an existing initialization unless --force-init is requested.
#   - Idempotently assigns waydroid0 to the trusted firewalld zone.
#   - Idempotently creates the waydroid-to-host firewalld policy without
#     deleting or recreating the trusted zone.
#   - Prints desktop-user commands for starting and testing Waydroid.
#
# Usage:
#   reference/install-waydroid-fedora.sh [options]
#
# Inputs:
#   --system-type TYPE     GAPPS, VANILLA, or FOSS. Defaults to GAPPS.
#   --system-channel URL   Override the official system OTA channel.
#   --vendor-channel URL   Override the official vendor OTA channel.
#   --force-init           Reinitialize Waydroid images and configuration.
#   --skip-firewall        Do not modify firewalld configuration.
#   --skip-host-policy     Configure the trusted zone but not the host policy.
#   --dry-run              Print mutating commands without running them.
#   --acknowledge-untested Allow mutating operations after reviewing the script.
#
# Outputs / Side Effects:
#   - Installs the waydroid RPM and downloads Android images.
#   - Enables and starts waydroid-container.service.
#   - May update permanent firewalld zone and policy configuration.
#   - Does not modify Docker configuration or start a graphical user session.
#
# Prerequisites:
#   A mutable Fedora installation, Bash, systemd, dnf, network access, and
#   sudo access when not run as root. firewalld is optional.
#
# Version:
#   1.0.0
#
# Changelog:
#   1.0.0:
#     - Added idempotent Fedora Waydroid installation and network setup.
###############################################################################

set -Eeuo pipefail

readonly SCRIPT_NAME="${0##*/}"
readonly POLICY_NAME="waydroid-to-host"
readonly WAYDROID_INTERFACE="waydroid0"

SYSTEM_TYPE="GAPPS"
SYSTEM_CHANNEL=""
VENDOR_CHANNEL=""
FORCE_INIT=0
CONFIGURE_FIREWALL=1
CONFIGURE_HOST_POLICY=1
DRY_RUN=0
ACKNOWLEDGE_UNTESTED=0
ROOT_CMD=()

log() {
  printf '%s\n' "$*"
}

warn() {
  printf 'WARNING: %s\n' "$*" >&2
}

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

on_error() {
  local exit_code="$1"
  local line_number="$2"
  printf 'ERROR: %s failed at line %s (exit %s).\n' \
    "$SCRIPT_NAME" "$line_number" "$exit_code" >&2
  exit "$exit_code"
}

trap 'on_error "$?" "$LINENO"' ERR

usage() {
  cat <<'USAGE'
Usage: install-waydroid-fedora.sh [options]

Install and initialize Waydroid on a mutable Fedora workstation.

Options:
  --system-type TYPE     GAPPS, VANILLA, or FOSS (default: GAPPS)
  --system-channel URL   Override the official system OTA channel
  --vendor-channel URL   Override the official vendor OTA channel
  --force-init           Reinitialize Waydroid images and configuration
  --skip-firewall        Do not modify firewalld configuration
  --skip-host-policy     Do not create the waydroid-to-host policy
  --dry-run              Print mutating commands without running them
  --acknowledge-untested Allow real changes after reviewing this reference
  -h, --help             Show this help

Examples:
  ./reference/install-waydroid-fedora.sh --dry-run
  ./reference/install-waydroid-fedora.sh --acknowledge-untested
USAGE
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

print_command() {
  printf '  '
  printf '%q ' "$@"
  printf '\n'
}

run_mutating() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    print_command "$@"
    return 0
  fi

  "$@"
}

run_root() {
  run_mutating "${ROOT_CMD[@]}" "$@"
}

root_capture() {
  "${ROOT_CMD[@]}" "$@"
}

contains_word() {
  local words="$1"
  local wanted="$2"
  local word

  for word in $words; do
    [[ "$word" == "$wanted" ]] && return 0
  done
  return 1
}

read_ini_value() {
  local file="$1"
  local key="$2"

  awk -F= -v wanted="$key" '
    $1 ~ "^[[:space:]]*" wanted "[[:space:]]*$" {
      value = $2
      sub(/^[[:space:]]+/, "", value)
      sub(/[[:space:]]+$/, "", value)
      print value
      exit
    }
  ' "$file"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --system-type)
      [[ $# -ge 2 ]] || fail "--system-type requires a value"
      SYSTEM_TYPE="${2^^}"
      shift 2
      ;;
    --system-channel)
      [[ $# -ge 2 ]] || fail "--system-channel requires a value"
      SYSTEM_CHANNEL="$2"
      shift 2
      ;;
    --vendor-channel)
      [[ $# -ge 2 ]] || fail "--vendor-channel requires a value"
      VENDOR_CHANNEL="$2"
      shift 2
      ;;
    --force-init)
      FORCE_INIT=1
      shift
      ;;
    --skip-firewall)
      CONFIGURE_FIREWALL=0
      shift
      ;;
    --skip-host-policy)
      CONFIGURE_HOST_POLICY=0
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --acknowledge-untested)
      ACKNOWLEDGE_UNTESTED=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "Unknown option: $1"
      ;;
  esac
done

warn "REFERENCE ONLY: this installer has not been tested end to end on a clean Fedora installation."
if [[ "$DRY_RUN" -eq 0 && "$ACKNOWLEDGE_UNTESTED" -eq 0 ]]; then
  fail "Review the script and rerun with --acknowledge-untested to permit changes."
fi

case "$SYSTEM_TYPE" in
  GAPPS|VANILLA|FOSS) ;;
  *) fail "Unsupported system type: $SYSTEM_TYPE (expected GAPPS, VANILLA, or FOSS)" ;;
esac

[[ -r /etc/os-release ]] || fail "Cannot read /etc/os-release"
# shellcheck disable=SC1091
source /etc/os-release
case "${ID:-} ${ID_LIKE:-}" in
  *fedora*) ;;
  *) fail "This installer supports Fedora only (detected: ${PRETTY_NAME:-unknown})" ;;
esac

if [[ -e /run/ostree-booted ]]; then
  fail "Fedora Atomic/immutable detected. Use rpm-ostree install waydroid, reboot, then initialize Waydroid separately."
fi

require_cmd awk
require_cmd dnf
require_cmd systemctl
require_cmd uname

case "$(uname -m)" in
  x86_64) WAYDROID_ARCH="x86_64" ;;
  aarch64) WAYDROID_ARCH="arm64" ;;
  *) fail "Unsupported architecture for the official channels: $(uname -m)" ;;
esac

if [[ -z "$SYSTEM_CHANNEL" ]]; then
  SYSTEM_CHANNEL="https://ota.waydro.id/system/lineage/waydroid_${WAYDROID_ARCH}/${SYSTEM_TYPE}.json"
fi
if [[ -z "$VENDOR_CHANNEL" ]]; then
  VENDOR_CHANNEL="https://ota.waydro.id/vendor/waydroid_${WAYDROID_ARCH}/MAINLINE.json"
fi

case "$SYSTEM_CHANNEL" in
  http://*|https://*) ;;
  *) fail "System channel must be an HTTP(S) URL: $SYSTEM_CHANNEL" ;;
esac
case "$VENDOR_CHANNEL" in
  http://*|https://*) ;;
  *) fail "Vendor channel must be an HTTP(S) URL: $VENDOR_CHANNEL" ;;
esac

if [[ "$EUID" -ne 0 ]]; then
  require_cmd sudo
  ROOT_CMD=(sudo)
  if [[ "$DRY_RUN" -eq 0 ]]; then
    log "Requesting sudo credentials once before installation..."
    sudo -v
  fi
fi

log "Waydroid Fedora installer"
log "  Host: ${PRETTY_NAME:-Fedora} ($(uname -m))"
log "  System type: $SYSTEM_TYPE"
log "  System channel: $SYSTEM_CHANNEL"
log "  Vendor channel: $VENDOR_CHANNEL"
log "  Firewalld: $([[ "$CONFIGURE_FIREWALL" -eq 1 ]] && printf enabled || printf skipped)"
log "  Dry run: $([[ "$DRY_RUN" -eq 1 ]] && printf yes || printf no)"

log "Installing the Fedora Waydroid package..."
run_root dnf install -y waydroid

if [[ "$DRY_RUN" -eq 0 ]]; then
  require_cmd waydroid
fi

readonly WAYDROID_CONFIG="/var/lib/waydroid/waydroid.cfg"
readonly WAYDROID_SYSTEM_IMAGE="/var/lib/waydroid/images/system.img"
readonly WAYDROID_VENDOR_IMAGE="/var/lib/waydroid/images/vendor.img"

INITIALIZED=0
if [[ -f "$WAYDROID_CONFIG" && -f "$WAYDROID_SYSTEM_IMAGE" && -f "$WAYDROID_VENDOR_IMAGE" ]]; then
  INITIALIZED=1
fi

if [[ "$INITIALIZED" -eq 1 && "$FORCE_INIT" -eq 0 ]]; then
  log "Waydroid is already initialized; leaving its images and data unchanged."
  EXISTING_SYSTEM_CHANNEL="$(read_ini_value "$WAYDROID_CONFIG" system_ota || true)"
  EXISTING_VENDOR_CHANNEL="$(read_ini_value "$WAYDROID_CONFIG" vendor_ota || true)"

  if [[ -n "$EXISTING_SYSTEM_CHANNEL" && "$EXISTING_SYSTEM_CHANNEL" != "$SYSTEM_CHANNEL" ]]; then
    warn "Existing system channel differs: $EXISTING_SYSTEM_CHANNEL"
    warn "Use --force-init only when you intentionally want to reinitialize."
  fi
  if [[ -n "$EXISTING_VENDOR_CHANNEL" && "$EXISTING_VENDOR_CHANNEL" != "$VENDOR_CHANNEL" ]]; then
    warn "Existing vendor channel differs: $EXISTING_VENDOR_CHANNEL"
    warn "Use --force-init only when you intentionally want to reinitialize."
  fi
else
  if [[ "$FORCE_INIT" -eq 1 ]]; then
    warn "Forced initialization requested; existing Waydroid images may be replaced."
    log "Stopping the Waydroid container before forced initialization..."
    if [[ "$DRY_RUN" -eq 1 ]] || systemctl is-active --quiet waydroid-container.service; then
      run_root waydroid container stop
    fi
  fi

  INIT_ARGS=(
    waydroid init
    --system_type "$SYSTEM_TYPE"
    --system_channel "$SYSTEM_CHANNEL"
    --vendor_channel "$VENDOR_CHANNEL"
  )
  if [[ "$FORCE_INIT" -eq 1 ]]; then
    INIT_ARGS+=(--force)
  fi

  log "Initializing Waydroid images..."
  run_root "${INIT_ARGS[@]}"
fi

log "Enabling and starting waydroid-container.service..."
run_root systemctl enable --now waydroid-container.service

FIREWALL_CHANGED=0
if [[ "$CONFIGURE_FIREWALL" -eq 1 ]]; then
  if ! command -v firewall-cmd >/dev/null 2>&1; then
    warn "firewalld is not installed; skipping firewall configuration."
  elif ! systemctl is-active --quiet firewalld.service; then
    warn "firewalld is not active; skipping firewall configuration."
  elif [[ "$DRY_RUN" -eq 1 ]]; then
    log "Would ensure the permanent firewalld configuration:"
    run_root firewall-cmd --permanent --zone=trusted --change-interface="$WAYDROID_INTERFACE"
    if [[ "$CONFIGURE_HOST_POLICY" -eq 1 ]]; then
      run_root firewall-cmd --permanent --new-policy="$POLICY_NAME"
      run_root firewall-cmd --permanent --policy="$POLICY_NAME" --add-ingress-zone=trusted
      run_root firewall-cmd --permanent --policy="$POLICY_NAME" --add-egress-zone=HOST
      run_root firewall-cmd --permanent --policy="$POLICY_NAME" --set-target=ACCEPT
    fi
    run_root firewall-cmd --reload
  else
    log "Configuring firewalld for $WAYDROID_INTERFACE..."
    CURRENT_ZONE="$(root_capture firewall-cmd --permanent --get-zone-of-interface="$WAYDROID_INTERFACE" 2>/dev/null || true)"
    if [[ "$CURRENT_ZONE" != "trusted" ]]; then
      run_root firewall-cmd --permanent --zone=trusted --change-interface="$WAYDROID_INTERFACE"
      FIREWALL_CHANGED=1
    else
      log "  $WAYDROID_INTERFACE is already assigned to the trusted zone."
    fi

    if [[ "$CONFIGURE_HOST_POLICY" -eq 1 ]]; then
      EXISTING_POLICIES="$(root_capture firewall-cmd --permanent --get-policies)"
      if ! contains_word "$EXISTING_POLICIES" "$POLICY_NAME"; then
        run_root firewall-cmd --permanent --new-policy="$POLICY_NAME"
        FIREWALL_CHANGED=1
      fi

      if ! root_capture firewall-cmd --permanent --policy="$POLICY_NAME" --query-ingress-zone=trusted >/dev/null; then
        run_root firewall-cmd --permanent --policy="$POLICY_NAME" --add-ingress-zone=trusted
        FIREWALL_CHANGED=1
      fi
      if ! root_capture firewall-cmd --permanent --policy="$POLICY_NAME" --query-egress-zone=HOST >/dev/null; then
        run_root firewall-cmd --permanent --policy="$POLICY_NAME" --add-egress-zone=HOST
        FIREWALL_CHANGED=1
      fi

      POLICY_TARGET="$(root_capture firewall-cmd --permanent --policy="$POLICY_NAME" --get-target)"
      if [[ "$POLICY_TARGET" != "ACCEPT" ]]; then
        run_root firewall-cmd --permanent --policy="$POLICY_NAME" --set-target=ACCEPT
        FIREWALL_CHANGED=1
      fi
    fi

    if [[ "$FIREWALL_CHANGED" -eq 1 ]]; then
      run_root firewall-cmd --reload
    else
      log "  Permanent firewalld configuration is already current."
    fi
  fi
fi

if [[ "$DRY_RUN" -eq 0 ]]; then
  systemctl is-active --quiet waydroid-container.service \
    || fail "waydroid-container.service is not active after setup"
  log "Verified: waydroid-container.service is active."
fi

if [[ "${XDG_SESSION_TYPE:-}" != "wayland" ]]; then
  warn "A Wayland desktop session is required to run the Waydroid UI."
fi

cat <<'NEXT_STEPS'

Installation setup is complete.

Run these commands as your normal desktop user from a Wayland session:

  waydroid session start
  waydroid show-full-ui

Docker was not modified. The supplied setup notes did not include the intended
/etc/docker/daemon.json content, and replacing that file can disrupt existing
Docker networks and published ports.
NEXT_STEPS
