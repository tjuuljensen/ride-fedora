# Legacy Fedora default migration ledger

Source: `default.preset` on `master` at `43ba467`. All 76 active lines are dispositioned below. The v3 default profile is intentionally small; deferred items are not silently executed. These decisions describe the development branch, not VM acceptance.

The [complete workstation and server burndown](workstation-server-burndown.md)
also inventories every non-active library function and the three server presets.

| Legacy action | Disposition | v3 target or rationale |
| --- | --- | --- |
| `DisableScreensaver` | retired | Conflicts with EnableScreenSaver in the same legacy preset; review a single desired state later. |
| `SetupUserDefaultDirs` | deferred | Review directory ownership and user scope. |
| `EnableFastDNF` | replaced | DNF5 defaults need current evidence; no legacy config edit. |
| `UpdateFedora` | deferred | Add explicit non-reversible system update operation after VM acceptance. |
| `InstallRequired` | replaced | Smaller package.less and package.openssh-clients in default; review remaining list. |
| `InstallShellTools` | deferred | Split into specific repository packages. |
| `InstallRPMfusionRepos` | deferred | External repository enablement needs opt-in and trust review. |
| `InstallKernelTools` | deferred | Kernel-dependent package group requires target checks. |
| `InstallDNFutils` | replaced | Review current DNF5 commands and plugins. |
| `InstallEzaGitHub` | replaced | Prefer Fedora repository package after verification. |
| `InstallFlathub` | deferred | External Flatpak remote remains opt-in. |
| `InstallAppImageLauncher` | deferred | Review maintained source and current desktop integration. |
| `InstallExif` | deferred | Review product identity and official package. |
| `InstallMd5deep` | deferred | Review current package and forensic use case. |
| `InstallLibEWF` | replaced | package.ewftools covers EWF utilities; verify library intent separately. |
| `InstallExifTool` | deferred | Current GitHub source build needs provenance and verification redesign. |
| `InstallASN` | deferred | Current upstream acquisition needs review. |
| `InstallUnfURL` | deferred | Current Python package method needs isolation. |
| `InstallCyberChef` | deferred | Align product facts with Windows catalog; platform package remains local. |
| `InstallChepy` | deferred | Python tooling needs isolated environment and pins. |
| `InstallNetworkMiner` | deferred | Align product identity with Windows; review Linux packaging. |
| `InstallVeraCrypt` | deferred | Review publisher verification and licensing. |
| `InstallPwgen` | deferred | Candidate native repository package. |
| `InstallHtop` | deferred | Candidate native repository package. |
| `InstallBat` | deferred | Candidate native repository package. |
| `InstallNcdu` | deferred | Candidate native repository package. |
| `InstallRipgrep` | deferred | Candidate native repository package. |
| `InstallFd` | deferred | Candidate native repository package. |
| `InstallDocker` | deferred | Generic server role only after provider and repository review. |
| `InstallVMFStools` | deferred | Legacy active entry is incomplete; no executable v3 handler. |
| `InstallPythonPip` | replaced | Use per-operation isolated Python installs, not global pip. |
| `InstallPackagingTools` | deferred | Split package list by use case. |
| `InstallBasicEditors` | deferred | Candidate native repository packages. |
| `InstallTerminator` | deferred | Optional desktop profile only. |
| `InstallAlien` | deferred | Review relevance and support. |
| `InstallSmartMonTools` | deferred | Optional system tools profile. |
| `InstallVisualStudioCode` | deferred | Align product facts with Windows; Fedora source stays local. |
| `InstallHexchat` | deferred | Review upstream maintenance before reintroduction. |
| `InstallNetworkTools` | deferred | Split broad network bundle into focused packages. |
| `InstallNetCommsTools` | deferred | Split broad communications bundle. |
| `InstallNetMgrLibreswan` | deferred | Optional VPN role. |
| `InstallSpeedtestCLI` | deferred | Review current upstream and source. |
| `InstallTecmintMonitorSh` | retired | Default profile must not fetch and execute remote scripts. |
| `InstallGnomeExtInstaller` | deferred | Review current GNOME extension lifecycle. |
| `InstallBrave` | deferred | Third-party repository and license review. |
| `InstallChromium` | deferred | Candidate distro repository package. |
| `SetFirefoxPreferences` | replaced | Review settings against current Firefox policy; avoid legacy file overwrite. |
| `InstallFirefoxAddons` | deferred | Keep existing verified policy helper; integrate with v3 lifecycle later. |
| `InstallYouTubeDownloader` | replaced | Review maintained yt-dlp packaging instead of legacy youtube-dl. |
| `InstallGnomeTools` | deferred | Split GNOME package bundle. |
| `InstallSystemMonitor` | deferred | Review current GNOME extension support. |
| `InstallGnomeExtensions` | deferred | Review current GNOME extension IDs and API. |
| `ShowDateInTaskbar` | deferred | Setting handler needs baseline and restore. |
| `ShowWeekNumbersInTaskbar` | deferred | Setting handler needs baseline and restore. |
| `SetWindowCtlMinMaxClose` | deferred | Setting handler needs baseline and restore. |
| `DisableMiddleButtonPaste` | deferred | Setting handler needs baseline and restore. |
| `SetGnomeRegionDaDK` | deferred | User locale must be explicit profile data. |
| `SetScreensaverSlp10Lgn5` | deferred | Resolve conflict with other screensaver operations. |
| `SetCustomKeyboardShortcut` | deferred | User-owned shortcut state needs exact restore. |
| `SetGnomeCustomFavorites` | deferred | User-specific favorites need profile data. |
| `SetGnmLocationServiceOff` | deferred | Review current GNOME setting and scope. |
| `SetGnmAutoProblemRptOff` | deferred | Review current GNOME setting and scope. |
| `SetPowerPercentageLow15` | deferred | Review current power setting and support. |
| `EnableBashAliases` | deferred | User shell configuration must preserve unowned content. |
| `SetAliasLsEza` | deferred | User shell configuration must preserve unowned content. |
| `SetAliasWanIP` | deferred | User shell configuration must preserve unowned content. |
| `InstallBitwardenAppImage` | deferred | Review publisher signature and platform artifact. |
| `InstallCheat` | deferred | Review current upstream and source. |
| `InstallUnifyingOnLaptop` | deferred | Hardware-dependent operation. |
| `InstallVMtoolsOnVM` | deferred | VM-specific provider after detection test. |
| `InstallYubikeyManager` | deferred | Hardware-dependent optional package. |
| `InstallSonosPlayer` | deferred | Review publisher source and architecture. |
| `SetHostname` | deferred | Host-specific value belongs in private profile. |
| `EnableScreenSaver` | retired | Conflicts with DisableScreensaver in the same legacy preset; review one desired state. |
| `PressAnyKeyToContinue` | retired | Interaction belongs in CLI flow, not an operation. |
| `Restart` | retired | Reboot remains an explicit separate user action. |

## Release gates

- Every implemented candidate remains blocked by default until a disposable Fedora VM run records apply, repeat apply, status, remove or restore where applicable, and failure behavior.
- The Firefox extension manager remains maintained and tested, but its v3 catalog lifecycle is pending. Its legacy direct function call is not reused.
- Generic server actions remain in `network-devices` until source, consumers, ownership, and rollback are reconciled. No host-specific preset is moved into this repository.
- Debian and Ubuntu adapters remain outside the supported target matrix until their own VM checks pass.

## Former CERT forensic repository burndown

`default.preset` labels these entries “CERT Forensic Repo — THESE ARE EMPTY”. The
corresponding functions in `lib-fedora.sh` only print a URL or nothing; none is
an installation or removal path. Keep each item visible until a maintained
source, verified acquisition method, detection, removal, and disposable-VM
result are recorded. No entry below is part of the v3 default profile.

| Preset install/remove pair | Preset state | v3 burndown item |
| --- | --- | --- |
| `InstallGalleta` / `RemoveGalleta` | commented out | Find maintained Fedora packaging or a verifiable upstream release; define real install and removal. |
| `InstallPlaso` / `RemovePlaso` | commented out | Evaluate the documented opt-in Fedora COPR in a disposable VM; retain as deferred if install/removal cannot pass. |
| `InstallAutopsy` / `RemoveAutopsy` | commented out | Evaluate upstream Linux setup and dependency ownership in a disposable VM; retain as deferred if recovery is unreliable. |
| `InstallXplico` / `RemoveXplico` | commented out | Review current upstream maintenance, dependencies, and a trusted package source before adding an operation. |
| `InstallVolatility` / `RemoveVolatility` | commented out | Treat the older Volatility line separately from Volatility3; check present support and a verifiable source before deciding whether to migrate or retire. |
| `InstallVolatility3` / `RemoveVolatility3` | commented out | Isolated `package.volatility3` is a v3 candidate; verify the pinned core install, detection, removal, and failure recovery in a disposable VM before support. |
| `InstallVMFStools` / `RemoveVMFStools` | both commented out in this block; install also active later in the preset | Resolve the duplicate preset intent; evaluate maintained VMFS tools packaging and tested removal. The active legacy function is still only a URL stub. |
