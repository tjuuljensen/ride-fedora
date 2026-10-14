#!/usr/bin/env bash
# Purpose:
#   Verify executable Git modes for tracked shell scripts.
#
# Behavior:
#   Read the Git index and report each tracked .sh file without mode 100755.
#   Do not change files or the index.
#
# Compatibility:
#   Bash on Linux; checks repository metadata, not host filesystem access.
#
# Usage:
#   tools/check-shell-executable.sh [--help | --version]
#
# Inputs / environment:
#   Git index in the repository containing this script.
#
# Outputs / side effects:
#   Print validation results; exit nonzero on invalid modes. Read-only.
#
# Prerequisites:
#   Bash and Git. Run from any working directory.
#
# Author:
#   RIDE Fedora maintainers.
#
# Based on:
#   https://github.com/tjuuljensen/network-devices/blob/master/tools/check-shell-executable.sh
#
# Version:
#   0.1.0
#
# Changelog:
#   0.1.0: Add Git-index mode validation for this repository.

set -euo pipefail
SCRIPT_VERSION=0.1.0

if [[ $# -gt 1 ]]; then
  printf 'Only one option is accepted.\n' >&2
  exit 2
fi
case "${1:-}" in
  --help)
    printf 'Usage: tools/check-shell-executable.sh [--help | --version]\n'
    exit 0
    ;;
  --version)
    printf 'check-shell-executable %s\n' "$SCRIPT_VERSION"
    exit 0
    ;;
  '') ;;
  *)
    printf 'Unknown option: %s\n' "$1" >&2
    exit 2
    ;;
esac

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo_root=$(git -C "$script_dir" rev-parse --show-toplevel)
invalid=()

while IFS= read -r -d '' entry; do
  metadata=${entry%%$'\t'*}
  path=${entry#*$'\t'}
  mode=${metadata%% *}
  if [[ "$mode" != 100755 ]]; then
    invalid+=("$path")
  fi
done < <(git -C "$repo_root" ls-files --stage -z -- '*.sh')

if (( ${#invalid[@]} > 0 )); then
  printf 'Tracked .sh files without Git mode 100755:\n' >&2
  printf '  %s\n' "${invalid[@]}" >&2
  printf 'Stage a mode fix with: git update-index --chmod=+x -- <path>\n' >&2
  exit 1
fi

printf 'All tracked .sh files have Git mode 100755.\n'
