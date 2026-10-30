# Alignment with the Windows v3 development branch

This review uses `ride-windows` branch `codex/ride-v3-migration` at `006f5ab`
(2026-10-14). The Linux
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
| Product, distribution, deployment, provider, artifact format and scope | Catalog schema 3 separates the current installed deployment from its selected source provider and format. | Add independently owned portable deployments and product-specific coexistence review before enabling them. |
| Multiple acquisition sources | An explicit `--source` or profile `source` selects a declared provider for the current installed slot; no automatic fallback. | Add only equivalent approved providers, preference resolution and transport-only fallback with exact artifact evidence. |
| Download and offline installation | RPM download is separate from installed state; DNF install still resolves by package name. | Retain a verified artifact manifest and add an explicit offline install that never falls back to the network. |
| Package identity and license review | Catalog records product, source, license and verification. | Cross-check shared product facts against Windows without sharing installers. |

Windows has a larger, VM-tested catalog and richer search filters, deployed
variants, credentials, and settings presentation. Linux v3 currently has a narrow
candidate catalog and no acceptance VM evidence. The command names align now;
feature parity is a staged migration, not a release claim.

The shared deployment contract and Linux implementation limits are recorded in
[package deployment decisions](package-deployment-decisions.md). Windows has
individual installed and portable handlers, while coexistence and kit assembly
remain design work there; Linux has no portable handler yet.

## Schema and behavior drift review

Review the catalog, profile, and run-state models against the Windows
development branch at each package migration batch and before each release
candidate. Compare the meaning of product IDs, distribution and deployment
identity, provider selection and fallback, artifact evidence, ownership, and
recovery. The models need not use identical file formats or field names, but
differences in shared behavior need an explicit decision. Update this register
when either repository changes its schema or package lifecycle.
Each batch records the compared branches or revisions, review date, and
resolution in its migration evidence so later reviewers can see what was
actually compared.

| Intentional difference (reviewed 2026-10-14) | Reason | Review trigger |
| --- | --- | --- |
| Windows catalog and profiles use PowerShell data files; Linux uses versioned JSON and `jq`. | Each client uses a native data representation with validation; product and lifecycle semantics are shared. | Any schema migration or new shared field. |
| Windows has installed and portable package handlers; Linux catalog schema 3 declares one `installed` deployment per package. | Linux portable ownership, destination selection, and recovery lack handler and VM evidence. | First Linux portable operation or Windows coexistence implementation. |
| Linux allows explicit selection among declared source providers for one installed deployment, with no preference or automatic fallback. | The bounded fallback and preference rules are agreed, but equivalent artifact proof and retry handling are unfinished. | Adding a second provider for a product or changing Windows source resolution. |
| Linux currently requires different RPM names for alternative providers in one deployment slot. | RPM presence alone cannot identify which provider supplied the same package name; provenance-aware observation is still needed. | Adding two repositories or downloads for the same RPM name. |
| Linux `download` writes an RPM and checksum sidecar while `install` resolves through DNF; neither client has completed the planned offline install-from-retained-artifact workflow. | A bound artifact manifest, offline dependency handling, and recovery need implementation and tests. | First offline install implementation in either repository. |
| Linux run schema 2 records selected provider and installed deployment; Windows uses platform-specific state records. | Journals must preserve each platform's observable state and restoration method. | Any run-state migration or cross-platform recovery contract change. |
