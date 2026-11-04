# Legacy Fedora default migration ledger

Source: `default.preset` on `master` at `43ba467`. All 76 active lines have a
summary below. The v3 default profile is intentionally small; candidates and
deferred items are not silently executed. Current progress for the full scoped
v2 inventory is authoritative in `migration/outcomes.json` and its
[generated report](migrations/progress.md); this table is a navigation summary.

The [scoped workstation and server burndown](workstation-server-burndown.md)
also covers non-active library functions and the three server presets, apart
from outcomes the owner excluded as obsolete or host-specific.

| Legacy action | Current disposition | v3 target or rationale |
| --- | --- | --- |
| `DisableScreensaver` | supported opt-in state | Fedora 44 Workstation acceptance verified the explicit `screensaver-disabled` value, unchanged `lock-delay`, and exact recovery; no base profile selects it. |
| `SetupUserDefaultDirs` | operable opt-in candidate | `setting.user-default-directories` passed Fedora 44 Workstation lifecycle and recovery; H084 tracks path identity and empty-only restore. |
| `EnableFastDNF` | operable opt-in candidate | `setting.dnf5-fast-tuning` passed Fedora 44 Workstation lifecycle and effective-config checks; H093 tracks future DNF5 precedence changes. See the [system review](migrations/system-security-core.md). |
| `UpdateFedora` | opt-in candidate | `system.update-all-packages` passed full Fedora 44 Workstation and Server DNF5 transactions, report/journal checks, current status, reboot assessment, and non-restorable refusal. It remains explicitly invoked and outside profiles; H111 tracks broader failure/reboot hardening. See [acceptance](acceptance/system.update-all-packages.md). |
| `InstallRequired` | operable opt-in candidate | Seven individual Fedora RPM operations passed Fedora 44 Workstation lifecycle checks in `required-tools`; all remain installed on profile removal. The separate generic Server bundle is operable in two opt-in profiles; its Server nano operation is installed-only and H035 tracks the observed DNF upgrades. See [Workstation provider foundation batch 01](migrations/provider-foundation-01.md), [Server migration](migrations/generic-server-required.md), and [Server VM acceptance](acceptance/generic-server-required.md). |
| `InstallShellTools` | supported | Split into supported `package.pv` and `package.strace` in the opt-in `shell-tools` profile; see [VM acceptance](acceptance/provider-shell-tools.md). |
| `InstallRPMfusionRepos` | supported opt-in | Fedora 44 Workstation x86_64 lifecycle, exact inverse, and focused signature/digest/rollback failures pass. Upstream uses `gpgcheck=1` and `repo_gpgcheck=0`; see [provider batch 02](migrations/provider-foundation-02.md) and [acceptance](acceptance/setting.rpmfusion-repositories.md). |
| `InstallKernelTools` | supported | Split into signed Fedora `kernel-devel` and `kernel-headers` package installs; [VM evidence](acceptance/provider-kernel-tools.md) does not establish a matching module-build environment. |
| `InstallDNFutils` | replaced | Fedora 44 Workstation has DNF5 and plugins; current `config-manager` and `download` commands passed the disposable-VM check. See [provider foundation batch 03](migrations/provider-foundation-03.md). |
| `InstallEzaGitHub` | operable opt-in candidate | `package.eza-portable` pins the upstream GNU x86_64 release and owns `~/.local/bin/eza`; it passed [VM acceptance](acceptance/package.eza-portable.md) beside the Fedora RPM. |
| `InstallFlathub` | operable opt-in candidate | `setting.flathub-system-remote` owns the signed Flathub remote lifecycle; app deployments remain separate. H033 tracks broader app and GUI behavior. See [provider batch 09](migrations/provider-foundation-09.md). |
| `InstallAppImageLauncher` | operable opt-in candidate | Gear Lever passed Fedora 44 Workstation package lifecycle and preserved existing AppImages and launcher state. Remove the legacy `appimagelauncher` RPM first; H070 tracks visual integration and desktop conflicts. See [publisher batch 01](migrations/publisher-apps-01.md). |
| `InstallExif` | supported | `package.exif` is supported on Fedora 44 Workstation; see the [generated migration progress](migrations/progress.md). |
| `InstallMd5deep` | supported | `package.md5deep` is supported on Fedora 44 Workstation; see the [generated migration progress](migrations/progress.md). |
| `InstallLibEWF` | replaced | package.ewftools covers EWF utilities; verify library intent separately. |
| `InstallExifTool` | supported | Fedora `perl-Image-ExifTool` passed [VM lifecycle acceptance](acceptance/package.exiftool.md); the v2 GitHub/CPAN build path is not adopted. |
| `InstallASN` | operable opt-in candidate | `package.asn` and its declared Fedora dependencies passed Workstation lifecycle checks; H027 and H008 track live lookup and wider DNF effects. See [acceptance](acceptance/package.asn.md). |
| `InstallUnfURL` | operable opt-in candidate | `package.dfir-unfurl` uses an isolated Python environment and passed Fedora 44 Workstation acceptance; H025 tracks UI and wider parser coverage. See [acceptance](acceptance/package.dfir-unfurl.md). |
| `InstallCyberChef` | operable opt-in candidate | `package.cyberchef` passed Fedora 44 Workstation acceptance; H028 tracks visual interaction, browser compatibility, and updates. See [acceptance](acceptance/package.cyberchef.md). |
| `InstallChepy` | operable opt-in candidate | `package.chepy` passed Fedora 44 Workstation acceptance; H029 tracks dependency locking, plugin compatibility, wider transformations, and updates. See [acceptance](acceptance/package.chepy.md). |
| `InstallNetworkMiner` | operable opt-in candidate (`RemoveNetworkMiner` shares the outcome) | Fedora 44 Workstation lifecycle and Xvfb startup passed; restore/removal preserved seeded output. Mono/GTK remain a separate opt-in runtime profile. H110 gates any evidence processing or live capture. See [batch 05](migrations/forensic-isolated-05-networkminer.md) and [acceptance](acceptance/package.networkminer.md). |
| `InstallVeraCrypt` | supported opt-in | The pinned Fedora 44 Workstation GUI RPM passed detached-signature refusal, failed-transaction cleanup, mounted-volume refusal, and encrypted test-volume preservation across removal and reinstall. See [batch 02](migrations/publisher-apps-02.md) and [acceptance](acceptance/package.veracrypt.md). |
| `InstallPwgen` | supported | `package.pwgen` is supported on Fedora 44 Workstation; see the [generated migration progress](migrations/progress.md). |
| `InstallHtop` | supported | `package.htop` is supported on Fedora 44 Workstation; see the [generated migration progress](migrations/progress.md). |
| `InstallBat` | supported | `package.bat` is supported on Fedora 44 Workstation; see the [generated migration progress](migrations/progress.md). |
| `InstallNcdu` | supported | `package.ncdu` is supported on Fedora 44 Workstation; see the [generated migration progress](migrations/progress.md). |
| `InstallRipgrep` | supported | `package.ripgrep` is supported on Fedora 44 Workstation; see the [generated migration progress](migrations/progress.md). |
| `InstallFd` | supported | `package.fd-find` is supported on Fedora 44 Workstation; see the [generated migration progress](migrations/progress.md). |
| `InstallDocker` | supported opt-in | `system.docker-engine` passed Workstation and Server lifecycle acceptance, preserves Docker data on removal, and does not add users to the `docker` group. See [acceptance](acceptance/system.docker-engine.md). |
| `InstallVMFStools` | kept gap | The active v2 function only prints URLs. An opt-in [VMFS6 reader install candidate](acceptance/package.vmfs6-reader.md) is available for manual testing; its genuine VMFS6 fixture and read-only access test remain deferred to v3.1. |
| `InstallPythonPip` | supported | Fedora `python3-pip` passed [VM lifecycle acceptance](acceptance/package.python3-pip.md); omit the v2 global pip self-upgrade. |
| `InstallPackagingTools` | replaced | Fedora `7zip` and `unar` passed [VM package acceptance](acceptance/provider-archive-tools.md); `unar` is a different CLI from `unrar`. |
| `InstallBasicEditors` | supported | Split into Fedora `nano` and `vim-enhanced` package installs with [VM evidence](acceptance/provider-basic-editors.md). |
| `InstallTerminator` | opt-in candidate | Fedora [`package.terminator`](acceptance/package.terminator.md) and the separate [iBus hotkey setting](acceptance/setting.ibus-emoji-hotkey.md) passed Workstation VM lifecycles; use the root package command and per-user hotkey profile with `--allow-candidate`. See [batch 10](migrations/desktop-user-10-terminator.md). |
| `InstallAlien` | supported | `package.alien` is supported on Fedora 44 Workstation; see the [generated migration progress](migrations/progress.md). |
| `InstallSmartMonTools` | operable opt-in candidate | `package.smartmontools` is limited to signed RPM presence and its observed `smartd` side effect; H108 tracks hardware access, device selection, and monitoring recovery. |
| `InstallVisualStudioCode` | operable opt-in candidate | The owned Microsoft repository and RPM lifecycle passed Fedora 44 Workstation checks; broader desktop and update review remains in v3.1. See [publisher batch 03](migrations/publisher-apps-03.md). |
| `InstallHexchat` | operable opt-in candidate | Keep Fedora `package.hexchat` as a separate RPM deployment and Halloy as an opt-in successor; H007 tracks visual behavior, configuration import, and profile review. |
| `InstallNetworkTools` | operable opt-in candidates | The broad bundle is split across focused operations and profiles; H019 tracks capture, connection, and desktop behavior. |
| `InstallNetCommsTools` | operable opt-in candidates | The communications bundle is split into focused package operations and profiles; H019 tracks connection and desktop behavior. |
| `InstallNetMgrLibreswan` | supported opt-in | Fedora 44 Workstation package lifecycle is supported; keep application use in an opt-in profile pending v3.1 review. |
| `InstallSpeedtestCLI` | supported, with opt-in alternative | Keep Fedora `speedtest-cli` RPM and offer digest-pinned LibreSpeed CLI as an operable opt-in candidate; see [native RPM batch 03](migrations/native-rpm-03.md). |
| `InstallTecmintMonitorSh` | retired | Default profile must not fetch and execute remote scripts. |
| `InstallGnomeExtInstaller` | operable opt-in candidate | Fedora's signed browser connector RPM passed the Workstation lifecycle and preserves user extension state; browser add-on installation remains user controlled. See [provider foundation batch 10](migrations/provider-foundation-10.md) and [acceptance](acceptance/package.gnome-browser-connector.md). |
| `InstallBrave` | operable opt-in candidate | The owned Brave repository and RPM lifecycle passed Fedora 44 Workstation checks; broader desktop and update review remains in v3.1. See [publisher batch 03](migrations/publisher-apps-03.md). |
| `InstallChromium` | operable opt-in candidate | `package.chromium` passed its Fedora 44 Workstation package lifecycle; broader desktop, failure, recovery, and accessibility checks remain in v3.1. |
| `SetFirefoxPreferences` | operable opt-in candidate | `setting.firefox-preferences` keeps the v2 values in an opt-in Mozilla AutoConfig profile, owns three files with guarded recovery, and passed Fedora 44 Workstation startup acceptance. H083 tracks value freshness and a brief visible review before promotion or value changes. |
| `InstallFirefoxAddons` | operable opt-in candidate | `setting.firefox-addons` passed the full 16-XPI Fedora 44 Workstation apply, restart, recovery, and removal lifecycle. Keep candidate-gated; H115 tracks publisher license metadata, update behavior, and profile migration. See [publisher batch 04](migrations/publisher-apps-04.md) and [acceptance](acceptance/setting.firefox-addons.md). |
| `InstallYouTubeDownloader` | replaced | Review maintained yt-dlp packaging instead of legacy youtube-dl. |
| `InstallGnomeTools` | opt-in candidate | Fedora printer UI and GNOME Tweaks passed [package VM acceptance](acceptance/provider-gnome-tools.md); visual checks remain v3.1, and v2's unowned `gparted` removal is excluded. |
| `InstallSystemMonitor` | operable opt-in candidate | The monitoring packages passed their Fedora 44 Workstation package lifecycle; keep the profile opt-in while H012 tracks GNOME activation, visual behavior, and broader recovery. |
| `InstallGnomeExtensions` | deferred | Review current GNOME extension IDs and API. |
| `ShowDateInTaskbar` | operable opt-in candidate | `setting.gnome-clock-date` passed lifecycle checks; H018 tracks visual behavior and implicit-default recovery before promotion. |
| `ShowWeekNumbersInTaskbar` | operable opt-in candidate | `setting.gnome-calendar-week-numbers` passed lifecycle checks; H018 tracks visual behavior and implicit-default recovery before promotion. |
| `SetWindowCtlMinMaxClose` | opt-in candidate | One [GNOME string-setting operation](migrations/desktop-user-string-01.md) selects this or either alternative layout and restores the exact prior user override; [Workstation VM evidence](acceptance/setting.gnome-string-values.md). |
| `DisableMiddleButtonPaste` | operable opt-in candidate | `setting.gnome-primary-paste` passed lifecycle checks; H018 tracks visual behavior and implicit-default recovery before promotion. |
| `SetGnomeRegionDaDK` | opt-in candidate | The [region operation](migrations/desktop-user-string-01.md) takes an explicit validated locale value; the Danish profile passed [Workstation VM acceptance](acceptance/setting.gnome-string-values.md). |
| `SetScreensaverSlp10Lgn5` | supported on Fedora 44 Workstation | `setting.gnome-lock-timing` carries both retained 10/5 and 15/5 variants through exact four-key recovery; the Workstation VM verified both profiles, status, repeat, and restore. H092 tracks brief visible idle/lock behavior review. |
| `SetCustomKeyboardShortcut` | opt-in candidate | `setting.gnome-custom-shortcuts` merges owned GNOME entries and restores only RIDE-owned shortcut state; Fedora 44 Workstation lifecycle and preservation checks passed. H089 tracks visible dispatch and conflict review. |
| `SetGnomeCustomFavorites` | opt-in candidate | `setting.gnome-favorite-apps` accepts a configurable desktop-ID list and restores the exact prior dconf value; Fedora 44 Workstation plan/apply/repeat/conflict/restore acceptance passed. H085 tracks visual app-ID review. |
| `SetGnmLocationServiceOff` | operable opt-in candidate | `setting.gnome-location` passed lifecycle checks; H018 tracks visual behavior and implicit-default recovery before promotion. |
| `SetGnmAutoProblemRptOff` | operable opt-in candidate | `setting.gnome-problem-reporting` passed lifecycle checks; H018 tracks visual behavior and implicit-default recovery before promotion. |
| `SetPowerPercentageLow15` | opt-in candidate | The [shared UPower threshold operation](migrations/desktop-user-upower-01.md) selects 15 or 20 through an owned drop-in and exact restore; [Workstation VM evidence](acceptance/setting.upower-percentage-low.md). |
| `EnableBashAliases` | opt-in candidate | `setting.bash-aliases` manages exact marked loader and alias blocks; Fedora 44 Workstation interactive use and preservation passed. See [alias batch](migrations/desktop-user-aliases-01.md) and [VM acceptance](acceptance/setting.bash-aliases.md). |
| `SetAliasLsEza` | opt-in candidate | The owned alias operation invokes Eza only after checking the executable; its Workstation lifecycle passed. H090 tracks public-service review for the alias family. |
| `SetAliasWanIP` | opt-in candidate | Fixed `wanip`, `wanip4`, and `wanip6` aliases use ipify HTTPS endpoints only when invoked; the VM verified their definitions without making network requests. |
| `InstallBitwardenAppImage` | supported opt-in | The pinned AppImage and manifest passed Fedora 44 Workstation high-risk lifecycle acceptance, including synthetic vault preservation. Keep the user-scoped deployment opt-in; see [publisher batch 06](migrations/publisher-apps-06.md). |
| `InstallCheat` | supported | `package.cheat` is supported on Fedora 44 Workstation; keep it out of profiles until optional CLI profile review. |
| `InstallUnifyingOnLaptop` | operable opt-in candidate | The Solaar and ACPI package paths passed Fedora 44 Workstation lifecycle checks; H013 tracks receiver pairing and desktop behavior. |
| `InstallVMtoolsOnVM` | operable opt-in candidates | QEMU/SPICE and VMware package profiles are explicit and opt-in; H071 tracks display, clipboard, and shared-folder behavior on real guests. |
| `InstallYubikeyManager` | operable opt-in candidates | The maintained Authenticator GUI and `ykman` paths passed Fedora 44 Workstation package checks; H072 tracks optional GUI launch and test-key visibility. |
| `InstallSonosPlayer` | deferred | Review publisher source and architecture. |
| `SetHostname` | supported | Private `--value` operation journals and restores the exact prior static hostname; Fedora 44 Workstation and Server VM acceptance passed. See the [system review](migrations/system-security-core.md). |
| `EnableScreenSaver` | supported opt-in state | Fedora 44 Workstation acceptance verified the explicit `screensaver-enabled` value, unchanged `lock-delay`, and exact recovery; no base profile selects it. |
| `PressAnyKeyToContinue` | retired | Interaction belongs in CLI flow, not an operation. |
| `Restart` | retired | Reboot remains an explicit separate user action. |

## V3 release envelope and target matrix

The initial v3 release envelope is the small, data-only Linux client and its
declared Fedora package baselines. It does not imply replay of the 76-action
legacy default preset. A deferred ledger row is migration inventory, not a
release blocker unless a later scope decision selects it. Every required row
below needs target-specific acceptance before its profile or operation is
advertised as supported.

The kept `EnableSSHreboot`/`DisableSSHreboot` pair is implemented as the
opt-in `setting.ssh-reboot` candidate. Fedora 44 Workstation acceptance verified
the scoped rule, a real non-TTY SSH reboot, reconnect, and exact recovery. It
is not selected by a base profile; see [batch 18](migrations/system-security-18-ssh-reboot.md)
and [acceptance](acceptance/setting.ssh-reboot.md).

| Target and scope | Required v3 outcome | Current decision and evidence |
| --- | --- | --- |
| Fedora 44 x86_64 Workstation | `default`: `package.less`, `package.openssh-clients`, `package.exfatprogs` installed through the Fedora RPM provider. | Accepted for this edition after the [package batch](acceptance/workstation-package-batch-1-pilot.md), [OpenSSH client](acceptance/openssh-clients-workstation-pilot.md), and [combined profile](acceptance/workstation-default-profile-pilot.md) VM checks. Each operation links its acceptance record in the catalog. |
| Fedora 44 x86_64 Server | `server-base`: `package.less` and `package.openssh-clients` as a generic baseline. | Accepted for this edition after the [Server pilot](acceptance/server-base-package-pilot.md) and per-operation review. Other server functions remain in `network-devices`. |
| Fedora 44 x86_64 Cloud Base | Generic `package.exfatprogs` handler pilot. | Accepted only for `package.exfatprogs` after its [Cloud Base pilot](acceptance/package.exfatprogs-cloud-base-pilot.md) and edition gate; it does not establish Workstation or Server support. |
| Optional Fedora outcomes | `forensics` profile, unselected audit, artifact, and Python package candidates, and scoped deferred workstation/server outcomes. | Review in separate batches with explicit selectors and target evidence. Their absence does not block the package baselines above. |
| Unsupported targets and private behavior | Other Fedora releases or architectures, Debian/Ubuntu, and host-specific server values. | Fail closed. Add adapters or targets only after their own implementation and VM evidence; keep identities, secrets, and site values outside this repository. |

The official [Fedora 44 Workstation download](https://fedoraproject.org/workstation/download/)
offers an x86_64 Live ISO, not the qcow2 accepted by the current harness. Its
published 44-1.7 ISO SHA-256 is
`1620295f6a00c27c3208f0c00b8ece4eab1ec69b9002152d97488bf26a426ddf`.
Anaconda [does not support Kickstart installation from a Live ISO](https://anaconda-installer.readthedocs.io/en/latest/user-guide/troubleshooting/common-bugs.html#automatic-installation-in-live-os).
For automated base preparation, use a signed-checksum-verified Fedora 44
[Everything network installer](https://fedoraproject.org/en/misc/) with the
Workstation environment selected in Kickstart. The [2026-10-30 build](acceptance/fedora-44-workstation-image.md)
identified as `VARIANT_ID=workstation`; its installer and recipe checksums and
derived qcow2 digest are pinned in the [target matrix](../tests/acceptance/targets.json).
A modified Cloud Base image does not count as Workstation or Server evidence.
The [Server image build](acceptance/fedora-44-server-image.md) also uses the
verified Everything installer and a separate Kickstart environment selection;
its `VARIANT_ID=server` and qcow2 digest are pinned in the target matrix.

## Full scoped v2 migration program

The original ledger covered 165 grouped workstation and 15 grouped generic
server outcomes, including functions absent from active presets. The later
[capability reassessment](migrations/v30-path-reassessment.md) brought six
additional generic server package outcomes into isolated review batches. The
current denominator is 180 + 6 server outcomes - 1 Opera outcome = 185. Opera's
install and remove functions form one grouped outcome, so excluding the product
removes one row, not two. Install/remove and analogous state pairs share one
outcome throughout the inventory. The two Citrix functions, two Opera
functions, and seven remaining host-specific server actions stay visible in
the exclusion list, outside the 185-outcome denominator. The three
already supported base package operations remain valid release-envelope
evidence but do not automatically resolve a v2 outcome with different intent.

[OpenCTI Community Edition](migrations/opencti-server.md) is a separately
planned generic server operation for after v3.0. It has no v2 source
function, adds nothing to this denominator, and does not gate v3.0 release
review. Its eventual deployment will be opt-in and requires the stated
container-runtime, data, and security recovery evidence.

`migration/outcomes.json` assigns every outcome exactly one small batch, a
planned Fedora 44 x86_64 target, risk, source function mapping, current
disposition and progress, v3 operation IDs, evidence, blocker, and next action.
The generated [burndown](workstation-server-burndown.md) keeps the initial
legacy assessment alongside its current batch and progress. The v2 presets
show which functions were selectable, not which packages anyone installed;
active, commented, and library-only packages get the same source and product
review. Choose batch order by source viability, dependencies, and risk rather
than selector coverage. Ordinary batches contain at most six
related outcomes; security, storage, encryption, and difficult recovery
changes are isolated, while related user-state checks may share a batch. The family order is Fedora
repository packages, package-source foundations, forensic and isolated tools,
publisher applications, desktop and user state, system/network/security,
generic server, and explicit resolution decisions.

System Security 06 now migrates the kept MulticastDNS setting through Fedora
authselect's `with-mdns4` feature. Its exact profile selection and resolver
line recovery passed the pinned Fedora 44 Workstation VM; alternate authselect
profiles remain in H100, with the setting available only through an opt-in
profile.

From the repository root as a regular user, these commands read the ledger,
source inventory, catalog, and evidence without changing the host or writing
files. No recovery is needed. CI runs `--check` on every migration-branch push.

```bash
python3 tools/migration_progress.py --summary
python3 tools/migration_progress.py --json
python3 tools/migration_progress.py --check
```

The percentage counts supported operations, evidence-backed opt-in candidates,
and documented non-operable resolutions separately; the report never presents
a retirement, private handoff, or unsupported decision as an install. An
unreviewed or merely implemented candidate stays unresolved. The linked
v3.1 hardening queue records broader coverage without weakening v3.0 safety.

The first [native RPM batch](migrations/native-rpm-01.md) passed on 2026-10-30:
six v2 CLI package outcomes are supported on Fedora 44 x86_64 Workstation in
the opt-in `cli-tools` profile. The [resolution record](migrations/resolution-decisions.md)
retires information-only, placeholder, and obsolete behavior without claiming
those outcomes as installs. [Native RPM batch 02](migrations/native-rpm-02.md)
passed four more exact-target packages. Its investigated `alien` recovery
retains one named DNF dependency without losing or changing pre-existing RPMs;
that cleanup question is in the v3.1 queue.
[Native RPM batch 03](migrations/native-rpm-03.md) accepted Speedtest CLI as supported
and LibreSpeed CLI as an operable opt-in candidate; HexChat and Chromium are
operable opt-in candidates with desktop
hardening in v3.1. The owner later retired its two unavailable Nautilus
integrations individually. [Native RPM batch 04](migrations/native-rpm-04.md) passed
`dc3dd` as supported and four desktop RPMs as operable opt-in candidates;
each passed install and inverse checks in the disposable Workstation VM.
[Native RPM batch 05](migrations/native-rpm-05.md) passed Libpst and Lynis as
supported and Dia, Wine, and VLC as opt-in candidates. Dia retained named
GTK2 dependencies; Wine and VLC updated named pre-existing RPMs without
losing their package identities.
[Provider foundation batch 01](migrations/provider-foundation-01.md) accepted
`pv` and `strace` as supported operations in the opt-in `shell-tools` profile.
The owner later clarified that every v2 package remains in v3.0 scope, so its
earlier workstation `Required` replacement decision is reopened: seven
separate opt-in Fedora RPM operations now preserve those package capabilities.
The generic Server `Required` bundle remains a separate in-scope migration
batch. [RPM Fusion provider batch 02](migrations/provider-foundation-02.md)
is supported on Fedora 44 Workstation x86_64 with an opt-in profile. Its
verified trust path uses Fedora-packaged signing keys and exact owned recovery;
the release RPMs use `gpgcheck=1` and `repo_gpgcheck=0`.
[Provider foundation batch 03](migrations/provider-foundation-03.md) accepted
kernel development and Python pip RPM installs, documented DNF5 as the
replacement for `dnf-utils`, and accepted Fedora 7zip/unar package operations
as a changed-CLI archive replacement. DNF5 replaces the obsolete DNFutils
bundle on the declared Fedora 44 Workstation target; see its [acceptance
record](acceptance/dnf5-utilities.md).
[Provider foundation batch 04](migrations/provider-foundation-04.md) accepted
the editor RPMs as supported, the GNOME utility RPMs as opt-in candidates,
and DNF5 versionlock as a non-runnable replacement. The archived GNOME
extension installer was resolved as unsupported. Flathub and snapd remain
isolated for their data, service, and source gates.
[Provider foundation batch 05](migrations/provider-foundation-05.md) completed
its v3.0 migration outcome: the owner-kept codec set has Fedora package
operations, the RPM Fusion alternative remains an explicit opt-in candidate,
and the fixed-list Multimedia update action passed Fedora 44 Workstation
acceptance. That action is opt-in and non-reversible; H037 tracks broader
dependency-impact and recovery reporting for v3.1. [Batch 08](migrations/provider-foundation-08.md)
retains both Eza paths: the supported Fedora RPM and a pinned portable x86_64
GNU release deployed separately in the user's local bin. Disposable Fedora 44
Workstation acceptance verified coexistence and independent removal. Neither
is in a base profile; H068 tracks release refresh and architecture expansion.
[Provider batch 02](migrations/provider-foundation-02.md) records passing
Fedora 44 repository and package-use lifecycle evidence; the supported source
profile remains opt-in and documents its upstream metadata-signature boundary.
[Batch 06](migrations/provider-foundation-06.md) maps all 137 observed Fedora
Security Lab group members across forty-three opt-in profiles. The Tripwire
and USB capture/replay RPM-presence candidates passed their declared Fedora
44 Workstation lifecycle checks; USB device behavior remains outside RIDE.
Batch 06AI's nano-default-editor candidate passed package and Bash default /
override checks; CSH and fish runtime checks remain in H061. Batch 06AJ's
Nebula package-presence candidate passed Fedora 44 Workstation lifecycle with
no dependency or pre-existing package changes; its service remained inactive
and disabled. H062 tracks Nebula network/service configuration and H063 tracks NTPsec
sysuser, service, and clock recovery for v3.1. Accepted batches 06E through
06AH remain documented in the detailed batch record.
Batches 06J, 06K, and 06L passed
candidate and supported VM acceptance; 06M and 06N passed candidate acceptance
and remain candidate-gated pending H038 and H039, respectively. Batch 06N comprises five host integrity and compliance packages and passed
candidate VM acceptance; the operations remain candidate-gated pending H039.
Batch 06O adds four SNMP packages and passed candidate VM acceptance; the
operations remain candidate-gated pending H040. Batch 06P adds five offline password and credential recovery packages and
passed candidate VM acceptance; those operations remain candidate-gated pending
H041. Batch 06Q adds four wireless auditing packages and passed candidate VM
acceptance; the operations remain candidate-gated pending H042. Batch 06R adds
five SIP and network-load tools and passed candidate VM acceptance; those
operations remain candidate-gated pending H043 review of later authorized
traffic and recovery. Batch 06S adds five credential auditing and interception
tools and passed candidate VM acceptance; Hydra updated preinstalled expat,
which remains at the Fedora repository version after restore, and H044 tracks
later authorized-use review. Batch 06T adds four network monitoring packages
and passed candidate acceptance; vnStat stayed inactive and created no database,
but its system account persisted after package restore. H045 tracks later data
and service review. Batch 06U adds five packet-crafting/replay utilities; hping3
has inactive upstream development, and Scapy or Nping are alternatives to
review in v3.1. DNF retained packETH's `gtk2`, `ibus-gtk2`, and weak
`libcanberra-gtk2` dependencies after restore; H046 tracks later dependency and
packet-scope review. Batch 06V adds five network observation and packet
analysis tools; the candidate VM lifecycle passed, PADS remained inactive, and
the two named dependencies were removed on restore. H047 tracks capture and
packet-data recovery review. Batch 06W adds four filesystem utility packages;
the candidate lifecycle passed with an unchanged mount table, and two packages
were already installed. H048 tracks data-preserving recovery review. Thirty-six
group RPMs remain unmapped. Batch 06X isolates Dislocker; its candidate
lifecycle and alternatives inverse passed, and all 16 dependencies were
removed on restore. H049 tracks key and encrypted-volume recovery review.
Thirty-five group RPMs remained unmapped after 06X. Batch 06Y adds four console
clients and passed its Workstation package lifecycle; all seven added
dependencies were removed on restore. H050 tracks client protocol and
user-data review. Thirty-one group RPMs remained unmapped after 06Y. Batch 06Z
adds four web and HTTP tools and passed its package lifecycle; `httpd.service`
stayed inactive and two initially present packages were preserved. H051 tracks
private log and authorized retrieval review. Twenty-seven group RPMs remained
unmapped before batch 06AA. Batch 06AA isolates three disk/file sanitizers; package lifecycle
passed with an unchanged mount table, and its three added dependencies were
removed on restore. H052 retains the deeper safety gate. Twenty-four group
RPMs remained unmapped after 06AA. Batch 06AB isolates four ARP/TCP/TLS interception
and manipulation packages; the RPM lifecycle is package-only and candidate-gated.
No packet or connection behavior was exercised; H053 tracks later authorization
and network recovery. Twenty group RPMs remained unmapped after 06AB. Batch 06AC adds four network and security diagnostics tools as candidate RPM-only operations; package lifecycle passed with 15 dependencies removed and no pre-existing RPM changes. No source scans, endpoint connections, or SMTP transactions were performed. H054 tracks the behavioral gate. Sixteen group RPMs remained unmapped after 06AC. Batch 06AD isolates GParted as a candidate RPM-only storage application; its package lifecycle passed with no dependency changes and an unchanged mount table. No device enumeration or partition action occurred; H055 retains the deeper storage safety gate. Fifteen group RPMs remained unmapped after 06AD. Batch 06AE isolates the AFF forensic-image utilities RPM; package lifecycle passed, `afflib` was removed on restore, and no evidence image was accessed. H056 retains the deeper image provenance and recovery gate. Fourteen group RPMs remained unmapped after 06AE. Batch 06AF adds ProxyChains-NG and Scapy as candidate RPM-only operations. Fedora 44 Workstation apply/repeat/restore passed; Scapy's DNF transaction installed 357 packages and left `python3-tkinter` and `tk` after restore, with no pre-existing RPM updates. Neither tool or any network/packet behavior was run. H046, H057, and H058 track those v3.1 gates and dependency residue. Twelve Security Lab RPMs remained unmapped after 06AF. Batch 06AG adds the Security Lab menu package and SETools GUI as candidate operations. Fedora 44 Workstation lifecycle passed; DNF installed 8 and 29 packages and upgraded 11 pre-existing Qt/GStreamer RPMs, which restore did not reverse. No GUI or policy behavior was run; the menu contains launchers for the wider group, including absent packages. H059 tracks visibility, launchers, Apol behavior, and update recovery. Ten group RPMs remained unmapped after 06AG. Batch 06AH adds scanmem and unhide as candidate RPM-only operations; their package lifecycles passed on Fedora 44 Workstation, no scans were run, and H060 tracks later behavior review. Eight group RPMs remained unmapped after 06AH. Batch 06AI maps the Fedora default-editor member to the nano-default-editor RPM. Its package lifecycle and Bash default/override checks passed on Fedora 44 Workstation; CSH and fish runtime behavior remains in H061. Seven group RPMs remained
unmapped after 06AI. Batch 06AJ maps Nebula as an opt-in package-presence
candidate; the signed RPM lifecycle passed with no dependency or pre-existing
package changes, and the service remained inactive and disabled. H062 tracks
network and service configuration for v3.1. Six group RPMs remained after
06AJ. Batch 06AK maps NTPsec as package presence only; its RPM lifecycle passed,
chronyd was preserved, and `ntpd` remained inactive/disabled. The persistent
`ntp` nologin account is recorded for H063. Five group RPMs remained after
06AK. Batch 06AL maps the OpenSSH core outcome to the existing supported
`package.openssh-clients` operation and reuses unchanged Workstation/Server VM
evidence; no SSH server configuration is added. Four group RPMs remained after 06AL. Batch 06AM adds PSAD as an opt-in RPM-only
candidate; its 15-RPM transaction restored exactly and left nftables unchanged.
Three group RPMs remained after 06AM. Batch 06AN adds Fedora 44 RATS as an
opt-in legacy analyzer package; its signed RPM lifecycle passed without
dependencies or side effects. Flawfinder remains a narrower C/C++ alternative.
Two group RPMs remained after 06AN. Batch 06AO adds Tripwire as package
presence only. The Fedora 44 Workstation lifecycle passed after acceptance
was taught to verify Fedora's intentional hostname substitution in the sample
policy. Removal preserves that sample as `.rpmsave`; the candidate documents
and checks this config residue, while keys, policy signing, and baseline
behavior remain deferred to H066. Batch 06AP adds the Fedora USB capture/replay
RPM as an opt-in candidate; package lifecycle and exact removal recovery passed
without operating USB hardware. All 137 observed Security Lab members are
profiled across forty-three opt-in profiles.
continue through focused batches; the broad DNF group operation
remains excluded while profiles are built without dropping package
capabilities. [Batch 07](migrations/provider-foundation-07.md) now provides an
operable opt-in HandBrake CLI candidate from the accepted RPM Fusion provider.
The Fedora 44 Workstation lifecycle passed; imported RPM Fusion signing-key
trust remains after package removal, while the HandBrake RPMs and dependencies
return to baseline. GUI/Flatpak conflict review remains in H067.
[Provider batch 09](migrations/provider-foundation-09.md) closed the active
Flathub remote as an opt-in candidate pending broader ownership recovery.
[Batch 11](migrations/provider-foundation-11.md) now supports an opt-in,
installed-only Flatpak runtime on Fedora 44 Workstation; its unsafe v2
removal is not exposed. [Batch 12](migrations/provider-foundation-12.md)
adds an opt-in candidate Snap runtime. Fedora's signed RPM, socket activation,
repeat apply, state preservation, and `hello-world` execution passed on Fedora
44 Workstation. The host reports partial Snap confinement because AppArmor is
not enabled; RIDE does not manage Snap apps or data. H034 tracks confinement,
application lifecycle, and coexistence review.
[Forensic isolated batch 01](migrations/forensic-isolated-01.md) accepted
Fedora ExifTool and four opt-in forensic tools. The old VMFS no-op is
retired, while [its kept access capability](migrations/forensic-isolated-07-vmfs.md)
remains a high-risk, non-runnable v3.0 gap; the owner deferred the genuine
VMFS6 fixture and read-only lifecycle test to v3.1.
[Forensic isolated batch 02](migrations/forensic-isolated-02.md) passed a
non-root, hash-pinned Volatility 3 core venv and Plaso's GIFT COPR path as
opt-in candidates. The owner kept Plaso, Autopsy, and Volatility 2 for v3.0.
Autopsy's Sleuth Kit Labs Snap path is isolated in
[batch 09](migrations/forensic-isolated-09-autopsy.md) because the publisher
auto-connects privileged disk and FUSE interfaces. Volatility 2 uses the
documented isolated PyPy 2.7 compatibility path, now an opt-in candidate after
its pinned core CLI lifecycle passed Fedora 44 Workstation acceptance; H088
carries plugin compatibility and broader integrity checks.
[Forensic isolated batch 03](migrations/forensic-isolated-03.md) promoted
Fedora Binwalk and autopep8 after a shared exact-target RPM lifecycle and
documented standalone MAC vendor lookup as a non-runnable replacement.
The old Dumpzilla script is discontinued, while the kept Firefox analysis
capability has a separate [high-risk successor batch](migrations/forensic-isolated-08-firefox.md).
Isolated forensic [batch 04](migrations/forensic-isolated-04.md),
[batch 05](migrations/forensic-isolated-05-networkminer.md), and
[batch 06](migrations/forensic-isolated-06.md)
keep the BulkExtractor Snap package, NetworkMiner portable deployment, and
email-header service visible. BulkExtractor now has an opt-in pinned-artifact
path with Fedora 44 Workstation package/data recovery evidence; H113 tracks
actual evidence-processing behavior. NetworkMiner's fixed publisher artifact
and user-output recovery are operable candidates. Email-header analysis now
has a pinned MIT static-SPA source review and an opt-in user-scope
operation/profile. Its frontend contains no header network or
browser-persistence APIs; the launcher pins loopback and blocks external
connections with CSP. Focused mocked lifecycle tests pass. Dependency license
review, a real upstream build, and Fedora 44 acceptance remain. The remaining
outcomes stay visible in the progress report.

The first [publisher application](migrations/publisher-apps-01.md) replaces
the kept AppImage integration capability with Flathub Gear Lever. Its Fedora
44 Workstation package lifecycle passed; keep it opt-in while H070 tracks
visual integration and desktop-conflict review. AppImage file operations
remain user-controlled. The separate
[encryption application](migrations/publisher-apps-02.md) review migrates the
publisher-signed VeraCrypt GUI RPM. Its high-risk gate passed on Fedora 44
Workstation x86_64, and the operation is supported in its opt-in profile.
[Publisher batch 03](migrations/publisher-apps-03.md) implements opt-in
Microsoft VS Code and Brave RPM operations with fingerprint/signature checks,
owned repository-file cleanup, and preserved browser/editor profiles. Both
passed Fedora 44 Workstation lifecycle checks and remain candidate-gated;
broader failure and recovery review is in H002. [Batch 04](migrations/publisher-apps-04.md) now has an operable opt-in `setting.firefox-addons` lifecycle: all 16 XPIs passed Fedora 44 Workstation apply, restart, staged recovery, and removal checks. Keep it candidate-gated while H115 reviews publisher metadata, updates, and profile migration; see the [acceptance record](acceptance/setting.firefox-addons.md).
[Publisher batch 05](migrations/publisher-apps-05.md) supports the Fedora
`youtube-dl` RPM and accepts System Monitor Next plus hardware sensors as a
curated opt-in package/profile candidate. The broad GNOME extension script
is a separate [high-risk outcome](migrations/publisher-apps-17.md),
non-runnable until user-owned extension recovery is proved.
[Publisher batch 06](migrations/publisher-apps-06.md) replaces the broken
Bitwarden AppImage path with a pinned publisher asset and an owned user-file
inverse; Fedora 44 Workstation acceptance passed and the operation is
supported. Review launcher visibility, desktop integration, and profile
coexistence before extending its scope. Publisher batches 07-08 accept Solaar and ACPI as a curated
opt-in package/profile candidate after the Fedora 44 VM lifecycle, defer
conditional VM guest tools until a hypervisor-specific owned inverse is
proved, and document the discontinued YubiKey Manager GUI handoff to
publisher-supported alternatives. The runnable candidate does not claim
receiver pairing or battery readings; H013 tracks the desktop and hardware
review for v3.1.
[Publisher batch 09](migrations/publisher-apps-09.md) accepts signed Fedora
GNOME Commander and Midnight Commander as a curated opt-in profile after a
combined package and profile VM lifecycle. Teams web access replaces the
unsupported Linux desktop client; the deprecated Sonos AppImage is retired;
PowerShell, WoeUSB, and Etcher remain non-runnable on their documented
source/ownership triggers; the owner retained all three for migration.
[Publisher batch 10](migrations/publisher-apps-10.md) retires Atom editor
and its plugin set after upstream sunset, and records Arduino IDE, Discord,
Joplin, and Vivaldi as non-runnable until their respective portable or
publisher-RPM acquisition and inverse contracts pass. The owner retained
Arduino IDE, Discord, and Joplin and deferred Vivaldi. These remain outside
the small v3 base profiles; their v2 selector state does not establish whether
they were used.
[Publisher batch 11](migrations/publisher-apps-11.md) accepts Clementine
and the PipeWire-compatible EasyEffects replacement for the misleading
`PulseAudioEq` source as separate opt-in candidates after exact-target RPM
and profile lifecycles. Chrome, Edge, and Spotify remain non-runnable until
their distinct publisher repository, key, LPF, and profile-preserving inverse
contracts pass. The owner retained Chrome, Edge, and Spotify for migration
and excluded Opera from the v3 migration; no v3 Opera install is planned.
[Publisher batch 12](migrations/publisher-apps-12.md) closes the commented
Bitwarden desktop RPM until a pinned publisher artifact and vault-safe
inverse meet the high-risk gate. [Batch 14](migrations/publisher-apps-14.md)
documents the archived YubiKey Personalization GUI handoff to current
Yubico tools without claiming a managed install. [Batch 15](migrations/publisher-apps-15.md)
keeps Xmind non-runnable until its current RPM, edition, and document-safe
inverse are owned. Projecteur and Cheat are reviewed separately in batches
13 and 16. [Projecteur](migrations/publisher-apps-13.md) is an opt-in
Fedora RPM candidate after package/profile VM checks; Spotlight behavior
is H017 in v3.1. [Cheat](migrations/publisher-apps-16.md) is a supported
Fedora RPM after the same exact-target package lifecycle, replacing the
unowned v2 binary download without expanding `default`.

The [GNOME boolean batch](migrations/desktop-user-boolean.md) passes five
fixed per-user settings in a disposable Fedora 44 Workstation VM, covering
seven v2 outcomes across desktop-user-02, -04, and -09. The opt-in
`gnome-shell-preferences` and `gnome-privacy` profiles require
`--allow-candidate`; they preserve the effective prior boolean on restore.
The [string and UPower review](migrations/desktop-user-configuration.md)
closes five other outcomes as non-runnable until exact user-state or
administrator-file recovery is available. The resulting checked-in progress
was 113/180 scoped outcomes at that handler milestone. The
[remaining desktop review](migrations/desktop-user-remaining.md) then closed
20 more outcomes with documented non-runnable decisions, including the
separate high-risk lock and idle batch. The generated report is authoritative
as later batches change it.

The [core system review](migrations/system-security-core.md) closes the
active hostname prompt, DNF tuning, unbounded update, and Docker composite
as non-runnable pending their distinct state and recovery contracts. DNF5
does not silently replace the old 15-download tuning.
The [high-risk system review](migrations/system-security-risk-decisions.md)
records source-specific non-runnable decisions for VPN connections and
credentials, destructive disk and LUKS behavior, VMware kernel modules,
network name resolution, and passwordless reboot policy. These stay outside
the v3.0 executable catalog until their owner and safety gates pass.

The [network package bundle](migrations/system-security-network-tools.md)
passed a disposable Workstation VM check and remains opt-in candidate while
application behavior stays in H019. The
[Server Python pip package](migrations/generic-server-python.md) passed on the
pinned Server edition, reusing the existing signed Fedora handler. The
[remaining generic Server review](migrations/generic-server-decisions.md)
keeps `network-devices` source ownership and closes its other scoped
outcomes with individual non-runnable reasons and triggers. The
[screensaver resolution](migrations/resolution-decisions.md) closes the
conflicting v2 preset actions without selecting a lock policy silently.
The [package-only security batch](migrations/system-security-packages.md)
passed scoped VPN-plugin and KeePassXC package lifecycles plus a targeted
partial-failure restore; vault and connection behavior stay outside those
operations. The [SmartMonTools probe](migrations/system-security-smartmontools.md)
found that the RPM enabled `smartd`, so that outcome remains non-runnable
until a service-aware inverse exists. Pidgin/OTR and ClamAV signatures have
their own [security decisions](migrations/system-security-27.md) and
[signature decision](migrations/system-security-28.md). Pidgin/OTR are
retired from v3 by explicit owner direction; ClamAV remains in v3.0 scope.

The kept ClamAV outcome has an opt-in `package.clamav` candidate that snapshots
and restores the prior signature tree, records package roots and FreshClam unit
states, and rolls back a failed or unconfirmed one-shot update. Focused mocked
lifecycle and tree-recovery tests and Fedora 44 Workstation acceptance pass;
H109 tracks broader signature database and update hardening. See the
[candidate acceptance record](acceptance/package.clamav.md).

The kept `KeyfileMounts` outcome has an opt-in `setting.keyfile-mounts`
candidate for one explicitly selected mapper. Focused tests and Fedora 44
Workstation encrypted-data, exact-restore, and reboot acceptance pass. It
remains outside base profiles; see the [batch record](migrations/system-security-25-keyfile-mounts.md).

The earlier 2026-10-30 ledger result was **180/180 scoped outcomes dispositioned**:
28 supported, 26 operable opt-in candidates, 13 replaced, 17 retired, and
96 unsupported. Runnable source outcomes total 54; 26 require
`--allow-candidate`. These counts precede the six server package additions
and the Opera exclusion. The current ledger reports **180/185 outcomes
dispositioned (97.3%)** and **148/169 package and setting capabilities
operable (87.6%)**, with five unresolved source outcomes, five v3.0 capability
gaps, and eleven owner exclusions outside the denominator. ExpressVPN Workstation
startup auto-connect now has a documented publisher-GUI replacement; old
unowned cron cleanup remains manual. The two ExpressVPN
package outcomes returned to active migration, and the owner-supplied
v14.3.1.15429 installer signature is now verified. Fedora 44 install/remove
and recovery remain untested. Runnable source outcomes total 151; 100 require
`--allow-candidate`. Use the
[generated progress report](migrations/progress.md) for current status.
The owner's later [v3.0 capability reassessment](migrations/v30-path-reassessment.md)
supersedes disposition-only completion for package and setting outcomes. It
identifies 169 in-scope package/setting capabilities including six formerly
excluded server package outcomes. The 54 operable mappings recorded in that
initial reassessment have since grown to 148/169; see the current ledger and
generated report above for the authoritative count.
Exact old products may be replaced, and the owner may explicitly retire a
capability through the fast-track review. The owner retired both GNOME Files
context actions. The owner also kept
RPM Fusion and archive-tool capabilities and specified DNF5 as the DNFutils
replacement. Historical "reopen only" review triggers
in batch records now describe the evidence needed for a v3.0 path, not
optional deferrals.
The [v3.0 review note](release-v3.0-review.md) identifies opt-in candidates
and remaining release checks. No v3 tag is implied by ledger completion.
Implementation commit `445810a` passed the
[v3 validation workflow](https://github.com/tjuuljensen/ride-fedora/actions/runs/41070406118)
and [shell executable-mode workflow](https://github.com/tjuuljensen/ride-fedora/actions/runs/41070406164).
Local shell, catalog, generated-doc, ledger, mocked and Firefox tests,
Python compilation, and acceptance collection also passed. The final
supported VPN-plugin and KeePassXC profiles passed the declared Workstation
VM without a candidate override; the shared Python pip operation passed
its Server VM. Those checks remain valid for unchanged components, but the
branch is no longer ready for v3.0 release review under the clarified scope.

The original 99 non-runnable `unsupported` rows have a separate
[decision triage](migrations/unsupported-triage.md): 10 original retirement
proposals, 38 individual keep-or-drop choices, and 51 original migration-design
decisions. The owner retired NautilusHash and NautilusImageTools; deferred
GnomeExtInstaller; migrated GnomeRegion through an explicit empty-string
region value with exact recovery on Fedora 44 Workstation; and retained portable
Bitwarden, six R2 inverse outcomes, BalenaEtcher, ArduinoIDE, Discord, Joplin,
Xmind, Chrome, Edge, SpotifyClient, HandBrake, PowerShell, and WoeUSB for
migration. The owner also deferred Vivaldi, retired Pidgin/OTR, and retired
the scoped Opera outcome, later excluding Opera from the v3 migration.
The [package path review](migrations/package-path-review.md) evaluates all
133 scoped package outcomes across existing migrations, replacements,
retirements, and unresolved paths. It distinguishes discontinued products
from obsolete acquisition methods and records the path required for each
non-runnable package. A commented v2 selector is never evidence of non-use.
The review also flags the existing HexChat, Speedtest CLI, and youtube-dl
package mappings for v3.0 successor paths. H007, H022, and H023 now name only
the broader v3.1 behavior checks. Their exact-target package-install evidence
remains valid while those paths are evaluated.
The retained outcomes require owned state and recovery; their unsafe v2
methods remain non-runnable. The current 96 unsupported rows comprise 68
migration-design outcomes, 23 keep-or-drop choices, and five deferred owner
decisions. Owner choices update next actions without changing legacy source
code or machine state.

For low-risk Fedora RPMs, use a focused automated plan/apply/repeat/status,
signature/files, and declared remove/restore check on each exact target; reuse
failure-injection evidence for an unchanged handler within the batch. For
third-party or desktop behavior, a VM happy path and focused mocked checks may
establish an opt-in candidate, with broader coverage in v3.1. Data, storage,
encryption, security policy, and difficult recovery require deeper safety and
inverse evidence before becoming runnable. Unsupported or private decisions
need a documented reason and review trigger. Keep candidate operations out of
`default` and `server-base`; add curated opt-in profiles as related operations
are ready. Manual checks are limited to behavior automation cannot observe.

The `high` risk label alone does not impose that deeper gate. For an opt-in
outcome outside those named safety domains, explicitly record its
`safetyDomains`, pass its exact-target lifecycle, and name its v3.1 hardening
item. A high-risk outcome in a deep-safety domain must also carry a passed
`safetyReview` with the domain-specific checks and linked evidence documented
in the acceptance record. The progress checker rejects unclassified high-risk
candidates and deep-domain candidates without that evidence.

The full v3.0 migration is ready for release review when every scoped v2 package and
setting capability has an operable v3 implementation, evidence-backed
functional replacement, or explicit owner-approved retirement, the six newly scoped server package outcomes have
working paths or evidence-backed functional replacements, supported profiles
pass their declared targets, relevant CI and generated-doc checks pass, and no
shared Windows contract drift remains unexplained. A v3 tag and movement of
the `master` release line are separate publication decisions.

## Cross-platform alignment for final v3

Added 2026-11-01 at the user's request. These engineering/release tasks supplement
the existing scoped migration and native acceptance gates; they do not add or
close legacy outcomes. Fedora and Windows maintainers own their respective
consumer work. Use the same ALIGN IDs in the
[Windows task list](https://github.com/tjuuljensen/ride-windows/blob/codex/ride-v3-migration/TODO.md#cross-platform-alignment-for-final-v3).
The [shared contract](https://github.com/tjuuljensen/ride-windows/blob/codex/ride-v3-migration/docs/models/ride-behavior-contract.md)
owns the rules; [Windows alignment](windows-alignment.md) owns local differences.

- [x] **ALIGN-01:** Adopt canonical contract 1.1.0 and matching SHA-256 references
  in both repos. Source documentation complete; immutable publication is ALIGN-09.
- [x] **ALIGN-02:** Add reciprocal AGENTS review/versioning rules covering CLI,
  settings, planning, acquisition, privilege and recovery, not only package batches.
- [ ] **ALIGN-03:** Declare unset semantics, restrict profile removal to eligible
  operation classes, reject conflicting ID/profile and irrelevant options, and
  transition bare remove to require an explicit selector. Coordinate the Windows
  argument/default-remove and exclusion-help changes. Done when mocked tests
  prove refusal before mutation and preserve explicit set and saved recovery.
  Fedora implementation and focused tests are recorded in
  [Windows alignment](windows-alignment.md); the Windows counterpart remains open.
- [ ] **ALIGN-04:** Separate download eligibility from VM execution acceptance;
  unify target/identity preflight for all restore previews, including the iBus
  branch. Coordinate Windows flag-free candidate preview and installed-package
  no-op exception review. Done when paired RB-03/04/05/08 cases retain actual
  mutation gates and demonstrate zero preview writes/run creation. Fedora's
  download and restore-preview changes and focused regression tests are recorded
  in [Windows alignment](windows-alignment.md); Windows counterpart review remains.
- [ ] **ALIGN-05:** Add pinned shared scenario data and the native Bash/Python
  adapter/CI alongside Windows Pester. Cover candidate/target/privilege gates,
  invalid arguments, unset/removal, dependencies, partial failure/recovery,
  acquisition and read-only completion. Done when both report the same revision
  and a seeded mismatch fails without using a live workstation for mutation.
  Fedora now pins the 12-case revision 1.1.0 and maps the privilege and
  dependency-order additions to CLI unittests. Fedora restore-preview identity
  is also tested in a UID 0 user/mount namespace; run Windows Pester before
  closing ALIGN-05.
- [x] **ALIGN-06:** Structure the local capability/difference register with stable
  IDs, owners, reasons, RB rules, reviewed revisions/evidence, linked tasks and
  review/removal triggers. Done when every current comparison row is aligned,
  an intentional platform difference, or a named temporary gap. Fedora has a
  20-entry register with CI hash/schema checks; the [reconciliation index](windows-alignment.md#reconciliation-of-earlier-batch-comparisons)
  maps the older package-level notes to those stable dispositions.
- [ ] **ALIGN-07:** Add linked-change review templates and scheduled/manual
  read-only drift reports against newer contract/peer capabilities. Keep PR
  checks pinned; never auto-merge updates. Done when a deliberate upstream
  change is detected and both consumer tasks carry compatibility and evidence.
- [ ] **ALIGN-08:** Add paired explicit-profile/state usage examples, compatible
  ID/view status selectors and a scoped versioned machine-output interface.
  Preserve native syntax and source/variant distinctions. Done when applicable
  examples and versioned output cases pass on each client.
  Fedora's `show --stdin` emits ordered schema-1 JSON records and preserves
  existing positional fields. Both clients now implement explicit ID and view
  status selectors while preserving their positional syntax; Linux uses
  `--id`/`--view`, Windows uses `-OperationId`/`-View`. Fedora has focused CLI
  coverage; Windows CLI routing, engine-filter, and catalog-completion Pester
  cases are added but await execution. Paired profile/state examples are now in
  both READMEs; machine-output cases and native test results remain before
  ALIGN-08 can close.
- [ ] **ALIGN-09:** Before final v3, record the immutable published contract
  reference, verify both digest pins, close preceding tasks or record explicit
  owner-approved deferrals, and review the final consumer implementations.
  Keep native target acceptance and publication separate; neither identical
  catalog coverage nor synchronized client release numbers is required.

Adoption evidence: matching contract 1.1.0 digest references, reciprocal AGENTS
rules and linked local task lists. Validation is documentation/link/digest/diff
inspection; no Linux command, installer, VM or supported target was changed.
Resolved: contract ownership/version and reciprocal policy. Partial: source policy
only. Deferred at adoption: ALIGN-03 through ALIGN-09. Retired/excluded or completed legacy
outcomes: none; `migration/outcomes.json` and generated counts remain unchanged.
Current alignment status: ALIGN-06 is complete; ALIGN-03 through ALIGN-05 and
ALIGN-07 through ALIGN-09 remain open. Next batch: run Windows Pester against the
shared 1.1.0 adapter, then continue the remaining alignment tasks. Fedora's full
`restore --dry-run` path now runs in an isolated user/mount namespace with
effective UID 0 and proves refusal before observation or journaling.
Fedora's ALIGN-03/04 implementation, ALIGN-05 scenario adapter, and ALIGN-06
register are recorded in [Windows alignment](windows-alignment.md); release-wide
closure remains outstanding.

## Release gates

- Complete the [final-v3 alignment tasks](#cross-platform-alignment-for-final-v3), or record explicit owner-approved deferrals; adopting the contract alone does not prove conformance.
- Candidates remain blocked by default and require `--allow-candidate` for an
  explicit change. An implemented outcome counts as operable only after its
  risk-appropriate focused evidence; support still requires a passing VM on
  the exact declared target.
- The Firefox add-on operation has an operable opt-in catalog lifecycle on Fedora 44 Workstation; it remains candidate-gated while H115 reviews publisher metadata, updates, and profile migration.
- Three package/setting gaps remain in the generated [migration progress report](migrations/progress.md): VMFS6 access, Workstation ExpressVPN scheduled rotation, and Server VPN randomizer ownership and recovery. Close each with evidence or record an explicit owner-approved v3.0 deferral before freezing release scope.
- The supplementary [legacy source audit](legacy-source-audit.md) identifies helper libraries outside the 185-row outcome ledger. Record whether each group is reference-only, standalone, or in a later migration; do not infer migration from a matching product name.
- Generic server actions remain in `network-devices` until source, consumers, ownership, and rollback are reconciled. No host-specific preset is moved into this repository.
- Debian and Ubuntu adapters remain outside the supported target matrix until their own VM checks pass.

## Batch delivery and evidence

Use this plan as the handoff record for phased migration. A batch names its
operation IDs or legacy outcomes, source owner, target VM, dependencies,
expected prior and final state, recovery limit, acceptance checks, status,
revision, dated evidence, and exact next action. Keep source readiness separate
from runtime activation and verified behavior. The three base package
operations are verified on their declared editions; optional source outcomes
have supported, candidate, or non-runnable decisions in the ledger.

| Stage | Agent work | Owner or runtime input | Completion evidence |
| --- | --- | --- | --- |
| Select | Group a small related outcome set; identify catalog IDs and deferred neighbors. | Choose a target and provide a disposable VM when runtime testing begins. | Named scope, target distro/release/CPU, owner, and exclusions in this plan. |
| Assess | Trace legacy behavior, consumers, upstream source, data ownership, dependencies, detection, and inverse. Compare catalog, profile, and run-state fields and their semantics with the Windows development branch. | Resolve host-specific values only if the selected operation needs them. | Current-to-v3 mapping, risks, recovery limits, and any intentional schema or behavior differences recorded in `windows-alignment.md`. |
| Implement | Prepare catalog, handler, profile, docs, and focused tests; run static and mocked checks. | Review only decisions that cannot be derived from source or established scope. | Reviewable patch and `source-ready` status after relevant CI passes. |
| Activate | Apply the prepared revision only in a disposable target VM; record exact command and snapshot. | Supply VM access or run the documented commands. | VM log and `deployed-awaiting-verification` status. |
| Verify | Check plan, apply, repeat apply, status, removal or restore, partial failure, and package or artifact evidence. | Confirm any user-visible desktop behavior that automation cannot observe. | Dated `docs/acceptance/<operation-id>.md` results and `verified` or failed status. |
| Close or recover | Recheck the shared contract after implementation; promote only accepted target rows. Otherwise restore the VM snapshot, retain candidate status, and record the failure. | Provide further observations only when a check depends on them. | Updated catalog, migration row, Windows alignment review, evidence, and concrete next action. |

### Practical test scope for remaining batches

- Define completion criteria before testing: the selected operation and target,
  expected prior and final states, required lifecycle and failure checks,
  artifact or signature proof, recovery limit, evidence location, and any
  user-visible observation. State which result permits promotion and which
  leaves the operation a candidate.
- Run focused automated checks for changed code and reuse dated evidence for
  unchanged handlers or contracts when its revision, target, source, and
  behavior still apply. Record that reasoning in the batch evidence. A Cloud
  Base result cannot substitute for Workstation or Server target acceptance.
- Automate VM preparation, command execution, evidence collection, and
  recovery. Use one brief manual session only when user-visible behavior needs
  direct observation, such as desktop integration; record its exact checks.
- Expand coverage for changes involving user data, storage, encryption,
  security policy, or difficult recovery. Keep optional additions and
  unsupported scenarios in their own queue unless they are required for the
  selected migration outcome or a declared supported target.
- Investigate a failed run and record its cause or current uncertainty before
  retrying. Fix the defect or test environment first; do not repeat an
  unchanged long-running scenario merely to seek a pass.

Repeat the cross-repository schema and behavior review for every package batch
and at release-candidate preparation. Compare product identity, distribution,
deployment, provider selection, artifact evidence, profile selection, run-state
ownership, and recovery semantics. Alignment is required for shared behavior,
not for platform-specific syntax or handlers. Record each deliberate difference
with its reason and next review trigger in
[Windows alignment](windows-alignment.md). Record the compared branches or
revisions and review date in the batch evidence; treat an unexplained
difference as unfinished migration work.

The first Fedora 44 x86_64 Workstation VM package pilot covers `package.less`
and `package.exfatprogs`. Run CI first, then use `plan`, `apply`,
repeat `apply`, `status`, `remove`, and `restore` as applicable. Keep the VM
snapshot until recovery is checked. A green static check or source commit alone
does not promote an operation to `supported`. Server, Firefox, third-party
artifact, and Waydroid work should use separate batches because their state
and recovery differ.

The [disposable VM harness](acceptance/VM-HARNESS.md) provides Fedora 44 Cloud
Base and Workstation package pilots. The [Cloud Base pilot](acceptance/package.exfatprogs-cloud-base-pilot.md)
passed lifecycle and partial-failure scenarios on clean commit `9cc6416`; the
[Workstation pilot](acceptance/workstation-package-batch-1-pilot.md) passed its
focused scenarios on the pinned edition image. The Cloud result informs the
shared handler review but cannot replace edition-specific acceptance.
`package.exfatprogs` was a candidate during those pilots; its declared Cloud
Base and Workstation targets are now accepted in the per-operation record.

### Workstation package batch 1: completion criteria

Scope: `package.less` and `package.exfatprogs`, Fedora 44 x86_64 Workstation,
default `fedora-rpm` source, system scope. Fedora owns the RPMs; RIDE owns the
catalog selection, DNF handler, and run journal. The required prior state is
the observed, recorded package inventory of each fresh VM overlay. If either
package is already present in the installed image, use a separate disposable
overlay with that package deliberately removed to test the install path; do
not count an unchanged apply as install evidence.
The [Windows schema and behavior preflight](windows-alignment.md#fedora-workstation-package-batch-preflight-2026-10-30)
compared Linux `0bfd3c0` and Windows `17f9cef` on 2026-10-30; repeat it if the
package contract changes before promotion.

Pass only if the pinned Workstation guest identifies as Fedora 44 x86_64 with
`VARIANT_ID=workstation`; read-only plan changes nothing; apply installs absent packages;
repeat apply is unchanged; status matches RPM observation; RPM signature and
files verify; restore and explicit remove recover RIDE-owned new installs;
package inventory returns to its recorded baseline after recovery; and a
focused injected failure leaves an accurate journal and recoverable completed
steps. Record any limit on reinstalling a pre-existing package. Use the clean
Cloud Base pilot as evidence for unchanged DNF handler logic, while recording
why that reuse applies; run the edition-specific lifecycle checks here. These
command-line packages need no desktop manual session.

Status: focused pilot PASS for both operations on the pinned Workstation target
as recorded in the [batch evidence](acceptance/workstation-package-batch-1-pilot.md).
The [edition gate pilot](acceptance/fedora-44-variant-gate-pilot.md) then passed
on Cloud Base and Workstation for the declared operation/edition pairs. Both
were candidates at that stage: source was dirty during the VM runs, and the
target row change invalidated signatures of any older run. Subsequent source
equivalence, edition gate, technical review, and the owner's confirmation that
no non-disposable v3 runs exist cleared those gates. The full Workstation
default profile also passed with `package.openssh-clients`.

### Workstation package batch 2: completion criteria

Scope: `package.openssh-clients` on Fedora 44 x86_64 Workstation only, with the
default `fedora-rpm` source and system scope. Legacy `InstallRequired` is
preserved by the separate package operations in
[provider foundation batch 01](migrations/provider-foundation-01.md); it is
not part of this OpenSSH outcome. Fedora's [OpenSSH client package](https://packages.fedoraproject.org/pkgs/openssh/openssh-clients/)
provides `ssh`, `scp`, `sftp`, and client configuration; the catalog records its
Fedora license expression and repository GPG verification. RIDE owns the
selection, DNF handler, and run journal, not existing SSH configuration.

The pinned Workstation base has `openssh-clients` installed. On an intact
overlay, require a read-only plan, unchanged apply and repeat, matching status,
unchanged client configuration bytes, `ssh -V`, RPM signature and file checks,
and continuing SSH server availability. DNF cannot remove this package while
GNOME depends on `ssh-add` and `ssh-agent`. To test installation, make it absent
only in a separate disposable overlay with `rpm -e --nodeps`; this deliberately
broken dependency state is a test fixture, never a default-profile action.
Require RIDE apply to repair it, `dnf check` to pass, repeat apply to be
unchanged, and the client and server checks to pass. Inject a later missing
package, require an accurate failed journal, and verify that restore and
explicit remove refuse unsupported reversal without changing the guest.
Recovery of the artificial state is by discarding the overlay. This
security-related batch gets its own failure/recovery run. The operation must
declare installed-only state and `recovery: none`; no exact restoration of
pre-existing SSH configuration is promised. No desktop manual session is
needed.

Status: the [first VM run and focused rerun](acceptance/openssh-clients-workstation-pilot.md)
retain the investigated preparation failure and show three applicable VM
scenarios passing under the installed-only contract. Mocked recovery and
catalog validation also pass. The Server variant was added after its separate
[pilot](acceptance/server-base-package-pilot.md). Technical review and the
owner's no-run confirmation now support the accepted target rows.

Before accepting the Workstation `default` profile as a whole, run one
combined smoke check on the pinned image. Require a read-only plan of exactly
its three installed operations, an unchanged apply journal in profile order,
matching individual status, identical package inventory and SSH client
configuration, and an active SSH server. Reuse the package-specific install,
failure, and recovery results above; this combined check tests profile
selection and interaction, not another full lifecycle.

Status: the [combined profile pilot](acceptance/workstation-default-profile-pilot.md)
passed on 2026-10-30. Its three operations are accepted on the pinned
Workstation target.

### Server base package batch: completion criteria

Scope: `server-base` with `package.less` and `package.openssh-clients` on a
separately installed Fedora 44 x86_64 Server guest. The Fedora repository and
RIDE catalog/provider ownership match the Workstation batches; no
`network-devices` server function or host-specific value is transferred. The
Server image must be built from the verified 44-1.7 Everything netinstaller
with the Server environment selected, pinned by recipe and qcow2 digests, and
identified by the harness as `VARIANT_ID=server`. Define a Server target row
only after the image is verified. The [Windows OpenSSH preflight](windows-alignment.md#fedora-workstation-openssh-client-batch-preflight-2026-10-30)
and first package batch review apply to the unchanged package and journal
fields; recheck the exact Server target declarations before promotion.

Pass only if read-only plan, apply, repeat apply, and status match RPM state on
this edition. Exercise a new `less` install and its declared remove/restore
in a disposable overlay with package inventory recovery. For OpenSSH, retain
the installed-only `recovery: none` contract; check client version, signed
RPM/files, unchanged configuration, active SSH server, and refusal of remove
or restore. Use a separate disposable overlay for an artificially absent
client and injected later failure if needed to establish Server-specific
installation and journal behavior; never remove the client on a persistent
host. Reuse Workstation/Cloud DNF handler failure evidence only where the
handler and source are unchanged. Run one combined `server-base` profile smoke
check, then create per-operation acceptance records before any Server target
is promoted. These command-line checks need no manual desktop session.

Status: the Server image and target matrix are pinned. The
[focused pilot](acceptance/server-base-package-pilot.md) passed for both
operations and the combined profile on 2026-10-30. Their per-operation records
and the owner's no-run confirmation support the accepted Server target rows.

Candidate milestone `17849c4` records the implementation, target-specific VM
pilots, and per-operation acceptance drafts. The repository validation gates
passed: shell syntax and ShellCheck, generated documentation and schema,
burndown, executable modes, 49 unit tests, and acceptance collection. A
post-commit byte comparison found all 11 runtime source files in representative
Server VM archives identical to the committed candidate. At that milestone,
the only remaining working-tree change was an unrelated user deletion of
`docs/v3-migration.md`.
Local `/var/lib/ride-fedora/runs` was absent. The owner confirmed on
2026-10-30 that no non-disposable machine has v3 runs. This resolves the
original-catalog recovery gate for this promotion. The VM pilots need not be
repeated for unchanged runtime files.

On each non-disposable machine where v3 may have run, start in this repository
root as a regular user and run the following read-only inventory. Use `sudo`
only if the private run directory denies read access. It prints run IDs,
status, and changed operation IDs, but not saved state values; it writes
nothing and needs no recovery. A `review` row needs an original-catalog
recovery decision before using a newer catalog. An `invalid` row makes the
command exit 2 and also needs inspection. A zero-journal result confirms only
that machine, so record the machine list separately.

```bash
python3 tools/audit_v3_runs.py
```

The 2026-10-30 local result was `journals=0 review=0`; six focused audit
unit tests passed, including failed, orphaned, and symlinked journal handling. Other
machines can use the command if future catalog target changes need an
inventory; no non-disposable v3 runs existed before this promotion.

The per-operation acceptance records include a 2026-10-30 technical review
of the Fedora package records, archived JUnit results, and source equivalence.
Across the Cloud Base, Workstation, and Server pilots, the archived Fedora
package handler and journal module are byte identical to candidate commit
`81f604f`. The older Workstation operation rows differ from the current
catalog only in their edition target declarations; the edition gate and
current Server pilots cover those additions. The owner confirmed there are no
non-disposable v3 runs; the declared targets are accepted after this review.

### Generic Server Required batch: completion status

Scope: the eleven RPMs in the pinned generic Server v2 `InstallRequired`
function. v3 maps them to ten one-way package operations in the opt-in
`server-required-tools` profile and isolates `firewalld` in
`server-firewall-package`. Neither profile changes `server-base`.

Status: **PASS as operable opt-in candidates** on Fedora 44 Server x86_64. The
disposable VM run passed candidate gating, apply, repeat, status, package
signature and file verification, command probes, and profile removal while
preserving all installed packages and the complete post-apply RPM inventory.
The pinned image digest is
`efb75956d6dbde0801059fdac4a8a1451f06ecc843344ecdb71bb3e8d247af90`; the
[acceptance record](acceptance/generic-server-required.md) contains the
transcript path, checksum, and run IDs.

DNF added 82 RPM identities and upgraded six existing identities without
losing any starting package identity. Installing `open-vm-tools` enabled its
two units but left them inactive under KVM. Firewalld was already installed,
active, and enabled; its operation completed unchanged and its configuration
hash did not change. H035 tracks the observed DNF transaction effects. H036
retains a deeper absent-package firewalld install check because that transition
was not exercised on the pinned image.

### Supported-state promotion check

The owner confirmed on 2026-10-30 that no non-disposable machine has run v3.
Promote only the three base package operations with acceptance records for
every declared edition. Before accepting the promoted revision, require
catalog/schema and generated-doc checks, mocked CLI and recovery tests, and
one focused disposable VM check of the supported execution path on each
declared profile target: Workstation `default` and Server `server-base` must
plan and apply without `--allow-candidate`, report supported status and an
unchanged journal, and preserve inventory, SSH configuration, and server
availability. Cloud Base `package.exfatprogs` must install without the
override, repeat unchanged, verify signed RPM/files and status, then restore
the new install and recover package inventory. Reuse the earlier target gates,
failure injection, and inverse checks because their handler, targets, and
recovery logic did not change. The status and acceptance path do not enter the
run source signature. No manual session is needed for these command-line
operations. Record the final VM outcome and remote CI before closing this
batch.

The [supported-state promotion check](acceptance/fedora-44-supported-promotion.md)
passed on 2026-10-30: Cloud Base exfatprogs installed and restored without
the candidate override, while Workstation `default` and Server `server-base`
planned and applied with supported status and unchanged journals. All three
JUnit runs passed. Local shell, catalog, generated-doc, burndown, mocked,
Firefox, Python compilation, and acceptance collection gates passed. The
only unrelated working-tree change remains the user's deletion of
`docs/v3-migration.md`, which is excluded from the promotion commit.

Promotion commit `cc96362` passed the remote
[v3 validation workflow](https://github.com/tjuuljensen/ride-fedora/actions/runs/41031081441)
and [shell executable-mode workflow](https://github.com/tjuuljensen/ride-fedora/actions/runs/41031081445).
The v3 job passed shell syntax and ShellCheck, catalog and generated docs,
55 mocked and Firefox tests, and acceptance collection. The required v3
package envelope is accepted on its declared Fedora targets; optional and
unsupported outcomes remain scoped separately above. A v3 release tag has
not been published and `master` remains the v2 release line.

## Former CERT forensic repository burndown

`default.preset` labels these entries “CERT Forensic Repo — THESE ARE EMPTY”. The
corresponding functions in `lib-fedora.sh` only print a URL or nothing; none is
an installation or removal path. Keep each item visible until a maintained
source, verified acquisition method, detection, removal, and disposable-VM
result are recorded. No entry below is part of the v3 default profile.

| Preset install/remove pair | Preset state | v3 burndown item |
| --- | --- | --- |
| `InstallGalleta` / `RemoveGalleta` | commented out | Candidate [`package.galleta`](acceptance/package.galleta.md) pins Debian 1.0+20040505-12, installs the x86_64 CLI user-locally, and removes only unchanged owned files; H099 covers representative parser fixtures. |
| `InstallPlaso` / `RemovePlaso` | commented out | Operable opt-in candidate [`package.plaso`](acceptance/package.plaso.md) uses the owned GIFT stable COPR/RPM path; Fedora 44 Workstation package lifecycle and case-output preservation passed. |
| `InstallAutopsy` / `RemoveAutopsy` | commented out | High-risk opt-in [`package.autopsy`](acceptance/package.autopsy.md) uses the Sleuth Kit Labs Snap Store stable channel. Fedora 44 acceptance verified candidate gating, actual block-device/dm-crypt/FUSE connections, automatic snapshot restore, and unchanged synthetic Autopsy case data across removal. The Store's 4.22.1 lags signed upstream 4.23.1; keep the version caveat visible and track GUI/analysis review in H087. |
| `InstallXplico` / `RemoveXplico` | commented out | v3.0 opt-in replacement is Fedora `zeek-core` for offline PCAP analysis and file extraction; Xplico-specific protocol parity remains in H098. |
| `InstallVolatility` / `RemoveVolatility` | commented out | Kept v3.0 migration gap, distinct from Volatility 3; assess an isolated legacy Python 2.7 runtime and plugin compatibility. |
| `InstallVolatility3` / `RemoveVolatility3` | commented out | Isolated `package.volatility3` passed a [non-root VM happy path](acceptance/package.volatility3.md) as an opt-in core candidate; plugin and broader recovery work is queued for v3.1. |
| `InstallVMFStools` / `RemoveVMFStools` | both commented out in this block; install also active later in the preset | The v2 no-op is retired; [an opt-in VMFS6 reader install candidate](acceptance/package.vmfs6-reader.md) is available for manual testing, while genuine VMFS6 access validation is deferred to v3.1. |
