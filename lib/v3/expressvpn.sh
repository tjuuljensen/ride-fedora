#!/usr/bin/env bash

ride_expressvpn_test_path() {
  local variable=$1 default=$2
  if [[ ${RIDE_TEST_MODE:-0} == 1 && $EUID -ne 0 && -n ${!variable:-} ]]; then
    printf '%s\n' "${!variable}"
  else
    printf '%s\n' "$default"
  fi
}

ride_expressvpn_state_dir() {
  ride_expressvpn_test_path RIDE_EXPRESSVPN_STATE_DIR /var/lib/ride-fedora/expressvpn
}

ride_expressvpn_artifact_dir() {
  local cache
  cache=$(ride_cache_dir)
  ride_expressvpn_test_path RIDE_EXPRESSVPN_ARTIFACT_DIR "$cache/artifacts/package.expressvpn"
}

ride_expressvpn_app_root() {
  ride_expressvpn_test_path RIDE_EXPRESSVPN_APP_ROOT /opt/expressvpn
}

ride_expressvpn_service_unit() {
  ride_expressvpn_test_path RIDE_EXPRESSVPN_SERVICE_UNIT /etc/systemd/system/expressvpn-service.service
}

ride_expressvpn_service_link() {
  ride_expressvpn_test_path RIDE_EXPRESSVPN_SERVICE_LINK /etc/systemd/system/multi-user.target.wants/expressvpn-service.service
}

ride_expressvpn_desktop_entry() {
  ride_expressvpn_test_path RIDE_EXPRESSVPN_DESKTOP_ENTRY /usr/share/applications/expressvpn.desktop
}

ride_expressvpn_cli_link() {
  ride_expressvpn_test_path RIDE_EXPRESSVPN_CLI_LINK /usr/bin/expressvpn
}

ride_expressvpn_ctl_link() {
  ride_expressvpn_test_path RIDE_EXPRESSVPN_CTL_LINK /usr/bin/expressvpnctl
}

ride_expressvpn_nm_config() {
  ride_expressvpn_test_path RIDE_EXPRESSVPN_NM_CONFIG /etc/NetworkManager/conf.d/wgexpressvpn.conf
}

ride_expressvpn_rt_tables() {
  ride_expressvpn_test_path RIDE_EXPRESSVPN_RT_TABLES /etc/iproute2/rt_tables
}

ride_expressvpn_root_config() {
  ride_expressvpn_test_path RIDE_EXPRESSVPN_ROOT_CONFIG /root/.config/expressvpn
}

ride_expressvpn_manifest() {
  printf '%s/manifest.json\n' "$(ride_expressvpn_state_dir)"
}

ride_expressvpn_hash_path() {
  local path=$1
  if [[ -L "$path" ]]; then
    ride_die "ExpressVPN recovery path became a symlink; preserving it: $path"
  elif [[ -f "$path" ]]; then
    sha256sum -- "$path" | cut -d' ' -f1
  elif [[ -d "$path" ]]; then
    tar --sort=name --numeric-owner -cf - -C "$(dirname -- "$path")" "$(basename -- "$path")" |
      sha256sum | cut -d' ' -f1
  elif [[ -e "$path" ]]; then
    ride_die "ExpressVPN recovery path has an unsupported file type: $path"
  else
    printf 'absent\n'
  fi
}

ride_expressvpn_capture_path() {
  local label=$1 path=$2 kind=$3 state_dir=$4 present=false backup hash
  backup="$state_dir/$label.before"
  if [[ -L "$path" ]]; then
    ride_die "refusing to snapshot a symlink at $path"
  elif [[ -e "$path" ]]; then
    if [[ "$kind" == file && ! -f "$path" ]] ||
       [[ "$kind" == directory && ! -d "$path" ]]; then
      ride_die "unexpected ExpressVPN recovery path type: $path"
    fi
    cp -a -- "$path" "$backup" || ride_die "cannot snapshot $path"
    hash=$(ride_expressvpn_hash_path "$path")
    present=true
  else
    hash=absent
  fi
  jq --arg label "$label" --arg path "$path" --arg backup "$backup" \
     --arg hash "$hash" --argjson present "$present" \
     '.snapshots[$label] = {path:$path, backup:$backup, beforePresent:$present,
       beforeHash:$hash, afterHash:null}' \
     "$state_dir/manifest.json" > "$state_dir/manifest.tmp" ||
    ride_die "cannot record ExpressVPN recovery snapshot for $path"
  chmod 0600 "$state_dir/manifest.tmp"
  mv -f -- "$state_dir/manifest.tmp" "$state_dir/manifest.json"
}

ride_expressvpn_record_after_path() {
  local label=$1 state_dir=$2 path hash
  path=$(jq -er --arg label "$label" '.snapshots[$label].path' "$state_dir/manifest.json") ||
    ride_die "missing ExpressVPN recovery path for $label"
  hash=$(ride_expressvpn_hash_path "$path")
  jq --arg label "$label" --arg hash "$hash" \
     '.snapshots[$label].afterHash = $hash' "$state_dir/manifest.json" > "$state_dir/manifest.tmp" ||
    ride_die "cannot record installed ExpressVPN state for $path"
  chmod 0600 "$state_dir/manifest.tmp"
  mv -f -- "$state_dir/manifest.tmp" "$state_dir/manifest.json"
}

ride_expressvpn_capture_policy_rules() {
  local state_dir=$1 name=$2 output line priority path hash
  path="$state_dir/policy-rules.$name"
  output=$(ip -o rule show) || ride_die "cannot snapshot policy-routing rules"
  : > "$path" || ride_die "cannot create private policy-rule snapshot"
  while IFS= read -r line; do
    line=${line//$'\t'/ }
    [[ -n "$line" ]] || continue
    priority=${line%%:*}
    case "$priority" in
      0|32766|32767) continue ;;
      50)
        [[ "$line" == '50: from all lookup main suppress_prefixlength 1' ]] ||
          ride_die "unexpected priority 50 policy rule; preserving it"
        continue
        ;;
      70)
        [[ "$line" == '70: from all fwmark 0x3214 lookup evpnFwdrt' ]] ||
          ride_die "unexpected priority 70 policy rule; preserving it"
        continue
        ;;
    esac
    [[ "$line" != *'lookup evpnFwdrt'* ]] ||
      ride_die "unexpected ExpressVPN routing-table rule; preserving it"
    printf '%s\n' "$line" >> "$path"
  done <<< "$output"
  chmod 0600 "$path"
  hash=$(sha256sum -- "$path" | cut -d' ' -f1)
  jq --arg name "$name" --arg path "$path" --arg hash "$hash" \
     '.policyRules[$name] = {path:$path, sha256:$hash}' \
     "$state_dir/manifest.json" > "$state_dir/manifest.tmp" ||
    ride_die "cannot record policy-rule recovery snapshot"
  chmod 0600 "$state_dir/manifest.tmp"
  mv -f -- "$state_dir/manifest.tmp" "$state_dir/manifest.json"
}

ride_expressvpn_restore_policy_rules() {
  local state_dir=$1 name=$2 path expected actual current line priority body
  local -a arguments=()
  path=$(jq -er --arg name "$name" '.policyRules[$name].path' "$state_dir/manifest.json") ||
    ride_die "missing policy-rule snapshot for $name"
  expected=$(jq -er --arg name "$name" '.policyRules[$name].sha256' "$state_dir/manifest.json") ||
    ride_die "missing policy-rule snapshot digest for $name"
  [[ "$path" == "$state_dir/policy-rules.$name" && -f "$path" && ! -L "$path" ]] ||
    ride_die "unsafe policy-rule snapshot for $name"
  actual=$(sha256sum -- "$path" | cut -d' ' -f1)
  [[ "$actual" == "$expected" ]] || ride_die "policy-rule recovery snapshot changed: $path"
  current=$(ip -o rule show) || ride_die "cannot query current policy-routing rules"
  current=${current//$'\t'/ }
  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    grep -Fxq -- "$line" <<< "$current" && continue
    priority=${line%%:*}
    if grep -Eq "^${priority}:[[:space:]]" <<< "$current"; then
      ride_die "policy rule priority $priority changed after ExpressVPN staging; preserving current rules"
    fi
    body=${line#*: }
    read -r -a arguments <<< "$body"
    ip rule add priority "$priority" "${arguments[@]}" ||
      ride_die "cannot restore pre-existing policy rule: $line"
    current=$(ip -o rule show) || ride_die "cannot verify restored policy-routing rules"
    current=${current//$'\t'/ }
    grep -Fxq -- "$line" <<< "$current" || ride_die "restored policy rule differs from its snapshot: $line"
  done < "$path"
}

ride_expressvpn_restore_path() {
  local label=$1 state_dir=$2 path backup before_present before_hash after_hash current temporary
  path=$(jq -er --arg label "$label" '.snapshots[$label].path' "$state_dir/manifest.json") ||
    ride_die "missing ExpressVPN recovery path for $label"
  backup=$(jq -er --arg label "$label" '.snapshots[$label].backup' "$state_dir/manifest.json") ||
    ride_die "missing ExpressVPN backup path for $label"
  before_present=$(jq -er --arg label "$label" '.snapshots[$label].beforePresent' "$state_dir/manifest.json")
  before_hash=$(jq -er --arg label "$label" '.snapshots[$label].beforeHash' "$state_dir/manifest.json")
  after_hash=$(jq -er --arg label "$label" '.snapshots[$label].afterHash' "$state_dir/manifest.json")
  [[ "$backup" == "$state_dir/"* ]] || ride_die "unsafe ExpressVPN backup path"
  current=$(ride_expressvpn_hash_path "$path")

  if [[ "$before_present" == true ]]; then
    [[ -f "$backup" || -d "$backup" ]] || ride_die "ExpressVPN recovery backup is missing: $backup"
    if [[ "$current" != absent && "$current" != "$before_hash" && "$current" != "$after_hash" ]]; then
      ride_die "ExpressVPN recovery path changed after install; preserving it: $path"
    fi
    if [[ "$current" != "$before_hash" ]]; then
      temporary="$state_dir/restore-$label.current"
      [[ ! -e "$temporary" && ! -L "$temporary" ]] || ride_die "restore temporary path already exists"
      if [[ "$current" != absent ]]; then
        mv -T -- "$path" "$temporary" || ride_die "cannot preserve current state at $path"
      fi
      if ! cp -a -- "$backup" "$path"; then
        [[ ! -e "$temporary" ]] || mv -T -- "$temporary" "$path" || true
        ride_die "cannot restore $path"
      fi
      rm -rf -- "$temporary"
    fi
  elif [[ "$current" != absent ]]; then
    [[ "$current" == "$after_hash" ]] ||
      ride_die "ExpressVPN-created path changed after install; preserving it: $path"
    rm -rf -- "$path" || ride_die "cannot remove ExpressVPN-created config: $path"
  fi
}

ride_expressvpn_state_valid() {
  local state_dir=$1 manifest
  manifest=$(ride_expressvpn_manifest)
  [[ -d "$state_dir" && ! -L "$state_dir" && -f "$manifest" && ! -L "$manifest" ]] || return 1
  jq -e '.schemaVersion == 1 and .operationId == "package.expressvpn" and
    (.snapshots | type == "object") and
    (.snapshots.networkManager | type == "object") and
    (.snapshots.routeTables | type == "object") and
    (.snapshots.rootConfig | type == "object") and (.policyRules | type == "object") and
    (.policyRules.before | type == "object")' \
    "$manifest" >/dev/null 2>&1
}

ride_expressvpn_observe() {
  local state_dir app_root service_unit desktop_entry cli_link ctl_link
  state_dir=$(ride_expressvpn_state_dir)
  app_root=$(ride_expressvpn_app_root)
  service_unit=$(ride_expressvpn_service_unit)
  desktop_entry=$(ride_expressvpn_desktop_entry)
  cli_link=$(ride_expressvpn_cli_link)
  ctl_link=$(ride_expressvpn_ctl_link)
  if ride_expressvpn_state_valid "$state_dir" || [[ -e "$app_root" || -L "$app_root" ||
       -e "$service_unit" || -L "$service_unit" || -e "$desktop_entry" ||
       -e "$cli_link" || -e "$ctl_link" ]]; then
    printf 'installed\n'
  else
    printf 'absent\n'
  fi
}

ride_expressvpn_validate_entry() {
  jq -e '
    .id == "package.expressvpn" and .handler == "expressvpn-wrapper" and
    .sourceId == "expressvpn-signed-local" and .version == "14.3.1.15429" and
    .sourceSha256 == "f784af6628564f4fcb0a82064d4dc1f22520c3c917bb1c882bd61eb621b31efb" and
    .signingFingerprint == "1D0B09AD6C93FEE93FDDBD9DAFF2A1415F6A3A38"
  ' <<< "$1" >/dev/null || ride_die "ExpressVPN catalog identity is invalid"
}

ride_expressvpn_verify_artifacts() {
  local entry=$1 directory asset signature key expected fingerprint actual temp temp_root status mode input
  directory=$(ride_expressvpn_artifact_dir)
  asset=$(jq -r '.assetName' <<< "$entry")
  signature=$(jq -r '.signatureAssetName' <<< "$entry")
  key=$(jq -r '.signingKeyAssetName' <<< "$entry")
  expected=$(jq -r '.sourceSha256' <<< "$entry")
  fingerprint=$(jq -r '.signingFingerprint' <<< "$entry")
  [[ -d "$directory" && ! -L "$directory" ]] ||
    ride_die "stage the signed ExpressVPN installer files in $directory"
  for input in "$directory/$asset" "$directory/$signature" "$directory/$key"; do
    [[ -f "$input" && ! -L "$input" && -r "$input" ]] ||
      ride_die "required ExpressVPN installer input is missing or unsafe: $input"
    if [[ ${RIDE_TEST_MODE:-0} != 1 ]]; then
      mode=$(stat -c %a -- "$input")
      if [[ "$(stat -c %u -- "$input")" != 0 ]] || (( (8#$mode & 0022) != 0 )); then
        ride_die "ExpressVPN installer inputs must be root-owned and not group/world writable: $input"
      fi
    fi
  done
  [[ -x "$directory/$asset" ]] ||
    ride_die "staged ExpressVPN installer must be executable by root: $directory/$asset"
  actual=$(sha256sum -- "$directory/$asset" | cut -d' ' -f1)
  [[ "$actual" == "$expected" ]] || ride_die "ExpressVPN installer SHA-256 does not match the catalog"
  ride_require_command gpg
  temp_root="$directory/.verify"
  if [[ -e "$temp_root" || -L "$temp_root" ]]; then
    [[ -d "$temp_root" && ! -L "$temp_root" ]] || ride_die "unsafe ExpressVPN verification directory"
  else
    install -d -m 0700 "$temp_root" || ride_die "cannot create ExpressVPN verification directory"
  fi
  temp=$(mktemp -d "$temp_root/gnupg.XXXXXXXX") || ride_die "cannot create temporary ExpressVPN keyring"
  chmod 0700 "$temp"
  if ! gpg --batch --homedir "$temp" --import "$directory/$key" >/dev/null 2>&1; then
    rm -rf -- "$temp"
    ride_die "could not import the staged ExpressVPN signing key"
  fi
  actual=$(gpg --batch --homedir "$temp" --with-colons --fingerprint 2>/dev/null |
    awk -F: '$1 == "fpr" {print $10; exit}')
  if [[ "$actual" != "$fingerprint" ]]; then
    rm -rf -- "$temp"
    ride_die "staged ExpressVPN signing key fingerprint does not match the pinned fingerprint"
  fi
  status=$(gpg --batch --homedir "$temp" --status-fd 1 --verify \
    "$directory/$signature" "$directory/$asset" 2>/dev/null || true)
  rm -rf -- "$temp"
  grep -Fq "[GNUPG:] VALIDSIG $fingerprint " <<< "$status" ||
    ride_die "ExpressVPN installer detached signature is invalid"
  printf '%s\n' "$directory/$asset"
}

ride_expressvpn_preflight_install() {
  local entry=$1 app_root unit state_dir nm_config rt_tables desktop_entry cli_link ctl_link
  ride_expressvpn_validate_entry "$entry"
  app_root=$(ride_expressvpn_app_root)
  unit=$(ride_expressvpn_service_unit)
  state_dir=$(ride_expressvpn_state_dir)
  nm_config=$(ride_expressvpn_nm_config)
  rt_tables=$(ride_expressvpn_rt_tables)
  desktop_entry=$(ride_expressvpn_desktop_entry)
  cli_link=$(ride_expressvpn_cli_link)
  ctl_link=$(ride_expressvpn_ctl_link)
  [[ ! -e "$state_dir" && ! -L "$state_dir" ]] ||
    ride_die "ExpressVPN has an incomplete RIDE state record; remove or recover it before reinstalling"
  [[ ! -e "$app_root" && ! -L "$app_root" && ! -e "$unit" && ! -L "$unit" &&
     ! -e "$desktop_entry" && ! -e "$cli_link" && ! -e "$ctl_link" ]] ||
    ride_die "ExpressVPN files already exist outside this RIDE deployment; refusing to replace them"
  [[ ! -e "$nm_config" || ( -f "$nm_config" && ! -L "$nm_config" ) ]] ||
    ride_die "ExpressVPN NetworkManager config path is not a regular file"
  [[ ! -e "$rt_tables" || ( -f "$rt_tables" && ! -L "$rt_tables" ) ]] ||
    ride_die "iproute2 table registry is not a regular file"
  if ip -o rule show | grep -Eq '^(50|70):|lookup evpnFwdrt'; then
    ride_die "policy-routing entries conflict with ExpressVPN; refusing to install"
  fi
  if [[ -f "$rt_tables" ]] && grep -Eiq '^[[:space:]]*[0-9]+[[:space:]]+evpnFwdrt([[:space:]]|$)' "$rt_tables"; then
    ride_die "routing table evpnFwdrt already exists; refusing to install"
  fi
  ride_require_command dnf
  ride_require_command systemctl
  ride_require_command ip
  ride_require_command rpm
  ride_require_command stat
  ride_require_command tar
  ride_require_command timeout
}

ride_expressvpn_start_manifest() {
  local entry=$1 installer=$2 state_dir=$3
  umask 077
  if ! mkdir -p -- "$state_dir" || ! chmod 0700 -- "$state_dir"; then
    ride_die "cannot create private ExpressVPN state directory"
  fi
  mkdir -m 0700 -- "$state_dir/backups" || ride_die "cannot create ExpressVPN recovery backups"
  jq -n --arg id package.expressvpn --arg version "$(jq -r '.version' <<< "$entry")" \
    --arg sha "$(jq -r '.sourceSha256' <<< "$entry")" --arg installer "$installer" \
    '{schemaVersion:1,operationId:$id,version:$version,installerSha256:$sha,installerPath:$installer,
      status:"installing",snapshots:{},policyRules:{}}' > "$state_dir/manifest.json" ||
    ride_die "cannot write ExpressVPN recovery manifest"
  chmod 0600 "$state_dir/manifest.json"
  ride_expressvpn_capture_policy_rules "$state_dir" before
  ride_expressvpn_capture_path networkManager "$(ride_expressvpn_nm_config)" file "$state_dir"
  ride_expressvpn_capture_path routeTables "$(ride_expressvpn_rt_tables)" file "$state_dir"
  ride_expressvpn_capture_path rootConfig "$(ride_expressvpn_root_config)" directory "$state_dir"
}

ride_expressvpn_has_vpn_connection() {
  local output
  output="$("$(ride_expressvpn_app_root)/bin/expressvpnctl" status 2>&1)" ||
    ride_die "cannot determine ExpressVPN connection state; refusing removal"
  if grep -Eiq 'not[[:space:]]+(connected|protected)|disconnected|not logged in' <<< "$output"; then
    return 1
  fi
  grep -Eiq 'connected|protected' <<< "$output"
}

ride_expressvpn_unit_matches() {
  local unit=$1
  [[ -f "$unit" && ! -L "$unit" ]] || return 1
  grep -Fxq 'Description=ExpressVPN daemon' "$unit" &&
  grep -Fxq "ExecStart=$(ride_expressvpn_app_root)/bin/expressvpn-daemon" "$unit" &&
    grep -Fxq "Environment=\"LD_LIBRARY_PATH=$(ride_expressvpn_app_root)/lib\"" "$unit"
}

ride_expressvpn_cleanup_unit() {
  local unit=$1 link
  link=$(ride_expressvpn_service_link)
  if [[ -e "$unit" || -L "$unit" ]]; then
    ride_expressvpn_unit_matches "$unit" || ride_die "ExpressVPN service unit changed; preserving it: $unit"
    systemctl disable --now expressvpn-service.service >/dev/null 2>&1 || true
    [[ "$(systemctl is-active expressvpn-service.service 2>/dev/null || true)" != active ]] ||
      ride_die "ExpressVPN service is still active"
    rm -f -- "$unit" || ride_die "cannot remove stale ExpressVPN service unit"
  fi
  if [[ -L "$link" ]]; then
    [[ "$(readlink -- "$link")" == "$unit" ]] || ride_die "ExpressVPN service enablement link changed"
    rm -f -- "$link" || ride_die "cannot remove stale ExpressVPN service enablement"
  elif [[ -e "$link" ]]; then
    ride_die "ExpressVPN service enablement path is not a symlink"
  fi
  systemctl daemon-reload || ride_die "systemd could not reload after ExpressVPN removal"
  systemctl reset-failed expressvpn-service.service >/dev/null 2>&1 || true
  [[ "$(systemctl is-enabled expressvpn-service.service 2>/dev/null || true)" != enabled ]] ||
    ride_die "ExpressVPN service remains enabled after cleanup"
}

ride_expressvpn_remove_owned_rules() {
  local rules rule
  rules=$(ip -o rule show)
  while IFS= read -r rule; do
    rule=${rule//$'\t'/ }
    [[ -n "$rule" ]] || continue
    case "$rule" in
      '50: from all lookup main suppress_prefixlength 1')
        ip rule del priority 50 lookup main suppress_prefixlength 1 ||
          ride_die "cannot remove ExpressVPN policy-routing rule at priority 50"
        ;;
      '70: from all fwmark 0x3214 lookup evpnFwdrt')
        ip rule del priority 70 fwmark 0x3214 lookup evpnFwdrt ||
          ride_die "cannot remove ExpressVPN policy-routing rule at priority 70"
        ;;
      50:*|70:*) ride_die "unexpected rule uses an ExpressVPN policy-routing priority; preserving it" ;;
      *'lookup evpnFwdrt'*) ride_die "unexpected ExpressVPN routing-table rule; preserving it" ;;
    esac
  done <<< "$rules"
}

ride_expressvpn_restore_snapshots() {
  local state_dir=$1
  ride_expressvpn_restore_path networkManager "$state_dir"
  ride_expressvpn_restore_path routeTables "$state_dir"
  ride_expressvpn_restore_path rootConfig "$state_dir"
}

ride_expressvpn_check_remove_snapshots() {
  local state_dir=$1 label path before_present before_hash after_hash current app_root
  app_root=$(ride_expressvpn_app_root)
  for label in networkManager routeTables rootConfig; do
    path=$(jq -er --arg label "$label" '.snapshots[$label].path' "$state_dir/manifest.json") ||
      ride_die "missing ExpressVPN recovery path for $label"
    before_present=$(jq -er --arg label "$label" '.snapshots[$label].beforePresent' "$state_dir/manifest.json")
    before_hash=$(jq -er --arg label "$label" '.snapshots[$label].beforeHash' "$state_dir/manifest.json")
    after_hash=$(jq -er --arg label "$label" '.snapshots[$label].afterHash' "$state_dir/manifest.json")
    current=$(ride_expressvpn_hash_path "$path")
    if [[ "$before_present" == true ]]; then
      if [[ "$current" == absent && "$after_hash" != absent && -e "$app_root" ]]; then
        ride_die "pre-existing ExpressVPN recovery path disappeared after install; preserving removal state: $path"
      fi
      [[ "$current" == "$before_hash" || "$current" == "$after_hash" || "$current" == absent ]] ||
        ride_die "ExpressVPN recovery path changed after install; preserving it: $path"
    else
      [[ "$current" == absent || "$current" == "$after_hash" ]] ||
        ride_die "ExpressVPN-created recovery path changed after install; preserving it: $path"
    fi
  done
}

ride_expressvpn_change() {
  local entry=$1 state=$2 installer state_dir manifest uninstaller app_root unit nm_config rt_tables desktop_entry cli_link ctl_link rules_snapshot=before
  [[ "$RIDE_OS_ID" == fedora && "$RIDE_OS_VERSION" == 44 && "$RIDE_ARCH" == x86_64 ]] ||
    ride_die "ExpressVPN wrapper requires Fedora 44 x86_64"
  ride_expressvpn_validate_entry "$entry"
  app_root=$(ride_expressvpn_app_root)
  unit=$(ride_expressvpn_service_unit)
  nm_config=$(ride_expressvpn_nm_config)
  rt_tables=$(ride_expressvpn_rt_tables)
  desktop_entry=$(ride_expressvpn_desktop_entry)
  cli_link=$(ride_expressvpn_cli_link)
  ctl_link=$(ride_expressvpn_ctl_link)
  state_dir=$(ride_expressvpn_state_dir)
  manifest=$(ride_expressvpn_manifest)

  case "$state" in
    installed)
      if ride_expressvpn_state_valid "$state_dir"; then
        [[ "$(jq -r '.status' "$manifest")" == installed ]] ||
          ride_die "ExpressVPN has an incomplete RIDE install record; recover it before retrying"
        [[ -x "$app_root/bin/expressvpnctl" && -x "$app_root/bin/expressvpn-uninstall.sh" &&
           -f "$unit" ]] ||
          ride_die "ExpressVPN RIDE state exists but installed files are incomplete; remove or recover it before retrying"
        return 0
      fi
      ride_expressvpn_preflight_install "$entry"
      installer=$(ride_expressvpn_verify_artifacts "$entry") ||
        ride_die "ExpressVPN artifact verification failed; no installer was run"
      ride_expressvpn_start_manifest "$entry" "$installer" "$state_dir"
      dnf --setopt=gpgcheck=1 --setopt=localpkg_gpgcheck=1 install -y libatomic ||
        ride_die "could not install ExpressVPN's Fedora libatomic prerequisite; recovery state is retained at $state_dir"
      if ! env -u SUDO_USER HOME=/root timeout --foreground 1200 \
           "$installer" -- --no-gui --force-update; then
        ride_expressvpn_restore_policy_rules "$state_dir" before
        ride_die "ExpressVPN installer failed; private recovery state is retained at $state_dir"
      fi
      ride_expressvpn_restore_policy_rules "$state_dir" before
      [[ -x "$app_root/bin/expressvpnctl" && -x "$app_root/bin/expressvpn-uninstall.sh" &&
         -f "$unit" ]] || ride_die "ExpressVPN installation is incomplete; recovery state is retained"
      ride_expressvpn_record_after_path networkManager "$state_dir"
      ride_expressvpn_record_after_path routeTables "$state_dir"
      ride_expressvpn_record_after_path rootConfig "$state_dir"
      jq '.status = "installed"' "$manifest" > "$state_dir/manifest.tmp"
      chmod 0600 "$state_dir/manifest.tmp"
      mv -f -- "$state_dir/manifest.tmp" "$manifest"
      ;;
    absent)
      if ! ride_expressvpn_state_valid "$state_dir"; then
        [[ ! -e "$app_root" && ! -L "$app_root" && ! -e "$unit" && ! -L "$unit" &&
           ! -e "$desktop_entry" && ! -e "$cli_link" && ! -e "$ctl_link" ]] ||
          ride_die "ExpressVPN is present without RIDE ownership; refusing vendor removal"
        return 0
      fi
      [[ "$(jq -r '.status' "$manifest")" == installed ||
         "$(jq -r '.status' "$manifest")" == removing ]] ||
        ride_die "ExpressVPN has an incomplete RIDE install record; recovery is required before removal"
      ride_expressvpn_check_remove_snapshots "$state_dir"
      if [[ -x "$app_root/bin/expressvpnctl" ]]; then
        if ride_expressvpn_has_vpn_connection; then
          ride_die "ExpressVPN is connected; disconnect it before removal"
        fi
        ride_expressvpn_capture_policy_rules "$state_dir" remove
        rules_snapshot=remove
        uninstaller="$app_root/bin/expressvpn-uninstall.sh"
        [[ -x "$uninstaller" && ! -L "$uninstaller" ]] ||
          ride_die "ExpressVPN uninstaller is missing or unsafe"
        jq '.status = "removing"' "$manifest" > "$state_dir/manifest.tmp"
        chmod 0600 "$state_dir/manifest.tmp"
        mv -f -- "$state_dir/manifest.tmp" "$manifest"
        if ! printf 'y\nx' | env -u SUDO_USER HOME=/root timeout --foreground 1200 "$uninstaller"; then
          ride_die "ExpressVPN vendor uninstaller failed; recovery state is retained at $state_dir"
        fi
      fi
      [[ ! -e "$app_root" && ! -L "$app_root" ]] ||
        ride_die "ExpressVPN app files remain after uninstall; recovery state is retained"
      ride_expressvpn_cleanup_unit "$unit"
      ride_expressvpn_remove_owned_rules
      ride_expressvpn_restore_policy_rules "$state_dir" "$rules_snapshot"
      [[ ! -e "$desktop_entry" && ! -e "$cli_link" && ! -e "$ctl_link" ]] ||
        ride_die "ExpressVPN desktop or CLI residue remains; recovery state is retained"
      ride_expressvpn_restore_snapshots "$state_dir"
      rm -rf -- "$state_dir"
      ;;
    *) ride_die "invalid ExpressVPN state: $state" ;;
  esac
}
