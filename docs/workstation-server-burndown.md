# Workstation and server outcome burndown

This queue accounts for **every named function** in the workstation and server libraries,
including functions absent from active presets. Install/remove and analogous state pairs
share an outcome row; each exact function name remains visible. A `deferred` row is
inventory, not an executable operation or acceptance claim.

Workstation source: `lib-fedora.sh` at Fedora commit `43ba467`; 289 functions,
166 grouped outcomes, 92 outcomes with no active default selector.
Function coverage: 74 active, 69 commented-only, 146 library-only.
Default preset: 76 active selectors and 71 commented selectors
that name a defined function or controller action. The [active migration ledger](MIGRATION-PLAN.md)
provides the decisions for all active selectors.

Server source: `operations/provisioning/ride/lib-fedora-server.sh` at `network-devices` commit
`fccc70f6825d13f899ac6fd4e72a1af6360be076`; 28 functions, 28 outcomes,
5 outcomes absent from all active server presets. Its three preset inventories
are stored as names only in `migration/server-inventory.json`; no host values were copied.
Function coverage: 23 active in a server preset, 3 commented-only, 2 library-only.

## Workstation library

| Outcome key | Exact source functions | Selector coverage | v3 disposition / next review |
| --- | --- | --- | --- |
| `action.SetupUserDefaultDirs` | `SetupUserDefaultDirs` | `SetupUserDefaultDirs`: active | deferred: Review directory ownership and user scope. |
| `setting.Hostname` | `SetHostname` | `SetHostname`: active | deferred: Host-specific value belongs in private profile. |
| `setting.FastDNF` | `EnableFastDNF`, `DisableFastDNF` | `EnableFastDNF`: active, `DisableFastDNF`: library only | replaced: DNF5 defaults need current evidence; no legacy config edit. |
| `action.UpdateFedora` | `UpdateFedora` | `UpdateFedora`: active | deferred: Add explicit non-reversible system update operation after VM acceptance. |
| `package.Required` | `InstallRequired` | `InstallRequired`: active | replaced: Smaller package.less and package.openssh-clients in default; review remaining list. |
| `package.ShellTools` | `InstallShellTools`, `RemoveShellTools` | `InstallShellTools`: active, `RemoveShellTools`: library only | deferred: Split into specific repository packages. |
| `package.RPMfusionRepos` | `InstallRPMfusionRepos`, `RemoveRPMfusionRepos` | `InstallRPMfusionRepos`: active, `RemoveRPMfusionRepos`: library only | deferred: External repository enablement needs opt-in and trust review. |
| `package.KernelTools` | `InstallKernelTools`, `RemoveKernelTools` | `InstallKernelTools`: active, `RemoveKernelTools`: library only | deferred: Kernel-dependent package group requires target checks. |
| `package.DNFutils` | `InstallDNFutils`, `RemoveDNFutils` | `InstallDNFutils`: active, `RemoveDNFutils`: library only | replaced: Review current DNF5 commands and plugins. |
| `package.Eza` | `InstallEza`, `RemoveEza` | `InstallEza`: library only, `RemoveEza`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.EzaGitHub` | `InstallEzaGitHub` | `InstallEzaGitHub`: active | replaced: Prefer Fedora repository package after verification. |
| `package.VersionLock` | `InstallVersionLock`, `RemoveVersionLock` | `InstallVersionLock`: commented, `RemoveVersionLock`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.NautilusHash` | `InstallNautilusHash`, `RemoveNautilusHash` | `InstallNautilusHash`: commented, `RemoveNautilusHash`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.NautilusImageTools` | `InstallNautilusImageTools`, `RemoveNautilusImageTools` | `InstallNautilusImageTools`: commented, `RemoveNautilusImageTools`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Flatpak` | `InstallFlatpak`, `RemoveFlatpak` | `InstallFlatpak`: commented, `RemoveFlatpak`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Flathub` | `InstallFlathub`, `RemoveFlathub` | `InstallFlathub`: active, `RemoveFlathub`: library only | deferred: External Flatpak remote remains opt-in. |
| `package.AppImageLauncher` | `InstallAppImageLauncher`, `RemoveAppImageLauncher` | `InstallAppImageLauncher`: active, `RemoveAppImageLauncher`: library only | deferred: Review maintained source and current desktop integration. |
| `package.Snap` | `InstallSnap`, `RemoveSnap` | `InstallSnap`: commented, `RemoveSnap`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Galleta` | `InstallGalleta`, `RemoveGalleta` | `InstallGalleta`: commented, `RemoveGalleta`: library only | deferred incomplete legacy stub; source and current package need review |
| `package.Plaso` | `InstallPlaso`, `RemovePlaso` | `InstallPlaso`: commented, `RemovePlaso`: library only | deferred candidate; opt-in COPR and removal need VM evidence |
| `package.Autopsy` | `InstallAutopsy`, `RemoveAutopsy` | `InstallAutopsy`: commented, `RemoveAutopsy`: library only | deferred candidate; upstream Linux setup and removal need VM evidence |
| `package.Xplico` | `InstallXplico`, `RemoveXplico` | `InstallXplico`: commented, `RemoveXplico`: library only | deferred incomplete legacy stub; source and current package need review |
| `package.VMFStools` | `InstallVMFStools`, `RemoveVMFStools` | `InstallVMFStools`: active, `RemoveVMFStools`: library only | deferred: Legacy active entry is incomplete; no executable v3 handler. |
| `package.Volatility` | `InstallVolatility`, `RemoveVolatility` | `InstallVolatility`: commented, `RemoveVolatility`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Volatility3` | `InstallVolatility3`, `RemoveVolatility3` | `InstallVolatility3`: commented, `RemoveVolatility3`: library only | implemented candidate `package.volatility3`; isolated pinned core, VM acceptance pending |
| `package.VeraCrypt` | `InstallVeraCrypt`, `UninstallVeraCrypt` | `InstallVeraCrypt`: active, `UninstallVeraCrypt`: library only | deferred: Review publisher verification and licensing. |
| `package.BulkExtractor` | `InstallBulkExtractor`, `RemoveBulkExtractor` | `InstallBulkExtractor`: commented, `RemoveBulkExtractor`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.EmailHeaderAnlzr` | `InstallEmailHeaderAnlzr`, `RemoveEmailHeaderAnlzr` | `InstallEmailHeaderAnlzr`: commented, `RemoveEmailHeaderAnlzr`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.LibEWF` | `InstallLibEWF`, `RemoveLibEWF` | `InstallLibEWF`: active, `RemoveLibEWF`: library only | replaced: package.ewftools covers EWF utilities; verify library intent separately. |
| `package.SecurityLab` | `InstallSecurityLab`, `RemoveSecurityLab` | `InstallSecurityLab`: commented, `RemoveSecurityLab`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Dc3dd` | `InstallDc3dd`, `RemoveDc3dd` | `InstallDc3dd`: commented, `RemoveDc3dd`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Exif` | `InstallExif`, `RemoveExif` | `InstallExif`: active, `RemoveExif`: library only | deferred: Review product identity and official package. |
| `package.Binwalk` | `InstallBinwalk`, `RemoveBinwalk` | `InstallBinwalk`: commented, `RemoveBinwalk`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Md5deep` | `InstallMd5deep`, `RemoveMd5deep` | `InstallMd5deep`: active, `RemoveMd5deep`: library only | deferred: Review current package and forensic use case. |
| `package.Libpst` | `InstallLibpst`, `RemoveLibpst` | `InstallLibpst`: library only, `RemoveLibpst`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Macvendor` | `InstallMacvendor`, `RemoveMacvendor` | `InstallMacvendor`: library only, `RemoveMacvendor`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.ExifTool` | `InstallExifTool`, `RemoveExifTool` | `InstallExifTool`: active, `RemoveExifTool`: library only | deferred: Current GitHub source build needs provenance and verification redesign. |
| `package.ASN` | `InstallASN`, `RemoveASN` | `InstallASN`: active, `RemoveASN`: library only | deferred: Current upstream acquisition needs review. |
| `package.UnfURL` | `InstallUnfURL`, `RemoveUnfURL` | `InstallUnfURL`: active, `RemoveUnfURL`: library only | deferred: Current Python package method needs isolation. |
| `package.CyberChef` | `InstallCyberChef`, `RemoveCyberChef` | `InstallCyberChef`: active, `RemoveCyberChef`: library only | deferred: Align product facts with Windows catalog; platform package remains local. |
| `package.Chepy` | `InstallChepy`, `RemoveChepy` | `InstallChepy`: active, `RemoveChepy`: library only | deferred: Python tooling needs isolated environment and pins. |
| `package.Dumpzilla` | `InstallDumpzilla`, `RemoveDumpzilla` | `InstallDumpzilla`: commented, `RemoveDumpzilla`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.NetworkMiner` | `InstallNetworkMiner`, `RemoveNetworkMiner` | `InstallNetworkMiner`: active, `RemoveNetworkMiner`: library only | deferred: Align product identity with Windows; review Linux packaging. |
| `package.Pwgen` | `InstallPwgen`, `RemovePwgen` | `InstallPwgen`: active, `RemovePwgen`: library only | deferred: Candidate native repository package. |
| `package.Htop` | `InstallHtop`, `RemoveHtop` | `InstallHtop`: active, `RemoveHtop`: library only | deferred: Candidate native repository package. |
| `package.Bat` | `InstallBat`, `RemoveBat` | `InstallBat`: active, `RemoveBat`: library only | deferred: Candidate native repository package. |
| `package.Ncdu` | `InstallNcdu`, `RemoveNcdu` | `InstallNcdu`: active, `RemoveNcdu`: library only | deferred: Candidate native repository package. |
| `package.Ripgrep` | `InstallRipgrep`, `RemoveRipgrep` | `InstallRipgrep`: active, `RemoveRipgrep`: library only | deferred: Candidate native repository package. |
| `package.Fd` | `InstallFd`, `RemoveFd` | `InstallFd`: active, `RemoveFd`: library only | deferred: Candidate native repository package. |
| `package.Docker` | `InstallDocker`, `RemoveDocker` | `InstallDocker`: active, `RemoveDocker`: library only | deferred: Generic server role only after provider and repository review. |
| `package.PythonPip` | `InstallPythonPip`, `RemovePythonPip` | `InstallPythonPip`: active, `RemovePythonPip`: library only | replaced: Use per-operation isolated Python installs, not global pip. |
| `package.PackagingTools` | `InstallPackagingTools`, `RemovePackagingTools` | `InstallPackagingTools`: active, `RemovePackagingTools`: library only | deferred: Split package list by use case. |
| `package.BasicEditors` | `InstallBasicEditors`, `RemoveBasicEditors` | `InstallBasicEditors`: active, `RemoveBasicEditors`: library only | deferred: Candidate native repository packages. |
| `package.CommanderFileMgrs` | `InstallCommanderFileMgrs`, `RemoveCommanderFileMgrs` | `InstallCommanderFileMgrs`: commented, `RemoveCommanderFileMgrs`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Terminator` | `InstallTerminator`, `RemoveTerminator` | `InstallTerminator`: active, `RemoveTerminator`: library only | deferred: Optional desktop profile only. |
| `package.Alien` | `InstallAlien`, `RemoveAlien` | `InstallAlien`: active, `RemoveAlien`: library only | deferred: Review relevance and support. |
| `package.SmartMonTools` | `InstallSmartMonTools`, `RemoveSmartMonTools` | `InstallSmartMonTools`: active, `RemoveSmartMonTools`: library only | deferred: Optional system tools profile. |
| `package.Qbittorrent` | `InstallQbittorrent`, `RemoveQbittorrent` | `InstallQbittorrent`: commented, `RemoveQbittorrent`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.PowerShell` | `InstallPowerShell`, `RemovePowerShell` | `InstallPowerShell`: commented, `RemovePowerShell`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.MicrosoftTeams` | `InstallMicrosoftTeams`, `RemoveMicrosoftTeams` | `InstallMicrosoftTeams`: commented, `RemoveMicrosoftTeams`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.WoeUSB` | `InstallWoeUSB`, `RemoveWoeUSB` | `InstallWoeUSB`: commented, `RemoveWoeUSB`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.BalenaEtcher` | `InstallBalenaEtcher`, `RemoveBalenaEtcher` | `InstallBalenaEtcher`: commented, `RemoveBalenaEtcher`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.VisualStudioCode` | `InstallVisualStudioCode`, `RemoveVisualStudioCode` | `InstallVisualStudioCode`: active, `RemoveVisualStudioCode`: library only | deferred: Align product facts with Windows; Fedora source stays local. |
| `package.ArduinoIDE` | `InstallArduinoIDE`, `RemoveArduinoIDE` | `InstallArduinoIDE`: commented, `RemoveArduinoIDE`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.AtomEditor` | `InstallAtomEditor`, `RemoveAtomEditor` | `InstallAtomEditor`: commented, `RemoveAtomEditor`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `setting.AtomTelemetry` | `DisableAtomTelemetry`, `EnableAtomTelemetry` | `DisableAtomTelemetry`: commented, `EnableAtomTelemetry`: library only | deferred; inspect exact prior value, ownership, applicability and restore |
| `package.AtomPlugins` | `InstallAtomPlugins`, `RemoveAtomPlugins` | `InstallAtomPlugins`: commented, `RemoveAtomPlugins`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.PyhtonAutopep8` | `InstallPyhtonAutopep8`, `RemovePyhtonAutopep8` | `InstallPyhtonAutopep8`: commented, `RemovePyhtonAutopep8`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Hexchat` | `InstallHexchat`, `RemoveHexchat` | `InstallHexchat`: active, `RemoveHexchat`: library only | deferred: Review upstream maintenance before reintroduction. |
| `package.Discord` | `InstallDiscord`, `RemoveDiscord` | `InstallDiscord`: commented, `RemoveDiscord`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Pidgin` | `InstallPidgin`, `RemovePidgin` | `InstallPidgin`: commented, `RemovePidgin`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Thunderbird` | `InstallThunderbird`, `RemoveThunderbird` | `InstallThunderbird`: commented, `RemoveThunderbird`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `setting.MulticastDNS` | `DisableMulticastDNS`, `EnableMulticastDNS` | `DisableMulticastDNS`: commented, `EnableMulticastDNS`: library only | deferred; inspect exact prior value, ownership, applicability and restore |
| `package.NetworkTools` | `InstallNetworkTools`, `RemoveNetworkTools` | `InstallNetworkTools`: active, `RemoveNetworkTools`: library only | deferred: Split broad network bundle into focused packages. |
| `package.NetCommsTools` | `InstallNetCommsTools`, `RemoveNetCommsTools` | `InstallNetCommsTools`: active, `RemoveNetCommsTools`: library only | deferred: Split broad communications bundle. |
| `package.NetMgrL2TP` | `InstallNetMgrL2TP`, `RemoveNetMgrL2TP` | `InstallNetMgrL2TP`: commented, `RemoveNetMgrL2TP`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.NetMgrLibreswan` | `InstallNetMgrLibreswan`, `RemoveNetMgrLibreswan` | `InstallNetMgrLibreswan`: active, `RemoveNetMgrLibreswan`: library only | deferred: Optional VPN role. |
| `package.Wireguard` | `InstallWireguard`, `RemoveWireguard` | `InstallWireguard`: library only, `RemoveWireguard`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.OpenconnectVPN` | `InstallOpenconnectVPN` | `InstallOpenconnectVPN`: commented | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.SpeedtestCLI` | `InstallSpeedtestCLI`, `RemoveSpeedtestCLI` | `InstallSpeedtestCLI`: active, `RemoveSpeedtestCLI`: library only | deferred: Review current upstream and source. |
| `package.Flameshot` | `InstallFlameshot`, `RemoveFlameshot` | `InstallFlameshot`: commented, `RemoveFlameshot`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Dia` | `InstallDia`, `RemoveDia` | `InstallDia`: commented, `RemoveDia`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Wine` | `InstallWine`, `RemoveWine` | `InstallWine`: commented, `RemoveWine`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Joplin` | `InstallJoplin`, `RemoveJoplin` | `InstallJoplin`: commented, `RemoveJoplin`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.TecmintMonitorSh` | `InstallTecmintMonitorSh`, `RemoveTecmintMonitorSh` | `InstallTecmintMonitorSh`: active, `RemoveTecmintMonitorSh`: library only | retired: Default profile must not fetch and execute remote scripts. |
| `package.GnomeExtInstaller` | `InstallGnomeExtInstaller`, `RemoveGnomeExtInstaller` | `InstallGnomeExtInstaller`: active, `RemoveGnomeExtInstaller`: library only | deferred: Review current GNOME extension lifecycle. |
| `package.Brave` | `InstallBrave`, `RemoveBrave` | `InstallBrave`: active, `RemoveBrave`: library only | deferred: Third-party repository and license review. |
| `package.Vivaldi` | `InstallVivaldi`, `RemoveVivaldi` | `InstallVivaldi`: commented, `RemoveVivaldi`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Chromium` | `InstallChromium`, `RemoveChromium` | `InstallChromium`: active, `RemoveChromium`: library only | deferred: Candidate distro repository package. |
| `package.Chrome` | `InstallChrome`, `RemoveChrome` | `InstallChrome`: commented, `RemoveChrome`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `setting.ChromePreferences` | `SetChromePreferences`, `UnsetChromePreferences` | `SetChromePreferences`: commented, `UnsetChromePreferences`: library only | deferred; inspect exact prior value, ownership, applicability and restore |
| `setting.FirefoxPreferences` | `SetFirefoxPreferences`, `UnsetFirefoxPreferences` | `SetFirefoxPreferences`: active, `UnsetFirefoxPreferences`: library only | replaced: Review settings against current Firefox policy; avoid legacy file overwrite. |
| `action.CheckFirefoxAddons` | `CheckFirefoxAddons` | `CheckFirefoxAddons`: library only | deferred v3 integration; existing policy helper remains tested separately |
| `package.FirefoxAddons` | `InstallFirefoxAddons`, `RemoveFirefoxAddons` | `InstallFirefoxAddons`: active, `RemoveFirefoxAddons`: library only | deferred: Keep existing verified policy helper; integrate with v3 lifecycle later. |
| `action.FinalizeFirefoxAddonRemoval` | `FinalizeFirefoxAddonRemoval` | `FinalizeFirefoxAddonRemoval`: library only | deferred v3 integration; restart-dependent policy lifecycle needs journal ownership |
| `package.Opera` | `InstallOpera`, `RemoveOpera` | `InstallOpera`: commented, `RemoveOpera`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Edge` | `InstallEdge`, `RemoveEdge` | `InstallEdge`: commented, `RemoveEdge`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Codecs` | `InstallCodecs`, `RemoveCodecs` | `InstallCodecs`: commented, `RemoveCodecs`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.SpotifyClient` | `InstallSpotifyClient`, `RemoveSpotifyClient` | `InstallSpotifyClient`: commented, `RemoveSpotifyClient`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.VLCPlayer` | `InstallVLCPlayer`, `RemoveVLCPlayer` | `InstallVLCPlayer`: commented, `RemoveVLCPlayer`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.ClementinePlayer` | `InstallClementinePlayer`, `RemoveClementinePlayer` | `InstallClementinePlayer`: commented, `RemoveClementinePlayer`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.PulseAudioEq` | `InstallPulseAudioEq`, `RemovePulseAudioEq` | `InstallPulseAudioEq`: commented, `RemovePulseAudioEq`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.YouTubeDownloader` | `InstallYouTubeDownloader`, `RemoveYouTubeDownloader` | `InstallYouTubeDownloader`: active, `RemoveYouTubeDownloader`: library only | replaced: Review maintained yt-dlp packaging instead of legacy youtube-dl. |
| `package.GIMP` | `InstallGIMP`, `RemoveGIMP` | `InstallGIMP`: commented, `RemoveGIMP`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.HandBrake` | `InstallHandBrake`, `RemoveHandBrake` | `InstallHandBrake`: commented, `RemoveHandBrake`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.GnomeTools` | `InstallGnomeTools`, `RemoveGnomeTools` | `InstallGnomeTools`: active, `RemoveGnomeTools`: library only | deferred: Split GNOME package bundle. |
| `package.SystemMonitor` | `InstallSystemMonitor`, `RemoveSystemMonitor` | `InstallSystemMonitor`: active, `RemoveSystemMonitor`: library only | deferred: Review current GNOME extension support. |
| `package.GnomeExtensions` | `InstallGnomeExtensions`, `RemoveGnomeExtensions` | `InstallGnomeExtensions`: active, `RemoveGnomeExtensions`: library only | deferred: Review current GNOME extension IDs and API. |
| `setting.ScreenSaver` | `EnableScreenSaver` | `EnableScreenSaver`: active | retired: Conflicts with DisableScreensaver in the same legacy preset; review one desired state. |
| `setting.Screensaver` | `DisableScreensaver` | `DisableScreensaver`: active | retired: Conflicts with EnableScreenSaver in the same legacy preset; review a single desired state later. |
| `setting.DateInTaskbar` | `ShowDateInTaskbar`, `HideDateInTaskbar` | `ShowDateInTaskbar`: active, `HideDateInTaskbar`: library only | deferred: Setting handler needs baseline and restore. |
| `setting.WeekNumbersInTaskbar` | `ShowWeekNumbersInTaskbar`, `HideWeekNumbersInTaskbar` | `ShowWeekNumbersInTaskbar`: active, `HideWeekNumbersInTaskbar`: library only | deferred: Setting handler needs baseline and restore. |
| `setting.WindowCtlMinMaxClose` | `SetWindowCtlMinMaxClose` | `SetWindowCtlMinMaxClose`: active | deferred: Setting handler needs baseline and restore. |
| `setting.WindowCtlAppmenuClose` | `SetWindowCtlAppmenuClose` | `SetWindowCtlAppmenuClose`: library only | deferred; inspect exact prior value, ownership, applicability and restore |
| `setting.WindowCtlLeftClsMinMax` | `SetWindowCtlLeftClsMinMax` | `SetWindowCtlLeftClsMinMax`: library only | deferred; inspect exact prior value, ownership, applicability and restore |
| `setting.MiddleButtonPaste` | `EnableMiddleButtonPaste`, `DisableMiddleButtonPaste` | `EnableMiddleButtonPaste`: library only, `DisableMiddleButtonPaste`: active | deferred: Setting handler needs baseline and restore. |
| `setting.GnomeRegionDaDK` | `SetGnomeRegionDaDK` | `SetGnomeRegionDaDK`: active | deferred: User locale must be explicit profile data. |
| `package.GnomeRegion` | `RemoveGnomeRegion` | `RemoveGnomeRegion`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `setting.ScreensaverSlp10Lgn5` | `SetScreensaverSlp10Lgn5` | `SetScreensaverSlp10Lgn5`: active | deferred: Resolve conflict with other screensaver operations. |
| `setting.ScreensaverSlp15Lgn5` | `SetScreensaverSlp15Lgn5` | `SetScreensaverSlp15Lgn5`: library only | deferred; inspect exact prior value, ownership, applicability and restore |
| `setting.CustomKeyboardShortcut` | `SetCustomKeyboardShortcut` | `SetCustomKeyboardShortcut`: active | deferred: User-owned shortcut state needs exact restore. |
| `setting.VMKeyboardShortcut` | `SetVMKeyboardShortcut` | `SetVMKeyboardShortcut`: library only | deferred; inspect exact prior value, ownership, applicability and restore |
| `package.CustomKbrdShortcut` | `RemoveCustomKbrdShortcut` | `RemoveCustomKbrdShortcut`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `setting.GnomeCustomFavorites` | `SetGnomeCustomFavorites` | `SetGnomeCustomFavorites`: active | deferred: User-specific favorites need profile data. |
| `setting.GnomeDefaultFavorites` | `SetGnomeDefaultFavorites` | `SetGnomeDefaultFavorites`: library only | deferred; inspect exact prior value, ownership, applicability and restore |
| `setting.GnomeMinimalFavorites` | `SetGnomeMinimalFavorites` | `SetGnomeMinimalFavorites`: library only | deferred; inspect exact prior value, ownership, applicability and restore |
| `setting.GnmLocationServiceOff` | `SetGnmLocationServiceOff` | `SetGnmLocationServiceOff`: active | deferred: Review current GNOME setting and scope. |
| `setting.GnmLocationServiceOn` | `SetGnmLocationServiceOn` | `SetGnmLocationServiceOn`: library only | deferred; inspect exact prior value, ownership, applicability and restore |
| `setting.GnmAutoProblemRptOff` | `SetGnmAutoProblemRptOff` | `SetGnmAutoProblemRptOff`: active | deferred: Review current GNOME setting and scope. |
| `setting.GnmAutoProblemRptOn` | `SetGnmAutoProblemRptOn` | `SetGnmAutoProblemRptOn`: library only | deferred; inspect exact prior value, ownership, applicability and restore |
| `setting.PowerPercentageLow15` | `SetPowerPercentageLow15` | `SetPowerPercentageLow15`: active | deferred: Review current power setting and support. |
| `setting.PowerPercentageLow20` | `SetPowerPercentageLow20` | `SetPowerPercentageLow20`: library only | deferred; inspect exact prior value, ownership, applicability and restore |
| `setting.BashAliases` | `EnableBashAliases`, `DisableBashAliases` | `EnableBashAliases`: active, `DisableBashAliases`: library only | deferred: User shell configuration must preserve unowned content. |
| `setting.AliasLsEza` | `SetAliasLsEza`, `UnsetAliasLsEza` | `SetAliasLsEza`: active, `UnsetAliasLsEza`: library only | deferred: User shell configuration must preserve unowned content. |
| `setting.AliasWanIP` | `SetAliasWanIP`, `UnsetAliasWanIP` | `SetAliasWanIP`: active, `UnsetAliasWanIP`: library only | deferred: User shell configuration must preserve unowned content. |
| `setting.AliasRideLog` | `SetAliasRideLog`, `UnsetAliasRideLog` | `SetAliasRideLog`: commented, `UnsetAliasRideLog`: library only | deferred; inspect exact prior value, ownership, applicability and restore |
| `package.Lynis` | `InstallLynis`, `RemoveLynis` | `InstallLynis`: commented, `RemoveLynis`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.ClamAV` | `InstallClamAV`, `RemoveClamAV` | `InstallClamAV`: commented, `RemoveClamAV`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.KeepassXC` | `InstallKeepassXC`, `RemoveKeepassXC` | `InstallKeepassXC`: commented, `RemoveKeepassXC`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Bitwarden` | `InstallBitwarden`, `RemoveBitwarden` | `InstallBitwarden`: commented, `RemoveBitwarden`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.BitwardenAppImage` | `InstallBitwardenAppImage`, `RemoveBitwardenAppImage` | `InstallBitwardenAppImage`: active, `RemoveBitwardenAppImage`: library only | deferred: Review publisher signature and platform artifact. |
| `action.ImportOpenVPNProfiles` | `ImportOpenVPNProfiles` | `ImportOpenVPNProfiles`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior |
| `package.VPNProfiles` | `RemoveVPNProfiles` | `RemoveVPNProfiles`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.ExpressVPNProfiles` | `RemoveExpressVPNProfiles` | `RemoveExpressVPNProfiles`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.ExpressVPN` | `InstallExpressVPN`, `RemoveExpressVPN` | `InstallExpressVPN`: commented, `RemoveExpressVPN`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `action.StartExpressVPNafterBoot` | `StartExpressVPNafterBoot` | `StartExpressVPNafterBoot`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior |
| `package.ExpressVPNafterBoot` | `RemoveExpressVPNafterBoot` | `RemoveExpressVPNafterBoot`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `action.CreateExpVPNrandomizer` | `CreateExpVPNrandomizer` | `CreateExpVPNrandomizer`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior |
| `action.ScheduleRandomExpVPNChange` | `ScheduleRandomExpVPNChange` | `ScheduleRandomExpVPNChange`: library only | deferred; classify as explicit operation, private value, CLI utility or retired behavior |
| `package.ScheduleExpVPNChange` | `RemoveScheduleExpVPNChange` | `RemoveScheduleExpVPNChange`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Cheat` | `InstallCheat`, `RemoveCheat` | `InstallCheat`: active, `RemoveCheat`: library only | deferred: Review current upstream and source. |
| `package.UnifyingOnLaptop` | `InstallUnifyingOnLaptop`, `RemoveUnifyingOnLaptop` | `InstallUnifyingOnLaptop`: active, `RemoveUnifyingOnLaptop`: library only | deferred: Hardware-dependent operation. |
| `package.Projecteur` | `InstallProjecteur`, `RemoveProjecteur` | `InstallProjecteur`: commented, `RemoveProjecteur`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.VMtoolsOnVM` | `InstallVMtoolsOnVM`, `RemoveVMtoolsOnVM` | `InstallVMtoolsOnVM`: active, `RemoveVMtoolsOnVM`: library only | deferred: VM-specific provider after detection test. |
| `package.YubikeyManager` | `InstallYubikeyManager`, `RemoveYubikeyManager` | `InstallYubikeyManager`: active, `RemoveYubikeyManager`: library only | deferred: Hardware-dependent optional package. |
| `package.YubikeyPersTool` | `InstallYubikeyPersTool` | `InstallYubikeyPersTool`: commented | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.Xmind` | `InstallXmind`, `RemoveXmind` | `InstallXmind`: commented, `RemoveXmind`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `package.SonosPlayer` | `InstallSonosPlayer`, `RemoveSonosPlayer` | `InstallSonosPlayer`: active, `RemoveSonosPlayer`: library only | deferred: Review publisher source and architecture. |
| `package.VMwareWorkstation` | `InstallVMwareWorkstation`, `RemoveVMwareWorkstation` | `InstallVMwareWorkstation`: commented, `RemoveVMwareWorkstation`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `action.PatchVMwareModules` | `PatchVMwareModules` | `PatchVMwareModules`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior |
| `package.CitrixClient` | `InstallCitrixClient`, `RemoveCitrixClient` | `InstallCitrixClient`: commented, `RemoveCitrixClient`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `action.AddExtraLUKSpasswords` | `AddExtraLUKSpasswords` | `AddExtraLUKSpasswords`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior |
| `action.EncryptUnpartitionedDisks` | `EncryptUnpartitionedDisks` | `EncryptUnpartitionedDisks`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior |
| `action.ReclaimEncryptDWUnmntPrt` | `ReclaimEncryptDWUnmntPrt` | `ReclaimEncryptDWUnmntPrt`: commented | deferred; classify as explicit operation, private value, CLI utility or retired behavior |
| `package.KeyfileMounts` | `RemoveKeyfileMounts` | `RemoveKeyfileMounts`: library only | deferred; inspect current package or publisher, detection, verification, removal and recovery |
| `setting.SSHreboot` | `EnableSSHreboot`, `DisableSSHreboot` | `EnableSSHreboot`: commented, `DisableSSHreboot`: library only | deferred; inspect exact prior value, ownership, applicability and restore |

`PressAnyKeyToContinue` and `Restart` are active default selectors but live outside
`lib-fedora.sh`; both are retired as install outcomes in the active ledger.
`RequireAdmin` is a commented controller selector, also outside the library.

## Server library and presets

| Outcome key | Exact source functions | Active presets | Commented presets | v3 disposition / next review |
| --- | --- | --- | --- | --- |
| `action.UpdateFedora` | `UpdateFedora` | complete, plexserver, streambox | — | deferred generic server baseline; split package/update/timer behavior and record recovery limits |
| `package.Required` | `InstallRequired` | complete, plexserver, streambox | — | deferred generic server baseline; split package/update/timer behavior and record recovery limits |
| `package.AutoUpdate` | `InstallAutoUpdate` | complete, plexserver, streambox | — | deferred generic server baseline; split package/update/timer behavior and record recovery limits |
| `action.ViewIPaddress` | `ViewIPaddress` | complete, plexserver, streambox | — | retire as install outcome; expose inspection through `status` if useful |
| `setting.Hostname` | `SetHostname` | complete, plexserver, streambox | — | private overlay for host values or key material; extract generic behavior only after ownership review |
| `package.Docker` | `InstallDocker` | complete | — | deferred optional server operation; verify current package/source, state and recovery |
| `package.Tailscale` | `InstallTailscale` | — | — | deferred optional server operation; verify current package/source, state and recovery |
| `package.Glances` | `InstallGlances` | complete | — | deferred optional server operation; verify current package/source, state and recovery |
| `package.PythonPip` | `InstallPythonPip` | — | complete | replace global Python installation with isolated, pinned per-tool environment |
| `package.Selenium` | `InstallSelenium` | — | complete | replace global Python installation with isolated, pinned per-tool environment |
| `setting.NoRootLogin` | `SetNoRootLogin` | complete | — | deferred SSH policy setting; preserve existing file content and test exact restore |
| `action.GenerateSSHkeysRSA` | `GenerateSSHkeysRSA` | — | complete | private overlay for host values or key material; extract generic behavior only after ownership review |
| `action.MountNASSMBfolders` | `MountNASSMBfolders` | complete, plexserver, streambox | — | private overlay for host values or key material; extract generic behavior only after ownership review |
| `package.ExpressVPN` | `InstallExpressVPN` | complete, streambox | plexserver | deferred opt-in VPN profile; keep provider account and host routing private |
| `action.CreateVPNrandomizer` | `CreateVPNrandomizer` | complete, streambox | plexserver | deferred opt-in VPN profile; keep provider account and host routing private |
| `setting.VPNRandomizerPersistent` | `SetVPNRandomizerPersistent` | complete, streambox | plexserver | deferred opt-in VPN profile; keep provider account and host routing private |
| `action.CreateqBittorrentUser` | `CreateqBittorrentUser` | complete, streambox | plexserver | deferred opt-in service profile; separate service logic from host users, ports, media paths and secrets |
| `package.qBittorrentServer` | `InstallqBittorrentServer` | complete, streambox | plexserver | deferred opt-in service profile; separate service logic from host users, ports, media paths and secrets |
| `action.CreateQbtFirewallRules` | `CreateQbtFirewallRules` | complete, streambox | plexserver | deferred opt-in service profile; separate service logic from host users, ports, media paths and secrets |
| `action.CreateQbtServiceFile` | `CreateQbtServiceFile` | complete, streambox | plexserver | deferred opt-in service profile; separate service logic from host users, ports, media paths and secrets |
| `action.CreateQbtSSHkeys` | `CreateQbtSSHkeys` | complete, streambox | plexserver | private overlay for host values or key material; extract generic behavior only after ownership review |
| `action.CreatePlexUser` | `CreatePlexUser` | complete, plexserver | streambox | deferred opt-in service profile; separate service logic from host users, ports, media paths and secrets |
| `package.PlexServer` | `InstallPlexServer` | complete, plexserver | streambox | deferred opt-in service profile; separate service logic from host users, ports, media paths and secrets |
| `action.CreatePlexFirewallRules` | `CreatePlexFirewallRules` | complete, plexserver | streambox | deferred opt-in service profile; separate service logic from host users, ports, media paths and secrets |
| `package.PlexAutoUpdate` | `InstallPlexAutoUpdate` | complete, plexserver | streambox | deferred opt-in service profile; separate service logic from host users, ports, media paths and secrets |
| `package.AMP` | `InstallAMP` | complete | — | deferred opt-in service profile; separate service logic from host users, ports, media paths and secrets |
| `package.Ferium` | `InstallFerium` | — | — | deferred opt-in service profile; separate service logic from host users, ports, media paths and secrets |
| `package.MinecraftServer` | `InstallMinecraftServer` | complete | plexserver, streambox | deferred opt-in service profile; separate service logic from host users, ports, media paths and secrets |

`RequireAdmin`, `PressAnyKeyToContinue` and `Restart` appear as active server preset
selectors but are controller flow, not server-library outcomes. The commented
`GenerateSSHkeys` selector is not defined in the server library; it must not silently
resolve to `GenerateSSHkeysRSA` without a migration decision.

## Closeout rules

1. Mark an outcome migrated only when its user-visible behavior and supported target
   have an accepted v3 operation and VM evidence. Keep partial replacements explicit.
2. Mark a retired outcome only with a concrete reason. Do not turn an old no-op
   function into a successful v3 operation.
3. Reconcile server consumers in `complete`, `plexserver`, and `streambox` before
   moving generic behavior. Keep hostname, NAS, accounts, secrets and media paths
   in a private overlay.
4. Regenerate this table after any source inventory or disposition change with
   `python3 tools/build_burndown.py --write`.
