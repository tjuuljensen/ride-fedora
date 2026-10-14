#!/usr/bin/env bash

ride_validate_catalog() {
  [[ -r "$RIDE_CATALOG" ]] || ride_die "catalog not readable: $RIDE_CATALOG"
  jq -e '
    .schemaVersion == 1 and (.operations | type == "array" and length > 0) and
    ([.operations[].id] | length == (unique | length)) and
    all(.operations[];
      (.id | type == "string" and test("^(package|setting|artifact|system)\\.[a-z0-9.-]+$")) and
      (.kind | IN("package", "setting", "artifact", "system")) and
      (.name | type == "string" and length > 0) and
      (.handler | IN("dnf-package", "systemd-service", "github-asset", "python-venv")) and
      (.scope | IN("system", "user")) and
      (.status | IN("candidate", "supported")) and
      (.recovery | IN("remove-new-install", "exact-state", "none")) and
      (if .kind == "package" then .recovery == "remove-new-install"
       elif .kind == "setting" then .recovery == "exact-state"
       elif .kind == "artifact" then .recovery == "none"
       else true end) and
      (.states | type == "array" and length > 0 and all(.[]; type == "string")) and
      (.targets | type == "object" and length > 0) and
      (.productUri | type == "string" and startswith("https://")) and
      (.sourceUri | type == "string" and startswith("https://")) and
      (.licenseUri | type == "string" and startswith("https://")) and
      (if .handler == "dnf-package" then (.kind == "package" and (.packageName | type == "string" and test("^[A-Za-z0-9+_.-]+$")))
       elif .handler == "systemd-service" then (.kind == "setting" and (.serviceName | type == "string" and test("^[A-Za-z0-9_.@-]+\\.service$")))
       elif .handler == "python-venv" then (.kind == "package" and .id == "package.volatility3")
       else (.kind == "artifact" and (.githubRepository | type == "string" and test("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")) and
             (.assetSuffix | type == "string" and test("^-[A-Za-z0-9_.-]+$")) and
             (.maxBytes | type == "number" and . > 0 and . <= 104857600)) end)
    )
  ' "$RIDE_CATALOG" >/dev/null || ride_die "invalid v3 operation catalog"
  local dependency
  while IFS= read -r dependency; do
    [[ -z "$dependency" ]] && continue
    ride_entry "$dependency" >/dev/null || ride_die "catalog has unknown dependency: $dependency"
  done < <(jq -r '.operations[] | .dependencies[]?' "$RIDE_CATALOG")
  local evidence supported_id
  while IFS=$'\t' read -r supported_id evidence; do
    [[ "$evidence" == "docs/acceptance/$supported_id.md" && -f "$RIDE_ROOT/$evidence" ]] ||
      ride_die "supported catalog entry lacks acceptance evidence: $supported_id"
  done < <(jq -r '.operations[] | select(.status == "supported") | [.id, (.acceptanceEvidence // "MISSING")] | @tsv' "$RIDE_CATALOG")
}

ride_entry() {
  local id=$1
  jq -ce --arg id "$id" '.operations[] | select(.id == $id)' "$RIDE_CATALOG"
}

ride_entry_or_die() {
  ride_entry "$1" || ride_die "unknown catalog ID: $1"
}

ride_profile_path() {
  local profile=${1:-default}
  if [[ "$profile" == */* || "$profile" == *.json ]]; then
    printf '%s\n' "$profile"
  else
    printf '%s/profiles/%s.json\n' "$RIDE_ROOT" "$profile"
  fi
}

ride_validate_profile() {
  local profile=$1 row id state entry
  [[ -r "$profile" ]] || ride_die "profile not readable: $profile"
  jq -e '
    .schemaVersion == 1 and (.id | type == "string" and test("^[a-z0-9-]+$")) and
    (.operations | type == "array") and
    ([.operations[].id] | length == (unique | length)) and
    all(.operations[]; (.id | type == "string") and (.state | type == "string"))
  ' "$profile" >/dev/null || ride_die "invalid v3 profile: $profile"
  while IFS=$'\t' read -r id state; do
    [[ -z "$id" ]] && continue
    entry=$(ride_entry_or_die "$id")
    [[ "$(jq -r '.kind' <<< "$entry")" != artifact ]] || ride_die "download-only artifact cannot appear in a profile: $id"
    jq -e --arg state "$state" '.states | index($state) != null' <<< "$entry" >/dev/null ||
      ride_die "invalid state $state for $id"
  done < <(jq -r '.operations[] | [.id, .state] | @tsv' "$profile")
}

ride_dependencies_ready() {
  local entry=$1 dependency dependency_entry current
  while IFS= read -r dependency; do
    [[ -z "$dependency" ]] && continue
    dependency_entry=$(ride_entry_or_die "$dependency")
    current=$(ride_observe "$dependency_entry")
    if [[ "$current" != installed ]]; then
      ride_error "dependency is not installed: $dependency"
      return 1
    fi
  done < <(jq -r '.dependencies[]?' <<< "$entry")
}
