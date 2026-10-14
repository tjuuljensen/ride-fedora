#!/bin/sh
# Purpose:
#   Download a selected RIDE Linux source release and optionally launch it.
#
# Behavior:
#   Download only by default; dependency installation and apply are explicit.
#
# Compatibility:
#   POSIX sh on Fedora, Debian, or Ubuntu; catalog support is declared separately.
#
# Usage:
#   sh docs/bootstrap.sh [--tag TAG | --branch BRANCH] [--download-only | --plan | --apply]
#
# Inputs / environment:
#   GitHub archive ref, destination, profile, and standard TMPDIR.
#
# Outputs / side effects:
#   Downloads source; optional package installation or profile changes require
#   explicit flags. A temporary directory is removed on exit.
#
# Prerequisites:
#   curl and tar; Bash and jq for the client. Dependency installation needs root.
#
# Author:
#   RIDE Fedora maintainers.
#
# Version:
#   3.0.0
#
# Changelog:
#   3.0.0: Introduce portable download-first RIDE v3 bootstrap.
set -eu

BOOTSTRAP_VERSION=3.0.0
author=tjuuljensen
repo=ride-fedora
ref=v$BOOTSTRAP_VERSION
ref_kind=tags
mode=download
profile=default
destination=
install_deps=no
allow_candidate=no
temporary=

usage() {
  cat <<HELP
Usage: sh docs/bootstrap.sh [--tag TAG | --branch BRANCH] [--destination DIR]
                       [--download-only | --plan | --apply]
                       [--profile NAME] [--install-deps] [--allow-candidate]
       sh docs/bootstrap.sh --help | --version

Defaults to downloading the v$BOOTSTRAP_VERSION tagged release into ./ride-v$BOOTSTRAP_VERSION.
--branch is for explicit development builds. --apply is the only option that
applies a profile. Installing missing Bash/jq requires --install-deps.
HELP
}

fail() { printf 'RIDE bootstrap: %s\n' "$*" >&2; exit 2; }
cleanup() { if [ -n "$temporary" ] && [ -d "$temporary" ]; then rm -rf "$temporary"; fi; }
trap cleanup 0
trap 'exit 2' 1 2 3 15

while [ "$#" -gt 0 ]; do
  case "$1" in
    --tag) [ "$#" -ge 2 ] || fail '--tag needs a value'; ref=$2; ref_kind=tags; shift 2 ;;
    --branch) [ "$#" -ge 2 ] || fail '--branch needs a value'; ref=$2; ref_kind=heads; shift 2 ;;
    --destination) [ "$#" -ge 2 ] || fail '--destination needs a value'; destination=$2; shift 2 ;;
    --download-only) mode=download; shift ;;
    --plan) mode=plan; shift ;;
    --apply) mode=apply; shift ;;
    --profile) [ "$#" -ge 2 ] || fail '--profile needs a value'; profile=$2; shift 2 ;;
    --install-deps) install_deps=yes; shift ;;
    --allow-candidate) allow_candidate=yes; shift ;;
    -h|--help) usage; exit 0 ;;
    --version) printf 'RIDE bootstrap %s\n' "$BOOTSTRAP_VERSION"; exit 0 ;;
    *) fail "unknown option: $1" ;;
  esac
done

case "$ref" in
  ''|*[!A-Za-z0-9._/-]*|*..*|/*|*/|-) fail 'invalid release ref' ;;
esac
case "$profile" in
  ''|*[!A-Za-z0-9._/-]*|*..*|/*) fail 'invalid profile name' ;;
esac

[ -r /etc/os-release ] || fail 'cannot identify this Linux distribution'
# os-release is a root-owned system file with shell-compatible assignments.
# shellcheck disable=SC1091
. /etc/os-release
case "$ID" in
  fedora|debian|ubuntu) ;;
  *) fail "distribution $ID is outside the planned Linux targets" ;;
esac

if ! command -v bash >/dev/null 2>&1 || ! command -v jq >/dev/null 2>&1; then
  if [ "$install_deps" != yes ]; then
    fail 'Bash and jq are required; install them or pass --install-deps'
  fi
  [ "$(id -u)" -eq 0 ] || fail '--install-deps requires root'
  case "$ID" in
    fedora) dnf install -y bash jq ;;
    debian|ubuntu) apt-get update && apt-get install -y bash jq ;;
  esac
fi
command -v curl >/dev/null 2>&1 || fail 'curl is required to download source'
command -v tar >/dev/null 2>&1 || fail 'tar is required to unpack source'

temporary=$(mktemp -d "${TMPDIR:-/tmp}/ride-bootstrap.XXXXXXXX") || fail 'cannot create temporary directory'
archive=$temporary/source.tar.gz
mkdir "$temporary/source"
url="https://github.com/$author/$repo/archive/refs/$ref_kind/$ref.tar.gz"
printf 'Downloading %s\n' "$url"
curl --fail --location --silent --show-error --proto '=https' --tlsv1.2 \
  --output "$archive" "$url" || fail 'download failed'
tar -tzf "$archive" >/dev/null || fail 'invalid source archive'
tar -xzf "$archive" --strip-components=1 -C "$temporary/source" || fail 'unpack failed'
[ -f "$temporary/source/ride.sh" ] || fail 'download did not contain ride.sh'

if [ "$mode" = download ]; then
  if [ -z "$destination" ]; then destination="./ride-${ref##*/}"; fi
  [ ! -e "$destination" ] || fail "destination already exists: $destination"
  mv "$temporary/source" "$destination" || fail 'cannot retain source'
  printf 'Source saved at %s\n' "$destination"
  exit 0
fi

if [ -n "$destination" ]; then
  [ ! -e "$destination" ] || fail "destination already exists: $destination"
  mv "$temporary/source" "$destination" || fail 'cannot retain source'
  ride_dir=$destination
else
  ride_dir=$temporary/source
fi
if [ "$allow_candidate" = yes ]; then
  bash "$ride_dir/ride.sh" "$mode" --profile "$profile" --allow-candidate
else
  bash "$ride_dir/ride.sh" "$mode" --profile "$profile"
fi
