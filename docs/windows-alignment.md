# Alignment with the Windows v3 development branch

This review uses `ride-windows` branch `codex/ride-v3-migration`. The Linux
client follows its public command vocabulary and catalog-driven lifecycle,
while JSON and Bash replace PowerShell's `.psd1` data and modules.

| Windows pattern | Linux v3 implementation | Next work |
| --- | --- | --- |
| Default `list`, literal `search`, `show`, `plan`, explicit `apply` | Same verbs and default; `--dry-run` parallels `-WhatIf` for mutations. | Keep help and generated docs aligned as new views arrive. |
| `download`, `install`, `set`, `unset`, `status`, `restore`, `remove` | Same verbs; typed IDs and declared states route to trusted handlers. | Add setting classes beyond systemd only after exact recovery tests. |
| PowerShell data-only catalog and profiles | JSON Schema plus `jq`; no sourced profile code. | Introduce user/site overlays with explicit ownership and validation. |
| PowerShell modules for packages, settings, discovery and run state | Bash modules under `lib/v3`; Fedora DNF/RPM first. | Add apt/dpkg adapters independently after Debian and Ubuntu VMs. |
| Tab completion from catalog and state | Bash completion reads local JSON, profiles and run IDs. | Add context filters and test stale/malformed state. |
| Per-run snapshots and recovery | Private JSON journals capture before and after observations. | Expand setting ownership; never promise exact package reinstall. |
| GitHub latest-release cache with provenance | Five-minute bounded disk cache, explicit PAT context, SHA-256 artifact evidence. | Stabilize cross-platform contract and only then consider a shared module. |
| Package identity and license review | Catalog records product, source, license and verification. | Cross-check the shared tools against Windows catalog without sharing installers. |

Windows has a larger, VM-tested catalog and richer search filters, variants,
credentials, and settings presentation. Linux v3 currently has a narrow
candidate catalog and no acceptance VM evidence. The command names align now;
feature parity is a staged migration, not a release claim.
