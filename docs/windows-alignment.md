# Alignment with the Windows v3 development branch

The initial review used `ride-windows` branch `codex/ride-v3-migration` at
`006f5ab` (2026-10-14). The Linux
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
variants, credentials, and settings presentation. Linux v3 has accepted base
package operations on Fedora 44 Cloud Base, Workstation, and Server, while its
remaining catalog entries are candidates. The command names align now;
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

### Fedora Workstation package batch preflight, 2026-10-30

Compared Linux `codex/ride-v3-migration` at `0bfd3c0` with Windows
`codex/ride-v3-migration` at `17f9cef` for `package.less` and
`package.exfatprogs`. Linux catalog schema 3 and profile schema 1 select one
installed deployment and an optional declared source; run schema 2 records
that selection. Windows catalog and profile schema 1 use PowerShell data;
package variants are selected from the catalog, and saved package recovery
records can use schema 3 with the selected variant. The data formats and
deployment models differ as registered above. Both clients separate
acquisition from installed state and preserve the selected package identity
for recovery. Neither offers the completed offline install-from-retained-RPM
workflow. These Fedora RPM products have no shared Windows installer facts to
copy into this batch.

No unexplained shared-contract drift was found in this scoped review. Recheck
the comparison if either schema or package lifecycle changes, and at release
candidate preparation. The Workstation pilot later passed its focused VM
checks; operation-level review remains before promotion. This review does not
promote either operation.

### Linux edition target gate, 2026-10-30

Reviewed the Linux working diff based on `0bfd3c0` against Windows `17f9cef`
before changing Linux catalog target matching. Windows `SupportedTargets`
distinguishes Windows 11 and Windows Server 2025; its offline profile
preflight also binds build, `EditionId`, and architecture. Linux's Fedora `ID`
and release are shared by Cloud Base, Workstation, and Server, so supported
Linux target rows require explicit `variantIds` matched against
`/etc/os-release` `VARIANT_ID`. Candidate
rows may omit the field during development, but still require
`--allow-candidate` for changes. This is an intentional platform identity
difference, not a shared package contract change. Review it when a new Linux
edition or Windows target form is added and again before the release candidate.

The Linux source signature includes the target declaration. Narrowing an
existing row changes that signature; an older run cannot be restored with the
new catalog. The mocked recovery check confirms that retaining the original
catalog permits restore. Inventory and resolve any non-disposable candidate
runs before publishing a narrowed target row; do not silently rewrite a run.

### Fedora Workstation OpenSSH client batch preflight, 2026-10-30

Compared the Linux working diff based on `0bfd3c0` with Windows `17f9cef` for
`package.openssh-clients`. Windows has no OpenSSH catalog operation in this
revision. The Linux operation uses the same installed `fedora-rpm` deployment,
DNF handler, profile source selection, and run schema 2 journal structure as
the first Fedora package batch. Its catalog row is restricted to Workstation
until Server has its own evidence. The Workstation VM found that removing
`openssh-clients` would break GNOME dependencies, so this Linux operation is
installed-only with `recovery: none`. The reversible `remove-new-install`
package contract remains available for other Linux operations; Windows has no
corresponding OpenSSH row to align. The edition identity difference and source
signature recovery limit above apply. No unexplained shared-contract drift
was found in this scoped review. Recheck this deliberate recovery difference
when adding Server, when Windows adds an OpenSSH operation, when changing
package deployment semantics, or before a release candidate.

### Fedora Server base package batch review, 2026-10-30

Compared the Linux working diff based on `0bfd3c0` with Windows `17f9cef`
again for the `server-base` profile, `package.less`, and
`package.openssh-clients`. The Server addition changes only Linux's Fedora
edition target lists and pinned VM matrix; catalog schema 3, profile schema
1, run schema 2, package identity, explicit source selection, DNF handler,
artifact verification, and installed deployment retain the semantics above.
Windows `SupportedTargets` already separates Windows Server from Windows 11;
Linux now binds `VARIANT_ID=server` in its target declaration and VM harness.
The Server pilot verified reversible `less` and installed-only OpenSSH with
its explicit `recovery: none` limit. No Windows OpenSSH operation or shared
product fact was introduced, and no unexplained shared-contract drift was
found. Recheck when Windows adds OpenSSH, either schema or package recovery
changes, another Linux edition is declared, or a release candidate is
prepared.

### Base package support promotion, 2026-10-30

The owner confirmed no non-disposable v3 runs. The accepted Linux rows retain
their reviewed target, provider, installed deployment, and recovery semantics;
promotion changes only `status` and adds a per-operation acceptance path.
The Windows development branch remained at `17f9cef` when checked before this
promotion. No shared catalog, profile, or run-state contract changed, and no
new Windows product fact was inferred. Recheck both branches at release
candidate preparation or when a package contract changes.

### Fedora CLI package batch 01, 2026-10-30

Compared Linux `codex/ride-v3-migration` with Windows
`codex/ride-v3-migration` at `17f9cef` before adding the six v2 CLI package
replacements in [native RPM batch 01](migrations/native-rpm-01.md). Windows has
no corresponding `pwgen`, `htop`, `bat`, `ncdu`, `ripgrep`, or `fd-find` catalog
operation. Linux adds candidate rows using the existing installed Fedora RPM
deployment, explicit `fedora-rpm` source, profile schema 1 selectors, and run
schema 2 journal. No shared schema, source fallback, artifact, or recovery
contract changes. Recheck if these products enter the Windows catalog, if
Linux changes package deployment behavior, and before release-candidate
promotion.

### Fedora RPM package batch 02, 2026-10-30

Compared Linux `codex/ride-v3-migration` with Windows
`codex/ride-v3-migration` at `17f9cef` for the four scoped v2 outcomes in
[native RPM batch 02](migrations/native-rpm-02.md). Windows has no shared
Fedora installer for `libewf`, `exif`, `md5deep`, or `alien`. Linux uses the
existing installed `fedora-rpm` deployment, explicit source, and run schema 2
journal without changing shared package, profile, or recovery semantics.
`libewf` and `ewftools` remain separate Linux packages; no product-wide
exclusion is inferred. Recheck at release-candidate preparation or if a
shared product identity or deployment contract changes.

### Fedora workstation package batch 03, 2026-10-30

Compared the Linux catalog, profile selectors, and run-state contract with
Windows `codex/ride-v3-migration` at `17f9cef` before implementing
[native RPM batch 03](migrations/native-rpm-03.md). The three Linux operations
select Fedora RPMs through the existing `fedora-rpm` installed deployment;
the two Nautilus resolution decisions add no runnable operation. No shared
schema, product identity, source fallback, or journal behavior changes. The
Windows branch has no corresponding Fedora installer. Recheck if Chromium or
another product gains a shared identity contract, if either platform changes
profile or run-state behavior, and before release-candidate preparation.

### Fedora workstation package batch 04, 2026-10-30

Compared the Linux catalog, profile, and run-state schemas with Windows
`codex/ride-v3-migration` at `17f9cef` before adding the five
[native RPM batch 04](migrations/native-rpm-04.md) candidates. These rows only
install Fedora packages; `dc3dd` is never run against a device. The
source-built, broad-group, and OTR security outcomes were moved to separate
batches before promotion. No Windows installer is inferred from these Linux
product facts, and no shared schema, source-selection, or journal behavior
changed. Review again if Windows gains one of these product IDs or package
semantics change, and before release-candidate preparation.

### Fedora repository package batch 05, 2026-10-30

Compared Linux catalog, profile, and run-state schemas with Windows
`codex/ride-v3-migration` at `17f9cef` before implementing the five
[native RPM batch 05](migrations/native-rpm-05.md) candidates. Fedora's
`vlc` source supplies the player; additional codec sources remain separate.
Wine, Dia, libpst, and Lynis use Fedora installed deployments without
running the applications or touching user data. HandBrake, Eza, ClamAV, and
KeePassXC were moved to source-ownership or safety-specific batches. No
shared schema, source-selection fallback, journal, or Windows installer
contract changed. Recheck product facts and shared behavior if Windows
adds a matching product, Linux changes deployment semantics, or a release
candidate is prepared.

### Fedora provider foundation batch 01, 2026-10-30

Compared Linux catalog, profile, and run-state schemas with Windows
`codex/ride-v3-migration` at `0ff139f` before splitting the v2
[`Required` and `ShellTools` bundles](migrations/provider-foundation-01.md).
The Windows branch changed only `docs/MIGRATION-PLAN.md` since the prior
comparison, adding the shared practical test-effort guidance; its schema and
runtime contract remain as reviewed for native RPM batch 05. Linux's proposed
`pv` and `strace` operations use Fedora RPMs and the existing DNF package
handler. No Windows installer or shared product ID is inferred. Review again
if the source-selection contract, profile/run-state schemas, or a shared
product mapping changes, and before release-candidate preparation.

### RPM Fusion provider assessment, 2026-10-30

Compared Linux catalog, profile, and run-state schemas with Windows
`codex/ride-v3-migration` at `0ff139f` while assessing
[provider foundation batch 02](migrations/provider-foundation-02.md). No
Linux catalog operation or shared schema was added: the current Fedora DNF
handler does not establish RPM Fusion key trust or owned repository recovery.
This remains an unresolved, high-risk Linux provider decision. Review again
when a trust-pinned provider is designed, when Windows changes shared source
selection, and before release-candidate preparation.

### Fedora provider foundation batch 03, 2026-10-30

Compared Linux catalog, profile, and run-state schemas with Windows
`codex/ride-v3-migration` at `0ff139f` before adding the
[kernel and Python package candidates](migrations/provider-foundation-03.md).
These use Fedora RPMs and the unchanged DNF installed deployment. DNF5
utility and archive-tool replacements are recorded separately from working
install status. Flathub was isolated as a remote-ownership batch. No shared
schema, journal, source fallback, or Windows installer changed. Recheck if
either platform changes package identity or source-selection semantics, and
before release-candidate preparation.

### Fedora provider foundation batch 04, 2026-10-30

Compared Linux catalog, profile, and run-state schemas with Windows
`codex/ride-v3-migration` at `0ff139f` before splitting the
[editor and GNOME utility packages](migrations/provider-foundation-04.md).
The four proposed Linux rows use Fedora RPMs, the unchanged DNF handler,
and exact Workstation target scope. DNF5 versionlock is a documented
replacement, not a new policy handler. The unowned v2 `gparted` removal is
excluded. GNOME extension installer, Flatpak runtime, and snapd were
separated for their own acquisition, data, and security gates. No shared
schema, source fallback, journal, or Windows installer changed. Recheck on
shared product or package-contract changes and before release review.

### Fedora provider foundation batches 05 and 08, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f`. The
[codec bundle](migrations/provider-foundation-05.md) is a non-runnable
Linux-only resolution; it adds no catalog or profile row. The
[Eza source batch](migrations/provider-foundation-08.md) adds one installed
Fedora RPM operation with the existing DNF handler and Workstation target.
The legacy GitHub portable download is a separately counted replacement,
not a second provider or a Windows installer fact. Windows has no Eza catalog
row in this revision. The Linux change does not alter the shared product,
source-selection, deployment, profile, journal, or recovery contract. The
existing platform-specific representation and portable-handler differences
remain intentional as registered above. Recheck if either platform adds Eza
or portable coexistence, changes source fallback or run-state semantics, or
before release review. No unexplained shared-contract drift was found.

### Fedora provider foundation batches 02, 06, and 07, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f`. The
[RPM Fusion repository](migrations/provider-foundation-02.md),
[Security Lab group](migrations/provider-foundation-06.md), and
[HandBrake RPM](migrations/provider-foundation-07.md) outcomes are
documented non-runnable v3.0 decisions. They add no catalog ID, profile
selection, handler, or journal semantics. Existing Fedora-signed individual
forensic packages retain their separately reviewed Linux source and target.
No Windows repository source or installer fact is inferred from these
Linux-only decisions. The registered representation and deployment
differences remain intentional; no unexplained shared-contract drift was
found. Recheck if a repository or group handler is introduced, a shared
product/source contract changes, or a release candidate is prepared.
