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
    python-venv)
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
      [[ "$(jq -r '.id' <<< "$entry")" == package.volatility3 ]] || ride_die "unknown isolated Python operation"
      ride_change_volatility "$state"
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
    *) ride_die "untrusted handler: $handler" ;;
  esac
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
