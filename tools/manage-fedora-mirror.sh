#!/usr/bin/env bash
# Purpose: Create, update, inspect, and verify local Fedora DNF repository mirrors.
#
# Behavior: Uses DNF5 reposync with metadata and RPM signature checks. Before
#           syncing Fedora repositories, checks that the target key is in RPM's
#           keyring. Sync does not prune RPMs omitted from upstream metadata.
#
# Compatibility: Bash 4+, Fedora systems with DNF5; not a POSIX sh script.
#
# Usage: tools/manage-fedora-mirror.sh {list|plan|sync|verify} [options]
#
# Inputs / environment: Fedora release, architecture, destination path, and
#                       selected repository IDs; host Fedora keys and RPM keyring.
#
# Outputs / side effects: sync downloads repository data and writes a TSV sync
#                         manifest; list, plan, and verify are read-only.
#
# Prerequisites: Bash, DNF5, dnf5-plugins, gpg, rpmkeys, awk, and coreutils.
#
# Author: RIDE Linux contributors.
#
# Version: 1.0.1
#
# Changelog: 1.0.1 - Check Fedora key trust early and remove the sync lock on exit.
#            1.0.0 - Initial standalone mirror manager.

set -o nounset
set -o pipefail

readonly SCRIPT_VERSION=1.0.1
readonly DEFAULT_REPOS=(fedora updates)

usage() {
  cat <<'USAGE'
Usage:
  manage-fedora-mirror.sh list --releasever VERSION
  manage-fedora-mirror.sh plan --releasever VERSION --arch ARCH --destination DIR [--repo ID ...]
  manage-fedora-mirror.sh sync --releasever VERSION --arch ARCH --destination DIR \
      --min-free-gib GIB [--repo ID ...] [--yes]
  manage-fedora-mirror.sh verify --releasever VERSION --arch ARCH --destination DIR [--repo ID ...]
  manage-fedora-mirror.sh --help | --version

Commands:
  list    Show enabled repositories for a Fedora release value.
  plan    Show selected repositories, local mirror size, and available space.
  sync    Create or update the selected mirror in place. Requires an explicit
          free-space floor; asks for confirmation unless --yes is given.
  verify  Check that each selected local repo has metadata and RPM files.

Options:
  --releasever VERSION  Target Fedora release, for example 44 or 45.
  --arch ARCH           Target package architecture, for example x86_64.
  --destination DIR     Mirror root; repository data is stored under
                        DIR/VERSION/ARCH/REPO_ID.
  --repo ID             Repository ID to include; repeat for multiple repos.
                        Defaults to fedora and updates.
  --min-free-gib GIB    Minimum currently free space required before sync.
                        This is a user-selected floor, not a mirror-size estimate.
  --yes                 Skip the interactive sync confirmation.
  -h, --help            Show this help.
  --version             Show the tool version.

The tool does not enable repositories, import signing keys, edit system DNF
configuration, or delete old data. Sync requires the selected Fedora release's
signing key in the RPM keyring. Check Fedora 45 and later repository definitions
with `list --releasever VERSION` before syncing. Third-party repositories may
not publish content for every Fedora release.
USAGE
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 2
}

note() {
  printf '%s\n' "$*" >&2
}

need_command() {
  command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
}

valid_release() {
  [[ "$1" =~ ^[0-9]{2,3}$ ]]
}

valid_arch() {
  [[ "$1" =~ ^[A-Za-z0-9_]+$ ]]
}

valid_repo() {
  [[ "$1" =~ ^[A-Za-z0-9_.+-]+$ ]]
}

parse_options() {
  RELEASEVER=
  ARCH=
  DESTINATION=
  MIN_FREE_GIB=
  ASSUME_YES=0
  REPOS=()

  while (($#)); do
    case "$1" in
      --releasever)
        (($# >= 2)) || die '--releasever requires a value'
        RELEASEVER=$2
        shift 2
        ;;
      --arch)
        (($# >= 2)) || die '--arch requires a value'
        ARCH=$2
        shift 2
        ;;
      --destination)
        (($# >= 2)) || die '--destination requires a value'
        DESTINATION=$2
        shift 2
        ;;
      --repo)
        (($# >= 2)) || die '--repo requires a value'
        REPOS+=("$2")
        shift 2
        ;;
      --min-free-gib)
        (($# >= 2)) || die '--min-free-gib requires a value'
        MIN_FREE_GIB=$2
        shift 2
        ;;
      --yes)
        ASSUME_YES=1
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      --version)
        printf '%s\n' "$SCRIPT_VERSION"
        exit 0
        ;;
      *) die "unknown option: $1" ;;
    esac
  done

  [[ -n "$RELEASEVER" ]] || die '--releasever is required'
  valid_release "$RELEASEVER" || die "invalid Fedora release: $RELEASEVER"

  if [[ -n "$ARCH" ]]; then
    valid_arch "$ARCH" || die "invalid architecture: $ARCH"
  fi

  if [[ -n "$DESTINATION" ]]; then
    [[ "$DESTINATION" == /* ]] || die '--destination must be an absolute path'
    [[ "$DESTINATION" != / ]] || die 'refusing to use / as the mirror root'
  fi

  if [[ -n "$MIN_FREE_GIB" ]]; then
    [[ "$MIN_FREE_GIB" =~ ^[0-9]+$ ]] || die '--min-free-gib must be a non-negative integer'
    ((MIN_FREE_GIB <= 1048576)) || die '--min-free-gib is too large'
  fi

  if ((${#REPOS[@]} == 0)); then
    REPOS=("${DEFAULT_REPOS[@]}")
  fi
  local repo
  for repo in "${REPOS[@]}"; do
    valid_repo "$repo" || die "invalid repository ID: $repo"
  done
}

require_target_options() {
  [[ -n "$ARCH" ]] || die '--arch is required'
  [[ -n "$DESTINATION" ]] || die '--destination is required'
}

join_repos() {
  local separator=
  local repo
  for repo in "${REPOS[@]}"; do
    printf '%s%s' "$separator" "$repo"
    separator=', '
  done
}

existing_parent() {
  local path=$1
  while [[ ! -d "$path" ]]; do
    [[ "$path" != / ]] || break
    path=${path%/*}
    [[ -n "$path" ]] || path=/
  done
  printf '%s\n' "$path"
}

available_kib() {
  local path=$1
  local existing
  existing=$(existing_parent "$path")
  df -Pk -- "$existing" | awk 'NR == 2 {print $4}'
}

tree_kib() {
  local path=$1
  if [[ -d "$path" ]]; then
    du -sk -- "$path" | awk '{print $1}'
  else
    printf '0\n'
  fi
}

format_gib() {
  awk -v kib="$1" 'BEGIN {printf "%.2f GiB", kib / 1024 / 1024}'
}

show_plan() {
  require_target_options
  need_command df
  need_command du

  local target="$DESTINATION/$RELEASEVER/$ARCH"
  local free_kib used_kib
  free_kib=$(available_kib "$target") || die 'cannot determine available destination space'
  [[ "$free_kib" =~ ^[0-9]+$ ]] || die 'df returned an unexpected available-space value'
  used_kib=$(tree_kib "$target") || die 'cannot determine existing mirror size'

  printf 'Fedora release:       %s\n' "$RELEASEVER"
  printf 'Architecture:         %s\n' "$ARCH"
  printf 'Repositories:         %s\n' "$(join_repos)"
  printf 'Mirror path:          %s\n' "$target"
  printf 'Existing tree size:   %s\n' "$(format_gib "$used_kib")"
  printf 'Available space now:  %s\n' "$(format_gib "$free_kib")"
  printf 'Space note:           this is not an estimate of the download size.\n'
  printf 'Sync mode:            incremental, in place; no RPM pruning.\n'
}

run_list() {
  need_command dnf5
  dnf5 --releasever="$RELEASEVER" repolist --enabled
}

check_fedora_key() {
  local repo
  for repo in "${REPOS[@]}"; do
    [[ "$repo" == fedora || "$repo" == updates ]] || continue

    need_command gpg
    need_command rpmkeys
    local key_file="/etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-$RELEASEVER-$ARCH"
    [[ -r "$key_file" ]] || die "Fedora signing key file is missing: $key_file"

    local fingerprint
    fingerprint=$(gpg --show-keys --with-colons "$key_file" 2>/dev/null |
      awk -F: '$1 == "fpr" {print tolower($10); exit}') || die "cannot read Fedora signing key: $key_file"
    [[ "$fingerprint" =~ ^[0-9a-f]{40}$ ]] || die "invalid Fedora signing key: $key_file"
    local keyring
    keyring=$(rpmkeys --list) || die 'cannot inspect the RPM keyring'
    if ! awk -v key="$fingerprint" 'tolower($1) == key {found = 1} END {exit !found}' <<<"$keyring"; then
      die "Fedora $RELEASEVER signing key is absent from the RPM keyring ($fingerprint). Verify its fingerprint with Fedora, then import $key_file with 'sudo rpmkeys --import $key_file' and rerun sync"
    fi
    break
  done
}

run_sync() {
  require_target_options
  [[ -n "$MIN_FREE_GIB" ]] || die 'sync requires --min-free-gib as a disk-space safety floor'
  need_command dnf5
  need_command df
  need_command mkdir
  need_command date
  check_fedora_key

  local target="$DESTINATION/$RELEASEVER/$ARCH"
  mkdir -p -- "$target" || die "cannot create mirror destination: $target"

  local free_kib min_kib
  free_kib=$(available_kib "$target") || die 'cannot determine available destination space'
  [[ "$free_kib" =~ ^[0-9]+$ ]] || die 'df returned an unexpected available-space value'
  min_kib=$((MIN_FREE_GIB * 1024 * 1024))
  printf 'Available space: %s; required floor: %s GiB\n' \
    "$(format_gib "$free_kib")" "$MIN_FREE_GIB"
  ((free_kib >= min_kib)) || die 'available space is below --min-free-gib'

  SYNC_LOCK="$target/.manage-fedora-mirror.lock"
  mkdir -- "$SYNC_LOCK" 2>/dev/null || die "another sync may be active, or a stale lock exists: $SYNC_LOCK"
  cleanup_lock() { rmdir -- "$SYNC_LOCK" 2>/dev/null || true; }
  trap cleanup_lock EXIT
  trap 'exit 130' INT
  trap 'exit 143' TERM

  printf 'Release: %s\nArchitecture: %s\nRepositories: %s\nDestination: %s\n' \
    "$RELEASEVER" "$ARCH" "$(join_repos)" "$target"
  if ((ASSUME_YES == 0)); then
    [[ -t 0 ]] || die 'non-interactive sync requires --yes'
    printf 'Update the selected mirror in place? [y/N] '
    local answer
    IFS= read -r answer || exit 1
    [[ "$answer" == y || "$answer" == Y || "$answer" == yes || "$answer" == YES ]] || {
      note 'Sync cancelled.'
      exit 1
    }
  fi

  local -a repo_args=()
  local repo
  for repo in "${REPOS[@]}"; do
    repo_args+=("--repo=$repo")
    repo_args+=("--setopt=$repo.gpgcheck=1")
  done

  dnf5 --releasever="$RELEASEVER" reposync \
    "${repo_args[@]}" \
    --arch="$ARCH" \
    --download-metadata \
    --gpgcheck \
    --destdir="$target" || die 'DNF5 reposync failed; rerun sync to complete the mirror'

  local timestamp manifest temporary
  timestamp=$(date -u '+%Y-%m-%dT%H:%M:%SZ') || die 'cannot get UTC timestamp'
  manifest="$target/.mirror-manifest.tsv"
  temporary=$(mktemp "$target/.mirror-manifest.XXXXXXXX") || die 'cannot create sync manifest'
  {
    printf 'key\tvalue\n'
    printf 'tool_version\t%s\n' "$SCRIPT_VERSION"
    printf 'synced_utc\t%s\n' "$timestamp"
    printf 'releasever\t%s\n' "$RELEASEVER"
    printf 'architecture\t%s\n' "$ARCH"
    local repo
    for repo in "${REPOS[@]}"; do
      printf 'repository\t%s\n' "$repo"
    done
  } >"$temporary" || { rm -f -- "$temporary"; die 'cannot write sync manifest'; }
  mv -f -- "$temporary" "$manifest" || { rm -f -- "$temporary"; die 'cannot install sync manifest'; }
  printf 'Mirror sync completed. Manifest: %s\n' "$manifest"
}

run_verify() {
  require_target_options
  need_command find

  local target="$DESTINATION/$RELEASEVER/$ARCH"
  local failed=0 repo path rpm_count
  for repo in "${REPOS[@]}"; do
    path="$target/$repo"
    if [[ ! -s "$path/repodata/repomd.xml" ]]; then
      printf 'FAIL %s: missing repodata/repomd.xml\n' "$repo"
      failed=1
      continue
    fi
    rpm_count=$(find "$path" -type f -name '*.rpm' -print | awk 'END {print NR}') || {
      printf 'FAIL %s: cannot scan repository files\n' "$repo"
      failed=1
      continue
    }
    if ((rpm_count == 0)); then
      printf 'FAIL %s: no RPM files found\n' "$repo"
      failed=1
    else
      printf 'OK   %s: metadata present; %s RPM files\n' "$repo" "$rpm_count"
    fi
  done

  if ((failed)); then
    return 1
  fi
  if [[ -f "$target/.mirror-manifest.tsv" ]]; then
    printf 'Manifest: %s/.mirror-manifest.tsv\n' "$target"
  else
    printf 'Manifest: absent (this mirror was not last recorded by this tool)\n'
  fi
}

main() {
  (($#)) || { usage >&2; exit 2; }
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --version) printf '%s\n' "$SCRIPT_VERSION"; exit 0 ;;
  esac

  local action=$1
  shift
  case "$action" in
    list|plan|sync|verify) ;;
    *) die "unknown command: $action" ;;
  esac

  parse_options "$@"
  case "$action" in
    list) run_list ;;
    plan) show_plan ;;
    sync) run_sync ;;
    verify) run_verify ;;
  esac
}

main "$@"
