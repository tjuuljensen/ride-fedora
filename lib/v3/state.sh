#!/usr/bin/env bash

ride_journal_write() {
  local file=$1 jq_filter=$2 temp
  shift 2
  temp=$(mktemp "${file}.tmp.XXXXXXXX") || ride_die "cannot create journal temporary file"
  if ! jq "$@" "$jq_filter" "$file" > "$temp"; then
    rm -f "$temp"
    ride_die "cannot update run journal"
  fi
  chmod 600 "$temp"
  mv -f "$temp" "$file"
}

ride_journal_create() {
  local action=$1 directory id file
  directory=$(ride_state_dir)
  umask 077
  mkdir -p "$directory" || ride_die "cannot create run-state directory: $directory"
  chmod 700 "$directory"
  id="$(date -u +%Y%m%dT%H%M%SZ)-$$-$RANDOM"
  file="$directory/$id.json"
  jq -n --arg id "$id" --arg action "$action" --arg started "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    '{schemaVersion:1, runId:$id, action:$action, startedAt:$started, status:"running", steps:[]}' > "$file" ||
    ride_die "cannot create run journal"
  chmod 600 "$file"
  RIDE_RUN_ID=$id
  RIDE_RUN_FILE=$file
  printf 'Run ID: %s\n' "$id"
}

ride_journal_finalize_on_exit() {
  local exit_code=$1
  [[ -n "${RIDE_RUN_FILE:-}" && -f "$RIDE_RUN_FILE" ]] || return 0
  if jq -e '.status == "running"' "$RIDE_RUN_FILE" >/dev/null 2>&1; then
    ride_journal_finish failed || true
    ride_error "run stopped before completion; inspect $RIDE_RUN_FILE (exit $exit_code)"
  fi
}

ride_journal_append() {
  local step=$1
  ride_journal_write "$RIDE_RUN_FILE" '.steps += [$step]' --argjson step "$step"
}

ride_journal_update_last() {
  local result=$1 observed=$2
  ride_journal_write "$RIDE_RUN_FILE" '.steps[-1].result = $result | .steps[-1].observedAfter = $observed' \
    --arg result "$result" --arg observed "$observed"
}

ride_journal_finish() {
  local status=$1
  ride_journal_write "$RIDE_RUN_FILE" '.status = $status | .finishedAt = $finished' \
    --arg status "$status" --arg finished "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

ride_journal_by_id() {
  local id=$1 directory file
  [[ "$id" =~ ^[0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+$ ]] || ride_die "invalid run ID"
  directory=$(ride_state_dir)
  file="$directory/$id.json"
  [[ -f "$file" && ! -L "$file" ]] || ride_die "run not found: $id"
  jq -e '.schemaVersion == 1 and (.steps | type == "array")' "$file" >/dev/null || ride_die "invalid run journal"
  printf '%s\n' "$file"
}

ride_journal_has_completed_restore() {
  local original_id=$1 file directory
  directory=$(ride_state_dir)
  for file in "$directory"/*.json; do
    [[ -f "$file" && ! -L "$file" ]] || continue
    if jq -e --arg action "restore:$original_id" '.action == $action and .status == "complete"' "$file" >/dev/null 2>&1; then
      return 0
    fi
  done
  return 1
}
