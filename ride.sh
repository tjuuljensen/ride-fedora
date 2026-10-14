#!/usr/bin/env bash
# RIDE Linux v3 development client. System changes are explicit and journaled.
set -euo pipefail

RIDE_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
RIDE_CATALOG=${RIDE_CATALOG_PATH:-$RIDE_ROOT/catalog/operations.json}
RIDE_ALLOW_CANDIDATE=0
RIDE_DRY_RUN=0
RIDE_RUN_FILE=

# These are trusted repository modules; catalog and profile JSON are never sourced.
# shellcheck source=lib/v3/common.sh
source "$RIDE_ROOT/lib/v3/common.sh"
# shellcheck source=lib/v3/catalog.sh
source "$RIDE_ROOT/lib/v3/catalog.sh"
# shellcheck source=lib/v3/providers.sh
source "$RIDE_ROOT/lib/v3/providers.sh"
# shellcheck source=lib/v3/state.sh
source "$RIDE_ROOT/lib/v3/state.sh"
# shellcheck source=lib/v3/github.sh
source "$RIDE_ROOT/lib/v3/github.sh"
trap 'ride_journal_finalize_on_exit "$?"' EXIT

ride_help() {
  cat <<'HELP'
RIDE Linux 3.0.0 — explicit, catalog-driven setup

Usage: ./ride.sh <command> [argument] [options]
  list [all|packages|artifacts|settings|profiles|groups]
  search <literal query>
  show <operation-id>
  plan [--profile name-or-path]
  apply [--profile name-or-path]
  download <package-or-artifact-id> [--destination directory]
  install <package-id>
  set <setting-id> --state <declared-state>
  unset <setting-id>
  status [operation-id] [--profile name-or-path]
  restore --run-id <id>
  remove <package-id> | remove --profile name-or-path
  completion bash

Options: --dry-run previews state-changing commands; --allow-candidate enables
development-only operations without VM acceptance. System changes need sudo.
No command defaults to list. Profiles and catalog are JSON data, never shell.
HELP
}

ride_list() {
  local view=${1:-all}
  if [[ "$view" == profiles ]]; then
    local file
    for file in "$RIDE_ROOT"/profiles/*.json; do
      [[ -f "$file" ]] || continue
      jq -r '[.id, .description] | @tsv' "$file"
    done
    return
  fi
  case "$view" in all|packages|artifacts|settings|groups) ;; *) ride_die "unknown list view: $view" ;; esac
  if [[ "$view" == groups ]]; then
    jq -r '.operations | group_by(.group)[] | [.[0].group, (length | tostring)] | @tsv' "$RIDE_CATALOG"
    return
  fi
  jq -r --arg view "$view" '
    .operations[] | select($view == "all" or
      ($view == "packages" and .kind == "package") or
      ($view == "artifacts" and .kind == "artifact") or
      ($view == "settings" and .kind == "setting")) |
    [.id, .status, .name] | @tsv
  ' "$RIDE_CATALOG"
}

ride_search() {
  local query=${1:-}
  [[ -n "$query" ]] || ride_die "search requires a literal query"
  jq -r --arg q "$query" '
    .operations[] | select(([.id, .name, .description, .group, .productId] |
      map(ascii_downcase) | join(" ") | contains($q | ascii_downcase))) |
    [.id, .name, .description] | @tsv
  ' "$RIDE_CATALOG"
}

ride_show() {
  local id=${1:-} entry current
  [[ -n "$id" ]] || ride_die "show requires an operation ID"
  entry=$(ride_entry_or_die "$id")
  if jq -e --arg os "$RIDE_OS_ID" --arg arch "$RIDE_ARCH" --arg release "$RIDE_OS_VERSION" \
      '.targets[$os] as $t | $t != null and ($t.releases | index($release) != null) and ($t.architectures | index($arch) != null)' \
      <<< "$entry" >/dev/null; then
    current=$(ride_observe "$entry")
  else
    current=unsupported
  fi
  jq --arg observed "$current" '. + {observedState:$observed}' <<< "$entry"
}

ride_plan_entry() {
  local id=$1 desired=$2 entry current status
  entry=$(ride_entry_or_die "$id")
  ride_require_target "$entry"
  jq -e --arg desired "$desired" '.states | index($desired) != null' <<< "$entry" >/dev/null ||
    ride_die "invalid state $desired for $id"
  current=$(ride_observe "$entry")
  status=$(jq -r '.status' <<< "$entry")
  printf '%s\t%s\t%s\t%s\n' "$id" "$current" "$desired" "$status"
}

ride_plan_profile() {
  local profile=$1 id desired
  ride_validate_profile "$profile"
  printf 'ID\tCURRENT\tDESIRED\tSTATUS\n'
  while IFS=$'\t' read -r id desired; do
    [[ -z "$id" ]] && continue
    ride_plan_entry "$id" "$desired"
  done < <(jq -r '.operations[] | [.id, .state] | @tsv' "$profile")
}

ride_preflight_change() {
  local entry=$1 desired=$2 id
  id=$(jq -r '.id' <<< "$entry")
  ride_require_target "$entry"
  ride_require_accepted "$entry"
  jq -e --arg desired "$desired" '.states | index($desired) != null' <<< "$entry" >/dev/null ||
    ride_die "invalid state $desired for $id"
  ride_require_privilege "$entry"
}

ride_apply_one() {
  local entry=$1 desired=$2 id before after step recovery
  id=$(jq -r '.id' <<< "$entry")
  recovery=$(jq -r '.recovery' <<< "$entry")
  before=$(ride_observe "$entry")
  step=$(jq -nc --arg id "$id" --arg before "$before" --arg desired "$desired" --arg recovery "$recovery" \
    '{id:$id, observedBefore:$before, desired:$desired, recovery:$recovery, result:"pending"}')
  ride_journal_append "$step"
  if [[ "$before" == "$desired" ]]; then
    ride_journal_update_last unchanged "$before"
    printf 'unchanged %s (%s)\n' "$id" "$before"
    return
  fi
  if ! ride_dependencies_ready "$entry"; then
    ride_journal_update_last failed "$before"
    ride_journal_finish failed
    ride_error "dependency is unavailable for $id"
    return 1
  fi
  if ! ride_change "$entry" "$desired"; then
    ride_journal_update_last failed unknown
    ride_journal_finish failed
    ride_error "change failed: $id"
    return 1
  fi
  if ! after=$(ride_observe "$entry"); then
    ride_journal_update_last failed unknown
    ride_journal_finish failed
    ride_error "cannot verify changed state: $id"
    return 1
  fi
  if [[ "$after" != "$desired" ]]; then
    ride_journal_update_last failed "$after"
    ride_journal_finish failed
    ride_error "desired state was not reached for $id (observed $after)"
    return 1
  fi
  ride_journal_update_last changed "$after"
  printf 'changed %s: %s -> %s\n' "$id" "$before" "$after"
}

ride_apply_profile() {
  local profile=$1 id desired entry
  ride_validate_profile "$profile"
  if [[ "$RIDE_DRY_RUN" == 1 ]]; then ride_plan_profile "$profile"; return; fi
  # Validate every target, desired state and privilege before the first mutation.
  while IFS=$'\t' read -r id desired; do
    [[ -z "$id" ]] && continue
    entry=$(ride_entry_or_die "$id")
    ride_preflight_change "$entry" "$desired"
  done < <(jq -r '.operations[] | [.id, .state] | @tsv' "$profile")
  ride_journal_create apply
  while IFS=$'\t' read -r id desired; do
    [[ -z "$id" ]] && continue
    entry=$(ride_entry_or_die "$id")
    ride_apply_one "$entry" "$desired" || return 1
  done < <(jq -r '.operations[] | [.id, .state] | @tsv' "$profile")
  ride_journal_finish complete
}

ride_apply_single() {
  local id=$1 desired=$2 entry
  entry=$(ride_entry_or_die "$id")
  if [[ "$RIDE_DRY_RUN" == 1 ]]; then
    ride_plan_entry "$id" "$desired"
    return
  fi
  ride_preflight_change "$entry" "$desired"
  ride_journal_create single
  ride_apply_one "$entry" "$desired" || return 1
  ride_journal_finish complete
}

ride_restore() {
  local original_id=$1 original id before after result entry current recovery
  [[ -n "$original_id" ]] || ride_die "restore requires --run-id"
  original=$(ride_journal_by_id "$original_id")
  if ride_journal_has_completed_restore "$original_id"; then
    ride_die "run has already been restored: $original_id"
  fi
  # Refuse a conflicting machine state before restoring any step.
  while IFS=$'\t' read -r id before after result; do
    [[ "$result" == changed ]] || continue
    entry=$(ride_entry_or_die "$id")
    recovery=$(jq -r '.recovery' <<< "$entry")
    if [[ "$recovery" == none || ( "$recovery" == remove-new-install && ( "$before" != absent || "$after" != installed ) ) ]]; then
      ride_die "exact recovery is unavailable for $id ($before -> $after)"
    fi
    if [[ "$RIDE_DRY_RUN" != 1 ]]; then ride_preflight_change "$entry" "$before"; fi
    current=$(ride_observe "$entry")
    [[ "$current" == "$after" || "$current" == "$before" ]] ||
      ride_die "restore conflict for $id: expected $after, observed $current"
  done < <(jq -r '.steps | reverse[] | [.id, .observedBefore, .observedAfter, .result] | @tsv' "$original")
  if [[ "$RIDE_DRY_RUN" == 1 ]]; then
    while IFS=$'\t' read -r id before after result; do
      [[ "$result" == changed ]] || continue
      ride_plan_entry "$id" "$before"
    done < <(jq -r '.steps | reverse[] | [.id, .observedBefore, .observedAfter, .result] | @tsv' "$original")
    return
  fi
  ride_journal_create "restore:$original_id"
  while IFS=$'\t' read -r id before after result; do
    [[ "$result" == changed ]] || continue
    entry=$(ride_entry_or_die "$id")
    ride_apply_one "$entry" "$before" || return 1
  done < <(jq -r '.steps | reverse[] | [.id, .observedBefore, .observedAfter, .result] | @tsv' "$original")
  ride_journal_finish complete
}

ride_remove_profile() {
  local profile=$1 id entry
  ride_validate_profile "$profile"
  if [[ "$RIDE_DRY_RUN" == 1 ]]; then
    while IFS= read -r id; do ride_plan_entry "$id" absent; done < <(jq -r '.operations | reverse[] | .id' "$profile")
    return
  fi
  while IFS= read -r id; do
    [[ -z "$id" ]] && continue
    entry=$(ride_entry_or_die "$id")
    ride_preflight_change "$entry" absent
  done < <(jq -r '.operations | reverse[] | .id' "$profile")
  ride_journal_create remove-profile
  while IFS= read -r id; do
    [[ -z "$id" ]] && continue
    entry=$(ride_entry_or_die "$id")
    ride_apply_one "$entry" absent || return 1
  done < <(jq -r '.operations | reverse[] | .id' "$profile")
  ride_journal_finish complete
}

ride_status() {
  local id=${1:-} entry current
  printf 'ID\tOBSERVED\tSTATUS\n'
  if [[ -n "$id" ]]; then
    entry=$(ride_entry_or_die "$id")
    ride_require_target "$entry"
    current=$(ride_observe "$entry")
    printf '%s\t%s\t%s\n' "$id" "$current" "$(jq -r '.status' <<< "$entry")"
  else
    while IFS= read -r id; do
      entry=$(ride_entry_or_die "$id")
      if jq -e --arg os "$RIDE_OS_ID" --arg arch "$RIDE_ARCH" --arg release "$RIDE_OS_VERSION" \
          '.targets[$os] as $t | $t != null and ($t.releases | index($release) != null) and ($t.architectures | index($arch) != null)' \
          <<< "$entry" >/dev/null; then
        current=$(ride_observe "$entry")
      else
        current=unsupported
      fi
      printf '%s\t%s\t%s\n' "$id" "$current" "$(jq -r '.status' <<< "$entry")"
    done < <(jq -r '.operations[].id' "$RIDE_CATALOG")
  fi
}

ride_main() {
  local command=${1:-list} argument= profile=default profile_set=0 desired= run_id= destination=
  if [[ $# -gt 0 ]]; then shift; fi
  case "$command" in
    -h|--help|help) ride_help; return ;;
    -v|--version|version) printf 'RIDE Linux 3.0.0\n'; return ;;
  esac
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --profile) [[ $# -ge 2 ]] || ride_die "--profile needs a value"; profile=$2; profile_set=1; shift 2 ;;
      --state) [[ $# -ge 2 ]] || ride_die "--state needs a value"; desired=$2; shift 2 ;;
      --run-id) [[ $# -ge 2 ]] || ride_die "--run-id needs a value"; run_id=$2; shift 2 ;;
      --destination) [[ $# -ge 2 ]] || ride_die "--destination needs a value"; destination=$2; shift 2 ;;
      --allow-candidate) RIDE_ALLOW_CANDIDATE=1; shift ;;
      --dry-run) RIDE_DRY_RUN=1; shift ;;
      --*) ride_die "unknown option: $1" ;;
      *) [[ -z "$argument" ]] || ride_die "unexpected argument: $1"; argument=$1; shift ;;
    esac
  done
  ride_require_command jq
  ride_platform
  ride_validate_catalog
  case "$command" in
    list) ride_list "${argument:-all}" ;;
    search) ride_search "$argument" ;;
    show) ride_show "$argument" ;;
    plan) [[ -z "$argument" ]] || ride_die "plan takes --profile, not a positional argument"; ride_plan_profile "$(ride_profile_path "$profile")" ;;
    apply) [[ -z "$argument" ]] || ride_die "apply takes --profile, not a positional argument"; ride_apply_profile "$(ride_profile_path "$profile")" ;;
    download)
      [[ -n "$argument" ]] || ride_die "download requires a package ID"
      local entry
      entry=$(ride_entry_or_die "$argument")
      ride_require_target "$entry"
      [[ "$(jq -r '.kind' <<< "$entry")" == package || "$(jq -r '.kind' <<< "$entry")" == artifact ]] ||
        ride_die "download requires a package or artifact operation"
      case "$(jq -r '.handler' <<< "$entry")" in
        dnf-package|github-asset) ;;
        *) ride_die "download unsupported for this handler" ;;
      esac
      [[ "$RIDE_DRY_RUN" == 0 ]] || { printf 'would download %s\n' "$argument"; return; }
      ride_require_accepted "$entry"
      case "$(jq -r '.handler' <<< "$entry")" in
        dnf-package) ride_download_package "$entry" "${destination:-$(ride_cache_dir)/artifacts/$argument}" ;;
        github-asset) ride_github_download_asset "$entry" "${destination:-$(ride_cache_dir)/artifacts/$argument}" ;;
        *) ride_die "download unsupported for this handler" ;;
      esac
      ;;
    install)
      [[ "$(jq -r '.kind' <<< "$(ride_entry_or_die "$argument")")" == package ]] || ride_die "install requires a package ID"
      ride_apply_single "$argument" installed
      ;;
    set)
      [[ "$(jq -r '.kind' <<< "$(ride_entry_or_die "$argument")")" == setting ]] || ride_die "set requires a setting ID"
      [[ -n "$desired" ]] || ride_die "set requires --state"
      ride_apply_single "$argument" "$desired"
      ;;
    unset)
      [[ "$(jq -r '.kind' <<< "$(ride_entry_or_die "$argument")")" == setting ]] || ride_die "unset requires a setting ID"
      ride_apply_single "$argument" disabled
      ;;
    status)
      if [[ "$profile_set" == 1 ]]; then
        [[ -z "$argument" ]] || ride_die "status takes an ID or --profile, not both"
        ride_plan_profile "$(ride_profile_path "$profile")"
      else
        ride_status "$argument"
      fi
      ;;
    restore) ride_restore "$run_id" ;;
    remove)
      if [[ -n "$argument" ]]; then
        [[ "$(jq -r '.kind' <<< "$(ride_entry_or_die "$argument")")" == package ]] || ride_die "remove requires a package ID"
        ride_apply_single "$argument" absent
      else
        ride_remove_profile "$(ride_profile_path "$profile")"
      fi
      ;;
    completion)
      [[ "$argument" == bash ]] || ride_die "only Bash completion is supported"
      cat "$RIDE_ROOT/completion/ride.bash"
      ;;
    *) ride_die "unknown command: $command" ;;
  esac
}

ride_main "$@"
