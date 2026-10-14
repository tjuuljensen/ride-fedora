# Legacy Fedora default migration ledger

Source: `default.preset` on `master` at `43ba467`. All 76 active lines are dispositioned below. The v3 default profile is intentionally small; deferred items are not silently executed. These decisions describe the development branch, not VM acceptance.

The [scoped workstation and server burndown](workstation-server-burndown.md)
also covers non-active library functions and the three server presets, apart
from outcomes the owner excluded as obsolete or host-specific.

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

## Batch delivery and evidence

Use this plan as the handoff record for phased migration. A batch names its
operation IDs or legacy outcomes, source owner, target VM, dependencies,
expected prior and final state, recovery limit, acceptance checks, status,
revision, dated evidence, and exact next action. Keep source readiness separate
from runtime activation and verified behavior. No batch is currently marked
verified; catalog operations remain candidates.

| Stage | Agent work | Owner or runtime input | Completion evidence |
| --- | --- | --- | --- |
| Select | Group a small related outcome set; identify catalog IDs and deferred neighbors. | Choose a target and provide a disposable VM when runtime testing begins. | Named scope, target distro/release/CPU, owner, and exclusions in this plan. |
| Assess | Trace legacy behavior, consumers, upstream source, data ownership, dependencies, detection, and inverse. | Resolve host-specific values only if the selected operation needs them. | Current-to-v3 mapping, risks, and recovery limits. |
| Implement | Prepare catalog, handler, profile, docs, and focused tests; run static and mocked checks. | Review only decisions that cannot be derived from source or established scope. | Reviewable patch and `source-ready` status after relevant CI passes. |
| Activate | Apply the prepared revision only in a disposable target VM; record exact command and snapshot. | Supply VM access or run the documented commands. | VM log and `deployed-awaiting-verification` status. |
| Verify | Check plan, apply, repeat apply, status, removal or restore, partial failure, and package or artifact evidence. | Confirm any user-visible desktop behavior that automation cannot observe. | Dated `docs/acceptance/<operation-id>.md` results and `verified` or failed status. |
| Close or recover | Promote only accepted target rows; otherwise restore the VM snapshot, retain candidate status, and record the failure. | Provide further observations only when a check depends on them. | Updated catalog, migration row, evidence, and concrete next action. |

Begin with a Fedora 44 x86_64 Workstation VM package pilot such as
`package.less` and `package.exfatprogs`. Run CI first, then use `plan`, `apply`,
repeat `apply`, `status`, `remove`, and `restore` as applicable. Keep the VM
snapshot until recovery is checked. A green static check or source commit alone
does not promote an operation to `supported`. Server, Firefox, third-party
artifact, and Waydroid work should use separate batches because their state
and recovery differ.

The [disposable VM harness](acceptance/VM-HARNESS.md) now provides a Fedora 44
Cloud Base pilot for `package.exfatprogs`, including partial failure. Its Cloud
result can inform the package handler review; Workstation and Server edition
acceptance remain separate release gates. No operation has been promoted from
source readiness by adding the harness.

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
