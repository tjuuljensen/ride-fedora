# V2 outcomes resolved without a v3 install operation

These decisions close source outcomes in the v3.0 progress denominator without
claiming an executable replacement. They do not delete or alter the legacy
source. Reopen a decision if its stated review trigger occurs.

| Source outcome | Decision and evidence | Review trigger |
| --- | --- | --- |
| `server:action.ViewIPaddress` | Retired as an install outcome, 2026-10-30. The `network-devices` v2 function only prints IPv4 addresses found by `ip addr show`; it does not establish desired state. The generic server source and consumers remain owned by `network-devices`. Operators can use `ip addr show` directly; a future read-only v3 status view would be a separate feature. | A request for IP discovery in the v3 CLI or a cross-repository ownership change. |
| `workstation:package.TecmintMonitorSh` | Retired, 2026-10-30. The v2 pair downloads a remote HTTP script into `/usr/local/bin` and removes that path. RIDE v3 does not put fetched scripts in a default profile. No maintained, verified acquisition or owned update path was established for this behavior; the v2 function is not a safe v3 operation. | A maintained, verifiable upstream artifact and explicit user demand for this monitoring function. |
| `workstation:package.Galleta` | Retired, 2026-10-30. `InstallGalleta` prints a Kali project URL and `RemoveGalleta` prints an empty line; neither changes machine state. A v3 install operation cannot claim that this placeholder succeeded. | An explicit request for Galleta installation with a current source, license, detection, and inverse review. |
| `workstation:package.Xplico` | Retired, 2026-10-30. `InstallXplico` prints a project URL and `RemoveXplico` prints an empty line; neither changes machine state. A v3 install operation cannot claim that this placeholder succeeded. | An explicit request for Xplico installation with a current source, license, detection, and inverse review. |
| `workstation:setting.AtomTelemetry` | Retired, 2026-10-30. The two v2 functions edit `.atom/init.coffee`; the enable path starts and kills Atom, then deletes that file. [Atom's upstream repository](https://github.com/atom/atom) is archived and read-only. Applying this setting to a current Fedora 44 machine would edit a user's legacy file without an owned, maintained application or safe inverse. | A maintained Atom-compatible editor with the same telemetry contract, explicit user demand, and tested user-file backup and restoration. |

Reviewer: Codex. No VM install or manual session is appropriate for these
non-operable dispositions. The progress ledger records them separately from
supported and opt-in candidate operations.
