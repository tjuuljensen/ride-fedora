#!/usr/bin/env bash
# Purpose:
#   Apply declared Linux workstation and server operations through RIDE v3.
#
# Behavior:
#   List operations by default; align interactive tables; plan without changes;
#   journal explicit changes.
#
# Compatibility:
#   Bash on Linux. Supported package targets are Fedora 44 x86_64 editions;
#   other catalog entries remain candidates.
#
# Usage:
#   ./ride.sh [command] [options]; run ./ride.sh --help for commands.
#
# Inputs / environment:
#   JSON catalog and profiles; optional RIDE_GITHUB_TOKEN for release metadata.
#
# Outputs / side effects:
#   Status output, private run state/cache, package or settings changes only
#   from explicit commands. System operations require root.
#
# Prerequisites:
#   Bash and jq; operation-specific tools are checked by trusted handlers.
#
# Author:
#   RIDE Fedora maintainers.
#
# Version:
#   3.0.0
#
# Changelog:
#   3.0.0: Begin catalog-driven Linux client development.
set -euo pipefail

RIDE_VERSION=3.0.0
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
# shellcheck source=lib/v3/email_header_analyzer.sh
source "$RIDE_ROOT/lib/v3/email_header_analyzer.sh"
# shellcheck source=lib/v3/ssh_reboot.sh
source "$RIDE_ROOT/lib/v3/ssh_reboot.sh"
# shellcheck source=lib/v3/firefox.sh
source "$RIDE_ROOT/lib/v3/firefox.sh"
# shellcheck source=lib/v3/bash_aliases.sh
source "$RIDE_ROOT/lib/v3/bash_aliases.sh"
# shellcheck source=lib/v3/chrome_preferences.sh
source "$RIDE_ROOT/lib/v3/chrome_preferences.sh"
# shellcheck source=lib/v3/clamav.sh
source "$RIDE_ROOT/lib/v3/clamav.sh"
# shellcheck source=lib/v3/wireguard.sh
source "$RIDE_ROOT/lib/v3/wireguard.sh"
# shellcheck source=lib/v3/networkmanager-vpn-profiles.sh
source "$RIDE_ROOT/lib/v3/networkmanager-vpn-profiles.sh"
# shellcheck source=lib/v3/expressvpn.sh
source "$RIDE_ROOT/lib/v3/expressvpn.sh"
# shellcheck source=lib/v3/keyfile_mounts.sh
source "$RIDE_ROOT/lib/v3/keyfile_mounts.sh"
# shellcheck source=lib/v3/flatpak.sh
source "$RIDE_ROOT/lib/v3/flatpak.sh"
# shellcheck source=lib/v3/rpmfusion.sh
source "$RIDE_ROOT/lib/v3/rpmfusion.sh"
# shellcheck source=lib/v3/state.sh
source "$RIDE_ROOT/lib/v3/state.sh"
# shellcheck source=lib/v3/github.sh
source "$RIDE_ROOT/lib/v3/github.sh"
trap 'ride_journal_finalize_on_exit "$?"' EXIT

ride_help() {
  cat <<HELP
RIDE Linux $RIDE_VERSION - explicit, catalog-driven setup

Usage: ./ride.sh <command> [argument] [options]
  list [all|packages|artifacts|settings|profiles|groups]
  search <literal query>
  show <operation-id> [--source source-id]
  show --stdin [--source source-id]  # one operation ID per input line
  plan [--profile name-or-path]
  apply [--profile name-or-path]
  download <package-or-artifact-id> [--source source-id] [--destination directory]
  install <package-id> [--source source-id]
  set <setting-id> --state <declared-state> [--value <declared-value>]
  deploy <system-operation-id> --state <declared-state>
  update <system-operation-id>
  unset <setting-id>
  status [operation-id] [--source source-id] [--value declared-value] [--profile name-or-path]
  status --id <operation-id> | --view <view> [--profile name-or-path]
  restore --run-id <id>
  remove <package-id> [--source source-id] | remove --profile name-or-path
  completion bash

Options: --dry-run previews state-changing commands; --allow-candidate enables
development-only operations without VM acceptance. System changes need sudo.
unset uses only a catalog-declared unset state. Profile removal removes only
reversible packages; settings remain in place. remove requires an ID or profile.
No command defaults to list. Profiles and catalog are JSON data, never shell.
Package source selection is explicit; profiles may declare a source per package.
Download does not install. Installing from a retained local artifact is pending.
Interactive tables use column when available; redirected output remains TSV.
HELP
}

ride_table() {
  local header=${1:-}
  if [[ -t 1 ]]; then
    if command -v column >/dev/null 2>&1; then
      if [[ -n "$header" ]]; then
        { printf '%s\n' "$header"; cat; } | column -t -s $'\t'
      else
        column -t -s $'\t'
      fi
    else
      [[ -z "$header" ]] || printf '%s\n' "$header"
      cat
    fi
  else
    cat
  fi
}

ride_list() {
  local view=${1:-all}
  if [[ "$view" == profiles ]]; then
    local file
    for file in "$RIDE_ROOT"/profiles/*.json; do
      [[ -f "$file" ]] || continue
      jq -r '[.id, .description] | @tsv' "$file"
    done | ride_table $'ID\tDESCRIPTION'
    return
  fi
  case "$view" in all|packages|artifacts|settings|groups) ;; *) ride_die "unknown list view: $view" ;; esac
  if [[ "$view" == groups ]]; then
    jq -r '.operations | group_by(.group)[] | [.[0].group, (length | tostring)] | @tsv' "$RIDE_CATALOG" |
      ride_table $'GROUP\tCOUNT'
    return
  fi
  jq -r --arg view "$view" '
    .operations[] | select($view == "all" or
      ($view == "packages" and .kind == "package") or
      ($view == "artifacts" and .kind == "artifact") or
      ($view == "settings" and .kind == "setting")) |
    [.id, .status, .name] | @tsv
  ' "$RIDE_CATALOG" | ride_table $'ID\tSTATUS\tNAME'
}

ride_search() {
  local query=${1:-}
  [[ -n "$query" ]] || ride_die "search requires a literal query"
  jq -r --arg q "$query" '
    .operations[] | select(([.id, .name, .description, .group, .productId] |
      map(ascii_downcase) | join(" ") | contains($q | ascii_downcase))) |
    [.id, .name, .description] | @tsv
  ' "$RIDE_CATALOG" | ride_table $'ID\tNAME\tDESCRIPTION'
}

ride_package_noop_outside_target() {
  local entry=$1 desired=$2 handler name conflict state
  [[ "$desired" == installed && "$(jq -r '.kind' <<< "$entry")" == package &&
     "$RIDE_OS_ID" == fedora && "$(jq -r '.status' <<< "$entry")" != blocked ]] || return 1
  handler=$(jq -r '.handler' <<< "$entry")
  case "$handler" in
    dnf-package|pinned-rpm|amp-pinned-rpm|veracrypt-signed-rpm) ;;
    *) return 1 ;;
  esac
  jq -e '.states | index("installed") != null' <<< "$entry" >/dev/null || return 1
  name=$(jq -r '.packageName // empty' <<< "$entry")
  [[ "$name" =~ ^[A-Za-z0-9._+-]+$ ]] || return 1
  command -v rpm >/dev/null 2>&1 || return 1
  conflict=$(ride_provider_conflict "$entry")
  [[ -z "$conflict" ]] || return 1
  state=$(ride_observe "$entry") || return 1
  [[ "$state" == installed ]]
}

ride_show_one() {
  local id=$1 source=${2:-} compact=${3:-false} entry current conflict sources
  entry=$(ride_entry_or_die "$id" "$source")
  if ride_target_matches "$entry"; then
    current=$(ride_observe "$entry")
    conflict=$(ride_provider_conflict "$entry")
    [[ -z "$conflict" ]] || current="conflict:$conflict"
  else
    current=unsupported
  fi
  sources=$(ride_entry "$id" | jq -c 'if .kind == "package" then [.sourceId] + [.sourceProviders[]?.sourceId] else [] end')
  jq --arg observed "$current" --argjson sources "$sources" \
    '. + {schemaVersion:1, observedState:$observed, availableSources:$sources}' <<< "$entry" |
    if [[ "$compact" == true ]]; then jq -c .; else cat; fi
}

ride_show() {
  local id=${1:-} source=${2:-} stdin_mode=${3:-0} line
  if [[ "$stdin_mode" == 1 ]]; then
    while IFS= read -r line || [[ -n "$line" ]]; do
      [[ "$line" != *$'\r' ]] || line=${line%$'\r'}
      [[ -n "$line" ]] || ride_die "show --stdin received a blank operation ID"
      ride_show_one "$line" "$source" true
    done
  else
    [[ -n "$id" ]] || ride_die "show requires an operation ID or --stdin"
    ride_show_one "$id" "$source"
  fi
}

ride_plan_entry() {
  local id=$1 desired=$2 source=${3:-} value=${4:-} value_provided=${5:-false} entry current status conflict shown target_noop=0
  entry=$(ride_entry_or_die "$id" "$source" "$value" "$value_provided")
  jq -e --arg desired "$desired" '.states | index($desired) != null' <<< "$entry" >/dev/null ||
    ride_die "invalid state $desired for $id"
  if ! ride_target_matches "$entry"; then
    if ride_package_noop_outside_target "$entry" "$desired"; then target_noop=1; else ride_require_target "$entry"; fi
  fi
  if [[ "$(jq -r '.handler' <<< "$entry")" == gsettings-string || "$(jq -r '.handler' <<< "$entry")" == gnome-lock-timing || "$(jq -r '.handler' <<< "$entry")" == gnome-custom-shortcuts || "$(jq -r '.handler' <<< "$entry")" == bash-aliases || "$(jq -r '.handler' <<< "$entry")" == chrome-preferences || "$(jq -r '.handler' <<< "$entry")" == upower-threshold || "$(jq -r '.handler' <<< "$entry")" == system-hostname || "$(jq -r '.handler' <<< "$entry")" == ssh-reboot-sudoers || "$(jq -r '.handler' <<< "$entry")" == networkmanager-vpn-profiles || "$(jq -r '.handler' <<< "$entry")" == keyfile-mounts ]] &&
      [[ -z "$value" && "$(jq -r '.unsetState // ""' <<< "$entry")" != "$desired" ]]; then
    if [[ "$id" != setting.gnome-region || "$value_provided" != true ]]; then
      ride_die "configurable setting requires --value or a profile value: $id"
    fi
  fi
  current=$(ride_observe "$entry")
  conflict=$(ride_provider_conflict "$entry")
  [[ -z "$conflict" ]] || current="conflict:$conflict"
  status=$(jq -r '.status' <<< "$entry")
  [[ "$target_noop" == 0 ]] || status=unsupported
  shown=$desired
  [[ -z "$value" ]] || shown="$desired:$value"
  [[ "$id" != setting.gnome-region || "$value_provided" != true || -n "$value" ]] || shown="$desired:<empty>"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$id" \
    "$(jq -r '.sourceId // "-"' <<< "$entry")" "$current" "$shown" "$status" \
    "$(jq -r '.distribution // "-"' <<< "$entry")" \
    "$(jq -r '.deploymentId // "-"' <<< "$entry")" "$(jq -r '.scope' <<< "$entry")"
}

ride_plan_profile() {
  local profile=$1 view=${2:-all} id_filter=${3:-} id desired source value value_provided entry
  ride_validate_profile "$profile"
  if [[ -n "$id_filter" ]] && ! jq -e --arg id "$id_filter" 'any(.operations[]; .id == $id)' "$profile" >/dev/null; then
    ride_die "operation ID is not selected by profile: $id_filter"
  fi
  {
    printf 'ID\tSOURCE\tCURRENT\tDESIRED\tSTATUS\tDISTRIBUTION\tDEPLOYMENT\tSCOPE\n'
    while IFS=$'\t' read -r id desired source value value_provided; do
      [[ -z "$id" ]] && continue
      [[ "$source" != '~' ]] || source=
      [[ "$value" != '~' ]] || value=
      if [[ "$value" == __RIDE_EMPTY_VALUE__ ]]; then value=; fi
      [[ -z "$id_filter" || "$id" == "$id_filter" ]] || continue
      if [[ "$view" != all ]]; then
        entry=$(ride_entry "$id")
        ride_status_view_matches "$entry" "$view" || continue
      fi
      ride_plan_entry "$id" "$desired" "$source" "$value" "$value_provided"
    done < <(jq -r '.operations[] | [.id, .state, (.source // "~"), (if has("value") then (if .value == "" then "__RIDE_EMPTY_VALUE__" else .value end) else "~" end), (if has("value") then "true" else "false" end)] | @tsv' "$profile")
  } | ride_table
}

ride_preflight_change() {
  local entry=$1 desired=$2 id conflict
  id=$(jq -r '.id' <<< "$entry")
  RIDE_PREFLIGHT_TARGET_NOOP=0
  if ! ride_target_matches "$entry"; then
    if ride_package_noop_outside_target "$entry" "$desired"; then
      RIDE_PREFLIGHT_TARGET_NOOP=1
      return 0
    fi
    ride_require_target "$entry"
  fi
  ride_require_accepted "$entry"
  jq -e --arg desired "$desired" '.states | index($desired) != null' <<< "$entry" >/dev/null ||
    ride_die "invalid state $desired for $id"
  if [[ "$(jq -r '.handler' <<< "$entry")" == gsettings-string || "$(jq -r '.handler' <<< "$entry")" == gnome-lock-timing || "$(jq -r '.handler' <<< "$entry")" == gnome-custom-shortcuts || "$(jq -r '.handler' <<< "$entry")" == bash-aliases || "$(jq -r '.handler' <<< "$entry")" == chrome-preferences || "$(jq -r '.handler' <<< "$entry")" == upower-threshold || "$(jq -r '.handler' <<< "$entry")" == system-hostname || "$(jq -r '.handler' <<< "$entry")" == ssh-reboot-sudoers || "$(jq -r '.handler' <<< "$entry")" == networkmanager-vpn-profiles || "$(jq -r '.handler' <<< "$entry")" == keyfile-mounts ]] &&
      [[ "$(jq -r '.unsetState // ""' <<< "$entry")" != "$desired" ]]; then
    if [[ "$id" == setting.gnome-region ]]; then
      jq -e 'has("selectedValue")' <<< "$entry" >/dev/null ||
        ride_die "configurable setting requires --value or a profile value: $id"
    else
      [[ -n "$(jq -r '.selectedValue // ""' <<< "$entry")" ]] ||
        ride_die "configurable setting requires --value or a profile value: $id"
    fi
  fi
  ride_require_privilege "$entry"
  if [[ "$(jq -r '.handler' <<< "$entry")" == upower-threshold ]]; then
    ride_upower_guard "$(jq -r '.selectedValue' <<< "$entry")"
  elif [[ "$(jq -r '.handler' <<< "$entry")" == dnf5-fast-tuning ]]; then
    ride_dnf5_tuning_guard
  elif [[ "$(jq -r '.handler' <<< "$entry")" == wireguard-keypair ]]; then
    ride_wireguard_preflight
  elif [[ "$(jq -r '.handler' <<< "$entry")" == flatpak-remote ]]; then
    ride_flathub_preflight "$desired"
  elif [[ "$(jq -r '.handler' <<< "$entry")" == flatpak-app ]]; then
    ride_flatpak_halloy_preflight "$desired"
  elif [[ "$(jq -r '.handler' <<< "$entry")" == pinned-binary ]]; then
    ride_librespeed_preflight "$entry" "$desired"
  elif [[ "$(jq -r '.handler' <<< "$entry")" == rpmfusion-repositories ]]; then
    ride_rpmfusion_guard "$desired"
  elif [[ "$(jq -r '.handler' <<< "$entry")" == dnf5-system-update ]]; then
    local system_update_state
    system_update_state=$(ride_dnf5_system_update_check refresh)
    if [[ "$system_update_state" == outdated ]]; then ride_dnf5_system_update_preview; fi
  elif [[ "$(jq -r '.handler' <<< "$entry")" == docker-engine ]]; then
    if [[ "$desired" == configured ]]; then
      local docker_state
      docker_state=$(ride_docker_engine_observe "$entry")
      [[ "$docker_state" != absent ]] || ride_docker_engine_guard "$entry"
    elif [[ "$desired" == absent ]]; then
      local docker_state
      docker_state=$(ride_docker_engine_observe "$entry")
      [[ "$docker_state" == absent ]] || ride_docker_engine_remove_guard "$entry"
    fi
  elif [[ "$(jq -r '.handler' <<< "$entry")" == dnf-package-set-update ]]; then
    local update_state
    update_state=$(ride_dnf5_package_set_update_observe "$entry" refresh)
    [[ "$update_state" != no-packages ]] || ride_die "no declared Multimedia packages are installed"
    if [[ "$update_state" == outdated ]]; then
      ride_dnf5_package_set_update_preview "$entry"
    fi
  fi
  if [[ "$(jq -r '.kind' <<< "$entry")" == package ]]; then
    conflict=$(ride_provider_conflict "$entry")
    if [[ -n "$conflict" && ( "$desired" == installed || "$(ride_observe "$entry")" != installed ) ]]; then
      ride_die "another source is installed for $id: $conflict; select that source explicitly before changing this one"
    fi
  fi
}

ride_apply_one() {
  local entry=$1 desired=$2 id before after step recovery source signature conflict distribution deployment scope selected_value selected_value_present update_report
  id=$(jq -r '.id' <<< "$entry")
  recovery=$(jq -r '.recovery' <<< "$entry")
  source=$(jq -r '.sourceId // ""' <<< "$entry")
  distribution=$(jq -r '.distribution // ""' <<< "$entry")
  deployment=$(jq -r '.deploymentId // ""' <<< "$entry")
  scope=$(jq -r '.scope' <<< "$entry")
  selected_value=$(jq -r '.selectedValue // ""' <<< "$entry")
  selected_value_present=$(jq -r 'has("selectedValue")' <<< "$entry")
  RIDE_DNF5_SYSTEM_UPDATE_REPORT=
  signature=$(ride_source_signature "$entry")
  if [[ "$(jq -r '.kind' <<< "$entry")" == package ]]; then
    conflict=$(ride_provider_conflict "$entry")
    if [[ -n "$conflict" && ( "$desired" == installed || "$(ride_observe "$entry")" != installed ) ]]; then
      ride_die "another source is installed for $id: $conflict; select that source explicitly before changing this one"
    fi
  fi
  before=$(ride_observe "$entry") || ride_die "cannot observe current state for $id"
  step=$(jq -nc --arg id "$id" --arg before "$before" --arg desired "$desired" --arg recovery "$recovery" \
    --arg source "$source" --arg signature "$signature" --arg distribution "$distribution" \
    --arg deployment "$deployment" --arg scope "$scope" --arg selectedValue "$selected_value" \
    --argjson selectedValuePresent "$selected_value_present" \
    '{id:$id, distribution:$distribution, deploymentId:$deployment, scope:$scope,
      sourceId:$source, sourceSignature:$signature, sourceSignatureVersion:2,
      observedBefore:$before, desired:$desired, recovery:$recovery, result:"pending"} |
      if $selectedValuePresent then . + {selectedValue:$selectedValue} else . end')
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
    update_report=$RIDE_DNF5_SYSTEM_UPDATE_REPORT
    [[ -z "$update_report" ]] || ride_journal_update_last_report "$update_report"
    ride_journal_update_last failed unknown
    ride_journal_finish failed
    ride_error "change failed: $id"
    return 1
  fi
  update_report=$RIDE_DNF5_SYSTEM_UPDATE_REPORT
  if ! after=$(ride_observe "$entry"); then
    if [[ "$id" == setting.ibus-emoji-hotkey || "$(jq -r '.handler' <<< "$entry")" == gsettings-string || "$(jq -r '.handler' <<< "$entry")" == gnome-lock-timing || "$(jq -r '.handler' <<< "$entry")" == gnome-custom-shortcuts || "$(jq -r '.handler' <<< "$entry")" == bash-aliases || "$(jq -r '.handler' <<< "$entry")" == chrome-preferences || "$(jq -r '.handler' <<< "$entry")" == upower-threshold || "$(jq -r '.handler' <<< "$entry")" == rpmfusion-repositories || "$(jq -r '.handler' <<< "$entry")" == dnf5-fast-tuning || "$(jq -r '.handler' <<< "$entry")" == system-hostname || "$(jq -r '.handler' <<< "$entry")" == ssh-reboot-sudoers || "$(jq -r '.handler' <<< "$entry")" == networkmanager-vpn-profiles || "$(jq -r '.handler' <<< "$entry")" == keyfile-mounts ]]; then
      ride_change "$entry" "$before" || ride_error "user setting rollback failed after observation error"
    fi
    [[ -z "$update_report" ]] || ride_journal_update_last_report "$update_report"
    ride_journal_update_last failed unknown
    ride_journal_finish failed
    ride_error "cannot verify changed state: $id"
    return 1
  fi
  if [[ "$after" != "$desired" ]]; then
    if [[ "$(jq -r '.handler' <<< "$entry")" == firefox-extensions &&
          "$desired" == absent && "$after" == removal-pending ]]; then
      ride_journal_update_last pending "$after"
      RIDE_RUN_PENDING=1
      printf 'pending %s: Firefox must restart before removal can be finalized\n' "$id"
      return 0
    fi
    if [[ "$id" == setting.ibus-emoji-hotkey || "$(jq -r '.handler' <<< "$entry")" == gsettings-string || "$(jq -r '.handler' <<< "$entry")" == gnome-lock-timing || "$(jq -r '.handler' <<< "$entry")" == gnome-custom-shortcuts || "$(jq -r '.handler' <<< "$entry")" == bash-aliases || "$(jq -r '.handler' <<< "$entry")" == chrome-preferences || "$(jq -r '.handler' <<< "$entry")" == upower-threshold || "$(jq -r '.handler' <<< "$entry")" == rpmfusion-repositories || "$(jq -r '.handler' <<< "$entry")" == dnf5-fast-tuning || "$(jq -r '.handler' <<< "$entry")" == system-hostname || "$(jq -r '.handler' <<< "$entry")" == ssh-reboot-sudoers || "$(jq -r '.handler' <<< "$entry")" == networkmanager-vpn-profiles || "$(jq -r '.handler' <<< "$entry")" == keyfile-mounts ]]; then
      ride_change "$entry" "$before" || ride_error "user setting rollback failed after state mismatch"
    fi
    [[ -z "$update_report" ]] || ride_journal_update_last_report "$update_report"
    ride_journal_update_last failed "$after"
    ride_journal_finish failed
    ride_error "desired state was not reached for $id (observed $after)"
    return 1
  fi
  ride_journal_update_last changed "$after"
  [[ -z "$update_report" ]] || ride_journal_update_last_report "$update_report"
  printf 'changed %s: %s -> %s\n' "$id" "$before" "$after"
}

ride_apply_profile() {
  local profile=$1 id desired source value value_provided entry op_count=0 noop_id
  local -a target_noops=()
  ride_validate_profile "$profile"
  if [[ "$RIDE_DRY_RUN" == 1 ]]; then ride_plan_profile "$profile"; return; fi
  # Validate every target, desired state and privilege before the first mutation.
  while IFS=$'\t' read -r id desired source value value_provided; do
    [[ -z "$id" ]] && continue
    [[ "$source" != '~' ]] || source=
    [[ "$value" != '~' ]] || value=
    if [[ "$value" == __RIDE_EMPTY_VALUE__ ]]; then value=; fi
    entry=$(ride_entry_or_die "$id" "$source" "$value" "$value_provided")
    ride_preflight_change "$entry" "$desired"
    ((++op_count))
    if [[ "${RIDE_PREFLIGHT_TARGET_NOOP:-0}" == 1 ]]; then target_noops+=("$id"); fi
  done < <(jq -r '.operations[] | [.id, .state, (.source // "~"), (if has("value") then (if .value == "" then "__RIDE_EMPTY_VALUE__" else .value end) else "~" end), (if has("value") then "true" else "false" end)] | @tsv' "$profile")
  if (( op_count == ${#target_noops[@]} )); then
    for noop_id in "${target_noops[@]}"; do
      printf 'unchanged %s: already installed; target remains unsupported and no action was taken\n' "$noop_id"
    done
    return 0
  fi
  ride_journal_create apply
  RIDE_RUN_PENDING=0
  while IFS=$'\t' read -r id desired source value value_provided; do
    [[ -z "$id" ]] && continue
    [[ "$source" != '~' ]] || source=
    [[ "$value" != '~' ]] || value=
    if [[ "$value" == __RIDE_EMPTY_VALUE__ ]]; then value=; fi
    entry=$(ride_entry_or_die "$id" "$source" "$value" "$value_provided")
    if [[ " ${target_noops[*]} " == *" $id "* ]]; then
      printf 'unchanged %s: already installed; target remains unsupported and no action was taken\n' "$id"
      continue
    fi
    ride_apply_one "$entry" "$desired" || return 1
  done < <(jq -r '.operations[] | [.id, .state, (.source // "~"), (if has("value") then (if .value == "" then "__RIDE_EMPTY_VALUE__" else .value end) else "~" end), (if has("value") then "true" else "false" end)] | @tsv' "$profile")
  if [[ "${RIDE_RUN_PENDING:-0}" == 1 ]]; then ride_journal_finish pending; else ride_journal_finish complete; fi
}

ride_apply_single() {
  local id=$1 desired=$2 source=${3:-} value=${4:-} value_provided=${5:-false} entry
  entry=$(ride_entry_or_die "$id" "$source" "$value" "$value_provided")
  if [[ "$RIDE_DRY_RUN" == 1 ]]; then
    ride_plan_entry "$id" "$desired" "$source" "$value" "$value_provided" | ride_table $'ID\tSOURCE\tCURRENT\tDESIRED\tSTATUS\tDISTRIBUTION\tDEPLOYMENT\tSCOPE'
    return
  fi
  ride_preflight_change "$entry" "$desired"
  if [[ "${RIDE_PREFLIGHT_TARGET_NOOP:-0}" == 1 ]]; then
    printf 'unchanged %s: already installed; target remains unsupported and no action was taken\n' "$id"
    return 0
  fi
  ride_journal_create single
  RIDE_RUN_PENDING=0
  ride_apply_one "$entry" "$desired" || return 1
  if [[ "${RIDE_RUN_PENDING:-0}" == 1 ]]; then ride_journal_finish pending; else ride_journal_finish complete; fi
}

ride_restore_steps() {
  jq -r '.steps | reverse[] |
    [.id, .observedBefore, .observedAfter, .result,
     (if .sourceId == null or .sourceId == "" then "-" else .sourceId end),
     (.sourceSignature // "-"), (.sourceSignatureVersion // 1)] | @tsv' "$1"
}

ride_restore_entry() {
  local id=$1 source=$2 original=$3 entry value value_provided
  entry=$(ride_entry_or_die "$id" "$source")
  if [[ "$(jq -r '.handler' <<< "$entry")" == gsettings-string || "$(jq -r '.handler' <<< "$entry")" == gnome-lock-timing || "$(jq -r '.handler' <<< "$entry")" == gnome-custom-shortcuts || "$(jq -r '.handler' <<< "$entry")" == bash-aliases || "$(jq -r '.handler' <<< "$entry")" == chrome-preferences || "$(jq -r '.handler' <<< "$entry")" == upower-threshold || "$(jq -r '.handler' <<< "$entry")" == system-hostname || "$(jq -r '.handler' <<< "$entry")" == ssh-reboot-sudoers || "$(jq -r '.handler' <<< "$entry")" == networkmanager-vpn-profiles || "$(jq -r '.handler' <<< "$entry")" == keyfile-mounts ]]; then
    if jq -e --arg id "$id" '[.steps[] | select(.id == $id and has("selectedValue"))] | length == 1' "$original" >/dev/null; then
      value=$(jq -er --arg id "$id" '[.steps[] | select(.id == $id and has("selectedValue")) | .selectedValue][0]' "$original") ||
        ride_die "run has an invalid selected value for $id"
      value_provided=true
      ride_entry_or_die "$id" "$source" "$value" "$value_provided"
    else
      printf '%s\n' "$entry"
    fi
  else
    printf '%s\n' "$entry"
  fi
}

ride_restore_signature_matches() {
  local id=$1 source=$2 signature=$3 version=$4 entry=$5 original=$6
  [[ "$signature" == - || "$signature" == "$(ride_source_signature "$entry" "$version")" ]] && return 0
  [[ "$id" == package.tmog && "$source" == tmog-publisher-appimage-pinned &&
     "$version" == 2 &&
     "$signature" == 8ca372bf3ad0402e022ade54114679a22ba195c8d8353c571aae73dab93266c3 &&
     "$(jq -r '.handler' <<< "$entry")" == tmog-appimage ]] || return 1
  jq -e --arg signature "$signature" '
    [.steps[] | select(.id == "package.tmog" and
      .sourceId == "tmog-publisher-appimage-pinned" and
      .sourceSignature == $signature and .sourceSignatureVersion == 2 and
      .deploymentId == "user-applications-appimage" and
      .observedBefore == "absent" and .observedAfter == "installed" and
      .result == "changed")] | length == 1
  ' "$original" >/dev/null
}

ride_restore() {
  local original_id=$1 original id before after result source signature signature_version entry current recovery
  [[ -n "$original_id" ]] || ride_die "restore requires --run-id"
  original=$(ride_journal_by_id "$original_id")
  if ride_journal_has_completed_restore "$original_id"; then
    ride_die "run has already been restored: $original_id"
  fi
  # Refuse a conflicting machine state before restoring any step.
  while IFS=$'\t' read -r id before after result source signature signature_version; do
    [[ "$source" != - ]] || source=
    entry=$(ride_restore_entry "$id" "$source" "$original")
    [[ "$result" == changed || ( "$result" == pending &&
       "$(jq -r '.handler' <<< "$entry")" == firefox-extensions ) ]] || continue
    ride_require_target "$entry"
    if [[ "$RIDE_DRY_RUN" == 1 ]]; then
      ride_require_preview_identity "$entry"
    fi
    ride_restore_signature_matches "$id" "$source" "$signature" "$signature_version" "$entry" "$original" ||
      ride_die "source definition changed since run for $id; exact recovery is unavailable"
    recovery=$(jq -r '.recovery' <<< "$entry")
    if [[ "$recovery" == none || ( "$recovery" == remove-new-install && ( "$before" != absent || "$after" != installed ) ) ]]; then
      ride_die "exact recovery is unavailable for $id ($before -> $after)"
    fi
    if [[ "$id" == setting.ibus-emoji-hotkey || "$(jq -r '.handler' <<< "$entry")" == gsettings-string || "$(jq -r '.handler' <<< "$entry")" == gnome-lock-timing || "$(jq -r '.handler' <<< "$entry")" == upower-threshold || "$(jq -r '.handler' <<< "$entry")" == dnf5-fast-tuning || "$(jq -r '.handler' <<< "$entry")" == system-hostname ]]; then
      if [[ "$(jq -r '.handler' <<< "$entry")" == gnome-lock-timing ]]; then
        [[ "$before" == absent ]] || ride_gnome_lock_timing_snapshot_valid "$before" ||
          ride_die "invalid saved GNOME lock timing state"
      elif [[ "$(jq -r '.handler' <<< "$entry")" == upower-threshold ]]; then
        ride_upower_valid_snapshot "$before" || ride_die "invalid saved UPower setting state"
      elif [[ "$(jq -r '.handler' <<< "$entry")" == dnf5-fast-tuning ]]; then
        [[ "$before" == absent || "$before" == configured ]] || ride_die "invalid saved DNF5 tuning state"
      elif [[ "$(jq -r '.handler' <<< "$entry")" == system-hostname ]]; then
        ride_system_hostname_snapshot_valid "$before" || ride_die "invalid saved static hostname state"
      else
        ride_gsettings_valid_snapshot "$before" || ride_die "invalid saved user setting state"
      fi
      if [[ "$RIDE_DRY_RUN" != 1 ]]; then
        ride_require_target "$entry"
        ride_require_accepted "$entry"
        ride_require_privilege "$entry"
      fi
    elif [[ "$RIDE_DRY_RUN" != 1 ]]; then
      ride_preflight_change "$entry" "$before"
    fi
    current=$(ride_observe "$entry")
    [[ "$current" == "$after" || "$current" == "$before" ||
       ( "$(jq -r '.handler' <<< "$entry")" == firefox-extensions &&
         "$before" == absent && "$after" == configured &&
         "$current" == removal-pending ) ]] ||
      ride_die "restore conflict for $id: expected $after, observed $current"
  done < <(ride_restore_steps "$original")
  if [[ "$RIDE_DRY_RUN" == 1 ]]; then
    {
      while IFS=$'\t' read -r id before after result source signature signature_version; do
        [[ "$source" != - ]] || source=
        entry=$(ride_restore_entry "$id" "$source" "$original")
        [[ "$result" == changed || ( "$result" == pending &&
           "$(jq -r '.handler' <<< "$entry")" == firefox-extensions ) ]] || continue
        if [[ "$id" == setting.ibus-emoji-hotkey || "$(jq -r '.handler' <<< "$entry")" == gsettings-string || "$(jq -r '.handler' <<< "$entry")" == gnome-lock-timing || "$(jq -r '.handler' <<< "$entry")" == gnome-custom-shortcuts || "$(jq -r '.handler' <<< "$entry")" == bash-aliases || "$(jq -r '.handler' <<< "$entry")" == chrome-preferences || "$(jq -r '.handler' <<< "$entry")" == upower-threshold || "$(jq -r '.handler' <<< "$entry")" == system-hostname ]]; then
          printf '%s\t-\t%s\t%s\t%s\t-\t-\t%s\n' \
            "$id" "$(ride_observe "$entry")" "$before" "$(jq -r '.status' <<< "$entry")" "$(jq -r '.scope' <<< "$entry")"
        else
          ride_plan_entry "$id" "$before" "$source"
        fi
      done < <(ride_restore_steps "$original")
    } | ride_table $'ID\tSOURCE\tCURRENT\tDESIRED\tSTATUS\tDISTRIBUTION\tDEPLOYMENT\tSCOPE'
    return
  fi
  ride_journal_create "restore:$original_id"
  RIDE_RUN_PENDING=0
  while IFS=$'\t' read -r id before after result source signature signature_version; do
    [[ "$source" != - ]] || source=
    entry=$(ride_restore_entry "$id" "$source" "$original")
    [[ "$result" == changed || ( "$result" == pending &&
       "$(jq -r '.handler' <<< "$entry")" == firefox-extensions ) ]] || continue
    ride_apply_one "$entry" "$before" || return 1
  done < <(ride_restore_steps "$original")
  if [[ "${RIDE_RUN_PENDING:-0}" == 1 ]]; then ride_journal_finish pending; else ride_journal_finish complete; fi
}

ride_remove_profile() {
  local profile=$1 id source value entry removable_count=0
  ride_validate_profile "$profile"
  if [[ "$RIDE_DRY_RUN" == 1 ]]; then
    {
      while IFS=$'\t' read -r id source value; do
        [[ "$source" != - ]] || source=
        [[ "$value" != '~' ]] || value=
        entry=$(ride_entry_or_die "$id" "$source" "$value")
        if jq -e '.kind == "package" and .recovery == "remove-new-install" and (.states | index("absent") != null)' <<< "$entry" >/dev/null; then
          ride_plan_entry "$id" absent "$source" "$value"
        fi
      done < <(jq -r '.operations | reverse[] | [.id, (.source // "-"), (.value // "~")] | @tsv' "$profile")
    } | ride_table $'ID\tSOURCE\tCURRENT\tDESIRED\tSTATUS\tDISTRIBUTION\tDEPLOYMENT\tSCOPE'
    while IFS= read -r id; do
      [[ -n "$id" ]] || continue
      entry=$(ride_entry_or_die "$id")
      if ! jq -e '.kind == "package" and .recovery == "remove-new-install" and (.states | index("absent") != null)' <<< "$entry" >/dev/null; then
        if [[ "$(jq -r '.kind' <<< "$entry")" == package ]]; then
          printf 'kept one-way prerequisite %s\n' "$id" >&2
        else
          printf 'kept non-package profile operation %s\n' "$id" >&2
        fi
      fi
    done < <(jq -r '.operations | reverse[] | .id' "$profile")
    return
  fi
  while IFS=$'\t' read -r id source value; do
    [[ -z "$id" ]] && continue
    [[ "$source" != - ]] || source=
    [[ "$value" != '~' ]] || value=
    entry=$(ride_entry_or_die "$id" "$source" "$value")
    jq -e '.kind == "package" and .recovery == "remove-new-install" and (.states | index("absent") != null)' <<< "$entry" >/dev/null || continue
    ride_preflight_change "$entry" absent
    removable_count=$((removable_count + 1))
  done < <(jq -r '.operations | reverse[] | [.id, (.source // "-"), (.value // "~")] | @tsv' "$profile")
  if (( removable_count == 0 )); then
    while IFS= read -r id; do
      entry=$(ride_entry_or_die "$id")
      if [[ "$(jq -r '.kind' <<< "$entry")" == package ]]; then
        printf 'kept one-way prerequisite %s\n' "$id"
      else
        printf 'kept non-package profile operation %s\n' "$id"
      fi
    done < <(jq -r '.operations[].id' "$profile")
    return
  fi
  ride_journal_create remove-profile
  RIDE_RUN_PENDING=0
  while IFS=$'\t' read -r id source value; do
    [[ -z "$id" ]] && continue
    [[ "$source" != - ]] || source=
    [[ "$value" != '~' ]] || value=
    entry=$(ride_entry_or_die "$id" "$source" "$value")
    if ! jq -e '.kind == "package" and .recovery == "remove-new-install" and (.states | index("absent") != null)' <<< "$entry" >/dev/null; then
      if [[ "$(jq -r '.kind' <<< "$entry")" == package ]]; then
        printf 'kept one-way prerequisite %s\n' "$id"
      else
        printf 'kept non-package profile operation %s\n' "$id"
      fi
      continue
    fi
    ride_apply_one "$entry" absent || return 1
  done < <(jq -r '.operations | reverse[] | [.id, (.source // "-"), (.value // "~")] | @tsv' "$profile")
  if [[ "${RIDE_RUN_PENDING:-0}" == 1 ]]; then ride_journal_finish pending; else ride_journal_finish complete; fi
}

ride_status_view_matches() {
  local entry=$1 view=${2,,}
  jq -e --arg view "$view" '
    (.kind // "" | ascii_downcase) as $kind |
    if $view == "all" then true
    elif $view == "packages" then $kind == "package"
    elif $view == "artifacts" then $kind == "artifact"
    elif $view == "settings" then $kind == "setting"
    elif $view == "systems" then $kind == "system"
    elif $view == "groups" then ((.group // "") | length > 0)
    else ((.group // "") | ascii_downcase) == $view
    end' <<< "$entry" >/dev/null
}

ride_status_view_validate() {
  local view=${1,,}
  case "$view" in
    all|packages|artifacts|settings|systems|groups) return 0 ;;
    *) jq -e --arg view "$view" \
         'any(.operations[]; ((.group // "") | ascii_downcase) == $view)' \
         "$RIDE_CATALOG" >/dev/null || ride_die "unknown status view: $1" ;;
  esac
}

ride_status() {
  local id=${1:-} source=${2:-} value=${3:-} view=${4:-all} entry current conflict
  ride_status_view_validate "$view"
  {
    printf 'ID\tSOURCE\tOBSERVED\tSTATUS\tDISTRIBUTION\tDEPLOYMENT\tSCOPE\n'
    if [[ -n "$id" ]]; then
      entry=$(ride_entry_or_die "$id" "$source" "$value")
      ride_require_target "$entry"
      current=$(ride_observe "$entry")
      conflict=$(ride_provider_conflict "$entry")
      [[ -z "$conflict" ]] || current="conflict:$conflict"
      printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$id" \
        "$(jq -r '.sourceId // "-"' <<< "$entry")" "$current" "$(jq -r '.status' <<< "$entry")" \
        "$(jq -r '.distribution // "-"' <<< "$entry")" \
        "$(jq -r '.deploymentId // "-"' <<< "$entry")" "$(jq -r '.scope' <<< "$entry")"
    else
      while IFS= read -r id; do
        entry=$(ride_entry_or_die "$id")
        ride_status_view_matches "$entry" "$view" || continue
        if ride_target_matches "$entry"; then
          current=$(ride_observe "$entry")
          conflict=$(ride_provider_conflict "$entry")
          [[ -z "$conflict" ]] || current="conflict:$conflict"
        else
          current=unsupported
        fi
        printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$id" \
          "$(jq -r '.sourceId // "-"' <<< "$entry")" "$current" "$(jq -r '.status' <<< "$entry")" \
          "$(jq -r '.distribution // "-"' <<< "$entry")" \
          "$(jq -r '.deploymentId // "-"' <<< "$entry")" "$(jq -r '.scope' <<< "$entry")"
      done < <(jq -r '.operations[].id' "$RIDE_CATALOG")
    fi
  } | ride_table
}

ride_main() {
  local command=${1:-list} argument='' profile=default profile_set=0 desired='' value='' run_id='' destination='' source='' source_set=0 stdin_set=0 status_id='' status_view=all status_id_set=0 status_view_set=0
  local state_set=0 value_set=0 run_id_set=0 destination_set=0 allow_candidate_set=0 dry_run_set=0
  if [[ $# -gt 0 ]]; then shift; fi
  case "$command" in
    -h|--help|help) ride_help; return ;;
    -v|--version|version) printf 'RIDE Linux %s\n' "$RIDE_VERSION"; return ;;
  esac
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --profile) [[ $# -ge 2 ]] || ride_die "--profile needs a value"; profile=$2; profile_set=1; shift 2 ;;
      --state) [[ $# -ge 2 ]] || ride_die "--state needs a value"; desired=$2; state_set=1; shift 2 ;;
      --value) [[ $# -ge 2 ]] || ride_die "--value needs a value"; value=$2; value_set=1; shift 2 ;;
      --run-id) [[ $# -ge 2 ]] || ride_die "--run-id needs a value"; run_id=$2; run_id_set=1; shift 2 ;;
      --destination) [[ $# -ge 2 ]] || ride_die "--destination needs a value"; destination=$2; destination_set=1; shift 2 ;;
      --source) [[ $# -ge 2 ]] || ride_die "--source needs a value"; source=$2; source_set=1; shift 2 ;;
      --id) [[ $# -ge 2 ]] || ride_die "--id needs an operation ID"; status_id=$2; status_id_set=1; shift 2 ;;
      --view) [[ $# -ge 2 ]] || ride_die "--view needs a view name"; status_view=$2; status_view_set=1; shift 2 ;;
      --stdin) stdin_set=1; shift ;;
      --allow-candidate) RIDE_ALLOW_CANDIDATE=1; allow_candidate_set=1; shift ;;
      --dry-run) RIDE_DRY_RUN=1; dry_run_set=1; shift ;;
      --*) ride_die "unknown option: $1" ;;
      *) [[ -z "$argument" ]] || ride_die "unexpected argument: $1"; argument=$1; shift ;;
    esac
  done
  case "$command" in
    list|search)
      [[ "$profile_set$state_set$value_set$run_id_set$destination_set$source_set$allow_candidate_set$dry_run_set" == 00000000 ]] || ride_die "$command does not accept options" ;;
    show)
      [[ "$profile_set$state_set$value_set$run_id_set$destination_set$allow_candidate_set$dry_run_set" == 0000000 ]] || ride_die "show accepts only an ID or --stdin, plus optional --source"
      if [[ "$stdin_set" == 1 ]]; then
        [[ -z "$argument" ]] || ride_die "show --stdin cannot be combined with a positional ID"
      else
        [[ -n "$argument" ]] || ride_die "show requires an ID or --stdin"
      fi ;;
    plan)
      [[ "$state_set$value_set$run_id_set$destination_set$source_set$dry_run_set" == 000000 && -z "$argument" ]] || ride_die "plan accepts only --profile and --allow-candidate" ;;
    apply)
      [[ "$state_set$value_set$run_id_set$destination_set$source_set" == 00000 && -z "$argument" ]] || ride_die "apply accepts only --profile, --allow-candidate, and --dry-run" ;;
    download)
      [[ "$profile_set$state_set$value_set$run_id_set$allow_candidate_set" == 00000 && -n "$argument" ]] || ride_die "download requires an ID and accepts only --source, --destination, and --dry-run" ;;
    install)
      [[ "$profile_set$state_set$value_set$run_id_set$destination_set" == 00000 && -n "$argument" ]] || ride_die "install requires an ID and accepts only --source, --allow-candidate, and --dry-run" ;;
    set)
      [[ "$profile_set$run_id_set$destination_set$source_set" == 0000 && -n "$argument" && "$state_set" == 1 && -n "$desired" ]] || ride_die "set requires an ID and --state; it accepts --value, --allow-candidate, and --dry-run" ;;
    deploy)
      [[ "$profile_set$value_set$run_id_set$destination_set$source_set" == 00000 && -n "$argument" && "$state_set" == 1 && -n "$desired" ]] || ride_die "deploy requires an ID and --state; it accepts --allow-candidate and --dry-run" ;;
    update)
      [[ "$profile_set$state_set$value_set$run_id_set$destination_set$source_set" == 000000 && -n "$argument" ]] || ride_die "update requires an ID and accepts --allow-candidate and --dry-run" ;;
    unset)
      [[ "$profile_set$state_set$value_set$run_id_set$destination_set$source_set" == 000000 && -n "$argument" ]] || ride_die "unset requires an ID and accepts --allow-candidate and --dry-run" ;;
    status)
      [[ "$state_set$run_id_set$destination_set$allow_candidate_set$dry_run_set" == 00000 ]] || ride_die "status does not accept those options" ;
      [[ "$status_id_set" == 0 || -z "$argument" ]] || ride_die "status accepts either a positional ID or --id, not both" ;
      [[ "$status_id_set$status_view_set" != 11 ]] || ride_die "status accepts either --id or --view, not both" ;
      [[ "$status_view_set" == 0 || ( -z "$argument" && "$source_set$value_set" == 00 ) ]] || ride_die "status --view cannot be combined with an ID, --source, or --value" ;
      [[ "$profile_set" == 0 || ( -z "$argument" && "$source_set$value_set" == 00 ) ]] || ride_die "status --profile cannot be combined with a positional ID, --source, or --value" ;;
    restore)
      [[ "$profile_set$state_set$value_set$destination_set$source_set" == 00000 && -z "$argument" && "$run_id_set" == 1 && -n "$run_id" ]] || ride_die "restore requires --run-id and accepts --allow-candidate and --dry-run" ;;
    remove)
      [[ "$state_set$value_set$run_id_set$destination_set" == 0000 ]] || ride_die "remove does not accept those options" ;
      if [[ "$profile_set" == 1 ]]; then
        [[ -z "$argument" && "$source_set" == 0 ]] || ride_die "remove --profile cannot be combined with an ID or --source"
      else
        [[ -n "$argument" ]] || ride_die "remove requires a package ID or an explicit --profile"
      fi ;;
    completion)
      [[ "$profile_set$state_set$value_set$run_id_set$destination_set$source_set$allow_candidate_set$dry_run_set" == 00000000 && "$argument" == bash ]] || ride_die "completion requires bash and accepts no options" ;;
    *) ride_die "unknown command: $command" ;;
  esac
  [[ "$status_id_set$status_view_set" == 00 || "$command" == status ]] || ride_die "--id and --view are only valid with status"
  [[ "$stdin_set" == 0 || "$command" == show ]] || ride_die "--stdin is only valid with show"
  ride_require_command jq
  ride_platform
  ride_validate_catalog
  if [[ "$source_set" == 1 ]]; then
    case "$command" in
      show|download|install|remove) [[ -n "$argument" || ( "$command" == show && "$stdin_set" == 1 ) ]] || ride_die "--source needs a package ID or show --stdin" ;;
      status) [[ -n "$argument$status_id" && "$status_view_set" == 0 ]] || ride_die "--source needs a status operation ID" ;;
      *) ride_die "--source is only valid with a direct package command" ;;
    esac
  fi
  [[ "$value_set" == 0 || "$command" == set || ( "$command" == status && "$profile_set" == 0 ) ]] ||
    ride_die "--value is only valid with set or direct status"
  [[ "$value_set" == 0 || "$command" != status || -n "$argument$status_id" ]] ||
    ride_die "status --value requires an ID"
  case "$command" in
    list) ride_list "${argument:-all}" ;;
    search) ride_search "$argument" ;;
    show) ride_show "$argument" "$source" "$stdin_set" ;;
    plan) [[ -z "$argument" ]] || ride_die "plan takes --profile, not a positional argument"; ride_plan_profile "$(ride_profile_path "$profile")" ;;
    apply) [[ -z "$argument" ]] || ride_die "apply takes --profile, not a positional argument"; ride_apply_profile "$(ride_profile_path "$profile")" ;;
    download)
      [[ -n "$argument" ]] || ride_die "download requires a package ID"
      local entry
      entry=$(ride_entry_or_die "$argument" "$source")
      ride_require_target "$entry"
      [[ "$(jq -r '.kind' <<< "$entry")" == package || "$(jq -r '.kind' <<< "$entry")" == artifact ]] ||
        ride_die "download requires a package or artifact operation"
      case "$(jq -r '.handler' <<< "$entry")" in
        dnf-package|github-asset) ;;
        *) ride_die "download unsupported for this handler" ;;
      esac
      [[ "$RIDE_DRY_RUN" == 0 ]] || { printf 'would download %s\n' "$argument"; return; }
      case "$(jq -r '.handler' <<< "$entry")" in
        dnf-package) ride_download_package "$entry" "${destination:-$(ride_cache_dir)/artifacts/$argument}" ;;
        github-asset) ride_github_download_asset "$entry" "${destination:-$(ride_cache_dir)/artifacts/$argument}" ;;
        *) ride_die "download unsupported for this handler" ;;
      esac
      ;;
    install)
      [[ "$(jq -r '.kind' <<< "$(ride_entry_or_die "$argument" "$source")")" == package ]] || ride_die "install requires a package ID"
      ride_apply_single "$argument" installed "$source"
      ;;
    set)
      local selected_value_provided=false
      [[ "$(jq -r '.kind' <<< "$(ride_entry_or_die "$argument")")" == setting ]] || ride_die "set requires a setting ID"
      [[ -n "$desired" ]] || ride_die "set requires --state"
      [[ "$value_set" == 0 ]] || selected_value_provided=true
      ride_apply_single "$argument" "$desired" "" "$value" "$selected_value_provided"
      ;;
    deploy)
      local deploy_entry
      deploy_entry=$(ride_entry_or_die "$argument")
      [[ "$(jq -r '.handler' <<< "$deploy_entry")" == docker-engine &&
         "$(jq -r '.kind' <<< "$deploy_entry")" == system ]] ||
        ride_die "deploy requires a managed Docker Engine system operation ID"
      [[ -n "$desired" && -z "$value" ]] || ride_die "deploy requires --state and does not accept --value"
      if [[ "$RIDE_DRY_RUN" == 1 ]]; then
        ride_plan_entry "$argument" "$desired" | ride_table $'ID\tSOURCE\tCURRENT\tDESIRED\tSTATUS\tDISTRIBUTION\tDEPLOYMENT\tSCOPE'
      else
        ride_apply_single "$argument" "$desired"
      fi
      ;;
    update)
      local update_entry
      update_entry=$(ride_entry_or_die "$argument")
      [[ "$(jq -r '.kind' <<< "$update_entry")" == system &&
         "$(jq -r '.handler' <<< "$update_entry")" == dnf5-system-update ]] ||
        ride_die "update requires a whole-system update operation ID"
      [[ -z "$desired" && -z "$value" ]] || ride_die "update does not accept --state or --value"
      if [[ "$RIDE_DRY_RUN" == 1 ]]; then
        ride_plan_entry "$argument" current | ride_table $'ID\tSOURCE\tCURRENT\tDESIRED\tSTATUS\tDISTRIBUTION\tDEPLOYMENT\tSCOPE'
      else
        ride_apply_single "$argument" current
      fi
      ;;
    unset)
      local unset_entry unset_state
      unset_entry=$(ride_entry_or_die "$argument")
      [[ "$(jq -r '.kind' <<< "$unset_entry")" == setting ]] || ride_die "unset requires a setting ID"
      unset_state=$(jq -r '.unsetState // empty' <<< "$unset_entry")
      [[ -n "$unset_state" ]] || ride_die "operation has no declared unset state: $argument"
      ride_apply_single "$argument" "$unset_state"
      ;;
    status)
      if [[ "$profile_set" == 1 ]]; then
        local status_profile
        status_profile=$(ride_profile_path "$profile")
        if [[ "$status_id_set" == 1 ]]; then
          ride_plan_profile "$status_profile" all "$status_id"
        elif [[ "$status_view_set" == 1 ]]; then
          ride_plan_profile "$status_profile" "$status_view"
        else
          ride_plan_profile "$status_profile"
        fi
      else
        if [[ "$status_view_set" == 1 ]]; then
          ride_status "" "" "" "$status_view"
        elif [[ "$status_id_set" == 1 ]]; then
          ride_status "$status_id" "$source" "$value"
        else
          ride_status "$argument" "$source" "$value"
        fi
      fi
      ;;
    restore) ride_restore "$run_id" ;;
    remove)
      if [[ -n "$argument" ]]; then
        [[ "$(jq -r '.kind' <<< "$(ride_entry_or_die "$argument" "$source")")" == package ]] || ride_die "remove requires a package ID"
        jq -e '.states | index("absent") != null' <<< "$(ride_entry_or_die "$argument" "$source")" >/dev/null || ride_die "invalid state absent for $argument"
        [[ "$(jq -r '.recovery' <<< "$(ride_entry_or_die "$argument" "$source")")" == remove-new-install ]] || ride_die "package removal is not supported by its recovery contract: $argument"
        ride_apply_single "$argument" absent "$source"
      elif [[ "$profile_set" == 1 ]]; then
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

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  ride_main "$@"
fi
