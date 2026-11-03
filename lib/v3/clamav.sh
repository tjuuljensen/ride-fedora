#!/usr/bin/env bash
# RIDE v3 Fedora ClamAV package and initial signature lifecycle.

RIDE_CLAMAV_DATA_DIR=/var/lib/clamav
RIDE_CLAMAV_OWNER_DIR=/var/lib/ride-fedora/owned-tools/package.clamav

ride_clamav_manifest() {
  printf '%s/state.json\n' "$RIDE_CLAMAV_OWNER_DIR"
}

ride_clamav_snapshot_dir() {
  printf '%s/snapshots\n' "$RIDE_CLAMAV_OWNER_DIR"
}

ride_clamav_tree_hash() {
  python3 "$RIDE_ROOT/tools/clamav-state.py" hash "$1"
}

ride_clamav_units_snapshot() {
  local unit load enabled active result='{}'
  for unit in clamav-freshclam.service clamav-freshclam-once.service clamav-freshclam-once.timer; do
    load=$(systemctl show --property=LoadState --value "$unit" 2>/dev/null) ||
      ride_die "cannot inspect $unit load state"
    enabled=$(systemctl is-enabled "$unit" 2>/dev/null || true)
    active=$(systemctl is-active "$unit" 2>/dev/null || true)
    [[ -n "$enabled" ]] || enabled=unknown
    [[ -n "$active" ]] || active=unknown
    result=$(jq -cn --argjson current "$result" --arg unit "$unit" \
      --arg load "$load" --arg enabled "$enabled" --arg active "$active" \
      '$current + {($unit):{load:$load,enabled:$enabled,active:$active}}') ||
      ride_die "cannot record $unit state"
  done
  printf '%s\n' "$result"
}

ride_clamav_packages_snapshot() {
  local package result='{}' installed
  for package in clamav clamav-freshclam; do
    if rpm -q --quiet "$package"; then installed=true; else installed=false; fi
    result=$(jq -cn --argjson current "$result" --arg package "$package" \
      --argjson installed "$installed" '$current + {($package):$installed}') ||
      ride_die "cannot record $package package state"
  done
  printf '%s\n' "$result"
}

ride_clamav_related_packages_snapshot() {
  local names
  names=$(rpm -qa --qf '%{NAME}\n') || ride_die "cannot inspect installed ClamAV RPMs"
  awk '/^clamav($|-)/ {print}' <<< "$names" | sort -u | jq -Rsc 'split("\n") | map(select(length > 0))'
}

ride_clamav_manifest_valid() {
  local file
  file=$(ride_clamav_manifest)
  [[ -f "$file" && ! -L "$file" &&
     "$(stat -c '%u:%g:%a:%h' -- "$file")" == "$(id -u):$(id -g):600:1" ]] || return 1
  jq -e '
    .schemaVersion == 1 and .id == "package.clamav" and
    (.status == "applying" or .status == "installed") and
    (.dataExisted | type == "boolean") and
    (.dataBeforeHash | type == "string" and (test("^[0-9a-f]{64}$") or . == "absent")) and
    (.packagesBefore | type == "object") and
    (.packagesBefore.clamav | type == "boolean") and
    (.packagesBefore["clamav-freshclam"] | type == "boolean") and
    (.relatedPackagesBefore | type == "array" and all(.[]; type == "string" and test("^clamav($|-)"))) and
    (.unitsBefore | type == "object") and
    (.introducedPackages | type == "array" and all(.[]; IN("clamav", "clamav-freshclam"))) and
    ((.status == "applying") or
      (.dataAfterHash | type == "string" and test("^[0-9a-f]{64}$"))) and
    ((.status == "applying") or
      (.relatedPackagesAfter | type == "array" and all(.[]; type == "string" and test("^clamav($|-)")))) and
    ((.status == "applying") or (.unitsAfter | type == "object"))
  ' "$file" >/dev/null 2>&1
}

ride_clamav_paths_safe() {
  local path
  for path in /var /var/lib /var/lib/ride-fedora /var/lib/ride-fedora/owned-tools \
    "$RIDE_CLAMAV_OWNER_DIR" "$RIDE_CLAMAV_DATA_DIR"; do
    [[ ! -L "$path" ]] || return 1
  done
}

ride_clamav_prepare_owner_dir() {
  local parent
  parent=$(dirname "$RIDE_CLAMAV_OWNER_DIR")
  ride_clamav_paths_safe || ride_die "ClamAV state path contains a symbolic link"
  [[ ! -e "$parent" || -d "$parent" ]] || ride_die "ClamAV state parent is not a directory"
  if [[ ! -e "$RIDE_CLAMAV_OWNER_DIR" ]]; then
    if ! mkdir -p -- "$RIDE_CLAMAV_OWNER_DIR" || ! chmod 0700 -- "$RIDE_CLAMAV_OWNER_DIR"; then
      ride_die "cannot create private ClamAV state directory"
    fi
  fi
  [[ -d "$RIDE_CLAMAV_OWNER_DIR" && ! -L "$RIDE_CLAMAV_OWNER_DIR" &&
     "$(stat -c '%u:%a' -- "$RIDE_CLAMAV_OWNER_DIR")" == "$(id -u):700" ]] ||
    ride_die "ClamAV state directory is not private and owned by the current administrator"
}

ride_clamav_write_manifest() {
  local json=$1 file temp
  file=$(ride_clamav_manifest)
  temp=$(mktemp "$RIDE_CLAMAV_OWNER_DIR/.state.XXXXXXXX") || return 1
  if ! jq -e . <<< "$json" > "$temp" || ! chmod 0600 "$temp" || ! mv -T "$temp" "$file"; then
    rm -f -- "$temp"
    return 1
  fi
}

ride_clamav_restore_data() {
  local manifest=$1 snapshot existed expected actual
  snapshot=$(ride_clamav_snapshot_dir)
  existed=$(jq -r '.dataExisted' <<< "$manifest")
  expected=$(jq -r '.dataBeforeHash' <<< "$manifest")
  if [[ "$existed" == true ]]; then
    python3 "$RIDE_ROOT/tools/clamav-state.py" restore "$snapshot/before" \
      "$RIDE_CLAMAV_DATA_DIR" yes || return 1
  else
    python3 "$RIDE_ROOT/tools/clamav-state.py" restore "$snapshot/before" \
      "$RIDE_CLAMAV_DATA_DIR" no || return 1
  fi
  actual=$(ride_clamav_tree_hash "$RIDE_CLAMAV_DATA_DIR") || return 1
  [[ "$actual" == "$expected" ]]
}

ride_clamav_remove_introduced_packages() {
  local manifest=$1 package
  local -a introduced=()
  while IFS= read -r package; do
    [[ -n "$package" ]] && introduced+=("$package")
  done < <(jq -r '.introducedPackages[]' <<< "$manifest")
  ((${#introduced[@]} == 0)) || dnf remove -y "${introduced[@]}"
}

ride_clamav_restore_installed_state() {
  local manifest=$1 snapshot package current expected related units
  local -a reinstall=()
  snapshot=$(ride_clamav_snapshot_dir)
  while IFS= read -r package; do
    [[ -n "$package" ]] || continue
    if ! rpm -q --quiet "$package"; then reinstall+=("$package"); fi
  done < <(jq -r '.relatedPackagesAfter[]' <<< "$manifest")
  ((${#reinstall[@]} == 0)) || dnf --setopt=gpgcheck=1 --setopt=localpkg_gpgcheck=1 \
    install -y "${reinstall[@]}" || return 1
  python3 "$RIDE_ROOT/tools/clamav-state.py" restore "$snapshot/installed" \
    "$RIDE_CLAMAV_DATA_DIR" yes || return 1
  current=$(ride_clamav_tree_hash "$RIDE_CLAMAV_DATA_DIR") || return 1
  expected=$(jq -r '.dataAfterHash' <<< "$manifest") || return 1
  [[ "$current" == "$expected" ]] || return 1
  related=$(ride_clamav_related_packages_snapshot) || return 1
  jq -e --argjson actual "$related" '.relatedPackagesAfter == $actual' \
    <<< "$manifest" >/dev/null || return 1
  units=$(ride_clamav_units_snapshot) || return 1
  jq -e --argjson actual "$units" '.unitsAfter == $actual' <<< "$manifest" >/dev/null
}

ride_clamav_rollback_applying() {
  local manifest=$1 before_units current_units
  ride_clamav_remove_introduced_packages "$manifest" || return 1
  ride_clamav_restore_data "$manifest" || return 1
  before_units=$(jq -c '.unitsBefore' <<< "$manifest") || return 1
  current_units=$(ride_clamav_units_snapshot) || return 1
  # Units newly supplied by packages may disappear on rollback. Every unit
  # already present before the transaction must retain its complete state.
  jq -e --argjson current "$current_units" '
    to_entries | all(.[]; if .value.load == "not-found" then true else
      $current[.key] == .value end)
  ' <<< "$before_units" >/dev/null
}

ride_clamav_observe() {
  local manifest status expected actual packages units related
  ride_clamav_paths_safe || { printf 'unowned\n'; return 0; }
  manifest=$(ride_clamav_manifest)
  [[ -e "$manifest" || -L "$manifest" ]] || { printf 'absent\n'; return 0; }
  ride_clamav_manifest_valid || { printf 'unowned\n'; return 0; }
  status=$(jq -r '.status' "$manifest")
  [[ "$status" == installed ]] || { printf 'pending\n'; return 0; }
  expected=$(jq -r '.dataAfterHash' "$manifest") || return 1
  actual=$(ride_clamav_tree_hash "$RIDE_CLAMAV_DATA_DIR") || ride_die "cannot inspect ClamAV data"
  [[ "$actual" == "$expected" ]] || { printf 'drifted\n'; return 0; }
  packages=$(ride_clamav_packages_snapshot) || return 1
  jq -e --argjson actual "$packages" \
    '$actual.clamav == true and $actual["clamav-freshclam"] == true' \
    <<< '{}' >/dev/null || { printf 'drifted\n'; return 0; }
  related=$(ride_clamav_related_packages_snapshot) || return 1
  jq -e --argjson actual "$related" '.relatedPackagesAfter == $actual' \
    "$manifest" >/dev/null 2>&1 || { printf 'drifted\n'; return 0; }
  units=$(ride_clamav_units_snapshot) || return 1
  jq -e --argjson actual "$units" '.unitsAfter == $actual' "$manifest" >/dev/null 2>&1 || {
    printf 'drifted\n'; return 0;
  }
  printf 'installed\n'
}

ride_clamav_change() {
  local entry=$1 state=$2 id current lock_file lock_fd manifest_json packages_before units_before
  local data_before_hash data_existed snapshot package installed introduced packages_after units_after
  local related_before related_after related_current missing_before
  local -a new_packages=()
  id=$(jq -r '.id' <<< "$entry")
  [[ "$id" == package.clamav && "$(jq -r '.handler' <<< "$entry")" == clamav-initial-signatures ]] ||
    ride_die "unknown ClamAV operation identity"
  [[ "$RIDE_OS_ID" == fedora && "$RIDE_OS_VERSION" == 44 && "$RIDE_ARCH" == x86_64 ]] ||
    ride_die "ClamAV initial-signature operation requires Fedora 44 x86_64"
  ride_require_command dnf
  ride_require_command rpm
  ride_require_command systemctl
  ride_require_command flock
  ride_require_command python3
  ride_require_command jq
  ride_clamav_prepare_owner_dir
  lock_file="$RIDE_CLAMAV_OWNER_DIR/lock"
  exec {lock_fd}>"$lock_file" || ride_die "cannot open ClamAV operation lock"
  flock -n "$lock_fd" || ride_die "another ClamAV package operation is running"
  current=$(ride_clamav_observe) || ride_die "cannot observe ClamAV operation state"
  case "$state" in
    installed)
      [[ "$current" != unowned && "$current" != drifted ]] ||
        ride_die "ClamAV state is modified or outside the recorded RIDE install"
      [[ "$current" != installed ]] || return 0
      [[ "$current" != pending ]] || {
        ride_clamav_manifest_valid || ride_die "invalid pending ClamAV transaction"
        manifest_json=$(cat "$(ride_clamav_manifest)")
        ride_clamav_rollback_applying "$manifest_json" ||
          ride_die "pending ClamAV apply could not be rolled back; preserve its recovery files"
        rm -rf -- "$(ride_clamav_snapshot_dir)"
        rm -f -- "$(ride_clamav_manifest)"
      }
      ride_clamav_paths_safe || ride_die "ClamAV path contains a symbolic link"
      [[ ! -e "$RIDE_CLAMAV_DATA_DIR" || -d "$RIDE_CLAMAV_DATA_DIR" ]] ||
        ride_die "ClamAV data path is not a directory"
      packages_before=$(ride_clamav_packages_snapshot)
      related_before=$(ride_clamav_related_packages_snapshot)
      units_before=$(ride_clamav_units_snapshot)
      jq -e 'all(.[]; .active != "active")' <<< "$units_before" >/dev/null ||
        ride_die "a FreshClam service or timer is active; stop it before the one-shot update"
      if jq -e 'all(.[]; . == false)' <<< "$packages_before" >/dev/null &&
         jq -e 'any(.[]; .load != "not-found")' <<< "$units_before" >/dev/null; then
        ride_die "FreshClam units exist without either owning RPM; refusing package changes"
      fi
      data_before_hash=$(ride_clamav_tree_hash "$RIDE_CLAMAV_DATA_DIR") ||
        ride_die "cannot safely snapshot ClamAV signature data"
      data_existed=true; [[ "$data_before_hash" != absent ]] || data_existed=false
      snapshot=$(ride_clamav_snapshot_dir)
      mkdir -m 0700 -- "$snapshot" || ride_die "cannot create ClamAV recovery snapshot directory"
      if [[ "$data_existed" == true ]]; then
        python3 "$RIDE_ROOT/tools/clamav-state.py" copy "$RIDE_CLAMAV_DATA_DIR" "$snapshot/before" || {
          rm -rf -- "$snapshot"; ride_die "cannot snapshot existing ClamAV data"
        }
      fi
      for package in clamav clamav-freshclam; do
        [[ "$(jq -r --arg p "$package" '.[$p]' <<< "$packages_before")" == true ]] ||
          new_packages+=("$package")
      done
      introduced=$(printf '%s\n' "${new_packages[@]:-}" | jq -Rsc 'split("\n") | map(select(length > 0))')
      manifest_json=$(jq -cn --argjson packages "$packages_before" --argjson units "$units_before" \
        --argjson related "$related_before" \
        --arg data_hash "$data_before_hash" --argjson data_existed "$data_existed" \
        --argjson introduced "$introduced" \
        '{schemaVersion:1,id:"package.clamav",status:"applying",packagesBefore:$packages,
          relatedPackagesBefore:$related,
          unitsBefore:$units,dataExisted:$data_existed,dataBeforeHash:$data_hash,
          introducedPackages:$introduced}') || ride_die "cannot prepare ClamAV recovery record"
      ride_clamav_write_manifest "$manifest_json" || ride_die "cannot persist ClamAV recovery record"
      if ((${#new_packages[@]} > 0)) &&
         ! dnf --setopt=gpgcheck=1 --setopt=localpkg_gpgcheck=1 install -y "${new_packages[@]}"; then
        ride_clamav_rollback_applying "$manifest_json" && {
          rm -rf -- "$snapshot"; rm -f -- "$(ride_clamav_manifest)"
        }
        ride_die "ClamAV RPM installation failed; recovery record retained if rollback was incomplete"
      fi
      units_after=$(ride_clamav_units_snapshot) || ride_die "cannot verify FreshClam unit state"
      # Preserve every pre-existing unit state. Newly installed units must stay
      # stopped and disabled so this remains a one-shot update operation.
      for package in clamav-freshclam.service clamav-freshclam-once.service clamav-freshclam-once.timer; do
        local old_load old_enabled old_active new_load new_enabled new_active
        old_load=$(jq -r --arg u "$package" '.[$u].load' <<< "$units_before")
        old_enabled=$(jq -r --arg u "$package" '.[$u].enabled' <<< "$units_before")
        old_active=$(jq -r --arg u "$package" '.[$u].active' <<< "$units_before")
        new_load=$(jq -r --arg u "$package" '.[$u].load' <<< "$units_after")
        new_enabled=$(jq -r --arg u "$package" '.[$u].enabled' <<< "$units_after")
        new_active=$(jq -r --arg u "$package" '.[$u].active' <<< "$units_after")
        if [[ "$old_load" != not-found ]]; then
          [[ "$new_load:$new_enabled:$new_active" == "$old_load:$old_enabled:$old_active" ]] || {
            ride_clamav_rollback_applying "$manifest_json" ||
              ride_die "FreshClam unit state changed and package rollback failed"
            rm -rf -- "$snapshot"; rm -f -- "$(ride_clamav_manifest)"
            ride_die "install changed a pre-existing FreshClam unit state"
          }
        else
          [[ "$new_active" != active && "$new_enabled" != enabled ]] || {
            systemctl disable --now "$package" >/dev/null 2>&1 || true
            ride_clamav_rollback_applying "$manifest_json" ||
              ride_die "new FreshClam unit state rollback failed"
            rm -rf -- "$snapshot"; rm -f -- "$(ride_clamav_manifest)"
            ride_die "Fedora enabled or started a FreshClam unit during install"
          }
        fi
      done
      if ! command -v freshclam >/dev/null 2>&1; then
        ride_clamav_rollback_applying "$manifest_json" ||
          ride_die "FreshClam command is unavailable after RPM installation and rollback is incomplete"
        rm -rf -- "$snapshot"; rm -f -- "$(ride_clamav_manifest)"
        ride_die "clamav-freshclam did not provide freshclam; prior package and signature state was restored"
      fi
      local freshclam_log="$RIDE_CLAMAV_OWNER_DIR/freshclam.log"
      if ! freshclam --verbose >"$freshclam_log" 2>&1; then
        tail -n 20 "$freshclam_log" >&2 || true
        ride_clamav_rollback_applying "$manifest_json" ||
          ride_die "FreshClam failed and its package/data rollback is incomplete; recovery files retained"
        rm -f -- "$freshclam_log"
        rm -rf -- "$snapshot"; rm -f -- "$(ride_clamav_manifest)"
        ride_die "initial FreshClam update failed; prior package and signature state was restored"
      fi
      if ! grep -Eiq 'Database test passed|database[^[:cntrl:]]*(updated|up-to-date)' "$freshclam_log"; then
        tail -n 20 "$freshclam_log" >&2 || true
        ride_clamav_rollback_applying "$manifest_json" ||
          ride_die "FreshClam did not confirm a tested update and its rollback is incomplete"
        rm -f -- "$freshclam_log"
        rm -rf -- "$snapshot"; rm -f -- "$(ride_clamav_manifest)"
        ride_die "FreshClam returned success without confirming a tested or current signature database"
      fi
      rm -f -- "$freshclam_log"
      packages_after=$(ride_clamav_packages_snapshot)
      jq -e 'all(.[]; . == true)' <<< "$packages_after" >/dev/null || {
        ride_clamav_rollback_applying "$manifest_json" ||
          ride_die "ClamAV package verification failed and rollback is incomplete"
        rm -rf -- "$snapshot"; rm -f -- "$(ride_clamav_manifest)"
        ride_die "ClamAV RPMs are not both installed after the update"
      }
      python3 "$RIDE_ROOT/tools/clamav-state.py" copy "$RIDE_CLAMAV_DATA_DIR" "$snapshot/installed" ||
        ride_die "cannot snapshot the installed ClamAV signature state"
      local data_after_hash
      data_after_hash=$(ride_clamav_tree_hash "$RIDE_CLAMAV_DATA_DIR") || ride_die "cannot verify updated ClamAV data"
      related_after=$(ride_clamav_related_packages_snapshot) || ride_die "cannot record installed ClamAV RPM set"
      manifest_json=$(jq -c --arg hash "$data_after_hash" --argjson units "$units_after" \
        --argjson related "$related_after" \
        '.status="installed" | .dataAfterHash=$hash | .unitsAfter=$units | .relatedPackagesAfter=$related' \
        <<< "$manifest_json") ||
        ride_die "cannot finalize ClamAV recovery record"
      ride_clamav_write_manifest "$manifest_json" || ride_die "cannot finalize ClamAV ownership record"
      ride_clamav_observe | grep -Fxq installed || ride_die "installed ClamAV state failed its ownership check"
      ;;
    absent)
      [[ "$current" != unowned && "$current" != drifted ]] ||
        ride_die "ClamAV state is modified or has an incomplete transaction; refusing removal"
      if [[ "$current" == pending ]]; then
        manifest_json=$(cat "$(ride_clamav_manifest)")
        ride_clamav_rollback_applying "$manifest_json" ||
          ride_die "pending ClamAV transaction could not be restored; preserve its recovery files"
        rm -rf -- "$(ride_clamav_snapshot_dir)"
        rm -f -- "$(ride_clamav_manifest)"
        return 0
      fi
      [[ "$current" == installed ]] || return 0
      manifest_json=$(cat "$(ride_clamav_manifest)")
      local current_hash current_units installed_hash
      current_hash=$(ride_clamav_tree_hash "$RIDE_CLAMAV_DATA_DIR") || ride_die "cannot inspect ClamAV signatures"
      installed_hash=$(jq -r '.dataAfterHash' <<< "$manifest_json")
      [[ "$current_hash" == "$installed_hash" ]] || ride_die "ClamAV signature data changed after RIDE install"
      current_units=$(ride_clamav_units_snapshot)
      jq -e --argjson current "$current_units" '.unitsAfter == $current' <<< "$manifest_json" >/dev/null ||
        ride_die "FreshClam units changed after RIDE install"
      related_current=$(ride_clamav_related_packages_snapshot)
      jq -e --argjson current "$related_current" '.relatedPackagesAfter == $current' \
        <<< "$manifest_json" >/dev/null || ride_die "ClamAV RPM set changed after RIDE install"
      if ! ride_clamav_remove_introduced_packages "$manifest_json"; then
        ride_clamav_restore_installed_state "$manifest_json" ||
          ride_die "package removal failed and the installed ClamAV state could not be recovered"
        ride_die "cannot remove RIDE-added ClamAV RPMs; installed state was restored"
      fi
      related_current=$(ride_clamav_related_packages_snapshot)
      missing_before=$(jq -cn --argjson current "$related_current" \
        --argjson before "$(jq -c '.relatedPackagesBefore' <<< "$manifest_json")" \
        '[$before[] | select(. as $name | $current | index($name) | not)]') ||
        ride_die "cannot compare prior ClamAV RPMs"
      if (($(jq 'length' <<< "$missing_before") > 0)); then
        local -a restore_packages=()
        while IFS= read -r package; do [[ -n "$package" ]] && restore_packages+=("$package"); done \
          < <(jq -r '.[]' <<< "$missing_before")
        if ! dnf --setopt=gpgcheck=1 --setopt=localpkg_gpgcheck=1 install -y "${restore_packages[@]}"; then
          ride_clamav_restore_installed_state "$manifest_json" ||
            ride_die "pre-existing ClamAV RPM recovery failed and installed state could not be restored"
          ride_die "removal changed a pre-existing ClamAV RPM; the installed state was restored"
        fi
      fi
      related_current=$(ride_clamav_related_packages_snapshot)
      jq -e --argjson actual "$related_current" '
        all(.relatedPackagesBefore[]; . as $name | $actual | index($name) != null)
      ' <<< "$manifest_json" >/dev/null || {
        ride_clamav_restore_installed_state "$manifest_json" ||
          ride_die "pre-existing ClamAV RPM state could not be repaired and installed state could not be restored"
        ride_die "a pre-existing ClamAV RPM remains missing; installed state was restored"
      }
      ride_clamav_restore_data "$manifest_json" || {
        ride_clamav_restore_installed_state "$manifest_json" ||
          ride_die "signature restore failed and the installed ClamAV state could not be recovered"
        ride_die "could not restore the exact pre-install ClamAV signature state; installed state was restored"
      }
      current_units=$(ride_clamav_units_snapshot)
      local before_units
      before_units=$(jq -c '.unitsBefore' <<< "$manifest_json")
      jq -e --argjson actual "$current_units" '
        to_entries | all(.[]; if .value.load == "not-found" then true else $actual[.key] == .value end)
      ' <<< "$before_units" >/dev/null || {
        ride_clamav_restore_installed_state "$manifest_json" ||
          ride_die "unit-state restore failed and the installed ClamAV state could not be recovered"
        ride_die "FreshClam unit state differs from the recorded prior state; installed state was restored"
      }
      rm -rf -- "$(ride_clamav_snapshot_dir)" || ride_die "cannot remove ClamAV recovery snapshot"
      rm -f -- "$(ride_clamav_manifest)" || ride_die "cannot remove ClamAV ownership record"
      ;;
    *) ride_die "invalid ClamAV operation state: $state" ;;
  esac
}
