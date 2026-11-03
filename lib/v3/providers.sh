#!/usr/bin/env bash

ride_observe() {
  local entry=$1 handler name result
  handler=$(jq -r '.handler' <<< "$entry")
  case "$handler" in
    clamav-initial-signatures) ride_clamav_observe ;;
    dnf-package|smartmontools-package)
      ride_require_command rpm
      name=$(jq -r '.packageName' <<< "$entry")
      if rpm -q --quiet "$name"; then printf 'installed\n'; else printf 'absent\n'; fi
      ;;
    veracrypt-signed-rpm)
      ride_require_command rpm
      if rpm -q --quiet veracrypt; then printf 'installed\n'; else printf 'absent\n'; fi
      ;;
    pinned-rpm)
      ride_require_command rpm
      name=$(jq -r '.packageName' <<< "$entry")
      if rpm -q --quiet "$name"; then printf 'installed\n'; else printf 'absent\n'; fi
      ;;
    amp-pinned-rpm)
      ride_require_command rpm
      if rpm -q --quiet ampinstmgr; then printf 'installed\n'; else printf 'absent\n'; fi
      ;;
    publisher-repo-rpm)
      ride_require_command rpm
      name=$(jq -r '.packageName' <<< "$entry")
      if rpm -q --quiet "$name"; then printf 'installed\n'; else printf 'absent\n'; fi
      ;;
    systemd-service)
      ride_require_command systemctl
      name=$(jq -r '.serviceName' <<< "$entry")
      result=$(systemctl is-enabled "$name" 2>/dev/null) || true
      case "$result" in
        enabled|disabled) printf '%s\n' "$result" ;;
        *) ride_die "cannot identify enabled state for $name: ${result:-unknown}" ;;
      esac
      ;;
    plex-server-service) ride_plex_server_service_observe ;;
    glances-web-service) ride_glances_web_service_observe ;;
    sshd-root-login) ride_sshd_root_login_observe ;;
    ssh-reboot-sudoers) ride_ssh_reboot_observe "$entry" ;;
    keyfile-mounts) ride_keyfile_mounts_observe "$entry" ;;
    github-asset) printf 'not-applicable\n' ;;
    pinned-script) ride_observe_asn "$entry" ;;
    pinned-woeusb-script) ride_observe_woeusb "$entry" ;;
    pinned-zip) ride_observe_cyberchef "$entry" ;;
    networkminer-portable) ride_observe_networkminer "$entry" ;;
    pinned-binary) ride_observe_librespeed "$entry" ;;
    pinned-eza-binary) ride_observe_eza_portable "$entry" ;;
    pinned-appimage) ride_observe_bitwarden_appimage "$entry" ;;
    pinned-publisher-appimage) ride_observe_publisher_appimage "$entry" ;;
    pinned-email-header-spa) ride_observe_email_header_analyzer ;;
    pinned-yubico-tarball) ride_observe_yubico_authenticator "$entry" ;;
    pinned-volatility2-bundle) ride_observe_volatility2 "$entry" ;;
    pinned-deb-binary) ride_galleta_state observe ;;
    ferium-portable) ride_ferium_portable_state observe ;;
    minecraft-server-jar) ride_minecraft_server_state observe ;;
    python-venv)
      case "$(jq -r '.id' <<< "$entry")" in
        package.volatility3)
          local environment
          environment=$(ride_volatility_environment)
          if [[ -f "$environment/.ride-owned" && ! -L "$environment" &&
                -x "$environment/bin/python" ]] &&
             "$environment/bin/python" -c 'import importlib.metadata as m; assert m.version("volatility3") == "2.28.2"; assert m.version("pefile") == "2024.8.26"' >/dev/null 2>&1; then
            printf 'installed\n'
          else
            printf 'absent\n'
          fi
          ;;
        package.dfir-unfurl)
          ride_observe_unfurl
          ;;
        package.chepy)
          ride_observe_chepy "$entry"
          ;;
        *) ride_die "unknown isolated Python operation" ;;
      esac
      ;;
    rust-source-build) ride_observe_browser_forensic "$entry" ;;
    vmfs6-source-build) ride_observe_vmfs6_reader "$entry" ;;
    gsettings-boolean)
      local schema key value
      read -r schema key < <(ride_gsettings_target "$entry")
      value=$(ride_gsettings get "$schema" "$key") || ride_die "cannot observe GNOME setting: $schema $key"
      case "$value" in
        true) printf 'enabled\n' ;;
        false) printf 'disabled\n' ;;
        *) ride_die "unexpected GNOME setting value: $schema $key=$value" ;;
      esac
      ;;
    ibus-emoji-hotkey) ride_ibus_hotkey_observe ;;
    gnome-lock-timing) ride_gnome_lock_timing_observe "$entry" ;;
    user-directories) ride_user_default_directories_observe ;;
    firefox-preferences) ride_firefox_preferences_observe ;;
    firefox-extensions) ride_firefox_extensions_observe ;;
    chrome-preferences) ride_chrome_preferences_observe ;;
    gsettings-string) ride_gsettings_string_observe "$entry" ;;
    gnome-custom-shortcuts) ride_gnome_custom_shortcuts_observe "$entry" ;;
    bash-aliases) ride_bash_aliases_observe "$entry" ;;
    upower-threshold) ride_upower_observe "$entry" ;;
    dnf5-fast-tuning) ride_dnf5_fast_tuning_observe ;;
    system-hostname) ride_system_hostname_observe "$entry" ;;
    wireguard-keypair) ride_wireguard_observe ;;
    networkmanager-vpn-profiles) ride_vpn_profiles_observe "$entry" ;;
    expressvpn-wrapper) ride_expressvpn_observe ;;
    flatpak-remote) ride_flathub_remote_state ;;
    flatpak-app) ride_flatpak_app_state "$entry" ;;
    rpmfusion-repositories) ride_rpmfusion_state ;;
    dnf-package-set-update) ride_dnf5_package_set_update_observe "$entry" ;;
    dnf5-system-update) ride_dnf5_system_update_observe ;;
    docker-engine) ride_docker_engine_observe "$entry" ;;
    nsswitch-mdns) ride_nsswitch_mdns_observe ;;
    dnf5-automatic) ride_dnf5_automatic_observe ;;
    snap-store-package) ride_snap_store_package_observe "$entry" ;;
    pinned-snap-package) ride_bulk_extractor_observe "$entry" ;;
    *) ride_die "untrusted handler: $handler" ;;
  esac
}

ride_change() {
  local entry=$1 state=$2 handler name source_id
  handler=$(jq -r '.handler' <<< "$entry")
  case "$handler" in
    clamav-initial-signatures) ride_clamav_change "$entry" "$state" ;;
    dnf-package)
      [[ "$RIDE_OS_ID" == fedora ]] || ride_die "DNF handler requires Fedora"
      ride_require_command dnf
      name=$(jq -r '.packageName' <<< "$entry")
      source_id=$(jq -r '.sourceId // ""' <<< "$entry")
      case "$state" in
        installed)
          case "$source_id" in
            rpmfusion-free-updates)
              dnf --setopt=gpgcheck=1 --setopt=localpkg_gpgcheck=1 install -y \
                --from-repo="$source_id" "$name"
              ;;
            *) dnf --setopt=gpgcheck=1 --setopt=localpkg_gpgcheck=1 install -y "$name" ;;
          esac
          ;;
        absent) dnf remove -y "$name" ;;
        *) ride_die "invalid package state: $state" ;;
      esac
      ;;
    smartmontools-package)
      [[ "$RIDE_OS_ID" == fedora ]] || ride_die "smartmontools handler requires Fedora"
      [[ "$(jq -r '.id' <<< "$entry")" == package.smartmontools &&
         "$(jq -r '.packageName' <<< "$entry")" == smartmontools &&
         "$(jq -r '.serviceName' <<< "$entry")" == smartd.service ]] ||
        ride_die "invalid SmartMonTools operation identity"
      ride_require_command dnf
      ride_require_command systemctl
      case "$state" in
        installed)
          dnf --setopt=gpgcheck=1 --setopt=localpkg_gpgcheck=1 install -y smartmontools
          systemctl disable --now smartd.service || ride_die "could not leave smartd.service stopped and disabled"
          [[ "$(systemctl is-enabled smartd.service 2>/dev/null || true)" == disabled &&
             "$(systemctl is-active smartd.service 2>/dev/null || true)" == inactive ]] ||
            ride_die "smartd.service is not stopped and disabled after installation"
          ;;
        absent)
          local smartd_enabled smartd_active
          smartd_enabled=$(systemctl is-enabled smartd.service 2>/dev/null || true)
          smartd_active=$(systemctl is-active smartd.service 2>/dev/null || true)
          [[ "$smartd_enabled" != enabled && "$smartd_active" != active ]] ||
            ride_die "smartd.service was enabled or active outside RIDE; refusing package removal"
          dnf remove -y smartmontools
          ;;
        *) ride_die "invalid SmartMonTools package state: $state" ;;
      esac
      ;;
    veracrypt-signed-rpm)
      ride_change_veracrypt "$entry" "$state"
      ;;
    pinned-rpm)
      ride_change_pinned_rpm "$entry" "$state"
      ;;
    amp-pinned-rpm)
      ride_change_amp_pinned_rpm "$entry" "$state"
      ;;
    publisher-repo-rpm)
      ride_change_publisher_repo_rpm "$entry" "$state"
      ;;
    systemd-service)
      ride_require_command systemctl
      name=$(jq -r '.serviceName' <<< "$entry")
      case "$state" in
        enabled) systemctl enable "$name" ;;
        disabled) systemctl disable "$name" ;;
        *) ride_die "invalid service state: $state" ;;
      esac
      ;;
    plex-server-service) ride_plex_server_service_change "$state" ;;
    glances-web-service) ride_glances_web_service_change "$state" ;;
    sshd-root-login) ride_sshd_root_login_change "$state" ;;
    ssh-reboot-sudoers) ride_ssh_reboot_change "$entry" "$state" ;;
    keyfile-mounts) ride_keyfile_mounts_change "$entry" "$state" ;;
    python-venv)
      case "$(jq -r '.id' <<< "$entry")" in
        package.volatility3) ride_change_volatility "$state" ;;
        package.dfir-unfurl) ride_change_unfurl "$state" ;;
        package.chepy) ride_change_chepy "$entry" "$state" ;;
        *) ride_die "unknown isolated Python operation" ;;
      esac
      ;;
    rust-source-build)
      [[ "$(jq -r '.id' <<< "$entry")" == package.browser-forensic ]] || ride_die "unknown pinned Rust source build"
      ride_change_browser_forensic "$entry" "$state"
      ;;
    vmfs6-source-build)
      [[ "$(jq -r '.id' <<< "$entry")" == package.vmfs6-reader ]] || ride_die "unknown VMFS6 source build"
      ride_change_vmfs6_reader "$entry" "$state"
      ;;
    pinned-script)
      [[ "$(jq -r '.id' <<< "$entry")" == package.asn ]] || ride_die "unknown pinned script operation"
      ride_change_asn "$entry" "$state"
      ;;
    pinned-woeusb-script)
      [[ "$(jq -r '.id' <<< "$entry")" == package.woeusb ]] || ride_die "unknown pinned WoeUSB script operation"
      ride_change_woeusb "$entry" "$state"
      ;;
    pinned-zip)
      [[ "$(jq -r '.id' <<< "$entry")" == package.cyberchef ]] || ride_die "unknown pinned ZIP operation"
      ride_change_cyberchef "$entry" "$state"
      ;;
    networkminer-portable)
      [[ "$(jq -r '.id' <<< "$entry")" == package.networkminer ]] || ride_die "unknown NetworkMiner operation"
      ride_change_networkminer "$entry" "$state"
      ;;
    pinned-binary)
      [[ "$(jq -r '.id' <<< "$entry")" == package.librespeed-cli ]] || ride_die "unknown pinned binary operation"
      ride_change_librespeed "$entry" "$state"
      ;;
    pinned-eza-binary)
      [[ "$(jq -r '.id' <<< "$entry")" == package.eza-portable ]] || ride_die "unknown pinned Eza binary operation"
      ride_change_eza_portable "$entry" "$state"
      ;;
    pinned-appimage)
      [[ "$(jq -r '.id' <<< "$entry")" == package.bitwarden-appimage ]] || ride_die "unknown pinned AppImage operation"
      ride_change_bitwarden_appimage "$entry" "$state"
      ;;
    pinned-publisher-appimage)
      [[ "$(jq -r '.id' <<< "$entry")" == package.arduino-ide ||
         "$(jq -r '.id' <<< "$entry")" == package.joplin ]] || ride_die "unknown pinned publisher AppImage operation"
      ride_change_publisher_appimage "$entry" "$state"
      ;;
    pinned-email-header-spa)
      [[ "$(jq -r '.id' <<< "$entry")" == package.email-header-analyzer ]] || ride_die "unknown pinned email header analyzer operation"
      ride_change_email_header_analyzer "$entry" "$state"
      ;;
    pinned-yubico-tarball)
      [[ "$(jq -r '.id' <<< "$entry")" == package.yubico-authenticator ]] || ride_die "unknown pinned Yubico archive operation"
      ride_change_yubico_authenticator "$entry" "$state"
      ;;
    pinned-volatility2-bundle)
      [[ "$(jq -r '.id' <<< "$entry")" == package.volatility2 ]] || ride_die "unknown pinned Volatility 2 bundle operation"
      ride_change_volatility2 "$entry" "$state"
      ;;
    pinned-deb-binary)
      [[ "$(jq -r '.id' <<< "$entry")" == package.galleta ]] || ride_die "unknown pinned Debian binary operation"
      case "$state" in
        installed|absent) ride_galleta_state "$state" ;;
        *) ride_die "invalid Galleta desired state: $state" ;;
      esac
      ;;
    ferium-portable)
      ride_ferium_portable_state "$state"
      ;;
    minecraft-server-jar)
      [[ "$(jq -r '.id' <<< "$entry")" == package.minecraft-server ]] || ride_die "unknown Minecraft server JAR operation"
      ride_minecraft_server_state "$state"
      ;;
    gsettings-boolean)
      local schema key value writable
      read -r schema key < <(ride_gsettings_target "$entry")
      case "$state" in
        enabled) value=true ;;
        disabled) value=false ;;
        *) ride_die "invalid GNOME boolean state: $state" ;;
      esac
      writable=$(ride_gsettings writable "$schema" "$key") || ride_die "cannot check GNOME setting writability: $schema $key"
      [[ "$writable" == true ]] || ride_die "GNOME setting is locked: $schema $key"
      ride_gsettings set "$schema" "$key" "$value"
      ;;
    ibus-emoji-hotkey) ride_ibus_hotkey_change "$state" ;;
    gnome-lock-timing) ride_gnome_lock_timing_change "$entry" "$state" ;;
    user-directories) ride_user_default_directories_change "$state" ;;
    firefox-preferences) ride_firefox_preferences_change "$state" ;;
    firefox-extensions) ride_firefox_extensions_change "$state" ;;
    chrome-preferences) ride_chrome_preferences_change "$entry" "$state" ;;
    gsettings-string) ride_gsettings_string_change "$entry" "$state" ;;
    gnome-custom-shortcuts) ride_gnome_custom_shortcuts_change "$entry" "$state" ;;
    bash-aliases) ride_bash_aliases_change "$entry" "$state" ;;
    upower-threshold) ride_upower_change "$entry" "$state" ;;
    dnf5-fast-tuning) ride_dnf5_fast_tuning_change "$state" ;;
    system-hostname) ride_system_hostname_change "$entry" "$state" ;;
    wireguard-keypair) ride_wireguard_change "$state" ;;
    networkmanager-vpn-profiles) ride_vpn_profiles_change "$entry" "$state" ;;
    expressvpn-wrapper)
      [[ "$(jq -r '.id' <<< "$entry")" == package.expressvpn ]] || ride_die "unknown ExpressVPN wrapper operation"
      ride_expressvpn_change "$entry" "$state"
      ;;
    flatpak-remote) ride_flathub_change "$state" ;;
    flatpak-app) ride_flatpak_app_change "$entry" "$state" ;;
    rpmfusion-repositories) ride_rpmfusion_change "$state" ;;
    dnf-package-set-update) ride_dnf5_package_set_update_change "$entry" "$state" ;;
    dnf5-system-update) ride_dnf5_system_update_change "$state" ;;
    docker-engine) ride_docker_engine_change "$entry" "$state" ;;
    nsswitch-mdns) ride_nsswitch_mdns_change "$state" ;;
    dnf5-automatic) ride_dnf5_automatic_change "$state" ;;
    snap-store-package) ride_snap_store_package_change "$entry" "$state" ;;
    pinned-snap-package) ride_bulk_extractor_change "$entry" "$state" ;;
    *) ride_die "untrusted handler: $handler" ;;
  esac
}

ride_snap_store_package_observe() {
  local entry=$1 package listing
  [[ "$(jq -r '.id' <<< "$entry")" == package.autopsy ]] || ride_die "unknown Snap Store package operation"
  ride_require_command snap
  package=$(jq -r '.packageName' <<< "$entry")
  listing=$(snap list 2>/dev/null) || ride_die "cannot query Snap Store package state"
  if awk -v package="$package" 'NR > 1 && $1 == package {found=1} END {exit !found}' <<< "$listing"; then
    printf 'installed\n'
  else
    printf 'absent\n'
  fi
}

ride_snap_store_package_change() {
  local entry=$1 state=$2 package channel
  [[ "$(jq -r '.id' <<< "$entry")" == package.autopsy ]] || ride_die "unknown Snap Store package operation"
  ride_require_command snap
  package=$(jq -r '.packageName' <<< "$entry")
  channel=$(jq -r '.snapChannel' <<< "$entry")
  case "$state" in
    installed)
      if [[ "$(ride_snap_store_package_observe "$entry")" == installed ]]; then return 0; fi
      snap install "$package" --channel="$channel"
      ;;
    absent)
      if [[ "$(ride_snap_store_package_observe "$entry")" == absent ]]; then return 0; fi
      # Keep Snap's application data and its automatic snapshot on removal.
      snap remove "$package"
      ;;
    *) ride_die "invalid Snap Store package state: $state" ;;
  esac
}

ride_bulk_extractor_observe() {
  local entry=$1 package expected listing version
  [[ "$(jq -r '.id' <<< "$entry")" == package.bulk-extractor ]] ||
    ride_die "unknown pinned Snap package operation"
  ride_require_command snap
  package=$(jq -r '.packageName' <<< "$entry")
  expected=$(jq -r '.releaseVersion' <<< "$entry")
  listing=$(snap list 2>/dev/null) || ride_die "cannot query Snap package state"
  version=$(awk -v package="$package" 'NR > 1 && $1 == package { print $2 }' <<< "$listing")
  [[ -n "$version" ]] || { printf 'absent\n'; return 0; }
  [[ "$version" == "$expected" ]] ||
    ride_die "$package is installed at version ${version:-unknown}; expected pinned version $expected"
  printf 'installed\n'
}

ride_bulk_extractor_install() (
  local entry=$1 package url expected temporary actual
  [[ "$(jq -r '.id' <<< "$entry")" == package.bulk-extractor ]] ||
    ride_die "unknown pinned Snap package operation"
  [[ "$RIDE_OS_ID" == fedora ]] || ride_die "BulkExtractor Snap requires Fedora"
  ride_require_command snap
  ride_require_command curl
  ride_require_command sha256sum
  package=$(jq -r '.packageName' <<< "$entry")
  url=$(jq -r '.snapArchiveUri' <<< "$entry")
  expected=$(jq -r '.sha256' <<< "$entry")
  temporary=$(mktemp -d "${TMPDIR:-/tmp}/ride-bulk-extractor.XXXXXXXX") ||
    ride_die "cannot create temporary BulkExtractor download directory"
  trap 'rm -rf -- "$temporary"' EXIT
  curl --fail --location --silent --show-error --proto '=https' --tlsv1.2 \
    --output "$temporary/$package.snap" "$url" || ride_die "BulkExtractor download failed"
  actual=$(sha256sum "$temporary/$package.snap" | awk '{print $1}')
  [[ "$actual" == "$expected" ]] || ride_die "BulkExtractor Snap SHA-256 mismatch"
  snap install --dangerous "$temporary/$package.snap" || ride_die "BulkExtractor Snap installation failed"
)

ride_bulk_extractor_change() {
  local entry=$1 state=$2 package current_state
  [[ "$(jq -r '.id' <<< "$entry")" == package.bulk-extractor ]] ||
    ride_die "unknown pinned Snap package operation"
  [[ "$RIDE_OS_ID" == fedora ]] || ride_die "BulkExtractor Snap requires Fedora"
  ride_require_command snap
  package=$(jq -r '.packageName' <<< "$entry")
  case "$state" in
    installed)
      current_state=$(ride_bulk_extractor_observe "$entry") || return $?
      if [[ "$current_state" == installed ]]; then return 0; fi
      ride_bulk_extractor_install "$entry"
      current_state=$(ride_bulk_extractor_observe "$entry") || return $?
      [[ "$current_state" == installed ]] ||
        ride_die "BulkExtractor did not reach its pinned installed state"
      ;;
    absent)
      current_state=$(ride_bulk_extractor_observe "$entry") || return $?
      if [[ "$current_state" == absent ]]; then return 0; fi
      # Keep Snap's automatic data snapshot; never use --purge.
      snap remove "$package"
      ;;
    *) ride_die "invalid BulkExtractor state: $state" ;;
  esac
}

ride_change_veracrypt() {
  local entry=$1 state=$2 temporary expected package_url signature_url key_url
  local fingerprint_output package_name
  [[ "$RIDE_OS_ID" == fedora ]] || ride_die "VeraCrypt publisher RPM requires Fedora"
  ride_require_command rpm
  case "$state" in
    installed)
      if rpm -q --quiet veracrypt; then return 0; fi
      ride_require_command dnf
      ride_require_command curl
      ride_require_command gpg
      package_name=$(jq -r '.packageName' <<< "$entry")
      expected=$(jq -r '.signingFingerprint' <<< "$entry")
      package_url=$(jq -r '.sourceUri' <<< "$entry")
      signature_url=$(jq -r '.signatureUri' <<< "$entry")
      key_url=$(jq -r '.signingKeyUri' <<< "$entry")
      temporary=$(mktemp -d "${TMPDIR:-/tmp}/ride-veracrypt.XXXXXXXX") || return 1
      if ! mkdir -m 0700 "$temporary/gnupg" ||
         ! curl --fail --location --silent --show-error "$package_url" -o "$temporary/package.rpm" ||
         ! curl --fail --location --silent --show-error "$signature_url" -o "$temporary/package.rpm.sig" ||
         ! curl --fail --location --silent --show-error "$key_url" -o "$temporary/publisher-key.asc"; then
        rm -rf -- "$temporary"
        ride_die "could not acquire VeraCrypt RPM, signature, or publisher key"
      fi
      if ! gpg --batch --homedir "$temporary/gnupg" --import "$temporary/publisher-key.asc" >/dev/null 2>&1; then
        rm -rf -- "$temporary"
        ride_die "could not import the VeraCrypt key into the temporary verification keyring"
      fi
      fingerprint_output=$(gpg --batch --homedir "$temporary/gnupg" --with-colons --fingerprint 2>/dev/null || true)
      if ! awk -F: '$1 == "fpr" {print $10}' <<< "$fingerprint_output" | grep -Fxq "$expected"; then
        rm -rf -- "$temporary"
        ride_die "VeraCrypt publisher key fingerprint did not match the pinned fingerprint"
      fi
      if ! gpg --batch --homedir "$temporary/gnupg" --verify "$temporary/package.rpm.sig" "$temporary/package.rpm" >/dev/null 2>&1; then
        rm -rf -- "$temporary"
        ride_die "VeraCrypt RPM detached signature verification failed"
      fi
      if ! rpm -qp --qf '%{NAME}\n' "$temporary/package.rpm" | grep -Fxq "$package_name"; then
        rm -rf -- "$temporary"
        ride_die "verified VeraCrypt artifact has an unexpected RPM package name"
      fi
      if dnf --setopt=localpkg_gpgcheck=0 install -y "$temporary/package.rpm"; then
        rm -rf -- "$temporary"
      else
        local result=$?
        rm -rf -- "$temporary"
        return "$result"
      fi
      ;;
    absent)
      if ! rpm -q --quiet veracrypt; then return 0; fi
      ride_require_command dnf
      ride_require_command veracrypt
      local mounted_output mounted_status=0
      mounted_output=$(veracrypt -t --list 2>&1) || mounted_status=$?
      # VeraCrypt reports the empty mount list as a diagnostic and returns 1.
      # Accept only that exact response; other nonzero output remains unknown.
      if [[ "$mounted_output" == "Error: No volumes mounted." ]]; then
        :
      elif [[ "$mounted_status" == 0 && "$mounted_output" =~ ^[[:space:]]*[0-9]+: ]]; then
        ride_die "VeraCrypt has mounted volumes; unmount them before removing the application"
      else
        ride_die "cannot determine VeraCrypt mount state safely: $mounted_output"
      fi
      dnf remove -y veracrypt
      ;;
    *) ride_die "invalid VeraCrypt package state: $state" ;;
  esac
}

ride_publisher_repo_file() {
  local entry=$1
  printf '/etc/yum.repos.d/%s\n' "$(jq -r '.repositoryFile' <<< "$entry")"
}

ride_publisher_repo_owner_file() {
  local entry=$1
  printf '/var/lib/ride-fedora/owned-repositories/%s.sha256\n' "$(jq -r '.repositoryId' <<< "$entry")"
}

ride_publisher_repo_content() {
  local entry=$1 repository_id base_url key_uri product
  repository_id=$(jq -r '.repositoryId' <<< "$entry")
  base_url=$(jq -r '.repositoryBaseUrl' <<< "$entry")
  key_uri=$(jq -r '.repositoryKeyUri' <<< "$entry")
  product=$(jq -r '.id' <<< "$entry")
  case "$product" in
    package.visual-studio-code)
      printf '[%s]\nname=Microsoft Visual Studio Code (RIDE)\nbaseurl=%s\nenabled=1\nautorefresh=1\ntype=rpm-md\ngpgcheck=1\nrepo_gpgcheck=0\ngpgkey=%s\n' \
        "$repository_id" "$base_url" "$key_uri"
      ;;
    package.brave)
      printf '[%s]\nname=Brave Browser (RIDE)\nbaseurl=%s\nenabled=1\ngpgcheck=1\ngpgkey=%s\n' \
        "$repository_id" "$base_url" "$key_uri"
      ;;
    package.plaso)
      printf '[%s]\nname=GIFT stable COPR for Plaso (RIDE)\nbaseurl=%s\nenabled=1\ntype=rpm-md\nskip_if_unavailable=True\ngpgcheck=1\ngpgkey=%s\nrepo_gpgcheck=0\n' \
        "$repository_id" "$base_url" "$key_uri"
      ;;
    package.tailscale)
      printf '[%s]\nname=Tailscale stable (RIDE)\nbaseurl=%s\nenabled=1\ntype=rpm\nrepo_gpgcheck=1\ngpgcheck=1\ngpgkey=%s\n' \
        "$repository_id" "$base_url" "$key_uri"
      ;;
    package.plex-server)
      printf '[%s]\nname=Plex Media Server (RIDE)\nbaseurl=%s\nenabled=1\ntype=rpm\nrepo_gpgcheck=1\ngpgcheck=1\ngpgkey=%s\n' \
        "$repository_id" "$base_url" "$key_uri"
      ;;
    *) ride_die "unknown publisher RPM operation" ;;
  esac
}

ride_publisher_repo_verify_key() {
  local entry=$1 temporary key_uri expected output
  ride_require_command curl
  ride_require_command gpg
  key_uri=$(jq -r '.repositoryKeyUri' <<< "$entry")
  expected=$(jq -r '.repositoryKeyFingerprint // ""' <<< "$entry")
  temporary=$(mktemp -d "${TMPDIR:-/tmp}/ride-publisher-key.XXXXXXXX") || return 1
  mkdir -m 0700 "$temporary/gnupg" || { rm -rf -- "$temporary"; return 1; }
  if ! curl --fail --location --silent --show-error "$key_uri" -o "$temporary/key.asc" ||
     ! gpg --batch --homedir "$temporary/gnupg" --import "$temporary/key.asc" >/dev/null 2>&1; then
    rm -rf -- "$temporary"
    ride_die "could not fetch or parse publisher signing key"
  fi
  output=$(gpg --batch --homedir "$temporary/gnupg" --with-colons --fingerprint 2>/dev/null || true)
  if [[ -n "$expected" ]]; then
    if ! awk -F: '$1 == "fpr" {print $10}' <<< "$output" | grep -Fxq "$expected"; then
      rm -rf -- "$temporary"
      ride_die "publisher signing-key fingerprint did not match the pinned fingerprint"
    fi
  elif ! awk -F: '$1 == "fpr" {found=1} END {exit !found}' <<< "$output"; then
    rm -rf -- "$temporary"
    ride_die "publisher signing key contained no primary fingerprint"
  fi
  rm -rf -- "$temporary"
}

ride_publisher_repo_install_file() {
  local entry=$1 file owner expected actual temporary directory repository_id
  file=$(ride_publisher_repo_file "$entry")
  owner=$(ride_publisher_repo_owner_file "$entry")
  repository_id=$(jq -r '.repositoryId' <<< "$entry")
  expected=$(ride_publisher_repo_content "$entry")
  directory=$(dirname -- "$file")
  if [[ -e "$file" || -L "$file" ]]; then
    [[ -f "$file" && ! -L "$file" ]] || ride_die "publisher repository path is not a regular file: $file"
    [[ "$(cat -- "$file")" == "$expected" ]] || ride_die "publisher repository file conflicts with existing content: $file"
    return 1
  fi
  install -d -m 0755 "$directory" "$(dirname -- "$owner")"
  temporary=$(mktemp "$directory/.${repository_id}.XXXXXXXX") || return 1
  if ! printf '%s' "$expected" > "$temporary" || ! chmod 0644 "$temporary" || ! mv -f -- "$temporary" "$file"; then
    rm -f -- "$temporary"
    return 1
  fi
  printf '%s\n' "$(sha256sum -- "$file" | cut -d' ' -f1)" > "$owner"
  printf 'created\n'
}

ride_publisher_repo_remove_file() {
  local entry=$1 file owner expected recorded actual
  file=$(ride_publisher_repo_file "$entry")
  owner=$(ride_publisher_repo_owner_file "$entry")
  [[ -f "$owner" && ! -L "$owner" ]] || return 0
  [[ -f "$file" && ! -L "$file" ]] || ride_die "owned publisher repository file is missing or unsafe: $file"
  expected=$(ride_publisher_repo_content "$entry")
  recorded=$(cat -- "$owner")
  actual=$(sha256sum -- "$file" | cut -d' ' -f1)
  [[ "$actual" == "$recorded" && "$(cat -- "$file")" == "$expected" ]] ||
    ride_die "owned publisher repository file changed; preserving it: $file"
  rm -f -- "$file" "$owner"
}

ride_change_publisher_repo_rpm() {
  local entry=$1 state=$2 name repository_id file_created
  [[ "$RIDE_OS_ID" == fedora ]] || ride_die "publisher RPM handler requires Fedora"
  ride_require_command rpm
  name=$(jq -r '.packageName' <<< "$entry")
  repository_id=$(jq -r '.repositoryId' <<< "$entry")
  case "$state" in
    installed)
      if rpm -q --quiet "$name"; then return 0; fi
      ride_require_command dnf
      ride_publisher_repo_verify_key "$entry"
      if file_created=$(ride_publisher_repo_install_file "$entry"); then
        file_created=1
      else
        local status=$?
        [[ "$status" == 1 ]] && file_created=0 || return "$status"
      fi
      if dnf --setopt="${repository_id}.gpgcheck=1" --setopt=localpkg_gpgcheck=1 \
           install -y --from-repo="$repository_id" "$name"; then
        :
      else
        local result=$?
        if [[ "$file_created" == 1 ]] && ! rpm -q --quiet "$name"; then
          ride_publisher_repo_remove_file "$entry" || true
        fi
        return "$result"
      fi
      ;;
    absent)
      if rpm -q --quiet "$name"; then
        ride_require_command dnf
        dnf remove -y "$name"
      fi
      ride_publisher_repo_remove_file "$entry"
      ;;
    *) ride_die "invalid publisher RPM state: $state" ;;
  esac
}

ride_plex_server_unit() { printf '/usr/lib/systemd/system/plexmediaserver.service\n'; }

ride_plex_server_service_observe() {
  local unit fragment enabled active
  unit=$(ride_plex_server_unit)
  fragment=$(systemctl show --property=FragmentPath --value plexmediaserver.service 2>/dev/null || true)
  if [[ -z "$fragment" || "$fragment" == /dev/null ]]; then
    printf 'disabled\n'
    return 0
  fi
  [[ "$fragment" == "$unit" ]] || ride_die "refusing an unowned Plex service unit: $fragment"
  [[ "$(rpm -qf --qf '%{NAME}' "$unit" 2>/dev/null || true)" == plexmediaserver ]] ||
    ride_die 'Plex service unit is not owned by the plexmediaserver RPM'
  enabled=$(systemctl is-enabled plexmediaserver.service 2>/dev/null || true)
  active=$(systemctl is-active plexmediaserver.service 2>/dev/null || true)
  if [[ "$enabled" == enabled && "$active" == active ]]; then
    printf 'enabled\n'
  elif [[ "$enabled" == disabled && "$active" != active ]]; then
    printf 'disabled\n'
  else
    ride_die "Plex service has mixed enabled/active state: ${enabled:-unknown}/${active:-unknown}"
  fi
}

ride_plex_server_service_change() {
  local state=$1 observed
  observed=$(ride_plex_server_service_observe)
  case "$state" in
    enabled)
      [[ "$observed" == enabled ]] && return 0
      [[ "$observed" == disabled ]] || ride_die 'Plex service is not in a managed disabled state'
      systemctl enable --now plexmediaserver.service || ride_die 'could not enable and start Plex Media Server'
      ;;
    disabled)
      [[ "$observed" == disabled ]] && return 0
      [[ "$observed" == enabled ]] || ride_die 'Plex service is not in a managed enabled state'
      systemctl disable --now plexmediaserver.service || ride_die 'could not stop and disable Plex Media Server'
      ;;
    *) ride_die "invalid Plex service state: $state" ;;
  esac
  observed=$(ride_plex_server_service_observe)
  [[ "$observed" == "$state" ]] || ride_die "Plex service did not reach $state state"
}

ride_change_pinned_rpm() {
  local entry=$1 state=$2 name version architecture url expected temporary metadata
  case "$(jq -r '.id' <<< "$entry")" in
    package.bitwarden-rpm|package.powershell|package.balena-etcher|package.discord) ;;
    *) ride_die "unknown pinned RPM operation" ;;
  esac
  [[ "$RIDE_OS_ID" == fedora ]] || ride_die "pinned RPM handler requires Fedora"
  name=$(jq -r '.packageName' <<< "$entry")
  version=$(jq -r '.version' <<< "$entry")
  architecture=$(jq -r '.targets.fedora.architectures[0]' <<< "$entry")
  url=$(jq -r '.sourceUri' <<< "$entry")
  expected=$(jq -r '.sourceSha256' <<< "$entry")
  case "$state" in
    installed)
      ride_require_command rpm
      if rpm -q --quiet "$name"; then return 0; fi
      ride_require_command curl
      ride_require_command sha256sum
      ride_require_command dnf
      temporary=$(mktemp "${TMPDIR:-/tmp}/ride-pinned-rpm.XXXXXXXX.rpm") || return 1
      if ! curl --fail --location --silent --show-error --connect-timeout 20 --max-time 300 --max-filesize 200000000 \
          --output "$temporary" "$url"; then
        rm -f -- "$temporary"
        ride_die "failed to download pinned publisher RPM"
      fi
      if ! printf '%s  %s\n' "$expected" "$temporary" | sha256sum --check --status; then
        rm -f -- "$temporary"
        ride_die "pinned publisher RPM SHA-256 mismatch"
      fi
      metadata=$(rpm -qp --queryformat '%{NAME} %{VERSION} %{ARCH}' "$temporary") || {
        rm -f -- "$temporary"
        ride_die "downloaded Bitwarden RPM metadata is invalid"
      }
      if [[ "$metadata" != "$name $version $architecture" ]]; then
        rm -f -- "$temporary"
        ride_die "downloaded Bitwarden RPM identity does not match catalog"
      fi
      if dnf --setopt=localpkg_gpgcheck=0 install -y "$temporary"; then
        rm -f -- "$temporary"
      else
        local result=$?
        rm -f -- "$temporary"
        return "$result"
      fi
      ;;
    absent)
      if rpm -q --quiet "$name"; then
        ride_require_command dnf
        dnf remove -y "$name"
      fi
      ;;
    *) ride_die "invalid pinned RPM state: $state" ;;
  esac
}

ride_amp_preflight_new_install() {
  local path
  for path in /opt/cubecoders /etc/ampinstmgr.conf \
    /etc/systemd/system/ampinstmgr.service \
    /etc/systemd/system/ampfirewall.service \
    /etc/systemd/system/ampfirewall.timer \
    /etc/systemd/system/amptasks.service \
    /etc/systemd/system/amptasks.timer; do
    [[ ! -e "$path" && ! -L "$path" ]] ||
      ride_die "AMP install path already exists; preserving unowned state: $path"
  done
}

ride_amp_services_are_quiet() {
  local unit
  for unit in ampinstmgr.service ampfirewall.service ampfirewall.timer amptasks.service amptasks.timer; do
    if systemctl is-enabled --quiet "$unit" 2>/dev/null || systemctl is-active --quiet "$unit" 2>/dev/null; then
      ride_die "AMP unit is active or enabled; refusing package removal: $unit"
    fi
  done
}

ride_change_amp_pinned_rpm() {
  local entry=$1 state=$2 name version architecture url expected temporary metadata
  [[ "$(jq -r '.id' <<< "$entry")" == package.amp-installer ]] ||
    ride_die "unknown AMP RPM operation"
  [[ "$RIDE_OS_ID" == fedora ]] || ride_die "AMP RPM handler requires Fedora"
  ride_require_command rpm
  name=$(jq -r '.packageName' <<< "$entry")
  version=$(jq -r '.version' <<< "$entry")
  architecture=$(jq -r '.targets.fedora.architectures[0]' <<< "$entry")
  url=$(jq -r '.sourceUri' <<< "$entry")
  expected=$(jq -r '.sourceSha256' <<< "$entry")
  case "$state" in
    installed)
      if rpm -q --quiet "$name"; then return 0; fi
      ride_amp_preflight_new_install
      ride_require_command curl
      ride_require_command sha256sum
      ride_require_command dnf
      ride_require_command systemctl
      temporary=$(mktemp "${TMPDIR:-/tmp}/ride-amp-rpm.XXXXXXXX.rpm") || return 1
      if ! curl --fail --location --silent --show-error --connect-timeout 20 --max-time 300 --max-filesize 200000000 \
          --output "$temporary" "$url"; then
        rm -f -- "$temporary"
        ride_die "failed to download pinned CubeCoders RPM"
      fi
      if ! printf '%s  %s\n' "$expected" "$temporary" | sha256sum --check --status; then
        rm -f -- "$temporary"
        ride_die "pinned CubeCoders RPM SHA-256 mismatch"
      fi
      metadata=$(rpm -qp --queryformat '%{NAME} %{VERSION}-%{RELEASE} %{ARCH}' "$temporary") || {
        rm -f -- "$temporary"
        ride_die "downloaded CubeCoders RPM metadata is invalid"
      }
      if [[ "$metadata" != "$name $version $architecture" ]]; then
        rm -f -- "$temporary"
        ride_die "downloaded CubeCoders RPM identity does not match catalog"
      fi
      if dnf --setopt=localpkg_gpgcheck=0 --setopt=tsflags=noscripts install -y "$temporary"; then
        rm -f -- "$temporary"
        systemctl daemon-reload || ride_die "could not reload systemd after AMP package install"
      else
        local result=$?
        rm -f -- "$temporary"
        return "$result"
      fi
      ;;
    absent)
      if rpm -q --quiet "$name"; then
        ride_require_command dnf
        ride_require_command systemctl
        ride_amp_services_are_quiet
        dnf --setopt=tsflags=noscripts remove -y "$name" || return
        systemctl daemon-reload || ride_die "could not reload systemd after AMP package removal"
      fi
      ;;
    *) ride_die "invalid AMP package state: $state" ;;
  esac
}

ride_dnf5_package_set_installed_names() {
  local entry=$1 package
  while IFS= read -r package; do
    [[ -n "$package" ]] || continue
    if rpm -q --quiet "$package"; then printf '%s\n' "$package"; fi
  done < <(jq -r '.packageNames[]' <<< "$entry")
}

ride_dnf5_package_set_update_observe() {
  local entry=$1 refresh=${2:-} installed output status has_updates
  local -a packages=()
  ride_require_command rpm
  ride_require_command dnf5
  installed=$(ride_dnf5_package_set_installed_names "$entry")
  [[ -n "$installed" ]] || { printf 'no-packages\n'; return; }
  mapfile -t packages <<< "$installed"
  if [[ "$refresh" == refresh ]]; then
    if output=$(dnf5 --refresh check-upgrade --json "${packages[@]}" 2>&1); then
      status=0
    else
      status=$?
    fi
  elif output=$(dnf5 check-upgrade --json "${packages[@]}" 2>&1); then
    status=0
  else
    status=$?
  fi
  [[ "$status" == 0 || "$status" == 100 ]] || ride_die "DNF5 update check failed: $output"
  jq -e 'type == "object" and all(.[]; type == "array")' <<< "$output" >/dev/null ||
    ride_die "DNF5 update check returned invalid JSON: $output"
  has_updates=$(jq -r '[.[] | .[]] | length > 0' <<< "$output")
  if [[ "$has_updates" == true ]]; then
    printf 'outdated\n'
  elif [[ "$status" == 0 && "$has_updates" == false ]]; then
    printf 'current\n'
  else
    ride_die "DNF5 update check exit status disagrees with its JSON result"
  fi
}

ride_dnf5_package_set_update_preview() {
  local entry=$1 installed output status
  local -a packages=()
  installed=$(ride_dnf5_package_set_installed_names "$entry")
  [[ -n "$installed" ]] || ride_die "no declared Multimedia packages are installed"
  mapfile -t packages <<< "$installed"
  if output=$(LC_ALL=C dnf5 upgrade --assumeno --no-allow-downgrade "${packages[@]}" 2>&1); then
    status=0
  else
    status=$?
  fi
  if grep -Eq '^[[:space:]]*(Removing|Downgrading)([[:space:]]+[^:]*)?:' <<< "$output"; then
    ride_die "DNF5 update preview would remove or downgrade packages; inspect the transaction before retrying"
  fi
  if [[ "$status" != 0 ]] && ! grep -Fq 'Operation aborted' <<< "$output"; then
    ride_die "DNF5 update preview failed: $output"
  fi
  printf 'DNF5 transaction preview for %s:\n%s\n' "$(jq -r '.id' <<< "$entry")" "$output"
}

ride_dnf5_package_set_update_change() {
  local entry=$1 state=$2 installed
  local -a packages=()
  [[ "$state" == current ]] || ride_die "invalid DNF5 package update state: $state"
  installed=$(ride_dnf5_package_set_installed_names "$entry")
  [[ -n "$installed" ]] || ride_die "no declared Multimedia packages are installed"
  mapfile -t packages <<< "$installed"
  dnf5 upgrade --no-allow-downgrade --assumeyes "${packages[@]}"
}

ride_dnf5_system_update_check() {
  local refresh=${1:-} output status count
  ride_require_command dnf5
  if [[ "$refresh" == refresh ]]; then
    if output=$(dnf5 --refresh check-upgrade --json 2>&1); then status=0; else status=$?; fi
  else
    if output=$(dnf5 check-upgrade --json 2>&1); then status=0; else status=$?; fi
  fi
  [[ "$status" == 0 || "$status" == 100 ]] || ride_die "DNF5 system update check failed: $output"
  jq -e 'type == "object" and all(.[]; type == "array")' <<< "$output" >/dev/null ||
    ride_die "DNF5 system update check returned invalid JSON: $output"
  count=$(jq -r '[.[] | .[]] | length' <<< "$output")
  [[ "$count" =~ ^[0-9]+$ ]] || ride_die 'DNF5 system update check returned an invalid package count'
  if (( count > 0 )); then printf 'outdated\n';
  elif [[ "$status" == 0 ]]; then printf 'current\n';
  else ride_die 'DNF5 system update check exit status disagrees with its JSON result'; fi
}

ride_dnf5_system_update_observe() {
  ride_dnf5_system_update_check
}

ride_dnf5_system_update_preview() {
  local output status
  if output=$(LC_ALL=C dnf5 upgrade --assumeno --no-allow-downgrade 2>&1); then status=0; else status=$?; fi
  if grep -Eiq '^[[:space:]]*(Removing|Downgrading|Obsoleting)([[:space:]]+[^:]*)?:' <<< "$output"; then
    ride_die "DNF5 system update preview includes removal, downgrade, or obsoletion; inspect repository state before proceeding"
  fi
  if [[ "$status" != 0 ]] && ! grep -Fq 'Operation aborted' <<< "$output"; then
    ride_die "DNF5 system update preview failed: $output"
  fi
  printf 'DNF5 whole-system update preview:\n%s\n' "$output"
}

ride_dnf5_system_update_history() {
  local output
  output=$(dnf5 history list --json) || ride_die 'cannot read DNF5 transaction history'
  jq -ce 'type == "array" and all(.[]; (.id | type == "number") and (.status | type == "string"))' <<< "$output" >/dev/null ||
    ride_die "DNF5 transaction history returned invalid JSON: $output"
  printf '%s\n' "$output"
}

ride_dnf5_system_update_latest_id() {
  local history=$1
  jq -r 'if length == 0 then 0 else .[0].id end' <<< "$history"
}

ride_dnf5_system_update_reboot_assessment() {
  local output status
  if ! command -v dnf5 >/dev/null 2>&1; then printf '{"assessment":"unavailable"}\n'; return; fi
  if output=$(dnf5 needs-restarting --json 2>&1); then status=0; else status=$?; fi
  if [[ "$status" != 0 && "$status" != 1 ]] ||
     ! jq -e 'type == "array" and length == 1 and .[0].type == "reboot" and (.[0].reboot_required | type == "boolean") and (.[0].packages | type == "array")' <<< "$output" >/dev/null 2>&1; then
    jq -nc --arg detail "${output:0:1000}" '{assessment:"unavailable", detail:$detail}'
    return
  fi
  jq -c '.[0] | {assessment:"available", rebootRequired:.reboot_required, packages}' <<< "$output"
}

RIDE_DNF5_SYSTEM_UPDATE_REPORT=
ride_dnf5_system_update_change() {
  local state=$1 before_history after_history before_id after_id info status reboot report
  [[ "$state" == current ]] || ride_die 'invalid DNF5 system update state'
  ride_require_command dnf5
  before_history=$(ride_dnf5_system_update_history) || return 1
  before_id=$(ride_dnf5_system_update_latest_id "$before_history") || return 1
  if dnf5 upgrade --no-allow-downgrade --assumeyes; then status=success; else status=failed; fi
  after_history=$(ride_dnf5_system_update_history) || after_history='[]'
  after_id=$(ride_dnf5_system_update_latest_id "$after_history" 2>/dev/null) || after_id=0
  info='[]'
  if (( after_id > before_id )); then
    info=$(dnf5 history info "$after_id" --json 2>/dev/null) || info='[]'
    jq -e 'type == "array" and length == 1 and (.[0].packages | type == "array")' <<< "$info" >/dev/null 2>&1 || info='[]'
  else
    after_id=0
  fi
  reboot=$(ride_dnf5_system_update_reboot_assessment)
  report=$(jq -cn --arg status "$status" --argjson transactionId "$after_id" \
    --argjson reboot "$reboot" \
    'input as $historyInfo | {status:$status, transactionId:$transactionId,
      transactionStatus:(if $transactionId == 0 then "no-transaction" else ($historyInfo[0].status // "unknown") end),
      packages:(if $transactionId == 0 then [] else ($historyInfo[0].packages | map(.nevra)) end), reboot:$reboot}' \
    <<< "$info") || return 1
  RIDE_DNF5_SYSTEM_UPDATE_REPORT=$report
  printf 'DNF5 system update report: %s\n' "$report"
  [[ "$status" == success ]] || return 1
}

ride_docker_engine_repo_path() { printf '/etc/yum.repos.d/docker-ce.repo\n'; }
ride_docker_engine_key_path() { printf '/etc/pki/rpm-gpg/RPM-GPG-KEY-docker-ce-ride\n'; }
ride_docker_engine_repo_content() {
  printf '[docker-ce-stable]\nname=Docker CE Stable - $basearch\nbaseurl=https://download.docker.com/linux/fedora/$releasever/$basearch/stable\nenabled=1\ngpgcheck=1\ngpgkey=file://%s\n' \
    "$(ride_docker_engine_key_path)"
}
ride_docker_engine_state_dir() {
  if [[ "${RIDE_TEST_MODE:-0}" == 1 && -n "${RIDE_TEST_DOCKER_STATE_DIR:-}" ]]; then
    printf '%s\n' "$RIDE_TEST_DOCKER_STATE_DIR"
  else
    printf '/var/lib/ride-fedora/operations\n'
  fi
}
ride_docker_engine_marker() { printf '%s/docker-engine.json\n' "$(ride_docker_engine_state_dir)"; }
ride_docker_engine_packages() { printf '%s\n' docker-ce docker-ce-cli containerd.io; }
ride_docker_engine_owned_marker_valid() {
  local marker=$1
  [[ -f "$marker" && ! -L "$marker" ]] || return 1
  jq -e '.operationId == "system.docker-engine" and
    .packages == ["docker-ce", "docker-ce-cli", "containerd.io"] and
    (.signingFingerprint | type == "string" and test("^[A-F0-9]{40}$")) and
    (.keySha256 | type == "string" and test("^[a-f0-9]{64}$"))' \
    "$marker" >/dev/null 2>&1
}
ride_docker_engine_all_packages_installed() {
  local package
  for package in $(ride_docker_engine_packages); do
    rpm -q --quiet "$package" || return 1
  done
}
ride_docker_engine_any_package_installed() {
  local package
  for package in docker-ce docker-ce-cli containerd.io docker docker-client \
    docker-client-latest docker-common docker-latest docker-latest-logrotate \
    docker-logrotate docker-selinux docker-engine moby-engine docker-cli containerd \
    podman-docker; do
    if rpm -q --quiet "$package"; then return 0; fi
  done
  return 1
}
ride_docker_engine_observe() {
  local entry=$1 marker repo service expected key key_hash
  ride_require_command rpm
  marker=$(ride_docker_engine_marker)
  repo=$(ride_docker_engine_repo_path)
  if [[ ! -e "$marker" && ! -L "$marker" && ! -e "$repo" && ! -L "$repo" ]] &&
     ! ride_docker_engine_any_package_installed; then
    printf 'absent\n'
    return
  fi
  ride_docker_engine_owned_marker_valid "$marker" ||
    ride_die 'Docker Engine has partial or unowned state; inspect it before changing anything'
  expected=$(jq -r '.signingFingerprint' <<< "$entry")
  jq -e --arg expected "$expected" '.signingFingerprint == $expected' "$marker" >/dev/null ||
    ride_die 'Docker ownership marker signing key differs from the catalog pin'
  key=$(ride_docker_engine_key_path)
  [[ -f "$key" && ! -L "$key" ]] || ride_die 'RIDE-managed Docker signing key is missing or unsafe'
  key_hash=$(sha256sum "$key" | cut -d' ' -f1)
  jq -e --arg keyHash "$key_hash" '.keySha256 == $keyHash' "$marker" >/dev/null ||
    ride_die 'RIDE-managed Docker signing key has changed'
  [[ -f "$repo" && ! -L "$repo" ]] || ride_die 'owned Docker repository file is missing or unsafe'
  cmp -s "$repo" <(ride_docker_engine_repo_content) ||
    ride_die 'Docker repository file differs from the RIDE-owned content'
  ride_docker_engine_all_packages_installed ||
    ride_die 'Docker Engine package set is incomplete; inspect it before changing anything'
  service=$(systemctl is-active docker.service 2>/dev/null || true)
  case "$service" in
    active) printf 'configured\n' ;;
    inactive) printf 'stopped\n' ;;
    *) ride_die "cannot identify RIDE-managed Docker service state: ${service:-unknown}" ;;
  esac
}
ride_docker_engine_guard() {
  local entry=$1 marker repo key directory fingerprint load_state
  [[ "$RIDE_OS_ID" == fedora ]] || ride_die 'Docker Engine requires Fedora'
  marker=$(ride_docker_engine_marker)
  repo=$(ride_docker_engine_repo_path)
  key=$(ride_docker_engine_key_path)
  directory=${repo%/*}
  [[ -d "$directory" && ! -L "$directory" && -f /etc/os-release ]] ||
    ride_die 'Docker repository directory or Fedora identity is unavailable'
  [[ -d "${key%/*}" && ! -L "${key%/*}" ]] || ride_die 'Docker signing-key directory is unavailable'
  [[ ! -e "$repo" && ! -L "$repo" ]] || ride_die 'Docker repository path is already owned by another source'
  [[ ! -e "$key" && ! -L "$key" ]] || ride_die 'Docker signing-key path is already owned by another source'
  [[ ! -e "$marker" && ! -L "$marker" ]] || ride_die 'Docker ownership marker already exists; inspect it before continuing'
  ride_docker_engine_any_package_installed &&
    ride_die 'a Docker-compatible engine package is already installed; resolve its ownership first'
  ride_require_command rpm
  ride_require_command dnf5
  ride_require_command curl
  ride_require_command gpg
  ride_require_command systemctl
  ride_require_command install
  load_state=$(systemctl show --property=LoadState --value docker.service 2>/dev/null || true)
  [[ -z "$load_state" || "$load_state" == not-found ]] ||
    ride_die 'a Docker service unit is already present; resolve its ownership first'
  fingerprint=$(jq -r '.signingFingerprint' <<< "$entry")
  [[ "$fingerprint" =~ ^[A-F0-9]{40}$ ]] || ride_die 'invalid pinned Docker signing fingerprint'
}
ride_docker_engine_write_key() {
  local entry=$1 fingerprint output found key temporary
  fingerprint=$(jq -r '.signingFingerprint' <<< "$entry")
  key=$(ride_docker_engine_key_path)
  temporary=$(mktemp "${key%/*}/.ride-docker-key.XXXXXXXX") || return 1
  if ! curl --fail --location --silent --show-error \
       https://download.docker.com/linux/fedora/gpg -o "$temporary"; then
    rm -f -- "$temporary"
    ride_die 'could not acquire the Docker signing key'
  fi
  output=$(gpg --batch --with-colons --show-keys "$temporary" 2>/dev/null) || {
    rm -f -- "$temporary"
    ride_die 'could not inspect the Docker signing key'
  }
  found=$(awk -F: '$1 == "fpr" {print $10}' <<< "$output")
  if ! grep -Fxq "$fingerprint" <<< "$found"; then
    rm -f -- "$temporary"
    ride_die 'Docker signing key fingerprint does not match the pinned publisher key'
  fi
  chmod 0644 "$temporary" || { rm -f -- "$temporary"; return 1; }
  if ! ln -- "$temporary" "$key"; then
    rm -f -- "$temporary"
    ride_die 'Docker signing-key path appeared during installation'
  fi
  rm -f -- "$temporary"
  RIDE_DOCKER_ENGINE_KEY_SHA256=$(sha256sum "$key" | cut -d' ' -f1)
}
ride_docker_engine_write_marker() {
  local fingerprint=$1 key_sha256=$2 marker directory temporary
  marker=$(ride_docker_engine_marker)
  directory=${marker%/*}
  mkdir -p -- "$directory" || return 1
  [[ -d "$directory" && ! -L "$directory" ]] || return 1
  if [[ "${RIDE_TEST_MODE:-0}" != 1 ]]; then
    [[ "$(stat -c %u "$directory")" == 0 ]] || return 1
  fi
  temporary=$(mktemp "$directory/.docker-engine.XXXXXXXX") || return 1
  if ! jq -nc --arg fingerprint "$fingerprint" --arg keySha256 "$key_sha256" \
       '{operationId:"system.docker-engine", packages:["docker-ce","docker-ce-cli","containerd.io"], signingFingerprint:$fingerprint, keySha256:$keySha256}' > "$temporary" ||
     ! chmod 0600 "$temporary" || ! ln -- "$temporary" "$marker"; then
    rm -f -- "$temporary"
    return 1
  fi
  rm -f -- "$temporary"
}
ride_docker_engine_write_repo() {
  local repo=$1 temporary
  temporary=$(mktemp "${repo%/*}/.ride-docker-ce.XXXXXXXX") || return 1
  if ! ride_docker_engine_repo_content > "$temporary" ||
     ! chmod 0644 "$temporary" || ! ln -- "$temporary" "$repo"; then
    rm -f -- "$temporary"
    return 1
  fi
  rm -f -- "$temporary"
}
ride_docker_engine_cleanup_install() {
  local repo marker key key_hash
  repo=$(ride_docker_engine_repo_path)
  marker=$(ride_docker_engine_marker)
  key=$(ride_docker_engine_key_path)
  systemctl stop docker.service >/dev/null 2>&1 || true
  if ride_docker_engine_any_package_installed; then
    dnf5 remove --assumeyes docker-ce docker-ce-cli containerd.io >/dev/null 2>&1 || true
  fi
  if [[ -f "$repo" && ! -L "$repo" ]] && cmp -s "$repo" <(ride_docker_engine_repo_content); then
    rm -f -- "$repo"
  fi
  key_hash=$(sha256sum "$key" 2>/dev/null | cut -d' ' -f1 || true)
  if [[ -n "$key_hash" && "$key_hash" == "${RIDE_DOCKER_ENGINE_KEY_SHA256:-}" ]] ||
     { [[ -n "$key_hash" && -f "$marker" ]] &&
       jq -e --arg hash "$key_hash" '.keySha256 == $hash' "$marker" >/dev/null 2>&1; }; then
    rm -f -- "$key"
  fi
  ride_docker_engine_owned_marker_valid "$marker" && rm -f -- "$marker"
}
ride_docker_engine_remove_guard() {
  local entry=$1 running current
  current=$(ride_docker_engine_observe "$entry")
  [[ "$current" != absent ]] || return 0
  [[ "$current" == configured ]] ||
    ride_die 'Docker daemon is inactive; start it so RIDE can verify that no containers are running before removal'
  if running=$(docker ps --quiet 2>&1); then
    [[ -z "$running" ]] || ride_die 'running Docker containers prevent removal; stop them and retry'
  elif [[ "$(systemctl is-active docker.service 2>/dev/null || true)" == active ]]; then
    ride_die "cannot inspect running Docker containers: $running"
  fi
}
ride_docker_engine_change() {
  local entry=$1 state=$2 repo marker key fingerprint package running current
  repo=$(ride_docker_engine_repo_path)
  marker=$(ride_docker_engine_marker)
  key=$(ride_docker_engine_key_path)
  case "$state" in
    configured)
      current=$(ride_docker_engine_observe "$entry")
      [[ "$current" != configured ]] || return 0
      if [[ "$current" == stopped ]]; then
        systemctl start docker.service || ride_die 'could not start the RIDE-managed Docker service'
        [[ "$(ride_docker_engine_observe "$entry")" == configured ]] ||
          ride_die 'Docker Engine did not return to the active state'
        return
      fi
      ride_docker_engine_guard "$entry"
      fingerprint=$(jq -r '.signingFingerprint' <<< "$entry")
      if ! ride_docker_engine_write_key "$entry" ||
         ! ride_docker_engine_write_repo "$repo" ||
         ! ride_docker_engine_write_marker "$fingerprint" "$RIDE_DOCKER_ENGINE_KEY_SHA256"; then
        [[ ! -f "$key" ]] || rm -f -- "$key"
        [[ ! -f "$repo" ]] || { cmp -s "$repo" <(ride_docker_engine_repo_content) && rm -f -- "$repo"; }
        ride_die 'could not create Docker Engine ownership state'
      fi
      if ! dnf5 --setopt=install_weak_deps=False install --assumeyes docker-ce docker-ce-cli containerd.io; then
        ride_docker_engine_cleanup_install
        return 1
      fi
      if ! systemctl start docker.service ||
         ! ride_docker_engine_all_packages_installed ||
         [[ "$(systemctl is-active docker.service 2>/dev/null || true)" != active ]]; then
        ride_docker_engine_cleanup_install
        ride_die 'Docker Engine did not reach the active state; newly installed packages were removed and data paths were preserved'
      fi
      ;;
    absent)
      current=$(ride_docker_engine_observe "$entry")
      [[ "$current" != absent ]] || return 0
      ride_docker_engine_remove_guard "$entry"
      systemctl stop docker.service || return 1
      if ! dnf5 remove --assumeyes docker-ce docker-ce-cli containerd.io; then
        systemctl start docker.service >/dev/null 2>&1 ||
          ride_error 'Docker Engine removal failed and the service could not be restarted'
        return 1
      fi
      rm -f -- "$repo" "$key" "$marker" || ride_die 'Docker packages were removed but owned repository cleanup failed'
      ;;
    *) ride_die "invalid Docker Engine state: $state" ;;
  esac
}

ride_glances_web_service_unit() { printf '/usr/lib/systemd/system/glances.service\n'; }
ride_glances_web_service_dropin() {
  printf '/etc/systemd/system/glances.service.d/60-ride-loopback.conf\n'
}
ride_glances_web_service_content() {
  cat <<'EOF'
[Service]
ExecStart=
ExecStart=/usr/bin/glances -w -B 127.0.0.1
EOF
}

ride_glances_web_service_dropins_are_owned() {
  local directory dropin file
  dropin=$(ride_glances_web_service_dropin)
  directory=${dropin%/*}
  [[ -d "$directory" ]] || return 0
  for file in "$directory"/*.conf; do
    [[ -e "$file" || -L "$file" ]] || continue
    [[ "$file" == "$dropin" ]] || ride_die "refusing unrelated Glances service drop-in: $file"
  done
}

ride_glances_web_service_observe() {
  local unit fragment enabled active dropin
  unit=$(ride_glances_web_service_unit)
  dropin=$(ride_glances_web_service_dropin)
  fragment=$(systemctl show --property=FragmentPath --value glances.service 2>/dev/null || true)
  if [[ -z "$fragment" || "$fragment" == /dev/null ]]; then
    printf 'disabled\n'
    return 0
  fi
  [[ "$fragment" == "$unit" ]] || ride_die "refusing an unowned Glances unit: $fragment"
  [[ "$(rpm -qf --qf '%{NAME}' "$unit" 2>/dev/null || true)" == glances ]] ||
    ride_die 'Glances service unit is not owned by the Fedora glances RPM'
  if [[ -e "$dropin" || -L "$dropin" ]]; then
    [[ -f "$dropin" && ! -L "$dropin" ]] || ride_die 'Glances RIDE drop-in is not a regular file'
    cmp -s "$dropin" <(ride_glances_web_service_content) ||
      ride_die "refusing an unowned Glances service drop-in: $dropin"
    ride_glances_web_service_dropins_are_owned
  else
    enabled=$(systemctl is-enabled glances.service 2>/dev/null || true)
    active=$(systemctl is-active glances.service 2>/dev/null || true)
    [[ "$enabled" == disabled && "$active" != active ]] ||
      ride_die 'refusing a pre-enabled or active Glances service without the RIDE loopback override'
    printf 'disabled\n'
    return 0
  fi
  enabled=$(systemctl is-enabled glances.service 2>/dev/null || true)
  active=$(systemctl is-active glances.service 2>/dev/null || true)
  if [[ "$enabled" == enabled && "$active" == active ]]; then
    printf 'enabled\n'
  elif [[ "$enabled" == disabled && "$active" != active ]]; then
    printf 'disabled\n'
  else
    ride_die "Glances service has mixed enabled/active state: ${enabled:-unknown}/${active:-unknown}"
  fi
}

ride_glances_web_service_change() {
  local state=$1 observed dropin directory temporary
  dropin=$(ride_glances_web_service_dropin)
  directory=${dropin%/*}
  case "$state" in
    enabled)
      observed=$(ride_glances_web_service_observe)
      [[ "$observed" == enabled ]] && return 0
      [[ "$observed" == disabled ]] || ride_die 'Glances Web service is not in a managed disabled state'
      ride_glances_web_service_dropins_are_owned
      mkdir -p -- "$directory" || ride_die 'could not create Glances service drop-in directory'
      [[ ! -e "$dropin" && ! -L "$dropin" ]] || ride_die "Glances service drop-in already exists: $dropin"
      temporary=$(mktemp "$directory/.60-ride-loopback.XXXXXXXX") || ride_die 'could not stage Glances loopback override'
      if ! ride_glances_web_service_content > "$temporary" || ! chmod 0644 "$temporary" || ! ln -- "$temporary" "$dropin"; then
        rm -f -- "$temporary"
        ride_die 'could not install Glances loopback override without replacing existing state'
      fi
      rm -f -- "$temporary"
      if ! systemctl daemon-reload || ! systemctl enable --now glances.service; then
        systemctl disable --now glances.service >/dev/null 2>&1 || true
        cmp -s "$dropin" <(ride_glances_web_service_content) && rm -f -- "$dropin"
        systemctl daemon-reload >/dev/null 2>&1 || true
        ride_die 'could not enable and start the loopback-only Glances Web service'
      fi
      ;;
    disabled)
      observed=$(ride_glances_web_service_observe)
      [[ "$observed" == disabled ]] && return 0
      [[ "$observed" == enabled ]] || ride_die 'Glances Web service is not in a managed enabled state'
      systemctl disable --now glances.service || ride_die 'could not stop and disable Glances Web service'
      cmp -s "$dropin" <(ride_glances_web_service_content) ||
        ride_die 'Glances service override changed; refusing to remove modified state'
      rm -f -- "$dropin" || ride_die 'could not remove the RIDE Glances service override'
      rmdir --ignore-fail-on-non-empty -- "${dropin%/*}" 2>/dev/null || true
      systemctl daemon-reload || ride_die 'could not reload systemd after removing Glances override'
      ;;
    *) ride_die "invalid Glances Web service state: $state" ;;
  esac
  observed=$(ride_glances_web_service_observe)
  [[ "$observed" == "$state" ]] || ride_die "Glances Web service did not reach $state state"
}

ride_sshd_root_login_dropin() { printf '/etc/ssh/sshd_config.d/00-ride-root-login.conf\n'; }
ride_sshd_root_login_content() {
  cat <<'EOF'
# Managed by RIDE. Disable direct SSH login as root.
PermitRootLogin no
EOF
}

ride_sshd_root_login_effective() {
  local policy host
  host=$(hostname -f 2>/dev/null || hostname)
  policy=$(sshd -T -C "user=root,host=$host,addr=127.0.0.1" 2>/dev/null |
    awk 'tolower($1) == "permitrootlogin" { print tolower($2); exit }') || return 1
  [[ "$policy" == no ]]
}

ride_sshd_root_login_observe() {
  local dropin
  dropin=$(ride_sshd_root_login_dropin)
  if [[ ! -e "$dropin" && ! -L "$dropin" ]]; then
    printf 'absent\n'
    return 0
  fi
  [[ -f "$dropin" && ! -L "$dropin" ]] || ride_die 'RIDE SSH root-login drop-in is not a regular file'
  cmp -s "$dropin" <(ride_sshd_root_login_content) ||
    ride_die "refusing a modified SSH root-login drop-in: $dropin"
  sshd -t || ride_die 'sshd rejected the current configuration'
  ride_sshd_root_login_effective || ride_die 'effective PermitRootLogin is not no for root'
  printf 'configured\n'
}

ride_sshd_root_login_change() {
  local state=$1 dropin directory temporary
  dropin=$(ride_sshd_root_login_dropin)
  directory=${dropin%/*}
  case "$state" in
    configured)
      [[ "$(systemctl is-active sshd.service 2>/dev/null || true)" == active ]] ||
        ride_die 'refusing SSH policy change while sshd.service is not active'
      [[ ! -e "$dropin" && ! -L "$dropin" ]] || {
        [[ "$(ride_sshd_root_login_observe)" == configured ]] && return 0
        ride_die "SSH root-login drop-in already exists: $dropin"
      }
      sshd -t || ride_die 'sshd rejected the existing configuration'
      mkdir -p -- "$directory" || ride_die 'could not create sshd configuration directory'
      temporary=$(mktemp "$directory/.00-ride-root-login.XXXXXXXX") ||
        ride_die 'could not stage SSH root-login policy'
      if ! ride_sshd_root_login_content > "$temporary" || ! chmod 0644 "$temporary" || ! ln -- "$temporary" "$dropin"; then
        rm -f -- "$temporary"
        ride_die 'could not install SSH root-login policy without replacing existing state'
      fi
      rm -f -- "$temporary"
      if ! sshd -t || ! ride_sshd_root_login_effective || ! systemctl reload sshd.service; then
        cmp -s "$dropin" <(ride_sshd_root_login_content) && rm -f -- "$dropin"
        systemctl reload sshd.service >/dev/null 2>&1 || true
        ride_die 'could not safely apply PermitRootLogin no; prior SSH configuration was restored'
      fi
      [[ "$(ride_sshd_root_login_observe)" == configured ]] || ride_die 'SSH root-login policy did not reach configured state'
      ;;
    absent)
      [[ "$(ride_sshd_root_login_observe)" == configured ]] || return 0
      rm -f -- "$dropin" || ride_die 'could not remove RIDE SSH root-login drop-in'
      if ! sshd -t || ! systemctl reload sshd.service; then
        ride_sshd_root_login_content > "$dropin"
        chmod 0644 "$dropin"
        systemctl reload sshd.service >/dev/null 2>&1 || true
        ride_die 'could not safely restore the previous SSH policy; RIDE drop-in was reinstated'
      fi
      rmdir --ignore-fail-on-non-empty -- "$directory" 2>/dev/null || true
      [[ "$(ride_sshd_root_login_observe)" == absent ]] || ride_die 'SSH root-login policy did not reach absent state'
      ;;
    *) ride_die "invalid SSH root-login state: $state" ;;
  esac
}

ride_nsswitch_mdns_marker() {
  if [[ "${RIDE_TEST_MODE:-0}" == 1 && -n "${RIDE_TEST_NSSWITCH_MARKER:-}" ]]; then
    printf '%s\n' "$RIDE_TEST_NSSWITCH_MARKER"
  else
    printf '%s\n' /var/lib/ride-fedora/operations/multicast-dns.json
  fi
}
ride_nsswitch_mdns_current() {
  local raw profile features
  authselect check >/dev/null 2>&1 || ride_die 'authselect configuration is invalid or unmanaged; refusing to edit resolver policy'
  raw=$(authselect current --raw 2>/dev/null) || ride_die 'cannot read the current authselect profile'
  read -r profile features <<< "$raw"
  [[ "$profile" =~ ^[A-Za-z0-9_.-]+$ && -n "$raw" ]] || ride_die 'authselect returned an invalid profile'
  authselect list-features "$profile" 2>/dev/null | grep -Fxq with-mdns4 ||
    ride_die 'the selected authselect profile does not support with-mdns4'
  if [[ " $features " == *" with-mdns4 "* && "${features##* }" != with-mdns4 ]]; then
    ride_die 'with-mdns4 is not the final authselect feature; refusing a non-exact inverse'
  fi
  printf '%s\n' "$raw"
}
ride_nsswitch_mdns_feature_state() {
  [[ " $1 " == *" with-mdns4 "* ]] && printf 'enabled\n' || printf 'disabled\n'
}
ride_nsswitch_mdns_observe() {
  local marker current managed desired
  marker=$(ride_nsswitch_mdns_marker)
  current=$(ride_nsswitch_mdns_current)
  if [[ -e "$marker" || -L "$marker" ]]; then
    [[ -f "$marker" && ! -L "$marker" ]] || ride_die 'MulticastDNS ownership marker is unsafe'
    jq -e '.operationId == "setting.multicast-dns" and (.priorCurrent | type == "string") and (.managedCurrent | type == "string") and (.desired | IN("enabled","disabled"))' "$marker" >/dev/null ||
      ride_die 'MulticastDNS ownership marker is invalid'
    managed=$(jq -r '.managedCurrent' "$marker")
    desired=$(jq -r '.desired' "$marker")
    [[ "$current" == "$managed" ]] || ride_die 'authselect profile changed outside RIDE; refusing to claim MulticastDNS state'
    printf '%s\n' "$desired"
  else
    ride_nsswitch_mdns_feature_state "$current"
  fi
}
ride_nsswitch_mdns_change() {
  local desired=$1 marker current prior managed current_state updated temporary
  [[ "$desired" == enabled || "$desired" == disabled ]] || ride_die "invalid MulticastDNS state: $desired"
  marker=$(ride_nsswitch_mdns_marker)
  current=$(ride_nsswitch_mdns_current)
  current_state=$(ride_nsswitch_mdns_feature_state "$current")
  if [[ -e "$marker" || -L "$marker" ]]; then
    [[ -f "$marker" && ! -L "$marker" ]] || ride_die 'MulticastDNS ownership marker is unsafe'
    jq -e '.operationId == "setting.multicast-dns" and (.priorCurrent | type == "string") and (.managedCurrent | type == "string") and (.desired | IN("enabled","disabled"))' "$marker" >/dev/null ||
      ride_die 'MulticastDNS ownership marker is invalid'
    prior=$(jq -r '.priorCurrent' "$marker")
    managed=$(jq -r '.managedCurrent' "$marker")
    [[ "$current" == "$managed" ]] || ride_die 'authselect profile changed outside RIDE; refusing MulticastDNS recovery'
  else
    [[ "$current_state" != "$desired" ]] || return 0
    prior=$current
  fi
  if [[ "$current_state" != "$desired" ]]; then
    if [[ "$desired" == enabled ]]; then
      authselect enable-feature with-mdns4 >/dev/null || ride_die 'authselect could not enable with-mdns4'
    else
      authselect disable-feature with-mdns4 >/dev/null || ride_die 'authselect could not disable with-mdns4'
    fi
  fi
  updated=$(ride_nsswitch_mdns_current)
  [[ "$(ride_nsswitch_mdns_feature_state "$updated")" == "$desired" ]] ||
    ride_die 'authselect did not apply the requested with-mdns4 state'
  if [[ "$updated" == "$prior" ]]; then
    rm -f -- "$marker" || ride_die 'restored prior authselect state but could not remove ownership marker'
    return 0
  fi
  mkdir -p -- "${marker%/*}" || ride_die 'cannot create MulticastDNS state directory'
  [[ -d "${marker%/*}" && ! -L "${marker%/*}" ]] || ride_die 'MulticastDNS state directory is unsafe'
  if [[ "${RIDE_TEST_MODE:-0}" != 1 ]]; then
    [[ "$(stat -c %u "${marker%/*}")" == 0 ]] || ride_die 'MulticastDNS state directory must be root-owned'
  fi
  temporary=$(mktemp "${marker%/*}/.multicast-dns.XXXXXXXX") || ride_die 'cannot stage MulticastDNS ownership marker'
  if ! jq -nc --arg prior "$prior" --arg managed "$updated" --arg desired "$desired" \
       '{operationId:"setting.multicast-dns",priorCurrent:$prior,managedCurrent:$managed,desired:$desired}' > "$temporary" ||
     ! chmod 0600 "$temporary" || ! mv -f -- "$temporary" "$marker"; then
    rm -f -- "$temporary"
    ride_die 'cannot record MulticastDNS ownership state'
  fi
}

ride_upower_dir() {
  printf '/etc/UPower/UPower.conf.d\n'
}

ride_upower_main() {
  printf '/etc/UPower/UPower.conf\n'
}

ride_upower_path() {
  printf '%s/70-ride-percentage-low.conf\n' "$(ride_upower_dir)"
}

ride_upower_content() {
  printf '# RIDE v3 managed: setting.upower-percentage-low\n[UPower]\nPercentageLow=%s.0\n' "$1"
}

ride_upower_valid_snapshot() {
  [[ "$1" == absent || "$1" =~ ^owned:([6-9]|[1-4][0-9]|50)$ ]]
}

ride_upower_file_state() {
  local path value
  path=$(ride_upower_path)
  if [[ ! -e "$path" && ! -L "$path" ]]; then printf 'absent\n'; return; fi
  [[ -f "$path" && ! -L "$path" && "$(stat -c %u "$path")" == 0 ]] ||
    { printf 'unowned\n'; return; }
  value=$(sed -n 's/^PercentageLow=\([0-9][0-9]*\)\.0$/\1/p' "$path") || return 1
  if [[ "$value" =~ ^([6-9]|[1-4][0-9]|50)$ ]] &&
      cmp -s "$path" <(ride_upower_content "$value"); then
    printf 'owned:%s\n' "$value"
  else
    printf 'unowned\n'
  fi
}

ride_upower_observe() {
  local entry=$1 selected current
  selected=$(jq -r '.selectedValue // ""' <<< "$entry")
  current=$(ride_upower_file_state) || ride_die "cannot read UPower drop-in"
  if [[ "$current" == "owned:$selected" && -n "$selected" ]]; then
    printf 'configured\n'
  else
    printf '%s\n' "$current"
  fi
}

ride_upower_guard() {
  local threshold=$1 dir path main file key value critical action percent_policy
  dir=$(ride_upower_dir)
  path=$(ride_upower_path)
  main=$(ride_upower_main)
  [[ -d "$dir" && ! -L "$dir" && -f "$main" ]] ||
    ride_die "UPower configuration directory or main file is unavailable"
  [[ "$(stat -c %u "$dir")" == 0 ]] || ride_die "UPower configuration directory is not root-owned"
  ride_require_command rpm
  ride_require_command systemctl
  rpm -q --quiet upower || ride_die "UPower is not installed"
  [[ "$(ride_upower_file_state)" != unowned ]] || ride_die "UPower RIDE path is not owned by RIDE"
  local -a files=("$main")
  while IFS= read -r -d '' file; do
    [[ -f "$file" && ! -L "$file" ]] || ride_die "UPower drop-in is not a regular file: $file"
    if [[ "$file" != "$path" ]] && grep -Eq '^[[:space:]]*PercentageLow[[:space:]]*=' "$file"; then
      ride_die "another UPower drop-in selects PercentageLow: $file"
    fi
    files+=("$file")
  done < <(find "$dir" -maxdepth 1 -name '[0-9][0-9]-*.conf' -print0 | LC_ALL=C sort -z)
  for key in UsePercentageForPolicy PercentageCritical PercentageAction; do
    value=$(awk -F= -v wanted="$key" '
      /^[[:space:]]*\[UPower\][[:space:]]*$/ { section=1; next }
      /^[[:space:]]*\[/ { section=0 }
      section && $1 ~ "^[[:space:]]*" wanted "[[:space:]]*$" {
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2); result=$2
      }
      END { print result }
    ' "${files[@]}") || ride_die "cannot parse UPower policy"
    case "$key" in
      UsePercentageForPolicy) percent_policy=$value ;;
      PercentageCritical) critical=$value ;;
      PercentageAction) action=$value ;;
    esac
  done
  [[ "$percent_policy" == true && "$critical" =~ ^[0-9]+([.][0-9]+)?$ &&
     "$action" =~ ^[0-9]+([.][0-9]+)?$ ]] || ride_die "UPower percentage policy is unavailable"
  awk -v low="$threshold" -v critical="$critical" -v action="$action" \
    'BEGIN { exit !(low > critical && critical > action && action >= 0) }' ||
    ride_die "UPower low threshold must exceed critical and action thresholds"
}

ride_upower_write() {
  local state=$1 dir path temp value
  dir=$(ride_upower_dir)
  path=$(ride_upower_path)
  case "$state" in
    absent) rm -f -- "$path" ;;
    owned:*)
      ride_upower_valid_snapshot "$state" || ride_die "invalid UPower snapshot"
      value=${state#owned:}
      temp=$(mktemp "$dir/.ride-upower.XXXXXXXX") || return 1
      if ! ride_upower_content "$value" > "$temp" || ! chmod 0644 "$temp" || ! mv -T -- "$temp" "$path"; then
        rm -f -- "$temp"
        return 1
      fi
      ;;
    *) ride_die "invalid UPower write state" ;;
  esac
}

ride_upower_change() {
  local entry=$1 state=$2 selected target before after
  selected=$(jq -r '.selectedValue // ""' <<< "$entry")
  [[ "$selected" =~ ^([6-9]|[1-4][0-9]|50)$ ]] || ride_die "invalid selected UPower threshold"
  case "$state" in
    configured) target="owned:$selected" ;;
    absent|owned:*) ride_upower_valid_snapshot "$state" || ride_die "invalid saved UPower state"; target=$state ;;
    *) ride_die "invalid UPower state" ;;
  esac
  if [[ "$target" == absent ]]; then
    ride_upower_guard "$selected"
  else
    ride_upower_guard "${target#owned:}"
  fi
  before=$(ride_upower_file_state) || ride_die "cannot observe UPower drop-in"
  ride_upower_valid_snapshot "$before" || ride_die "UPower drop-in is not owned by RIDE"
  if ! ride_upower_write "$target" || ! systemctl try-restart upower.service; then
    ride_upower_write "$before" && systemctl try-restart upower.service ||
      ride_error "UPower rollback failed after write or reload error"
    return 1
  fi
  after=$(ride_upower_observe "$entry") || after=unknown
  if [[ "$after" != "$state" ]]; then
    ride_upower_write "$before" && systemctl try-restart upower.service ||
      ride_error "UPower rollback failed after verification error"
    ride_error "UPower threshold verification failed"
    return 1
  fi
}

ride_dnf5_tuning_dir() { printf '/etc/dnf/libdnf5.conf.d\n'; }
ride_dnf5_tuning_path() { printf '%s/99-ride-fastdnf.conf\n' "$(ride_dnf5_tuning_dir)"; }
ride_dnf5_tuning_main() { printf '/etc/dnf/dnf.conf\n'; }
ride_dnf5_tuning_distribution_dir() { printf '/usr/share/dnf5/libdnf.conf.d\n'; }
ride_dnf5_tuning_content() {
  printf '# RIDE v3 managed: setting.dnf5-fast-tuning\n[main]\nfastestmirror=True\nmax_parallel_downloads=15\n'
}

ride_dnf5_tuning_file_state() {
  local path
  path=$(ride_dnf5_tuning_path)
  if [[ ! -e "$path" && ! -L "$path" ]]; then printf 'absent\n'; return; fi
  [[ -f "$path" && ! -L "$path" && "$(stat -c %u "$path")" == 0 ]] ||
    { printf 'unowned\n'; return; }
  if cmp -s "$path" <(ride_dnf5_tuning_content); then printf 'configured\n';
  else printf 'unowned\n'; fi
}

ride_dnf5_tuning_effective() {
  local output
  ride_require_command dnf5
  output=$(dnf5 --dump-main-config) || ride_die 'cannot read effective DNF5 configuration'
  grep -Eiq '^[[:space:]]*fastestmirror[[:space:]]*=[[:space:]]*(true|1)[[:space:]]*$' <<< "$output" ||
    ride_die 'DNF5 did not load the RIDE fastestmirror setting'
  grep -Eiq '^[[:space:]]*max_parallel_downloads[[:space:]]*=[[:space:]]*15[[:space:]]*$' <<< "$output" ||
    ride_die 'DNF5 did not load the RIDE parallel download setting'
}

ride_dnf5_tuning_guard() {
  local dir path main distribution
  dir=$(ride_dnf5_tuning_dir)
  path=$(ride_dnf5_tuning_path)
  main=$(ride_dnf5_tuning_main)
  distribution=$(ride_dnf5_tuning_distribution_dir)
  [[ -d "$dir" && ! -L "$dir" && "$(stat -c %u "$dir")" == 0 ]] ||
    ride_die 'DNF5 configuration drop-in directory must exist and be root-owned'
  [[ -f "$main" && ! -L "$main" ]] || ride_die 'DNF5 main configuration is unavailable'
  [[ "$(ride_dnf5_tuning_file_state)" != unowned ]] ||
    ride_die 'DNF5 RIDE drop-in exists but is not owned by this operation'
  ride_require_command dnf5
  local file
  while IFS= read -r -d '' file; do
    [[ "$file" == "$path" ]] && continue
    [[ -f "$file" && ! -L "$file" ]] || ride_die "DNF5 configuration is not a regular file: $file"
    if grep -Eiq '^[[:space:]]*(fastestmirror|max_parallel_downloads)[[:space:]]*=' "$file"; then
      ride_die "DNF5 tuning conflicts with another configuration file: $file"
    fi
  done < <(find "$dir" "$distribution" -maxdepth 1 -type f -name '*.conf' -print0 2>/dev/null | LC_ALL=C sort -z)
  if grep -Eiq '^[[:space:]]*(fastestmirror|max_parallel_downloads)[[:space:]]*=' "$main"; then
    ride_die 'DNF5 main configuration sets a RIDE-managed key; remove the conflict first'
  fi
}

ride_dnf5_tuning_write() {
  local state=$1 path dir temp
  dir=$(ride_dnf5_tuning_dir)
  path=$(ride_dnf5_tuning_path)
  case "$state" in
    absent) rm -f -- "$path" ;;
    configured)
      temp=$(mktemp "$dir/.ride-fastdnf.XXXXXXXX") || return 1
      if ! ride_dnf5_tuning_content > "$temp" || ! chmod 0644 "$temp" || ! mv -T -- "$temp" "$path"; then
        rm -f -- "$temp"
        return 1
      fi
      ;;
    *) ride_die 'invalid saved DNF5 tuning state' ;;
  esac
}

ride_dnf5_fast_tuning_observe() {
  local state
  state=$(ride_dnf5_tuning_file_state) || ride_die 'cannot inspect DNF5 tuning drop-in'
  [[ "$state" != configured ]] || ride_dnf5_tuning_effective
  printf '%s\n' "$state"
}

ride_dnf5_fast_tuning_change() {
  local desired=$1 before after
  case "$desired" in configured|absent) ;; *) ride_die 'invalid DNF5 tuning state' ;; esac
  ride_dnf5_tuning_guard
  before=$(ride_dnf5_tuning_file_state)
  [[ "$before" != unowned ]] || ride_die 'DNF5 RIDE drop-in is not owned'
  if ! ride_dnf5_tuning_write "$desired"; then ride_die 'cannot write DNF5 tuning drop-in'; fi
  if [[ "$desired" == configured ]]; then
    if ! ride_dnf5_tuning_effective; then
      ride_dnf5_tuning_write "$before" || ride_error 'DNF5 tuning rollback failed'
      return 1
    fi
  fi
  after=$(ride_dnf5_tuning_file_state)
  if [[ "$after" != "$desired" ]]; then
    ride_dnf5_tuning_write "$before" || ride_error 'DNF5 tuning rollback failed'
    ride_die 'DNF5 tuning verification failed'
  fi
}

ride_dnf5_automatic_dropin() {
  if [[ "${RIDE_TEST_MODE:-0}" == 1 && -n "${RIDE_TEST_DNF5_AUTOMATIC_DROPIN:-}" ]]; then
    printf '%s\n' "$RIDE_TEST_DNF5_AUTOMATIC_DROPIN"
  else
    printf '%s\n' /etc/systemd/system/dnf5-automatic.service.d/50-ride-fedora.conf
  fi
}

ride_dnf5_automatic_marker() {
  if [[ "${RIDE_TEST_MODE:-0}" == 1 && -n "${RIDE_TEST_DNF5_AUTOMATIC_MARKER:-}" ]]; then
    printf '%s\n' "$RIDE_TEST_DNF5_AUTOMATIC_MARKER"
  else
    printf '%s\n' /var/lib/ride-fedora/operations/dnf5-automatic.json
  fi
}

ride_dnf5_automatic_unit_path() {
  local unit=$1
  if [[ "${RIDE_TEST_MODE:-0}" == 1 ]]; then
    case "$unit" in
      dnf5-automatic.service) printf '%s\n' "${RIDE_TEST_DNF5_AUTOMATIC_SERVICE_UNIT:-}" ;;
      dnf5-automatic.timer) printf '%s\n' "${RIDE_TEST_DNF5_AUTOMATIC_TIMER_UNIT:-}" ;;
      *) return 1 ;;
    esac
  else
    printf '/usr/lib/systemd/system/%s\n' "$unit"
  fi
}

ride_dnf5_automatic_timer_state() {
  local enabled active
  enabled=$(systemctl is-enabled dnf5-automatic.timer 2>/dev/null) || true
  active=$(systemctl is-active dnf5-automatic.timer 2>/dev/null) || true
  case "$enabled:$active" in
    enabled:active|disabled:inactive)
      printf '%s\t%s\n' "$enabled" "$active"
      ;;
    not-found:inactive)
      # The automatic-update RPM is an operation dependency and is absent
      # during initial profile observation and after package restore. Treat
      # the timer as disabled only when systemd confirms the unit is absent.
      if ! systemctl cat dnf5-automatic.timer >/dev/null 2>&1; then
        printf 'disabled\tinactive\n'
      else
        ride_die 'cannot determine dnf5-automatic.timer enablement'
      fi
      ;;
    *) ride_die "unexpected DNF5 automatic timer state: ${enabled:-unknown}/${active:-unknown}" ;;
  esac
}

ride_dnf5_automatic_has_unowned_dropins() {
  local dropin=$1 directory entry
  local -a directories
  if [[ "${RIDE_TEST_MODE:-0}" == 1 ]]; then
    directories=("${dropin%/*}")
  else
    directories=(
      /etc/systemd/system/dnf5-automatic.service.d
      /run/systemd/system/dnf5-automatic.service.d
      /usr/local/lib/systemd/system/dnf5-automatic.service.d
      /usr/lib/systemd/system/dnf5-automatic.service.d
    )
  fi
  for directory in "${directories[@]}"; do
    [[ -e "$directory" || -L "$directory" ]] || continue
    [[ -d "$directory" && ! -L "$directory" ]] || return 0
    entry=$(find "$directory" -mindepth 1 -maxdepth 1 -print -quit) || return 0
    [[ -z "$entry" ]] || return 0
  done
  return 1
}

ride_dnf5_automatic_content() {
  cat <<'EOF'
[Service]
ExecStart=
ExecStart=/usr/bin/dnf5 automatic --timer --installupdates
EOF
}

ride_dnf5_automatic_manifest_valid() {
  local marker=$1 dropin=$2 expected actual state
  jq -e '.operationId == "setting.dnf5-automatic" and
    .priorEnabled == "disabled" and .priorActive == "inactive" and
    .managedEnabled == "enabled" and .managedActive == "active" and
    (.sha256 | type == "string" and test("^[0-9a-f]{64}$"))' "$marker" >/dev/null || return 1
  expected=$(jq -r '.sha256' "$marker") || return 1
  [[ -f "$dropin" && ! -L "$dropin" ]] || return 1
  actual=$(sha256sum -- "$dropin") || return 1
  actual=${actual%% *}
  [[ "$actual" == "$expected" ]] || return 1
  state=$(ride_dnf5_automatic_timer_state) || return 1
  [[ "$state" == $'enabled\tactive' || "$state" == $'disabled\tinactive' ]]
}

ride_dnf5_automatic_observe() {
  local marker dropin state
  marker=$(ride_dnf5_automatic_marker)
  dropin=$(ride_dnf5_automatic_dropin)
  [[ ! -L "$marker" && ! -L "$dropin" ]] || ride_die 'DNF5 automatic-update ownership path is a symlink'
  if [[ -e "$marker" ]]; then
    [[ -f "$marker" ]] || ride_die 'DNF5 automatic-update marker is unsafe'
    ride_dnf5_automatic_manifest_valid "$marker" "$dropin" ||
      ride_die 'DNF5 automatic-update files or timer changed outside RIDE'
    [[ "$(ride_dnf5_automatic_timer_state)" == $'enabled\tactive' ]] ||
      ride_die 'RIDE-owned DNF5 automatic timer is not enabled and active'
    printf 'enabled\n'
    return 0
  fi
  [[ ! -e "$dropin" ]] || ride_die 'an unowned DNF5 automatic service override exists'
  state=$(ride_dnf5_automatic_timer_state)
  [[ "$state" == $'disabled\tinactive' ]] ||
    ride_die 'an unowned DNF5 automatic timer is enabled or active'
  printf 'disabled\n'
}

ride_dnf5_automatic_change() {
  local desired=$1 marker dropin state directory temporary sha
  case "$desired" in enabled|disabled) ;; *) ride_die "invalid DNF5 automatic-update state: $desired" ;; esac
  marker=$(ride_dnf5_automatic_marker)
  dropin=$(ride_dnf5_automatic_dropin)
  [[ ! -L "$marker" && ! -L "$dropin" ]] || ride_die 'DNF5 automatic-update ownership path is a symlink'
  if [[ "$desired" == enabled ]]; then
    if [[ -e "$marker" ]]; then
      ride_dnf5_automatic_manifest_valid "$marker" "$dropin" ||
        ride_die 'DNF5 automatic-update files or timer changed outside RIDE'
      [[ "$(ride_dnf5_automatic_timer_state)" == $'enabled\tactive' ]] ||
        ride_die 'RIDE-owned DNF5 automatic timer is not enabled and active'
      return 0
    fi
    [[ ! -e "$dropin" ]] || ride_die 'an unowned DNF5 automatic service override exists'
    state=$(ride_dnf5_automatic_timer_state)
    [[ "$state" == $'disabled\tinactive' ]] ||
      ride_die 'an unowned DNF5 automatic timer is enabled or active'
    # The package may have installed its units earlier in this same profile
    # apply. Refresh systemd's manager view before resolving those new units.
    systemctl daemon-reload || ride_die 'systemd could not reload newly installed DNF5 automatic units'
    local service_unit timer_unit
    service_unit=$(ride_dnf5_automatic_unit_path dnf5-automatic.service)
    timer_unit=$(ride_dnf5_automatic_unit_path dnf5-automatic.timer)
    [[ -f "$service_unit" && ! -L "$service_unit" &&
       -f "$timer_unit" && ! -L "$timer_unit" ]] ||
      ride_die 'DNF5 automatic service and timer unit files are unavailable; install dnf5-plugin-automatic first'
    ! ride_dnf5_automatic_has_unowned_dropins "$dropin" ||
      ride_die 'unowned DNF5 automatic service drop-ins exist; refusing to replace service behavior'
    dnf5 automatic --help 2>&1 | grep -q -- '--installupdates' ||
      ride_die 'installed DNF5 automatic command lacks --installupdates'
    directory=${dropin%/*}
    [[ ! -L "$directory" ]] || ride_die 'DNF5 automatic service override directory is a symlink'
    mkdir -p -m 0755 -- "$directory" || ride_die 'cannot create DNF5 automatic service override directory'
    [[ -d "$directory" && ! -L "$directory" ]] || ride_die 'DNF5 automatic service override directory is unsafe'
    [[ ! -e "$dropin" ]] || ride_die 'an unowned DNF5 automatic service override exists'
    temporary=$(mktemp "$directory/.50-ride-fedora.XXXXXXXX") || ride_die 'cannot stage DNF5 automatic service override'
    if ! ride_dnf5_automatic_content > "$temporary" || ! chmod 0644 "$temporary"; then
      rm -f -- "$temporary"
      ride_die 'cannot prepare DNF5 automatic service override'
    fi
    sha=$(sha256sum -- "$temporary") || { rm -f -- "$temporary"; ride_die 'cannot hash DNF5 automatic service override'; }
    sha=${sha%% *}
    mkdir -p -m 0700 -- "${marker%/*}" || { rm -f -- "$temporary"; ride_die 'cannot create DNF5 automatic state directory'; }
    [[ -d "${marker%/*}" && ! -L "${marker%/*}" ]] || { rm -f -- "$temporary"; ride_die 'DNF5 automatic state directory is unsafe'; }
    if [[ "${RIDE_TEST_MODE:-0}" != 1 ]]; then
      [[ "$(stat -c %u "${marker%/*}")" == 0 ]] || { rm -f -- "$temporary"; ride_die 'DNF5 automatic state directory must be root-owned'; }
    fi
    local marker_tmp
    marker_tmp=$(mktemp "${marker%/*}/.dnf5-automatic.XXXXXXXX") || { rm -f -- "$temporary"; ride_die 'cannot stage DNF5 automatic ownership marker'; }
    if ! jq -nc --arg sha "$sha" '{operationId:"setting.dnf5-automatic",priorEnabled:"disabled",priorActive:"inactive",managedEnabled:"enabled",managedActive:"active",sha256:$sha}' > "$marker_tmp" ||
       ! chmod 0600 "$marker_tmp" || ! ln -T -- "$marker_tmp" "$marker"; then
      rm -f -- "$temporary" "$marker_tmp"
      ride_die 'cannot create DNF5 automatic ownership marker'
    fi
    rm -f -- "$marker_tmp"
    if ! ln -T -- "$temporary" "$dropin"; then
      rm -f -- "$temporary" "$marker"
      ride_die 'cannot install DNF5 automatic service override'
    fi
    rm -f -- "$temporary"
    systemctl daemon-reload || ride_die 'systemd could not reload DNF5 automatic service configuration'
    systemctl enable --now dnf5-automatic.timer || ride_die 'cannot enable and start dnf5-automatic.timer'
    ride_dnf5_automatic_manifest_valid "$marker" "$dropin" ||
      ride_die 'DNF5 automatic timer or service override did not reach the requested state'
    return 0
  fi
  if [[ ! -e "$marker" ]]; then
    [[ ! -e "$dropin" ]] || ride_die 'an unowned DNF5 automatic service override exists'
    state=$(ride_dnf5_automatic_timer_state)
    [[ "$state" == $'disabled\tinactive' ]] ||
      ride_die 'an unowned DNF5 automatic timer is enabled or active'
    return 0
  fi
  ride_dnf5_automatic_manifest_valid "$marker" "$dropin" ||
    ride_die 'DNF5 automatic-update files or timer changed outside RIDE; preserving them'
  systemctl disable --now dnf5-automatic.timer || ride_die 'cannot stop and disable RIDE-owned DNF5 automatic timer'
  rm -- "$dropin" || ride_die 'cannot remove RIDE-owned DNF5 automatic service override'
  rm -- "$marker" || ride_die 'cannot remove DNF5 automatic ownership marker'
  systemctl daemon-reload || ride_die 'systemd could not reload restored DNF5 automatic service state'
  state=$(ride_dnf5_automatic_timer_state)
  [[ "$state" == $'disabled\tinactive' ]] || ride_die 'DNF5 automatic timer did not return to its prior disabled/inactive state'
}

ride_system_hostname_value() {
  local value=$1 label
  local -a labels
  [[ ${#value} -le 64 && "$value" =~ ^[A-Za-z0-9.-]+$ ]] || return 1
  IFS=. read -r -a labels <<< "$value"
  for label in "${labels[@]}"; do
    [[ ${#label} -le 63 && "$label" =~ ^[A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?$ ]] || return 1
  done
}

ride_system_hostname_snapshot_valid() {
  local state=${1#hostname:}
  [[ "$1" == hostname:* ]] && ride_system_hostname_value "$state"
}

ride_system_hostname_current() {
  local current
  ride_require_command hostnamectl
  current=$(hostnamectl --static) || ride_die 'cannot read static hostname'
  [[ -n "$current" ]] || ride_die 'static hostname is unset; exact prior-name recovery requires a configured static name'
  ride_system_hostname_value "$current" || ride_die 'current static hostname is outside the managed hostname format'
  printf '%s\n' "$current"
}

ride_system_hostname_observe() {
  local entry=$1 selected current
  current=$(ride_system_hostname_current)
  selected=$(jq -r '.selectedValue // ""' <<< "$entry")
  if [[ -n "$selected" && "$current" == "$selected" ]]; then printf 'configured\n';
  else printf 'hostname:%s\n' "$current"; fi
}

ride_system_hostname_change() {
  local entry=$1 desired=$2 selected value
  selected=$(jq -r '.selectedValue // ""' <<< "$entry")
  case "$desired" in
    configured)
      ride_system_hostname_value "$selected" || ride_die 'invalid selected static hostname'
      value=$selected
      ;;
    hostname:*)
      ride_system_hostname_snapshot_valid "$desired" || ride_die 'invalid saved static hostname'
      value=${desired#hostname:}
      ;;
    *) ride_die 'invalid static hostname state' ;;
  esac
  ride_require_command hostnamectl
  hostnamectl set-hostname --static "$value"
  [[ "$(hostnamectl --static)" == "$value" ]] || ride_die 'static hostname verification failed'
}

ride_ibus_hotkey_schema() {
  printf 'org.freedesktop.ibus.panel.emoji hotkey\n'
}

ride_ibus_hotkey_override() {
  ride_require_command dconf
  dconf read /desktop/ibus/panel/emoji/hotkey
}

ride_ibus_hotkey_observe() {
  local schema key effective override
  ride_require_command base64
  read -r schema key < <(ride_ibus_hotkey_schema)
  effective=$(ride_gsettings get "$schema" "$key") || ride_die "cannot observe iBus emoji hotkey"
  override=$(ride_ibus_hotkey_override) || ride_die "cannot read iBus emoji override"
  if [[ "$effective" == "['<Control><Alt><Shift>e']" &&
        "$override" == "['<Control><Alt><Shift>e']" ]]; then
    printf 'enabled\n'
  elif [[ -z "$override" ]]; then
    printf 'unset\n'
  else
    printf 'user:%s\n' "$(printf '%s' "$override" | base64 -w0)"
  fi
}

ride_gsettings_valid_snapshot() {
  local state=$1 encoded raw
  [[ "$state" == unset || "$state" == absent ]] && return 0
  [[ "$state" =~ ^user:([A-Za-z0-9+/]+={0,2})$ ]] || return 1
  encoded=${state#user:}
  raw=$(printf '%s' "$encoded" | base64 --decode 2>/dev/null) || return 1
  [[ -n "$raw" && ${#raw} -le 1024 && "$raw" != *$'\n'* ]]
}

ride_ibus_hotkey_write() {
  local state=$1 schema key raw
  read -r schema key < <(ride_ibus_hotkey_schema)
  case "$state" in
    enabled) ride_gsettings set "$schema" "$key" "['<Control><Alt><Shift>e']" ;;
    absent|unset) ride_gsettings reset "$schema" "$key" ;;
    user:*)
      ride_gsettings_valid_snapshot "$state" || ride_die "invalid saved iBus hotkey value"
      raw=$(printf '%s' "${state#user:}" | base64 --decode) || return 1
      ride_gsettings set "$schema" "$key" "$raw"
      ;;
    *) ride_die "invalid iBus hotkey state" ;;
  esac
}

ride_ibus_hotkey_change() {
  local state=$1 schema key before writable after
  [[ "$state" == enabled ]] || ride_gsettings_valid_snapshot "$state" ||
    ride_die "invalid saved iBus hotkey state"
  read -r schema key < <(ride_ibus_hotkey_schema)
  writable=$(ride_gsettings writable "$schema" "$key") || ride_die "cannot check iBus hotkey writability"
  [[ "$writable" == true ]] || ride_die "iBus hotkey is locked"
  before=$(ride_ibus_hotkey_observe) || return 1
  if [[ "$before" == user:* ]]; then
    ride_gsettings_valid_snapshot "$before" || ride_die "existing iBus hotkey cannot be safely journaled"
  fi
  if ! ride_ibus_hotkey_write "$state"; then
    ride_ibus_hotkey_write "$before" || ride_error "iBus hotkey rollback failed after write error"
    return 1
  fi
  after=$(ride_ibus_hotkey_observe) || after=unknown
  if [[ "$after" != "$state" ]]; then
    ride_ibus_hotkey_write "$before" || ride_error "iBus hotkey rollback failed after verification error"
    ride_error "iBus hotkey verification failed"
    return 1
  fi
}

ride_user_directories_home() {
  [[ -n "${HOME:-}" && "$HOME" == /* && -d "$HOME" && ! -L "$HOME" ]] ||
    ride_die "user default directories require a real absolute HOME directory"
  printf '%s\n' "$HOME"
}

ride_user_directories_manifest() {
  local home
  home=$(ride_user_directories_home) || return 1
  printf '%s/.local/share/ride-fedora/owned-directories/package.user-default-directories.json\n' "$home"
}

ride_user_directories_check_parent() {
  local home path component
  home=$(ride_user_directories_home) || return 1
  for component in .local .local/share .local/share/ride-fedora \
                   .local/share/ride-fedora/owned-directories; do
    path="$home/$component"
    [[ ! -L "$path" ]] || ride_die "RIDE user-directory state path is a symlink: $path"
    if [[ -e "$path" && ! -d "$path" ]]; then
      ride_die "RIDE user-directory state path is not a directory: $path"
    fi
  done
}

ride_user_default_directories_observe() {
  local home name path all_present=true
  home=$(ride_user_directories_home) || return 1
  for name in bin git; do
    path="$home/$name"
    [[ ! -L "$path" ]] || ride_die "refusing symlink user directory: $path"
    if [[ -e "$path" && ! -d "$path" ]]; then
      ride_die "user default directory path is not a directory: $path"
    fi
    [[ -d "$path" ]] || all_present=false
  done
  if [[ "$all_present" == true ]]; then printf 'installed\n'; else printf 'absent\n'; fi
}

ride_user_default_directories_change() {
  local state=$1 home marker parent name path inode temporary created_json
  local -a created=()
  home=$(ride_user_directories_home) || return 1
  marker=$(ride_user_directories_manifest) || return 1
  parent=${marker%/*}
  ride_user_directories_check_parent || return 1
  case "$state" in
    installed)
      if [[ -e "$marker" || -L "$marker" ]]; then
        [[ ! -L "$marker" ]] || ride_die "RIDE user-directory ownership record is a symlink"
        jq -e 'type == "object" and .schemaVersion == 1 and (.owned | type == "array") and
          all(.owned[]; (.name == "bin" or .name == "git") and (.deviceInode | type == "string"))' \
          "$marker" >/dev/null || ride_die "invalid RIDE user-directory ownership record"
        while IFS=$'\t' read -r name inode; do
          [[ -n "$name" ]] || continue
          path="$home/$name"
          [[ ! -L "$path" && -d "$path" ]] || ride_die "owned user directory is missing or unsafe: $path"
          [[ "$(stat -c '%d:%i' -- "$path")" == "$inode" ]] ||
            ride_die "user directory identity changed; preserving it: $path"
        done < <(jq -r '.owned[] | [.name,.deviceInode] | @tsv' "$marker")
        return 0
      fi
      # Check every target before creating either one, so conflicts are side-effect free.
      for name in bin git; do
        path="$home/$name"
        [[ ! -L "$path" ]] || ride_die "refusing symlink user directory: $path"
        if [[ -e "$path" && ! -d "$path" ]]; then
          ride_die "user default directory path is not a directory: $path"
        fi
      done
      for name in bin git; do
        path="$home/$name"
        if [[ ! -d "$path" ]]; then
          mkdir -m 0755 -- "$path" || ride_die "cannot create user directory: $path"
          created+=("$name")
        fi
      done
      ((${#created[@]})) || return 0
      if [[ -e "$parent" ]]; then
        [[ -d "$parent" && ! -L "$parent" ]] || {
          for name in "${created[@]}"; do rmdir -- "$home/$name" 2>/dev/null || true; done
          ride_die "invalid RIDE user-directory state directory"
        }
      else
        (umask 077; mkdir -p -- "$parent") || {
          for name in "${created[@]}"; do rmdir -- "$home/$name" 2>/dev/null || true; done
          ride_die "cannot create RIDE user-directory state directory"
        }
      fi
      [[ ! -L "$parent" && -d "$parent" ]] || ride_die "invalid RIDE user-directory state directory"
      created_json=$(printf '%s\n' "${created[@]}" | jq -R . | jq -s .) || {
        for name in "${created[@]}"; do rmdir -- "$home/$name" 2>/dev/null || true; done
        ride_die "cannot encode owned user directories"
      }
      local owned_json='[]'
      while IFS= read -r name; do
        [[ -n "$name" ]] || continue
        inode=$(stat -c '%d:%i' -- "$home/$name") || ride_die "cannot inspect created user directory"
        owned_json=$(jq -c --arg name "$name" --arg inode "$inode" '. + [{name:$name,deviceInode:$inode}]' <<< "$owned_json") ||
          ride_die "cannot record created user directory"
      done < <(jq -r '.[]' <<< "$created_json")
      temporary=$(mktemp "$parent/.package.user-default-directories.XXXXXXXX") || {
        for name in "${created[@]}"; do rmdir -- "$home/$name" 2>/dev/null || true; done
        ride_die "cannot stage user-directory ownership record"
      }
      if ! jq -n --argjson owned "$owned_json" '{schemaVersion:1,owned:$owned}' > "$temporary" ||
         ! chmod 0600 -- "$temporary" || ! ln -T -- "$temporary" "$marker"; then
        rm -f -- "$temporary"
        for name in "${created[@]}"; do rmdir -- "$home/$name" 2>/dev/null || true; done
        ride_die "cannot write user-directory ownership record"
      fi
      rm -- "$temporary" || ride_die "cannot remove staged user-directory ownership record"
      ;;
    absent)
      [[ ! -L "$marker" ]] || ride_die "RIDE user-directory ownership record is a symlink"
      [[ -e "$marker" ]] || return 0
      jq -e 'type == "object" and .schemaVersion == 1 and (.owned | type == "array") and
        all(.owned[]; (.name == "bin" or .name == "git") and (.deviceInode | type == "string"))' \
        "$marker" >/dev/null || ride_die "invalid RIDE user-directory ownership record"
      while IFS=$'\t' read -r name inode; do
        [[ -n "$name" ]] || continue
        path="$home/$name"
        [[ ! -L "$path" ]] || ride_die "owned user directory became a symlink: $path"
        [[ -e "$path" ]] || continue
        [[ -d "$path" ]] || ride_die "owned user directory is no longer a directory: $path"
        [[ "$(stat -c '%d:%i' -- "$path")" == "$inode" ]] ||
          ride_die "user directory identity changed; preserving it: $path"
        rmdir -- "$path" || ride_die "preserving nonempty user directory; clean and retry removal: $path"
      done < <(jq -r '.owned[] | [.name,.deviceInode] | @tsv' "$marker")
      rm -f -- "$marker" || ride_die "cannot remove user-directory ownership record"
      ;;
    *) ride_die "invalid user default directory state: $state" ;;
  esac
}

ride_gsettings_string_target() {
  case "$(jq -r '.id' <<< "$1")" in
    setting.gnome-region) printf 'org.gnome.system.locale region /system/locale/region\n' ;;
    setting.gnome-favorite-apps) printf 'org.gnome.shell favorite-apps /org/gnome/shell/favorite-apps\n' ;;
    setting.gnome-window-buttons) printf 'org.gnome.desktop.wm.preferences button-layout /org/gnome/desktop/wm/preferences/button-layout\n' ;;
    *) ride_die "unknown GNOME string operation" ;;
  esac
}

ride_gnome_lock_timing_values() {
  case "$(jq -r '.selectedValue // ""' <<< "$1")" in
    idle-10-lock-5) printf '600 300 true true\n' ;;
    idle-15-lock-5) printf '900 300 true true\n' ;;
    screensaver-enabled) printf '300 - true true\n' ;;
    screensaver-disabled) printf '0 - false false\n' ;;
    *) ride_die "invalid GNOME lock timing selection" ;;
  esac
}

ride_gnome_lock_timing_paths() {
  local entry=${1:-'{}'} selected
  selected=$(jq -r '.selectedValue // ""' <<< "$entry")
  printf '%s\n' \
    'org.gnome.desktop.session idle-delay /org/gnome/desktop/session/idle-delay' \
    'org.gnome.desktop.screensaver idle-activation-enabled /org/gnome/desktop/screensaver/idle-activation-enabled' \
    'org.gnome.desktop.screensaver lock-enabled /org/gnome/desktop/screensaver/lock-enabled'
  [[ "$selected" == screensaver-enabled || "$selected" == screensaver-disabled ]] ||
    printf '%s\n' 'org.gnome.desktop.screensaver lock-delay /org/gnome/desktop/screensaver/lock-delay'
}

ride_gnome_lock_timing_snapshot_valid() {
  local state=$1 encoded raw
  [[ "$state" =~ ^prior:([A-Za-z0-9+/]+={0,2})$ ]] || return 1
  encoded=${state#prior:}
  raw=$(printf '%s' "$encoded" | base64 --decode 2>/dev/null) || return 1
  jq -e '
    type == "object" and
    ((keys | sort) == ["idle-activation-enabled", "idle-delay", "lock-enabled"] or
     (keys | sort) == ["idle-activation-enabled", "idle-delay", "lock-delay", "lock-enabled"]) and
    all(.[]; type == "string" and length <= 64) and
    ((."idle-delay" == "") or
      ((."idle-delay" | test("^uint32 (0|[1-9][0-9]{0,9})$")) and
       ((."idle-delay" | sub("^uint32 "; "") | tonumber) <= 4294967295))) and
    (."idle-activation-enabled" == "" or ."idle-activation-enabled" == "true" or ."idle-activation-enabled" == "false") and
    (."lock-enabled" == "" or ."lock-enabled" == "true" or ."lock-enabled" == "false") and
    ((."lock-delay" == null or ."lock-delay" == "") or
      ((."lock-delay" | test("^uint32 (0|[1-9][0-9]{0,9})$")) and
       ((."lock-delay" | sub("^uint32 "; "") | tonumber) <= 4294967295)))
  ' <<< "$raw" >/dev/null 2>&1
}

ride_gnome_lock_timing_observe() {
  local entry=$1 candidate_entry idle_delay lock_delay activation lock_enabled schema key path value
  local effective_idle effective_activation effective_lock effective_lock_delay snapshot selected
  local -a candidates
  ride_require_command dconf
  ride_require_command base64
  ride_require_command gsettings
  selected=$(jq -r '.selectedValue // ""' <<< "$entry")
  if [[ -n "$selected" ]]; then
    candidates=("$selected")
  else
    candidates=(idle-10-lock-5 idle-15-lock-5 screensaver-enabled screensaver-disabled)
  fi
  effective_idle=$(ride_gsettings get org.gnome.desktop.session idle-delay) || ride_die "cannot observe GNOME idle delay"
  effective_activation=$(ride_gsettings get org.gnome.desktop.screensaver idle-activation-enabled) || ride_die "cannot observe GNOME idle activation"
  effective_lock=$(ride_gsettings get org.gnome.desktop.screensaver lock-enabled) || ride_die "cannot observe GNOME lock setting"
  effective_lock_delay=$(ride_gsettings get org.gnome.desktop.screensaver lock-delay) || ride_die "cannot observe GNOME lock delay"
  for selected in "${candidates[@]}"; do
    candidate_entry=$(jq -c --arg selected "$selected" '. + {selectedValue:$selected}' <<< "$entry") || return 1
    read -r idle_delay lock_delay activation lock_enabled < <(ride_gnome_lock_timing_values "$candidate_entry")
    snapshot='{}'
    while read -r schema key path; do
      value=$(dconf read "$path") || ride_die "cannot observe GNOME lock timing override: $path"
      snapshot=$(jq -c --arg key "$key" --arg value "$value" '. + {($key):$value}' <<< "$snapshot") || return 1
    done < <(ride_gnome_lock_timing_paths "$candidate_entry")
    if [[ "$effective_idle" == "uint32 $idle_delay" &&
          "$effective_activation" == "$activation" && "$effective_lock" == "$lock_enabled" &&
          "$(jq -r '."idle-delay"' <<< "$snapshot")" == "uint32 $idle_delay" &&
          "$(jq -r '."idle-activation-enabled"' <<< "$snapshot")" == "$activation" &&
          "$(jq -r '."lock-enabled"' <<< "$snapshot")" == "$lock_enabled" ]]; then
      if [[ "$lock_delay" != - &&
            ("$effective_lock_delay" != "uint32 $lock_delay" ||
             "$(jq -r '."lock-delay"' <<< "$snapshot")" != "uint32 $lock_delay") ]]; then
        continue
      fi
      printf 'configured\n'
      return 0
    fi
  done
  snapshot='{}'
  while read -r schema key path; do
    value=$(dconf read "$path") || ride_die "cannot observe GNOME lock timing override: $path"
    snapshot=$(jq -c --arg key "$key" --arg value "$value" '. + {($key):$value}' <<< "$snapshot") || return 1
  done < <(ride_gnome_lock_timing_paths "$entry")
  if [[ -z "$(jq -r '[.[] | select(length > 0)] | length' <<< "$snapshot")" ]]; then
    printf 'absent\n'
  else
    printf 'prior:%s\n' "$(printf '%s' "$snapshot" | base64 -w0)"
  fi
}

ride_gnome_lock_timing_write() {
  local entry=$1 state=$2 idle_delay lock_delay activation lock_enabled raw snapshot schema key path value
  case "$state" in
    configured)
      read -r idle_delay lock_delay activation lock_enabled < <(ride_gnome_lock_timing_values "$entry")
      ride_gsettings set org.gnome.desktop.session idle-delay "uint32 $idle_delay" &&
        ride_gsettings set org.gnome.desktop.screensaver idle-activation-enabled "$activation" &&
        ride_gsettings set org.gnome.desktop.screensaver lock-enabled "$lock_enabled" || return 1
      [[ "$lock_delay" == - ]] || ride_gsettings set org.gnome.desktop.screensaver lock-delay "uint32 $lock_delay"
      ;;
    absent) while read -r schema key path; do ride_gsettings reset "$schema" "$key" || return 1; done < <(ride_gnome_lock_timing_paths "$entry") ;;
    prior:*)
      ride_gnome_lock_timing_snapshot_valid "$state" || ride_die "invalid saved GNOME lock timing state"
      raw=$(printf '%s' "${state#prior:}" | base64 --decode) || return 1
      while read -r schema key path; do
        value=$(jq -r --arg key "$key" '.[$key]' <<< "$raw") || return 1
        if [[ -n "$value" ]]; then ride_gsettings set "$schema" "$key" "$value" || return 1
        else ride_gsettings reset "$schema" "$key" || return 1
        fi
      done < <(ride_gnome_lock_timing_paths "$entry")
      ;;
    *) ride_die "invalid GNOME lock timing state" ;;
  esac
}

ride_gnome_lock_timing_change() {
  local entry=$1 state=$2 before after schema key path range writable
  [[ "$state" == configured || "$state" == absent ]] ||
    ride_gnome_lock_timing_snapshot_valid "$state" || ride_die "invalid saved GNOME lock timing state"
  while read -r schema key path; do
    range=$(ride_gsettings range "$schema" "$key") || ride_die "cannot check GNOME lock timing type: $schema $key"
    if [[ "$key" == idle-delay || "$key" == lock-delay ]]; then
      [[ "$range" == 'type u' ]] || ride_die "GNOME lock timing key is not uint32: $schema $key"
    else
      [[ "$range" == 'type b' ]] || ride_die "GNOME lock timing key is not boolean: $schema $key"
    fi
    writable=$(ride_gsettings writable "$schema" "$key") || ride_die "cannot check GNOME lock timing writability: $schema $key"
    [[ "$writable" == true ]] || ride_die "GNOME lock timing key is locked: $schema $key"
  done < <(ride_gnome_lock_timing_paths "$entry")
  before=$(ride_gnome_lock_timing_observe "$entry") || return 1
  if [[ "$before" == prior:* ]]; then
    ride_gnome_lock_timing_snapshot_valid "$before" || ride_die "existing GNOME lock timing cannot be safely journaled"
  fi
  if ! ride_gnome_lock_timing_write "$entry" "$state"; then
    ride_gnome_lock_timing_write "$entry" "$before" || ride_error "GNOME lock timing rollback failed after write error"
    return 1
  fi
  after=$(ride_gnome_lock_timing_observe "$entry") || after=unknown
  if [[ "$after" != "$state" ]]; then
    ride_gnome_lock_timing_write "$entry" "$before" || ride_error "GNOME lock timing rollback failed after verification error"
    ride_error "GNOME lock timing verification failed"
  fi
}

ride_gsettings_favorite_variant() {
  local value=$1
  jq -er --argjson favorites "$value" '
    if ($favorites | length) == 0 then "@as []"
    else "[" + ($favorites | map("\u0027" + . + "\u0027") | join(", ")) + "]" end
  ' <<< '{}' || ride_die "invalid GNOME favorite-app list"
}

ride_gsettings_string_observe() {
  local entry=$1 schema key path selected effective override expected selected_present
  ride_require_command dconf
  ride_require_command base64
  read -r schema key path < <(ride_gsettings_string_target "$entry")
  selected=$(jq -r '.selectedValue // ""' <<< "$entry")
  selected_present=$(jq -r 'has("selectedValue")' <<< "$entry")
  effective=$(ride_gsettings get "$schema" "$key") || ride_die "cannot observe GNOME string setting"
  override=$(dconf read "$path") || ride_die "cannot read GNOME string override"
  if [[ "$(jq -r '.id' <<< "$entry")" == setting.gnome-favorite-apps ]]; then
    if [[ -n "$selected" ]]; then
      expected=$(ride_gsettings_favorite_variant "$selected") || return 1
    else
      expected='__ride_unselected_value__'
    fi
  else
    expected="'$selected'"
  fi
  if [[ "$selected_present" == true && "$effective" == "$expected" && "$override" == "$expected" ]]; then
    printf 'configured\n'
  elif [[ -z "$override" ]]; then
    printf 'absent\n'
  else
    printf 'user:%s\n' "$(printf '%s' "$override" | base64 -w0)"
  fi
}

ride_gsettings_string_write() {
  local entry=$1 state=$2 schema key path selected raw
  read -r schema key path < <(ride_gsettings_string_target "$entry")
  case "$state" in
    configured)
      selected=$(jq -r '.selectedValue // ""' <<< "$entry")
      if [[ "$(jq -r '.id' <<< "$entry")" != setting.gnome-region ||
            "$(jq -r 'has("selectedValue")' <<< "$entry")" != true ]]; then
        [[ -n "$selected" ]] || ride_die "GNOME string setting needs a selected value"
      fi
      if [[ "$(jq -r '.id' <<< "$entry")" == setting.gnome-favorite-apps ]]; then
        ride_gsettings set "$schema" "$key" "$(ride_gsettings_favorite_variant "$selected")"
      else
        ride_gsettings set "$schema" "$key" "'$selected'"
      fi
      ;;
    absent|unset) ride_gsettings reset "$schema" "$key" ;;
    user:*)
      ride_gsettings_valid_snapshot "$state" || ride_die "invalid saved GNOME string value"
      raw=$(printf '%s' "${state#user:}" | base64 --decode) || return 1
      ride_gsettings set "$schema" "$key" "$raw"
      ;;
    *) ride_die "invalid GNOME string state" ;;
  esac
}

ride_gsettings_string_change() {
  local entry=$1 state=$2 schema key path selected range writable before after listed locale_name
  [[ "$state" == configured || "$state" == absent ]] || ride_gsettings_valid_snapshot "$state" ||
    ride_die "invalid saved GNOME string state"
  read -r schema key path < <(ride_gsettings_string_target "$entry")
  range=$(ride_gsettings range "$schema" "$key") || ride_die "cannot check GNOME string type"
  if [[ "$(jq -r '.id' <<< "$entry")" == setting.gnome-favorite-apps ]]; then
    [[ "$range" == 'type as' ]] || ride_die "GNOME setting is not a string list: $schema $key"
  else
    [[ "$range" == 'type s' ]] || ride_die "GNOME setting is not a string: $schema $key"
  fi
  writable=$(ride_gsettings writable "$schema" "$key") || ride_die "cannot check GNOME setting writability"
  [[ "$writable" == true ]] || ride_die "GNOME string setting is locked"
  if [[ "$state" == configured && "$(jq -r '.id' <<< "$entry")" == setting.gnome-region ]]; then
    selected=$(jq -r '.selectedValue' <<< "$entry")
    if [[ -n "$selected" ]]; then
      locale_name=${selected/.UTF-8/.utf8}
      listed=$(LC_ALL=C locale -a) || ride_die "cannot list installed locales"
      grep -Fxiq -- "$locale_name" <<< "$listed" || ride_die "selected GNOME region locale is unavailable: $selected"
    fi
  fi
  before=$(ride_gsettings_string_observe "$entry") || return 1
  if [[ "$before" == user:* ]]; then
    ride_gsettings_valid_snapshot "$before" || ride_die "existing GNOME value cannot be safely journaled"
  fi
  if ! ride_gsettings_string_write "$entry" "$state"; then
    ride_gsettings_string_write "$entry" "$before" || ride_error "GNOME string rollback failed after write error"
    return 1
  fi
  after=$(ride_gsettings_string_observe "$entry") || after=unknown
  if [[ "$after" != "$state" ]]; then
    ride_gsettings_string_write "$entry" "$before" || ride_error "GNOME string rollback failed after verification error"
    ride_error "GNOME string verification failed"
    return 1
  fi
}

ride_gsettings_target() {
  case "$(jq -r '.id' <<< "$1")" in
    setting.gnome-clock-date) printf 'org.gnome.desktop.interface clock-show-date\n' ;;
    setting.gnome-calendar-week-numbers) printf 'org.gnome.desktop.calendar show-weekdate\n' ;;
    setting.gnome-primary-paste) printf 'org.gnome.desktop.interface gtk-enable-primary-paste\n' ;;
    setting.gnome-location) printf 'org.gnome.system.location enabled\n' ;;
    setting.gnome-problem-reporting) printf 'org.gnome.desktop.privacy report-technical-problems\n' ;;
    *) ride_die "unknown GNOME boolean operation" ;;
  esac
}

ride_gnome_shortcuts_owner_file() {
  printf '%s/ride-fedora/owned/setting.gnome-custom-shortcuts.json\n' "${XDG_DATA_HOME:-$HOME/.local/share}"
}

ride_gnome_shortcuts_global_target() {
  case "$1" in
    showDesktop) printf 'org.gnome.desktop.wm.keybindings show-desktop\n' ;;
    switchWindows) printf 'org.gnome.desktop.wm.keybindings switch-windows\n' ;;
    *) ride_die "unknown RIDE GNOME shortcut setting" ;;
  esac
}

ride_gnome_shortcuts_variant() {
  local value=$1
  jq -er --argjson values "$value" '
    "[" + ($values | map("\u0027" + . + "\u0027") | join(", ")) + "]"
  ' <<< '{}' || ride_die "invalid GNOME shortcut list"
}

ride_gnome_shortcuts_read_array() {
  local schema=$1 key=$2 raw tokens remainder
  raw=$(ride_gsettings get "$schema" "$key") || ride_die "cannot read GNOME shortcut setting: $key"
  [[ "$raw" =~ ^(@as[[:space:]]+)?\[.*\]$ ]] || ride_die "unexpected GNOME shortcut list format: $key"
  tokens=$(grep -oE "'[^']*'" <<< "$raw" | sed "s/^'//;s/'$//" || true)
  remainder=$(sed -E "s/'[^']*'//g" <<< "$raw" | tr -d ' @as,[]')
  [[ -z "$remainder" ]] || ride_die "unsafe GNOME shortcut list value: $key"
  printf '%s\n' "$tokens" | jq -Rsc 'split("\n") | map(select(length > 0))'
}

ride_gnome_shortcuts_write_array() {
  local schema=$1 key=$2 values=$3
  ride_gsettings set "$schema" "$key" "$(ride_gnome_shortcuts_variant "$values")"
}

ride_gnome_shortcuts_path() {
  local shortcut=$1 digest
  digest=$(printf '%s' "$shortcut" | sha256sum); digest=${digest%% *}
  printf '/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/ridefedora-%s/\n' "${digest:0:16}"
}

ride_gnome_custom_shortcuts_global_owned() {
  local entry=$1 key config current desired initial owned='{}'
  config=$(jq -r '.selectedValue' <<< "$entry")
  for key in showDesktop switchWindows; do
    local schema setting
    read -r schema setting < <(ride_gnome_shortcuts_global_target "$key")
    current=$(ride_gnome_shortcuts_read_array "$schema" "$setting") || return 1
    desired=$(jq -c --arg key "$key" '.global[$key]' <<< "$config") || return 1
    [[ "$desired" != null ]] || ride_die "missing GNOME shortcut global list: $key"
    initial=$(jq -c --argjson current "$current" --argjson desired "$desired" \
      '$desired | map(select(. as $item | ($current | index($item)) == null))' <<< '{}' ) || return 1
    owned=$(jq -c --arg key "$key" --argjson values "$initial" '. + {($key):$values}' <<< "$owned") || return 1
  done
  printf '%s\n' "$owned"
}

ride_gnome_custom_shortcuts_specs() {
  local entry=$1 config index shortcut path
  config=$(jq -r '.selectedValue' <<< "$entry")
  index=0
  while IFS= read -r shortcut; do
    path=$(ride_gnome_shortcuts_path "$shortcut")
    jq -nc --arg path "$path" --argjson shortcut "$shortcut" '$shortcut + {path:$path}'
    ((index+=1))
  done < <(jq -c '.shortcuts[]' <<< "$config")
  ((index > 0)) || ride_die "no GNOME custom shortcuts selected"
}

ride_gnome_custom_shortcuts_validate_owner() {
  local entry=$1 owner config_hash expected current paths item path name command binding schema
  local expected_entries actual_entries expected_global_owned actual_global_owned old_global
  owner=$(ride_gnome_shortcuts_owner_file)
  [[ -f "$owner" && ! -L "$owner" ]] || ride_die "GNOME shortcut ownership record is missing or unsafe"
  [[ -O "$owner" && "$(stat -c '%a' -- "$owner")" == 600 ]] ||
    ride_die "GNOME shortcut ownership record has unsafe owner or permissions"
  jq -e '.schemaVersion == 1 and (.entries | type == "array" and length > 0) and
    (.globalOwned.showDesktop | type == "array") and (.globalOwned.switchWindows | type == "array") and
    (.oldGlobal.showDesktop | type == "array") and (.oldGlobal.switchWindows | type == "array") and
    (.originalPaths | type == "array") and (.configSha256 | test("^[0-9a-f]{64}$"))' "$owner" >/dev/null ||
    ride_die "invalid GNOME shortcut ownership record"
  config=$(jq -r '.selectedValue' <<< "$entry")
  config_hash=$(jq -cS . <<< "$config" | sha256sum); config_hash=${config_hash%% *}
  expected=$(jq -r '.configSha256' "$owner")
  [[ "$config_hash" == "$expected" ]] || ride_die "GNOME shortcut configuration changed; restore or remove the existing profile first"
  jq -e --argjson config "$config" '.global == $config.global' "$owner" >/dev/null ||
    ride_die "GNOME shortcut ownership record does not match its selected global settings"
  expected_entries=$(ride_gnome_custom_shortcuts_specs "$entry" | jq -s 'sort_by(.path)')
  actual_entries=$(jq -cS '.entries | sort_by(.path)' "$owner")
  expected_entries=$(jq -cS 'sort_by(.path)' <<< "$expected_entries")
  [[ "$actual_entries" == "$expected_entries" ]] || ride_die "GNOME shortcut ownership record does not match the selected entries"
  old_global=$(jq -c '.oldGlobal' "$owner")
  expected_global_owned=$(jq -nc --argjson prior "$old_global" --argjson config "$config" '{
    showDesktop: ($config.global.showDesktop | map(select(. as $item | ($prior.showDesktop | index($item)) == null))),
    switchWindows: ($config.global.switchWindows | map(select(. as $item | ($prior.switchWindows | index($item)) == null)))
  }')
  actual_global_owned=$(jq -cS '.globalOwned' "$owner")
  expected_global_owned=$(jq -cS . <<< "$expected_global_owned")
  [[ "$actual_global_owned" == "$expected_global_owned" ]] || ride_die "GNOME shortcut ownership record has inconsistent prior-state data"
  paths=$(ride_gnome_shortcuts_read_array org.gnome.settings-daemon.plugins.media-keys custom-keybindings)
  while IFS=$'\t' read -r path name command binding; do
    [[ -n "$path" ]] || continue
    jq -e --arg path "$path" --argjson paths "$paths" '$paths | index($path) != null' <<< '{}' >/dev/null 2>&1 ||
      ride_die "RIDE GNOME shortcut path was removed from the active list: $path"
    item="org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$path"
    [[ "$(ride_gsettings get "$item" name)" == "'$name'" &&
       "$(ride_gsettings get "$item" command)" == "'$command'" &&
       "$(ride_gsettings get "$item" binding)" == "'$binding'" ]] ||
      ride_die "RIDE GNOME shortcut was changed outside RIDE; preserving it: $path"
  done < <(jq -r '.entries[] | [.path,.name,.command,.binding] | @tsv' "$owner")
  for name in showDesktop switchWindows; do
    local target_schema target_key owned current desired
    read -r target_schema target_key < <(ride_gnome_shortcuts_global_target "$name")
    owned=$(jq -c --arg key "$name" '.globalOwned[$key]' "$owner")
    current=$(ride_gnome_shortcuts_read_array "$target_schema" "$target_key")
    desired=$(jq -c --arg key "$name" '.global[$key]' <<< "$config")
    jq -e --argjson current "$current" --argjson desired "$desired" \
      'all($desired[]; . as $item | ($current | index($item)) != null)' <<< '{}' >/dev/null ||
      ride_die "RIDE GNOME global shortcut changed; preserving current value: $name"
    [[ "$owned" != null ]] || ride_die "invalid owned global shortcut state: $name"
  done
}

ride_gnome_custom_shortcuts_observe() {
  local entry=$1 owner path config_hash config
  owner=$(ride_gnome_shortcuts_owner_file)
  if [[ -e "$owner" || -L "$owner" ]]; then
    [[ ! -L "$owner" ]] || ride_die "GNOME shortcut ownership record is a symlink"
    if [[ -z "$(jq -r '.selectedValue // ""' <<< "$entry")" ]]; then
      config=$(jq -c '{global:.global,shortcuts:[.entries[] | del(.path)]}' "$owner")
      entry=$(jq -c --arg value "$config" '. + {selectedValue:$value}' <<< "$entry")
    fi
    ride_gnome_custom_shortcuts_validate_owner "$entry"
    printf 'configured\n'
    return 0
  fi
  config=$(jq -r '.selectedValue' <<< "$entry")
  config_hash=$(jq -cS . <<< "$config" | sha256sum); config_hash=${config_hash%% *}
  while IFS= read -r path; do
    [[ -n "$path" ]] || continue
    local listed
    listed=$(ride_gnome_shortcuts_read_array org.gnome.settings-daemon.plugins.media-keys custom-keybindings)
    jq -e --arg path "$path" --argjson listed "$listed" '$listed | index($path) != null' <<< '{}' >/dev/null &&
      ride_die "unowned GNOME shortcut path conflicts with RIDE configuration: $path"
  done < <(ride_gnome_custom_shortcuts_specs "$entry" | jq -r '.path')
  : "$config_hash"
  printf 'absent\n'
}

ride_gnome_custom_shortcuts_rollback_remove() {
  local owner=$1 paths=$2 globals=$3 item path name command binding key schema setting value
  while IFS=$'\t' read -r path name command binding; do
    [[ -n "$path" ]] || continue
    item="org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$path"
    ride_gsettings set "$item" name "'$name'" || true
    ride_gsettings set "$item" command "'$command'" || true
    ride_gsettings set "$item" binding "'$binding'" || true
  done < <(jq -r '.entries[] | [.path,.name,.command,.binding] | @tsv' "$owner")
  for key in showDesktop switchWindows; do
    read -r schema setting < <(ride_gnome_shortcuts_global_target "$key")
    value=$(jq -c --arg key "$key" '.[$key]' <<< "$globals")
    ride_gnome_shortcuts_write_array "$schema" "$setting" "$value" || true
  done
  ride_gnome_shortcuts_write_array org.gnome.settings-daemon.plugins.media-keys custom-keybindings "$paths" || true
}

ride_gnome_custom_shortcuts_rollback() {
  local original_paths=$1 old_global=$2 entries=$3 path item key schema setting value
  for key in showDesktop switchWindows; do
    read -r schema setting < <(ride_gnome_shortcuts_global_target "$key")
    value=$(jq -c --arg key "$key" '.[$key] // []' <<< "$old_global")
    ride_gnome_shortcuts_write_array "$schema" "$setting" "$value" || true
  done
  while IFS= read -r path; do
    [[ -n "$path" ]] || continue
    item="org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$path"
    for key in name command binding; do ride_gsettings reset "$item" "$key" >/dev/null 2>&1 || true; done
  done < <(jq -r '.[].path' <<< "$entries")
  ride_gnome_shortcuts_write_array org.gnome.settings-daemon.plugins.media-keys custom-keybindings "$original_paths" || true
}

ride_gnome_custom_shortcuts_change() {
  local entry=$1 state=$2 owner config config_hash paths original_paths path item name command binding raw_list new_list old_global owned_global spec_json='[]'
  local schema key current desired add updated temporary
  owner=$(ride_gnome_shortcuts_owner_file)
  case "$state" in
    configured)
      [[ ! -e "$owner" && ! -L "$owner" ]] || { ride_gnome_custom_shortcuts_validate_owner "$entry"; return 0; }
      config=$(jq -r '.selectedValue' <<< "$entry")
      config_hash=$(jq -cS . <<< "$config" | sha256sum); config_hash=${config_hash%% *}
      paths=$(ride_gnome_shortcuts_read_array org.gnome.settings-daemon.plugins.media-keys custom-keybindings)
      original_paths=$paths
      [[ "$(ride_gsettings writable org.gnome.settings-daemon.plugins.media-keys custom-keybindings)" == true ]] ||
        ride_die "GNOME custom shortcut list is locked"
      while IFS= read -r spec; do
        [[ -n "$spec" ]] || continue
        path=$(jq -r '.path' <<< "$spec"); name=$(jq -r '.name' <<< "$spec")
        command=$(jq -r '.command' <<< "$spec"); binding=$(jq -r '.binding' <<< "$spec")
        jq -e --arg path "$path" --argjson paths "$paths" '$paths | index($path) == null' <<< '{}' >/dev/null ||
          ride_die "custom shortcut path already exists; preserving it: $path"
        item="org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$path"
        for key in name command binding; do
          [[ "$(ride_gsettings get "$item" "$key")" == "''" ]] || ride_die "custom shortcut slot contains unowned data: $path"
          [[ "$(ride_gsettings writable "$item" "$key")" == true ]] || ride_die "custom shortcut slot is locked: $path"
        done
        spec_json=$(jq -c --argjson spec "$spec" '. + [$spec]' <<< "$spec_json")
      done < <(ride_gnome_custom_shortcuts_specs "$entry")
      old_global='{}'; owned_global=$(ride_gnome_custom_shortcuts_global_owned "$entry")
      for key in showDesktop switchWindows; do
        read -r schema binding < <(ride_gnome_shortcuts_global_target "$key")
        [[ "$(ride_gsettings range "$schema" "$binding")" == 'type as' ]] || ride_die "GNOME global shortcut setting is not a string list: $key"
        [[ "$(ride_gsettings writable "$schema" "$binding")" == true ]] || ride_die "GNOME global shortcut setting is locked: $key"
        current=$(ride_gnome_shortcuts_read_array "$schema" "$binding")
        old_global=$(jq -c --arg key "$key" --argjson value "$current" '. + {($key):$value}' <<< "$old_global")
      done
      for key in showDesktop switchWindows; do
        read -r schema binding < <(ride_gnome_shortcuts_global_target "$key")
        current=$(jq -c --arg key "$key" '.[$key]' <<< "$old_global")
        desired=$(jq -c --arg key "$key" '.global[$key]' <<< "$config")
        add=$(jq -c --argjson current "$current" --argjson desired "$desired" '$current + ($desired | map(select(. as $item | ($current | index($item)) == null)))' <<< '{}')
        ride_gnome_shortcuts_write_array "$schema" "$binding" "$add" || { ride_gnome_custom_shortcuts_rollback "$original_paths" "$old_global" "$spec_json"; ride_die "cannot apply GNOME global shortcut list: $key"; }
      done
      while IFS=$'\t' read -r path name command binding; do
        [[ -n "$path" ]] || continue
        item="org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$path"
        ride_gsettings set "$item" name "'$name'" || { ride_gnome_custom_shortcuts_rollback "$original_paths" "$old_global" "$spec_json"; ride_die "cannot write custom shortcut name: $path"; }
        ride_gsettings set "$item" command "'$command'" || { ride_gnome_custom_shortcuts_rollback "$original_paths" "$old_global" "$spec_json"; ride_die "cannot write custom shortcut command: $path"; }
        ride_gsettings set "$item" binding "'$binding'" || { ride_gnome_custom_shortcuts_rollback "$original_paths" "$old_global" "$spec_json"; ride_die "cannot write custom shortcut binding: $path"; }
        paths=$(jq -c --arg path "$path" '. + [$path]' <<< "$paths")
      done < <(jq -r '.entries[] | [.path,.name,.command,.binding] | @tsv' <<< "$(jq -nc --argjson entries "$spec_json" '{entries:$entries}')")
      ride_gnome_shortcuts_write_array org.gnome.settings-daemon.plugins.media-keys custom-keybindings "$paths" || { ride_gnome_custom_shortcuts_rollback "$original_paths" "$old_global" "$spec_json"; ride_die "cannot register custom GNOME shortcuts"; }
      [[ ! -L "${owner%/*}" ]] || { ride_gnome_custom_shortcuts_rollback "$original_paths" "$old_global" "$spec_json"; ride_die "GNOME shortcut ownership directory is a symlink"; }
      if [[ -e "${owner%/*}" && ! -d "${owner%/*}" ]]; then
        ride_gnome_custom_shortcuts_rollback "$original_paths" "$old_global" "$spec_json"
        ride_die "GNOME shortcut ownership path is not a directory"
      fi
      mkdir -p -m 0700 "${owner%/*}" || { ride_gnome_custom_shortcuts_rollback "$original_paths" "$old_global" "$spec_json"; ride_die "cannot create GNOME shortcut ownership directory"; }
      temporary=$(mktemp "${owner%/*}/.shortcuts.XXXXXXXX") || { ride_gnome_custom_shortcuts_rollback "$original_paths" "$old_global" "$spec_json"; ride_die "cannot stage GNOME shortcut ownership record"; }
      jq -n --arg hash "$config_hash" --argjson entries "$spec_json" --argjson config "$config" --argjson oldGlobal "$old_global" --argjson globalOwned "$owned_global" --argjson originalPaths "$original_paths" \
        '{schemaVersion:1,configSha256:$hash,entries:$entries,global:$config.global,oldGlobal:$oldGlobal,globalOwned:$globalOwned,originalPaths:$originalPaths}' > "$temporary" || { rm -f "$temporary"; ride_gnome_custom_shortcuts_rollback "$original_paths" "$old_global" "$spec_json"; ride_die "cannot write GNOME shortcut ownership record"; }
      chmod 0600 "$temporary" && mv -f -- "$temporary" "$owner" || { rm -f "$temporary"; ride_gnome_custom_shortcuts_rollback "$original_paths" "$old_global" "$spec_json"; ride_die "cannot install GNOME shortcut ownership record"; }
      ;;
    absent)
      [[ -f "$owner" && ! -L "$owner" ]] || return 0
      ride_gnome_custom_shortcuts_validate_owner "$entry"
      paths=$(ride_gnome_shortcuts_read_array org.gnome.settings-daemon.plugins.media-keys custom-keybindings)
      raw_list=$paths; old_global='{}'
      for key in showDesktop switchWindows; do
        read -r schema binding < <(ride_gnome_shortcuts_global_target "$key")
        [[ "$(ride_gsettings writable "$schema" "$binding")" == true ]] || ride_die "GNOME global shortcut setting is locked: $key"
        current=$(ride_gnome_shortcuts_read_array "$schema" "$binding")
        old_global=$(jq -c --arg key "$key" --argjson value "$current" '. + {($key):$value}' <<< "$old_global")
      done
      while IFS= read -r path; do [[ -n "$path" ]] && paths=$(jq -c --arg path "$path" 'map(select(. != $path))' <<< "$paths"); done < <(jq -r '.entries[].path' "$owner")
      for key in showDesktop switchWindows; do
        read -r schema binding < <(ride_gnome_shortcuts_global_target "$key")
        current=$(ride_gnome_shortcuts_read_array "$schema" "$binding")
        owned=$(jq -c --arg key "$key" '.globalOwned[$key]' "$owner")
        updated=$(jq -c --argjson current "$current" --argjson owned "$owned" '$current | map(select(. as $item | ($owned | index($item)) == null))' <<< '{}')
        ride_gnome_shortcuts_write_array "$schema" "$binding" "$updated" || { ride_gnome_custom_shortcuts_rollback_remove "$owner" "$raw_list" "$old_global"; ride_die "cannot restore GNOME shortcut list: $key"; }
      done
      ride_gnome_shortcuts_write_array org.gnome.settings-daemon.plugins.media-keys custom-keybindings "$paths" || { ride_gnome_custom_shortcuts_rollback_remove "$owner" "$raw_list" "$old_global"; ride_die "cannot unregister RIDE GNOME shortcuts"; }
      while IFS= read -r path; do [[ -n "$path" ]] || continue; item="org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$path"; for key in name command binding; do ride_gsettings reset "$item" "$key" || { ride_gnome_custom_shortcuts_rollback_remove "$owner" "$raw_list" "$old_global"; ride_die "cannot clear owned shortcut slot: $path"; }; done; done < <(jq -r '.entries[].path' "$owner")
      rm -f -- "$owner" || { ride_gnome_custom_shortcuts_rollback_remove "$owner" "$raw_list" "$old_global"; ride_die "cannot remove GNOME shortcut ownership record"; }
      ;;
    *) ride_die "invalid GNOME custom shortcut state: $state" ;;
  esac
}

ride_gsettings() {
  ride_require_command gsettings
  if [[ -n "${DBUS_SESSION_BUS_ADDRESS:-}" ]]; then
    gsettings "$@"
  elif [[ -S "/run/user/$UID/bus" ]]; then
    DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$UID/bus" gsettings "$@"
  else
    ride_require_command dbus-run-session
    dbus-run-session -- gsettings "$@"
  fi
}

ride_volatility_environment() {
  printf '%s\n' "${XDG_DATA_HOME:-$HOME/.local/share}/ride-fedora/tools/volatility3"
}

ride_volatility2_environment() {
  printf '%s\n' "${XDG_DATA_HOME:-$HOME/.local/share}/ride-fedora/tools/volatility2"
}

ride_observe_volatility2() {
  local entry=$1 environment version source_sha runtime_sha marker
  environment=$(ride_volatility2_environment)
  version=$(jq -r '.version' <<< "$entry")
  source_sha=$(jq -r '.sourceSha512Hex' <<< "$entry")
  runtime_sha=$(jq -r '.runtimeSha256' <<< "$entry")
  marker="$environment/.ride-owned"
  if [[ ! -e "$environment" && ! -L "$environment" ]]; then
    printf 'absent\n'; return
  fi
  [[ -d "$environment" && ! -L "$environment" && -f "$marker" && ! -L "$marker" &&
     -x "$environment/runtime/bin/pypy" && -f "$environment/source/vol.py" &&
     -x "$environment/bin/vol2" &&
     "$(cat -- "$marker")" == "ride-fedora package.volatility2 $version $source_sha $runtime_sha" ]] || {
    printf 'unowned\n'; return;
  }
  [[ "$(stat -c '%u:%g' -- "$environment")" == "$(id -u):$(id -g)" ]] || {
    printf 'unowned\n'; return;
  }
  printf 'installed\n'
}

ride_change_volatility2() {
  local entry=$1 state=$2 environment parent temporary source_uri runtime_uri
  local source_sha runtime_sha version extracted_name
  environment=$(ride_volatility2_environment)
  parent=$(dirname -- "$environment")
  source_uri=$(jq -r '.sourceUri' <<< "$entry")
  runtime_uri=$(jq -r '.runtimeUri' <<< "$entry")
  source_sha=$(jq -r '.sourceSha512Hex' <<< "$entry")
  runtime_sha=$(jq -r '.runtimeSha256' <<< "$entry")
  version=$(jq -r '.version' <<< "$entry")
  case "$state" in
    installed)
      [[ "$(ride_observe_volatility2 "$entry")" == absent ]] || {
        [[ "$(ride_observe_volatility2 "$entry")" == installed ]] && return 0
        ride_die "Volatility 2 destination exists or is not owned: $environment"
      }
      local check_parent
      for check_parent in "$HOME" "$HOME/.local" "${XDG_DATA_HOME:-$HOME/.local/share}" \
        "${XDG_DATA_HOME:-$HOME/.local/share}/ride-fedora" "$parent"; do
        [[ ! -L "$check_parent" ]] || ride_die "Volatility 2 parent is a symlink: $check_parent"
      done
      ride_require_command curl; ride_require_command sha256sum; ride_require_command sha512sum; ride_require_command tar
      temporary=$(mktemp -d "${TMPDIR:-/tmp}/ride-volatility2.XXXXXXXX") || return 1
      mkdir -m 0700 "$temporary/source" "$temporary/runtime" || { rm -rf -- "$temporary"; return 1; }
      if ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 300 --max-filesize 8000000 "$source_uri" -o "$temporary/source.tar.gz" ||
         ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 300 --max-filesize 40000000 "$runtime_uri" -o "$temporary/runtime.tar.gz" ||
         [[ "$(sha512sum "$temporary/source.tar.gz" | cut -d' ' -f1)" != "$source_sha" ]] ||
         [[ "$(sha256sum "$temporary/runtime.tar.gz" | cut -d' ' -f1)" != "$runtime_sha" ]]; then
        rm -rf -- "$temporary"
        ride_die "Volatility 2 source or PyPy archive download/checksum failed"
      fi
      local archive_name
      for archive_name in "$temporary/source.tar.gz" "$temporary/runtime.tar.gz"; do
        if ! tar -tzf "$archive_name" | awk 'BEGIN {ok=1} /^\// || /(^|\/)\.\.(\/|$)/ {ok=0} END {exit !ok}'; then
          rm -rf -- "$temporary"
          ride_die "Volatility 2 archive contains an unsafe path"
        fi
      done
      tar -xzf "$temporary/source.tar.gz" --strip-components=1 --no-same-owner -C "$temporary/source" || {
        rm -rf -- "$temporary"; return 1;
      }
      tar -xzf "$temporary/runtime.tar.gz" --strip-components=1 --no-same-owner -C "$temporary/runtime" || {
        rm -rf -- "$temporary"; return 1;
      }
      [[ -f "$temporary/source/vol.py" && -x "$temporary/runtime/bin/pypy" ]] || {
        rm -rf -- "$temporary"; ride_die "Volatility 2 bundle is missing its expected CLI or runtime"
      }
      "$temporary/runtime/bin/pypy" --version 2>&1 | grep -q 'Python 2\.7' || {
        rm -rf -- "$temporary"; ride_die "pinned PyPy archive did not provide Python 2.7"
      }
      if ! "$temporary/runtime/bin/pypy" "$temporary/source/vol.py" --info >"$temporary/info.txt" 2>&1 ||
         ! grep -q 'Volatility Foundation Volatility Framework 2\.6\.1' "$temporary/info.txt"; then
        cat "$temporary/info.txt" >&2
        rm -rf -- "$temporary"
        ride_die "Volatility 2 core --info check failed"
      fi
      mkdir -p -- "$parent" || { rm -rf -- "$temporary"; return 1; }
      [[ ! -e "$environment" && ! -L "$environment" ]] || {
        rm -rf -- "$temporary"; ride_die "Volatility 2 destination appeared during installation"
      }
      mv -- "$temporary/source" "$temporary/bundle-source"
      mv -- "$temporary/runtime" "$temporary/bundle-runtime"
      mkdir -p "$temporary/bundle/bin"
      mv -- "$temporary/bundle-source" "$temporary/bundle/source"
      mv -- "$temporary/bundle-runtime" "$temporary/bundle/runtime"
      cat > "$temporary/bundle/bin/vol2" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
bundle_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
exec "$bundle_dir/runtime/bin/pypy" "$bundle_dir/source/vol.py" "$@"
EOF
      chmod 0755 "$temporary/bundle/bin/vol2"
      printf 'ride-fedora package.volatility2 %s %s %s\n' "$version" "$source_sha" "$runtime_sha" > "$temporary/bundle/.ride-owned"
      chmod 0600 "$temporary/bundle/.ride-owned"
      mv -- "$temporary/bundle" "$environment" || { rm -rf -- "$temporary"; return 1; }
      rm -rf -- "$temporary"
      ;;
    absent)
      case "$(ride_observe_volatility2 "$entry")" in
        absent) return 0 ;;
        installed) rm -rf -- "$environment" ;;
        *) ride_die "refusing to remove unowned Volatility 2 files: $environment" ;;
      esac
      ;;
    *) ride_die "invalid Volatility 2 bundle state: $state" ;;
  esac
}

ride_unfurl_environment() {
  printf '%s\n' "${XDG_DATA_HOME:-$HOME/.local/share}/ride-fedora/tools/dfir-unfurl"
}

ride_chepy_environment() {
  printf '%s\n' "${XDG_DATA_HOME:-$HOME/.local/share}/ride-fedora/tools/chepy"
}

ride_chepy_link() {
  printf '%s\n' "$HOME/.local/bin/chepy"
}

ride_chepy_owned_contents() {
  local environment=$1
  [[ "$(find "$environment" -mindepth 1 -maxdepth 1 -printf '%f\n' | LC_ALL=C sort)" == \
    $'.ride-owned\nchepy-7.6.0.tar.gz\ndependencies.txt\nvenv' ]]
}

ride_observe_chepy() {
  local entry=$1 environment link source_sha marker
  environment=$(ride_chepy_environment)
  link=$(ride_chepy_link)
  source_sha=$(jq -r '.sourceSha256' <<< "$entry")
  marker="ride-fedora package.chepy 7.6.0 $source_sha"
  if [[ -d "$environment" && ! -L "$environment" ]] &&
     ride_chepy_owned_contents "$environment" &&
     [[ -f "$environment/.ride-owned" && ! -L "$environment/.ride-owned" &&
        "$(cat "$environment/.ride-owned")" == "$marker" &&
        -f "$environment/chepy-7.6.0.tar.gz" && ! -L "$environment/chepy-7.6.0.tar.gz" &&
        "$(sha256sum -- "$environment/chepy-7.6.0.tar.gz" | cut -d' ' -f1)" == "$source_sha" &&
        -f "$environment/dependencies.txt" && ! -L "$environment/dependencies.txt" &&
        -x "$environment/venv/bin/python" && -x "$environment/venv/bin/chepy" &&
        -L "$link" && "$(readlink -- "$link")" == "$environment/venv/bin/chepy" ]] &&
     "$environment/venv/bin/python" -c 'import importlib.metadata as m; assert m.version("chepy") == "7.6.0"; import chepy' >/dev/null 2>&1; then
    printf 'installed\n'
  else
    printf 'absent\n'
  fi
}

ride_change_chepy() {
  local entry=$1 state=$2 environment link base source_uri source_sha marker
  environment=$(ride_chepy_environment)
  link=$(ride_chepy_link)
  base=$(dirname "$environment")
  source_uri=$(jq -r '.sourceUri' <<< "$entry")
  source_sha=$(jq -r '.sourceSha256' <<< "$entry")
  marker="ride-fedora package.chepy 7.6.0 $source_sha"
  case "$state" in
    installed)
      ride_require_command python3.12
      ride_require_command curl
      ride_require_command sha256sum
      if [[ -e "$environment" || -L "$environment" || -e "$link" || -L "$link" ]]; then
        ride_die "Chepy destination already exists; refusing to overwrite"
      fi
      umask 077
      mkdir -p "$base" "$(dirname "$link")"
      mkdir "$environment" || ride_die "cannot create isolated Chepy destination"
      if ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 90 --max-filesize 200000 \
          "$source_uri" -o "$environment/chepy-7.6.0.tar.gz"; then
        rm -rf -- "$environment"
        return 1
      fi
      if [[ "$(sha256sum -- "$environment/chepy-7.6.0.tar.gz" | cut -d' ' -f1)" != "$source_sha" ]]; then
        rm -rf -- "$environment"
        ride_error "Chepy source digest verification failed"
        return 1
      fi
      if ! python3.12 -m venv "$environment/venv"; then
        rm -rf -- "$environment"
        return 1
      fi
      if ! PIP_NO_INPUT=1 "$environment/venv/bin/python" -m pip --isolated install \
          --disable-pip-version-check --index-url https://pypi.org/simple \
          "$environment/chepy-7.6.0.tar.gz"; then
        rm -rf -- "$environment"
        return 1
      fi
      if [[ ! -x "$environment/venv/bin/chepy" ]] ||
         ! "$environment/venv/bin/python" -c 'import importlib.metadata as m; assert m.version("chepy") == "7.6.0"; import chepy' >/dev/null 2>&1; then
        rm -rf -- "$environment"
        ride_error "Chepy CLI or import verification failed"
        return 1
      fi
      if ! "$environment/venv/bin/python" -m pip --isolated freeze --all > "$environment/dependencies.txt"; then
        rm -rf -- "$environment"
        return 1
      fi
      printf '%s\n' "$marker" > "$environment/.ride-owned"
      if ! ln -s -- "$environment/venv/bin/chepy" "$link"; then
        rm -rf -- "$environment"
        return 1
      fi
      ;;
    absent)
      if [[ -e "$environment" || -L "$environment" || -e "$link" || -L "$link" ]]; then
        if ! { [[ -d "$environment" && ! -L "$environment" ]] &&
               ride_chepy_owned_contents "$environment" &&
               [[ -f "$environment/.ride-owned" && ! -L "$environment/.ride-owned" &&
                  "$(cat "$environment/.ride-owned")" == "$marker" &&
                  -f "$environment/chepy-7.6.0.tar.gz" && ! -L "$environment/chepy-7.6.0.tar.gz" &&
                  "$(sha256sum -- "$environment/chepy-7.6.0.tar.gz" | cut -d' ' -f1)" == "$source_sha" &&
                  -L "$link" && "$(readlink -- "$link")" == "$environment/venv/bin/chepy" ]]; }; then
          ride_die "refusing to remove modified or unowned Chepy files"
        fi
        rm -- "$link"
        rm -rf -- "$environment"
      fi
      ;;
    *) ride_die "invalid Chepy state: $state" ;;
  esac
}

ride_browser_forensic_environment() {
  printf '%s\n' "${XDG_DATA_HOME:-$HOME/.local/share}/ride-fedora/tools/browser-forensic"
}

ride_browser_forensic_link() {
  printf '%s\n' "$HOME/.local/bin/br4n6"
}

ride_browser_forensic_owned_contents() {
  local environment=$1
  [[ "$(find "$environment" -mindepth 1 -maxdepth 1 -printf '%f\n' | LC_ALL=C sort)" == \
    $'.ride-owned\nbr4n6\nbrowser-forensic-10e2f70.tar.gz' ]]
}

ride_browser_forensic_marker() {
  local environment=$1 source_sha=$2 binary_sha
  [[ -d "$environment" && ! -L "$environment" && -f "$environment/br4n6" &&
     ! -L "$environment/br4n6" && -x "$environment/br4n6" ]] || return 1
  binary_sha=$(sha256sum -- "$environment/br4n6" | cut -d' ' -f1)
  printf 'ride-fedora package.browser-forensic 0.3.0 %s %s\n' "$source_sha" "$binary_sha"
}

ride_observe_browser_forensic() {
  local entry=$1 environment link source_sha marker
  environment=$(ride_browser_forensic_environment)
  link=$(ride_browser_forensic_link)
  source_sha=$(jq -r '.sourceSha256' <<< "$entry")
  marker=$(ride_browser_forensic_marker "$environment" "$source_sha" 2>/dev/null) || {
    printf 'absent\n'
    return 0
  }
  if [[ -d "$environment" && ! -L "$environment" ]] &&
     ride_browser_forensic_owned_contents "$environment" &&
     [[ -f "$environment/.ride-owned" && ! -L "$environment/.ride-owned" &&
        "$(cat "$environment/.ride-owned")" == "$marker" &&
        -f "$environment/browser-forensic-10e2f70.tar.gz" && ! -L "$environment/browser-forensic-10e2f70.tar.gz" &&
        "$(sha256sum -- "$environment/browser-forensic-10e2f70.tar.gz" | cut -d' ' -f1)" == "$source_sha" &&
        -x "$environment/br4n6" && -L "$link" && "$(readlink -- "$link")" == "$environment/br4n6" ]] &&
     "$environment/br4n6" --version >/dev/null 2>&1; then
    printf 'installed\n'
  else
    printf 'absent\n'
  fi
}

ride_change_browser_forensic() {
  local entry=$1 state=$2 environment link base source_uri source_sha marker
  local build_dir archive extracted_binary
  environment=$(ride_browser_forensic_environment)
  link=$(ride_browser_forensic_link)
  base=$(dirname "$environment")
  source_uri=$(jq -r '.sourceUri' <<< "$entry")
  source_sha=$(jq -r '.sourceSha256' <<< "$entry")
  case "$state" in
    installed)
      ride_require_command cargo
      ride_require_command rustc
      ride_require_command curl
      ride_require_command sha256sum
      if [[ -e "$environment" || -L "$environment" || -e "$link" || -L "$link" ]]; then
        ride_die "browser-forensic destination already exists; refusing to overwrite"
      fi
      umask 077
      mkdir -p "$base" "$(dirname "$link")"
      mkdir "$environment" || ride_die "cannot create browser-forensic destination"
      archive="$environment/browser-forensic-10e2f70.tar.gz"
      if ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 120 --max-filesize 10000000 \
          "$source_uri" -o "$archive"; then
        rm -rf -- "$environment"
        return 1
      fi
      if [[ "$(sha256sum -- "$archive" | cut -d' ' -f1)" != "$source_sha" ]]; then
        rm -rf -- "$environment"
        ride_error "browser-forensic source digest verification failed"
        return 1
      fi
      build_dir="$environment/.build"
      mkdir "$build_dir" "$build_dir/source" || { rm -rf -- "$environment"; return 1; }
      if ! tar -xzf "$archive" --strip-components=1 -C "$build_dir/source"; then
        rm -rf -- "$environment"
        return 1
      fi
      if ! CARGO_HOME="$build_dir/cargo-home" CARGO_TARGET_DIR="$build_dir/target" \
          cargo build --locked --release --package browser-forensic-cli --bin br4n6 \
          --manifest-path "$build_dir/source/Cargo.toml"; then
        rm -rf -- "$environment"
        ride_error "browser-forensic pinned Cargo build failed"
        return 1
      fi
      extracted_binary="$build_dir/target/release/br4n6"
      if [[ ! -x "$extracted_binary" ]] || ! "$extracted_binary" --version >/dev/null 2>&1; then
        rm -rf -- "$environment"
        ride_error "browser-forensic CLI build verification failed"
        return 1
      fi
      if ! install -m 0755 -- "$extracted_binary" "$environment/br4n6"; then
        rm -rf -- "$environment"
        return 1
      fi
      rm -rf -- "$build_dir"
      marker=$(ride_browser_forensic_marker "$environment" "$source_sha") || {
        rm -rf -- "$environment"
        return 1
      }
      printf '%s' "$marker" > "$environment/.ride-owned"
      if ! ln -s -- "$environment/br4n6" "$link"; then
        rm -rf -- "$environment"
        return 1
      fi
      ;;
    absent)
      if [[ -e "$environment" || -L "$environment" || -e "$link" || -L "$link" ]]; then
        marker=$(ride_browser_forensic_marker "$environment" "$source_sha" 2>/dev/null) ||
          ride_die "refusing to remove modified or unowned browser-forensic files"
        if ! { [[ -d "$environment" && ! -L "$environment" ]] &&
               ride_browser_forensic_owned_contents "$environment" &&
               [[ -f "$environment/.ride-owned" && ! -L "$environment/.ride-owned" &&
                  "$(cat "$environment/.ride-owned")" == "$marker" &&
                  -f "$environment/browser-forensic-10e2f70.tar.gz" && ! -L "$environment/browser-forensic-10e2f70.tar.gz" &&
                  "$(sha256sum -- "$environment/browser-forensic-10e2f70.tar.gz" | cut -d' ' -f1)" == "$source_sha" &&
                  -x "$environment/br4n6" && -L "$link" && "$(readlink -- "$link")" == "$environment/br4n6" ]]; }; then
          ride_die "refusing to remove modified or unowned browser-forensic files"
        fi
        rm -- "$link"
        rm -rf -- "$environment"
      fi
      ;;
    *) ride_die "invalid browser-forensic state: $state" ;;
  esac
}

ride_vmfs6_reader_directory() {
  printf '%s\n' "${XDG_DATA_HOME:-$HOME/.local/share}/ride-fedora/tools/vmfs6-reader"
}

ride_vmfs6_reader_link() {
  printf '%s\n' "$HOME/.local/bin/debugvmfs6"
}

ride_vmfs6_reader_owned_contents() {
  local directory=$1
  [[ "$(find "$directory" -mindepth 1 -maxdepth 1 -printf '%f\n' | LC_ALL=C sort)" == \
    $'.ride-owned\ndebugvmfs6\nvmfs6-tools-0.2.1.tar.gz' ]]
}

ride_vmfs6_reader_marker() {
  local directory=$1 source_sha=$2 binary_sha
  [[ -d "$directory" && ! -L "$directory" && -f "$directory/debugvmfs6" &&
     ! -L "$directory/debugvmfs6" && -x "$directory/debugvmfs6" &&
     -f "$directory/vmfs6-tools-0.2.1.tar.gz" && ! -L "$directory/vmfs6-tools-0.2.1.tar.gz" ]] || return 1
  [[ "$(sha256sum -- "$directory/vmfs6-tools-0.2.1.tar.gz" | cut -d' ' -f1)" == "$source_sha" ]] || return 1
  binary_sha=$(sha256sum -- "$directory/debugvmfs6" | cut -d' ' -f1)
  printf 'ride-fedora package.vmfs6-reader 0.2.1 %s %s\n' "$source_sha" "$binary_sha"
}

ride_observe_vmfs6_reader() {
  local entry=$1 directory link source_sha marker
  directory=$(ride_vmfs6_reader_directory)
  link=$(ride_vmfs6_reader_link)
  source_sha=$(jq -r '.sourceSha256' <<< "$entry")
  marker=$(ride_vmfs6_reader_marker "$directory" "$source_sha" 2>/dev/null) || {
    printf 'absent\n'
    return 0
  }
  if ride_vmfs6_reader_owned_contents "$directory" &&
     [[ -f "$directory/.ride-owned" && ! -L "$directory/.ride-owned" &&
        "$(cat "$directory/.ride-owned")" == "$marker" &&
        -L "$link" && "$(readlink -- "$link")" == "$directory/debugvmfs6" ]]; then
    printf 'installed\n'
  else
    printf 'absent\n'
  fi
}

ride_change_vmfs6_reader() {
  local entry=$1 state=$2 directory link base source_uri source_sha stage source_tree archive binary marker
  directory=$(ride_vmfs6_reader_directory)
  link=$(ride_vmfs6_reader_link)
  base=$(dirname "$directory")
  source_uri=$(jq -r '.sourceUri' <<< "$entry")
  source_sha=$(jq -r '.sourceSha256' <<< "$entry")
  case "$state" in
    installed)
      local command_name
      for command_name in curl sha256sum tar gcc make pkg-config install; do
        ride_require_command "$command_name"
      done
      if [[ -e "$directory" || -L "$directory" || -e "$link" || -L "$link" ]]; then
        ride_die "VMFS6 reader destination already exists; refusing to overwrite"
      fi
      umask 077
      mkdir -p "$base" "$(dirname "$link")"
      stage=$(mktemp -d "$base/.vmfs6-reader.XXXXXX") || ride_die "cannot create VMFS6 reader staging directory"
      archive="$stage/vmfs6-tools-0.2.1.tar.gz"
      if ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 120 --max-filesize 10000000 "$source_uri" -o "$archive"; then
        rm -rf -- "$stage"
        return 1
      fi
      if [[ "$(sha256sum -- "$archive" | cut -d' ' -f1)" != "$source_sha" ]]; then
        rm -rf -- "$stage"
        ride_error "VMFS6 reader source digest verification failed"
        return 1
      fi
      source_tree="$stage/source"
      mkdir "$source_tree" || { rm -rf -- "$stage"; return 1; }
      if ! tar -xzf "$archive" --strip-components=1 -C "$source_tree"; then
        rm -rf -- "$stage"
        return 1
      fi
      if ! (cd "$source_tree" && env -u VMFS_WRITE -u CPPFLAGS -u CFLAGS ./configure &&
            env -u VMFS_WRITE -u CPPFLAGS -u CFLAGS make debugvmfs6/debugvmfs6); then
        rm -rf -- "$stage"
        ride_error "pinned VMFS6 reader build failed"
        return 1
      fi
      binary="$source_tree/debugvmfs6/debugvmfs6"
      if [[ ! -f "$binary" || ! -x "$binary" || -L "$binary" ]] ||
         ! install -m 0755 -- "$binary" "$stage/debugvmfs6"; then
        rm -rf -- "$stage"
        ride_error "pinned VMFS6 reader build output is missing or invalid"
        return 1
      fi
      rm -rf -- "$source_tree"
      if ! mv -- "$stage" "$directory"; then
        rm -rf -- "$stage"
        return 1
      fi
      marker=$(ride_vmfs6_reader_marker "$directory" "$source_sha") || {
        rm -rf -- "$directory"
        return 1
      }
      printf '%s' "$marker" > "$directory/.ride-owned"
      if ! ln -s -- "$directory/debugvmfs6" "$link"; then
        rm -rf -- "$directory"
        return 1
      fi
      ;;
    absent)
      if [[ -e "$directory" || -L "$directory" || -e "$link" || -L "$link" ]]; then
        marker=$(ride_vmfs6_reader_marker "$directory" "$source_sha" 2>/dev/null) ||
          ride_die "refusing to remove modified or unowned VMFS6 reader files"
        if ! ride_vmfs6_reader_owned_contents "$directory" ||
           [[ ! -f "$directory/.ride-owned" || -L "$directory/.ride-owned" ||
              "$(cat "$directory/.ride-owned")" != "$marker" ||
              ! -L "$link" || "$(readlink -- "$link")" != "$directory/debugvmfs6" ]]; then
          ride_die "refusing to remove modified or unowned VMFS6 reader files"
        fi
        rm -- "$link"
        rm -rf -- "$directory"
      fi
      ;;
    *) ride_die "invalid VMFS6 reader state: $state" ;;
  esac
}

ride_asn_environment() {
  printf '%s\n' "${XDG_DATA_HOME:-$HOME/.local/share}/ride-fedora/tools/asn"
}

ride_asn_link() {
  printf '%s\n' "$HOME/.local/bin/asn"
}

ride_asn_owned_contents() {
  local environment=$1
  [[ "$(find "$environment" -mindepth 1 -maxdepth 1 -printf '%f\n' | LC_ALL=C sort)" == \
    $'.ride-owned\nLICENSE\nasn' ]]
}

ride_observe_asn() {
  local entry=$1 environment link script_sha license_sha marker
  environment=$(ride_asn_environment)
  link=$(ride_asn_link)
  script_sha=$(jq -r '.sourceSha256' <<< "$entry")
  license_sha=$(jq -r '.licenseSha256' <<< "$entry")
  marker="ride-fedora package.asn $script_sha"
  if [[ -d "$environment" && ! -L "$environment" ]] &&
     ride_asn_owned_contents "$environment" &&
     [[ -f "$environment/.ride-owned" && ! -L "$environment/.ride-owned" &&
        "$(cat "$environment/.ride-owned")" == "$marker" &&
        -f "$environment/asn" && ! -L "$environment/asn" && -x "$environment/asn" &&
        -f "$environment/LICENSE" && ! -L "$environment/LICENSE" &&
        -L "$link" && "$(readlink -- "$link")" == "$environment/asn" &&
        "$(sha256sum -- "$environment/asn" | cut -d' ' -f1)" == "$script_sha" &&
        "$(sha256sum -- "$environment/LICENSE" | cut -d' ' -f1)" == "$license_sha" ]]; then
    printf 'installed\n'
  else
    printf 'absent\n'
  fi
}

ride_change_asn() {
  local entry=$1 state=$2 environment link base temporary source_uri license_uri script_sha license_sha marker
  environment=$(ride_asn_environment)
  link=$(ride_asn_link)
  base=$(dirname "$environment")
  source_uri=$(jq -r '.sourceUri' <<< "$entry")
  license_uri=$(jq -r '.licenseUri' <<< "$entry")
  script_sha=$(jq -r '.sourceSha256' <<< "$entry")
  license_sha=$(jq -r '.licenseSha256' <<< "$entry")
  marker="ride-fedora package.asn $script_sha"
  case "$state" in
    installed)
      ride_require_command curl
      ride_require_command sha256sum
      if [[ -e "$environment" || -L "$environment" || -e "$link" || -L "$link" ]]; then
        ride_die "ASN destination already exists; refusing to overwrite: $environment or $link"
      fi
      umask 077
      mkdir -p "$base" "$(dirname "$link")"
      temporary=$(mktemp -d "$base/.asn.XXXXXXXX") || ride_die "cannot stage ASN script"
      if ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 60 --max-filesize 250000 \
          "$source_uri" -o "$temporary/asn" ||
         ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 60 --max-filesize 4096 \
          "$license_uri" -o "$temporary/LICENSE"; then
        rm -rf -- "$temporary"
        return 1
      fi
      if [[ "$(sha256sum -- "$temporary/asn" | cut -d' ' -f1)" != "$script_sha" ||
            "$(sha256sum -- "$temporary/LICENSE" | cut -d' ' -f1)" != "$license_sha" ]] ||
         ! bash -n "$temporary/asn"; then
        rm -rf -- "$temporary"
        ride_error "ASN source digest or syntax verification failed"
        return 1
      fi
      chmod 0755 "$temporary/asn"
      chmod 0644 "$temporary/LICENSE"
      printf '%s\n' "$marker" > "$temporary/.ride-owned"
      if ! mv -T -- "$temporary" "$environment"; then
        rm -rf -- "$temporary"
        return 1
      fi
      if ! ln -s -- "$environment/asn" "$link"; then
        rm -rf -- "$environment"
        return 1
      fi
      ;;
    absent)
      if [[ -e "$environment" || -L "$environment" || -e "$link" || -L "$link" ]]; then
        [[ -d "$environment" && ! -L "$environment" ]] &&
        ride_asn_owned_contents "$environment" &&
        [[ -f "$environment/.ride-owned" && ! -L "$environment/.ride-owned" &&
           "$(cat "$environment/.ride-owned")" == "$marker" &&
           -f "$environment/asn" && ! -L "$environment/asn" &&
           -f "$environment/LICENSE" && ! -L "$environment/LICENSE" &&
           -L "$link" && "$(readlink -- "$link")" == "$environment/asn" &&
           "$(sha256sum -- "$environment/asn" | cut -d' ' -f1)" == "$script_sha" &&
           "$(sha256sum -- "$environment/LICENSE" | cut -d' ' -f1)" == "$license_sha" ]] ||
          ride_die "refusing to remove modified or unowned ASN files"
        rm -- "$link"
        rm -rf -- "$environment"
      fi
      ;;
    *) ride_die "invalid ASN state: $state" ;;
  esac
}

ride_woeusb_environment() {
  printf '%s\n' "$HOME/.local/opt/ride-fedora/woeusb/5.2.4"
}

ride_woeusb_link() {
  printf '%s\n' "$HOME/.local/bin/woeusb"
}

ride_woeusb_owned_contents() {
  local environment=$1
  [[ "$(find "$environment" -mindepth 1 -maxdepth 1 -printf '%f\n' | LC_ALL=C sort)" == \
    $'.ride-owned\nLICENSE\nwoeusb-5.2.4.bash' ]]
}

ride_observe_woeusb() {
  local entry=$1 environment link source_sha license_sha marker
  environment=$(ride_woeusb_environment)
  link=$(ride_woeusb_link)
  source_sha=$(jq -r '.sourceSha256' <<< "$entry")
  license_sha=$(jq -r '.licenseSha256' <<< "$entry")
  marker="ride-fedora package.woeusb $source_sha"
  if [[ -d "$environment" && ! -L "$environment" ]] &&
     ride_woeusb_owned_contents "$environment" &&
     [[ -f "$environment/.ride-owned" && ! -L "$environment/.ride-owned" &&
        "$(cat "$environment/.ride-owned")" == "$marker" &&
        -f "$environment/woeusb-5.2.4.bash" && ! -L "$environment/woeusb-5.2.4.bash" &&
        -x "$environment/woeusb-5.2.4.bash" &&
        -f "$environment/LICENSE" && ! -L "$environment/LICENSE" &&
        -L "$link" && "$(readlink -- "$link")" == "$environment/woeusb-5.2.4.bash" &&
        "$(sha256sum -- "$environment/woeusb-5.2.4.bash" | cut -d' ' -f1)" == "$source_sha" &&
        "$(sha256sum -- "$environment/LICENSE" | cut -d' ' -f1)" == "$license_sha" ]]; then
    printf 'installed\n'
  else
    printf 'absent\n'
  fi
}

ride_change_woeusb() {
  local entry=$1 state=$2 environment link base temporary source_uri license_uri source_sha license_sha marker
  environment=$(ride_woeusb_environment)
  link=$(ride_woeusb_link)
  base=$(dirname "$environment")
  source_uri=$(jq -r '.sourceUri' <<< "$entry")
  license_uri=$(jq -r '.licenseUri' <<< "$entry")
  source_sha=$(jq -r '.sourceSha256' <<< "$entry")
  license_sha=$(jq -r '.licenseSha256' <<< "$entry")
  marker="ride-fedora package.woeusb $source_sha"
  case "$state" in
    installed)
      ride_require_command curl
      ride_require_command sha256sum
      if [[ -e "$environment" || -L "$environment" || -e "$link" || -L "$link" ]]; then
        ride_die "WoeUSB destination already exists; refusing to overwrite: $environment or $link"
      fi
      umask 077
      mkdir -p "$base" "$(dirname "$link")"
      temporary=$(mktemp -d "$base/.woeusb.XXXXXXXX") || ride_die "cannot stage WoeUSB script"
      if ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 60 --max-filesize 250000 \
          "$source_uri" -o "$temporary/woeusb-5.2.4.bash" ||
         ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 60 --max-filesize 200000 \
          "$license_uri" -o "$temporary/LICENSE"; then
        rm -rf -- "$temporary"
        return 1
      fi
      if [[ "$(sha256sum -- "$temporary/woeusb-5.2.4.bash" | cut -d' ' -f1)" != "$source_sha" ||
            "$(sha256sum -- "$temporary/LICENSE" | cut -d' ' -f1)" != "$license_sha" ]] ||
         ! bash -n "$temporary/woeusb-5.2.4.bash"; then
        rm -rf -- "$temporary"
        ride_error "WoeUSB source digest or syntax verification failed"
        return 1
      fi
      chmod 0755 "$temporary/woeusb-5.2.4.bash"
      chmod 0644 "$temporary/LICENSE"
      printf '%s\n' "$marker" > "$temporary/.ride-owned"
      if ! mv -T -- "$temporary" "$environment"; then
        rm -rf -- "$temporary"
        return 1
      fi
      if ! ln -s -- "$environment/woeusb-5.2.4.bash" "$link"; then
        rm -rf -- "$environment"
        return 1
      fi
      ;;
    absent)
      if [[ -e "$environment" || -L "$environment" || -e "$link" || -L "$link" ]]; then
        [[ -d "$environment" && ! -L "$environment" ]] &&
        ride_woeusb_owned_contents "$environment" &&
        [[ -f "$environment/.ride-owned" && ! -L "$environment/.ride-owned" &&
           "$(cat "$environment/.ride-owned")" == "$marker" &&
           -f "$environment/woeusb-5.2.4.bash" && ! -L "$environment/woeusb-5.2.4.bash" &&
           -f "$environment/LICENSE" && ! -L "$environment/LICENSE" &&
           -L "$link" && "$(readlink -- "$link")" == "$environment/woeusb-5.2.4.bash" &&
           "$(sha256sum -- "$environment/woeusb-5.2.4.bash" | cut -d' ' -f1)" == "$source_sha" &&
           "$(sha256sum -- "$environment/LICENSE" | cut -d' ' -f1)" == "$license_sha" ]] ||
          ride_die "refusing to remove modified or unowned WoeUSB files"
        rm -- "$link"
        rm -rf -- "$environment"
      fi
      ;;
    *) ride_die "invalid WoeUSB state: $state" ;;
  esac
}

ride_librespeed_environment() {
  printf '%s\n' "$HOME/.local/opt/ride-fedora/librespeed-cli/1.0.14"
}

ride_librespeed_link() {
  printf '%s\n' "$HOME/.local/bin/librespeed-cli"
}

ride_librespeed_manifest() {
  printf '%s\n' "$HOME/.local/share/ride-fedora/owned-tools/package.librespeed-cli.json"
}

ride_librespeed_owned_contents() {
  local environment=$1
  [[ "$(find "$environment" -mindepth 1 -maxdepth 1 -printf '%f\n' | LC_ALL=C sort)" == \
    $'.ride-owned\nLICENSE\nlibrespeed-cli' ]]
}

ride_librespeed_version_ok() {
  local executable=$1 output
  output=$("$executable" --version 2>&1) || return 1
  [[ "$output" == *"1.0.14"* ]]
}

ride_observe_librespeed() {
  local entry=$1 environment link manifest archive_sha binary_sha license_sha marker
  environment=$(ride_librespeed_environment)
  link=$(ride_librespeed_link)
  manifest=$(ride_librespeed_manifest)
  archive_sha=$(jq -r '.sourceSha256' <<< "$entry")
  if [[ ! -e "$environment" && ! -L "$environment" &&
        ! -e "$link" && ! -L "$link" && ! -e "$manifest" && ! -L "$manifest" ]]; then
    printf 'absent\n'
    return
  fi
  [[ -d "$environment" && ! -L "$environment" ]] || { printf 'unowned\n'; return; }
  ride_librespeed_owned_contents "$environment" || { printf 'unowned\n'; return; }
  [[ -f "$environment/.ride-owned" && ! -L "$environment/.ride-owned" &&
     -f "$environment/librespeed-cli" && ! -L "$environment/librespeed-cli" &&
     -x "$environment/librespeed-cli" &&
     -f "$environment/LICENSE" && ! -L "$environment/LICENSE" &&
     -L "$link" && "$(readlink -- "$link")" == "$environment/librespeed-cli" &&
     -f "$manifest" && ! -L "$manifest" &&
     "$(stat -c '%u:%g:%a:%h' -- "$manifest")" == "$(id -u):$(id -g):600:1" ]] || {
    printf 'unowned\n'
    return
  }
  binary_sha=$(sha256sum -- "$environment/librespeed-cli" | cut -d' ' -f1) || return 1
  license_sha=$(sha256sum -- "$environment/LICENSE" | cut -d' ' -f1) || return 1
  marker="ride-fedora package.librespeed-cli 1.0.14 $archive_sha $binary_sha $license_sha"
  if [[ "$(cat -- "$environment/.ride-owned")" == "$marker" &&
        "$(jq -r '.id + " " + .version + " " + .archiveSha256 + " " + .binarySha256 + " " + .licenseSha256 + " " + .destination' -- "$manifest")" == \
          "package.librespeed-cli 1.0.14 $archive_sha $binary_sha $license_sha $link" ]]; then
    printf 'installed\n'
  else
    printf 'unowned\n'
  fi
}

ride_librespeed_preflight() {
  local entry=$1 desired=$2 current environment link manifest
  environment=$(ride_librespeed_environment)
  link=$(ride_librespeed_link)
  manifest=$(ride_librespeed_manifest)
  current=$(ride_observe_librespeed "$entry") || ride_die "cannot inspect LibreSpeed CLI deployment"
  [[ "$current" != unowned ]] || ride_die "LibreSpeed CLI files are modified or not RIDE-owned"
  if [[ "$desired" == installed && "$current" == absent ]]; then
    [[ ! -L "$HOME/.local" && ! -L "$HOME/.local/opt" &&
       ! -L "$HOME/.local/opt/ride-fedora" && ! -L "$HOME/.local/opt/ride-fedora/librespeed-cli" &&
       ! -L "$HOME/.local/bin" && ! -L "$HOME/.local/share" &&
       ! -L "$HOME/.local/share/ride-fedora" && ! -L "$HOME/.local/share/ride-fedora/owned-tools" ]] ||
      ride_die "LibreSpeed CLI destination parent is a symlink"
    [[ ! -e "$environment" && ! -L "$environment" &&
       ! -e "$link" && ! -L "$link" && ! -e "$manifest" && ! -L "$manifest" ]] ||
      ride_die "LibreSpeed CLI destination already exists; refusing to overwrite"
  fi
}

ride_change_librespeed() {
  local entry=$1 state=$2 current environment link manifest environment_base manifest_dir
  local archive_uri checksum_uri asset archive_sha manifest_sha temporary
  local binary_sha license_sha marker manifest_temp link_dir
  environment=$(ride_librespeed_environment)
  link=$(ride_librespeed_link)
  manifest=$(ride_librespeed_manifest)
  environment_base=$(dirname "$environment")
  manifest_dir=$(dirname "$manifest")
  link_dir=$(dirname "$link")
  archive_uri=$(jq -r '.sourceUri' <<< "$entry")
  checksum_uri=$(jq -r '.sourceManifestUri' <<< "$entry")
  asset=$(jq -r '.assetName' <<< "$entry")
  archive_sha=$(jq -r '.sourceSha256' <<< "$entry")
  manifest_sha=$(jq -r '.manifestSha256' <<< "$entry")
  ride_librespeed_preflight "$entry" "$state"
  current=$(ride_observe_librespeed "$entry") || return 1
  [[ ! ( "$state" == installed && "$current" == installed ) &&
     ! ( "$state" == absent && "$current" == absent ) ]] || return 0
  case "$state" in
    installed)
      ride_require_command curl
      ride_require_command sha256sum
      ride_require_command python3
      temporary=$(mktemp -d "${TMPDIR:-/tmp}/ride-librespeed.XXXXXXXX") || return 1
      if ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 60 --max-filesize 4096 \
          "$checksum_uri" -o "$temporary/checksums.txt" ||
         ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 120 --max-filesize 6000000 \
          "$archive_uri" -o "$temporary/release.tar.gz"; then
        rm -rf -- "$temporary"
        return 1
      fi
      if [[ "$(sha256sum -- "$temporary/checksums.txt" | cut -d' ' -f1)" != "$manifest_sha" ||
            "$(sha256sum -- "$temporary/release.tar.gz" | cut -d' ' -f1)" != "$archive_sha" ]] ||
         ! grep -Fqx "$archive_sha  $asset" "$temporary/checksums.txt"; then
        rm -rf -- "$temporary"
        ride_error "LibreSpeed CLI release or checksum manifest digest verification failed"
        return 1
      fi
      if ! python3 - "$temporary/release.tar.gz" "$temporary/librespeed-cli" "$temporary/LICENSE" <<'PY'
import pathlib
import sys
import tarfile

archive_path, binary_path, license_path = map(pathlib.Path, sys.argv[1:])
selected = {}
with tarfile.open(archive_path, "r:gz") as archive:
    members = archive.getmembers()
    for member in members:
        parts = pathlib.PurePosixPath(member.name).parts
        if (member.name.startswith("/") or ".." in parts or
                not (member.isfile() or member.isdir())):
            raise SystemExit("unsafe release archive member")
        if member.isfile() and pathlib.PurePosixPath(member.name).name in {"librespeed-cli", "LICENSE"}:
            name = pathlib.PurePosixPath(member.name).name
            if name in selected or member.size > 8_000_000:
                raise SystemExit("ambiguous or oversized release archive member")
            selected[name] = member
    if set(selected) != {"librespeed-cli", "LICENSE"}:
        raise SystemExit("release archive lacks the expected binary or license")
    for name, destination in (("librespeed-cli", binary_path), ("LICENSE", license_path)):
        source = archive.extractfile(selected[name])
        if source is None:
            raise SystemExit("cannot read release archive member")
        destination.write_bytes(source.read())
PY
      then
        rm -rf -- "$temporary"
        ride_error "LibreSpeed CLI archive contents failed validation"
        return 1
      fi
      binary_sha=$(sha256sum -- "$temporary/librespeed-cli" | cut -d' ' -f1) || {
        rm -rf -- "$temporary"; return 1;
      }
      license_sha=$(sha256sum -- "$temporary/LICENSE" | cut -d' ' -f1) || {
        rm -rf -- "$temporary"; return 1;
      }
      chmod 0755 "$temporary/librespeed-cli"
      chmod 0644 "$temporary/LICENSE"
      if ! ride_librespeed_version_ok "$temporary/librespeed-cli"; then
        rm -rf -- "$temporary"
        ride_error "LibreSpeed CLI binary version probe failed"
        return 1
      fi
      rm -f -- "$temporary/release.tar.gz" "$temporary/checksums.txt"
      umask 077
      mkdir -p "$environment_base" "$link_dir" "$manifest_dir"
      [[ ! -L "$environment_base" && ! -L "$link_dir" && ! -L "$manifest_dir" ]] || {
        rm -rf -- "$temporary"
        ride_die "LibreSpeed CLI destination parent became a symlink"
      }
      marker="ride-fedora package.librespeed-cli 1.0.14 $archive_sha $binary_sha $license_sha"
      printf '%s\n' "$marker" > "$temporary/.ride-owned"
      mv -T -- "$temporary" "$environment" || { rm -rf -- "$temporary"; return 1; }
      if ! ln -s -- "$environment/librespeed-cli" "$link"; then
        rm -rf -- "$environment"
        return 1
      fi
      manifest_temp=$(mktemp "$manifest_dir/.package.librespeed-cli.XXXXXXXX") || {
        rm -- "$link"; rm -rf -- "$environment"; return 1;
      }
      if ! jq -nc --arg binarySha "$binary_sha" --arg licenseSha "$license_sha" \
          --arg archiveSha "$archive_sha" --arg destination "$link" \
          '{schemaVersion:1,id:"package.librespeed-cli",version:"1.0.14",archiveSha256:$archiveSha,binarySha256:$binarySha,licenseSha256:$licenseSha,destination:$destination}' > "$manifest_temp" ||
         ! chmod 0600 "$manifest_temp" || ! mv -T -- "$manifest_temp" "$manifest"; then
        rm -f -- "$manifest_temp" "$link"
        rm -rf -- "$environment"
        return 1
      fi
      rm -rf -- "$temporary"
      ;;
    absent)
      if [[ "$(ride_observe_librespeed "$entry")" == installed ]]; then
        rm -- "$link"
        rm -f -- "$manifest"
        rm -rf -- "$environment"
      fi
      ;;
    *) ride_die "invalid LibreSpeed CLI state: $state" ;;
  esac
}

ride_eza_portable_environment() {
  printf '%s\n' "$HOME/.local/opt/ride-fedora/eza/0.23.5"
}

ride_eza_portable_link() {
  printf '%s\n' "$HOME/.local/bin/eza"
}

ride_eza_portable_manifest() {
  printf '%s\n' "$HOME/.local/share/ride-fedora/owned-tools/package.eza-portable.json"
}

ride_observe_eza_portable() {
  local entry=$1 environment link manifest archive_sha binary_sha marker
  environment=$(ride_eza_portable_environment)
  link=$(ride_eza_portable_link)
  manifest=$(ride_eza_portable_manifest)
  archive_sha=$(jq -r '.sourceSha256' <<< "$entry")
  if [[ ! -e "$environment" && ! -L "$environment" &&
        ! -e "$link" && ! -L "$link" && ! -e "$manifest" && ! -L "$manifest" ]]; then
    printf 'absent\n'
    return
  fi
  [[ -d "$environment" && ! -L "$environment" &&
     "$(find "$environment" -mindepth 1 -maxdepth 1 -printf '%f\n' | LC_ALL=C sort)" == $'.ride-owned\neza' &&
     -f "$environment/.ride-owned" && ! -L "$environment/.ride-owned" &&
     -f "$environment/eza" && ! -L "$environment/eza" && -x "$environment/eza" &&
     -L "$link" && "$(readlink -- "$link")" == "$environment/eza" &&
     -f "$manifest" && ! -L "$manifest" &&
     "$(stat -c '%u:%g:%a:%h' -- "$manifest")" == "$(id -u):$(id -g):600:1" ]] || {
    printf 'unowned\n'
    return
  }
  binary_sha=$(sha256sum -- "$environment/eza" | cut -d' ' -f1) || return 1
  marker="ride-fedora package.eza-portable 0.23.5 $archive_sha $binary_sha"
  if [[ "$(cat -- "$environment/.ride-owned")" == "$marker" &&
        "$(jq -r '.id + " " + .version + " " + .archiveSha256 + " " + .binarySha256 + " " + .destination' -- "$manifest")" == \
          "package.eza-portable 0.23.5 $archive_sha $binary_sha $link" ]]; then
    printf 'installed\n'
  else
    printf 'unowned\n'
  fi
}

ride_eza_portable_preflight() {
  local entry=$1 desired=$2 current environment link manifest parent
  environment=$(ride_eza_portable_environment)
  link=$(ride_eza_portable_link)
  manifest=$(ride_eza_portable_manifest)
  current=$(ride_observe_eza_portable "$entry") || ride_die "cannot inspect portable Eza deployment"
  [[ "$current" != unowned ]] || ride_die "portable Eza files are modified or not RIDE-owned"
  if [[ "$desired" == installed && "$current" == absent ]]; then
    for parent in "$HOME/.local" "$HOME/.local/opt" "$HOME/.local/opt/ride-fedora" \
      "$HOME/.local/opt/ride-fedora/eza" "$HOME/.local/bin" "$HOME/.local/share" \
      "$HOME/.local/share/ride-fedora" "$HOME/.local/share/ride-fedora/owned-tools"; do
      [[ ! -L "$parent" ]] || ride_die "portable Eza destination parent is a symlink: $parent"
    done
    [[ ! -e "$environment" && ! -L "$environment" &&
       ! -e "$link" && ! -L "$link" && ! -e "$manifest" && ! -L "$manifest" ]] ||
      ride_die "portable Eza destination already exists; refusing to overwrite"
  fi
}

ride_change_eza_portable() {
  local entry=$1 state=$2 current environment link manifest archive_uri archive_sha temporary
  local binary_sha marker manifest_temp parent
  environment=$(ride_eza_portable_environment)
  link=$(ride_eza_portable_link)
  manifest=$(ride_eza_portable_manifest)
  archive_uri=$(jq -r '.sourceUri' <<< "$entry")
  archive_sha=$(jq -r '.sourceSha256' <<< "$entry")
  ride_eza_portable_preflight "$entry" "$state"
  current=$(ride_observe_eza_portable "$entry") || return 1
  [[ ! ( "$state" == installed && "$current" == installed ) &&
     ! ( "$state" == absent && "$current" == absent ) ]] || return 0
  case "$state" in
    installed)
      ride_require_command curl
      ride_require_command sha256sum
      ride_require_command python3
      temporary=$(mktemp -d "${TMPDIR:-/tmp}/ride-eza.XXXXXXXX") || return 1
      if ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 120 --max-filesize 8000000 \
          "$archive_uri" -o "$temporary/release.tar.gz"; then
        rm -rf -- "$temporary"
        return 1
      fi
      if [[ "$(sha256sum -- "$temporary/release.tar.gz" | cut -d' ' -f1)" != "$archive_sha" ]]; then
        rm -rf -- "$temporary"
        ride_error "portable Eza release digest verification failed"
        return 1
      fi
      if ! python3 - "$temporary/release.tar.gz" "$temporary/eza" <<'PY'
import pathlib
import sys
import tarfile

archive_path, binary_path = map(pathlib.Path, sys.argv[1:])
selected = []
with tarfile.open(archive_path, "r:gz") as archive:
    for member in archive.getmembers():
        parts = pathlib.PurePosixPath(member.name).parts
        if (member.name.startswith("/") or ".." in parts or
                not (member.isfile() or member.isdir())):
            raise SystemExit("unsafe release archive member")
        if member.isfile() and pathlib.PurePosixPath(member.name).name == "eza":
            if member.size <= 0 or member.size > 8_000_000:
                raise SystemExit("invalid Eza binary size")
            selected.append(member)
    if len(selected) != 1:
        raise SystemExit("release archive must contain exactly one eza binary")
    source = archive.extractfile(selected[0])
    if source is None:
        raise SystemExit("cannot read Eza binary from release archive")
    binary_path.write_bytes(source.read())
PY
      then
        rm -rf -- "$temporary"
        ride_error "portable Eza archive contents failed validation"
        return 1
      fi
      binary_sha=$(sha256sum -- "$temporary/eza" | cut -d' ' -f1) || {
        rm -rf -- "$temporary"; return 1;
      }
      chmod 0755 "$temporary/eza"
      if ! "$temporary/eza" --version 2>&1 | grep -Fq '0.23.5'; then
        rm -rf -- "$temporary"
        ride_error "portable Eza binary version probe failed"
        return 1
      fi
      umask 077
      for parent in "$(dirname "$environment")" "$(dirname "$link")" "$(dirname "$manifest")"; do
        mkdir -p -- "$parent"
        [[ ! -L "$parent" ]] || { rm -rf -- "$temporary"; ride_die "portable Eza destination parent became a symlink"; }
      done
      marker="ride-fedora package.eza-portable 0.23.5 $archive_sha $binary_sha"
      printf '%s\n' "$marker" > "$temporary/.ride-owned"
      chmod 0600 "$temporary/.ride-owned"
      rm -f -- "$temporary/release.tar.gz"
      mv -T -- "$temporary" "$environment" || { rm -rf -- "$temporary"; return 1; }
      if ! ln -s -- "$environment/eza" "$link"; then
        rm -rf -- "$environment"
        return 1
      fi
      manifest_temp=$(mktemp "$(dirname "$manifest")/.package.eza-portable.XXXXXXXX") || {
        rm -- "$link"; rm -rf -- "$environment"; return 1;
      }
      if ! jq -nc --arg binarySha "$binary_sha" --arg archiveSha "$archive_sha" \
          --arg destination "$link" --arg licenseUri "$(jq -r '.licenseUri' <<< "$entry")" \
          '{schemaVersion:1,id:"package.eza-portable",version:"0.23.5",archiveSha256:$archiveSha,binarySha256:$binarySha,destination:$destination,licenseUri:$licenseUri}' > "$manifest_temp" ||
         ! chmod 0600 "$manifest_temp" || ! mv -T -- "$manifest_temp" "$manifest"; then
        rm -f -- "$manifest_temp" "$link"
        rm -rf -- "$environment"
        return 1
      fi
      ;;
    absent)
      if [[ "$(ride_observe_eza_portable "$entry")" == installed ]]; then
        rm -- "$link"
        rm -f -- "$manifest"
        rm -rf -- "$environment"
      fi
      ;;
    *) ride_die "invalid portable Eza state: $state" ;;
  esac
}

ride_bitwarden_appimage_path() {
  printf '%s\n' "$HOME/Applications/Bitwarden-2026.10.1-x86_64.AppImage"
}

ride_bitwarden_appimage_manifest() {
  printf '%s\n' "$HOME/.local/share/ride-fedora/owned-tools/package.bitwarden-appimage.json"
}

ride_observe_bitwarden_appimage() {
  local entry=$1 path manifest expected_sha actual_sha version manifest_sha manifest_value
  path=$(ride_bitwarden_appimage_path)
  manifest=$(ride_bitwarden_appimage_manifest)
  expected_sha=$(jq -r '.sourceSha512' <<< "$entry")
  version=$(jq -r '.version' <<< "$entry")
  manifest_sha=$(jq -r '.manifestSha256' <<< "$entry")
  if [[ ! -e "$path" && ! -L "$path" && ! -e "$manifest" && ! -L "$manifest" ]]; then
    printf 'absent\n'
    return
  fi
  [[ -f "$path" && ! -L "$path" && -x "$path" && -f "$manifest" && ! -L "$manifest" &&
     "$(stat -c '%u:%g:%a:%h' -- "$manifest")" == "$(id -u):$(id -g):600:1" ]] || {
    printf 'unowned\n'; return;
  }
  actual_sha=$(sha512sum -- "$path" | cut -d' ' -f1 | python3 -c 'import base64,sys; print(base64.b64encode(bytes.fromhex(sys.stdin.read().strip())).decode())') || return 1
  manifest_value=$(jq -r '.id + " " + .version + " " + .sha512 + " " + .manifestSha256 + " " + .destination' -- "$manifest") || return 1
  if [[ "$actual_sha" == "$expected_sha" &&
        "$manifest_value" == "package.bitwarden-appimage $version $expected_sha $manifest_sha $path" ]]; then
    printf 'installed\n'
  else
    printf 'unowned\n'
  fi
}

ride_change_bitwarden_appimage() {
  local entry=$1 state=$2 path manifest parent source manifest_uri asset expected_sha expected_manifest
  local current temporary downloaded_sha manifest_temp
  path=$(ride_bitwarden_appimage_path)
  manifest=$(ride_bitwarden_appimage_manifest)
  parent=$(dirname "$path")
  source=$(jq -r '.sourceUri' <<< "$entry")
  manifest_uri=$(jq -r '.sourceManifestUri' <<< "$entry")
  asset=$(jq -r '.assetName' <<< "$entry")
  expected_sha=$(jq -r '.sourceSha512' <<< "$entry")
  expected_manifest=$(jq -r '.manifestSha256' <<< "$entry")
  current=$(ride_observe_bitwarden_appimage "$entry") || ride_die "cannot inspect Bitwarden AppImage"
  [[ "$current" != unowned ]] || ride_die "Bitwarden AppImage files are modified or not RIDE-owned"
  [[ ! ( "$state" == installed && "$current" == installed ) &&
     ! ( "$state" == absent && "$current" == absent ) ]] || return 0
  case "$state" in
    installed)
      ride_require_command curl
      ride_require_command sha256sum
      ride_require_command sha512sum
      ride_require_command python3
      [[ ! -L "$HOME" && ! -L "$HOME/Applications" && ! -L "$(dirname "$manifest")" &&
         ! -L "$HOME/.local" && ! -L "$HOME/.local/share" && ! -L "$HOME/.local/share/ride-fedora" &&
         ! -L "$HOME/.local/share/ride-fedora/owned-tools" ]] || ride_die "Bitwarden destination parent is a symlink"
      [[ ! -e "$path" && ! -L "$path" && ! -e "$manifest" && ! -L "$manifest" ]] ||
        ride_die "Bitwarden destination already exists; refusing to overwrite"
      temporary=$(mktemp -d "${TMPDIR:-/tmp}/ride-bitwarden.XXXXXXXX") || return 1
      if ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 60 --max-filesize 4096 \
          "$manifest_uri" -o "$temporary/latest-linux.yml" ||
         [[ "$(sha256sum -- "$temporary/latest-linux.yml" | cut -d' ' -f1)" != "$expected_manifest" ]] ||
         ! grep -Fqx "path: $asset" "$temporary/latest-linux.yml" ||
         ! grep -Fqx "sha512: $expected_sha" "$temporary/latest-linux.yml"; then
        rm -rf -- "$temporary"
        ride_error "Bitwarden release manifest verification failed"
        return 1
      fi
      if ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 300 --max-filesize 180000000 \
          "$source" -o "$temporary/$asset"; then
        rm -rf -- "$temporary"
        return 1
      fi
      downloaded_sha=$(sha512sum -- "$temporary/$asset" | cut -d' ' -f1 | python3 -c 'import base64,sys; print(base64.b64encode(bytes.fromhex(sys.stdin.read().strip())).decode())') || {
        rm -rf -- "$temporary"; return 1;
      }
      if [[ "$downloaded_sha" != "$expected_sha" ]] ||
         [[ "$(head -c4 -- "$temporary/$asset")" != $'\177ELF' ]]; then
        rm -rf -- "$temporary"
        ride_error "Bitwarden AppImage digest or executable format verification failed"
        return 1
      fi
      chmod 0755 "$temporary/$asset"
      mkdir -p -- "$parent" "$(dirname "$manifest")" || { rm -rf -- "$temporary"; return 1; }
      if [[ ! -L "$parent" && ! -L "$(dirname "$manifest")" &&
            ! -e "$path" && ! -L "$path" && ! -e "$manifest" && ! -L "$manifest" ]]; then
        mv -T -- "$temporary/$asset" "$path" || { rm -rf -- "$temporary"; return 1; }
      else
        rm -rf -- "$temporary"
        ride_die "Bitwarden destination changed during install; refusing to overwrite"
      fi
      rm -rf -- "$temporary"
      umask 077
      manifest_temp=$(mktemp "$(dirname "$manifest")/.package.bitwarden-appimage.XXXXXXXX") || {
        rm -- "$path"; return 1;
      }
      if ! jq -nc --arg version "$(jq -r '.version' <<< "$entry")" --arg sha512 "$expected_sha" \
          --arg manifestSha "$expected_manifest" --arg destination "$path" \
          '{schemaVersion:1,id:"package.bitwarden-appimage",version:$version,sha512:$sha512,manifestSha256:$manifestSha,destination:$destination}' > "$manifest_temp" ||
         ! chmod 0600 "$manifest_temp" || ! mv -T -- "$manifest_temp" "$manifest"; then
        rm -f -- "$manifest_temp" "$path"
        return 1
      fi
      ;;
    absent)
      if [[ "$current" == installed ]]; then
        rm -- "$path"
        rm -- "$manifest"
      fi
      ;;
    *) ride_die "invalid Bitwarden AppImage state: $state" ;;
  esac
}

ride_publisher_appimage_path() {
  printf '%s/%s\n' "$HOME/Applications" "$(jq -r '.assetName' <<< "$1")"
}

ride_publisher_appimage_manifest() {
  printf '%s/%s.json\n' "$HOME/.local/share/ride-fedora/owned-tools" "$(jq -r '.id' <<< "$1")"
}

ride_observe_publisher_appimage() {
  local entry=$1 path manifest expected_sha version identifier value
  path=$(ride_publisher_appimage_path "$entry")
  manifest=$(ride_publisher_appimage_manifest "$entry")
  identifier=$(jq -r '.id' <<< "$entry")
  expected_sha=$(jq -r '.sourceSha256' <<< "$entry")
  version=$(jq -r '.version' <<< "$entry")
  if [[ ! -e "$path" && ! -L "$path" && ! -e "$manifest" && ! -L "$manifest" ]]; then
    printf 'absent\n'; return
  fi
  [[ -f "$path" && ! -L "$path" && -x "$path" && -f "$manifest" && ! -L "$manifest" &&
     "$(stat -c '%u:%g:%a:%h' -- "$manifest")" == "$(id -u):$(id -g):600:1" ]] || {
    printf 'unowned\n'; return;
  }
  value=$(jq -r '.id + " " + .version + " " + .sha256 + " " + .destination' -- "$manifest") || return 1
  if [[ "$(sha256sum -- "$path" | cut -d' ' -f1)" == "$expected_sha" &&
        "$value" == "$identifier $version $expected_sha $path" ]]; then
    printf 'installed\n'
  else
    printf 'unowned\n'
  fi
}

ride_change_publisher_appimage() {
  local entry=$1 state=$2 path manifest parent source expected_sha version identifier current temporary manifest_temp
  path=$(ride_publisher_appimage_path "$entry")
  manifest=$(ride_publisher_appimage_manifest "$entry")
  identifier=$(jq -r '.id' <<< "$entry")
  parent=$(dirname "$path")
  source=$(jq -r '.sourceUri' <<< "$entry")
  expected_sha=$(jq -r '.sourceSha256' <<< "$entry")
  version=$(jq -r '.version' <<< "$entry")
  current=$(ride_observe_publisher_appimage "$entry") || ride_die "cannot inspect publisher AppImage"
  [[ "$current" != unowned ]] || ride_die "publisher AppImage files are modified or not RIDE-owned"
  [[ ! ( "$state" == installed && "$current" == installed ) &&
     ! ( "$state" == absent && "$current" == absent ) ]] || return 0
  case "$state" in
    installed)
      ride_require_command curl
      ride_require_command sha256sum
      [[ ! -L "$HOME" && ! -L "$HOME/Applications" && ! -L "$HOME/.local" && ! -L "$HOME/.local/share" &&
         ! -L "$HOME/.local/share/ride-fedora" && ! -L "$(dirname "$manifest")" &&
         ! -L "$HOME/.local/share/ride-fedora/owned-tools" ]] || ride_die "publisher AppImage destination parent is a symlink"
      [[ ! -e "$path" && ! -L "$path" && ! -e "$manifest" && ! -L "$manifest" ]] ||
        ride_die "publisher AppImage destination already exists; refusing to overwrite"
      temporary=$(mktemp -d "${TMPDIR:-/tmp}/ride-publisher-appimage.XXXXXXXX") || return 1
      if ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 300 --max-filesize 240000000 \
          "$source" -o "$temporary/publisher.AppImage"; then
        rm -rf -- "$temporary"; return 1
      fi
      if [[ "$(sha256sum -- "$temporary/publisher.AppImage" | cut -d' ' -f1)" != "$expected_sha" ||
            "$(head -c4 -- "$temporary/publisher.AppImage")" != $'\177ELF' ]]; then
        rm -rf -- "$temporary"
        ride_error "publisher AppImage digest or executable format verification failed"
        return 1
      fi
      chmod 0755 "$temporary/publisher.AppImage"
      mkdir -p -- "$parent" "$(dirname "$manifest")" || { rm -rf -- "$temporary"; return 1; }
      if [[ ! -L "$parent" && ! -L "$(dirname "$manifest")" &&
            ! -e "$path" && ! -L "$path" && ! -e "$manifest" && ! -L "$manifest" ]]; then
        mv -T -- "$temporary/publisher.AppImage" "$path" || { rm -rf -- "$temporary"; return 1; }
      else
        rm -rf -- "$temporary"
        ride_die "publisher AppImage destination changed during install; refusing to overwrite"
      fi
      rm -rf -- "$temporary"
      umask 077
      manifest_temp=$(mktemp "$(dirname "$manifest")/.$identifier.XXXXXXXX") || {
        rm -- "$path"; return 1;
      }
      if ! jq -nc --arg id "$identifier" --arg version "$version" --arg sha256 "$expected_sha" --arg destination "$path" \
          '{schemaVersion:1,id:$id,version:$version,sha256:$sha256,destination:$destination}' > "$manifest_temp" ||
         ! chmod 0600 "$manifest_temp" || ! mv -T -- "$manifest_temp" "$manifest"; then
        rm -f -- "$manifest_temp" "$path"; return 1
      fi
      ;;
    absent)
      if [[ "$current" == installed ]]; then rm -- "$path"; rm -- "$manifest"; fi
      ;;
    *) ride_die "invalid Arduino IDE AppImage state: $state" ;;
  esac
}

ride_yubico_authenticator_environment() {
  printf '%s\n' "$HOME/.local/opt/ride-fedora/yubico-authenticator/7.4.1"
}

ride_yubico_authenticator_launcher() { printf '%s\n' "$HOME/.local/bin/yubico-authenticator"; }
ride_yubico_authenticator_desktop() { printf '%s\n' "$HOME/.local/share/applications/com.yubico.yubioath.desktop"; }
ride_yubico_authenticator_icon() { printf '%s\n' "$HOME/.local/share/icons/hicolor/256x256/apps/com.yubico.yubioath.png"; }
ride_yubico_authenticator_manifest() { printf '%s\n' "$HOME/.local/share/ride-fedora/owned-tools/package.yubico-authenticator.json"; }
ride_yubico_authenticator_members() { printf '%s\n' "$HOME/.local/share/ride-fedora/owned-tools/package.yubico-authenticator.members"; }

ride_yubico_authenticator_desktop_content() {
  local environment=$1 icon=$2 executable=$1/authenticator
  printf '[Desktop Entry]\nName=Yubico Authenticator\nGenericName=Yubico Authenticator\nExec="%s"\nIcon=%s\nType=Application\nCategories=Utility;\nKeywords=Yubico;Authenticator;\n' \
    "$executable" "$icon"
}

ride_ferium_portable_state() {
  local action=$1 script="$RIDE_ROOT/tools/manage-ferium.py" current
  [[ -f "$script" && ! -L "$script" ]] || ride_die "Ferium lifecycle helper is missing or unsafe"
  ride_require_command python3
  case "$action" in
    observe) ;;
    installed) action=install ;;
    absent) action=remove ;;
    *) ride_die "invalid Ferium action: $action" ;;
  esac
  current=$(python3 "$script" "$action") || ride_die "Ferium lifecycle action failed"
  case "$action:$current" in
    observe:absent|observe:installed|install:installed|remove:absent) printf '%s\n' "${current#install:}" ;;
    *) ride_die "unexpected Ferium lifecycle state: $action:$current" ;;
  esac
}

ride_minecraft_server_state() {
  local action=$1 script="$RIDE_ROOT/tools/manage-minecraft-server.py" current
  [[ -f "$script" && ! -L "$script" ]] || ride_die "Minecraft server lifecycle helper is missing or unsafe"
  ride_require_command python3
  case "$action" in
    observe) ;;
    installed) action=install ;;
    absent) action=remove ;;
    *) ride_die "invalid Minecraft server action: $action" ;;
  esac
  current=$(python3 "$script" "$action") || ride_die "Minecraft server lifecycle action failed"
  [[ "$current" == installed || "$current" == absent ]] ||
    ride_die "Minecraft server helper returned an invalid state: $current"
  printf '%s\n' "$current"
}

ride_galleta_state() {
  local action=$1 script="$RIDE_ROOT/tools/manage-galleta.py" current
  [[ -f "$script" && ! -L "$script" ]] || ride_die "Galleta lifecycle helper is missing or unsafe"
  ride_require_command python3
  case "$action" in
    observe) ;;
    installed) action=install ;;
    absent) action=remove ;;
    *) ride_die "invalid Galleta action: $action" ;;
  esac
  current=$(python3 "$script" "$action") || ride_die "Galleta lifecycle action failed"
  [[ "$current" == installed || "$current" == absent ]] ||
    ride_die "Galleta helper returned an invalid state: $current"
  printf '%s\n' "$current"
}

ride_yubico_authenticator_tree_sha256() {
  local environment=$1
  tar --sort=name --mtime='@0' --owner=0 --group=0 --numeric-owner \
    --exclude='./.ride-owned' -cf - -C "$environment" . | sha256sum | cut -d' ' -f1
}

ride_observe_yubico_authenticator() {
  local entry=$1 environment launcher desktop icon manifest members expected_sha version actual_sha tree_sha
  environment=$(ride_yubico_authenticator_environment)
  launcher=$(ride_yubico_authenticator_launcher)
  desktop=$(ride_yubico_authenticator_desktop)
  icon=$(ride_yubico_authenticator_icon)
  manifest=$(ride_yubico_authenticator_manifest)
  members=$(ride_yubico_authenticator_members)
  expected_sha=$(jq -r '.sourceSha256' <<< "$entry")
  version=$(jq -r '.version' <<< "$entry")
  if [[ ! -e "$environment" && ! -L "$environment" && ! -e "$launcher" && ! -L "$launcher" &&
        ! -e "$desktop" && ! -L "$desktop" && ! -e "$icon" && ! -L "$icon" &&
        ! -e "$manifest" && ! -L "$manifest" && ! -e "$members" && ! -L "$members" ]]; then
    printf 'absent\n'; return
  fi
  [[ -d "$environment" && ! -L "$environment" && -f "$environment/.ride-owned" &&
     ! -L "$environment/.ride-owned" && -L "$launcher" &&
     "$(readlink -- "$launcher")" == "$environment/authenticator" &&
     -f "$desktop" && ! -L "$desktop" && -f "$icon" && ! -L "$icon" &&
     -f "$manifest" && ! -L "$manifest" && -f "$members" && ! -L "$members" &&
     "$(stat -c '%u:%g:%a:%h' -- "$manifest")" == "$(id -u):$(id -g):600:1" &&
     "$(stat -c '%u:%g:%a:%h' -- "$members")" == "$(id -u):$(id -g):600:1" ]] || {
    printf 'unowned\n'; return;
  }
  actual_sha=$(jq -r '.sourceSha256' -- "$manifest") || return 1
  tree_sha=$(ride_yubico_authenticator_tree_sha256 "$environment") || return 1
  [[ "$actual_sha" == "$expected_sha" &&
     "$(cat -- "$environment/.ride-owned")" == "ride-fedora package.yubico-authenticator $version $expected_sha $tree_sha" &&
     "$(jq -r '.id + " " + .version + " " + .sourceSha256 + " " + .treeSha256 + " " + .environment + " " + .launcher + " " + .desktop + " " + .icon' -- "$manifest")" == \
       "package.yubico-authenticator $version $expected_sha $tree_sha $environment $launcher $desktop $icon" ]] || {
    printf 'unowned\n'; return;
  }
  diff -u "$members" <(find "$environment" -mindepth 1 ! -name .ride-owned -printf '%P\n' | LC_ALL=C sort) >/dev/null || {
    printf 'unowned\n'; return;
  }
  cmp -s <(ride_yubico_authenticator_desktop_content "$environment" "$icon") "$desktop" &&
    cmp -s "$environment/linux_support/com.yubico.yubioath.png" "$icon" || {
      printf 'unowned\n'; return;
    }
  printf 'installed\n'
}

ride_change_yubico_authenticator() {
  local entry=$1 state=$2 current environment launcher desktop icon manifest members parent
  local source signature key_uri fingerprint expected_sha version temporary archive_root actual_sha tree_sha manifest_temp
  environment=$(ride_yubico_authenticator_environment)
  launcher=$(ride_yubico_authenticator_launcher)
  desktop=$(ride_yubico_authenticator_desktop)
  icon=$(ride_yubico_authenticator_icon)
  manifest=$(ride_yubico_authenticator_manifest)
  members=$(ride_yubico_authenticator_members)
  source=$(jq -r '.sourceUri' <<< "$entry")
  signature=$(jq -r '.signatureUri' <<< "$entry")
  key_uri=$(jq -r '.signingKeyUri' <<< "$entry")
  fingerprint=$(jq -r '.signingFingerprint' <<< "$entry")
  expected_sha=$(jq -r '.sourceSha256' <<< "$entry")
  version=$(jq -r '.version' <<< "$entry")
  current=$(ride_observe_yubico_authenticator "$entry") || ride_die "cannot inspect Yubico Authenticator files"
  [[ "$current" != unowned ]] || ride_die "Yubico Authenticator files are modified or not RIDE-owned"
  [[ ! ( "$state" == installed && "$current" == installed ) &&
     ! ( "$state" == absent && "$current" == absent ) ]] || return 0
  case "$state" in
    installed)
      ride_require_command curl; ride_require_command gpg; ride_require_command sha256sum
      ride_require_command tar; ride_require_command find; ride_require_command diff
      for parent in "$HOME" "$HOME/.local" "$HOME/.local/opt" "$HOME/.local/opt/ride-fedora" \
        "$HOME/.local/opt/ride-fedora/yubico-authenticator" "$HOME/.local/bin" \
        "$HOME/.local/share" "$HOME/.local/share/applications" "$HOME/.local/share/icons" \
        "$HOME/.local/share/icons/hicolor" "$HOME/.local/share/icons/hicolor/256x256" \
        "$HOME/.local/share/icons/hicolor/256x256/apps" "$HOME/.local/share/ride-fedora" \
        "$HOME/.local/share/ride-fedora/owned-tools"; do
        [[ ! -L "$parent" ]] || ride_die "Yubico Authenticator destination parent is a symlink: $parent"
      done
      [[ ! -e "$environment" && ! -L "$environment" && ! -e "$launcher" && ! -L "$launcher" &&
         ! -e "$desktop" && ! -L "$desktop" && ! -e "$icon" && ! -L "$icon" &&
         ! -e "$manifest" && ! -L "$manifest" && ! -e "$members" && ! -L "$members" ]] ||
        ride_die "Yubico Authenticator destination exists; refusing to overwrite"
      temporary=$(mktemp -d "${TMPDIR:-/tmp}/ride-yubico-authenticator.XXXXXXXX") || return 1
      mkdir -m 0700 "$temporary/gnupg" "$temporary/extract" || { rm -rf "$temporary"; return 1; }
      if ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 300 --max-filesize 70000000 "$source" -o "$temporary/release.tar.gz" ||
         ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 30 --max-filesize 4096 "$signature" -o "$temporary/release.tar.gz.sig" ||
         ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 30 --max-filesize 1048576 "$key_uri" -o "$temporary/signing-key.asc"; then
        rm -rf -- "$temporary"; ride_error "Yubico Authenticator download failed"; return 1
      fi
      actual_sha=$(sha256sum -- "$temporary/release.tar.gz" | cut -d' ' -f1) || { rm -rf "$temporary"; return 1; }
      if [[ "$actual_sha" != "$expected_sha" ]] ||
         [[ "$(GNUPGHOME="$temporary/gnupg" gpg --batch --with-colons --show-keys "$temporary/signing-key.asc" | awk -F: '$1=="fpr" {print $10; exit}')" != "$fingerprint" ]] ||
         ! GNUPGHOME="$temporary/gnupg" gpg --batch --import "$temporary/signing-key.asc" >/dev/null 2>&1 ||
         ! GNUPGHOME="$temporary/gnupg" gpg --batch --verify "$temporary/release.tar.gz.sig" "$temporary/release.tar.gz" >/dev/null 2>&1; then
        rm -rf -- "$temporary"; ride_error "Yubico Authenticator digest or publisher signature verification failed"; return 1
      fi
      archive_root="yubico-authenticator-$version-linux"
      if ! tar -tzf "$temporary/release.tar.gz" > "$temporary/archive-members" ||
         ! awk -v root="$archive_root/" 'index($0, root) != 1 || $0 ~ /(^|\/)\.\.(\/|$)/ || $0 ~ /^\// {bad=1} END {exit bad}' "$temporary/archive-members"; then
        rm -rf -- "$temporary"; ride_error "Yubico Authenticator archive has an unsafe member"; return 1
      fi
      if ! tar --no-same-owner --no-same-permissions -xzf "$temporary/release.tar.gz" -C "$temporary/extract"; then
        rm -rf -- "$temporary"; return 1
      fi
      [[ -x "$temporary/extract/$archive_root/authenticator" &&
         -f "$temporary/extract/$archive_root/linux_support/com.yubico.yubioath.png" ]] || {
        rm -rf -- "$temporary"; ride_error "Yubico Authenticator archive layout is unexpected"; return 1;
      }
      sed -e "s|^${archive_root}/||" -e 's|/$||' "$temporary/archive-members" | awk 'NF' | LC_ALL=C sort -u > "$temporary/members"
      mkdir -p -- "$(dirname "$environment")" "$(dirname "$launcher")" "$(dirname "$desktop")" \
        "$(dirname "$icon")" "$(dirname "$manifest")" || { rm -rf -- "$temporary"; return 1; }
      if [[ -L "$(dirname "$environment")" || -e "$environment" || -L "$environment" ||
            -e "$launcher" || -L "$launcher" || -e "$desktop" || -L "$desktop" || -e "$icon" || -L "$icon" ||
            -e "$manifest" || -L "$manifest" || -e "$members" || -L "$members" ]]; then
        rm -rf -- "$temporary"; ride_die "Yubico Authenticator destination changed during download"
      fi
      mv -T -- "$temporary/extract/$archive_root" "$environment" || { rm -rf -- "$temporary"; return 1; }
      cp -- "$environment/linux_support/com.yubico.yubioath.png" "$icon" || { rm -rf "$environment" "$temporary"; return 1; }
      ride_yubico_authenticator_desktop_content "$environment" "$icon" > "$desktop" || { rm -rf "$environment" "$temporary"; return 1; }
      ln -s -- "$environment/authenticator" "$launcher" || { rm -rf "$environment" "$desktop" "$icon" "$temporary"; return 1; }
      chmod 0755 "$environment/authenticator"; chmod 0644 "$desktop" "$icon"
      mv -- "$temporary/members" "$members" || { rm -rf "$environment" "$launcher" "$desktop" "$icon" "$temporary"; return 1; }
      tree_sha=$(ride_yubico_authenticator_tree_sha256 "$environment") || { rm -rf "$environment" "$launcher" "$desktop" "$icon" "$members" "$temporary"; return 1; }
      printf 'ride-fedora package.yubico-authenticator %s %s %s\n' "$version" "$expected_sha" "$tree_sha" > "$environment/.ride-owned"
      umask 077
      manifest_temp=$(mktemp "$(dirname "$manifest")/.package.yubico-authenticator.XXXXXXXX") || { rm -rf "$environment" "$launcher" "$desktop" "$icon" "$members" "$temporary"; return 1; }
      if ! jq -nc --arg version "$version" --arg sha "$expected_sha" --arg tree "$tree_sha" \
          --arg environment "$environment" --arg launcher "$launcher" --arg desktop "$desktop" --arg icon "$icon" \
          '{schemaVersion:1,id:"package.yubico-authenticator",version:$version,sourceSha256:$sha,treeSha256:$tree,environment:$environment,launcher:$launcher,desktop:$desktop,icon:$icon}' > "$manifest_temp" ||
         ! chmod 0600 "$manifest_temp" "$members" "$environment/.ride-owned" || ! mv -T "$manifest_temp" "$manifest"; then
        rm -rf "$environment" "$launcher" "$desktop" "$icon" "$members" "$manifest_temp" "$temporary"; return 1
      fi
      rm -rf -- "$temporary"
      ;;
    absent)
      if [[ "$current" == installed ]]; then
        rm -rf -- "$environment"
        rm -f -- "$launcher" "$desktop" "$icon" "$manifest" "$members"
      fi
      ;;
    *) ride_die "invalid Yubico Authenticator package state: $state" ;;
  esac
}

ride_cyberchef_environment() {
  printf '%s\n' /opt/ride-fedora/cyberchef
}

ride_cyberchef_link() {
  printf '%s\n' /usr/share/applications/ride-cyberchef.desktop
}

ride_cyberchef_owned_contents() {
  local environment=$1
  [[ "$(find "$environment" -mindepth 1 -maxdepth 1 -printf '%f\n' | LC_ALL=C sort)" == \
    $'.ride-owned\nmanifest.json\npayload' ]]
}

ride_observe_cyberchef() {
  local entry=$1 environment link archive_sha license_sha marker
  environment=$(ride_cyberchef_environment)
  link=$(ride_cyberchef_link)
  archive_sha=$(jq -r '.sourceSha256' <<< "$entry")
  license_sha=$(jq -r '.licenseSha256' <<< "$entry")
  marker="ride-fedora package.cyberchef 11.5.0 $archive_sha"
  if [[ -d "$environment" && ! -L "$environment" ]] &&
     ride_cyberchef_owned_contents "$environment" &&
     [[ -f "$environment/.ride-owned" && ! -L "$environment/.ride-owned" &&
        "$(cat "$environment/.ride-owned")" == "$marker" &&
        -d "$environment/payload" && ! -L "$environment/payload" &&
        -f "$environment/manifest.json" && ! -L "$environment/manifest.json" &&
        -L "$link" && "$(readlink -- "$link")" == "$environment/payload/ride-cyberchef.desktop" &&
        "$(sha256sum -- "$environment/payload/LICENSE" | cut -d' ' -f1)" == "$license_sha" ]] &&
     python3 "$RIDE_ROOT/lib/v3/cyberchef_archive.py" verify "$environment/payload" "$environment/manifest.json" >/dev/null 2>&1; then
    printf 'installed\n'
  else
    printf 'absent\n'
  fi
}

ride_change_cyberchef() {
  local entry=$1 state=$2 environment link base temporary source_uri license_uri archive_sha license_sha marker
  environment=$(ride_cyberchef_environment)
  link=$(ride_cyberchef_link)
  base=$(dirname "$environment")
  source_uri=$(jq -r '.sourceUri' <<< "$entry")
  license_uri=$(jq -r '.licenseUri' <<< "$entry")
  archive_sha=$(jq -r '.sourceSha256' <<< "$entry")
  license_sha=$(jq -r '.licenseSha256' <<< "$entry")
  marker="ride-fedora package.cyberchef 11.5.0 $archive_sha"
  case "$state" in
    installed)
      ride_require_command curl
      ride_require_command python3
      ride_require_command sha256sum
      ride_require_command firefox
      if [[ -e "$environment" || -L "$environment" || -e "$link" || -L "$link" ]]; then
        ride_die "CyberChef destination already exists; refusing to overwrite"
      fi
      umask 022
      mkdir -p "$base"
      temporary=$(mktemp -d "$base/.cyberchef.XXXXXXXX") || ride_die "cannot stage CyberChef"
      if ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 300 --max-filesize 90000000 \
          "$source_uri" -o "$temporary/release.zip" ||
         ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 60 --max-filesize 20000 \
          "$license_uri" -o "$temporary/LICENSE"; then
        rm -rf -- "$temporary"
        return 1
      fi
      if [[ "$(sha256sum -- "$temporary/release.zip" | cut -d' ' -f1)" != "$archive_sha" ||
            "$(sha256sum -- "$temporary/LICENSE" | cut -d' ' -f1)" != "$license_sha" ]]; then
        rm -rf -- "$temporary"
        ride_error "CyberChef release or license digest verification failed"
        return 1
      fi
      if ! python3 "$RIDE_ROOT/lib/v3/cyberchef_archive.py" extract \
          "$temporary/release.zip" "$temporary/payload"; then
        rm -rf -- "$temporary"
        return 1
      fi
      if ! mv -- "$temporary/LICENSE" "$temporary/payload/LICENSE"; then
        rm -rf -- "$temporary"
        return 1
      fi
      if ! cat > "$temporary/payload/ride-cyberchef.desktop" <<'DESKTOP'
[Desktop Entry]
Version=1.0
Type=Application
Name=CyberChef
Comment=Offline CyberChef analysis in Firefox
Icon=/opt/ride-fedora/cyberchef/payload/images/cyberchef-128x128.png
Exec=firefox file:///opt/ride-fedora/cyberchef/payload/CyberChef_v11.5.0.html
Categories=Network;Utility;
Terminal=false
DESKTOP
      then
        rm -rf -- "$temporary"
        return 1
      fi
      if ! python3 "$RIDE_ROOT/lib/v3/cyberchef_archive.py" manifest \
          "$temporary/payload" "$temporary/manifest.json"; then
        rm -rf -- "$temporary"
        return 1
      fi
      printf '%s\n' "$marker" > "$temporary/.ride-owned"
      rm -- "$temporary/release.zip"
      chmod 0755 "$temporary"
      if ! mv -T -- "$temporary" "$environment"; then
        rm -rf -- "$temporary"
        return 1
      fi
      if ! ln -s -- "$environment/payload/ride-cyberchef.desktop" "$link"; then
        rm -rf -- "$environment"
        return 1
      fi
      ;;
    absent)
      if [[ -e "$environment" || -L "$environment" || -e "$link" || -L "$link" ]]; then
        if ! { [[ -d "$environment" && ! -L "$environment" ]] &&
               ride_cyberchef_owned_contents "$environment" &&
               [[ -f "$environment/.ride-owned" && ! -L "$environment/.ride-owned" &&
                  "$(cat "$environment/.ride-owned")" == "$marker" &&
                  -L "$link" && "$(readlink -- "$link")" == "$environment/payload/ride-cyberchef.desktop" &&
                  "$(sha256sum -- "$environment/payload/LICENSE" | cut -d' ' -f1)" == "$license_sha" ]] &&
               python3 "$RIDE_ROOT/lib/v3/cyberchef_archive.py" verify "$environment/payload" "$environment/manifest.json"; }; then
          ride_die "refusing to remove modified or unowned CyberChef files"
        fi
        rm -- "$link"
        rm -rf -- "$environment"
      fi
      ;;
    *) ride_die "invalid CyberChef state: $state" ;;
  esac
}

ride_networkminer_environment() { printf '%s\n' "$HOME/.local/opt/ride-fedora/networkminer/3.2"; }
ride_networkminer_data() { printf '%s\n' "$HOME/.local/share/networkminer"; }
ride_networkminer_launcher() { printf '%s\n' "$HOME/.local/bin/networkminer"; }
ride_networkminer_desktop() { printf '%s\n' "$HOME/.local/share/applications/networkminer.desktop"; }

ride_networkminer_wrapper_content() {
  cat <<'WRAPPER'
#!/usr/bin/env bash
set -euo pipefail
umask 077
data="$HOME/.local/share/networkminer"
[[ ! -L "$HOME/.local" && ! -L "$HOME/.local/share" && ! -L "$data" ]] || {
  printf 'NetworkMiner data path contains a symlink\n' >&2
  exit 1
}
if [[ -e "$data" ]]; then
  [[ -d "$data" && "$(stat -c '%u:%a' -- "$data")" == "$(id -u):700" ]] || {
    printf 'NetworkMiner data path must be a private user-owned directory\n' >&2
    exit 1
  }
else
  mkdir -m 0700 -- "$data"
fi
cd -- "$data"
exec mono "$HOME/.local/opt/ride-fedora/networkminer/3.2/payload/NetworkMiner.exe" "$@"
WRAPPER
}

ride_networkminer_desktop_content() {
  local launcher=$1
  printf '[Desktop Entry]\nType=Application\nName=NetworkMiner\nComment=Network forensic analysis tool\nExec=%s\nTerminal=false\nCategories=Network;Security;\n' "$launcher"
}

ride_networkminer_safe_parents() {
  local path
  for path in "$HOME/.local" "$HOME/.local/opt" "$HOME/.local/opt/ride-fedora" \
    "$HOME/.local/opt/ride-fedora/networkminer" "$HOME/.local/share/networkminer" "$HOME/.local/bin" \
    "$HOME/.local/share" "$HOME/.local/share/applications" "$HOME/.local/share/ride-fedora"; do
    [[ ! -L "$path" ]] || return 1
  done
}

ride_observe_networkminer() {
  local entry=$1 environment launcher desktop expected_sha version marker
  environment=$(ride_networkminer_environment)
  launcher=$(ride_networkminer_launcher)
  desktop=$(ride_networkminer_desktop)
  expected_sha=$(jq -r '.sourceSha256' <<< "$entry")
  version=$(jq -r '.version' <<< "$entry")
  marker="ride-fedora package.networkminer $version $expected_sha"
  [[ -d "$environment" && ! -L "$environment" && -d "$environment/payload" &&
     ! -L "$environment/payload" && -f "$environment/.ride-owned" && ! -L "$environment/.ride-owned" &&
     "$(cat -- "$environment/.ride-owned")" == "$marker" &&
     -L "$launcher" && "$(readlink -- "$launcher")" == "$environment/bin/networkminer" &&
     -L "$desktop" && "$(readlink -- "$desktop")" == "$environment/networkminer.desktop" &&
     -f "$environment/manifest.json" && ! -L "$environment/manifest.json" &&
     "$(stat -c '%u:%g:%a:%h' -- "$environment/manifest.json")" == "$(id -u):$(id -g):600:1" ]] || {
    printf 'absent\n'; return;
  }
  if cmp -s <(ride_networkminer_wrapper_content) "$environment/bin/networkminer" &&
     cmp -s <(ride_networkminer_desktop_content "$launcher") "$environment/networkminer.desktop" &&
     diff -u <(printf '.ride-owned\nbin\nbin/networkminer\nmanifest.json\nnetworkminer.desktop\npayload\n';
               find "$environment/payload" -mindepth 1 -printf 'payload/%P\n' | LC_ALL=C sort) \
       <(find "$environment" -mindepth 1 -printf '%P\n' | LC_ALL=C sort) >/dev/null &&
     python3 "$RIDE_ROOT/lib/v3/networkminer_archive.py" verify "$environment/payload" "$environment/manifest.json" >/dev/null 2>&1; then
    printf 'installed\n'
  else
    printf 'unowned\n'
  fi
}

ride_change_networkminer() {
  local entry=$1 state=$2 current environment launcher desktop data parent version source expected_sha temporary actual_sha
  environment=$(ride_networkminer_environment)
  launcher=$(ride_networkminer_launcher)
  desktop=$(ride_networkminer_desktop)
  data=$(ride_networkminer_data)
  version=$(jq -r '.version' <<< "$entry")
  source=$(jq -r '.sourceUri' <<< "$entry")
  expected_sha=$(jq -r '.sourceSha256' <<< "$entry")
  ride_networkminer_safe_parents || ride_die "NetworkMiner destination parent is a symlink"
  current=$(ride_observe_networkminer "$entry") || ride_die "cannot inspect NetworkMiner files"
  [[ "$current" != unowned ]] || ride_die "NetworkMiner program files are modified or not RIDE-owned"
  [[ ! ( "$state" == installed && "$current" == installed ) &&
     ! ( "$state" == absent && "$current" == absent ) ]] || return 0
  case "$state" in
    installed)
      [[ "$version" == 3.2 && "$expected_sha" == daceec649fb4fe59b11e4a9e4ecd5f51c1dd37824280dfbeac67bec27b6b6d60 &&
         "$source" == https://download.netresec.com/networkminer/NetworkMiner_3-2.zip ]] ||
        ride_die "unrecognized NetworkMiner source identity"
      ride_require_command curl; ride_require_command sha256sum; ride_require_command python3
      ride_require_command mono
      ride_networkminer_safe_parents || ride_die "NetworkMiner destination parent is a symlink"
      if [[ -e "$data" || -L "$data" ]]; then
        [[ -d "$data" && ! -L "$data" && "$(stat -c '%u:%a' -- "$data")" == "$(id -u):700" ]] ||
          ride_die "existing NetworkMiner output directory is not private and user-owned: $data"
      fi
      [[ ! -e "$environment" && ! -L "$environment" && ! -e "$launcher" && ! -L "$launcher" &&
         ! -e "$desktop" && ! -L "$desktop" ]] || ride_die "NetworkMiner destination exists; refusing to overwrite"
      mkdir -p -- "$(dirname "$environment")" || ride_die "cannot create NetworkMiner program parent"
      temporary=$(mktemp -d "$(dirname "$environment")/.networkminer.XXXXXXXX") || return 1
      if ! curl --proto '=https' --tlsv1.2 -fsSL --max-time 300 --max-filesize 300000000 "$source" -o "$temporary/release.zip"; then
        rm -rf -- "$temporary"; ride_error "NetworkMiner download failed"; return 1
      fi
      actual_sha=$(sha256sum -- "$temporary/release.zip" | cut -d' ' -f1) || { rm -rf -- "$temporary"; return 1; }
      if [[ "$actual_sha" != "$expected_sha" ]] ||
         ! python3 "$RIDE_ROOT/lib/v3/networkminer_archive.py" extract "$temporary/release.zip" "$temporary/payload"; then
        rm -rf -- "$temporary"; ride_error "NetworkMiner archive digest or contents failed verification"; return 1
      fi
      python3 "$RIDE_ROOT/lib/v3/networkminer_archive.py" manifest "$temporary/payload" "$temporary/manifest.json" || {
        rm -rf -- "$temporary"; return 1;
      }
      rm -- "$temporary/release.zip"
      mkdir -m 0700 "$temporary/bin"
      ride_networkminer_wrapper_content > "$temporary/bin/networkminer"
      ride_networkminer_desktop_content "$launcher" > "$temporary/networkminer.desktop"
      chmod 0700 "$temporary/bin/networkminer"
      printf 'ride-fedora package.networkminer %s %s\n' "$version" "$expected_sha" > "$temporary/.ride-owned"
      chmod 0600 "$temporary/.ride-owned" "$temporary/manifest.json"
      mkdir -p -- "$(dirname "$launcher")" "$(dirname "$desktop")"
      [[ ! -L "$(dirname "$environment")" && ! -e "$environment" &&
         ! -e "$launcher" && ! -L "$launcher" && ! -e "$desktop" && ! -L "$desktop" ]] || {
        rm -rf -- "$temporary"; ride_die "NetworkMiner destination changed during download";
      }
      mv -T -- "$temporary" "$environment" || { rm -rf -- "$temporary"; return 1; }
      if ! ln -s -- "$environment/bin/networkminer" "$launcher"; then
        rm -rf -- "$environment"; return 1
      fi
      if ! ln -s -- "$environment/networkminer.desktop" "$desktop"; then
        rm -f -- "$launcher"; rm -rf -- "$environment"; return 1
      fi
      if [[ ! -e "$data" ]]; then mkdir -m 0700 -- "$data" || { rm -f -- "$launcher" "$desktop"; rm -rf -- "$environment"; return 1; }; fi
      ;;
    absent)
      if [[ "$current" == installed ]]; then
        rm -f -- "$launcher" "$desktop"
        rm -rf -- "$environment"
      fi
      ;;
    *) ride_die "invalid NetworkMiner state: $state" ;;
  esac
}

ride_observe_unfurl() {
  local environment
  environment=$(ride_unfurl_environment)
  if [[ -f "$environment/.ride-owned" && ! -L "$environment" &&
        "$(cat "$environment/.ride-owned")" == 'ride-fedora package.dfir-unfurl 20261007' &&
        -x "$environment/bin/python" && -x "$environment/bin/unfurl" &&
        -x "$environment/bin/unfurl_app" ]] &&
     "$environment/bin/python" -c 'import importlib.metadata as m; assert m.version("dfir-unfurl") == "20261007"' >/dev/null 2>&1; then
    printf 'installed\n'
  else
    printf 'absent\n'
  fi
}

ride_change_unfurl() {
  local state=$1 environment base
  environment=$(ride_unfurl_environment)
  base=$(dirname "$environment")
  case "$state" in
    installed)
      ride_require_command python3
      if [[ -e "$environment" || -L "$environment" ]]; then
        ride_die "isolated UnfURL path already exists; refusing to overwrite: $environment"
      fi
      umask 077
      mkdir -p "$base"
      python3 -m venv "$environment" || { rm -rf -- "$environment"; return 1; }
      if ! "$environment/bin/python" -m pip --isolated install --disable-pip-version-check \
          --index-url https://pypi.org/simple --require-hashes --only-binary=:all: \
          -r "$RIDE_ROOT/requirements/unfurl.txt"; then
        rm -rf -- "$environment"
        return 1
      fi
      if [[ ! -x "$environment/bin/unfurl" || ! -x "$environment/bin/unfurl_app" ]] ||
         ! "$environment/bin/python" -c 'import importlib.metadata as m; assert m.version("dfir-unfurl") == "20261007"'; then
        rm -rf -- "$environment"
        return 1
      fi
      printf 'ride-fedora package.dfir-unfurl 20261007\n' > "$environment/.ride-owned"
      ;;
    absent)
      if [[ -e "$environment" || -L "$environment" ]]; then
        [[ -d "$environment" && ! -L "$environment" && -f "$environment/.ride-owned" && ! -L "$environment/.ride-owned" ]] ||
          ride_die "refusing to remove unowned UnfURL path: $environment"
        [[ "$(cat "$environment/.ride-owned")" == 'ride-fedora package.dfir-unfurl 20261007' ]] ||
          ride_die "UnfURL ownership marker differs"
        rm -rf -- "$environment"
      fi
      ;;
    *) ride_die "invalid isolated Python state: $state" ;;
  esac
}

ride_change_volatility() {
  local state=$1 environment base
  environment=$(ride_volatility_environment)
  base=$(dirname "$environment")
  case "$state" in
    installed)
      ride_require_command python3
      if [[ -e "$environment" || -L "$environment" ]]; then
        ride_die "isolated Volatility3 path already exists; refusing to overwrite: $environment"
      fi
      umask 077
      mkdir -p "$base"
      python3 -m venv "$environment" || { rm -rf "$environment"; return 1; }
      if ! "$environment/bin/python" -m pip --isolated install --disable-pip-version-check \
          --index-url https://pypi.org/simple --require-hashes --only-binary=:all: \
          -r "$RIDE_ROOT/requirements/volatility3.txt"; then
        rm -rf "$environment"
        return 1
      fi
      if ! "$environment/bin/python" -c 'import importlib.metadata as m; assert m.version("volatility3") == "2.28.2"; assert m.version("pefile") == "2024.8.26"'; then
        rm -rf "$environment"
        return 1
      fi
      printf 'ride-fedora package.volatility3 2.28.2\n' > "$environment/.ride-owned"
      ;;
    absent)
      if [[ -e "$environment" || -L "$environment" ]]; then
        [[ -d "$environment" && ! -L "$environment" && -f "$environment/.ride-owned" && ! -L "$environment/.ride-owned" ]] ||
          ride_die "refusing to remove unowned Volatility3 path: $environment"
        [[ "$(cat "$environment/.ride-owned")" == 'ride-fedora package.volatility3 2.28.2' ]] ||
          ride_die "Volatility3 ownership marker differs"
        rm -rf -- "$environment"
      fi
      ;;
    *) ride_die "invalid isolated Python state: $state" ;;
  esac
}

ride_download_package() {
  local entry=$1 destination=$2 name source_id file temporary target sidecar checksum found=0
  [[ "$(jq -r '.handler' <<< "$entry")" == dnf-package ]] || ride_die "download unsupported for this handler"
  [[ "$RIDE_OS_ID" == fedora ]] || ride_die "DNF download requires Fedora"
  ride_require_command dnf
  ride_require_command rpmkeys
  ride_require_command sha256sum
  name=$(jq -r '.packageName' <<< "$entry")
  source_id=$(jq -r '.sourceId // ""' <<< "$entry")
  mkdir -p "$destination"
  temporary=$(mktemp -d "$destination/.ride-rpm.XXXXXXXX") || ride_die "cannot create RPM staging directory"
  case "$source_id" in
    rpmfusion-free-updates)
      dnf download --destdir "$temporary" --from-repo="$source_id" "$name" ||
        { rm -rf "$temporary"; ride_die "DNF download failed for $name from $source_id"; }
      ;;
    *) dnf download --destdir "$temporary" "$name" || { rm -rf "$temporary"; ride_die "DNF download failed for $name"; } ;;
  esac
  shopt -s nullglob
  for file in "$temporary"/*.rpm; do
    [[ "$(basename "$file")" == "$name"-* ]] || continue
    if ! rpmkeys --define '_pkgverify_level all' --checksig "$file"; then
      rm -rf "$temporary"
      ride_die "RPM signature verification failed: $name"
    fi
    target="$destination/$(basename "$file")"
    if [[ -e "$target" ]]; then
      if [[ ! -f "$target" || -L "$target" || "$(sha256sum "$target" | cut -d' ' -f1)" != "$(sha256sum "$file" | cut -d' ' -f1)" ]]; then
        rm -rf "$temporary"
        ride_die "RPM destination already exists with different content: $target"
      fi
    else
      mv "$file" "$target"
    fi
    sidecar="$target.sha256"
    checksum=$(cd "$destination" && sha256sum "$(basename "$target")")
    if [[ -e "$sidecar" || -L "$sidecar" ]]; then
      if [[ ! -f "$sidecar" || -L "$sidecar" || "$(cat "$sidecar")" != "$checksum" ]]; then
        rm -rf "$temporary"
        ride_die "RPM checksum sidecar already exists with different content: $sidecar"
      fi
    else
      printf '%s\n' "$checksum" > "$sidecar"
    fi
    printf '%s\n' "$target"
    found=1
  done
  shopt -u nullglob
  rm -rf "$temporary"
  [[ "$found" -eq 1 ]] || ride_die "DNF returned no RPM for $name"
}
