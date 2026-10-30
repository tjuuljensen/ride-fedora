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
| `action.SetupUserDefaultDirs` | `SetupUserDefaultDirs` | `SetupUserDefaultDirs`: active | deferred: Review directory ownership and user scope. | `desktop-user-01` / resolved |
| `setting.Hostname` | `SetHostname` | `SetHostname`: active | deferred: Host-specific value belongs in private profile. | `system-security-01` / resolved |
| `setting.FastDNF` | `EnableFastDNF`, `DisableFastDNF` | `EnableFastDNF`: active, `DisableFastDNF`: library only | unsupported: DNF5 still defaults to three parallel downloads; the v2 file edit has no owned inverse. See the [system review](migrations/system-security-core.md). | `system-security-01` / resolved |
| `action.UpdateFedora` | `UpdateFedora` | `UpdateFedora`: active | deferred: Add explicit non-reversible system update operation after VM acceptance. | `system-security-02` / resolved |
| `package.Required` | `InstallRequired` | `InstallRequired`: active | replaced: The global seven-package bundle is replaced by bootstrap and handler prerequisite checks. Optional developer tools need a separate requested profile; see [provider foundation batch 01](migrations/provider-foundation-01.md). | `provider-foundation-01` / resolved |
| `package.ShellTools` | `InstallShellTools`, `RemoveShellTools` | `InstallShellTools`: active, `RemoveShellTools`: library only | supported: Split into supported `package.pv` and `package.strace` in the opt-in `shell-tools` profile; see [VM acceptance](acceptance/provider-shell-tools.md). | `provider-foundation-01` / supported |
| `package.RPMfusionRepos` | `InstallRPMfusionRepos`, `RemoveRPMfusionRepos` | `InstallRPMfusionRepos`: active, `RemoveRPMfusionRepos`: library only | unsupported: [Provider batch 02](migrations/provider-foundation-02.md) records the signing-key and owned-recovery work required before a runnable operation. | `provider-foundation-02` / resolved |
| `package.KernelTools` | `InstallKernelTools`, `RemoveKernelTools` | `InstallKernelTools`: active, `RemoveKernelTools`: library only | supported: Split into signed Fedora `kernel-devel` and `kernel-headers` package installs; [VM evidence](acceptance/provider-kernel-tools.md) does not establish a matching module-build environment. | `provider-foundation-03` / supported |
| `package.DNFutils` | `InstallDNFutils`, `RemoveDNFutils` | `InstallDNFutils`: active, `RemoveDNFutils`: library only | replaced: Fedora 44 Workstation has DNF5 and plugins; current `config-manager` and `download` commands passed the disposable-VM check. See [provider foundation batch 03](migrations/provider-foundation-03.md). | `provider-foundation-03` / resolved |
| `package.Eza` | `InstallEza`, `RemoveEza` | `InstallEza`: library only, `RemoveEza`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `provider-foundation-08` / supported |
| `package.EzaGitHub` | `InstallEzaGitHub` | `InstallEzaGitHub`: active | replaced: The unpinned ZIP path is a [non-runnable replacement](migrations/provider-foundation-08.md); Fedora `package.eza` passed [VM acceptance](acceptance/package.eza.md) for an installed Eza. | `provider-foundation-08` / resolved |
| `package.VersionLock` | `InstallVersionLock`, `RemoveVersionLock` | `InstallVersionLock`: commented, `RemoveVersionLock`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `provider-foundation-04` / resolved |
| `package.NautilusHash` | `InstallNautilusHash`, `RemoveNautilusHash` | `InstallNautilusHash`: commented, `RemoveNautilusHash`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-03` / resolved |
| `package.NautilusImageTools` | `InstallNautilusImageTools`, `RemoveNautilusImageTools` | `InstallNautilusImageTools`: commented, `RemoveNautilusImageTools`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-03` / resolved |
| `package.Flatpak` | `InstallFlatpak`, `RemoveFlatpak` | `InstallFlatpak`: commented, `RemoveFlatpak`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `provider-foundation-11` / resolved |
| `package.Flathub` | `InstallFlathub`, `RemoveFlathub` | `InstallFlathub`: active, `RemoveFlathub`: library only | unsupported: [Flathub remote ownership](migrations/provider-foundation-09.md) needs a scoped handler, app preservation, and inverse evidence before it is runnable. | `provider-foundation-09` / resolved |
| `package.AppImageLauncher` | `InstallAppImageLauncher`, `RemoveAppImageLauncher` | `InstallAppImageLauncher`: active, `RemoveAppImageLauncher`: library only | deferred: Review maintained source and current desktop integration. | `publisher-apps-01` / resolved |
| `package.Snap` | `InstallSnap`, `RemoveSnap` | `InstallSnap`: commented, `RemoveSnap`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `provider-foundation-12` / resolved |
| `package.Galleta` | `InstallGalleta`, `RemoveGalleta` | `InstallGalleta`: commented, `RemoveGalleta`: library only | deferred incomplete legacy stub; source and current package need review | `resolution-review-01` / resolved |
| `package.Plaso` | `InstallPlaso`, `RemovePlaso` | `InstallPlaso`: commented, `RemovePlaso`: library only | deferred candidate; opt-in COPR and removal need VM evidence | `forensic-isolated-02` / resolved |
| `package.Autopsy` | `InstallAutopsy`, `RemoveAutopsy` | `InstallAutopsy`: commented, `RemoveAutopsy`: library only | deferred candidate; upstream Linux setup and removal need VM evidence | `forensic-isolated-02` / resolved |
| `package.Xplico` | `InstallXplico`, `RemoveXplico` | `InstallXplico`: commented, `RemoveXplico`: library only | deferred incomplete legacy stub; source and current package need review | `resolution-review-01` / resolved |
| `package.VMFStools` | `InstallVMFStools`, `RemoveVMFStools` | `InstallVMFStools`: active, `RemoveVMFStools`: library only | retired: The active function only prints URLs; [forensic batch 01](migrations/forensic-isolated-01.md) records the no-op and reopening trigger. | `forensic-isolated-01` / resolved |
| `package.Volatility` | `InstallVolatility`, `RemoveVolatility` | `InstallVolatility`: commented, `RemoveVolatility`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `forensic-isolated-02` / resolved |
| `package.Volatility3` | `InstallVolatility3`, `RemoveVolatility3` | `InstallVolatility3`: commented, `RemoveVolatility3`: library only | implemented candidate `package.volatility3`; isolated pinned core, VM acceptance pending | `forensic-isolated-02` / operable |
| `package.VeraCrypt` | `InstallVeraCrypt`, `UninstallVeraCrypt` | `InstallVeraCrypt`: active, `UninstallVeraCrypt`: library only | deferred: Review publisher verification and licensing. | `publisher-apps-02` / resolved |
| `package.BulkExtractor` | `InstallBulkExtractor`, `RemoveBulkExtractor` | `InstallBulkExtractor`: commented, `RemoveBulkExtractor`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `forensic-isolated-04` / resolved |
| `package.EmailHeaderAnlzr` | `InstallEmailHeaderAnlzr`, `RemoveEmailHeaderAnlzr` | `InstallEmailHeaderAnlzr`: commented, `RemoveEmailHeaderAnlzr`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `forensic-isolated-06` / resolved |
| `package.LibEWF` | `InstallLibEWF`, `RemoveLibEWF` | `InstallLibEWF`: active, `RemoveLibEWF`: library only | replaced: package.ewftools covers EWF utilities; verify library intent separately. | `native-rpm-02` / supported |
| `package.SecurityLab` | `InstallSecurityLab`, `RemoveSecurityLab` | `InstallSecurityLab`: commented, `RemoveSecurityLab`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `provider-foundation-06` / resolved |
| `package.Dc3dd` | `InstallDc3dd`, `RemoveDc3dd` | `InstallDc3dd`: commented, `RemoveDc3dd`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-04` / supported |
| `package.Exif` | `InstallExif`, `RemoveExif` | `InstallExif`: active, `RemoveExif`: library only | deferred: Review product identity and official package. | `native-rpm-02` / supported |
| `package.Binwalk` | `InstallBinwalk`, `RemoveBinwalk` | `InstallBinwalk`: commented, `RemoveBinwalk`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `forensic-isolated-03` / supported |
| `package.Md5deep` | `InstallMd5deep`, `RemoveMd5deep` | `InstallMd5deep`: active, `RemoveMd5deep`: library only | deferred: Review current package and forensic use case. | `native-rpm-02` / supported |
| `package.Libpst` | `InstallLibpst`, `RemoveLibpst` | `InstallLibpst`: library only, `RemoveLibpst`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-05` / supported |
| `package.Macvendor` | `InstallMacvendor`, `RemoveMacvendor` | `InstallMacvendor`: library only, `RemoveMacvendor`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `forensic-isolated-03` / resolved |
| `package.ExifTool` | `InstallExifTool`, `RemoveExifTool` | `InstallExifTool`: active, `RemoveExifTool`: library only | supported: Fedora `perl-Image-ExifTool` passed [VM lifecycle acceptance](acceptance/package.exiftool.md); the v2 GitHub/CPAN build path is not adopted. | `forensic-isolated-01` / supported |
| `package.ASN` | `InstallASN`, `RemoveASN` | `InstallASN`: active, `RemoveASN`: library only | unsupported: [Forensic batch 01](migrations/forensic-isolated-01.md) requires a pinned owned script and shared-dependency-safe inverse. | `forensic-isolated-01` / resolved |
| `package.UnfURL` | `InstallUnfURL`, `RemoveUnfURL` | `InstallUnfURL`: active, `RemoveUnfURL`: library only | unsupported: [Forensic batch 01](migrations/forensic-isolated-01.md) requires a pinned isolated Python environment. | `forensic-isolated-01` / operable |
| `package.CyberChef` | `InstallCyberChef`, `RemoveCyberChef` | `InstallCyberChef`: active, `RemoveCyberChef`: library only | unsupported: [Forensic batch 01](migrations/forensic-isolated-01.md) requires a pinned offline artifact and owned desktop destination. | `forensic-isolated-01` / resolved |
| `package.Chepy` | `InstallChepy`, `RemoveChepy` | `InstallChepy`: active, `RemoveChepy`: library only | unsupported: [Forensic batch 01](migrations/forensic-isolated-01.md) requires a pinned isolated build and owned inverse. | `forensic-isolated-01` / resolved |
| `package.Dumpzilla` | `InstallDumpzilla`, `RemoveDumpzilla` | `InstallDumpzilla`: commented, `RemoveDumpzilla`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `forensic-isolated-03` / resolved |
| `package.NetworkMiner` | `InstallNetworkMiner`, `RemoveNetworkMiner` | `InstallNetworkMiner`: active, `RemoveNetworkMiner`: library only | deferred: Align product identity with Windows; review Linux packaging. | `forensic-isolated-05` / resolved |
| `package.Pwgen` | `InstallPwgen`, `RemovePwgen` | `InstallPwgen`: active, `RemovePwgen`: library only | deferred: Candidate native repository package. | `native-rpm-01` / supported |
| `package.Htop` | `InstallHtop`, `RemoveHtop` | `InstallHtop`: active, `RemoveHtop`: library only | deferred: Candidate native repository package. | `native-rpm-01` / supported |
| `package.Bat` | `InstallBat`, `RemoveBat` | `InstallBat`: active, `RemoveBat`: library only | deferred: Candidate native repository package. | `native-rpm-01` / supported |
| `package.Ncdu` | `InstallNcdu`, `RemoveNcdu` | `InstallNcdu`: active, `RemoveNcdu`: library only | deferred: Candidate native repository package. | `native-rpm-01` / supported |
| `package.Ripgrep` | `InstallRipgrep`, `RemoveRipgrep` | `InstallRipgrep`: active, `RemoveRipgrep`: library only | deferred: Candidate native repository package. | `native-rpm-01` / supported |
| `package.Fd` | `InstallFd`, `RemoveFd` | `InstallFd`: active, `RemoveFd`: library only | deferred: Candidate native repository package. | `native-rpm-01` / supported |
| `package.Docker` | `InstallDocker`, `RemoveDocker` | `InstallDocker`: active, `RemoveDocker`: library only | deferred: Generic server role only after provider and repository review. | `system-security-03` / resolved |
| `package.PythonPip` | `InstallPythonPip`, `RemovePythonPip` | `InstallPythonPip`: active, `RemovePythonPip`: library only | supported: Fedora `python3-pip` passed [VM lifecycle acceptance](acceptance/package.python3-pip.md); omit the v2 global pip self-upgrade. | `provider-foundation-03` / supported |
| `package.PackagingTools` | `InstallPackagingTools`, `RemovePackagingTools` | `InstallPackagingTools`: active, `RemovePackagingTools`: library only | replaced: Fedora `7zip` and `unar` passed [VM package acceptance](acceptance/provider-archive-tools.md); `unar` is a different CLI from `unrar`. | `provider-foundation-03` / resolved |
| `package.BasicEditors` | `InstallBasicEditors`, `RemoveBasicEditors` | `InstallBasicEditors`: active, `RemoveBasicEditors`: library only | supported: Split into Fedora `nano` and `vim-enhanced` package installs with [VM evidence](acceptance/provider-basic-editors.md). | `provider-foundation-04` / supported |
| `package.CommanderFileMgrs` | `InstallCommanderFileMgrs`, `RemoveCommanderFileMgrs` | `InstallCommanderFileMgrs`: commented, `RemoveCommanderFileMgrs`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-09` / operable |
| `package.Terminator` | `InstallTerminator`, `RemoveTerminator` | `InstallTerminator`: active, `RemoveTerminator`: library only | deferred: Optional desktop profile only. | `desktop-user-10` / resolved |
| `package.Alien` | `InstallAlien`, `RemoveAlien` | `InstallAlien`: active, `RemoveAlien`: library only | deferred: Review relevance and support. | `native-rpm-02` / supported |
| `package.SmartMonTools` | `InstallSmartMonTools`, `RemoveSmartMonTools` | `InstallSmartMonTools`: active, `RemoveSmartMonTools`: library only | deferred: Optional system tools profile. | `system-security-26` / resolved |
| `package.Qbittorrent` | `InstallQbittorrent`, `RemoveQbittorrent` | `InstallQbittorrent`: commented, `RemoveQbittorrent`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-04` / operable |
| `package.PowerShell` | `InstallPowerShell`, `RemovePowerShell` | `InstallPowerShell`: commented, `RemovePowerShell`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-09` / resolved |
| `package.MicrosoftTeams` | `InstallMicrosoftTeams`, `RemoveMicrosoftTeams` | `InstallMicrosoftTeams`: commented, `RemoveMicrosoftTeams`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-09` / resolved |
| `package.WoeUSB` | `InstallWoeUSB`, `RemoveWoeUSB` | `InstallWoeUSB`: commented, `RemoveWoeUSB`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-09` / resolved |
| `package.BalenaEtcher` | `InstallBalenaEtcher`, `RemoveBalenaEtcher` | `InstallBalenaEtcher`: commented, `RemoveBalenaEtcher`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-09` / resolved |
| `package.VisualStudioCode` | `InstallVisualStudioCode`, `RemoveVisualStudioCode` | `InstallVisualStudioCode`: active, `RemoveVisualStudioCode`: library only | deferred: Align product facts with Windows; Fedora source stays local. | `publisher-apps-03` / resolved |
| `package.ArduinoIDE` | `InstallArduinoIDE`, `RemoveArduinoIDE` | `InstallArduinoIDE`: commented, `RemoveArduinoIDE`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-10` / resolved |
| `package.AtomEditor` | `InstallAtomEditor`, `RemoveAtomEditor` | `InstallAtomEditor`: commented, `RemoveAtomEditor`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-10` / resolved |
| `setting.AtomTelemetry` | `DisableAtomTelemetry`, `EnableAtomTelemetry` | `DisableAtomTelemetry`: commented, `EnableAtomTelemetry`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `resolution-review-01` / resolved |
| `package.AtomPlugins` | `InstallAtomPlugins`, `RemoveAtomPlugins` | `InstallAtomPlugins`: commented, `RemoveAtomPlugins`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-10` / resolved |
| `package.PyhtonAutopep8` | `InstallPyhtonAutopep8`, `RemovePyhtonAutopep8` | `InstallPyhtonAutopep8`: commented, `RemovePyhtonAutopep8`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `forensic-isolated-03` / supported |
| `package.Hexchat` | `InstallHexchat`, `RemoveHexchat` | `InstallHexchat`: active, `RemoveHexchat`: library only | deferred: Review upstream maintenance before reintroduction. | `native-rpm-03` / operable |
| `package.Discord` | `InstallDiscord`, `RemoveDiscord` | `InstallDiscord`: commented, `RemoveDiscord`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-10` / resolved |
| `package.Pidgin` | `InstallPidgin`, `RemovePidgin` | `InstallPidgin`: commented, `RemovePidgin`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-27` / resolved |
| `package.Thunderbird` | `InstallThunderbird`, `RemoveThunderbird` | `InstallThunderbird`: commented, `RemoveThunderbird`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-04` / operable |
| `setting.MulticastDNS` | `DisableMulticastDNS`, `EnableMulticastDNS` | `DisableMulticastDNS`: commented, `EnableMulticastDNS`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `system-security-06` / resolved |
| `package.NetworkTools` | `InstallNetworkTools`, `RemoveNetworkTools` | `InstallNetworkTools`: active, `RemoveNetworkTools`: library only | deferred: Split broad network bundle into focused packages. | `system-security-04` / operable |
| `package.NetCommsTools` | `InstallNetCommsTools`, `RemoveNetCommsTools` | `InstallNetCommsTools`: active, `RemoveNetCommsTools`: library only | deferred: Split broad communications bundle. | `system-security-04` / operable |
| `package.NetMgrL2TP` | `InstallNetMgrL2TP`, `RemoveNetMgrL2TP` | `InstallNetMgrL2TP`: commented, `RemoveNetMgrL2TP`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-07` / supported |
| `package.NetMgrLibreswan` | `InstallNetMgrLibreswan`, `RemoveNetMgrLibreswan` | `InstallNetMgrLibreswan`: active, `RemoveNetMgrLibreswan`: library only | deferred: Optional VPN role. | `system-security-05` / supported |
| `package.Wireguard` | `InstallWireguard`, `RemoveWireguard` | `InstallWireguard`: library only, `RemoveWireguard`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-19` / resolved |
| `package.OpenconnectVPN` | `InstallOpenconnectVPN` | `InstallOpenconnectVPN`: commented | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-08` / resolved |
| `package.SpeedtestCLI` | `InstallSpeedtestCLI`, `RemoveSpeedtestCLI` | `InstallSpeedtestCLI`: active, `RemoveSpeedtestCLI`: library only | deferred: Review current upstream and source. | `native-rpm-03` / supported |
| `package.Flameshot` | `InstallFlameshot`, `RemoveFlameshot` | `InstallFlameshot`: commented, `RemoveFlameshot`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-04` / operable |
| `package.Dia` | `InstallDia`, `RemoveDia` | `InstallDia`: commented, `RemoveDia`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-05` / operable |
| `package.Wine` | `InstallWine`, `RemoveWine` | `InstallWine`: commented, `RemoveWine`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-05` / operable |
| `package.Joplin` | `InstallJoplin`, `RemoveJoplin` | `InstallJoplin`: commented, `RemoveJoplin`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-10` / resolved |
| `package.TecmintMonitorSh` | `InstallTecmintMonitorSh`, `RemoveTecmintMonitorSh` | `InstallTecmintMonitorSh`: active, `RemoveTecmintMonitorSh`: library only | retired: Default profile must not fetch and execute remote scripts. | `resolution-review-01` / resolved |
| `package.GnomeExtInstaller` | `InstallGnomeExtInstaller`, `RemoveGnomeExtInstaller` | `InstallGnomeExtInstaller`: active, `RemoveGnomeExtInstaller`: library only | unsupported: [Archived upstream](migrations/provider-foundation-10.md), unpinned clone, and unowned path removal lack Fedora 44 compatibility and safe recovery. | `provider-foundation-10` / resolved |
| `package.Brave` | `InstallBrave`, `RemoveBrave` | `InstallBrave`: active, `RemoveBrave`: library only | deferred: Third-party repository and license review. | `publisher-apps-03` / resolved |
| `package.Vivaldi` | `InstallVivaldi`, `RemoveVivaldi` | `InstallVivaldi`: commented, `RemoveVivaldi`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-10` / resolved |
| `package.Chromium` | `InstallChromium`, `RemoveChromium` | `InstallChromium`: active, `RemoveChromium`: library only | deferred: Candidate distro repository package. | `native-rpm-03` / operable |
| `package.Chrome` | `InstallChrome`, `RemoveChrome` | `InstallChrome`: commented, `RemoveChrome`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-11` / resolved |
| `setting.ChromePreferences` | `SetChromePreferences`, `UnsetChromePreferences` | `SetChromePreferences`: commented, `UnsetChromePreferences`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-05` / resolved |
| `setting.FirefoxPreferences` | `SetFirefoxPreferences`, `UnsetFirefoxPreferences` | `SetFirefoxPreferences`: active, `UnsetFirefoxPreferences`: library only | replaced: Review settings against current Firefox policy; avoid legacy file overwrite. | `desktop-user-01` / resolved |
| `action.CheckFirefoxAddons` | `CheckFirefoxAddons` | `CheckFirefoxAddons`: library only | deferred v3 integration; existing policy helper remains tested separately | `desktop-user-05` / resolved |
| `package.FirefoxAddons` | `InstallFirefoxAddons`, `RemoveFirefoxAddons` | `InstallFirefoxAddons`: active, `RemoveFirefoxAddons`: library only | deferred: Keep existing verified policy helper; integrate with v3 lifecycle later. | `publisher-apps-04` / resolved |
| `action.FinalizeFirefoxAddonRemoval` | `FinalizeFirefoxAddonRemoval` | `FinalizeFirefoxAddonRemoval`: library only | deferred v3 integration; restart-dependent policy lifecycle needs journal ownership | `desktop-user-06` / resolved |
| `package.Edge` | `InstallEdge`, `RemoveEdge` | `InstallEdge`: commented, `RemoveEdge`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-11` / resolved |
| `package.Codecs` | `InstallCodecs`, `RemoveCodecs` | `InstallCodecs`: commented, `RemoveCodecs`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `provider-foundation-05` / resolved |
| `package.SpotifyClient` | `InstallSpotifyClient`, `RemoveSpotifyClient` | `InstallSpotifyClient`: commented, `RemoveSpotifyClient`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-11` / resolved |
| `package.VLCPlayer` | `InstallVLCPlayer`, `RemoveVLCPlayer` | `InstallVLCPlayer`: commented, `RemoveVLCPlayer`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-05` / operable |
| `package.ClementinePlayer` | `InstallClementinePlayer`, `RemoveClementinePlayer` | `InstallClementinePlayer`: commented, `RemoveClementinePlayer`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-11` / operable |
| `package.PulseAudioEq` | `InstallPulseAudioEq`, `RemovePulseAudioEq` | `InstallPulseAudioEq`: commented, `RemovePulseAudioEq`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-11` / operable |
| `package.YouTubeDownloader` | `InstallYouTubeDownloader`, `RemoveYouTubeDownloader` | `InstallYouTubeDownloader`: active, `RemoveYouTubeDownloader`: library only | replaced: Review maintained yt-dlp packaging instead of legacy youtube-dl. | `publisher-apps-05` / supported |
| `package.GIMP` | `InstallGIMP`, `RemoveGIMP` | `InstallGIMP`: commented, `RemoveGIMP`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-04` / operable |
| `package.HandBrake` | `InstallHandBrake`, `RemoveHandBrake` | `InstallHandBrake`: commented, `RemoveHandBrake`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `provider-foundation-07` / resolved |
| `package.GnomeTools` | `InstallGnomeTools`, `RemoveGnomeTools` | `InstallGnomeTools`: active, `RemoveGnomeTools`: library only | opt-in candidate: Fedora printer UI and GNOME Tweaks passed [package VM acceptance](acceptance/provider-gnome-tools.md); visual checks remain v3.1, and v2's unowned `gparted` removal is excluded. | `provider-foundation-04` / operable |
| `package.SystemMonitor` | `InstallSystemMonitor`, `RemoveSystemMonitor` | `InstallSystemMonitor`: active, `RemoveSystemMonitor`: library only | deferred: Review current GNOME extension support. | `publisher-apps-05` / operable |
| `package.GnomeExtensions` | `InstallGnomeExtensions`, `RemoveGnomeExtensions` | `InstallGnomeExtensions`: active, `RemoveGnomeExtensions`: library only | deferred: Review current GNOME extension IDs and API. | `publisher-apps-17` / resolved |
| `setting.ScreenSaver` | `EnableScreenSaver` | `EnableScreenSaver`: active | retired: Conflicts with DisableScreensaver in the same legacy preset; review one desired state. | `resolution-review-01` / resolved |
| `setting.Screensaver` | `DisableScreensaver` | `DisableScreensaver`: active | retired: Conflicts with EnableScreenSaver in the same legacy preset; review a single desired state later. | `resolution-review-01` / resolved |
| `setting.DateInTaskbar` | `ShowDateInTaskbar`, `HideDateInTaskbar` | `ShowDateInTaskbar`: active, `HideDateInTaskbar`: library only | deferred: Setting handler needs baseline and restore. | `desktop-user-02` / operable |
| `setting.WeekNumbersInTaskbar` | `ShowWeekNumbersInTaskbar`, `HideWeekNumbersInTaskbar` | `ShowWeekNumbersInTaskbar`: active, `HideWeekNumbersInTaskbar`: library only | deferred: Setting handler needs baseline and restore. | `desktop-user-02` / operable |
| `setting.WindowCtlMinMaxClose` | `SetWindowCtlMinMaxClose` | `SetWindowCtlMinMaxClose`: active | deferred: Setting handler needs baseline and restore. | `desktop-user-02` / resolved |
| `setting.WindowCtlAppmenuClose` | `SetWindowCtlAppmenuClose` | `SetWindowCtlAppmenuClose`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-07` / resolved |
| `setting.WindowCtlLeftClsMinMax` | `SetWindowCtlLeftClsMinMax` | `SetWindowCtlLeftClsMinMax`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-07` / resolved |
| `setting.MiddleButtonPaste` | `EnableMiddleButtonPaste`, `DisableMiddleButtonPaste` | `EnableMiddleButtonPaste`: library only, `DisableMiddleButtonPaste`: active | deferred: Setting handler needs baseline and restore. | `desktop-user-02` / operable |
| `setting.GnomeRegionDaDK` | `SetGnomeRegionDaDK` | `SetGnomeRegionDaDK`: active | deferred: User locale must be explicit profile data. | `desktop-user-02` / resolved |
| `package.GnomeRegion` | `RemoveGnomeRegion` | `RemoveGnomeRegion`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `desktop-user-02` / resolved |
| `setting.ScreensaverSlp10Lgn5` | `SetScreensaverSlp10Lgn5` | `SetScreensaverSlp10Lgn5`: active | deferred: Resolve conflict with other screensaver operations. | `desktop-user-11` / resolved |
| `setting.ScreensaverSlp15Lgn5` | `SetScreensaverSlp15Lgn5` | `SetScreensaverSlp15Lgn5`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-11` / resolved |
| `setting.CustomKeyboardShortcut` | `SetCustomKeyboardShortcut` | `SetCustomKeyboardShortcut`: active | deferred: User-owned shortcut state needs exact restore. | `desktop-user-03` / resolved |
| `setting.VMKeyboardShortcut` | `SetVMKeyboardShortcut` | `SetVMKeyboardShortcut`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-08` / resolved |
| `package.CustomKbrdShortcut` | `RemoveCustomKbrdShortcut` | `RemoveCustomKbrdShortcut`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `desktop-user-03` / resolved |
| `setting.GnomeCustomFavorites` | `SetGnomeCustomFavorites` | `SetGnomeCustomFavorites`: active | deferred: User-specific favorites need profile data. | `desktop-user-03` / resolved |
| `setting.GnomeDefaultFavorites` | `SetGnomeDefaultFavorites` | `SetGnomeDefaultFavorites`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-08` / resolved |
| `setting.GnomeMinimalFavorites` | `SetGnomeMinimalFavorites` | `SetGnomeMinimalFavorites`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-08` / resolved |
| `setting.GnmLocationServiceOff` | `SetGnmLocationServiceOff` | `SetGnmLocationServiceOff`: active | deferred: Review current GNOME setting and scope. | `desktop-user-04` / operable |
| `setting.GnmLocationServiceOn` | `SetGnmLocationServiceOn` | `SetGnmLocationServiceOn`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-09` / operable |
| `setting.GnmAutoProblemRptOff` | `SetGnmAutoProblemRptOff` | `SetGnmAutoProblemRptOff`: active | deferred: Review current GNOME setting and scope. | `desktop-user-04` / operable |
| `setting.GnmAutoProblemRptOn` | `SetGnmAutoProblemRptOn` | `SetGnmAutoProblemRptOn`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-09` / operable |
| `setting.PowerPercentageLow15` | `SetPowerPercentageLow15` | `SetPowerPercentageLow15`: active | deferred: Review current power setting and support. | `desktop-user-04` / resolved |
| `setting.PowerPercentageLow20` | `SetPowerPercentageLow20` | `SetPowerPercentageLow20`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-09` / resolved |
| `setting.BashAliases` | `EnableBashAliases`, `DisableBashAliases` | `EnableBashAliases`: active, `DisableBashAliases`: library only | deferred: User shell configuration must preserve unowned content. | `desktop-user-05` / resolved |
| `setting.AliasLsEza` | `SetAliasLsEza`, `UnsetAliasLsEza` | `SetAliasLsEza`: active, `UnsetAliasLsEza`: library only | deferred: User shell configuration must preserve unowned content. | `desktop-user-05` / resolved |
| `setting.AliasWanIP` | `SetAliasWanIP`, `UnsetAliasWanIP` | `SetAliasWanIP`: active, `UnsetAliasWanIP`: library only | deferred: User shell configuration must preserve unowned content. | `desktop-user-05` / resolved |
| `setting.AliasRideLog` | `SetAliasRideLog`, `UnsetAliasRideLog` | `SetAliasRideLog`: commented, `UnsetAliasRideLog`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `desktop-user-05` / resolved |
| `package.Lynis` | `InstallLynis`, `RemoveLynis` | `InstallLynis`: commented, `RemoveLynis`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `native-rpm-05` / supported |
| `package.ClamAV` | `InstallClamAV`, `RemoveClamAV` | `InstallClamAV`: commented, `RemoveClamAV`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-28` / resolved |
| `package.KeepassXC` | `InstallKeepassXC`, `RemoveKeepassXC` | `InstallKeepassXC`: commented, `RemoveKeepassXC`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-29` / supported |
| `package.Bitwarden` | `InstallBitwarden`, `RemoveBitwarden` | `InstallBitwarden`: commented, `RemoveBitwarden`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-12` / resolved |
| `package.BitwardenAppImage` | `InstallBitwardenAppImage`, `RemoveBitwardenAppImage` | `InstallBitwardenAppImage`: active, `RemoveBitwardenAppImage`: library only | deferred: Review publisher signature and platform artifact. | `publisher-apps-06` / resolved |
| `action.ImportOpenVPNProfiles` | `ImportOpenVPNProfiles` | `ImportOpenVPNProfiles`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior | `system-security-09` / resolved |
| `package.VPNProfiles` | `RemoveVPNProfiles` | `RemoveVPNProfiles`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-20` / resolved |
| `package.ExpressVPNProfiles` | `RemoveExpressVPNProfiles` | `RemoveExpressVPNProfiles`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-21` / resolved |
| `package.ExpressVPN` | `InstallExpressVPN`, `RemoveExpressVPN` | `InstallExpressVPN`: commented, `RemoveExpressVPN`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-10` / resolved |
| `action.StartExpressVPNafterBoot` | `StartExpressVPNafterBoot` | `StartExpressVPNafterBoot`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior | `system-security-11` / resolved |
| `package.ExpressVPNafterBoot` | `RemoveExpressVPNafterBoot` | `RemoveExpressVPNafterBoot`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-22` / resolved |
| `action.CreateExpVPNrandomizer` | `CreateExpVPNrandomizer` | `CreateExpVPNrandomizer`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior | `system-security-12` / resolved |
| `action.ScheduleRandomExpVPNChange` | `ScheduleRandomExpVPNChange` | `ScheduleRandomExpVPNChange`: library only | deferred; classify as explicit operation, private value, CLI utility or retired behavior | `system-security-23` / resolved |
| `package.ScheduleExpVPNChange` | `RemoveScheduleExpVPNChange` | `RemoveScheduleExpVPNChange`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-24` / resolved |
| `package.Cheat` | `InstallCheat`, `RemoveCheat` | `InstallCheat`: active, `RemoveCheat`: library only | deferred: Review current upstream and source. | `publisher-apps-16` / supported |
| `package.UnifyingOnLaptop` | `InstallUnifyingOnLaptop`, `RemoveUnifyingOnLaptop` | `InstallUnifyingOnLaptop`: active, `RemoveUnifyingOnLaptop`: library only | deferred: Hardware-dependent operation. | `publisher-apps-07` / operable |
| `package.Projecteur` | `InstallProjecteur`, `RemoveProjecteur` | `InstallProjecteur`: commented, `RemoveProjecteur`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-13` / operable |
| `package.VMtoolsOnVM` | `InstallVMtoolsOnVM`, `RemoveVMtoolsOnVM` | `InstallVMtoolsOnVM`: active, `RemoveVMtoolsOnVM`: library only | deferred: VM-specific provider after detection test. | `publisher-apps-07` / resolved |
| `package.YubikeyManager` | `InstallYubikeyManager`, `RemoveYubikeyManager` | `InstallYubikeyManager`: active, `RemoveYubikeyManager`: library only | deferred: Hardware-dependent optional package. | `publisher-apps-08` / resolved |
| `package.YubikeyPersTool` | `InstallYubikeyPersTool` | `InstallYubikeyPersTool`: commented | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-14` / resolved |
| `package.Xmind` | `InstallXmind`, `RemoveXmind` | `InstallXmind`: commented, `RemoveXmind`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `publisher-apps-15` / resolved |
| `package.SonosPlayer` | `InstallSonosPlayer`, `RemoveSonosPlayer` | `InstallSonosPlayer`: active, `RemoveSonosPlayer`: library only | deferred: Review publisher source and architecture. | `publisher-apps-09` / resolved |
| `package.VMwareWorkstation` | `InstallVMwareWorkstation`, `RemoveVMwareWorkstation` | `InstallVMwareWorkstation`: commented, `RemoveVMwareWorkstation`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-13` / resolved |
| `action.PatchVMwareModules` | `PatchVMwareModules` | `PatchVMwareModules`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior | `system-security-14` / resolved |
| `action.AddExtraLUKSpasswords` | `AddExtraLUKSpasswords` | `AddExtraLUKSpasswords`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior | `system-security-15` / resolved |
| `action.EncryptUnpartitionedDisks` | `EncryptUnpartitionedDisks` | `EncryptUnpartitionedDisks`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior | `system-security-16` / resolved |
| `action.ReclaimEncryptDWUnmntPrt` | `ReclaimEncryptDWUnmntPrt` | `ReclaimEncryptDWUnmntPrt`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior | `system-security-17` / resolved |
| `package.KeyfileMounts` | `RemoveKeyfileMounts` | `RemoveKeyfileMounts`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery | `system-security-25` / resolved |
| `setting.SSHreboot` | `EnableSSHreboot`, `DisableSSHreboot` | `EnableSSHreboot`: commented, `DisableSSHreboot`: library only | deferred; inspect exact prior value, ownership, applicability and restore | `system-security-18` / resolved |

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
| `action.UpdateFedora` | `UpdateFedora` | complete, plexserver, streambox | — | deferred generic server baseline; split package/update/timer behavior and record recovery limits | `generic-server-01` / resolved |
| `package.Required` | `InstallRequired` | complete, plexserver, streambox | — | deferred generic server baseline; split package/update/timer behavior and record recovery limits | `generic-server-02` / resolved |
| `package.AutoUpdate` | `InstallAutoUpdate` | complete, plexserver, streambox | — | deferred generic server baseline; split package/update/timer behavior and record recovery limits | `generic-server-03` / resolved |
| `action.ViewIPaddress` | `ViewIPaddress` | complete, plexserver, streambox | — | retire as install outcome; expose inspection through `status` if useful | `generic-server-04` / resolved |
| `setting.Hostname` | `SetHostname` | complete, plexserver, streambox | — | private overlay for host values or key material; extract generic behavior only after ownership review | `generic-server-05` / resolved |
| `package.Docker` | `InstallDocker` | complete | — | deferred optional server operation; verify current package/source, state and recovery | `generic-server-06` / resolved |
| `package.Tailscale` | `InstallTailscale` | — | — | deferred optional server operation; verify current package/source, state and recovery | `generic-server-14` / resolved |
| `package.Glances` | `InstallGlances` | complete | — | deferred optional server operation; verify current package/source, state and recovery | `generic-server-07` / resolved |
| `package.PythonPip` | `InstallPythonPip` | — | complete | replace global Python installation with isolated, pinned per-tool environment | `generic-server-12` / supported |
| `package.Selenium` | `InstallSelenium` | — | complete | replace global Python installation with isolated, pinned per-tool environment | `generic-server-12` / resolved |
| `setting.NoRootLogin` | `SetNoRootLogin` | complete | — | deferred SSH policy setting; preserve existing file content and test exact restore | `generic-server-08` / resolved |
| `action.GenerateSSHkeysRSA` | `GenerateSSHkeysRSA` | — | complete | private overlay for host values or key material; extract generic behavior only after ownership review | `generic-server-13` / resolved |
| `package.ExpressVPN` | `InstallExpressVPN` | complete, streambox | plexserver | deferred opt-in VPN profile; keep provider account and host routing private | `generic-server-09` / resolved |
| `action.CreateVPNrandomizer` | `CreateVPNrandomizer` | complete, streambox | plexserver | deferred opt-in VPN profile; keep provider account and host routing private | `generic-server-10` / resolved |
| `setting.VPNRandomizerPersistent` | `SetVPNRandomizerPersistent` | complete, streambox | plexserver | deferred opt-in VPN profile; keep provider account and host routing private | `generic-server-11` / resolved |
| `package.qBittorrentServer` | `InstallqBittorrentServer` | complete, streambox | plexserver | deferred optional server operation; verify current package/source, state and recovery | `generic-server-15` / supported |
| `package.PlexServer` | `InstallPlexServer` | complete, plexserver | streambox | deferred optional server operation; verify current package/source, state and recovery | `generic-server-16` / resolved |
| `package.PlexAutoUpdate` | `InstallPlexAutoUpdate` | complete, plexserver | streambox | deferred optional server operation; verify current package/source, state and recovery | `generic-server-17` / resolved |
| `package.AMP` | `InstallAMP` | complete | — | deferred optional server operation; verify current package/source, state and recovery | `generic-server-18` / resolved |
| `package.Ferium` | `InstallFerium` | — | — | deferred optional server operation; verify current package/source, state and recovery | `generic-server-19` / resolved |
| `package.MinecraftServer` | `InstallMinecraftServer` | complete | plexserver, streambox | deferred optional server operation; verify current package/source, state and recovery | `generic-server-20` / resolved |

`RequireAdmin`, `PressAnyKeyToContinue` and `Restart` appear as active server preset
selectors but are controller flow, not server-library outcomes. The commented
`GenerateSSHkeys` selector is not defined in the server library; it must not silently
resolve to `GenerateSSHkeysRSA` without a migration decision.

## Current retirement and replacement decisions

These dispositions come from `migration/outcomes.json` and supersede the
initial assessment above. The ledger records each reason and review trigger.

| Source outcome | Current disposition | Batch |
| --- | --- | --- |
| `workstation:package.Required` | `replace` | `provider-foundation-01` |
| `workstation:package.DNFutils` | `replace` | `provider-foundation-03` |
| `workstation:package.EzaGitHub` | `replace` | `provider-foundation-08` |
| `workstation:package.VersionLock` | `replace` | `provider-foundation-04` |
| `workstation:package.NautilusHash` | `retire` | `native-rpm-03` |
| `workstation:package.NautilusImageTools` | `retire` | `native-rpm-03` |
| `workstation:package.Flatpak` | `replace` | `provider-foundation-11` |
| `workstation:package.VMFStools` | `retire` | `forensic-isolated-01` |
| `workstation:package.Volatility` | `retire` | `forensic-isolated-02` |
| `workstation:package.Macvendor` | `replace` | `forensic-isolated-03` |
| `workstation:package.Dumpzilla` | `retire` | `forensic-isolated-03` |
| `workstation:package.PackagingTools` | `replace` | `provider-foundation-03` |
| `workstation:package.MicrosoftTeams` | `retire` | `publisher-apps-09` |
| `workstation:package.AtomEditor` | `retire` | `publisher-apps-10` |
| `workstation:setting.AtomTelemetry` | `retire` | `resolution-review-01` |
| `workstation:package.AtomPlugins` | `retire` | `publisher-apps-10` |
| `workstation:action.CheckFirefoxAddons` | `replace` | `desktop-user-05` |
| `workstation:package.FirefoxAddons` | `replace` | `publisher-apps-04` |
| `workstation:action.FinalizeFirefoxAddonRemoval` | `replace` | `desktop-user-06` |
| `workstation:setting.AliasRideLog` | `retire` | `desktop-user-05` |
| `workstation:package.YubikeyManager` | `replace` | `publisher-apps-08` |
| `workstation:package.YubikeyPersTool` | `replace` | `publisher-apps-14` |
| `workstation:package.SonosPlayer` | `retire` | `publisher-apps-09` |
| `workstation:package.VMwareWorkstation` | `retire` | `system-security-13` |
| `server:action.ViewIPaddress` | `retire` | `generic-server-04` |

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
