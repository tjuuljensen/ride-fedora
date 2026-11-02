#!/usr/bin/env bash

ride_validate_catalog() {
  [[ -r "$RIDE_CATALOG" ]] || ride_die "catalog not readable: $RIDE_CATALOG"
  jq -e '
    def valid_variant_targets:
      .status as $status | .targets |
      type == "object" and length > 0 and all(.[];
        if has("variantIds") then
          (.variantIds | type == "array" and length > 0 and
            all(.[]; type == "string" and test("^[a-z0-9_-]+$")))
        else $status != "supported" end);
    .schemaVersion == 3 and (.operations | type == "array" and length > 0) and
    ([.operations[].id] | length == (unique | length)) and
    all(.operations[];
      (.id | type == "string" and test("^(package|setting|artifact|system)\\.[a-z0-9.-]+$")) and
      (.kind | IN("package", "setting", "artifact", "system")) and
      (.name | type == "string" and length > 0) and
      (.handler | IN("dnf-package", "smartmontools-package", "systemd-service", "plex-server-service", "glances-web-service", "sshd-root-login", "github-asset", "python-venv", "pinned-script", "pinned-woeusb-script", "pinned-zip", "pinned-binary", "pinned-eza-binary", "pinned-appimage", "pinned-publisher-appimage", "pinned-yubico-tarball", "pinned-volatility2-bundle", "pinned-deb-binary", "ferium-portable", "minecraft-server-jar", "pinned-rpm", "amp-pinned-rpm", "veracrypt-signed-rpm", "publisher-repo-rpm", "snap-store-package", "gsettings-boolean", "ibus-emoji-hotkey", "gsettings-string", "gnome-lock-timing", "gnome-custom-shortcuts", "bash-aliases", "chrome-preferences", "upower-threshold", "dnf5-fast-tuning", "system-hostname", "wireguard-keypair", "flatpak-remote", "flatpak-app", "rpmfusion-repositories", "dnf-package-set-update", "dnf5-system-update", "docker-engine", "user-directories", "firefox-preferences", "firefox-extensions", "nsswitch-mdns", "dnf5-automatic")) and
      (.scope | IN("system", "user")) and
      (.status | IN("blocked", "candidate", "supported")) and
      (.status != "blocked" or .handler == "firefox-extensions") and
      (.recovery | IN("remove-new-install", "exact-state", "none")) and
      (if .kind == "package" then
         ((.states == ["installed", "absent"] and .recovery == "remove-new-install") or
          (.states == ["installed"] and .recovery == "none"))
       elif .kind == "setting" then .recovery == "exact-state"
       elif .kind == "artifact" then .recovery == "none"
       else true end) and
      (.states | type == "array" and length > 0 and all(.[]; type == "string")) and
      valid_variant_targets and
      (.productUri | type == "string" and startswith("https://")) and
      (.sourceUri | type == "string" and startswith("https://")) and
      (.licenseUri | type == "string" and startswith("https://")) and
      (if .kind == "package" then
        ((.distribution == "installed") or ((.handler | IN("pinned-appimage", "pinned-publisher-appimage", "pinned-yubico-tarball", "pinned-volatility2-bundle", "pinned-deb-binary")) and .distribution == "portable")) and
        (.deploymentId | IN("local-installed", "system-flatpak", "user-local-bin", "user-applications-appimage", "user-local-opt")) and
        (.artifactFormat | IN("rpm", "wheel", "script", "zip", "sdist", "flatpak-ref", "tar.gz", "AppImage", "snap", "jar", "deb")) and
        (.sourceId | type == "string" and test("^[a-z0-9-]+$")) and
        (.sourceId as $defaultSource | (.sourceProviders // []) | type == "array" and
          ([.[].sourceId] | length == (unique | length)) and
          all(.[];
            (.sourceId | type == "string" and test("^[a-z0-9-]+$")) and
            .handler == "dnf-package" and
            .scope == null and
            .artifactFormat == "rpm" and
            (.status | IN("candidate", "supported")) and
            .recovery == "remove-new-install" and
            valid_variant_targets and
            (.sourceUri | type == "string" and startswith("https://")) and
            .verification == "fedora-repository-gpg" and
            (.packageName | type == "string" and test("^[A-Za-z0-9+_.-]+$"))
          ) and all(.[]; .sourceId != $defaultSource)) and
        (([.packageName] + [.sourceProviders[]?.packageName] | map(select(. != null))) |
          length == (unique | length))
       else .distribution == null and .deploymentId == null and .artifactFormat == null and
         .sourceId == null and .sourceProviders == null end) and
      (if .handler == "dnf-package" then (.kind == "package" and .artifactFormat == "rpm" and
        (.packageName | type == "string" and test("^[A-Za-z0-9+_.-]+$")) and
        (if .sourceId == "fedora-rpm" then .verification == "fedora-repository-gpg"
         elif .sourceId == "rpmfusion-free-updates" then
           ((.id == "package.gstreamer1-plugins-bad-freeworld" and
             .packageName == "gstreamer1-plugins-bad-freeworld") or
            (.id == "package.handbrake-cli" and .packageName == "HandBrake")) and
           .verification == "fedora-rpmfusion-signatures-and-owned-state"
         else false end))
       elif .handler == "smartmontools-package" then (.kind == "package" and .id == "package.smartmontools" and
         .packageName == "smartmontools" and .serviceName == "smartd.service" and
         .sourceId == "fedora-rpm" and .artifactFormat == "rpm" and
         .states == ["installed", "absent"] and .recovery == "remove-new-install" and
         .verification == "fedora-rpm-gpg-smartd-disabled" and .status == "candidate")
       elif .handler == "systemd-service" then (.kind == "setting" and (.serviceName | type == "string" and test("^[A-Za-z0-9_.@-]+\\.service$")))
       elif .handler == "plex-server-service" then (.kind == "setting" and .scope == "system" and
         .id == "setting.plex-server-service" and .serviceName == "plexmediaserver.service" and
         .states == ["enabled", "disabled"] and .recovery == "exact-state" and
         .verification == "plex-unit-and-active-enabled-state" and
         (.status == "candidate" or .status == "supported") and
         .dependencies == ["package.plex-server"])
       elif .handler == "glances-web-service" then (.kind == "setting" and .scope == "system" and
         .id == "setting.glances-web-service" and .states == ["enabled", "disabled"] and
         .recovery == "exact-state" and .verification == "glances-loopback-web-service" and
         (.status == "candidate" or .status == "supported") and .dependencies == ["package.glances"])
       elif .handler == "sshd-root-login" then (.kind == "setting" and .scope == "system" and
         .id == "setting.ssh-root-login" and .states == ["configured", "absent"] and
         .recovery == "exact-state" and .verification == "sshd-tested-root-login-dropin" and
         (.status == "candidate" or .status == "supported"))
       elif .handler == "nsswitch-mdns" then (.kind == "setting" and .scope == "system" and
         .id == "setting.multicast-dns" and .states == ["enabled", "disabled"] and
         .recovery == "exact-state" and .verification == "authselect-feature-state" and
         .status == "candidate")
       elif .handler == "dnf5-automatic" then (.kind == "setting" and .scope == "system" and
         .id == "setting.dnf5-automatic" and .states == ["enabled", "disabled"] and
         .recovery == "exact-state" and .verification == "dnf5-automatic-owned-systemd-dropin" and
         .status == "candidate" and .dependencies == ["package.dnf5-plugin-automatic"])
       elif .handler == "gsettings-boolean" then (.kind == "setting" and .scope == "user" and
         .states == ["enabled", "disabled"] and
         (.id | IN("setting.gnome-clock-date", "setting.gnome-calendar-week-numbers", "setting.gnome-primary-paste", "setting.gnome-location", "setting.gnome-problem-reporting")))
       elif .handler == "ibus-emoji-hotkey" then (.kind == "setting" and .scope == "user" and
         .id == "setting.ibus-emoji-hotkey" and .states == ["enabled"] and
         .recovery == "exact-state" and .verification == "local-gsettings-state")
       elif .handler == "user-directories" then (.kind == "setting" and .scope == "user" and
         .id == "setting.user-default-directories" and .states == ["installed", "absent"] and
         .recovery == "exact-state" and .verification == "local-owned-user-directories" and
         .status == "candidate")
       elif .handler == "firefox-preferences" then (.kind == "setting" and .scope == "system" and
         .id == "setting.firefox-preferences" and .states == ["configured", "absent"] and
         .recovery == "exact-state" and .verification == "local-owned-firefox-config" and
         .status == "candidate")
       elif .handler == "firefox-extensions" then (.kind == "setting" and .scope == "system" and
         .id == "setting.firefox-addons" and .states == ["configured", "removal-pending", "absent"] and
         .recovery == "exact-state" and .verification == "local-owned-firefox-extension-policy" and
        (.status == "blocked" or .status == "candidate"))
       elif .handler == "ferium-portable" then (.kind == "package" and
         .id == "package.ferium-portable" and .scope == "user" and
         .states == ["installed", "absent"] and .recovery == "remove-new-install" and
         .distribution == "installed" and .deploymentId == "user-local-bin" and
         .artifactFormat == "zip" and .sourceId == "github-release-tagged" and
         .version == "4.7.1" and .assetName == "ferium-linux-nogui.zip" and
         .sourceUri == "https://github.com/gorilla-devs/ferium/releases/download/v4.7.1/ferium-linux-nogui.zip" and
         .verification == "github-release-version-and-observed-sha256" and .status == "candidate")
       elif .handler == "minecraft-server-jar" then (.kind == "package" and
         .id == "package.minecraft-server" and .scope == "user" and
         .states == ["installed", "absent"] and .recovery == "remove-new-install" and
         .distribution == "installed" and .deploymentId == "user-local-opt" and
         .artifactFormat == "jar" and .sourceId == "mojang-server-pinned" and
         .version == "26.3" and .sourceSha1Hex == "33680f5f2ac32864d6d7cf5e56a705fdb3e05f4c" and
         .sourceUri == "https://piston-data.mojang.com/v1/objects/33680f5f2ac32864d6d7cf5e56a705fdb3e05f4c/server.jar" and
         .verification == "mojang-object-sha1-and-observed-sha256" and .status == "candidate")
       elif .handler == "gsettings-string" then (.kind == "setting" and .scope == "user" and
         .states == ["configured", "absent"] and .recovery == "exact-state" and
         .verification == "local-gsettings-state" and
          (if .id == "setting.gnome-region" then .valueKind == "locale" and .allowedValues == null
           elif .id == "setting.gnome-favorite-apps" then .valueKind == "desktop-id-list" and .allowedValues == null
          elif .id == "setting.gnome-window-buttons" then .valueKind == "window-buttons" and
            .allowedValues == [":minimize,maximize,close", ":appmenu:close", "close,minimize,maximize:"]
          else false end))
       elif .handler == "gnome-lock-timing" then (.kind == "setting" and .scope == "user" and
         .id == "setting.gnome-lock-timing" and .states == ["configured", "absent"] and
         .valueKind == "screensaver-lock-timing" and .recovery == "exact-state" and
         .verification == "local-gsettings-state" and
         (.status == "candidate" or .status == "supported"))
       elif .handler == "gnome-custom-shortcuts" then (.kind == "setting" and .scope == "user" and
         .id == "setting.gnome-custom-shortcuts" and .states == ["configured", "absent"] and
         .valueKind == "custom-shortcut-list" and .recovery == "exact-state" and
         .verification == "local-gsettings-state" and .status == "candidate")
       elif .handler == "bash-aliases" then (.kind == "setting" and .scope == "user" and
         .id == "setting.bash-aliases" and .states == ["configured", "absent"] and
         .valueKind == "bash-alias-list" and .recovery == "exact-state" and
         .verification == "local-owned-shell-config" and .status == "candidate")
       elif .handler == "chrome-preferences" then (.kind == "setting" and .scope == "system" and
         .id == "setting.chrome-preferences" and .states == ["configured", "absent"] and
         .valueKind == "chrome-policy-list" and .recovery == "exact-state" and
         .verification == "local-owned-chrome-policy" and .status == "candidate")
       elif .handler == "upower-threshold" then (.kind == "setting" and .scope == "system" and
         .id == "setting.upower-percentage-low" and .states == ["configured"] and
         .valueKind == "percentage-low" and .recovery == "exact-state" and
         .verification == "local-upower-config")
       elif .handler == "system-hostname" then (.kind == "setting" and .scope == "system" and
         .id == "setting.hostname" and .states == ["configured"] and .valueKind == "hostname" and
         .recovery == "exact-state" and .verification == "local-systemd-static-hostname" and (.status == "candidate" or .status == "supported"))
       elif .handler == "dnf5-fast-tuning" then (.kind == "setting" and .scope == "system" and
         .id == "setting.dnf5-fast-tuning" and .states == ["configured", "absent"] and
         .recovery == "exact-state" and .verification == "local-dnf5-config" and .status == "candidate")
       elif .handler == "wireguard-keypair" then (.kind == "setting" and .scope == "system" and
         .id == "setting.wireguard-keypair" and .states == ["configured", "absent"] and
         .recovery == "exact-state" and .verification == "local-wireguard-keypair")
       elif .handler == "flatpak-remote" then (.kind == "setting" and .scope == "system" and
         .id == "setting.flathub-system-remote" and .states == ["configured", "absent"] and
         .recovery == "exact-state" and .verification == "local-flatpak-remote")
       elif .handler == "flatpak-app" then (.kind == "package" and
         ((.id == "package.halloy" and .applicationId == "org.squidowl.halloy") or
          (.id == "package.gearlever" and .applicationId == "it.mijorus.gearlever") or
          (.id == "package.chrome" and .applicationId == "com.google.Chrome") or
          (.id == "package.edge" and .applicationId == "com.microsoft.Edge") or
          (.id == "package.spotify" and .applicationId == "com.spotify.Client") or
          (.id == "package.vivaldi" and .applicationId == "com.vivaldi.Vivaldi") or
          (.id == "package.xmind" and .applicationId == "net.xmind.XMind")) and
         .scope == "system" and .states == ["installed", "absent"] and
         .recovery == "remove-new-install" and .distribution == "installed" and
         .deploymentId == "system-flatpak" and .artifactFormat == "flatpak-ref" and
         .sourceId == "flathub-flatpak" and
         .verification == "flathub-system-gpg")
       elif .handler == "rpmfusion-repositories" then (.kind == "setting" and .scope == "system" and
         .id == "setting.rpmfusion-repositories" and .states == ["configured", "absent"] and
         .recovery == "exact-state" and .verification == "fedora-rpmfusion-signatures-and-owned-state")
       elif .handler == "dnf5-system-update" then (.kind == "system" and .scope == "system" and
         .id == "system.update-all-packages" and .states == ["current"] and
         .recovery == "none" and .verification == "dnf5-system-update-report" and
         (.status == "candidate" or .status == "supported"))
       elif .handler == "docker-engine" then (.kind == "system" and .scope == "system" and
         .id == "system.docker-engine" and .states == ["configured", "absent"] and
         .recovery == "none" and .verification == "docker-ce-local-key-and-data-preservation" and
         .signingFingerprint == "060A61C51B558A7F742B77AAC52FEB6B621E9F35" and .status == "supported")
       elif .handler == "dnf-package-set-update" then (.kind == "system" and .scope == "system" and
         .id == "system.update-multimedia-codecs" and .states == ["current"] and
         .recovery == "none" and .verification == "dnf5-scoped-package-updates" and
         (.packageNames | type == "array" and length == 16 and
           all(.[]; type == "string" and test("^[A-Za-z0-9+_.-]+$"))) and
         .packageNames == ["PackageKit-gstreamer-plugin", "alsa-ucm", "alsa-utils", "gstreamer1-plugin-dav1d", "gstreamer1-plugin-libav", "gstreamer1-plugin-openh264", "gstreamer1-plugins-bad-free", "gstreamer1-plugins-good", "gstreamer1-plugins-ugly-free", "libva-intel-media-driver", "pipewire-alsa", "pipewire-gstreamer", "pipewire-pulseaudio", "pipewire-utils", "wireplumber", "gstreamer-plugins-espeak"])
       elif .handler == "python-venv" then (.kind == "package" and
         (if .id == "package.chepy" then
           .scope == "user" and .artifactFormat == "sdist" and .sourceId == "pypi-sdist-venv" and
           .verification == "pypi-sdist-sha256" and
           .sourceUri == "https://files.pythonhosted.org/packages/3f/4c/b8bc1607c96e1df206912e4db82ace5adfb2fe9dce5926fd7860d265fa58/chepy-7.6.0.tar.gz" and
           .sourceSha256 == "f6084689e43d128748c18f79c79d75539abb67ac8245e950b678cfa0da2f5010"
          else .artifactFormat == "wheel" and (.id | IN("package.volatility3", "package.dfir-unfurl")) end))
      elif .handler == "pinned-script" then (.kind == "package" and .id == "package.asn" and
         .scope == "user" and .artifactFormat == "script" and
         .sourceId == "github-raw-pinned" and .verification == "github-commit-sha256-observed" and
         (.sourceUri | test("^https://raw[.]githubusercontent[.]com/nitefood/asn/[0-9a-f]{40}/asn$")) and
         (.licenseUri | test("^https://raw[.]githubusercontent[.]com/nitefood/asn/[0-9a-f]{40}/LICENSE$")) and
         (.sourceUri | split("/")[5]) == (.licenseUri | split("/")[5]) and
         (.sourceSha256 | type == "string" and test("^[0-9a-f]{64}$")) and
         (.licenseSha256 | type == "string" and test("^[0-9a-f]{64}$")))
       elif .handler == "pinned-woeusb-script" then (.kind == "package" and .id == "package.woeusb" and
         .scope == "user" and .artifactFormat == "script" and .sourceId == "github-release-pinned" and
         .verification == "github-release-pinned-sha256" and .sourceUri == "https://github.com/WoeUSB/WoeUSB/releases/download/v5.2.4/woeusb-5.2.4.bash" and
         .licenseUri == "https://raw.githubusercontent.com/WoeUSB/WoeUSB/v5.2.4/LICENSES/GPL-3.0-or-later.txt" and
         .sourceSha256 == "0b9e502313c6461346cc4d150459b2e1341d30f9ffda005e160829ad9d5bfffc" and
         .licenseSha256 == "2ca9503d76d1ffab14f599b4741382eec11face60ad1f0d7a41897809003a286")
       elif .handler == "pinned-zip" then (.kind == "package" and .id == "package.cyberchef" and
         .scope == "system" and .artifactFormat == "zip" and
         .sourceId == "github-release-pinned" and .verification == "github-release-api-sha256" and
         .sourceUri == "https://github.com/gchq/CyberChef/releases/download/v11.5.0/CyberChef_8cd426dd4f40f1423912d5fad91b578a86a65112.zip" and
         .licenseUri == "https://raw.githubusercontent.com/gchq/CyberChef/v11.5.0/LICENSE" and
         .sourceSha256 == "f6478925d3eaa16ec08626a85f5b85eed10d531a5e18700615fed7ecb024cccf" and
         .licenseSha256 == "58d1e17ffe5109a7ae296caafcadfdbe6a7d176f0bc4ab01e12a689b0499d8bd")
       elif .handler == "pinned-binary" then (.kind == "package" and .id == "package.librespeed-cli" and
         .scope == "user" and .states == ["installed", "absent"] and .recovery == "remove-new-install" and
         .distribution == "installed" and .deploymentId == "user-local-bin" and .artifactFormat == "tar.gz" and
         .sourceId == "github-release-pinned" and .version == "1.0.14" and
         .assetName == "librespeed-cli_1.0.14_linux_amd64.tar.gz" and
         .sourceUri == "https://github.com/librespeed/speedtest-cli/releases/download/v1.0.14/librespeed-cli_1.0.14_linux_amd64.tar.gz" and
         .sourceManifestUri == "https://github.com/librespeed/speedtest-cli/releases/download/v1.0.14/checksums.txt" and
         .sourceSha256 == "89800767ac14085c78a20847ebea23340f6c14a78de0a15c2ac7db8b565c961f" and
         .manifestSha256 == "1cd30f1c4a25b008f2a401ffb4d5617cf5d3b4bc9e44e873f44dd2f2fbd8b3c6" and
         .verification == "github-release-manifest-sha256")
       elif .handler == "pinned-eza-binary" then (.kind == "package" and .id == "package.eza-portable" and
         .scope == "user" and .states == ["installed", "absent"] and .recovery == "remove-new-install" and
         .distribution == "installed" and .deploymentId == "user-local-bin" and .artifactFormat == "tar.gz" and
         .sourceId == "github-release-pinned" and .version == "0.23.5" and
         .assetName == "eza_x86_64-unknown-linux-gnu.tar.gz" and
         .sourceUri == "https://github.com/eza-community/eza/releases/download/v0.23.5/eza_x86_64-unknown-linux-gnu.tar.gz" and
         .sourceSha256 == "35c70c5c43c29108075e58b893234c67ef585f0b53a7eaf8e9e7d4eec9f339b4" and
         .licenseUri == "https://raw.githubusercontent.com/eza-community/eza/v0.23.5/LICENSE.txt" and
         .license == "EUPL-1.2" and .verification == "github-release-pinned-sha256")
       elif .handler == "pinned-appimage" then (.kind == "package" and .id == "package.bitwarden-appimage" and
         .scope == "user" and .states == ["installed", "absent"] and .recovery == "remove-new-install" and
         .distribution == "portable" and .deploymentId == "user-applications-appimage" and .artifactFormat == "AppImage" and
         .sourceId == "github-release-pinned" and .version == "2026.10.1" and
         .assetName == "Bitwarden-2026.10.1-x86_64.AppImage" and
         .sourceUri == "https://github.com/bitwarden/clients/releases/download/desktop-v2026.10.1/Bitwarden-2026.10.1-x86_64.AppImage" and
         .sourceManifestUri == "https://github.com/bitwarden/clients/releases/download/desktop-v2026.10.1/latest-linux.yml" and
         .sourceSha512 == "Nd2GYFve1jSZ7ba3rAlZqRltN4UBzJAOTNuquAK93kiZuWOKagJZBstZ4ocXKeB3LNdbLmbiHZISQht5pQw/ug==" and
         .manifestSha256 == "995c06dcb33b8f7d63468840f1edc245447975ac20b81aeb5258c78d2aaa6aa7" and
         .license == "GPL-3.0 (default; repository contains separately licensed components)" and
         .verification == "publisher-release-manifest-and-sha512")
       elif .handler == "pinned-publisher-appimage" then (.kind == "package" and (.id | IN("package.arduino-ide", "package.joplin")) and
         .scope == "user" and .states == ["installed", "absent"] and .recovery == "remove-new-install" and
         .distribution == "portable" and .deploymentId == "user-applications-appimage" and .artifactFormat == "AppImage" and
         .sourceId == "github-release-pinned" and .verification == "github-release-api-sha256" and
         (if .id == "package.arduino-ide" then .version == "2.3.10" and
           .assetName == "arduino-ide_2.3.10_Linux_64bit.AppImage" and
           .sourceUri == "https://github.com/arduino/arduino-ide/releases/download/2.3.10/arduino-ide_2.3.10_Linux_64bit.AppImage" and
           .sourceSha256 == "79c8590a1744c220d72cbed0ea91c6e2a7f4594292699b2fb3364ebd713cd566" and
           .license == "AGPL-3.0-or-later (distribution includes separately licensed components)" and
           .licenseUri == "https://raw.githubusercontent.com/arduino/arduino-ide/2.3.10/LICENSE.txt"
          else .version == "3.7.22" and .assetName == "Joplin-3.7.22.AppImage" and
           .sourceUri == "https://github.com/laurent22/joplin/releases/download/v3.7.22/Joplin-3.7.22.AppImage" and
           .sourceSha256 == "2b0b1ee82999f00883d21d950c2fb5dff28ccc3d2f570248b3abd40e5100dfdc" and
           .license == "AGPL-3.0-or-later (distribution includes separately licensed components)" and
           .licenseUri == "https://github.com/laurent22/joplin/tree/v3.7.22"
          end))
       elif .handler == "pinned-yubico-tarball" then (.kind == "package" and .id == "package.yubico-authenticator" and
         .scope == "user" and .states == ["installed", "absent"] and .recovery == "remove-new-install" and
         .distribution == "portable" and .deploymentId == "user-local-opt" and .artifactFormat == "tar.gz" and
         .sourceId == "yubico-release-pinned" and .version == "7.4.1" and
         .sourceUri == "https://developers.yubico.com/yubioath-flutter/Releases/yubico-authenticator-7.4.1-linux.tar.gz" and
         .signatureUri == "https://developers.yubico.com/yubioath-flutter/Releases/yubico-authenticator-7.4.1-linux.tar.gz.sig" and
         .signingKeyUri == "https://keys.openpgp.org/vks/v1/by-fingerprint/20EE325B86A81BCBD3E56798F04367096FBA95E8" and
         .signingFingerprint == "20EE325B86A81BCBD3E56798F04367096FBA95E8" and
         .sourceSha256 == "5c8f49cf3653ae9dd3911b53ca60475b03c8c957eb7385b1bd3d49ec4767ddac" and
         .license == "Apache-2.0" and .verification == "yubico-detached-pgp-and-sha256")
       elif .handler == "pinned-deb-binary" then (.kind == "package" and .id == "package.galleta" and
         .scope == "user" and .states == ["installed", "absent"] and .recovery == "remove-new-install" and
         .distribution == "portable" and .deploymentId == "user-local-bin" and .artifactFormat == "deb" and
         .sourceId == "debian-galleta-pinned" and .version == "1.0+20040505-12" and
         .sourceUri == "https://deb.debian.org/debian/pool/main/g/galleta/galleta_1.0+20040505-12_amd64.deb" and
         .sourceSha256 == "1bb1867237e07c403c9f79abad71b6838645f4494a5ea1a4077821f610b401ff" and
         .license == "BSD-3-Clause" and .verification == "debian-package-index-sha256")
       elif .handler == "pinned-volatility2-bundle" then (.kind == "package" and .id == "package.volatility2" and
         .scope == "user" and .states == ["installed", "absent"] and .recovery == "remove-new-install" and
         .distribution == "portable" and .deploymentId == "user-local-opt" and .artifactFormat == "tar.gz" and
         .sourceId == "volatility2-pypy-pinned" and .version == "2.6.1-pypy2.7-8.0.1" and
         .sourceUri == "https://github.com/volatilityfoundation/volatility/archive/refs/tags/2.6.1.tar.gz" and
         .runtimeUri == "https://downloads.python.org/pypy/pypy2.7-v8.0.1-linux64.tar.gz" and
         .sourceSha512Hex == "64d49de21a87fb6152ad430126466bf66bca06457f3fa2d54cee29b0e4a2eee53ab658570b6cbc782e85ca558f45fac5cf6e6625ebd85aa3ffc9f69768cfa844" and
         .runtimeSha256 == "78674cdf95eb4cb1dd5a9b68a70200387111cb29467f8a472ab7cf07a251653c" and
         .license == "GPL-2.0" and .verification == "dual-pinned-archive-sha256-sha512")
       elif .handler == "amp-pinned-rpm" then (.kind == "package" and
         .id == "package.amp-installer" and .sourceId == "cubecoders-amp-pinned" and
         .packageName == "ampinstmgr" and .version == "2.8.0.10-2" and
         .sourceUri == "https://cdn-repo.c7rs.com/ampinstmgr-2.8.0.10-2.x86_64.rpm" and
         .sourceSha256 == "c766e78308df4ff29d703081b4e2477d70822deb5344c985a3502a2306d0396e" and
         .license == "Proprietary" and .verification == "publisher-https-observed-sha256" and
         .scope == "system" and .states == ["installed", "absent"] and
         .recovery == "remove-new-install" and .distribution == "installed" and
         .deploymentId == "local-installed" and .artifactFormat == "rpm")
       elif .handler == "pinned-rpm" then (.kind == "package" and
         (.id == "package.bitwarden-rpm" or .id == "package.powershell" or .id == "package.balena-etcher" or .id == "package.discord") and
         .scope == "system" and .states == ["installed", "absent"] and .recovery == "remove-new-install" and
         .distribution == "installed" and .deploymentId == "local-installed" and .artifactFormat == "rpm" and
         ((.verification == "github-release-pinned-sha256") or (.id == "package.discord" and .verification == "publisher-https-observed-sha256")) and
         ((.id == "package.bitwarden-rpm" and .sourceId == "bitwarden-release" and .packageName == "bitwarden" and
           .version == "2026.10.1" and .sourceUri == "https://github.com/bitwarden/clients/releases/download/desktop-v2026.10.1/Bitwarden-2026.10.1-x86_64.rpm" and
           .sourceSha256 == "2aa3b7a675432bef75e73f513ba365b055a8c16ec2a42610f019f4b6f7d0a61b") or
          (.id == "package.powershell" and .sourceId == "microsoft-powershell-release" and .packageName == "powershell" and
           .version == "7.6.6" and .sourceUri == "https://github.com/PowerShell/PowerShell/releases/download/v7.6.6/powershell-7.6.6-1.rh.x86_64.rpm" and
           .sourceSha256 == "d3f9bce6b6f0723db49ddb4681fdee2a332492bfd1238a305b0fbdb7825e786f" and .license == "MIT") or
          (.id == "package.balena-etcher" and .sourceId == "balena-etcher-release" and .packageName == "balena-etcher" and
           .version == "2.1.9" and .sourceUri == "https://github.com/balena-io/etcher/releases/download/v2.1.9/balena-etcher-2.1.9-1.x86_64.rpm" and
           .sourceSha256 == "7921555a7e3bdd7a2d020574d237a0aade2a112d9132ceb53af1f703abd9212d" and .license == "Apache-2.0") or
          (.id == "package.discord" and .sourceId == "discord-release" and .packageName == "discord" and
           .version == "1.0.168" and .sourceUri == "https://stable.dl2.discordapp.net/apps/linux/1.0.168/discord-1.0.168.rpm" and
           .sourceSha256 == "ade5550aa86cb4562116d5f5731d5af6110c7865d0712da5b25cdaf9d4137b61" and .license == "Proprietary")))
       elif .handler == "veracrypt-signed-rpm" then (.kind == "package" and .id == "package.veracrypt" and
         .scope == "system" and .states == ["installed", "absent"] and .recovery == "remove-new-install" and
         .distribution == "installed" and .deploymentId == "local-installed" and .artifactFormat == "rpm" and
         .sourceId == "veracrypt-publisher" and .packageName == "veracrypt" and .version == "1.26.30" and
         .sourceUri == "https://github.com/veracrypt/VeraCrypt/releases/download/VeraCrypt_1.26.30/veracrypt-1.26.30-Fedora-44-x86_64.rpm" and
         .signatureUri == "https://github.com/veracrypt/VeraCrypt/releases/download/VeraCrypt_1.26.30/veracrypt-1.26.30-Fedora-44-x86_64.rpm.sig" and
         .signingKeyUri == "https://amcrypto.jp/VeraCrypt/VeraCrypt_PGP_public_key.asc" and
         .signingFingerprint == "5069A233D55A0EEB174A5FC3821ACD02680D16DE" and
         .license == "VeraCrypt License (Apache-2.0 AND TrueCrypt License 3.0)" and
         .verification == "veracrypt-detached-pgp-signature")
       elif .handler == "publisher-repo-rpm" then (.kind == "package" and
         ((.id == "package.visual-studio-code" and .sourceId == "microsoft-vscode" and
           .packageName == "code" and .repositoryId == "ride-vscode" and
           .repositoryFile == "ride-vscode.repo" and
           .repositoryBaseUrl == "https://packages.microsoft.com/yumrepos/vscode/" and
           .repositoryKeyUri == "https://packages.microsoft.com/keys/microsoft.asc" and
           .repositoryKeyFingerprint == "BC528686B50D79E339D3721CEB3E94ADBE1229CF" and
           .repositoryConfigUri == "https://code.visualstudio.com/docs/setup/linux") or
          (.id == "package.brave" and .sourceId == "brave-release" and
           .packageName == "brave-browser" and .repositoryId == "ride-brave-browser" and
           .repositoryFile == "ride-brave-browser.repo" and
           .repositoryBaseUrl == "https://brave-browser-rpm-release.s3.brave.com/$basearch" and
           .repositoryKeyUri == "https://brave-browser-rpm-release.s3.brave.com/brave-core.asc" and
           .repositoryConfigUri == "https://brave.com/linux/") or
          (.id == "package.plaso" and .sourceId == "gift-stable-copr" and
           .packageName == "plaso-tools" and .repositoryId == "ride-gift-stable" and
           .repositoryFile == "ride-gift-stable.repo" and
           .repositoryBaseUrl == "https://download.copr.fedorainfracloud.org/results/@gift/stable/fedora-$releasever-$basearch/" and
           .repositoryKeyUri == "https://download.copr.fedorainfracloud.org/results/@gift/stable/pubkey.gpg" and
           .repositoryConfigUri == "https://plaso.readthedocs.io/en/latest/sources/user/Fedora-Packaged-Release.html") or
          (.id == "package.tailscale" and .sourceId == "tailscale-stable" and
           .packageName == "tailscale" and .repositoryId == "ride-tailscale" and
           .repositoryFile == "ride-tailscale.repo" and
           .repositoryBaseUrl == "https://pkgs.tailscale.com/stable/fedora/$basearch" and
           .repositoryKeyUri == "https://pkgs.tailscale.com/stable/fedora/repo.gpg" and
           .repositoryKeyFingerprint == "2596A99EAAB33821893C0A79458CA832957F5868" and
           .repositoryConfigUri == "https://tailscale.com/docs/install/linux") or
          (.id == "package.plex-server" and .sourceId == "plex-stable-v2" and
           .packageName == "plexmediaserver" and .repositoryId == "ride-plex-server" and
           .repositoryFile == "ride-plex-server.repo" and
           .repositoryBaseUrl == "https://repo.plex.tv/rpm/" and
           .repositoryKeyUri == "https://downloads.plex.tv/plex-keys/PlexSign.v2.key" and
           .repositoryKeyFingerprint == "6EFFEB478A6559D75C7C4FE706C521790B9CFFDE" and
           .repositoryConfigUri == "https://support.plex.tv/articles/235974187-enable-repository-updating-for-supported-linux-server-distributions/")) and
         .scope == "system" and .states == ["installed", "absent"] and
         .recovery == "remove-new-install" and .distribution == "installed" and
         .deploymentId == "local-installed" and .artifactFormat == "rpm" and
         .verification == "publisher-repository-rpm-signature")
       elif .handler == "snap-store-package" then (.kind == "package" and
         .id == "package.autopsy" and .sourceId == "snap-store" and
         .packageName == "autopsy" and .snapChannel == "latest/stable" and
         .dependencies == ["package.snapd"] and .states == ["installed", "absent"] and
         .scope == "system" and .recovery == "remove-new-install" and
         .distribution == "installed" and .deploymentId == "local-installed" and
         .artifactFormat == "snap" and .verification == "snap-store-assertion")
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
  local source_id
  while IFS=$'\t' read -r supported_id source_id evidence; do
    [[ "$evidence" == "docs/acceptance/$supported_id.$source_id.md" && -f "$RIDE_ROOT/$evidence" ]] ||
      ride_die "supported source lacks acceptance evidence: $supported_id/$source_id"
  done < <(jq -r '.operations[] | .id as $id | .sourceProviders[]? | select(.status == "supported") |
    [$id, .sourceId, (.acceptanceEvidence // "MISSING")] | @tsv' "$RIDE_CATALOG")
}

ride_entry() {
  local id=$1
  jq -ce --arg id "$id" '.operations[] | select(.id == $id)' "$RIDE_CATALOG"
}

ride_entry_or_die() {
  local id=$1 requested=${2:-} value=${3:-} base selected
  base=$(ride_entry "$id") || ride_die "unknown catalog ID: $id"
  if [[ "$(jq -r '.kind' <<< "$base")" != package ]]; then
    [[ -z "$requested" ]] || ride_die "source selection requires a package: $id"
    if [[ -n "$value" ]]; then
      [[ "$(jq -r '.handler' <<< "$base")" == gsettings-string || "$(jq -r '.handler' <<< "$base")" == gnome-lock-timing || "$(jq -r '.handler' <<< "$base")" == gnome-custom-shortcuts || "$(jq -r '.handler' <<< "$base")" == bash-aliases || "$(jq -r '.handler' <<< "$base")" == chrome-preferences || "$(jq -r '.handler' <<< "$base")" == upower-threshold || "$(jq -r '.handler' <<< "$base")" == system-hostname ]] ||
        ride_die "value selection requires a configurable setting: $id"
      ride_setting_value_valid "$base" "$value" || ride_die "invalid value for $id: $value"
      jq -c --arg value "$value" '. + {selectedValue:$value}' <<< "$base"
      return
    fi
    printf '%s\n' "$base"
    return
  fi
  [[ -z "$value" ]] || ride_die "value selection requires a configurable setting: $id"
  selected=${requested:-$(jq -r '.sourceId' <<< "$base")}
  if [[ "$selected" == "$(jq -r '.sourceId' <<< "$base")" ]]; then
    jq -c 'del(.sourceProviders)' <<< "$base"
    return
  fi
  jq -ce --arg selected "$selected" '
    . as $base | (.sourceProviders[]? | select(.sourceId == $selected)) as $source |
    ($base | del(.handler, .packageName, .artifactFormat, .status, .recovery,
                 .targets, .sourceUri, .verification, .sourceProviders)) + $source
  ' <<< "$base" || ride_die "unknown source $selected for $id"
}

ride_setting_value_valid() {
  local entry=$1 value=$2
  case "$(jq -r '.id' <<< "$entry")" in
    setting.gnome-region)
      [[ "$value" =~ ^[a-z]{2,3}_[A-Z]{2}\.UTF-8$ ]]
      ;;
    setting.gnome-lock-timing)
      [[ "$value" == idle-10-lock-5 || "$value" == idle-15-lock-5 ]]
      ;;
    setting.gnome-favorite-apps)
      [[ ${#value} -le 700 ]] || return 1
      jq -e --argjson favorites "$value" '
        ($favorites | type == "array" and length <= 20 and length == (unique | length)) and
        all($favorites[]; type == "string" and length <= 128 and test("^[A-Za-z0-9._+-]+[.]desktop$"))
      ' <<< '{}' >/dev/null 2>&1
      ;;
    setting.gnome-custom-shortcuts)
      jq -e --argjson config "$value" '
        ($config | type == "object" and
          (.shortcuts | type == "array" and length >= 1 and length <= 20) and
          (.shortcuts | map(.name) | length == (unique | length)) and
          (.shortcuts | map(.binding) | length == (unique | length))) and
        all($config.shortcuts[];
          (.name | type == "string" and length >= 1 and length <= 128 and test("^[A-Za-z0-9 ._+-]+$")) and
          (.command | type == "string" and length >= 1 and length <= 512 and test("^[A-Za-z0-9 ./_+-]+$")) and
          (.binding | type == "string" and length >= 1 and length <= 100 and test("^[A-Za-z0-9<>+-]+$"))) and
        all(["showDesktop", "switchWindows"][]; . as $key | ($config.global[$key] | type == "array" and length <= 8 and
          length == (unique | length) and all(.[]; type == "string" and length <= 100 and test("^[A-Za-z0-9<>+-]+$"))))
      ' <<< '{}' >/dev/null 2>&1
      ;;
    setting.bash-aliases)
      jq -e --argjson aliases "$value" '
        ($aliases | type == "array" and length >= 1 and length <= 4 and
          length == (unique | length)) and
        all($aliases[]; . as $alias | ["ls-eza", "wanip", "wanip4", "wanip6"] | index($alias) != null)
      ' <<< '{}' >/dev/null 2>&1
      ;;
    setting.chrome-preferences)
      jq -e --argjson policies "$value" '
        ($policies | type == "array" and length >= 1 and length <= 8 and length == (unique | length)) and
        all($policies[]; . as $policy | ["homepage", "homepage-not-newtab", "home-button", "no-default-browser-prompt", "disable-safe-browsing", "no-safe-browsing-reporting", "disable-network-prediction", "bookmark-bar"] | index($policy) != null)
      ' <<< '{}' >/dev/null 2>&1
      ;;
    setting.gnome-window-buttons)
      jq -e --arg value "$value" '.allowedValues | index($value) != null' <<< "$entry" >/dev/null
      ;;
    setting.upower-percentage-low)
      [[ "$value" =~ ^([6-9]|[1-4][0-9]|50)$ ]]
      ;;
    setting.hostname)
      ride_system_hostname_value "$value"
      ;;
    *) return 1 ;;
  esac
}

ride_provider_conflict() {
  local entry=$1 id selected source alternative observed
  [[ "$(jq -r '.kind' <<< "$entry")" == package ]] || return 0
  id=$(jq -r '.id' <<< "$entry")
  selected=$(jq -r '.sourceId' <<< "$entry")
  while IFS= read -r source; do
    [[ "$source" == "$selected" ]] && continue
    alternative=$(ride_entry_or_die "$id" "$source")
    if ! ride_target_matches "$alternative"; then
      continue
    fi
    observed=$(ride_observe "$alternative")
    [[ "$observed" != installed ]] || { printf '%s\n' "$source"; return 0; }
  done < <(jq -r '.sourceId, .sourceProviders[]?.sourceId' <<< "$(ride_entry "$id")")
}

ride_source_signature() {
  local version=${2:-2} fields
  case "$version" in
    1) fields='{id, sourceId, handler, packageName, serviceName, scope, sourceUri, verification, targets, recovery}' ;;
    2) fields='if (.handler | IN("gsettings-string", "gnome-lock-timing", "gnome-custom-shortcuts", "bash-aliases", "chrome-preferences", "upower-threshold", "system-hostname")) then
         {id, handler, scope, sourceUri, verification, targets, recovery, valueKind, allowedValues, selectedValue}
       elif (.handler | IN("pinned-script", "pinned-woeusb-script", "pinned-zip", "pinned-binary", "pinned-eza-binary", "pinned-publisher-appimage")) or .id == "package.chepy" then
         {id, distribution, deploymentId, sourceId, handler, packageName, artifactFormat, serviceName,
          scope, sourceUri, sourceSha256, sourceManifestUri, manifestSha256, licenseUri, licenseSha256,
          version, assetName, verification, targets, recovery}
       elif .handler == "pinned-appimage" then
         {id, distribution, deploymentId, sourceId, handler, artifactFormat, scope, sourceUri,
          sourceManifestUri, sourceSha512, manifestSha256, license, licenseUri, version, assetName,
          verification, targets, recovery}
       elif .handler == "pinned-yubico-tarball" then
         {id, distribution, deploymentId, sourceId, handler, artifactFormat, scope, sourceUri,
          signatureUri, signingKeyUri, signingFingerprint, sourceSha256, version, license, licenseUri,
          verification, targets, recovery}
       elif .handler == "pinned-volatility2-bundle" then
         {id, distribution, deploymentId, sourceId, handler, artifactFormat, scope, sourceUri,
          runtimeUri, sourceSha512Hex, runtimeSha256, version, license, licenseUri,
          verification, targets, recovery}
       elif .handler == "pinned-deb-binary" then
         {id, distribution, deploymentId, sourceId, handler, artifactFormat, scope, sourceUri,
          sourceSha256, version, license, licenseUri, verification, targets, recovery}
       elif .handler == "pinned-rpm" then
         {id, distribution, deploymentId, sourceId, handler, packageName, artifactFormat,
          scope, sourceUri, sourceSha256, version, license, licenseUri, verification, targets, recovery}
       elif .handler == "amp-pinned-rpm" then
         {id, distribution, deploymentId, sourceId, handler, packageName, artifactFormat,
          scope, sourceUri, sourceSha256, version, license, licenseUri, verification, targets, recovery}
       elif .handler == "flatpak-app" then
         {id, distribution, deploymentId, sourceId, handler, applicationId, artifactFormat,
          scope, sourceUri, verification, targets, recovery}
       elif .handler == "dnf-package-set-update" then
         {id, handler, packageNames, scope, sourceUri, verification, targets, recovery}
       elif .handler == "dnf5-system-update" then
         {id, handler, scope, sourceUri, verification, targets, recovery}
       elif .handler == "docker-engine" then
         {id, handler, scope, sourceUri, verification, targets, recovery, signingFingerprint}
       elif .handler == "glances-web-service" then
         {id, handler, scope, sourceUri, verification, targets, recovery, dependencies}
       elif .handler == "sshd-root-login" then
         {id, handler, scope, sourceUri, verification, targets, recovery}
       elif .handler == "plex-server-service" then
         {id, handler, serviceName, scope, sourceUri, verification, targets, recovery, dependencies}
       elif .handler == "veracrypt-signed-rpm" then
         {id, distribution, deploymentId, sourceId, handler, packageName, artifactFormat,
          scope, sourceUri, signatureUri, signingKeyUri, signingFingerprint, version,
          verification, targets, recovery}
       elif .handler == "publisher-repo-rpm" then
         {id, distribution, deploymentId, sourceId, handler, packageName, artifactFormat,
          repositoryId, repositoryFile, repositoryBaseUrl, repositoryKeyUri,
          repositoryKeyFingerprint, repositoryConfigUri, scope, sourceUri,
          verification, targets, recovery}
       else
         {id, distribution, deploymentId, sourceId, handler, packageName, artifactFormat, serviceName,
          scope, sourceUri, verification, targets, recovery}
       end' ;;
    *) ride_die "unsupported source signature version: $version" ;;
  esac
  jq -cS "$fields" <<< "$1" |
    sha256sum | cut -d' ' -f1
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
  local profile=$1 id state source value entry handler
  [[ -r "$profile" ]] || ride_die "profile not readable: $profile"
  jq -e '
    .schemaVersion == 1 and (.id | type == "string" and test("^[a-z0-9-]+$")) and
    (.operations | type == "array") and
    ([.operations[].id] | length == (unique | length)) and
    all(.operations[]; (.id | type == "string") and (.state | type == "string") and
      (.value == null or (.value | type == "string" and length > 0 and length <= 2048)) and
      (.source == null or (.source | type == "string" and test("^[a-z0-9-]+$"))))
  ' "$profile" >/dev/null || ride_die "invalid v3 profile: $profile"
  while IFS=$'\t' read -r id state source value; do
    [[ -z "$id" ]] && continue
    [[ "$source" != '~' ]] || source=
    [[ "$value" != '~' ]] || value=
    entry=$(ride_entry_or_die "$id" "$source" "$value")
    [[ "$(jq -r '.kind' <<< "$entry")" != artifact ]] || ride_die "download-only artifact cannot appear in a profile: $id"
    handler=$(jq -r '.handler' <<< "$entry")
    [[ "$handler" != dnf5-system-update ]] || ride_die "whole-system updates require the explicit update command: $id"
    [[ "$handler" != docker-engine ]] || ride_die "Docker Engine changes require the explicit deploy command: $id"
    jq -e --arg state "$state" '.states | index($state) != null' <<< "$entry" >/dev/null ||
      ride_die "invalid state $state for $id"
    if [[ "$handler" == gsettings-string || "$handler" == gnome-lock-timing || "$handler" == gnome-custom-shortcuts || "$handler" == bash-aliases || "$handler" == chrome-preferences || "$handler" == upower-threshold ]]; then
      [[ -n "$value" ]] || ride_die "configurable setting requires a profile value: $id"
    else
      [[ -z "$value" ]] || ride_die "profile value is not valid for $id"
    fi
  done < <(jq -r '.operations[] | [.id, .state, (.source // "~"), (.value // "~")] | @tsv' "$profile")
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
