# Workstation and server outcome burndown

This queue covers workstation and generic server migration candidates, including
functions absent from active presets. The owner-excluded Citrix and Opera functions and
host-specific server actions remain in the legacy source and server name inventory,
outside this queue.
Install/remove and analogous state pairs share an outcome row. A `deferred` row is
inventory, not an executable operation or acceptance claim.
Current progress and batch assignment come from `migration/outcomes.json`; the
older disposition text records the initial migration assessment.
Selector coverage records v2 preset references, not actual installations or
a priority rule. Active, commented, and library-only packages receive the same
source and product review; risk and dependencies determine batch order.

Workstation source: `lib-fedora.sh` at Fedora commit `43ba467`; 289 source functions,
285 queued functions,
164 grouped outcomes, 90 outcomes with no active default selector.
Function coverage: 74 active, 67 commented-only, 144 library-only.
Default preset: 76 active selectors and 71 commented selectors
that name a defined function or controller action. The [active migration ledger](MIGRATION-PLAN.md)
provides the decisions for all active selectors.

Server source: `operations/provisioning/ride/lib-fedora-server.sh` at `network-devices` commit
`fccc70f6825d13f899ac6fd4e72a1af6360be076`; 28 source functions,
21 queued functions, 21 outcomes,
5 outcomes absent from all active server presets. Its three preset inventories
are stored as names only in `migration/server-inventory.json`; no host values were copied.
Function coverage: 16 active in a server preset, 3 commented-only, 2 library-only.

## Workstation library

| Outcome key | Exact source functions | Selector coverage | Initial disposition / review rationale | Batch / current progress |
| --- | --- | --- | --- | --- |
| `action.SetupUserDefaultDirs` | `SetupUserDefaultDirs` | `SetupUserDefaultDirs`: active | opt-in candidate: `setting.user-default-directories` creates only absent `~/bin` and `~/git`, records RIDE-owned identities, and restores only unchanged empty directories; Fedora 44 Workstation VM evidence is in progress. | `desktop-user-01` / operable |
| `setting.Hostname` | `SetHostname` | `SetHostname`: active | supported: Private `--value` operation journals and restores the exact prior static hostname; Fedora 44 Workstation and Server VM acceptance passed. See the [system review](migrations/system-security-core.md). | `system-security-01` / supported |
| `setting.FastDNF` | `EnableFastDNF`, `DisableFastDNF` | `EnableFastDNF`: active, `DisableFastDNF`: library only | candidate: Migrated to an owned DNF5 drop-in with exact removal and effective-config verification; Fedora 44 Workstation acceptance is pending. See the [system review](migrations/system-security-core.md). | `system-security-01` / operable |
| `action.UpdateFedora` | `UpdateFedora` | `UpdateFedora`: active | opt-in candidate: `system.update-all-packages` passed full Fedora 44 Workstation and Server DNF5 transactions, report/journal checks, current status, reboot assessment, and non-restorable refusal. It remains explicitly invoked and outside profiles; H111 tracks broader failure/reboot hardening. See [acceptance](acceptance/system.update-all-packages.md). | `system-security-02` / operable |
| `package.Required` | `InstallRequired` | `InstallRequired`: active | operable opt-in candidate: Seven individual Fedora RPM operations passed Fedora 44 Workstation lifecycle checks in `required-tools`; all remain installed on profile removal. The separate generic Server bundle is operable in two opt-in profiles; its Server nano operation is installed-only and H035 tracks the observed DNF upgrades. See [Workstation provider foundation batch 01](migrations/provider-foundation-01.md), [Server migration](migrations/generic-server-required.md), and [Server VM acceptance](acceptance/generic-server-required.md). | `provider-foundation-01` / operable |
| `package.ShellTools` | `InstallShellTools`, `RemoveShellTools` | `InstallShellTools`: active, `RemoveShellTools`: library only | supported: Split into supported `package.pv` and `package.strace` in the opt-in `shell-tools` profile; see [VM acceptance](acceptance/provider-shell-tools.md). | `provider-foundation-01` / supported |
| `package.RPMfusionRepos` | `InstallRPMfusionRepos`, `RemoveRPMfusionRepos` | `InstallRPMfusionRepos`: active, `RemoveRPMfusionRepos`: library only | supported opt-in: Fedora 44 Workstation x86_64 lifecycle, exact inverse, and focused signature/digest/rollback failures pass. Upstream uses `gpgcheck=1` and `repo_gpgcheck=0`; see [provider batch 02](migrations/provider-foundation-02.md) and [acceptance](acceptance/setting.rpmfusion-repositories.md). | `provider-foundation-02` / supported |
| `package.KernelTools` | `InstallKernelTools`, `RemoveKernelTools` | `InstallKernelTools`: active, `RemoveKernelTools`: library only | supported: Split into signed Fedora `kernel-devel` and `kernel-headers` package installs; [VM evidence](acceptance/provider-kernel-tools.md) does not establish a matching module-build environment. | `provider-foundation-03` / supported |
| `package.DNFutils` | `InstallDNFutils`, `RemoveDNFutils` | `InstallDNFutils`: active, `RemoveDNFutils`: library only | replaced: Fedora 44 Workstation has DNF5 and plugins; current `config-manager` and `download` commands passed the disposable-VM check. See [provider foundation batch 03](migrations/provider-foundation-03.md). | `provider-foundation-03` / resolved |
| `package.Eza` | `InstallEza`, `RemoveEza` | `InstallEza`: library only, `RemoveEza`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `provider-foundation-08` / supported |
| `package.EzaGitHub` | `InstallEzaGitHub` | `InstallEzaGitHub`: active | operable opt-in candidate: `package.eza-portable` pins the upstream GNU x86_64 release and owns `~/.local/bin/eza`; it passed [VM acceptance](acceptance/package.eza-portable.md) beside the Fedora RPM. | `provider-foundation-08` / operable |
| `package.VersionLock` | `InstallVersionLock`, `RemoveVersionLock` | `InstallVersionLock`: commented, `RemoveVersionLock`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `provider-foundation-04` / resolved |
| `package.NautilusHash` | `InstallNautilusHash`, `RemoveNautilusHash` | `InstallNautilusHash`: commented, `RemoveNautilusHash`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-03` / resolved |
| `package.NautilusImageTools` | `InstallNautilusImageTools`, `RemoveNautilusImageTools` | `InstallNautilusImageTools`: commented, `RemoveNautilusImageTools`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-03` / resolved |
| `package.Flatpak` | `InstallFlatpak`, `RemoveFlatpak` | `InstallFlatpak`: commented, `RemoveFlatpak`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `provider-foundation-11` / supported |
| `package.Flathub` | `InstallFlathub`, `RemoveFlathub` | `InstallFlathub`: active, `RemoveFlathub`: library only | unsupported: [Flathub remote ownership](migrations/provider-foundation-09.md) needs a scoped handler, app preservation, and inverse evidence before it is runnable. | `provider-foundation-09` / operable |
| `package.AppImageLauncher` | `InstallAppImageLauncher`, `RemoveAppImageLauncher` | `InstallAppImageLauncher`: active, `RemoveAppImageLauncher`: library only | opt-in candidate in progress: Migrate the capability through Flathub Gear Lever after the operator removes the old `appimagelauncher` RPM; preserve `~/Applications`, AppImages, and launcher state. See [publisher batch 01](migrations/publisher-apps-01.md) and H070. | `publisher-apps-01` / operable |
| `package.Snap` | `InstallSnap`, `RemoveSnap` | `InstallSnap`: commented, `RemoveSnap`: library only | implemented candidate `package.snapd`; Fedora 44 Workstation socket and install lifecycle passed, while host confinement is partial | `provider-foundation-12` / operable |
| `package.Galleta` | `InstallGalleta`, `RemoveGalleta` | `InstallGalleta`: commented, `RemoveGalleta`: library only | deferred incomplete legacy stub; source and current package need review | `resolution-review-01` / operable |
| `package.Plaso` | `InstallPlaso`, `RemovePlaso` | `InstallPlaso`: commented, `RemovePlaso`: library only | deferred candidate; opt-in COPR and removal need VM evidence | `forensic-isolated-02` / operable |
| `package.Autopsy` | `InstallAutopsy`, `RemoveAutopsy` | `InstallAutopsy`: commented, `RemoveAutopsy`: library only | deferred candidate; upstream Linux setup and removal need VM evidence | `forensic-isolated-09` / operable |
| `package.Xplico` | `InstallXplico`, `RemoveXplico` | `InstallXplico`: commented, `RemoveXplico`: library only | deferred incomplete legacy stub; source and current package need review | `resolution-review-01` / supported |
| `package.VMFStools` | `InstallVMFStools`, `RemoveVMFStools` | `InstallVMFStools`: active, `RemoveVMFStools`: library only | kept gap: The active v2 function only prints URLs. An opt-in [VMFS6 reader install candidate](acceptance/package.vmfs6-reader.md) is available for manual testing; its genuine VMFS6 fixture and read-only access test remain deferred to v3.1. | `forensic-isolated-07` / implemented |
| `package.Volatility` | `InstallVolatility`, `RemoveVolatility` | `InstallVolatility`: commented, `RemoveVolatility`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `forensic-isolated-02` / operable |
| `package.Volatility3` | `InstallVolatility3`, `RemoveVolatility3` | `InstallVolatility3`: commented, `RemoveVolatility3`: library only | implemented candidate `package.volatility3`; isolated pinned core, VM acceptance pending | `forensic-isolated-02` / operable |
| `package.VeraCrypt` | `InstallVeraCrypt`, `UninstallVeraCrypt` | `InstallVeraCrypt`: active, `UninstallVeraCrypt`: library only | supported opt-in: The pinned Fedora 44 Workstation GUI RPM passed detached-signature refusal, failed-transaction cleanup, mounted-volume refusal, and encrypted test-volume preservation across removal and reinstall. See [batch 02](migrations/publisher-apps-02.md) and [acceptance](acceptance/package.veracrypt.md). | `publisher-apps-02` / supported |
| `package.BulkExtractor` | `InstallBulkExtractor`, `RemoveBulkExtractor` | `InstallBulkExtractor`: commented, `RemoveBulkExtractor`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `forensic-isolated-04` / operable |
| `package.EmailHeaderAnlzr` | `InstallEmailHeaderAnlzr`, `RemoveEmailHeaderAnlzr` | `InstallEmailHeaderAnlzr`: commented, `RemoveEmailHeaderAnlzr`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `forensic-isolated-06` / operable |
| `package.LibEWF` | `InstallLibEWF`, `RemoveLibEWF` | `InstallLibEWF`: active, `RemoveLibEWF`: library only | replaced: package.ewftools covers EWF utilities; verify library intent separately. | `native-rpm-02` / supported |
| `package.SecurityLab` | `InstallSecurityLab`, `RemoveSecurityLab` | `InstallSecurityLab`: commented, `RemoveSecurityLab`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `provider-foundation-06` / operable |
| `package.Dc3dd` | `InstallDc3dd`, `RemoveDc3dd` | `InstallDc3dd`: commented, `RemoveDc3dd`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-04` / supported |
| `package.Exif` | `InstallExif`, `RemoveExif` | `InstallExif`: active, `RemoveExif`: library only | deferred: Review product identity and official package. | `native-rpm-02` / supported |
| `package.Binwalk` | `InstallBinwalk`, `RemoveBinwalk` | `InstallBinwalk`: commented, `RemoveBinwalk`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `forensic-isolated-03` / supported |
| `package.Md5deep` | `InstallMd5deep`, `RemoveMd5deep` | `InstallMd5deep`: active, `RemoveMd5deep`: library only | deferred: Review current package and forensic use case. | `native-rpm-02` / supported |
| `package.Libpst` | `InstallLibpst`, `RemoveLibpst` | `InstallLibpst`: library only, `RemoveLibpst`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-05` / supported |
| `package.Macvendor` | `InstallMacvendor`, `RemoveMacvendor` | `InstallMacvendor`: library only, `RemoveMacvendor`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `forensic-isolated-03` / resolved |
| `package.ExifTool` | `InstallExifTool`, `RemoveExifTool` | `InstallExifTool`: active, `RemoveExifTool`: library only | supported: Fedora `perl-Image-ExifTool` passed [VM lifecycle acceptance](acceptance/package.exiftool.md); the v2 GitHub/CPAN build path is not adopted. | `forensic-isolated-01` / supported |
| `package.ASN` | `InstallASN`, `RemoveASN` | `InstallASN`: active, `RemoveASN`: library only | unsupported: [Forensic batch 01](migrations/forensic-isolated-01.md) requires a pinned owned script and shared-dependency-safe inverse. | `forensic-isolated-01` / operable |
| `package.UnfURL` | `InstallUnfURL`, `RemoveUnfURL` | `InstallUnfURL`: active, `RemoveUnfURL`: library only | unsupported: [Forensic batch 01](migrations/forensic-isolated-01.md) requires a pinned isolated Python environment. | `forensic-isolated-01` / operable |
| `package.CyberChef` | `InstallCyberChef`, `RemoveCyberChef` | `InstallCyberChef`: active, `RemoveCyberChef`: library only | unsupported: [Forensic batch 01](migrations/forensic-isolated-01.md) requires a pinned offline artifact and owned desktop destination. | `forensic-isolated-01` / operable |
| `package.Chepy` | `InstallChepy`, `RemoveChepy` | `InstallChepy`: active, `RemoveChepy`: library only | unsupported: [Forensic batch 01](migrations/forensic-isolated-01.md) requires a pinned isolated build and owned inverse. | `forensic-isolated-01` / operable |
| `package.Dumpzilla` | `InstallDumpzilla`, `RemoveDumpzilla` | `InstallDumpzilla`: commented, `RemoveDumpzilla`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `forensic-isolated-08` / operable |
| `package.NetworkMiner` | `InstallNetworkMiner`, `RemoveNetworkMiner` | `InstallNetworkMiner`: active, `RemoveNetworkMiner`: library only | operable opt-in candidate (`RemoveNetworkMiner` shares the outcome): Fedora 44 Workstation lifecycle and Xvfb startup passed; restore/removal preserved seeded output. Mono/GTK remain a separate opt-in runtime profile. H110 gates any evidence processing or live capture. See [batch 05](migrations/forensic-isolated-05-networkminer.md) and [acceptance](acceptance/package.networkminer.md). | `forensic-isolated-05` / operable |
| `package.Pwgen` | `InstallPwgen`, `RemovePwgen` | `InstallPwgen`: active, `RemovePwgen`: library only | deferred: Candidate native repository package. | `native-rpm-01` / supported |
| `package.Htop` | `InstallHtop`, `RemoveHtop` | `InstallHtop`: active, `RemoveHtop`: library only | deferred: Candidate native repository package. | `native-rpm-01` / supported |
| `package.Bat` | `InstallBat`, `RemoveBat` | `InstallBat`: active, `RemoveBat`: library only | deferred: Candidate native repository package. | `native-rpm-01` / supported |
| `package.Ncdu` | `InstallNcdu`, `RemoveNcdu` | `InstallNcdu`: active, `RemoveNcdu`: library only | deferred: Candidate native repository package. | `native-rpm-01` / supported |
| `package.Ripgrep` | `InstallRipgrep`, `RemoveRipgrep` | `InstallRipgrep`: active, `RemoveRipgrep`: library only | deferred: Candidate native repository package. | `native-rpm-01` / supported |
| `package.Fd` | `InstallFd`, `RemoveFd` | `InstallFd`: active, `RemoveFd`: library only | deferred: Candidate native repository package. | `native-rpm-01` / supported |
| `package.Docker` | `InstallDocker`, `RemoveDocker` | `InstallDocker`: active, `RemoveDocker`: library only | deferred: Generic server role only after provider and repository review. | `system-security-03` / supported |
| `package.PythonPip` | `InstallPythonPip`, `RemovePythonPip` | `InstallPythonPip`: active, `RemovePythonPip`: library only | supported: Fedora `python3-pip` passed [VM lifecycle acceptance](acceptance/package.python3-pip.md); omit the v2 global pip self-upgrade. | `provider-foundation-03` / supported |
| `package.PackagingTools` | `InstallPackagingTools`, `RemovePackagingTools` | `InstallPackagingTools`: active, `RemovePackagingTools`: library only | replaced: Fedora `7zip` and `unar` passed [VM package acceptance](acceptance/provider-archive-tools.md); `unar` is a different CLI from `unrar`. | `provider-foundation-03` / supported |
| `package.BasicEditors` | `InstallBasicEditors`, `RemoveBasicEditors` | `InstallBasicEditors`: active, `RemoveBasicEditors`: library only | supported: Split into Fedora `nano` and `vim-enhanced` package installs with [VM evidence](acceptance/provider-basic-editors.md). | `provider-foundation-04` / supported |
| `package.CommanderFileMgrs` | `InstallCommanderFileMgrs`, `RemoveCommanderFileMgrs` | `InstallCommanderFileMgrs`: commented, `RemoveCommanderFileMgrs`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-09` / operable |
| `package.Terminator` | `InstallTerminator`, `RemoveTerminator` | `InstallTerminator`: active, `RemoveTerminator`: library only | opt-in candidate: Fedora [`package.terminator`](acceptance/package.terminator.md) and the separate [iBus hotkey setting](acceptance/setting.ibus-emoji-hotkey.md) passed Workstation VM lifecycles; use the root package command and per-user hotkey profile with `--allow-candidate`. See [batch 10](migrations/desktop-user-10-terminator.md). | `desktop-user-10` / operable |
| `package.Alien` | `InstallAlien`, `RemoveAlien` | `InstallAlien`: active, `RemoveAlien`: library only | deferred: Review relevance and support. | `native-rpm-02` / supported |
| `package.SmartMonTools` | `InstallSmartMonTools`, `RemoveSmartMonTools` | `InstallSmartMonTools`: active, `RemoveSmartMonTools`: library only | deferred: Optional system tools profile. | `system-security-26` / operable |
| `package.Qbittorrent` | `InstallQbittorrent`, `RemoveQbittorrent` | `InstallQbittorrent`: commented, `RemoveQbittorrent`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-04` / operable |
| `package.PowerShell` | `InstallPowerShell`, `RemovePowerShell` | `InstallPowerShell`: commented, `RemovePowerShell`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-09` / operable |
| `package.MicrosoftTeams` | `InstallMicrosoftTeams`, `RemoveMicrosoftTeams` | `InstallMicrosoftTeams`: commented, `RemoveMicrosoftTeams`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-09` / resolved |
| `package.WoeUSB` | `InstallWoeUSB`, `RemoveWoeUSB` | `InstallWoeUSB`: commented, `RemoveWoeUSB`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-09` / operable |
| `package.BalenaEtcher` | `InstallBalenaEtcher`, `RemoveBalenaEtcher` | `InstallBalenaEtcher`: commented, `RemoveBalenaEtcher`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-09` / operable |
| `package.VisualStudioCode` | `InstallVisualStudioCode`, `RemoveVisualStudioCode` | `InstallVisualStudioCode`: active, `RemoveVisualStudioCode`: library only | deferred: Align product facts with Windows; Fedora source stays local. | `publisher-apps-03` / operable |
| `package.ArduinoIDE` | `InstallArduinoIDE`, `RemoveArduinoIDE` | `InstallArduinoIDE`: commented, `RemoveArduinoIDE`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-10` / operable |
| `package.AtomEditor` | `InstallAtomEditor`, `RemoveAtomEditor` | `InstallAtomEditor`: commented, `RemoveAtomEditor`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-10` / resolved |
| `setting.AtomTelemetry` | `DisableAtomTelemetry`, `EnableAtomTelemetry` | `DisableAtomTelemetry`: commented, `EnableAtomTelemetry`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `resolution-review-01` / resolved |
| `package.AtomPlugins` | `InstallAtomPlugins`, `RemoveAtomPlugins` | `InstallAtomPlugins`: commented, `RemoveAtomPlugins`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-10` / resolved |
| `package.PyhtonAutopep8` | `InstallPyhtonAutopep8`, `RemovePyhtonAutopep8` | `InstallPyhtonAutopep8`: commented, `RemovePyhtonAutopep8`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `forensic-isolated-03` / supported |
| `package.Hexchat` | `InstallHexchat`, `RemoveHexchat` | `InstallHexchat`: active, `RemoveHexchat`: library only | deferred: Review upstream maintenance before reintroduction. | `native-rpm-03` / operable |
| `package.Discord` | `InstallDiscord`, `RemoveDiscord` | `InstallDiscord`: commented, `RemoveDiscord`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-10` / operable |
| `package.Pidgin` | `InstallPidgin`, `RemovePidgin` | `InstallPidgin`: commented, `RemovePidgin`: library only | owner retired Pidgin and OTR from v3 on 2026-11-02; reopen only on explicit owner request | `system-security-27` / resolved |
| `package.Thunderbird` | `InstallThunderbird`, `RemoveThunderbird` | `InstallThunderbird`: commented, `RemoveThunderbird`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-04` / operable |
| `setting.MulticastDNS` | `DisableMulticastDNS`, `EnableMulticastDNS` | `DisableMulticastDNS`: commented, `EnableMulticastDNS`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `system-security-06` / operable |
| `package.NetworkTools` | `InstallNetworkTools`, `RemoveNetworkTools` | `InstallNetworkTools`: active, `RemoveNetworkTools`: library only | deferred: Split broad network bundle into focused packages. | `system-security-04` / operable |
| `package.NetCommsTools` | `InstallNetCommsTools`, `RemoveNetCommsTools` | `InstallNetCommsTools`: active, `RemoveNetCommsTools`: library only | deferred: Split broad communications bundle. | `system-security-04` / operable |
| `package.NetMgrL2TP` | `InstallNetMgrL2TP`, `RemoveNetMgrL2TP` | `InstallNetMgrL2TP`: commented, `RemoveNetMgrL2TP`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-07` / supported |
| `package.NetMgrLibreswan` | `InstallNetMgrLibreswan`, `RemoveNetMgrLibreswan` | `InstallNetMgrLibreswan`: active, `RemoveNetMgrLibreswan`: library only | deferred: Optional VPN role. | `system-security-05` / supported |
| `package.Wireguard` | `InstallWireguard`, `RemoveWireguard` | `InstallWireguard`: library only, `RemoveWireguard`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-19` / supported |
| `package.OpenconnectVPN` | `InstallOpenconnectVPN` | `InstallOpenconnectVPN`: commented | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-08` / supported |
| `package.SpeedtestCLI` | `InstallSpeedtestCLI`, `RemoveSpeedtestCLI` | `InstallSpeedtestCLI`: active, `RemoveSpeedtestCLI`: library only | supported, with opt-in alternative: Keep Fedora `speedtest-cli` RPM and offer digest-pinned LibreSpeed CLI as an operable opt-in candidate; see [native RPM batch 03](migrations/native-rpm-03.md). | `native-rpm-03` / supported |
| `package.Flameshot` | `InstallFlameshot`, `RemoveFlameshot` | `InstallFlameshot`: commented, `RemoveFlameshot`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-04` / operable |
| `package.Dia` | `InstallDia`, `RemoveDia` | `InstallDia`: commented, `RemoveDia`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-05` / operable |
| `package.Wine` | `InstallWine`, `RemoveWine` | `InstallWine`: commented, `RemoveWine`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-05` / operable |
| `package.Joplin` | `InstallJoplin`, `RemoveJoplin` | `InstallJoplin`: commented, `RemoveJoplin`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-10` / operable |
| `package.TecmintMonitorSh` | `InstallTecmintMonitorSh`, `RemoveTecmintMonitorSh` | `InstallTecmintMonitorSh`: active, `RemoveTecmintMonitorSh`: library only | retired: Default profile must not fetch and execute remote scripts. | `resolution-review-01` / supported |
| `package.GnomeExtInstaller` | `InstallGnomeExtInstaller`, `RemoveGnomeExtInstaller` | `InstallGnomeExtInstaller`: active, `RemoveGnomeExtInstaller`: library only | operable opt-in candidate: Fedora's signed browser connector RPM passed the Workstation lifecycle and preserves user extension state; browser add-on installation remains user controlled. See [provider foundation batch 10](migrations/provider-foundation-10.md) and [acceptance](acceptance/package.gnome-browser-connector.md). | `provider-foundation-10` / operable |
| `package.Brave` | `InstallBrave`, `RemoveBrave` | `InstallBrave`: active, `RemoveBrave`: library only | deferred: Third-party repository and license review. | `publisher-apps-03` / operable |
| `package.Vivaldi` | `InstallVivaldi`, `RemoveVivaldi` | `InstallVivaldi`: commented, `RemoveVivaldi`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-10` / operable |
| `package.Chromium` | `InstallChromium`, `RemoveChromium` | `InstallChromium`: active, `RemoveChromium`: library only | deferred: Candidate distro repository package. | `native-rpm-03` / operable |
| `package.Chrome` | `InstallChrome`, `RemoveChrome` | `InstallChrome`: commented, `RemoveChrome`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-11` / operable |
| `setting.ChromePreferences` | `SetChromePreferences`, `UnsetChromePreferences` | `SetChromePreferences`: commented, `UnsetChromePreferences`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-05` / operable |
| `setting.FirefoxPreferences` | `SetFirefoxPreferences`, `UnsetFirefoxPreferences` | `SetFirefoxPreferences`: active, `UnsetFirefoxPreferences`: library only | operable opt-in candidate: `setting.firefox-preferences` keeps the v2 values in an opt-in Mozilla AutoConfig profile, owns three files with guarded recovery, and passed Fedora 44 Workstation startup acceptance. H083 tracks value freshness and a brief visible review before promotion or value changes. | `desktop-user-01` / operable |
| `action.CheckFirefoxAddons` | `CheckFirefoxAddons` | `CheckFirefoxAddons`: library only | deferred v3 integration; existing policy helper remains tested separately | `desktop-user-05` / resolved |
| `package.FirefoxAddons` | `InstallFirefoxAddons`, `RemoveFirefoxAddons` | `InstallFirefoxAddons`: active, `RemoveFirefoxAddons`: library only | blocked implementation: The owner kept v3-managed add-on policy. The v3 envelope models configured, removal-pending, and absent states, but remains non-runnable until focused Fedora 44 Workstation restart, profile cleanup, and restoration evidence passes; see [publisher batch 04](migrations/publisher-apps-04.md). | `publisher-apps-04` / operable |
| `action.FinalizeFirefoxAddonRemoval` | `FinalizeFirefoxAddonRemoval` | `FinalizeFirefoxAddonRemoval`: library only | deferred v3 integration; restart-dependent policy lifecycle needs journal ownership | `desktop-user-06` / resolved |
| `package.Edge` | `InstallEdge`, `RemoveEdge` | `InstallEdge`: commented, `RemoveEdge`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-11` / operable |
| `package.Codecs` | `InstallCodecs`, `RemoveCodecs` | `InstallCodecs`: commented, `RemoveCodecs`: library only | operable opt-in v3.0 outcome: fixed Fedora codec package set, RPM Fusion alternative candidate and bounded Multimedia update; see provider-foundation-05 and hardening item H037 | `provider-foundation-05` / operable |
| `package.SpotifyClient` | `InstallSpotifyClient`, `RemoveSpotifyClient` | `InstallSpotifyClient`: commented, `RemoveSpotifyClient`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-11` / operable |
| `package.VLCPlayer` | `InstallVLCPlayer`, `RemoveVLCPlayer` | `InstallVLCPlayer`: commented, `RemoveVLCPlayer`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-05` / operable |
| `package.ClementinePlayer` | `InstallClementinePlayer`, `RemoveClementinePlayer` | `InstallClementinePlayer`: commented, `RemoveClementinePlayer`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-11` / operable |
| `package.PulseAudioEq` | `InstallPulseAudioEq`, `RemovePulseAudioEq` | `InstallPulseAudioEq`: commented, `RemovePulseAudioEq`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-11` / operable |
| `package.YouTubeDownloader` | `InstallYouTubeDownloader`, `RemoveYouTubeDownloader` | `InstallYouTubeDownloader`: active, `RemoveYouTubeDownloader`: library only | replaced: Review maintained yt-dlp packaging instead of legacy youtube-dl. | `publisher-apps-05` / supported |
| `package.GIMP` | `InstallGIMP`, `RemoveGIMP` | `InstallGIMP`: commented, `RemoveGIMP`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-04` / operable |
| `package.HandBrake` | `InstallHandBrake`, `RemoveHandBrake` | `InstallHandBrake`: commented, `RemoveHandBrake`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `provider-foundation-07` / operable |
| `package.GnomeTools` | `InstallGnomeTools`, `RemoveGnomeTools` | `InstallGnomeTools`: active, `RemoveGnomeTools`: library only | opt-in candidate: Fedora printer UI and GNOME Tweaks passed [package VM acceptance](acceptance/provider-gnome-tools.md); visual checks remain v3.1, and v2's unowned `gparted` removal is excluded. | `provider-foundation-04` / operable |
| `package.SystemMonitor` | `InstallSystemMonitor`, `RemoveSystemMonitor` | `InstallSystemMonitor`: active, `RemoveSystemMonitor`: library only | deferred: Review current GNOME extension support. | `publisher-apps-05` / operable |
| `package.GnomeExtensions` | `InstallGnomeExtensions`, `RemoveGnomeExtensions` | `InstallGnomeExtensions`: active, `RemoveGnomeExtensions`: library only | deferred: Review current GNOME extension IDs and API. | `publisher-apps-17` / resolved |
| `setting.ScreenSaver` | `EnableScreenSaver` | `EnableScreenSaver`: active | supported opt-in state: Fedora 44 Workstation acceptance verified the explicit `screensaver-enabled` value, unchanged `lock-delay`, and exact recovery; no base profile selects it. | `resolution-review-01` / supported |
| `setting.Screensaver` | `DisableScreensaver` | `DisableScreensaver`: active | supported opt-in state: Fedora 44 Workstation acceptance verified the explicit `screensaver-disabled` value, unchanged `lock-delay`, and exact recovery; no base profile selects it. | `resolution-review-01` / supported |
| `setting.DateInTaskbar` | `ShowDateInTaskbar`, `HideDateInTaskbar` | `ShowDateInTaskbar`: active, `HideDateInTaskbar`: library only | deferred: Setting handler needs baseline and restore. | `desktop-user-02` / operable |
| `setting.WeekNumbersInTaskbar` | `ShowWeekNumbersInTaskbar`, `HideWeekNumbersInTaskbar` | `ShowWeekNumbersInTaskbar`: active, `HideWeekNumbersInTaskbar`: library only | deferred: Setting handler needs baseline and restore. | `desktop-user-02` / operable |
| `setting.WindowCtlMinMaxClose` | `SetWindowCtlMinMaxClose` | `SetWindowCtlMinMaxClose`: active | opt-in candidate: One [GNOME string-setting operation](migrations/desktop-user-string-01.md) selects this or either alternative layout and restores the exact prior user override; [Workstation VM evidence](acceptance/setting.gnome-string-values.md). | `desktop-user-02` / operable |
| `setting.WindowCtlAppmenuClose` | `SetWindowCtlAppmenuClose` | `SetWindowCtlAppmenuClose`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-07` / operable |
| `setting.WindowCtlLeftClsMinMax` | `SetWindowCtlLeftClsMinMax` | `SetWindowCtlLeftClsMinMax`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-07` / operable |
| `setting.MiddleButtonPaste` | `EnableMiddleButtonPaste`, `DisableMiddleButtonPaste` | `EnableMiddleButtonPaste`: library only, `DisableMiddleButtonPaste`: active | deferred: Setting handler needs baseline and restore. | `desktop-user-02` / operable |
| `setting.GnomeRegionDaDK` | `SetGnomeRegionDaDK` | `SetGnomeRegionDaDK`: active | opt-in candidate: The [region operation](migrations/desktop-user-string-01.md) takes an explicit validated locale value; the Danish profile passed [Workstation VM acceptance](acceptance/setting.gnome-string-values.md). | `desktop-user-02` / operable |
| `package.GnomeRegion` | `RemoveGnomeRegion` | `RemoveGnomeRegion`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `desktop-user-02` / operable |
| `setting.ScreensaverSlp10Lgn5` | `SetScreensaverSlp10Lgn5` | `SetScreensaverSlp10Lgn5`: active | supported on Fedora 44 Workstation: `setting.gnome-lock-timing` carries both retained 10/5 and 15/5 variants through exact four-key recovery; the Workstation VM verified both profiles, status, repeat, and restore. H092 tracks brief visible idle/lock behavior review. | `desktop-user-11` / supported |
| `setting.ScreensaverSlp15Lgn5` | `SetScreensaverSlp15Lgn5` | `SetScreensaverSlp15Lgn5`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-11` / supported |
| `setting.CustomKeyboardShortcut` | `SetCustomKeyboardShortcut` | `SetCustomKeyboardShortcut`: active | opt-in candidate: `setting.gnome-custom-shortcuts` merges owned GNOME entries and restores only RIDE-owned shortcut state; Fedora 44 Workstation lifecycle and preservation checks passed. H089 tracks visible dispatch and conflict review. | `desktop-user-03` / operable |
| `setting.VMKeyboardShortcut` | `SetVMKeyboardShortcut` | `SetVMKeyboardShortcut`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-08` / operable |
| `package.CustomKbrdShortcut` | `RemoveCustomKbrdShortcut` | `RemoveCustomKbrdShortcut`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `desktop-user-03` / operable |
| `setting.GnomeCustomFavorites` | `SetGnomeCustomFavorites` | `SetGnomeCustomFavorites`: active | opt-in candidate: `setting.gnome-favorite-apps` accepts a configurable desktop-ID list and restores the exact prior dconf value; Fedora 44 Workstation plan/apply/repeat/conflict/restore acceptance passed. H085 tracks visual app-ID review. | `desktop-user-03` / operable |
| `setting.GnomeDefaultFavorites` | `SetGnomeDefaultFavorites` | `SetGnomeDefaultFavorites`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-08` / operable |
| `setting.GnomeMinimalFavorites` | `SetGnomeMinimalFavorites` | `SetGnomeMinimalFavorites`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-08` / operable |
| `setting.GnmLocationServiceOff` | `SetGnmLocationServiceOff` | `SetGnmLocationServiceOff`: active | deferred: Review current GNOME setting and scope. | `desktop-user-04` / operable |
| `setting.GnmLocationServiceOn` | `SetGnmLocationServiceOn` | `SetGnmLocationServiceOn`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-09` / operable |
| `setting.GnmAutoProblemRptOff` | `SetGnmAutoProblemRptOff` | `SetGnmAutoProblemRptOff`: active | deferred: Review current GNOME setting and scope. | `desktop-user-04` / operable |
| `setting.GnmAutoProblemRptOn` | `SetGnmAutoProblemRptOn` | `SetGnmAutoProblemRptOn`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-09` / operable |
| `setting.PowerPercentageLow15` | `SetPowerPercentageLow15` | `SetPowerPercentageLow15`: active | opt-in candidate: The [shared UPower threshold operation](migrations/desktop-user-upower-01.md) selects 15 or 20 through an owned drop-in and exact restore; [Workstation VM evidence](acceptance/setting.upower-percentage-low.md). | `desktop-user-04` / operable |
| `setting.PowerPercentageLow20` | `SetPowerPercentageLow20` | `SetPowerPercentageLow20`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-09` / operable |
| `setting.BashAliases` | `EnableBashAliases`, `DisableBashAliases` | `EnableBashAliases`: active, `DisableBashAliases`: library only | opt-in candidate: `setting.bash-aliases` manages exact marked loader and alias blocks; Fedora 44 Workstation interactive use and preservation passed. See [alias batch](migrations/desktop-user-aliases-01.md) and [VM acceptance](acceptance/setting.bash-aliases.md). | `desktop-user-05` / operable |
| `setting.AliasLsEza` | `SetAliasLsEza`, `UnsetAliasLsEza` | `SetAliasLsEza`: active, `UnsetAliasLsEza`: library only | opt-in candidate: The owned alias operation invokes Eza only after checking the executable; its Workstation lifecycle passed. H090 tracks public-service review for the alias family. | `desktop-user-05` / operable |
| `setting.AliasWanIP` | `SetAliasWanIP`, `UnsetAliasWanIP` | `SetAliasWanIP`: active, `UnsetAliasWanIP`: library only | opt-in candidate: Fixed `wanip`, `wanip4`, and `wanip6` aliases use ipify HTTPS endpoints only when invoked; the VM verified their definitions without making network requests. | `desktop-user-05` / operable |
| `setting.AliasRideLog` | `SetAliasRideLog`, `UnsetAliasRideLog` | `SetAliasRideLog`: commented, `UnsetAliasRideLog`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-05` / resolved |
| `package.Lynis` | `InstallLynis`, `RemoveLynis` | `InstallLynis`: commented, `RemoveLynis`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-05` / supported |
| `package.ClamAV` | `InstallClamAV`, `RemoveClamAV` | `InstallClamAV`: commented, `RemoveClamAV`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-28` / operable |
| `package.KeepassXC` | `InstallKeepassXC`, `RemoveKeepassXC` | `InstallKeepassXC`: commented, `RemoveKeepassXC`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-29` / supported |
| `package.Bitwarden` | `InstallBitwarden`, `RemoveBitwarden` | `InstallBitwarden`: commented, `RemoveBitwarden`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-12` / supported |
| `package.BitwardenAppImage` | `InstallBitwardenAppImage`, `RemoveBitwardenAppImage` | `InstallBitwardenAppImage`: active, `RemoveBitwardenAppImage`: library only | opt-in candidate in progress: The [pinned Bitwarden AppImage operation](migrations/publisher-apps-06.md) checks the official release manifest and SHA-512, owns one user file, and preserves vault data; Fedora 44 Workstation acceptance is pending. | `publisher-apps-06` / supported |
| `action.ImportOpenVPNProfiles` | `ImportOpenVPNProfiles` | `ImportOpenVPNProfiles`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior | `system-security-09` / resolved |
| `package.VPNProfiles` | `RemoveVPNProfiles` | `RemoveVPNProfiles`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-20` / supported |
| `package.ExpressVPNProfiles` | `RemoveExpressVPNProfiles` | `RemoveExpressVPNProfiles`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-21` / supported |
| `package.ExpressVPN` | `InstallExpressVPN`, `RemoveExpressVPN` | `InstallExpressVPN`: commented, `RemoveExpressVPN`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-10` / operable |
| `action.StartExpressVPNafterBoot` | `StartExpressVPNafterBoot` | `StartExpressVPNafterBoot`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior | `system-security-11` / resolved |
| `package.ExpressVPNafterBoot` | `RemoveExpressVPNafterBoot` | `RemoveExpressVPNafterBoot`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-22` / resolved |
| `action.CreateExpVPNrandomizer` | `CreateExpVPNrandomizer` | `CreateExpVPNrandomizer`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior | `system-security-12` / resolved |
| `action.ScheduleRandomExpVPNChange` | `ScheduleRandomExpVPNChange` | `ScheduleRandomExpVPNChange`: library only | deferred; classify as explicit operation, private value, CLI utility or retired behavior | `system-security-23` / resolved |
| `package.ScheduleExpVPNChange` | `RemoveScheduleExpVPNChange` | `RemoveScheduleExpVPNChange`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-24` / unresolved |
| `package.Cheat` | `InstallCheat`, `RemoveCheat` | `InstallCheat`: active, `RemoveCheat`: library only | deferred: Review current upstream and source. | `publisher-apps-16` / supported |
| `package.UnifyingOnLaptop` | `InstallUnifyingOnLaptop`, `RemoveUnifyingOnLaptop` | `InstallUnifyingOnLaptop`: active, `RemoveUnifyingOnLaptop`: library only | deferred: Hardware-dependent operation. | `publisher-apps-07` / operable |
| `package.Projecteur` | `InstallProjecteur`, `RemoveProjecteur` | `InstallProjecteur`: commented, `RemoveProjecteur`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-13` / operable |
| `package.VMtoolsOnVM` | `InstallVMtoolsOnVM`, `RemoveVMtoolsOnVM` | `InstallVMtoolsOnVM`: active, `RemoveVMtoolsOnVM`: library only | deferred: VM-specific provider after detection test. | `publisher-apps-07` / operable |
| `package.YubikeyManager` | `InstallYubikeyManager`, `RemoveYubikeyManager` | `InstallYubikeyManager`: active, `RemoveYubikeyManager`: library only | deferred: Hardware-dependent optional package. | `publisher-apps-08` / operable |
| `package.YubikeyPersTool` | `InstallYubikeyPersTool` | `InstallYubikeyPersTool`: commented | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-14` / operable |
| `package.Xmind` | `InstallXmind`, `RemoveXmind` | `InstallXmind`: commented, `RemoveXmind`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-15` / operable |
| `package.SonosPlayer` | `InstallSonosPlayer`, `RemoveSonosPlayer` | `InstallSonosPlayer`: active, `RemoveSonosPlayer`: library only | deferred: Review publisher source and architecture. | `publisher-apps-09` / resolved |
| `package.VMwareWorkstation` | `InstallVMwareWorkstation`, `RemoveVMwareWorkstation` | `InstallVMwareWorkstation`: commented, `RemoveVMwareWorkstation`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-13` / resolved |
| `action.PatchVMwareModules` | `PatchVMwareModules` | `PatchVMwareModules`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior | `system-security-14` / resolved |
| `action.AddExtraLUKSpasswords` | `AddExtraLUKSpasswords` | `AddExtraLUKSpasswords`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior | `system-security-15` / resolved |
| `action.EncryptUnpartitionedDisks` | `EncryptUnpartitionedDisks` | `EncryptUnpartitionedDisks`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior | `system-security-16` / resolved |
| `action.ReclaimEncryptDWUnmntPrt` | `ReclaimEncryptDWUnmntPrt` | `ReclaimEncryptDWUnmntPrt`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior | `system-security-17` / resolved |
| `package.KeyfileMounts` | `RemoveKeyfileMounts` | `RemoveKeyfileMounts`: library only | operable opt-in candidate `setting.keyfile-mounts`; Fedora 44 Workstation LUKS data and reboot recovery passed; see system-security-25 and its acceptance record | `system-security-25` / operable |
| `setting.SSHreboot` | `EnableSSHreboot`, `DisableSSHreboot` | `EnableSSHreboot`: commented, `DisableSSHreboot`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `system-security-18` / operable |

`PressAnyKeyToContinue` and `Restart` are active default selectors but live outside
`lib-fedora.sh`; both are retired as install outcomes in the active ledger.
`RequireAdmin` is a commented controller selector, also outside the library.

## Reference-script candidates

These are review inputs outside the v2 function libraries. They have no executable
v3 catalog ID and are not selected by a profile.

| Outcome | Reference | Status | Migration review |
| --- | --- | --- | --- |
| Waydroid on a mutable Fedora workstation | [install-waydroid-fedora.sh](../reference/install-waydroid-fedora.sh) | deferred; reference-only and not clean-VM tested | Split Fedora package installation, OTA image initialization, container service, and optional firewalld policy into owned changes. Verify image provenance, repeat apply, partial failure, removal and restore on a disposable Fedora Wayland workstation. Keep forced reinitialization explicit. |

## Server library and presets

| Outcome key | Exact source functions | Active presets | Commented presets | Initial disposition / review rationale | Batch / current progress |
| --- | --- | --- | --- | --- | --- |
| `action.UpdateFedora` | `UpdateFedora` | complete, plexserver, streambox | — | deferred generic server baseline; split package/update/timer behavior and record recovery limits | `generic-server-01` / operable |
| `package.Required` | `InstallRequired` | complete, plexserver, streambox | — | operable opt-in: eleven Fedora RPM operations in the separated `server-required-tools` and `server-firewall-package` profiles; see the Server acceptance record | `generic-server-02` / operable |
| `package.AutoUpdate` | `InstallAutoUpdate` | complete, plexserver, streambox | — | deferred generic server baseline; split package/update/timer behavior and record recovery limits | `generic-server-03` / operable |
| `action.ViewIPaddress` | `ViewIPaddress` | complete, plexserver, streambox | — | retire as install outcome; expose inspection through `status` if useful | `generic-server-04` / resolved |
| `setting.Hostname` | `SetHostname` | complete, plexserver, streambox | — | private overlay for host values or key material; extract generic behavior only after ownership review | `generic-server-05` / supported |
| `package.Docker` | `InstallDocker` | complete | — | deferred optional server operation; verify current package/source, state and recovery | `generic-server-06` / supported |
| `package.Tailscale` | `InstallTailscale` | — | — | deferred optional server operation; verify current package/source, state and recovery | `generic-server-14` / operable |
| `package.Glances` | `InstallGlances` | complete | — | deferred optional server operation; verify current package/source, state and recovery | `generic-server-07` / supported |
| `package.PythonPip` | `InstallPythonPip` | — | complete | replace global Python installation with isolated, pinned per-tool environment | `generic-server-12` / supported |
| `package.Selenium` | `InstallSelenium` | — | complete | replace global Python installation with isolated, pinned per-tool environment | `generic-server-12` / operable |
| `setting.NoRootLogin` | `SetNoRootLogin` | complete | — | deferred SSH policy setting; preserve existing file content and test exact restore | `generic-server-08` / operable |
| `action.GenerateSSHkeysRSA` | `GenerateSSHkeysRSA` | — | complete | private overlay for host values or key material; extract generic behavior only after ownership review | `generic-server-13` / resolved |
| `package.ExpressVPN` | `InstallExpressVPN` | complete, streambox | plexserver | deferred opt-in VPN profile; keep provider account and host routing private | `generic-server-09` / operable |
| `action.CreateVPNrandomizer` | `CreateVPNrandomizer` | complete, streambox | plexserver | deferred opt-in VPN profile; keep provider account and host routing private | `generic-server-10` / resolved |
| `setting.VPNRandomizerPersistent` | `SetVPNRandomizerPersistent` | complete, streambox | plexserver | deferred opt-in VPN profile; keep provider account and host routing private | `generic-server-11` / unresolved |
| `package.qBittorrentServer` | `InstallqBittorrentServer` | complete, streambox | plexserver | deferred optional server operation; verify current package/source, state and recovery | `generic-server-15` / supported |
| `package.PlexServer` | `InstallPlexServer` | complete, plexserver | streambox | deferred optional server operation; verify current package/source, state and recovery | `generic-server-16` / supported |
| `package.PlexAutoUpdate` | `InstallPlexAutoUpdate` | complete, plexserver | streambox | deferred optional server operation; verify current package/source, state and recovery | `generic-server-17` / resolved |
| `package.AMP` | `InstallAMP` | complete | — | deferred optional server operation; verify current package/source, state and recovery | `generic-server-18` / operable |
| `package.Ferium` | `InstallFerium` | — | — | deferred optional server operation; verify current package/source, state and recovery | `generic-server-19` / operable |
| `package.MinecraftServer` | `InstallMinecraftServer` | complete | plexserver, streambox | deferred optional server operation; verify current package/source, state and recovery | `generic-server-20` / operable |

`RequireAdmin`, `PressAnyKeyToContinue` and `Restart` appear as active server preset
selectors but are controller flow, not server-library outcomes. The commented
`GenerateSSHkeys` selector is not defined in the server library; it must not silently
resolve to `GenerateSSHkeysRSA` without a migration decision.

## Current retirement and replacement decisions

These dispositions come from `migration/outcomes.json` and supersede the
initial assessment above. The ledger records each reason and review trigger.

| Source outcome | Current disposition | Batch |
| --- | --- | --- |
| `workstation:package.DNFutils` | `replace` | `provider-foundation-03` |
| `workstation:package.VersionLock` | `replace` | `provider-foundation-04` |
| `workstation:package.NautilusHash` | `retire` | `native-rpm-03` |
| `workstation:package.NautilusImageTools` | `retire` | `native-rpm-03` |
| `workstation:package.Macvendor` | `replace` | `forensic-isolated-03` |
| `workstation:package.MicrosoftTeams` | `retire` | `publisher-apps-09` |
| `workstation:package.AtomEditor` | `retire` | `publisher-apps-10` |
| `workstation:setting.AtomTelemetry` | `retire` | `resolution-review-01` |
| `workstation:package.AtomPlugins` | `retire` | `publisher-apps-10` |
| `workstation:package.Pidgin` | `retire` | `system-security-27` |
| `workstation:action.CheckFirefoxAddons` | `replace` | `desktop-user-05` |
| `workstation:action.FinalizeFirefoxAddonRemoval` | `replace` | `desktop-user-06` |
| `workstation:package.GnomeExtensions` | `replace` | `publisher-apps-17` |
| `workstation:setting.AliasRideLog` | `retire` | `desktop-user-05` |
| `workstation:action.StartExpressVPNafterBoot` | `replace` | `system-security-11` |
| `workstation:package.ExpressVPNafterBoot` | `replace` | `system-security-22` |
| `workstation:package.SonosPlayer` | `retire` | `publisher-apps-09` |
| `workstation:package.VMwareWorkstation` | `retire` | `system-security-13` |
| `server:action.ViewIPaddress` | `retire` | `generic-server-04` |
| `server:package.PlexAutoUpdate` | `replace` | `generic-server-17` |

## Closeout rules

1. Count an outcome as operable only with a mapped v3 operation and focused
   automated evidence. Only a target-specific VM pass permits supported status.
   Keep candidate, supported, and non-operable resolutions distinct.
2. Mark a retired outcome only with a concrete reason. Do not turn an old no-op
   function into a successful v3 operation.
3. Reconcile server consumers in `complete`, `plexserver`, and `streambox` before
   moving generic behavior. Keep hostname, NAS, accounts, secrets and media paths
   in a private overlay.
4. Regenerate this table after any source inventory or disposition change with
   `python3 tools/build_burndown.py --write`.
