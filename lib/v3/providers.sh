#!/usr/bin/env bash

ride_observe() {
  local entry=$1 handler name result
  handler=$(jq -r '.handler' <<< "$entry")
  case "$handler" in
    dnf-package)
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
    github-asset) printf 'not-applicable\n' ;;
    pinned-script) ride_observe_asn "$entry" ;;
    pinned-zip) ride_observe_cyberchef "$entry" ;;
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
    *) ride_die "untrusted handler: $handler" ;;
  esac
}

ride_change() {
  local entry=$1 state=$2 handler name
  handler=$(jq -r '.handler' <<< "$entry")
  case "$handler" in
    dnf-package)
      [[ "$RIDE_OS_ID" == fedora ]] || ride_die "DNF handler requires Fedora"
      ride_require_command dnf
      name=$(jq -r '.packageName' <<< "$entry")
      case "$state" in
        installed) dnf --setopt=gpgcheck=1 --setopt=localpkg_gpgcheck=1 install -y "$name" ;;
        absent) dnf remove -y "$name" ;;
        *) ride_die "invalid package state: $state" ;;
      esac
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
    python-venv)
      case "$(jq -r '.id' <<< "$entry")" in
        package.volatility3) ride_change_volatility "$state" ;;
        package.dfir-unfurl) ride_change_unfurl "$state" ;;
        package.chepy) ride_change_chepy "$entry" "$state" ;;
        *) ride_die "unknown isolated Python operation" ;;
      esac
      ;;
    pinned-script)
      [[ "$(jq -r '.id' <<< "$entry")" == package.asn ]] || ride_die "unknown pinned script operation"
      ride_change_asn "$entry" "$state"
      ;;
    pinned-zip)
      [[ "$(jq -r '.id' <<< "$entry")" == package.cyberchef ]] || ride_die "unknown pinned ZIP operation"
      ride_change_cyberchef "$entry" "$state"
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
    *) ride_die "untrusted handler: $handler" ;;
  esac
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

ride_ibus_hotkey_valid_snapshot() {
  local state=$1 encoded raw
  [[ "$state" == unset ]] && return 0
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
    unset) ride_gsettings reset "$schema" "$key" ;;
    user:*)
      ride_ibus_hotkey_valid_snapshot "$state" || ride_die "invalid saved iBus hotkey value"
      raw=$(printf '%s' "${state#user:}" | base64 --decode) || return 1
      ride_gsettings set "$schema" "$key" "$raw"
      ;;
    *) ride_die "invalid iBus hotkey state" ;;
  esac
}

ride_ibus_hotkey_change() {
  local state=$1 schema key before writable after
  [[ "$state" == enabled ]] || ride_ibus_hotkey_valid_snapshot "$state" ||
    ride_die "invalid saved iBus hotkey state"
  read -r schema key < <(ride_ibus_hotkey_schema)
  writable=$(ride_gsettings writable "$schema" "$key") || ride_die "cannot check iBus hotkey writability"
  [[ "$writable" == true ]] || ride_die "iBus hotkey is locked"
  before=$(ride_ibus_hotkey_observe) || return 1
  if [[ "$before" == user:* ]]; then
    ride_ibus_hotkey_valid_snapshot "$before" || ride_die "existing iBus hotkey cannot be safely journaled"
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
  local entry=$1 destination=$2 name file temporary target sidecar checksum found=0
  [[ "$(jq -r '.handler' <<< "$entry")" == dnf-package ]] || ride_die "download unsupported for this handler"
  [[ "$RIDE_OS_ID" == fedora ]] || ride_die "DNF download requires Fedora"
  ride_require_command dnf
  ride_require_command rpmkeys
  ride_require_command sha256sum
  name=$(jq -r '.packageName' <<< "$entry")
  mkdir -p "$destination"
  temporary=$(mktemp -d "$destination/.ride-rpm.XXXXXXXX") || ride_die "cannot create RPM staging directory"
  if ! dnf download --destdir "$temporary" "$name"; then
    rm -rf "$temporary"
    ride_die "DNF download failed for $name"
  fi
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
