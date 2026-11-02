# Alignment with the Windows v3 development branch

## Shared contract adoption, 2026-11-01

### Plex Server package batch, 2026-11-02

Linux adds a Fedora-only Plex repository package and an RPM-owned systemd
service operation, both scoped to Fedora 44 Server x86_64. The Windows
development branch `codex/ride-v3-migration` at `d91c44b` has no corresponding
Plex Server catalog operation or shared installer identity, so no Windows
catalog ID or installer behavior was introduced. Linux acceptance verifies
publisher signatures and server-data preservation; Windows-specific package
acquisition, service semantics, and support evidence would require a separate
Windows migration. Plex's mutable v2 updater is replaced by the existing
Fedora DNF update lifecycle. Review if
the Windows client adopts Plex Server or the shared product/operation contract
changes.

### AMP package batch, 2026-11-02

Linux adds opt-in candidate `package.amp-installer` for CubeCoders' unsigned
Fedora RPM package, pinned by HTTPS URL, package identity, and SHA-256, with
RPM scriptlets suppressed. ADS/controller creation, credentials, license
activation, firewall policy, Java/container selection, and AMP instance data remain
operator-managed. Windows has no shared AMP package installer ID or matching
catalog operation, so Linux retains a platform-native provider and support
record. Revisit if Windows adds AMP deployment or the shared product contract
changes.

### Forensic package source, 2026-11-01

Linux adds `package.plaso` using Fedora's DNF and the upstream-documented GIFT
stable COPR; Windows package acquisition remains native to Windows and does not
share Fedora RPM repository configuration. The product intent is shared, while
package formats, providers, support evidence, and inverse behavior remain
platform-specific. The Plaso operation is opt-in and Fedora 44 Workstation
candidate acceptance is tracked in `docs/acceptance/package.plaso.md`.

Autopsy uses the Sleuth Kit Labs Snap Store listing on Fedora and the separate
Linux development/catalog path on Windows. The Linux client depends on the
Fedora `package.snapd` operation and does not install Snaps on Windows. RIDE
manages only the Autopsy Snap's presence on Linux; interface approvals and
application data remain governed by Snap's own interface and snapshot behavior.
Fedora 44 acceptance observed publisher-granted connections for
`block-devices`, `dm-crypt`, and `fuse-support`; this is an intentional
platform security difference under review, not a shared installer contract.

The user requested a versioned shared behavior contract and reciprocal maintainer
rules while both clients are under active development. Contract **1.0.0** is
canonical in [ride-windows](https://github.com/tjuuljensen/ride-windows/blob/codex/ride-v3-migration/docs/models/ride-behavior-contract.md);
the [local reference](models/ride-behavior-contract-ref.json) pins its exact UTF-8
LF bytes by SHA-256. Both repos adopt the same version/digest. Neither the mutable
development branch nor the peer implementation is automatically authoritative
for new behavior. Either repo can propose a versioned change.

ALIGN-01/02 are complete as source documentation/policy. AGENTS now requires
reciprocal review for shared CLI, settings, schema meaning, acquisition, planning,
acceptance, privilege and recovery changes, as well as package batches and RCs.
The contract owns the procedure; this register records Fedora's implementation
and evidence. No duplicate contract is maintained here.

The [updated Windows comparison](https://github.com/tjuuljensen/ride-windows/blob/codex/ride-v3-migration/docs/fedora-alignment.md)
includes Windows' new candidate execution/preview/restore switch. Remaining gaps
include candidate preview/download rules, generic disabled mapping for unset,
profile removal eligibility, ignored/conflicting arguments, status selectors and
completion. The special iBus restore-preview path needs common target/identity
preflight review. Native Bash/PowerShell syntax, provider implementations and
support evidence remain intentional platform boundaries.

The [final-v3 tasks](MIGRATION-PLAN.md#cross-platform-alignment-for-final-v3)
track ALIGN-03 through ALIGN-09 with owners and completion criteria. Existing
comparison rows below are dated evidence, not proof of full 1.0.0 conformance.
The contract is not published at an immutable commit yet; ALIGN-09 tracks that
release step. Adoption changes no CLI, target support, catalog or migration count.
Review triggers: every affected shared change, package batch and release candidate.

## Earlier comparison baseline

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
| Product, distribution, deployment, provider, artifact format and scope | Catalog schema 3 separates deployment identity and source evidence; Linux now has an opt-in pinned user-local Eza binary alongside its Fedora RPM. | Recheck ownership, coexistence, and journal behavior at each new portable operation. |
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
individual installed and portable handlers. Linux now has a pinned portable
binary handler for Eza, separate from its Fedora RPM deployment; product
coexistence is verified per operation and remains an explicit review item.

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
| Windows and Linux expose native installed and portable handlers; Linux Eza uses a separate operation and user-local deployment identity beside the Fedora RPM. | Platform handlers differ, and the Linux Eza path is limited to Fedora 44 Workstation x86_64 with pinned release evidence. | A new portable product, target, architecture, or shared recovery-contract change. |
| Linux allows explicit selection among declared source providers for one installed deployment, with no preference or automatic fallback. | The bounded fallback and preference rules are agreed, but equivalent artifact proof and retry handling are unfinished. | Adding a second provider for a product or changing Windows source resolution. |
| Linux currently requires different RPM names for alternative providers in one deployment slot. | RPM presence alone cannot identify which provider supplied the same package name; provenance-aware observation is still needed. | Adding two repositories or downloads for the same RPM name. |
| Linux `download` writes an RPM and checksum sidecar while `install` resolves through DNF; neither client has completed the planned offline install-from-retained-artifact workflow. | A bound artifact manifest, offline dependency handling, and recovery need implementation and tests. | First offline install implementation in either repository. |
| Linux run schema 2 records selected provider and installed deployment; Windows uses platform-specific state records. | Journals must preserve each platform's observable state and restoration method. | Any run-state migration or cross-platform recovery contract change. |
| Linux plans distinct RPM and Flatpak distributions of one product; current Linux catalog supports only the RPM installed slot. | Coexistence requires separate distribution, deployment, scope, and recovery identities, matching the shared product model without sharing installers. | First Linux Flatpak application operation or a Windows deployed-variant contract change. |

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

### RPM Fusion provider assessment, 2026-10-31

Compared Linux catalog, profile, and run-state schemas with Windows
`codex/ride-v3-migration` at `0ff139f` while assessing
[provider foundation batch 02](migrations/provider-foundation-02.md). A
disposable Fedora 44 VM verified both RPM Fusion release RPMs against the
Fedora-packaged signing keys. No Linux catalog operation or shared schema was
added; repository configuration ownership and recovery remain open. This is
still a high-risk Linux-only migration gap. Windows package and shared schema
contracts remain unchanged. Recheck after the Linux operation is implemented,
if Windows changes shared source selection, and before release-candidate
preparation. See the [signature evidence](acceptance/rpmfusion-bootstrap-trust.md).

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

The DNFutils fast-track choice is now recorded as a DNF5 replacement, backed
by read-only Fedora 44 Workstation checks for the `download` and
`config-manager` plugin commands. This uses the Linux platform's existing
DNF behavior and adds no shared catalog ID, profile contract, or run-state
field; Windows remains aligned at the shared client/schema boundary.

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
[codec bundle](migrations/provider-foundation-05.md) remains in v3.0
migration. The v2 wildcard and optional group operation will be decomposed
into explicit Linux RPM package operations. The first batch adds six
Fedora-only supported package rows and one opt-in Linux profile, accepted on
Fedora 44 Workstation x86_64. Windows has
no equivalent codec-bundle catalog rows in this revision; this changes no
shared source-selection, deployment, profile, journal, or recovery schema.
The next four Fedora good-family plugin operations and their opt-in profile
passed the declared Workstation lifecycle. Exact-target evidence found GTK and
Qt6 already installed, so those operations are installed-only one-way states
that profile removal preserves; Extras and Qt are reversible. The acquisition
and recovery handlers remain shared. The next six Fedora Multimedia group
GStreamer prerequisites now have explicit installed-only operations and an
opt-in profile; `gstreamer1-plugin-libav` replaces the unavailable v2 package
name. Their exact-target check asserts the pinned Workstation image baseline
and preserves all six through profile removal. This adds Linux catalog data,
not a shared schema or Windows installer contract. Review alignment again
after the remaining codec and Multimedia group operations are implemented.
The next six Fedora Workstation Multimedia group audio/video prerequisites
also passed exact-target plan, repeat, signature/file, status, and profile
removal checks as installed-only Linux package rows. None changed the shared
catalog, profile, or run-state schemas or the Windows installer contract.
Four additional codec runtime and OpenCV package rows then passed a Fedora 44
Workstation lifecycle; only OpenCV was newly installed, and the inverse removed
its 91 newly introduced package dependencies while preserving prior RPM
identities. This remains Linux Fedora-provider behavior with no shared schema
change. The final three PipeWire/WirePlumber prerequisites and conditional
eSpeak plugin also passed their declared Workstation lifecycle; eSpeak's new
RPM was removed cleanly and the existing packages remained. These Linux-only
package rows do not change the shared schema or Windows installer contract.
Recheck alignment when the RPM Fusion codec alternative and exact v2 wildcard
mapping are reconciled.
The
[Eza source batch](migrations/provider-foundation-08.md) keeps the Fedora RPM
and adds a distinct pinned user-local binary operation from the upstream
release. Both share product ID `eza` while using separate operation and
deployment identities. The Windows catalog has no Eza row in this revision,
so no Windows installer fact is inferred. Fedora 44 Workstation acceptance
passed for coexistence and independent removal. This is a Linux-native handler
implementation and does not change the shared catalog, profile, journal, or
lifecycle schemas. Recheck for a new portable product, target, or shared
lifecycle change, and before release review.

### Fedora Eza portable operation, 2026-11-01

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b`. Windows supports native
portable deployments but has no Eza product entry. Linux adds the pinned Eza
0.23.5 x86_64 GNU user-local operation beside the supported Fedora RPM. The
portable deployment passed disposable Fedora 44 Workstation install, repeat,
status, and remove checks while preserving the RPM. Both platforms retain
native handlers and separate operation identities; the Linux addition changes
no shared schema or lifecycle contract. Recheck on Eza version, target, or
coexistence changes and before release review.

### Fedora provider foundation batches 02, 06, and 07, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f`. The
[RPM Fusion repository](migrations/provider-foundation-02.md) and
[Security Lab group](migrations/provider-foundation-06.md) outcomes retain
their existing source-specific decisions. Batch 07 adds an operable opt-in
HandBrake CLI candidate from RPM Fusion, with a passed Fedora 44 Workstation
package lifecycle; its separate GUI/Flatpak path remains in H067. Linux uses
the Fedora-specific RPM Fusion provider and CLI package split. No Windows
repository source or installer fact is inferred from this Linux-only result.
The registered representation and deployment differences remain intentional;
no unexplained shared-contract drift was found. Recheck if the product split,
provider contract, or shared lifecycle behavior changes, or before release
review.

### Fedora provider foundation batches 09, 11, and 12, updated 2026-10-31

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` before resolving the
[Flathub remote](migrations/provider-foundation-09.md),
[Flatpak runtime](migrations/provider-foundation-11.md), and
[Snapd](migrations/provider-foundation-12.md) source outcomes. Linux adds the
supported `package.flatpak` RPM installation and candidate `package.snapd`
runtime on Fedora 44 Workstation. Both use the existing DNF handler,
installed-only state, and no inverse; opt-in profiles add no shared run-state
or catalog schema change. Snap acceptance observed partial host confinement
because AppArmor is not enabled; this Linux-specific security behavior is
queued as H034. Windows has no matching Flatpak runtime, Flathub, or Snapd
operation in this revision. The Linux package sources and targets remain
platform-specific facts. No unexplained shared-contract drift was found.
Recheck if Windows adds a matching runtime, either platform changes ownership
or recovery semantics, or at release review.

### Fedora forensic isolated batch 01, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` before the
[active forensic tool batch](migrations/forensic-isolated-01.md).
Windows has a supported `package.cyberchef` offline portable ZIP with
notice preservation and exact rollback; Linux's v2 ZIP/launcher lacks
pinned artifact and owned-path handling, so its source outcome is explicitly
non-runnable in Linux v3.0. This is an intentional platform handler and
acceptance difference, not a shared product or license disagreement. Windows
also has `package.exiftool` as an unaccepted pinned Windows x64 portable
candidate; Linux uses the same `exiftool` product identity with a supported
Fedora-signed RPM and a separately scoped Workstation VM lifecycle. The
distribution, provider, destination, and recovery evidence are platform
specific, as the shared package-deployment decisions require. No Linux
profile or run-state schema changed; no unexplained shared-contract drift
was found. Recheck when Linux gains portable artifacts, either product's
source or license facts change, or before release review.

### Fedora forensic isolated batch 02, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` for the
[Volatility and former CERT batch](migrations/forensic-isolated-02.md).
Linux narrowed the existing `package.volatility3` candidate to the
Workstation edition; this changes its source signature. The owner previously
confirmed no non-disposable v3 runs, and the disposable VM pilot used the
new target declaration. Windows has no Volatility 3 catalog operation in
this revision, so no shared installer fact is inferred. Windows has an
accepted `package.autopsy` MSI lifecycle; Linux's publisher-signed ZIP and
Java dependencies are a separate, unaccepted deployment. This is an
intentional platform source, handler, and evidence difference, not a
product-identity conflict. No profile or run-state schema changed and no
unexplained shared-contract drift was found. Recheck if Linux adds a
portable Autopsy handler, Windows adds Volatility 3, shared product facts
change, or release review begins.

### Fedora Autopsy and Volatility 2 follow-up, 2026-11-01

The Fedora Autopsy path is now the Sleuth Kit Labs Snap Store package and is
tracked separately as a high-risk Linux candidate. Fedora 44 acceptance
observed publisher-granted connections for `block-devices`, `dm-crypt`, and
`fuse-support`; the Snap runtime and those interfaces do not transfer to
Windows. Windows' existing MSI path remains a separate platform-native
deployment. The retained Linux Volatility 2 outcome is an opt-in user-local
PyPy 2.7 plus pinned upstream source bundle, accepted for the core CLI on
Fedora 44 Workstation. Windows has no corresponding Volatility 2 operation in
the reviewed development branch. Linux added an operation-specific handler
and profile; shared catalog, profile, and journal contracts did not change.
Recheck these differences if the source path changes, Windows adds Volatility
2, or release review begins.

### Fedora forensic isolated batch 03, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` for the
[Binwalk, autopep8, and legacy script batch](migrations/forensic-isolated-03.md).
Windows has no corresponding Binwalk, autopep8, Dumpzilla, or Macvendor
catalog/profile operation at this revision. Linux adds only two Fedora RPM
operations using the existing installed deployment, `fedora-rpm` source,
DNF handler, and run journal. The standalone Macvendor replacement and
Dumpzilla retirement add no Linux operation or executable fallback. No
shared package source resolution, recovery, catalog, profile, or run-state
contract changed, and no unexplained drift was found. Recheck if Windows
adds any of these products, Linux adds owned script deployment, either
schema/handler changes, or release review begins.

### Fedora forensic isolated decisions 04-06, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` before the isolated
[BulkExtractor](migrations/forensic-isolated-04.md),
[NetworkMiner](migrations/forensic-isolated-05.md), and
[email-header analyzer](migrations/forensic-isolated-06.md) decisions.
Windows has a reviewed `package.networkminer` portable ZIP, with the same
product identity and GPL-2.0 source fact but Windows-specific runtime,
destination, and capture-preserving recovery. Linux has no equivalent
portable handler or data inverse, so its active v2 outcome remains
non-runnable in v3.0. Windows has no corresponding BulkExtractor or email
header analyzer catalog operation in this revision. These decisions add no
Linux operation, profile, or run-state field. The platform deployment and
evidence difference is intentional, and no unexplained shared-contract
drift was found. Recheck at first Linux portable/service implementation,
product fact change, or release review.

### Fedora publisher application batches 01-02, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` before the
[AppImageLauncher](migrations/publisher-apps-01.md) and
[VeraCrypt](migrations/publisher-apps-02.md) resolutions. Windows has no
matching catalog operation for these products at this revision. The Linux
source outcomes add no new operation, profile selection, or run-state field;
the registered absent publisher-RPM and portable-deployment handlers remain
intentional platform gaps. No shared product fact or package contract is
changed and no unexplained drift was found. Recheck on a publisher handler,
Windows product addition, or release review.

### Fedora publisher application batches 03-04, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` for the
[VS Code/Brave](migrations/publisher-apps-03.md) and
[Firefox extension policy](migrations/publisher-apps-04.md) outcomes.
Windows has an accepted `package.vscode` x64 user-setup EXE. It shares
Visual Studio Code product identity but not Linux's system RPM repository,
key, scope, or inverse; those deployment differences are intentional.
Windows has no matching Brave or Firefox extension-policy catalog row in
this revision. Linux has corrected the kept Firefox outcome from a completed
standalone replacement to an open v3 migration gap; it adds no catalog,
profile, or run-state field in this change. No shared contract changed and no
unexplained drift was found. Recheck when Linux adds the policy handler,
Windows adds a corresponding product, or release review begins.

### Fedora publisher application batch 05, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` for the
[video downloader and GNOME monitoring batch](migrations/publisher-apps-05.md)
and the isolated [GNOME user-extension decision](migrations/publisher-apps-17.md).
Windows has no corresponding `youtube-dl`, GNOME applet, hardware sensors,
or GNOME user-extension operation in this revision. Linux's three new
catalog rows use the existing Fedora RPM source, installed deployment,
DNF handler, and run journal; the opt-in monitoring profile uses the
existing profile schema. The broad GNOME extension source is non-runnable
and adds no handler. No shared product, source resolution, ownership, or
recovery contract changed, and no unexplained drift was found. Recheck if
Windows adds a corresponding product, Linux implements user extension
state, or release review begins.

### Fedora publisher application batches 06-08, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` for the
[Bitwarden portable decision](migrations/publisher-apps-06.md),
[Solaar/ACPI and VM guest tools](migrations/publisher-apps-07.md), and
[YubiKey Manager handoff](migrations/publisher-apps-08.md). Windows has no
matching Bitwarden AppImage, Solaar, ACPI, VM guest-tools, or YubiKey Manager
catalog row in this revision. Linux's Solaar/ACPI rows use the existing
signed Fedora RPM, system scope, DNF, and journal contracts; its opt-in
profile uses the existing schema. The two high-risk publisher outcomes remain
non-runnable here. Linux now expresses guest tools as explicit QEMU/SPICE and
VMware RPM profiles rather than DMI-driven detection; these use the existing
catalog, profile, and run-state schemas. These platform deployments and
decisions are intentional; no unexplained shared-contract drift was found.
Recheck if Windows adds a corresponding product or release review begins.

### Fedora publisher application batch 06 implementation, 2026-11-01

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` after implementing the kept
[Bitwarden AppImage](migrations/publisher-apps-06.md). Windows has no
matching Bitwarden AppImage deployment. Linux adds one pinned portable
AppImage handler and opt-in profile; both use the existing operation and run
schemas, with no new shared field or Windows installer. Linux leaves the
Bitwarden profile/vault files and separate RPM deployment outside the owned
AppImage file inverse. This platform-specific deployment is intentional.
Recheck if Windows adds an AppImage deployment, Bitwarden changes its Linux
release manifest, or the shared package lifecycle changes.

### Fedora publisher application batch 09, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` for the
[file-manager and publisher review](migrations/publisher-apps-09.md).
Windows has `package.powershell` for a Windows 11 machine MSI. It shares
PowerShell 7 product identity with the v2 Linux function, but the Windows
MSI, machine inventory, and compensating uninstall do not establish an
owned Fedora RPM repository/key or Fedora support. Linux's PowerShell
outcome is non-runnable pending that separate deployment evidence. Windows
has no corresponding GNOME Commander, Midnight Commander, Teams Linux
client, WoeUSB, Etcher, or Sonos catalog row at this revision. The two
Linux file-manager candidates use the existing Fedora RPM, DNF, target,
and run journal contracts; the profile uses schema 1. No shared field or
product fact was changed, and no unexplained shared-contract drift was
found. Recheck if either platform adds a corresponding product deployment,
the PowerShell source contract changes, or release review begins.

### Fedora publisher application batch 10, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` for the
[Arduino, Atom, Discord, Joplin, and Vivaldi review](migrations/publisher-apps-10.md).
Windows has `package.joplin` as a current-user EXE and `package.discord` as
a pinned current-user EXE. Their product identities and Joplin AGPL or
Discord proprietary license facts remain aligned, but their Windows
installers and profile-preserving uninstall evidence do not prove a Linux
AppImage or publisher RPM inverse. Linux now has pinned AppImage operations
for Arduino IDE and Joplin and a digest-pinned Discord RPM candidate with
metadata checks; no platform installer is shared. Windows has no matching Arduino IDE,
Atom, or Vivaldi catalog row in this revision. No Linux catalog, profile, or
run-state schema fields changed in this batch; no unexplained shared-contract
drift was found. Recheck if a source contract changes, Windows changes the
shared product facts, or release review begins.

### Fedora publisher application batch 11, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` for the
[browser and media review](migrations/publisher-apps-11.md). Windows has
`package.chrome` as a pinned enterprise MSI with Windows 11 and Server
2025 lifecycle evidence. Chrome product identity and publisher terms are
shared facts, but that MSI and browser-profile evidence do not establish
an owned Fedora RPM repository/key or Linux inverse. Windows has no
matching Opera, Edge Linux, Spotify, Clementine, or EasyEffects catalog
operation at this revision. Linux's Clementine and EasyEffects candidates
use the existing signed Fedora RPM, DNF, Workstation target, and run-journal
contracts; each curated profile uses schema 1. The publisher browser and
Spotify outcomes add no handler. No unexplained shared-contract drift was
found. Recheck if Linux adds external repository support, Windows changes
the Chrome product facts, or release review begins.
Opera was subsequently excluded from the Linux v3 scope by owner decision;
this historical comparison does not reopen it.

### Fedora publisher application batches 12-16, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` for the
[Bitwarden RPM](migrations/publisher-apps-12.md),
[Projecteur](migrations/publisher-apps-13.md),
[YubiKey Personalization GUI](migrations/publisher-apps-14.md),
[Xmind](migrations/publisher-apps-15.md), and
[Cheat](migrations/publisher-apps-16.md) source outcomes. Windows has no
matching catalog rows in this revision. Linux's Projecteur and Cheat rows
use signed Fedora RPM, existing DNF and journal behavior, and the
Workstation-only target; the Spotlight profile uses schema 1. The
Bitwarden, archived YubiKey, and Xmind decisions add no handler or state
field. No unexplained shared-contract drift was found. Recheck if Windows
adds corresponding product facts, Linux implements an external publisher
deployment, or release review begins.

### Fedora Bitwarden RPM implementation, 2026-11-01

Linux now has a distinct `package.bitwarden-rpm` operation beside the
previously implemented portable AppImage. It reuses schema 3, profile schema
1, and run schema 2 and adds a Fedora-only pinned RPM handler. Windows has no
matching RPM deployment; its installer remains separately owned. The RPM and
AppImage have independent lifecycle state while preserving shared Bitwarden
vault files. This Linux deployment difference is intentional; recheck if
Windows adds a publisher RPM or Bitwarden changes release asset verification.

### GNOME boolean user-setting batch, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` for the
[GNOME boolean review](migrations/desktop-user-boolean.md). Windows has no
corresponding GNOME schema/key operations. The Linux handler adds five fixed,
per-user boolean settings with effective `enabled` or `disabled` observation;
the existing journal and `exact-state` preflight record and restore that
effective value. Windows uses platform-specific settings and recovery
records, so neither client shares GNOME keys or installers. The opt-in Linux
profiles use schema 1 and leave `default` unchanged. The Linux journal does
not distinguish an unset dconf default from an explicit equal value; H018
tracks that Linux recovery limit before support promotion. No unexplained
shared-contract drift was found. Recheck if Windows adds a corresponding
user-setting contract, Linux changes run-state representation, or release
review begins.

### Remaining desktop and user-state decisions, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` for the
[remaining desktop review](migrations/desktop-user-remaining.md). These
decisions add no Linux catalog handler, profile, or run-state field. Windows
has a Chrome package deployment but its machine MSI and Windows policy do
not establish an owned Linux browser or Linux initial-preferences inverse.
The existing Linux Firefox policy helper remains an explicit standalone
workflow, while its three-file v2 preference overwrite is unresolved as an
owned security policy. GNOME shortcuts, favorites, dconf state, Bash user
files, and iBus bindings are Linux user-state ownership questions, not
Windows installer behavior. No unexplained shared-contract drift was found.
Recheck if either client adds a shared browser preference or user-state
recovery contract, and before release review.

### Fedora core system decisions, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` for
[host identity, DNF tuning, update, and Docker](migrations/system-security-core.md).
These Linux decisions add no runnable operation or shared field. Windows
package and machine-setting records do not provide Fedora DNF configuration,
Linux host naming, or Docker repository and volume recovery. Host identity
remains private input on both platforms. No unexplained shared-contract drift
was found. Recheck if a cross-platform update action, Docker product model,
or parameterized host-setting contract is added, and before release review.

### Fedora network package bundle preflight, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` for the
[network package split](migrations/system-security-network-tools.md). Both
catalogs identify Wireshark and PuTTY as the same products. Windows Wireshark
is a pinned machine MSI candidate without bundled Npcap enrollment; Linux
selects Fedora's signed RPM and does not enable capture privileges or start
a capture. Windows PuTTY is an accepted standalone portable file; Linux uses
Fedora's installed RPM. Their deployment, artifact, destination, and inverse
contracts are intentionally platform-specific. Other network tools have no
matching Windows catalog row in this revision. Linux adds no shared schema,
source fallback, or journal field. Recheck if either product's shared facts
or source contract changes, or before release review.

### High-risk Linux system disposition preflight, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` for the
[VPN, storage, virtualization, and sudo review](migrations/system-security-risk-decisions.md).
The Linux decisions add no runnable handler or shared field. Windows has a
Docker Desktop candidate, which is a different product and service/data
contract from Linux Docker Engine; no Linux Docker operation is inferred.
The Linux v2 ExpressVPN, WireGuard, OpenVPN profile, VMware module, LUKS,
and sudoers functions have platform-specific private state or destructive
inverses. Neither Windows package acceptance nor shared command vocabulary
proves their Linux recovery. No unexplained shared-contract drift was found.
Recheck if a shared product identity or private-state contract is proposed,
or before release review.

### Generic Server and resolution decisions, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` for the
[generic Server decisions](migrations/generic-server-decisions.md),
[shared Python pip package](migrations/generic-server-python.md), and
[screensaver resolution](migrations/resolution-decisions.md). Fedora's
`python3-pip` package adds only the Server edition target to the existing
Linux DNF operation; it does not add a shared installer or journal field.
The server service, VPN, SSH, lock setting, and host identity decisions add
no runnable row. Windows package and machine-setting behavior cannot stand
in for Linux DNF5, systemd, GNOME, or server policy recovery. The Windows
product, package-source, profile, and saved-run schemas do not require a
change for these Linux decisions. Recheck if a cross-platform product or
state contract is proposed, and at release review.

### Fedora Server Selenium Python bindings, 2026-11-02

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` for the kept Server Selenium
binding outcome. Linux uses Fedora's signed `python3-selenium` RPM in an
opt-in Server profile; browser, driver, Grid, and test-code deployment remain
outside the operation. Windows has no matching Fedora RPM fact, and this adds
no shared catalog, profile, or journal field. No cross-platform installer or
browser lifecycle is implied. Recheck if a shared Selenium product or browser
deployment contract is proposed, or before release review.

### Package-only security batch and final v3.0 alignment, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `4c90577` for the
[VPN-plugin and KeePassXC package review](migrations/system-security-packages.md)
and [SmartMonTools failure](migrations/system-security-smartmontools.md).
The Windows branch advanced from `0ff139f` only with read-only public-IP
and MAC-vendor scripts, their tests, and docs; its catalog, profile, and
saved-run contracts did not change. Windows has no matching catalog product
for these five Fedora RPM operations. Linux's signed RPM source, package-only
scope, Workstation target, and DNF journal stay platform-specific. Linux
neither shares a VPN credential or encrypted-vault state contract with
Windows nor exposes smartd as an accepted package-only operation. The
remaining v2 source decisions add no shared contract fields. No unexplained
catalog, profile, or run-state drift was found at this comparison. Recheck
before a v3 tag if the Windows branch advances or a shared product or state
contract is proposed.

### Fedora Server qBittorrent package preflight, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` before adding
`package.qbittorrent-nox`. Since the prior Windows review at `4c90577`, its
catalog and default profile gained Windows-specific settings, while the
catalog schema version remains 1 and no run-state module changed. Windows
has no qBittorrent product row. The Linux row uses the existing Fedora RPM
provider, package-only system scope, `installed`/`local-installed` metadata,
and unchanged package journal. It does not transfer the server service,
firewall, user, credentials, or downloads from `network-devices`. No shared
package, profile, or run-state contract change is introduced. Recheck if
Windows adds qBittorrent, either client changes installed-deployment
identity, or the server service is migrated.

The package-only Fedora 44 Server VM lifecycle passed under QEMU TCG on
2026-10-30. Promotion changed only the Linux catalog status and added the
`server-qbittorrent-package` opt-in profile under the existing profile schema.
The [acceptance record](acceptance/package.qbittorrent-nox.md) contains exact
target and recovery evidence. No Windows contract change is needed; recheck
the triggers above before expanding scope.

### Fedora yt-dlp downloader preflight, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` before adding the maintained
Fedora `yt-dlp` alternative. Windows has no `yt-dlp` or `youtube-dl` product
row. The new Linux operation uses the existing DNF handler, `fedora-rpm`
source, installed deployment, and run journal. `package.youtube-dl` remains
a separate published ID. No schema or shared state behavior changes; recheck
if either platform introduces downloader variants, changes package source
selection, or changes run-state identity.

### Fedora UnfURL isolated Python preflight, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` before adding the UnfURL
user environment. Windows has no corresponding UnfURL product row. Linux
reuses its existing `python-venv` handler class and `pypi-venv` source, with
an allowlisted operation ID and a separate owned destination. No shared
catalog, profile, or run-state field changes. The Linux user venv, Python
wheel hashes, and exact owned inverse are platform-specific. Recheck if
Windows adds UnfURL or either client changes installed-deployment identity,
source selection, or run-journal recovery semantics.

The pinned Fedora 44 Workstation VM lifecycle passed under QEMU TCG. The
`forensic-unfurl` profile uses the existing profile schema and selects only
the new opt-in candidate. The [acceptance record](acceptance/package.dfir-unfurl.md)
shows the exact user-environment recovery. No unexplained Windows contract
drift was found; the Linux-specific runtime remains a deliberate difference.

### Fedora archive `unrar` preflight, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` before adding Fedora's
`unrar` wrapper. Windows has a `package.7zip` product selected by its default
profile, but no `unrar` or `unar` row. Linux retains its existing
`package.7zip` and `package.unar` IDs and uses a distinct RPM-backed
`package.unrar` ID to restore the v2 command choice. Its proposed opt-in
archive profile reflects the small Linux `default` profile. No shared
schema, installed-deployment identity, source-selection, or run-journal
behavior changes. Recheck if Windows adds a RAR command or either client
changes the 7-Zip product contract.

The Fedora 44 Workstation package lifecycle passed under QEMU TCG. The
`archive-tools` opt-in profile uses the existing profile schema and selects
only the accepted 7zip and unrar package operations. The
[acceptance record](acceptance/package.unrar.md) shows complete RPM inventory
recovery, a passing profile smoke, and preservation of pre-existing 7zip. No
unexplained shared Windows contract drift was found.

### Fedora ASN pinned-script preflight, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` before adding the ASN tool.
Windows has no ASN product row or matching deployment. Linux adds an
allowlisted `pinned-script` handler with fixed upstream commit, observed
script and license hashes, a user-owned destination, and separate Fedora
RPM prerequisites. The two opt-in profiles retain profile schema 1; the
run journal and its source signature version remain unchanged. New hash
fields are Linux acquisition metadata for this specific script, while
Windows uses its own artifact validation and recovery paths. This is an
intentional platform difference, with no shared product-state claim.
Recheck if Windows adds ASN, either client changes installed-deployment
identity or run-state recovery, or Linux generalizes the script handler.

The pinned Fedora 44 Workstation VM lifecycle passed under QEMU TCG. The
[acceptance record](acceptance/package.asn.md) covers the separate system
and user profiles, exact script and notice hashes, and owned user inverse.
The profile and run-state formats did not change. No unexplained shared
Windows contract drift was found; the Linux-specific RPM and script paths
remain deliberate differences.

### Fedora CyberChef offline archive preflight, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` before adding Linux
`package.cyberchef`. Both clients use the `cyberchef` product identity and
install the official offline ZIP, retain bundled notices, preserve user
recipes, and do not launch a browser during apply. Windows declares a
machine-scoped `portable` variant selected from the latest release API;
Linux pins v11.5.0 and its release API digest, then owns a system desktop
integration under the current `installed`/`local-installed` slot. The
distribution and acquisition difference is intentional because Linux has
no portable deployment selector yet. It does not change the shared run
schema or product behavior contract. Recheck when either platform changes
CyberChef source selection, adds a second deployment, or shares saved-run
identity across platforms.

The pinned Fedora 44 Workstation VM lifecycle passed under QEMU TCG. The
[acceptance record](acceptance/package.cyberchef.md) covers ZIP and notice
verification, headless offline browser startup, the desktop link, and owned
recovery. Linux's installed deployment remains a deliberate platform
difference; no unexplained shared Windows contract drift was found.

### Fedora Chepy isolated Python preflight, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` before adding Linux
`package.chepy` and `package.python3.12`. Windows has no Chepy or Python
3.12 catalog operation. Linux selects a Fedora RPM for the interpreter and
a hash-pinned PyPI source distribution in a user venv for the Chepy CLI.
This is a Linux-only capability and source path. The existing catalog,
profile, and run schema versions remain unchanged; the Chepy source digest
is bound to its Linux run signature. Recheck if Windows adds Chepy, either
platform changes product or deployment selection, or a shared run-state
contract is revised.

The pinned Fedora 44 Workstation VM lifecycle passed under QEMU TCG. The
[acceptance record](acceptance/package.chepy.md) covers the signed Python
3.12 RPM, exact Chepy sdist digest, isolated CLI startup, repeat, restore,
and explicit removal. No unexplained shared Windows contract drift was found.

### Fedora VMFS6 reader source probe, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` while reviewing the kept
VMFS access capability. Windows has no VMFS catalog or profile entry.
The Linux probe changed only migration planning; no executable operation,
profile, or shared data contract changed. A future Linux image reader would
be a platform-specific acquisition and storage-safety path. Recheck
Windows product identity and shared run-state behavior before adding it
to the Linux catalog or claiming cross-platform alignment.

### Fedora Firefox forensic successor preflight, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` while separating the kept
Firefox analysis capability from the discontinued Dumpzilla script.
Windows has no matching Dumpzilla or browser-forensic operation. This
review changes no executable Linux catalog, profile, or run contract.
A future successor must preserve seeded browser data and keep secret
output explicit; revisit product identity and shared recovery behavior
before adding it to either platform.

### Fedora Terminator package preflight, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` before adding
`package.terminator`. Windows has no Terminator operation. The Linux row
uses the existing single installed `fedora-rpm` deployment, DNF handler,
explicit operation ID, and run-state recovery contract. The v2 iBus hotkey
is a separate per-user setting. The subsequent Linux
`setting.ibus-emoji-hotkey` records the exact dconf user override in the
run journal and restores it on the intended account, independently of the
RPM. Windows has no matching setting. Linux catalog schema 3 and profile
schema 1 gained a fixed local handler and one opt-in user profile; run schema 2
uses its existing string observation field without a version change. No
shared product or lifecycle semantics changed, and no unexplained drift was
found. Recheck if either schema changes, Windows adds this product or a
similar user-setting recovery contract, or a release candidate is prepared.

### GNOME string value batch preflight, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` before adding GNOME region
and button-layout choices. Windows has no matching GNOME settings. Linux
adds an optional, typed profile `value` for its fixed string-setting handler;
the selected value is copied into the private run journal and source
signature. Existing package and boolean-setting profiles omit it and retain
their behavior. Windows uses platform-specific PowerShell data and recovery
records; the common contract remains explicit desired values and restoration
from the recorded selection. The optional Linux field and dconf user override
are intentional platform details. Recheck when either profile or run schema
changes, Windows adds a comparable configured setting, or a release
candidate is prepared.

### Fedora UPower threshold batch preflight, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` before adding the kept 15-
and 20-percent UPower settings. Windows has no UPower operation or equivalent
Linux battery-policy file. Linux reuses its optional profile `value` field
and selected-value run signature from the GNOME string batch, then adds a
fixed, system-scoped UPower drop-in handler. The operation ID, desired state,
selected value, observed prior state, and exact restore remain explicit data;
the numbered `/etc/UPower/UPower.conf.d` destination is platform-specific.
No Windows catalog, profile, or run-state behavior is changed, and no
unexplained shared contract drift was found. Recheck if either platform adds
battery-policy management, changes selected-value journaling, or prepares a
release candidate.

### Fedora OpenConnect package batch preflight, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` before replacing the v2
OpenConnect source build. Windows has no matching OpenConnect deployment or
VPN profile operation. Linux adds three Fedora RPM rows and one opt-in
profile using the existing `dnf-package`, signed-source, and
remove-new-install contract. Package IDs name the client, routing helper,
and GNOME editor separately; no shared profile or run-state schema changes.
VPN identities, credentials, and connection state remain outside this
package batch. No unexplained Windows contract drift was found. Recheck
if either platform adds VPN profile management, package-source semantics
change, or a release candidate is prepared.

### Fedora Server Tailscale package batch, 2026-11-02

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` before adding `package.tailscale`. Windows
has no matching Fedora repository or Tailscale package operation. Linux reuses
the existing installed-RPM and run-state contracts, adds a publisher repository
with its signing-key fingerprint and signed metadata checks, and makes no
shared schema or run-state change. The package-only operation does not
authenticate a node, enable Tailscale, select routes, or change firewall
policy. The disposable Fedora 44 Server result and service/state boundary are
recorded in [Tailscale acceptance](acceptance/package.tailscale.md). Recheck
if Windows adds a Tailscale package operation, the publisher source/signing
contract changes, or Linux adds node identity or route management.

The Fedora 44 Workstation package lifecycle passed before promotion. Changing
these three rows from candidate to supported adds only status and acceptance
links; the Linux source, handler, target, profile order, and run-state schema
stay the same. Windows still has no matching OpenConnect operation. Recheck
the package and connection contracts before any broader VPN behavior ships.

### Fedora WireGuard tools and local key pair, 2026-10-31

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` before adding the WireGuard RPM and local
key-pair operation. Windows has no matching WireGuard operation. Linux reuses
the existing DNF contract and adds a Linux-only exact-state handler with a
dedicated ownership marker; no shared schema or run-state field changes were
made. The Fedora 44 Workstation VM passed the owned key-pair lifecycle before
promotion. Recheck if Windows adds key management, Linux changes secret
journaling or ownership semantics, or interface and peer management expands
the shared VPN contract.

### Fedora system Flathub remote, 2026-10-31

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` before adding the system Flathub remote.
Windows has no matching Flatpak remote or app deployment operation. Linux
adds a setting handler and an owned marker under RIDE's system state; no shared
schema or run-journal fields change. Fedora 44 Workstation acceptance passed
before marking the operation an opt-in candidate. Recheck if Windows gains
Flatpak deployment behavior or Linux changes remote ownership, GPG, or
recovery semantics.

### Fedora RPM Fusion source lifecycle, 2026-10-31

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with the
Windows v3 contract documented above before adding the RPM Fusion source
operation. Windows has no RPM Fusion repository or RPM trust-store operation.
Linux adds a Fedora-specific custom handler and an opt-in profile; it does not
add shared profile values, journal fields, or alter common package source
selection. The repository lifecycle, focused trust and rollback failures, and
the `gstreamer1-plugins-bad-freeworld` package pass Fedora 44 Workstation
acceptance. Linux pins this
Fedora-specific candidate to `rpmfusion-free-updates` while retaining Fedora's
separate `bad-free` operation; Windows has no matching RPM provider or
GStreamer package source. This adds no shared profile values, journal fields,
or common package-source behavior. Recheck if Windows adds package-source
trust management, Linux changes ownership journaling, or before release
review.

### Fedora Multimedia fixed-list update, 2026-10-31

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` while adding the fixed-list
DNF5 Multimedia update operation. Windows has no Fedora Multimedia group or
DNF5 package-upgrade provider. Linux adds one Fedora 44 Workstation system
operation and one opt-in profile state; shared operation IDs, profile data,
and run-journal fields remain unchanged. The non-reversible `current` state is
documented in Linux only. A disposable Fedora 44 Workstation run passed: the
transaction upgraded 44 RPMs and installed one weak dependency without losing
baseline name/architecture identities. Recheck if Windows adds comparable
package-set updates or Linux changes the shared profile or journal contracts.

### Security Lab opt-in package profile batch 06A, 2026-10-31

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b`. Linux adds an opt-in profile
that composes six existing Fedora RPM operation IDs; the package handlers and
run-state contract are unchanged. Windows has no Fedora DNF Security Lab
group or matching Linux package operations. The profile does not alter shared
catalog, profile, or journal schemas, nor any Windows installer behavior.
Recheck when further Fedora group members are added, either platform changes
package ownership semantics, or before release review.

### Security Lab network analysis profile batch 06B, 2026-10-31

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b`. Linux adds one Fedora RPM
operation for `wireshark-cli` and composes it with four existing package IDs
in a candidate-gated opt-in profile. Windows has no Fedora Security Lab group
or matching Linux package IDs. No shared schema, lifecycle, or Windows
installer behavior changes. Recheck when further Fedora group members are
added, if package removal ownership changes, or before release review.

### Security Lab forensic recovery profile batch 06C, 2026-10-31

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b`. Linux composes three existing
Fedora RPM IDs in a new opt-in profile; the catalog handlers and run-state
contract are unchanged. Windows has no Fedora Security Lab group or matching
Linux package IDs. The profile performs package installation only and does
not open evidence images. Recheck when another Fedora group member is added,
if package recovery changes, or before release review.

### Security Lab network diagnostics profile batch 06D, 2026-10-31

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b`. Linux composes four existing
Fedora RPM IDs in an opt-in profile; package handlers and the run-state
contract are unchanged. Windows has no Fedora Security Lab group or matching
Linux package IDs. No shared contract or Windows installer behavior changes.
Recheck if another Fedora group member is added, package recovery changes, or
before release review.

### IRC package alternatives after native RPM batch 03, 2026-10-31

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b`. Linux's accepted HexChat RPM
operation remains available as an opt-in candidate. Fedora Konversation and
Polari alternatives were tested but not retained because their apps fail to
start on the pinned Fedora 44 image; their failure records remain in Linux
acceptance docs. Windows has separate application acquisition facts and no
Linux RPM or Flathub deployment is shared. No common schema or Windows
installer behavior changes. Recheck after Halloy VM acceptance, if shared
package-source or profile recovery contracts change, or before release review.

### Halloy Flathub app lifecycle, 2026-10-31

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b`. Linux adds an operable opt-in
`system-flatpak` deployment with a fixed `org.squidowl.halloy` identity and
Flathub system-GPG verification. Its Fedora 44 Workstation lifecycle passed;
per-user app data remains after package removal. The profile remains separate
from the legacy HexChat RPM deployment. Windows has no Flathub provider or
matching IRC operation; shared package deployment dimensions and run
journaling remain unchanged. No Windows behavior or shared contract changed.
Recheck if Flatpak deployment selection or recovery becomes shared.


### LibreSpeed CLI user-local pinned binary, 2026-10-31

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with Windows
`codex/ride-v3-migration` at `d91c44b`. Linux adds the opt-in user-local
`package.librespeed-cli` operation for Fedora 44 Workstation x86_64. It pins the
publisher archive and checksum-manifest digests, retains the license, and owns
its `~/.local` files and inverse. The disposable VM lifecycle passed. Windows
has no matching Linux binary acquisition or Fedora target; shared package
identity and lifecycle schemas are unchanged. Recheck if Windows adds a
comparable user-local Linux binary deployment, the shared verification model
changes, or before release review.

### Fedora Required package capabilities, 2026-10-31

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with Windows
`codex/ride-v3-migration` at `d91c44b`. Linux preserves the seven v2
`InstallRequired` RPM capabilities as distinct Fedora 44 Workstation x86_64
operations in an opt-in profile. Their installed-only state reflects the legacy
function's one-way behavior and avoids removal of essential packages. The
profile does not change the small base profiles. Windows retains its native
package facts and does not share Fedora RPM names or installers. Shared product
identity and journal behavior are unchanged. Recheck if package inverse policy,
Fedora target support, or the shared package contract changes, and before
release review.

The Required-tools profile later passed a disposable Fedora 44 Workstation run.
DNF installed GCC and four dependencies, then upgraded eight pre-existing RPMs
without losing any name/architecture identity. Linux records that observed
transaction in the operation acceptance evidence and tracks transaction-impact
review in H035. This Fedora-specific package behavior adds no Windows package
facts and changes no shared command or run-state contract.

### Generic Server Required RPM capabilities, 2026-10-31

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b`. Linux maps the generic Server
`InstallRequired` bundle to eleven Fedora 44 Server x86_64 package operations
in two opt-in profiles. Existing `package.git` and `package.wget` operations now
include the tested Server target; a Server-only installed-only nano ID
preserves the v2 one-way behavior without changing Workstation `package.nano`.
Windows retains its native package facts and does not share Fedora RPM names
or installers. Shared profile, catalog, and journal schemas are unchanged. The
VM evidence records Fedora's open-vm-tools service presets and six DNF upgrades
under H035; H036 tracks the absent-package firewalld scenario because the pinned
Server image already included an active firewalld package. Recheck if
package inverse policy, service-preset behavior, or the shared package contract
changes, and before release review.


### Security Lab provider batch 06E preflight, 2026-10-31

Compared Linux `codex/ride-v3-migration` at `d91c44b` with Windows
`codex/ride-v3-migration` at `d91c44b` for the Fedora RPM operations
`package.bmon`, `package.fping`, `package.iftop`, `package.lnav`, and
`package.nload`. The shared catalog/profile/run-state schemas and installed
package lifecycle are unchanged: Linux adds Fedora-only product metadata and
one curated opt-in profile. No Windows package facts or installer behavior
apply to this batch. The Fedora 44 Workstation lifecycle evidence is recorded
in [Security Lab network utilities acceptance](acceptance/security-lab-network-utilities.md).
Review again if a shared package field, source-selection rule, or recovery
contract changes.


### Security Lab provider batch 06F preflight, 2026-10-31

Compared Linux `codex/ride-v3-migration` at `d91c44b` with Windows
`codex/ride-v3-migration` at `d91c44b` for the Fedora RPM operations
`package.httpie`, `package.iperf`, `package.irssi`, and `package.socat`. The
shared catalog/profile/run-state schema and lifecycle behavior are unchanged;
Linux adds Fedora-specific package metadata and an opt-in profile. No shared
Windows installer fact applies. The dependency upgrade and recovery boundary
are recorded in [the 06F acceptance report](acceptance/security-lab-network-clients.md).
Review again if package-source selection or shared recovery semantics change.


### Security Lab provider batch 06G preflight, 2026-10-31

Compared Linux `codex/ride-v3-migration` at `d91c44b` with Windows
`codex/ride-v3-migration` at `d91c44b` for `package.dnsenum`,
`package.dnstracer`, `package.dnstop`, and `package.fpdns`. Linux adds Fedora
RPM metadata and a profile; the shared schema, provider choice, package
detection, and restore contracts are unchanged. The DNF Perl dependency updates
and their retention after restore are documented in
[06G acceptance](acceptance/security-lab-dns-tools.md). Review if the shared
package or recovery contract changes.


### Security Lab provider batch 06H preflight, 2026-10-31

Compared Linux `codex/ride-v3-migration` at `d91c44b` with Windows
`codex/ride-v3-migration` at `d91c44b` for `package.arp-scan`,
`package.argus-clients`, `package.dnsmap`, and `package.nmbscan`. Linux adds
Fedora RPM metadata and an opt-in profile; the shared catalog, profile,
provider, and run-state contracts are unchanged. No Windows installer facts
apply. The Fedora 44 Workstation lifecycle and Perl dependency upgrades are
recorded in [06H acceptance](acceptance/security-lab-network-discovery.md).
Review if shared package or recovery semantics change.


### Security Lab provider batch 06I preflight, 2026-10-31

Compared Linux `codex/ride-v3-migration` at `d91c44b` with Windows
`codex/ride-v3-migration` at `d91c44b` for `package.httping`,
`package.httpry`, `package.tcpflow`, and `package.tcpick`. Linux adds four
Fedora-only RPM operations and an opt-in profile; catalog, profile, provider,
and run-state semantics are unchanged. The active use of these utilities can
send requests or inspect traffic; the package lifecycle and acceptance probes
do not. Their supported Fedora 44 Workstation lifecycle passed and is recorded
in [06I acceptance](acceptance/security-lab-network-traffic.md). No Windows
installer facts apply. Review if a shared package or recovery contract changes.


### Security Lab provider batch 06J preflight, 2026-10-31

Compared Linux `codex/ride-v3-migration` at `d91c44b` with Windows
`codex/ride-v3-migration` at `d91c44b` before adding the Fedora-only package
operations `dcfldd`, `ddrescue`, `foremost`, and `hexedit`. The catalog,
profile, provider, and run-state contracts remain unchanged. These operations
manage RPM presence only; they do not process disks or user files. No Windows
installer facts apply. Recheck if package recovery semantics or a shared
product identity changes.

The four Fedora operations passed supported Fedora 44 Workstation x86_64
package lifecycle acceptance after the preflight. See
[`06J acceptance`](acceptance/security-lab-forensic-media.md).

### Security Lab provider batch 06K, 2026-10-31

Added only Fedora RPM operations and an opt-in profile for `inxi`,
`pcp-system-tools`, `powertop`, and `sysstat`. Engine, catalog, profile, and
run-state contracts remain unchanged from the Windows development contract;
there are no Windows installer or provider facts to align. The Fedora 44
Workstation x86_64 lifecycle passed, including recovery of sysstat timer
enablement. See [06K acceptance](acceptance/security-lab-system-monitoring.md).
Recheck if package lifecycle semantics or shared operation schemas change.

### Security Lab provider batch 06L, 2026-10-31

Added Fedora-only package operations and an opt-in profile for `iptraf-ng`,
`netsniff-ng`, `ngrep`, and `tcptrack`. No engine, profile, or run-state
contract changed. The Fedora 44 Workstation x86_64 package lifecycle passed;
no traffic capture behavior was exercised. See [06L acceptance](acceptance/security-lab-packet-observation.md).
Recheck if shared package or run-state contracts change.

### Security Lab provider batch 06M, 2026-10-31

Added Fedora-only package operations and an opt-in candidate profile for
`firewalk`, `lbd`, `masscan`, and `zmap`. No engine, profile, or run-state
contract changed. The Fedora 44 Workstation x86_64 package lifecycle passed;
no scanner behavior ran. H038 tracks any future authorized-scope runtime
review. See [06M acceptance](acceptance/security-lab-network-probing.md).


### Security Lab provider batch 06N, 2026-10-31

Added Fedora-only RPM operations for AIDE, chkrootkit, OpenSCAP Scanner,
rkhunter, and SCAP Security Guide in an opt-in candidate profile. Shared
catalog, profile, provider, and run-state contracts did not change. The
package lifecycle passed Fedora 44 Workstation x86_64 candidate acceptance; it
does not execute scanners, initialize integrity databases, evaluate policy, or
remediate host settings. Rkhunter brought in `cronie`, which enabled but did
not activate `crond.service`; restore returned it to baseline. H039 tracks
later scan-behavior and recovery review. See [06N batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06O preflight, 2026-10-31

Added candidate Fedora-only RPM operations and an opt-in profile for `net-snmp`,
`net-snmp-utils`, `onesixtyone`, and `snmpcheck`. No shared catalog, profile,
provider, or run-state contract changes. Preflight identifies the packaged
`snmpd` and `snmptrapd` units and the active SNMP query tools; package acceptance
will capture service state without starting daemons or issuing queries. The Fedora 44 Workstation candidate lifecycle passed; neither daemon was
active, and restore returned package state exactly. H040 tracks later
authorized-scope and service recovery review. See [06O acceptance](acceptance/security-lab-snmp.md)
and the [batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06P preflight, 2026-10-31

Added five Fedora-only package operations and an opt-in profile for bkhive,
CmosPwd, John the Ripper, Ophcrack, and PDFCrack. No shared catalog, profile,
provider, or run-state contract changed. Acceptance covers signed package
presence and recovery only; it will not open evidence or run recovery tools.
The Fedora 44 Workstation candidate lifecycle passed. The profile restored all
13 Ophcrack Qt dependencies, with no evidence opened or tools executed. H041
tracks authorized evidence and private output review. See [06P acceptance](acceptance/security-lab-password-recovery.md)
and the [batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06Q preflight, 2026-10-31

Added Fedora-only RPM operations and an opt-in candidate profile for
Aircrack-ng, Cowpatty, Kismet, and Reaver. No shared schemas or Windows
installer facts changed. Acceptance will observe Kismet service and account
state without starting a daemon, attaching a wireless adapter, or generating
radio traffic. The Fedora 44 Workstation candidate lifecycle passed; Kismet stayed inactive,
its optional account was absent, and package recovery restored the exact RPM
inventory. H042 tracks later radio authorization and recovery review. See
[06Q acceptance](acceptance/security-lab-wireless.md) and the [batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06R, 2026-10-31

Added Fedora-only RPM operations and an opt-in candidate profile for Siege,
SIPp, SIPSAK, sockperf, and uperf. Shared catalog, profile, provider, and
run-state contracts did not change. The Fedora 44 Workstation x86_64 candidate
lifecycle passed with signed RPM verification and exact recovery; DNF installed
four dependencies and changed no preexisting RPM identity or version. No
HTTP/SIP traffic or benchmark sockets were opened and no tool was executed.
H043 tracks future authorized traffic limits and recovery review. See the
[06R acceptance report](acceptance/security-lab-network-load-tools.md) and
[batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06S, 2026-10-31

Added Fedora-only candidate RPM operations and an opt-in profile for Hydra,
Medusa, Ncrack, dsniff, and Ettercap. Shared catalog, profile, provider, and
run-state contracts did not change. The Fedora 44 Workstation x86_64 candidate
lifecycle passed with signed RPM verification and recovery of the package
identity set. Hydra upgraded the preinstalled expat package to the Fedora 44
updates version; restoring the profile removed new packages but retained this
DNF update. dsniff added libdb and libnids; Hydra added 14 dependencies. No
logins or network capture were exercised. H044 tracks future authorized-use
review. See the [06S acceptance report](acceptance/security-lab-network-credential-tools.md)
and [batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06T, 2026-10-31

Added Fedora-only candidate RPM operations and an opt-in profile for Argus,
NFSwatch, nicstat, and vnStat. Shared schemas and Windows installer facts did
not change. The Fedora 44 Workstation x86_64 candidate lifecycle passed with
signed RPM verification and package identity recovery; there were no DNF
dependencies or existing RPM changes. vnstat.service stayed not-found/inactive
and its database remained absent. Its RPM-created system account persisted
after package removal. No traffic or tools were used. H045 tracks later
authorized interface, service, and data recovery review. See the [06T
acceptance report](acceptance/security-lab-network-monitoring.md) and [batch
record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06U, 2026-10-31

Added Fedora-only candidate RPM operations and an opt-in profile for hping3,
packETH, sing, tcpreplay, and THC-IPv6. Shared schemas and Windows installer
facts did not change. The Fedora 44 Workstation x86_64 candidate lifecycle
passed with signed RPM verification and package recovery. DNF retained the
three GTK weak-dependency packages `gtk2`, `ibus-gtk2`, and
`libcanberra-gtk2` after packETH removal; no existing RPM changed. No packets
were sent or replayed. Hping3's upstream is inactive; Scapy or Nping are
alternatives to review in v3.1. H046 tracks authorized-link and recovery
review. See the [06U acceptance report](acceptance/security-lab-packet-generation.md)
and [batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06V, 2026-10-31

Added candidate Fedora RPM operations and an opt-in profile for EtherApe, p0f,
PADS, pcapdiff, and ssldump. Shared schemas and Windows installer facts did
not change. Acceptance observes `pads.service` state but does not start it;
the package lifecycle passed on Fedora 44 Workstation x86_64. DNF's two
dependencies were removed on restore; PADS remained inactive and no prior RPM
changed. No traffic was captured, PCAPs opened, or tools executed. H047 tracks
capture authorization, sensitive packet-data handling, and recovery before
candidate-gate removal. See the
[06V acceptance report](acceptance/security-lab-network-observation.md) and
[batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06W, 2026-10-31

Added Fedora-only candidate RPM operations and an opt-in profile for
extundelete, hfsutils, ntfs-3g, and ntfsprogs. Shared schemas and Windows
installer facts did not change. The Fedora 44 Workstation x86_64 candidate
lifecycle passed with an unchanged mount table; two packages were already
installed. No disk was attached, volume mounted, user data inspected, or
recovery tool run. H048 tracks image-first recovery, read-only source
boundaries, and isolated output review before candidate-gate removal. See the
[06W acceptance report](acceptance/security-lab-filesystem-tools.md) and
[batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06X, 2026-10-31

Added a candidate Fedora RPM operation and isolated opt-in profile for
Dislocker. Shared schemas and Windows installer facts did not change. The
package-only lifecycle passed on Fedora 44 Workstation x86_64; DNF removed all
16 dependencies on restore and the package alternatives entry was cleaned up.
No key or volume was accessed. H049 tracks key, output, and recovery review
before any volume behavior is managed. See the
[06X acceptance report](acceptance/security-lab-dislocker.md) and
[batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06Y, 2026-10-31

Added candidate Fedora RPM operations for Mcabber, Mutt, and Telnet, and
extended the stable `package.screen` operation from Server-only/install-only
to include Workstation and owned RPM removal. The existing Server Required
acceptance remains evidence for its unchanged target install/restore behavior;
the new Workstation target passed focused lifecycle evidence. DNF's seven new
dependencies were removed on restore. No shared schemas or Windows installer
facts changed. No client was launched or connected. H050 tracks cleartext
protocol and user-data review. See the
[06Y acceptance report](acceptance/security-lab-console-clients.md) and
[batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06Z, 2026-10-31

Added candidate Fedora RPM operations and an opt-in profile for GoAccess,
httpd-tools, HTTrack, and Wget2. The existing wget1 capability remains
available; the profile adds Wget2 as a separate installation choice. Shared
schemas and Windows installer facts did not change. Fedora 44 Workstation
package lifecycle passed; `httpd.service` remained not-found/inactive and two
packages were already installed. No logs were read and no network content was
requested. H051 tracks private data and authorized retrieval. See the
[06Z acceptance report](acceptance/security-lab-web-tools.md) and
[batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06AA, 2026-10-31

Added isolated candidate Fedora RPM operations and an opt-in profile for
nwipe, scrub, and wipe. Shared schemas and Windows installer facts did not
change. The package lifecycle passed with an unchanged mount table; three
dependencies were removed on restore. No storage device was enumerated and no
sanitizer was run. H052 tracks the separate safeguards required before actual
data sanitization behavior is offered. See the
[06AA acceptance report](acceptance/security-lab-data-sanitizers.md) and
[batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06AB, 2026-10-31

Added candidate Fedora RPM operations and an opt-in profile for ArpON, Hunt,
NetSED, and SSLsplit. Shared schemas and Windows installer facts did not
change. Fedora 44 Workstation package lifecycle evidence covers signed RPM
installation and removal only; no network tools were run and no traffic or
network configuration was changed. H053 tracks authorized behavior and network
recovery review. See the [06AB acceptance report](acceptance/security-lab-network-interception.md)
and [batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06AC, 2026-10-31

Added candidate Fedora RPM operations and an opt-in profile for Flawfinder,
SSLScan, SubNetCalc, and Swaks. Shared schemas and Windows installer facts did
not change. Fedora 44 Workstation package lifecycle passed, including the
restore of 15 dependencies. No source scan, endpoint connection, or SMTP
transaction occurred. H054 tracks authorized behavioral use and data handling.
See the [06AC acceptance report](acceptance/security-lab-network-diagnostics-2.md)
and [batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06AD, 2026-10-31

Added an isolated candidate Fedora RPM operation and opt-in profile for
GParted. Shared schemas and Windows installer facts did not change. Fedora 44
Workstation package lifecycle passed with unchanged package and mount state;
GParted was not launched and storage was not enumerated or modified. H055
tracks device authorization and recovery before partition behavior is offered.
See the [06AD acceptance report](acceptance/package.gparted.md) and
[batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06AE, 2026-10-31

Added an isolated candidate Fedora RPM operation and opt-in profile for AFF
utilities. Shared schemas and Windows installer facts did not change. Fedora
44 Workstation lifecycle passed with the `afflib` dependency removed on
restore; no image was accessed. H056 tracks evidence provenance and recovery
before image behavior is offered. See the
[06AE acceptance report](acceptance/package.afftools.md) and
[batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06AF, 2026-11-01

Added isolated candidate Fedora RPM operations and an opt-in profile for
ProxyChains-NG and Scapy. Fedora 44 Workstation package lifecycle passed;
Scapy's broad dependency transaction left `python3-tkinter` and `tk` after
restore, which is recorded in the automated acceptance check and H058. No
proxy or packet behavior was exercised. Shared schemas and Windows installer
facts did not change. The Workstation fixture was rebuilt from the same
Fedora-verified installer and Kickstart; its replacement image digest is
pinned and documented. See the [06AF acceptance report](acceptance/security-lab-network-path-tools.md)
and [batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06AG, 2026-11-01

Added isolated candidate Fedora RPM operations and an opt-in profile for the
Security Lab menu package and SETools GUI. The Fedora 44 Workstation package
lifecycle passed; applying the profile updated 11 pre-existing Qt/GStreamer
RPMs and restore did not reverse them. The menu package owns launcher entries
for the full Security Lab collection, and no GUI or SELinux policy behavior
was exercised. H059 tracks these user-visible and recovery checks. Shared
schemas and Windows installer facts did not change. See the
[06AG acceptance report](acceptance/security-lab-security-desktop-tools.md)
and [batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06AH, 2026-11-01

Added candidate Fedora RPM operations and an opt-in profile for scanmem and
unhide. The shared package lifecycle contract is unchanged; Windows has no
matching Fedora RPM provider. Acceptance is limited to signed package
presence, verification, status, repeat, and recovery. Neither operation is
run against process memory, host visibility, or user data. Review the shared
contract only if either product gains a Windows implementation or the package
source model changes. See the [06AH batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06AI, 2026-11-01

Mapped the legacy Fedora `default-editor` member to the Fedora-owned
`nano-default-editor` package and an opt-in Linux profile. The shared package
and lifecycle contracts did not change. Windows editor selection remains
platform-specific and is not inferred from this Fedora shell configuration.
The Fedora 44 Workstation package and Bash environment lifecycle passed;
CSH/fish runtime checks remain in H061. Revisit if Windows adopts this shared
operation contract. See the [06AI batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06AJ, 2026-11-01

Added the Fedora Nebula RPM as an opt-in candidate package-presence operation.
Its systemd package hook registers the unit, but acceptance confirmed that the
unit remains inactive and disabled. No network behavior, certificate, or
configuration is managed. Fedora's systemd/RPM behavior has no shared Windows
contract counterpart; revisit only if Nebula becomes a cross-platform product
contract. See the [06AJ batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06AK, 2026-11-01

Added Fedora NTPsec as an opt-in package-presence candidate. Fedora's RPM
registers systemd units and creates a persistent `ntp` nologin account; the VM
pilot confirmed the daemon stayed inactive/disabled and the existing chronyd
service stayed active/enabled. This changes no shared lifecycle or source
contract. Windows time-service behavior remains platform-specific; revisit if
the operation expands into shared clock configuration. See the
[06AK batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06AL, 2026-11-01

Mapped the Fedora Security Lab `openssh` core package to the existing supported
Fedora `openssh-clients` operation. This reuses the previously reviewed Linux
package and lifecycle contract; it adds no Windows operation or server
configuration. Existing Windows alignment and the distinct Linux
`recovery: none` contract remain applicable. See the
[06AL batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06AM, 2026-11-01

Added PSAD as an opt-in candidate for Fedora package presence only. Acceptance
confirmed the systemd unit remains inactive and disabled and that installation
and removal preserve the nftables ruleset. Fedora's daemon/firewall behavior
has no shared Windows package contract. Revisit if PSAD behavior or a
Windows-equivalent operation is introduced. See the
[06AM batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06AN, 2026-11-01

Added the Fedora RATS package as an opt-in candidate for package presence only.
No scanner behavior or source-code access is shared across platforms. Fedora's
RPM and the legacy upstream archive provide no basis for a Windows product
contract; no Windows operation was added. H065 tracks a broader analyzer review.
See the [06AN batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06AO, 2026-11-01

Tripwire is a Fedora-specific RPM presence candidate; the Fedora package
intentionally substitutes the hostname into its sample policy at install and
preserves that policy as an unowned `.rpmsave` on removal. The Fedora 44
Workstation package lifecycle passed with this residue documented. This does
not change a shared lifecycle or Windows product contract. Tripwire key,
policy, baseline, and scan workflow remain outside this package-presence
operation. Revisit alignment only if a shared integrity-monitoring contract
is proposed. See the [06AO batch record](migrations/provider-foundation-06.md).


### Security Lab provider batch 06AP, 2026-11-01

Added Fedora `usbsniff` as an opt-in RPM-presence candidate. Its package
lifecycle passed; no USB device or capture/replay behavior was exercised.
There is no shared package or lifecycle change and no Windows USB behavior is
implied. Revisit only if cross-platform USB capture/replay management is
proposed. See the [06AP batch record](migrations/provider-foundation-06.md).

### Fedora GNOME connector batch 10, 2026-11-01

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` for the
[GNOME browser connector migration](migrations/provider-foundation-10.md).
Windows has no equivalent GNOME Shell native messaging connector because this
operation integrates a Fedora desktop package with GNOME and the user's
browser. Linux adds a Fedora 44 RPM operation and opt-in profile using the
existing package source, target, and journal contracts; it adds no shared
schema fields or Windows product claims. Browser add-ons and user extension
directories remain outside RIDE ownership, with seeded extension data
preserved in VM acceptance. No unexplained shared-contract drift was found.
Recheck if Windows adds a comparable Linux integration contract, Fedora
changes the connector interface or supported target, or RIDE takes ownership
of browser add-ons or user extensions.

### Fedora AppImage integration batch 01, 2026-11-01

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` for the
[AppImage manager migration](migrations/publisher-apps-01.md). Windows has no
Linux AppImage integration application or matching source package. Linux adds
an opt-in system Flathub deployment of Gear Lever through the existing
`flatpak-app` handler and GPG-verified Flathub remote; no shared schema fields
or Windows installer claims changed. The package lifecycle owns only the
Gear Lever Flatpak ref. Apply refuses while the legacy AppImageLauncher RPM is
installed because it may compete for file handling; removing that RPM is an
explicit operator step. AppImage binaries, `~/Applications`, per-user Gear
Lever state, and generated launchers remain user-owned. Fedora 44 x86_64
Workstation acceptance passed and preserved seeded data. Recheck if Windows
adds a corresponding product, Linux adds managed AppImage file operations, or
Flatpak app recovery semantics change.

### Fedora VeraCrypt publisher RPM batch 02, 2026-11-01

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b`. Windows has no VeraCrypt
operation in that revision. Linux adds one Fedora 44 Workstation x86_64
publisher-RPM operation, verifies its detached signature in a temporary GPG
keyring pinned to the fingerprint published by VeraCrypt, and uses the shared
installed deployment identity and lifecycle states. Linux does not add the
publisher key to the system RPM database; DNF's local-package signature check
is disabled only after independent signature verification. There is no
Windows installer or shared source fact to copy. Fedora 44 Workstation x86_64
acceptance passed: a disposable encrypted test volume remained byte-identical
across package removal and reinstall, the mounted volume blocked removal, and
a failed DNF transaction cleaned the verified temporary artifacts. Linux
promotes the operation only for this declared target; no Windows installer or
shared source fact is inferred. Recheck if either platform adds VeraCrypt or
the package trust/recovery contract changes.

### Fedora publisher RPM batch 03, 2026-11-01

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` for Visual Studio Code and
Brave. Windows' accepted Visual Studio Code user setup has a separate
deployment identity and profile recovery; Linux keeps the Fedora system RPM
deployment distinct. No Windows Brave installer was used as Linux source
evidence. Linux adds two publisher-specific repository RPM handlers and
opt-in profiles, with exact RIDE-owned repo files, package-signature checks,
and package-only user-data-preserving removal. Publisher RPM public keys may
remain in the global RPM database; Linux intentionally does not remove them by
key ID. Microsoft's current upstream repo config disables package and
metadata checks, so Linux uses a stricter owned `gpgcheck=1` definition and
pins the publisher key fingerprint. Both operations remain candidates until
the Fedora 44 Workstation acceptance passes. No shared schema fields or
Windows installers changed. Recheck on key rotation, repo format changes,
Windows deployment changes, or a shared package recovery update.

### Fedora guest tools and YubiKey tools batches 07-08, 2026-11-01

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b` for the
[guest-tool](migrations/publisher-apps-07.md) and
[YubiKey](migrations/publisher-apps-08.md) migrations. Windows has no matching
Fedora SPICE/VMware guest packages or YubiKey Linux RPM/archive deployment.
Linux adds Fedora-specific operations and opt-in profiles using existing
catalog target, package lifecycle, and run-journal contracts; no shared schema
fields or Windows installer/source claims changed. Guest profiles select
QEMU/SPICE or VMware explicitly and the test claims package presence only.
`ykman` is a Fedora RPM operation, and Yubico Authenticator is an opt-in
user-local archive operation. Both use existing catalog target, source, and
package lifecycle contracts. Fedora 44 Workstation acceptance verified the
archive signature and digest, exact owned paths, repeat/status/removal, and
user-state preservation; it did not launch the GUI or configure a key. No
shared schema fields or Windows product decisions changed, and no unexplained
contract drift was found. Recheck if Windows adds corresponding product
operations or the shared package lifecycle/state contract changes.

### Fedora Publisher Apps 09, 2026-11-01

Compared Fedora catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b`. PowerShell exists on both
platforms, but the package and deployment forms remain native: Fedora uses a
pinned universal Microsoft RPM; Windows keeps its Windows package path. Linux
adds a pinned balenaEtcher RPM with no shared Windows installer or source claim.
No shared schema fields changed. Fedora 44 Workstation TCG acceptance passed
candidate-gated install, repeat, status, removal, and the no-profile PowerShell
probe. Etcher was not launched and no removable media was accessed. Recheck on
publisher source or shared package lifecycle changes; visible GUI behavior is
tracked separately in H073.

### Fedora Publisher Apps 10 source review, 2026-11-01

Compared Fedora catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `d91c44b`. Arduino IDE, Discord, Joplin,
and Vivaldi are owner-kept migration outcomes. Linux uses publisher-native
AppImages or signed/Flathub package deployments with profile-safe recovery;
Windows remains on its own installer and profile paths. Atom editor/plugins
remain retired on both sides according to their v2 source lifecycle. No shared
schema changes are proposed. Recheck when any Linux deployment or shared
package recovery contract is added; keep Joplin's Fedora 44 startup report and
Vivaldi's deferred owner decision visible.

## WoeUSB private script deployment, 2026-11-01

Fedora adds a Linux-only pinned WoeUSB 5.2.4 standalone Bash operation with
Fedora-specific runtime RPMs. It uses the existing user-scoped lifecycle and
catalog fields; no shared command, schema, journal, or package contract changed.
Windows packaging is independently owned. This is an intentional platform
boundary because the source artifact and runtime packages target Fedora Linux.
Review if Windows adds a WoeUSB deployment or a shared contract change affects
pinned user tools.

## Publisher AppImage migration, 2026-11-01

Fedora adds pinned user-local AppImage handlers for Arduino IDE and Joplin.
They use the existing package lifecycle and manifest convention; no shared
schema or journal contract changed. The publisher artifacts and Fedora runtime
checks are Linux-specific. Windows versions remain independently managed and
may retain native installers. Recheck if either client adds publisher AppImage
support or the shared deployment fields change.

## Browser and media Flatpak candidates, 2026-11-01

Fedora adds candidate operations for Chrome, Edge, and Spotify using the
existing signed system Flathub remote and Flatpak lifecycle. Windows retains
its native installers and profiles; the Linux Flathub packages are not shared
across platforms. Linux's Fedora 44 acceptance covers package presence,
repeat, status, removal, and preserved app data. No shared schema or journal
fields changed. Recheck if Windows adds Flatpak deployments or a shared
package identity or recovery field changes.

### Chrome recommended preferences, 2026-11-01

Linux adds the candidate `setting.chrome-preferences` for host recommended
policy files imported by the Flathub wrapper. Windows Chrome deployment and
policy settings remain independently managed through native Windows policy
mechanisms; Linux's policy paths, Flatpak wrapper, and exact file recovery are
not shared implementations. No catalog, profile, or run-state schema changed
outside the Linux setting value and handler. Recheck if Chrome changes its
recommended-policy behavior, the Flathub wrapper stops importing host policy,
or Windows adds a cross-platform browser preference contract.

### Xmind Flathub candidate, 2026-11-01

Linux adds `package.xmind` as an opt-in `flatpak-app` candidate for
`net.xmind.XMind`, using the signed Flathub system remote and preserving app
state on removal. This is the current publisher app path replacing the v2
legacy RPM scrape. A separate Linux publisher RPM may coexist after its package
identity, source trust, and inverse are established. No Windows deployment
contract or shared handler change is implied. Review when the Flathub manifest,
source, or supported target changes.

### GNOME Extensions manager, 2026-11-01

Linux adds the Fedora `gnome-extensions-app` package to the existing Fedora
browser-connector operation in an opt-in profile. The package manager path does
not install, enable, or restart GNOME Shell extensions; extension code remains
user-managed while per-extension pinning and recovery are reviewed in H082.
This Linux-only desktop integration has no Windows lifecycle mapping. Revisit
if the extension list gains a Windows counterpart or shared state contract.

### Fedora user default directories, 2026-11-01

Fedora adds `setting.user-default-directories` as a user-scoped operation for
creating `~/bin` and `~/git` only when absent. It records created directory
identities and removes only unchanged empty directories on restore. Windows has
no matching v2-to-v3 operation or shared directory lifecycle contract; this is
an intentional Linux convention with no Windows handler or schema change.
Revisit if a Windows outcome adds equivalent managed user directories or the
shared lifecycle changes.

### Fedora Firefox preference policy, 2026-11-01

Linux adds `setting.firefox-preferences` as a Fedora RPM AutoConfig operation
with Linux installation paths and an ownership manifest. Windows Firefox
policy deployment remains independently owned; no shared Firefox installer,
policy file, or platform handler was added. The shared lifecycle and catalog
contracts are unchanged. Review if Windows adopts a matching declarative
Firefox policy outcome or if Firefox removes its documented AutoConfig path.

### Fedora configurable GNOME favorites, 2026-11-01

Linux adds `setting.gnome-favorite-apps` as a Fedora Workstation user setting
with a validated list value and exact dconf journal recovery. Windows has no
matching RIDE v2 favorites operation. The list schema remains a Linux catalog
parameter and does not change the shared profile lifecycle. GNOME string
settings declare `absent` so the client can reset an explicitly selected value;
the `restore` command still replays the exact recorded dconf value. The profile
value field limit increases only to carry bounded desktop-ID lists. Fedora 44
Workstation acceptance passed apply, repeat, and exact restore for both
favorite profiles. Revisit if Windows adds a comparable favorites outcome or
if the shared configurable-value contract changes.

### Fedora GNOME idle and lock timing, 2026-11-02

Linux adds `setting.gnome-lock-timing` for the two kept RIDE v2 idle/lock
profiles. The Fedora Workstation handler validates and journals four GNOME user
settings as one exact-recovery transaction. Windows has no matching v2 GNOME
session behavior; the two timing choices remain Linux profile values and do
not change the shared run-state contract. Review if Windows introduces a
matching session-lock setting or either platform changes configurable-value
handling.

### Fedora owned GNOME custom shortcuts, 2026-11-01

Linux adds `setting.gnome-custom-shortcuts` as a Fedora Workstation user
setting. It stores only RIDE-created keybinding paths and merges configured
global bindings with existing GNOME lists; removal preserves unowned entries.
Windows has no matching v2 outcome or GNOME state model. This is an intentional
Linux-specific catalog value and handler; it changes no shared lifecycle verb
or Windows schema. Fedora 44 Workstation x86_64 lifecycle acceptance passed,
with visible shortcut dispatch queued as H089. Revisit if Windows adopts a
matching user shortcut contract or the shared configurable-value contract
changes.

### Fedora user Bash aliases, 2026-11-01

Linux adds `setting.bash-aliases` for Fedora Workstation user's `.bashrc` and
`.bash_aliases` files, with a fixed allowlist of Bash alias templates and
owned-block recovery. Windows PowerShell aliases and profile files have no
matching v2 lifecycle or shared implementation. This is an intentional Linux
setting; it changes no shared lifecycle verb or schema. Fedora 44 Workstation
x86_64 acceptance passed interactive Bash execution and preservation checks.
Revisit if the owner adds another shell or Windows receives an equivalent
profile-alias outcome.


### Fedora DNF5 FastDNF tuning, 2026-11-02

Linux adds candidate `setting.dnf5-fast-tuning` for Fedora 44 Workstation. It
uses a root-owned DNF5 drop-in and verifies the effective `fastestmirror` and
parallel-download settings; Windows has no matching v2 package-manager tuning
outcome. This is an intentional Fedora provider setting with no shared run
state or profile schema change. Review if Windows adopts an equivalent package
manager option or DNF5 changes its configuration precedence. Disposable VM
acceptance is pending.


### Fedora private static hostname, 2026-11-02

Linux adds supported `setting.hostname` for a validated, explicitly supplied
static hostname. Its selected value is retained only in the local run journal;
no host identity is added to public profiles. The operation changes the static
name only and restores the previous static name. Windows has no matching v2
hostname setting contract, so this Fedora systemd handler does not change shared
profile or journal schemas. Review if Windows adds an equivalent operation or
systemd changes static-hostname semantics.


### Fedora explicit whole-system update, 2026-11-02

Linux adds `system.update-all-packages`, an explicit DNF5 action with a
non-restorable journal entry, transaction inventory, and reboot assessment.
It is excluded from profiles and never reboots automatically. Windows has no
matching v2 whole-system update outcome or package-manager transaction
contract. This remains a Linux-specific system operation and does not change
shared lifecycle verbs or schemas. Revisit if Windows adds a comparable
explicit update contract or Fedora acceptance reveals edition-specific DNF5
behavior. Fedora 44 Workstation and Server disposable VM acceptance is pending.


### Fedora Docker Engine migration assessment, 2026-11-02

Linux's kept v2 Docker outcome is scoped to Docker CE Engine, its CLI and
containerd packages, plus the Linux `docker.service` state. Docker Desktop on
Windows has a different deployment, data boundary, and lifecycle. The planned
Fedora owner operation therefore remains Linux-specific and makes no shared
catalog, profile, or journal schema change. Review if Windows adopts a
matching declarative engine operation or the Fedora operation starts managing
cross-platform product state. Seeded image and volume recovery is still a v3.0
implementation gate.


### Fedora Server SSH root-login policy, 2026-11-02

Linux adds candidate operation `setting.ssh-root-login`, which owns a narrow
OpenSSH drop-in, validates effective `PermitRootLogin no`, and reloads sshd
while preserving active sessions. Windows has no matching v2 SSH server policy
outcome; this adds no shared catalog, profile, run-state, or lifecycle contract.
H103 tracks additional OpenSSH `Match` contexts. Revisit if Windows adds an
equivalent server policy operation or Linux changes the shared operation
contract.


### Fedora MulticastDNS resolver setting, 2026-11-02

Linux's kept v2 setting changes the `hosts:` resolver order to disable
`mdns4_minimal`. Fedora 44 generates `/etc/nsswitch.conf` through authselect,
so the v3 candidate changes the selected profile's `with-mdns4` feature and
journals the exact prior selection. Windows has no equivalent glibc NSS
configuration or matching setting contract. This remains Linux-specific and
does not change shared lifecycle verbs or schemas. Revisit if Windows adds a
comparable resolver policy or Fedora changes authselect's feature contract.


### Fedora Glances terminal monitor, 2026-11-02

Linux replaces the v2 Tecmint monitoring script with the Fedora-native
`package.glances` operation, supported on Fedora 44 Workstation and selected
through an opt-in profile. The v2 Server outcome uses the same RPM and a
separate opt-in service operation. That service binds its Web/API UI to
loopback, leaves firewalld unchanged, and supports remote viewing through SSH
forwarding. Windows has no matching v2 source outcome and this adds no shared
catalog or journal schema. Review if Windows adds a common system-monitor
product contract or if Linux adds authenticated remote-listener configuration.


### Fedora Firefox extension policy, 2026-11-02

Linux adds blocked `setting.firefox-addons` for Fedora 44 Workstation. It
uses Mozilla `ExtensionSettings`, keeps a distinct `removal-pending` state
until Firefox restarts and discovered profiles no longer contain the managed
extensions, and preserves unrelated policy. Windows branch `d91c44b` has no
matching managed Firefox extension outcome; its Cookie Cruncher archive
evidence is a different browser-cookie analysis capability. This adds no
shared catalog, profile, lifecycle-verb, or journal schema change. Review if
Windows adds a comparable policy operation or the Firefox policy lifecycle
changes. Its disposable acceptance test may use a temporary candidate catalog
inside the guest only; the checked-in blocked status cannot be overridden by
`--allow-candidate`.


### Fedora Ferium and legacy IE cookie analysis, 2026-11-02

Linux's kept Ferium outcome has no matching Windows v2 operation in the
current Windows migration branch. Fedora registers an opt-in user-local
no-GUI Linux binary with user-owned configuration and modpack data; its
platform-specific path changes no shared product installer, catalog, profile,
or journal contract. The Linux release has no publisher checksum for its
Linux asset, so v3.0 records observed archive and binary hashes after fetching
the fixed HTTPS release; H096 tracks stronger provenance if upstream publishes
it.
Windows' Cookie Cruncher archive evidence concerns a different browser-cookie
workflow and does not establish parity with Galleta's legacy Internet
Explorer cookie-file format. Linux now has an opt-in, pinned user-local
`package.galleta` candidate using Debian's BSD-3-Clause x86_64 package; H099
tracks representative parser fixtures. Plaso remains a separate partial path
for modern IE WebCache data. Revisit alignment if Windows adopts Galleta or
both platforms converge on a shared browser-evidence capability.

### Fedora Zeek network analysis replacement, 2026-11-02

Linux maps the kept Xplico outcome to an opt-in Fedora `zeek-core` RPM for
offline PCAP analysis and Zeek File Analysis Framework extraction. Xplico's
upstream package page lists Fedora only through Fedora 29; Zeek's protocols
and decoded output are not fully equivalent. Windows has no matching Xplico
or Zeek v2 package outcome on branch `d91c44b`, so this is a Linux-native
replacement and adds no shared catalog or journal schema change. H098 tracks
representative extraction fixtures and any required decoder gap. Revisit if
Windows adds a corresponding network-forensics operation or Fedora drops the
Zeek package.

### Fedora Minecraft server artifact, 2026-11-02

Linux's kept `InstallMinecraftServer` outcome is an opt-in Fedora Server
profile containing Fedora `java-25-openjdk-headless` and the official Mojang
26.3 server JAR. It installs only the runtime and a versioned user-local JAR;
world data, EULA acceptance, service identity, and network access remain
outside its lifecycle. The Windows development branch `d91c44b` has Microsoft
OpenJDK 25 side-by-side operations but no Minecraft server artifact operation.
The runtime IDs and deployment paths therefore differ by native provider,
while lifecycle verbs remain aligned. This adds no shared catalog or journal
schema change. Revisit if Windows adds a server artifact outcome or Linux
adds RIDE-managed world/service lifecycle.

### Fedora Server scheduled DNF5 updates, 2026-11-02

Linux now exposes `package.dnf5-plugin-automatic` and
`setting.dnf5-automatic` as a Fedora 44 Server opt-in candidate. The setting
enables the DNF5 timer with a RIDE-owned service drop-in that requests update
installation. On Windows branch `d91c44b`, `windows.update-download-mode`
selects notification or automatic download policy but does not run an update;
the separate WinGet AutoUpdate helper remains deferred for scheduler and
service recovery review. The Fedora timer therefore has no shared automatic
installation contract. The package, systemd handler, timer and Fedora RPM
transaction remain Linux-native, and this batch changes no shared catalog,
profile, or journal schema. Fedora 44 Server acceptance passed; H101 retains
scheduled execution, Cockpit overlap, and reboot/failure review. Revisit if
Windows adopts scheduled package installation semantics or Linux changes the
timer contract.

### Fedora SmartMonTools storage monitor package boundary, 2026-11-02

Linux's kept SmartMonTools outcome has an opt-in Fedora 44 Workstation path in
`package.smartmontools`. Fedora's signed RPM enables `smartd.service` during
installation; the Linux handler disables and stops that service immediately,
and package removal refuses if an administrator later enabled or started it.
It does not select storage devices or launch monitoring. The Windows branch has
no corresponding Linux RPM or shared handler contract, so this provider-specific
side-effect guard adds no shared operation ID, profile format, or journal
schema. Revisit if Windows adds a SMART-management outcome or Linux adds
RIDE-owned device selection and monitoring.
