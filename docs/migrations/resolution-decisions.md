# V2 outcomes resolved without a v3 install operation

These decisions close source outcomes in the v3.0 progress denominator without
claiming an executable replacement. They do not delete or alter the legacy
source. Reopen a decision if its stated review trigger occurs.

| Source outcome | Decision and evidence | Review trigger |
| --- | --- | --- |
| `server:action.ViewIPaddress` | Retired as an install outcome, 2026-10-30. The `network-devices` v2 function only prints IPv4 addresses found by `ip addr show`; it does not establish desired state. The generic server source and consumers remain owned by `network-devices`. Operators can use `ip addr show` directly; a future read-only v3 status view would be a separate feature. | A request for IP discovery in the v3 CLI or a cross-repository ownership change. |
| `workstation:package.TecmintMonitorSh` | **Capability kept by owner; old HTTP script retired.** The v2 pair downloads an unverified HTTP script into `/usr/local/bin`. A maintained monitoring alternative needs its own verified source and owned recovery. | Review the monitoring use case and a maintained source; do not reuse the unverified HTTP script. |
| `workstation:package.Galleta` | **Decision deferred by owner.** `InstallGalleta` prints a Kali project URL and `RemoveGalleta` prints an empty line; neither changes machine state. Galleta parses legacy Internet Explorer cookies. [Hindsight](https://github.com/RyanDFIR/hindsight) handles modern Chromium and Firefox cookies, but is not established as a parser for the old IE format. | Decide whether legacy IE cookie parsing is needed or a modern browser-forensics capability covers the intent. |
| `workstation:package.Xplico` | **Capability kept by owner; old link-only pair retired.** `InstallXplico` prints a project URL and `RemoveXplico` prints an empty line; neither changes machine state. | Find a current source or robust alternative, then review license, deployment, detection, and inverse. |
| `workstation:setting.AtomTelemetry` | Retired, 2026-10-30. The two v2 functions edit `.atom/init.coffee`; the enable path starts and kills Atom, then deletes that file. [Atom's upstream repository](https://github.com/atom/atom) is archived and read-only. Applying this setting to a current Fedora 44 machine would edit a user's legacy file without an owned, maintained application or safe inverse. | A maintained Atom-compatible editor with the same telemetry contract, explicit user demand, and tested user-file backup and restoration. |
| `workstation:setting.Screensaver` | **Decision deferred by owner.** `DisableScreensaver` sets GNOME idle activation and lock to false and idle delay to zero. The same active v2 preset later calls `EnableScreenSaver`, so this earlier action is overwritten. | Decide whether an explicit lock-disabled value belongs in the kept configurable lock policy; require session-safety review and atomic prior-state recovery. |
| `workstation:setting.ScreenSaver` | **Decision deferred by owner.** `EnableScreenSaver` sets two GNOME lock booleans and idle delay 300 seconds, but v2 has no exact inverse or journal for the three settings. | Determine whether the kept configurable lock-timing operation covers this outcome; require baseline capture, partial-failure rollback, and disposable-session evidence. |

Reviewer: Codex. No VM install or manual session is appropriate for these
non-operable dispositions. The progress ledger records them separately from
supported and opt-in candidate operations.
