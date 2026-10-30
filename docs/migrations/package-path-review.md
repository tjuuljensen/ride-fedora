# Scoped v2 package path review

Status: **source and product assessment**, 2026-10-30. The scoped ledger has
133 v2 `package.*` outcomes: 52 mapped to runnable v3 operations, 9 replaced,
10 retired, and 62 unsupported. The five path groups below assess the **70
original unsupported or retired outcomes**; the 10 original replacement
assessments, 52 existing v3 mappings, and six newly scoped server outcomes
follow. The 52 mapped outcomes have catalog and acceptance evidence. The
[ledger](../../migration/outcomes.json) remains authoritative for current
disposition, risk, target, evidence, and next action.

The v2 default preset records selectors, not actual use. Active, commented,
and library-only functions receive the **same product and source review**.
The categories below describe the path from v2, not runnable v3 status.
A broken installer does not establish product EOL; a retired outcome does
not necessarily mean its product ended. High-risk data, storage, encryption,
and security outcomes still need their deeper recovery gate.
The owner's later [v3.0 capability clarification](v30-path-reassessment.md)
keeps every scoped v2 package and setting behavior in the v3.0 migration scope;
earlier retirement labels describe exact old implementations, not completed
capability coverage. Citrix and Opera are explicit owner exclusions.

Source checks: [Atom sunset](https://github.blog/2022-06-08-sunsetting-atom/),
[Volatility 2 archive](https://github.com/volatilityfoundation/volatility),
[Sonos controller deprecation](https://github.com/pascalopitz/unoffical-sonos-controller-for-linux),
[archived GNOME helper](https://github.com/brunelli/gnome-shell-extension-installer),
[GtkHash Fedora subpackages](https://packages.fedoraproject.org/pkgs/gtkhash/),
[WoeUSB-ng successor](https://github.com/WoeUSB/WoeUSB-ng),
[Fedora 44 Pidgin/OTR](https://packages.fedoraproject.org/pkgs/pidgin-otr/pidgin-otr/fedora-44.html),
[Plaso releases](https://github.com/log2timeline/plaso/releases), and
[bulk_extractor releases](https://github.com/simsong/bulk_extractor/releases).
The replacement review also uses [Microsoft's Teams Linux support table](https://learn.microsoft.com/en-gb/microsoftteams/new-teams-whats-changing),
[YubiKey Manager GUI EOL](https://developers.yubico.com/yubikey-manager-qt/),
and the [archived YubiKey Personalization GUI](https://github.com/Yubico/yubikey-personalization-gui).
Each row links its repository batch review for the v2 behavior and target gate.

## Obsolete or unavailable exact v2 product/integration (8)

Six outcomes name discontinued or archived products/helpers. The two Nautilus
outcomes name desktop integrations unavailable on Fedora 44. This is a path
assessment, not an automatic retirement decision.

| Source outcome | Path assessment | Evidence |
| --- | --- | --- |
| `workstation:package.AtomEditor` | GitHub sunset Atom; owner retired the full editor capability from this migration. | [Batch review](publisher-apps-10.md) |
| `workstation:package.AtomPlugins` | Depends on sunset Atom; owner retired the plugin capability from this migration. | [Batch review](publisher-apps-10.md) |
| `workstation:package.Dumpzilla` | Upstream declares the script discontinued, but Firefox profile analysis remains kept; compare pinned browser-forensic with the narrower shared Plaso path and prove seeded-data recovery. | [Batch review](forensic-isolated-08-firefox.md) |
| `workstation:package.GnomeExtInstaller` | The exact upstream helper is archived; owner deferred retirement, while GNOME extension management needs a new path. | [Batch review](provider-foundation-10.md) |
| `workstation:package.NautilusHash` | The exact GtkHash Nautilus integration is absent on Fedora 44; owner retired the full checksum context-action capability. | [Batch review](native-rpm-03.md) |
| `workstation:package.NautilusImageTools` | The old Nautilus image converter lacks a Fedora 44 build; owner retired the full image context-action capability. | [Batch review](native-rpm-03.md) |
| `workstation:package.SonosPlayer` | This unofficial controller declares itself deprecated; owner retired the player capability from this migration. | [Batch review](publisher-apps-09.md) |
| `workstation:package.Volatility` | Volatility 2 is archived; Volatility 3 is distinct and already tracked separately. | [Batch review](forensic-isolated-02.md) |

## Old implementation retired for a reason other than product EOL (6)

| Source outcome | Path assessment | Evidence |
| --- | --- | --- |
| `workstation:package.Galleta` | The v2 pair only printed links; owner deferred the capability decision while reviewing legacy IE cookies versus modern browser forensics. | [Batch review](resolution-decisions.md) |
| `workstation:package.Xplico` | The v2 pair only printed links; owner kept the capability and requested a current installation path or alternative. | [Batch review](resolution-decisions.md) |
| `workstation:package.VMFStools` | The v2 pair only printed links; the kept VMFS6 reader path now has pinned source and a Fedora build, but needs a genuine image fixture and owned lifecycle. | [Batch review](forensic-isolated-07-vmfs.md) |
| `workstation:package.TecmintMonitorSh` | The unverified HTTP script path was retired; owner kept monitoring capability for a maintained replacement review. | [Batch review](resolution-decisions.md) |
| `workstation:package.MicrosoftTeams` | Owner retired Linux Teams desktop capability; the web service remains outside RIDE installation. | [Batch review](publisher-apps-09.md) |
| `workstation:package.VMwareWorkstation` | Owner retired the full VMware Workstation capability; the v2 installer and module recovery remain migration history. | [Batch review](system-security-risk-decisions.md) |

## New acquisition or deployment path (27)

| Source outcome | Path assessment | Evidence |
| --- | --- | --- |
| `server:package.ExpressVPN` | Private publisher package, activation, and profile recovery need an owned path. | [Batch review](generic-server-decisions.md) |
| `server:package.Selenium` | Use an isolated, pinned environment with a declared browser and driver. | [Batch review](generic-server-decisions.md) |
| `server:package.Tailscale` | Use a verified package source with private node identity and service recovery. | [Batch review](generic-server-decisions.md) |
| `workstation:package.ASN` | The pinned MIT script and separately owned Fedora prerequisites now pass an opt-in lifecycle; live lookup checks remain H027. | [Acceptance](../acceptance/package.asn.md) |
| `workstation:package.ArduinoIDE` | Choose a current edition and pinned portable or installed deployment. | [Batch review](publisher-apps-10.md) |
| `workstation:package.Autopsy` | Pin the Linux distribution and preserve case data and Java dependencies. | [Batch review](forensic-isolated-02.md) |
| `workstation:package.BalenaEtcher` | Pin the publisher RPM and separate application install from media writing. | [Batch review](publisher-apps-09.md) |
| `workstation:package.Bitwarden` | Pin publisher RPM bytes and prove vault-preserving recovery. | [Batch review](publisher-apps-12.md) |
| `workstation:package.BitwardenAppImage` | Use the real AppImage with a separate portable identity and vault-safe inverse. | [Batch review](publisher-apps-06.md) |
| `workstation:package.Brave` | Own the publisher repository, signing key, and installed package lifecycle. | [Batch review](publisher-apps-03.md) |
| `workstation:package.BulkExtractor` | Use a pinned current release and preserve forensic output. | [Batch review](forensic-isolated-04.md) |
| `workstation:package.Chepy` | The pinned PyPI sdist, Fedora Python 3.12 runtime, and owned user venv now pass an opt-in lifecycle; wider behavior remains H029. | [Acceptance](../acceptance/package.chepy.md) |
| `workstation:package.Chrome` | Use an owned official package source and preserve browser profile data. | [Batch review](publisher-apps-11.md) |
| `workstation:package.CyberChef` | The pinned official ZIP, tagged license, bundled notices, and owned desktop launcher now pass an opt-in lifecycle. | [Acceptance](../acceptance/package.cyberchef.md) |
| `workstation:package.Discord` | Choose verified publisher RPM or owned Flatpak source; preserve profile data. | [Batch review](publisher-apps-10.md) |
| `workstation:package.Edge` | Choose channel and own Microsoft repository/key without affecting other products. | [Batch review](publisher-apps-11.md) |
| `workstation:package.HandBrake` | Accept RPM Fusion trust, then choose CLI or GUI package scope. | [Batch review](provider-foundation-07.md) |
| `workstation:package.Joplin` | Pin an owned deployment and preserve notebooks during inverse. | [Batch review](publisher-apps-10.md) |
| `workstation:package.NetworkMiner` | Pin portable artifact and preserve capture and analysis output. | [Batch review](forensic-isolated-05.md) |
| `workstation:package.Plaso` | Use a current packaged or isolated release, not the v2 URL-only stub. | [Batch review](forensic-isolated-02.md) |
| `workstation:package.PowerShell` | Choose a current publisher RPM/source with owned trust and Fedora 44 evidence. | [Batch review](publisher-apps-09.md) |
| `workstation:package.SpotifyClient` | Choose LPF or another reviewed provider and preserve profile state. | [Batch review](publisher-apps-11.md) |
| `workstation:package.UnfURL` | A pinned isolated user environment is now an operable opt-in candidate; no user-global pip change. | [Acceptance](../acceptance/package.dfir-unfurl.md) |
| `workstation:package.VeraCrypt` | Verify publisher artifact and license; preserve encrypted volumes. | [Batch review](publisher-apps-02.md) |
| `workstation:package.VisualStudioCode` | Own publisher repository/key and preserve user workspace and settings. | [Batch review](publisher-apps-03.md) |
| `workstation:package.Vivaldi` | Choose an exact publisher source and recover repository/key and browser profile. | [Batch review](publisher-apps-10.md) |
| `workstation:package.WoeUSB` | The old Fedora RPM path is gone; review WoeUSB-ng as a successor. | [Batch review](publisher-apps-09.md) |

## Split bundle or add an owned state handler (24)

| Source outcome | Path assessment | Evidence |
| --- | --- | --- |
| `server:package.AutoUpdate` | Separate DNF policy from the update timer and restore prior state. | [Batch review](generic-server-decisions.md) |
| `server:package.Docker` | Own repository, daemon, group, image, and volume boundaries. | [Batch review](generic-server-decisions.md) |
| `server:package.Glances` | Own package, service unit, port, and configuration separately. | [Batch review](generic-server-decisions.md) |
| `server:package.Required` | Split the broad package bundle into role-owned operations. | [Batch review](generic-server-decisions.md) |
| `workstation:package.ClamAV` | Separate signed RPMs from mutable signature database and update behavior. | [Batch review](system-security-28.md) |
| `workstation:package.Codecs` | Replace wildcard/group install with explicit packages and trusted source. | [Batch review](provider-foundation-05.md) |
| `workstation:package.CustomKbrdShortcut` | Make removal the exact inverse of journaled owned shortcuts. | [Batch review](desktop-user-remaining.md) |
| `workstation:package.Docker` | Separate package, repository, daemon, group, and container data state. | [Batch review](system-security-core.md) |
| `workstation:package.ExpressVPN` | Keep activation and profiles private; own package, service, and inverse. | [Batch review](system-security-risk-decisions.md) |
| `workstation:package.ExpressVPNProfiles` | Remove only recorded owned connection UUIDs. | [Batch review](system-security-risk-decisions.md) |
| `workstation:package.ExpressVPNafterBoot` | Replace text-based crontab filtering with an owned schedule inverse. | [Batch review](system-security-risk-decisions.md) |
| `workstation:package.Flathub` | Own remote trust and preserve apps installed through the remote. | [Batch review](provider-foundation-09.md) |
| `workstation:package.GnomeExtensions` | Split extension selection, acquisition, per-user state, and restore. | [Batch review](publisher-apps-17.md) |
| `workstation:package.GnomeRegion` | Decide inverse only after an owned locale setting records prior state. | [Batch review](desktop-user-configuration.md) |
| `workstation:package.KeyfileMounts` | Scope each mapping and prove backup, boot, and mount recovery. | [Batch review](system-security-risk-decisions.md) |
| `workstation:package.RPMfusionRepos` | Own signing keys and repository files before dependent packages. | [Batch review](provider-foundation-02.md) |
| `workstation:package.ScheduleExpVPNChange` | Remove only a journaled schedule and preserve unrelated jobs. | [Batch review](system-security-risk-decisions.md) |
| `workstation:package.SecurityLab` | Split the large mutable group into bounded owned tools or a group handler. | [Batch review](provider-foundation-06.md) |
| `workstation:package.SmartMonTools` | Model smartd service state changed by package installation. | [Batch review](system-security-smartmontools.md) |
| `workstation:package.Snap` | Model snapd service, confinement, installed snaps, and data recovery. | [Batch review](provider-foundation-12.md) |
| `workstation:package.Terminator` | Separate Fedora RPM lifecycle from user iBus hotkey restoration. | [Batch review](desktop-user-remaining.md) |
| `workstation:package.VMtoolsOnVM` | Split hypervisor detection and guest-service state; do not claim preinstalled RPMs. | [Batch review](publisher-apps-07.md) |
| `workstation:package.VPNProfiles` | Remove only RIDE-owned NetworkManager UUIDs. | [Batch review](system-security-risk-decisions.md) |
| `workstation:package.Wireguard` | Separate package tools from private keys, interfaces, and profile recovery. | [Batch review](system-security-risk-decisions.md) |

## Verify identity or target compatibility before choosing a path (5)

| Source outcome | Path assessment | Evidence |
| --- | --- | --- |
| `workstation:package.AppImageLauncher` | Project still publishes beta builds; Fedora 44 integration and seeded AppImage recovery are unverified. | [Batch review](publisher-apps-01.md) |
| `workstation:package.EmailHeaderAnlzr` | Verify the v2 source's current owner, maintenance, license, and service identity. | [Batch review](forensic-isolated-06.md) |
| `workstation:package.OpenconnectVPN` | Identify the intended VPN client and current package before replacing the unpinned source build. | [Batch review](system-security-risk-decisions.md) |
| `workstation:package.Pidgin` | Fedora 44 packages Pidgin and OTR, but combined messaging and key recovery remain unverified. | [Batch review](system-security-27.md) |
| `workstation:package.Xmind` | Choose the current publisher edition and package identity before pinning an install. | [Batch review](publisher-apps-15.md) |

## Original replacement assessments (10; nine remain)

These have explicit replacement dispositions in the ledger. EOL applies to
the named old products where stated; several others are platform or method
changes and must not be labeled EOL.

| Source outcome | Replacement assessment | Evidence |
| --- | --- | --- |
| `workstation:package.Required` | Split the v2 global package bundle into point-of-use prerequisites. | [Batch review](provider-foundation-01.md) |
| `workstation:package.DNFutils` | Fedora 44 DNF5 supplies the needed commands; the old package bundle is obsolete on this target. | [Batch review](provider-foundation-03.md) |
| `workstation:package.EzaGitHub` | Use the accepted Fedora Eza RPM; the mutable ZIP method is obsolete, not Eza itself. | [Batch review](provider-foundation-08.md) |
| `workstation:package.VersionLock` | DNF5 exposes versionlock without the v2 plugin package; policy-entry management remains separate. | [Batch review](provider-foundation-04.md) |
| `workstation:package.Flatpak` | Fedora Workstation supplies Flatpak; the unsafe v2 uninstall-all path is rejected. | [Batch review](provider-foundation-11.md) |
| `workstation:package.Macvendor` | The maintained standalone lookup script remains outside the v3 install catalog. | [Batch review](forensic-isolated-03.md) |
| `workstation:package.PackagingTools` | Initially replaced by 7zip and unar; the later Fedora unrar wrapper restored the command name and made the kept outcome operable. | [Acceptance](../acceptance/package.unrar.md) |
| `workstation:package.FirefoxAddons` | The existing policy helper manages repository-owned files outside the v3 catalog. | [Batch review](publisher-apps-04.md) |
| `workstation:package.YubikeyManager` | The old Manager GUI reached EOL; Yubico Authenticator is a separate product. | [Batch review](publisher-apps-08.md) |
| `workstation:package.YubikeyPersTool` | The old GUI is archived; Yubico Authenticator and ykman are separate paths. | [Batch review](publisher-apps-14.md) |

## Existing v3 package mappings (52)

These outcomes already have runnable v3 mappings: 30 supported on their
declared targets and 22 operable only as opt-in candidates. The linked
acceptance records and [ledger](../../migration/outcomes.json) state each
target and limit; this review does not broaden their support matrix.

| Source outcome | v3 operation ID(s) | Current readiness | Evidence |
| --- | --- | --- | --- |
| `server:package.PythonPip` | `package.python3-pip` | supported | [Acceptance](../acceptance/package.python3-pip.md) |
| `workstation:package.Alien` | `package.alien` | supported | [Acceptance](../acceptance/package.alien.md) |
| `workstation:package.ASN` | `package.asn` and ten Fedora prerequisite operations | opt-in candidate | [Acceptance](../acceptance/package.asn.md) |
| `workstation:package.BasicEditors` | `package.nano`, `package.vim-enhanced` | supported | [Acceptance](../acceptance/provider-basic-editors.md) |
| `workstation:package.Bat` | `package.bat` | supported | [Acceptance](../acceptance/package.bat.md) |
| `workstation:package.Binwalk` | `package.binwalk` | supported | [Acceptance](../acceptance/package.binwalk.md) |
| `workstation:package.Cheat` | `package.cheat` | supported | [Acceptance](../acceptance/package.cheat.md) |
| `workstation:package.Chromium` | `package.chromium` | opt-in candidate | [Acceptance](../acceptance/package.chromium.md) |
| `workstation:package.CyberChef` | `package.cyberchef` | opt-in candidate | [Acceptance](../acceptance/package.cyberchef.md) |
| `workstation:package.ClementinePlayer` | `package.clementine` | opt-in candidate | [Acceptance](../acceptance/package.clementine.md) |
| `workstation:package.CommanderFileMgrs` | `package.gnome-commander`, `package.mc` | opt-in candidate | [Acceptance](../acceptance/package.gnome-commander.md) |
| `workstation:package.Dc3dd` | `package.dc3dd` | supported | [Acceptance](../acceptance/package.dc3dd.md) |
| `workstation:package.Dia` | `package.dia` | opt-in candidate | [Acceptance](../acceptance/package.dia.md) |
| `workstation:package.Exif` | `package.exif` | supported | [Acceptance](../acceptance/package.exif.md) |
| `workstation:package.ExifTool` | `package.exiftool` | supported | [Acceptance](../acceptance/package.exiftool.md) |
| `workstation:package.Eza` | `package.eza` | supported | [Acceptance](../acceptance/package.eza.md) |
| `workstation:package.Fd` | `package.fd-find` | supported | [Acceptance](../acceptance/package.fd-find.md) |
| `workstation:package.Flameshot` | `package.flameshot` | opt-in candidate | [Acceptance](../acceptance/package.flameshot.md) |
| `workstation:package.GIMP` | `package.gimp` | opt-in candidate | [Acceptance](../acceptance/package.gimp.md) |
| `workstation:package.GnomeTools` | `package.system-config-printer`, `package.gnome-tweaks` | opt-in candidate | [Acceptance](../acceptance/provider-gnome-tools.md) |
| `workstation:package.Hexchat` | `package.hexchat` | opt-in candidate | [Acceptance](../acceptance/package.hexchat.md) |
| `workstation:package.Htop` | `package.htop` | supported | [Acceptance](../acceptance/package.htop.md) |
| `workstation:package.KeepassXC` | `package.keepassxc` | supported | [Acceptance](../acceptance/system-security-packages.md) |
| `workstation:package.KernelTools` | `package.kernel-devel`, `package.kernel-headers` | supported | [Acceptance](../acceptance/provider-kernel-tools.md) |
| `workstation:package.LibEWF` | `package.libewf` | supported | [Acceptance](../acceptance/package.libewf.md) |
| `workstation:package.Libpst` | `package.libpst` | supported | [Acceptance](../acceptance/package.libpst.md) |
| `workstation:package.Lynis` | `package.lynis` | supported | [Acceptance](../acceptance/package.lynis.md) |
| `workstation:package.Md5deep` | `package.md5deep` | supported | [Acceptance](../acceptance/package.md5deep.md) |
| `workstation:package.Ncdu` | `package.ncdu` | supported | [Acceptance](../acceptance/package.ncdu.md) |
| `workstation:package.NetCommsTools` | `package.minicom`, `package.putty`, `package.remmina` | opt-in candidate | [Acceptance](../acceptance/network-package-bundles.md) |
| `workstation:package.NetMgrL2TP` | `package.networkmanager-l2tp`, `package.networkmanager-l2tp-gnome` | supported | [Acceptance](../acceptance/system-security-packages.md) |
| `workstation:package.NetMgrLibreswan` | `package.networkmanager-libreswan`, `package.networkmanager-libreswan-gnome` | supported | [Acceptance](../acceptance/system-security-packages.md) |
| `workstation:package.PackagingTools` | `package.7zip`, `package.unrar`; `package.unar` optional | supported | [Acceptance](../acceptance/package.unrar.md) |
| `workstation:package.NetworkTools` | `package.tcpdump`, `package.wireshark`, `package.tftp-server`, `package.nmap`, `package.macchanger`, `package.flow-tools`, `package.nethogs` | opt-in candidate | [Acceptance](../acceptance/network-package-bundles.md) |
| `workstation:package.Projecteur` | `package.projecteur` | opt-in candidate | [Acceptance](../acceptance/package.projecteur.md) |
| `workstation:package.PulseAudioEq` | `package.easyeffects` | opt-in candidate | [Acceptance](../acceptance/package.easyeffects.md) |
| `workstation:package.Pwgen` | `package.pwgen` | supported | [Acceptance](../acceptance/package.pwgen.md) |
| `workstation:package.PyhtonAutopep8` | `package.autopep8` | supported | [Acceptance](../acceptance/package.autopep8.md) |
| `workstation:package.PythonPip` | `package.python3-pip` | supported | [Acceptance](../acceptance/package.python3-pip.md) |
| `workstation:package.Qbittorrent` | `package.qbittorrent` | opt-in candidate | [Acceptance](../acceptance/package.qbittorrent.md) |
| `workstation:package.Ripgrep` | `package.ripgrep` | supported | [Acceptance](../acceptance/package.ripgrep.md) |
| `workstation:package.ShellTools` | `package.pv`, `package.strace` | supported | [Acceptance](../acceptance/provider-shell-tools.md) |
| `workstation:package.SpeedtestCLI` | `package.speedtest-cli` | supported | [Acceptance](../acceptance/package.speedtest-cli.md) |
| `workstation:package.SystemMonitor` | `package.gnome-shell-extension-system-monitor-applet`, `package.lm-sensors` | opt-in candidate | [Acceptance](../acceptance/package.gnome-shell-extension-system-monitor-applet.md) |
| `workstation:package.Thunderbird` | `package.thunderbird` | opt-in candidate | [Acceptance](../acceptance/package.thunderbird.md) |
| `workstation:package.UnifyingOnLaptop` | `package.solaar`, `package.acpi` | opt-in candidate | [Acceptance](../acceptance/package.solaar.md) |
| `workstation:package.UnfURL` | `package.dfir-unfurl` | opt-in candidate | [Acceptance](../acceptance/package.dfir-unfurl.md) |
| `workstation:package.VLCPlayer` | `package.vlc` | opt-in candidate | [Acceptance](../acceptance/package.vlc.md) |
| `workstation:package.Volatility3` | `package.volatility3` | opt-in candidate | [Acceptance](../acceptance/package.volatility3.md) |
| `workstation:package.Wine` | `package.wine` | opt-in candidate | [Acceptance](../acceptance/package.wine.md) |
| `workstation:package.YouTubeDownloader` | `package.youtube-dl`, `package.yt-dlp` (opt-in alternative) | supported | [Acceptance](../acceptance/package.youtube-dl.md), [yt-dlp](../acceptance/package.yt-dlp.md) |

### Upstream changes found in existing v3 mappings

- `Hexchat`: [upstream announced its final release in 2024](https://hexchat.github.io/news/2.16.2.html),
  and [Fedora 44 lists the package as orphaned](https://packages.fedoraproject.org/pkgs/hexchat/hexchat/).
  Its VM-proven package install remains an opt-in candidate; a maintained
  GUI IRC path is now v3.0 work, with wider profile checks in H007.
- `SpeedtestCLI`: [upstream archived the repository in April 2026](https://github.com/sivel/speedtest-cli),
  while [Fedora 44 still packages it](https://packages.fedoraproject.org/pkgs/speedtest-cli/speedtest-cli/).
  The signed RPM install remains supported on its declared target; a maintained
  CLI path is v3.0 work, with wider network checks in H022.
- `YouTubeDownloader`: the [latest tagged youtube-dl release is from 2021](https://github.com/ytdl-org/youtube-dl/releases),
  though [Fedora 44 packages a later source snapshot](https://packages.fedoraproject.org/pkgs/youtube-dl/youtube-dl/).
  [yt-dlp is also available for Fedora 44](https://packages.fedoraproject.org/pkgs/yt-dlp/yt-dlp/).
  The existing operation proves installation only; a maintained downloader
  [yt-dlp path](publisher-apps-05-yt-dlp.md) is now supported as an opt-in
  alternative, with wider site checks in H023. Do not classify
  youtube-dl as EOL solely from the old release tag.

## Newly scoped generic server packages (6)

These source functions now have isolated `review` batches in the ledger. Their
acquisition candidates and ownership boundaries are in the
[v3.0 reassessment](v30-path-reassessment.md#formerly-excluded-server-package-paths).
The active source is still `network-devices`; adding a ledger row does not
transfer runtime ownership or establish a working install.

| Source outcome | Initial path | Evidence |
| --- | --- | --- |
| `server:package.qBittorrentServer` | Fedora `qbittorrent-nox` package, with service behavior separate. | [Path review](v30-path-reassessment.md#formerly-excluded-server-package-paths) |
| `server:package.PlexServer` | Publisher RPM repository with scoped trust and service state. | [Path review](v30-path-reassessment.md#formerly-excluded-server-package-paths) |
| `server:package.PlexAutoUpdate` | Owned repository plus explicit update policy. | [Path review](v30-path-reassessment.md#formerly-excluded-server-package-paths) |
| `server:package.AMP` | Reviewed publisher artifact or managed package. | [Path review](v30-path-reassessment.md#formerly-excluded-server-package-paths) |
| `server:package.Ferium` | Pinned publisher portable binary. | [Path review](v30-path-reassessment.md#formerly-excluded-server-package-paths) |
| `server:package.MinecraftServer` | Official Java server artifact and owned service path. | [Path review](v30-path-reassessment.md#formerly-excluded-server-package-paths) |

## Decisions and implementation order

- Keep prior retirement decisions as history about exact v2 implementations.
  The [v3.0 reassessment](v30-path-reassessment.md) reopens their useful
  capabilities for a working replacement where retained. The GNOME Files
  actions were subsequently retired by the owner. `GnomeExtInstaller` still
  lacks a runnable path. Opera is out of scope by
  explicit owner decision.
- Do not close a v3.0 package capability merely because its v2 selector was
  commented, its installer failed, or the exact old product ended. Verify the
  five identity cases before selecting the new path.
- Migrate retained products or successors through source-specific operations. Split
  repositories, bundles, services, settings, and private data by owner.
  Apply the existing risk-based VM gates in the [migration plan](../MIGRATION-PLAN.md).
- Review release and license evidence again when implementing a batch;
  this dated assessment is not package acceptance or proof of actual
  historical installation on any machine.
