#!/usr/bin/env bash

ride_rpmfusion_marker_dir() { printf '/var/lib/ride-fedora/ownership\n'; }
ride_rpmfusion_marker() { printf '%s/rpmfusion-repositories.json\n' "$(ride_rpmfusion_marker_dir)"; }
ride_rpmfusion_key_dir() { printf '/usr/share/distribution-gpg-keys/rpmfusion\n'; }

ride_rpmfusion_packages() {
  printf '%s\n' rpmfusion-free-release rpmfusion-nonfree-release
}

ride_rpmfusion_marker_content() {
  printf '{"schemaVersion":1,"operation":"setting.rpmfusion-repositories","fedoraRelease":"44","packages":["rpmfusion-free-release","rpmfusion-nonfree-release"]}\n'
}

ride_rpmfusion_marker_valid() {
  local marker
  marker=$(ride_rpmfusion_marker)
  [[ -f "$marker" && ! -L "$marker" && "$(stat -c '%u:%g:%a:%h' -- "$marker")" == 0:0:600:1 ]] &&
    cmp -s -- "$marker" <(ride_rpmfusion_marker_content)
}

ride_rpmfusion_installed_pair() {
  rpm -q --quiet rpmfusion-free-release rpmfusion-nonfree-release
}

ride_rpmfusion_owned_files_ok() {
  local package
  while IFS= read -r package; do
    rpm -q --quiet "$package" || continue
    rpm -V "$package" >/dev/null || return 1
  done < <(ride_rpmfusion_packages)
}

ride_rpmfusion_state() {
  local marker
  marker=$(ride_rpmfusion_marker)
  if ! ride_rpmfusion_installed_pair; then
    if [[ ! -e "$marker" && ! -L "$marker" ]]; then printf 'absent\n'; else printf 'unowned\n'; fi
    return
  fi
  if ride_rpmfusion_marker_valid; then
    if ride_rpmfusion_installed_pair && ride_rpmfusion_owned_files_ok; then
      printf 'configured\n'
    elif ride_rpmfusion_owned_files_ok; then
      printf 'partial\n'
    else
      printf 'unowned\n'
    fi
  else
    printf 'unowned\n'
  fi
}

ride_rpmfusion_guard() {
  local desired=$1 state marker_dir marker
  state=$(ride_rpmfusion_state) || ride_die "cannot inspect RPM Fusion state"
  if [[ "$desired" == configured ]]; then
    [[ "$state" == absent || "$state" == configured || "$state" == partial ]] ||
      ride_die "RPM Fusion release packages or ownership state conflict with RIDE"
  else
    [[ "$state" == configured || "$state" == partial || "$state" == absent ]] ||
      ride_die "RPM Fusion release packages are not owned and verified by RIDE"
    if [[ "$state" != absent ]]; then
      if ride_rpmfusion_has_foreign_packages; then
        ride_die "cannot remove RPM Fusion repositories while signed packages still depend on them"
      else
        local query_status=$?
        [[ "$query_status" == 1 ]] || ride_die "cannot inspect installed RPM signatures"
      fi
    fi
  fi
  marker_dir=$(ride_rpmfusion_marker_dir)
  marker=$(ride_rpmfusion_marker)
  if [[ -e "$marker_dir" ]]; then
    [[ -d "$marker_dir" && ! -L "$marker_dir" && "$(stat -c '%u:%g:%a' -- "$marker_dir")" == 0:0:700 ]] ||
      ride_die "RPM Fusion ownership directory is not private and root-owned"
  fi
  [[ ! -e "$marker" && ! -L "$marker" || "$state" == configured ]] ||
    [[ "$state" == partial ]] || ride_die "RPM Fusion ownership marker already exists"
}

ride_rpmfusion_has_foreign_packages() {
  local records name signature
  records=$(rpm -qa --qf '[%{NAME}\t%{RSAHEADER:pgpsig}\n]') || return 2
  while IFS=$'\t' read -r name signature; do
    [[ "$name" == rpmfusion-free-release || "$name" == rpmfusion-nonfree-release ]] && continue
    if [[ "${signature,,}" == *e06f8ecdd651ff2e* || "${signature,,}" == *6a2af96194843c65* ]]; then
      return 0
    fi
  done <<< "$records"
  return 1
}

ride_rpmfusion_download_verify() {
  local tempdir=$1 family key key_target fingerprint url rpmfile keyring expected_name metadata
  local -a families=(free nonfree)
  ride_require_command curl
  ride_require_command rpm
  rpm -q --quiet distribution-gpg-keys || ride_die "Fedora distribution-gpg-keys package is required"
  if [[ ! -f "$(ride_rpmfusion_key_dir)/RPM-GPG-KEY-rpmfusion-free-fedora-44" ||
        ! -f "$(ride_rpmfusion_key_dir)/RPM-GPG-KEY-rpmfusion-nonfree-fedora-44" ]]; then
    ride_require_command dnf5
    dnf5 upgrade --refresh -y distribution-gpg-keys || ride_die "cannot update Fedora distribution signing keys"
  fi
  rpm -V distribution-gpg-keys >/dev/null || ride_die "Fedora distribution-gpg-keys package failed integrity verification"
  keyring="$tempdir/rpm-keyring"
  mkdir -m 0700 -- "$keyring" || return 1
  for family in "${families[@]}"; do
    if [[ "$family" == free ]]; then
      key="$(ride_rpmfusion_key_dir)/RPM-GPG-KEY-rpmfusion-free-fedora-44"
      fingerprint=E9A491A3DE247814E7E067EAE06F8ECDD651FF2E
      url=https://download1.rpmfusion.org/free/fedora/updates/44/x86_64/r/rpmfusion-free-release-44-3.noarch.rpm
      expected_name=rpmfusion-free-release
    else
      key="$(ride_rpmfusion_key_dir)/RPM-GPG-KEY-rpmfusion-nonfree-fedora-44"
      fingerprint=79BDB88F9BBF73910FD4095B6A2AF96194843C65
      url=https://download1.rpmfusion.org/nonfree/fedora/updates/44/x86_64/r/rpmfusion-nonfree-release-44-3.noarch.rpm
      expected_name=rpmfusion-nonfree-release
    fi
    key_target=$(realpath -e -- "$key") || ride_die "Fedora packaged RPM Fusion key is missing: $key"
    [[ "$key_target" == "$(ride_rpmfusion_key_dir)"/* && -f "$key_target" && ! -L "$key_target" ]] ||
      ride_die "Fedora packaged RPM Fusion key resolves outside its owned key directory: $key"
    [[ "$(gpg --show-keys --with-colons --fingerprint "$key" | awk -F: '$1 == "fpr" {print toupper($10); exit}')" == "$fingerprint" ]] ||
      ride_die "Fedora packaged RPM Fusion key fingerprint mismatch"
    rpm --define '_keyring fs' --define "_keyringpath $keyring" --import "$key" ||
      { ride_error "cannot import Fedora-packaged RPM Fusion key: $family"; return 1; }
    rpmfile="$tempdir/$family.rpm"
    curl --fail --location --proto '=https' --tlsv1.2 --max-filesize 10485760 --output "$rpmfile" "$url" ||
      { ride_error "cannot download RPM Fusion release package: $family"; return 1; }
    metadata=$(rpm -qp --qf '%{NAME} %{VERSION}-%{RELEASE} %{LICENSE} %{ARCH}' "$rpmfile") ||
      { ride_error "cannot inspect RPM Fusion release package: $family"; return 1; }
    [[ "$metadata" == "$expected_name 44-3 BSD noarch" ]] || ride_die "unexpected RPM Fusion release package metadata: $metadata"
    while IFS= read -r path; do
      [[ -n "$path" ]] || continue
      if [[ -e "$path" || -L "$path" ]]; then
        [[ -d "$path" && ! -L "$path" ]] || ride_die "RPM Fusion package path already exists outside RIDE ownership: $path"
      fi
    done < <(rpm -qp --qf '[%{FILENAMES}\n]' "$rpmfile")
    local signature_result
    signature_result=$(rpm --define '_keyring fs' --define "_keyringpath $keyring" --checksig --verbose "$rpmfile") ||
      ride_die "RPM Fusion release package signature verification failed: $family"
    if ! grep -F "key fingerprint: ${fingerprint,,}: OK" <<< "$signature_result" >/dev/null ||
        ! grep -F 'Payload SHA256 digest: OK' <<< "$signature_result" >/dev/null; then
      ride_die "RPM Fusion release package signature or payload verification failed: $family"
    fi
  done
}

ride_rpmfusion_write_marker() {
  local dir marker temp
  dir=$(ride_rpmfusion_marker_dir)
  marker=$(ride_rpmfusion_marker)
  if [[ ! -e "$dir" ]]; then install -d -o root -g root -m 0700 -- "$dir" || return 1; fi
  [[ ! -e "$marker" && ! -L "$marker" ]] || return 1
  temp=$(mktemp "$dir/.rpmfusion.XXXXXXXX") || return 1
  if ! ride_rpmfusion_marker_content > "$temp" || ! chmod 0600 -- "$temp" ||
      ! chown root:root -- "$temp" || ! mv -T -- "$temp" "$marker"; then
    rm -f -- "$temp"
    return 1
  fi
}

ride_rpmfusion_remove_installed_release_packages() {
  local package
  local -a installed=()
  while IFS= read -r package; do
    if rpm -q --quiet "$package"; then installed+=("$package"); fi
  done < <(ride_rpmfusion_packages)
  ((${#installed[@]} == 0)) || dnf5 remove -y "${installed[@]}"
}

ride_rpmfusion_change() {
  local state=$1 current tempdir free_rpm nonfree_rpm repo_file verify_failed=0
  local -a repo_files=()
  [[ "$state" == configured || "$state" == absent ]] || ride_die "invalid RPM Fusion state"
  ride_rpmfusion_guard "$state"
  current=$(ride_rpmfusion_state) || ride_die "cannot inspect RPM Fusion state"
  [[ "$current" != "$state" ]] || return 0
  if [[ "$state" == configured ]]; then
    tempdir=$(mktemp -d /var/tmp/ride-rpmfusion.XXXXXXXX) || return 1
    if ! ride_rpmfusion_download_verify "$tempdir"; then rm -rf -- "$tempdir"; return 1; fi
    free_rpm="$tempdir/free.rpm"
    nonfree_rpm="$tempdir/nonfree.rpm"
    if ! dnf5 --setopt=localpkg_gpgcheck=0 install -y "$free_rpm" "$nonfree_rpm"; then
      ride_rpmfusion_remove_installed_release_packages || ride_error "partial RPM Fusion install rollback failed"
      rm -rf -- "$tempdir"
      return 1
    fi
    if ! ride_rpmfusion_owned_files_ok; then
      ride_rpmfusion_remove_installed_release_packages || ride_error "RPM Fusion rollback failed after verification error"
      rm -rf -- "$tempdir"
      ride_die "installed RPM Fusion repo files failed verification"
    fi
    mapfile -t repo_files < <(rpm -ql rpmfusion-free-release rpmfusion-nonfree-release | awk '/^\/etc\/yum\.repos\.d\/rpmfusion-.*\.repo$/')
    ((${#repo_files[@]} >= 2)) || verify_failed=1
    for repo_file in "${repo_files[@]}"; do
      [[ -f "$repo_file" && ! -L "$repo_file" ]] &&
        grep -Eq '^[[:space:]]*gpgcheck[[:space:]]*=[[:space:]]*1([[:space:]]|$)' "$repo_file" ||
        verify_failed=1
    done
    if ((verify_failed)); then
      ride_rpmfusion_remove_installed_release_packages || ride_error "RPM Fusion rollback failed after repo verification error"
      rm -rf -- "$tempdir"
      ride_die "RPM Fusion repository files failed signature enforcement verification"
    fi
    if ! ride_rpmfusion_write_marker; then
      ride_rpmfusion_remove_installed_release_packages || ride_error "RPM Fusion rollback failed after marker error"
      rm -rf -- "$tempdir"
      return 1
    fi
    if ! ride_rpmfusion_owned_files_ok || [[ "$(ride_rpmfusion_state)" != configured ]]; then
      rm -rf -- "$tempdir"
      ride_die "installed RPM Fusion state verification failed; owned marker retained for recovery"
    fi
    rm -rf -- "$tempdir"
    [[ "$(ride_rpmfusion_state)" == configured ]] || ride_die "RPM Fusion state verification failed"
  else
    dnf5 remove -y rpmfusion-free-release rpmfusion-nonfree-release || return 1
    rm -f -- "$(ride_rpmfusion_marker)"
  fi
}
