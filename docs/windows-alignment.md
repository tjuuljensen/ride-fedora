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

### Fedora provider foundation batches 09, 11, and 12, 2026-10-30

Compared Linux catalog schema 3, profile schema 1, and run schema 2 with
Windows `codex/ride-v3-migration` at `0ff139f` before resolving the
[Flathub remote](migrations/provider-foundation-09.md),
[Flatpak runtime](migrations/provider-foundation-11.md), and
[Snapd](migrations/provider-foundation-12.md) source outcomes. None adds a
Linux catalog operation, profile selection, or run-state change in v3.0.
Fedora Workstation's existing Flatpak runtime is recorded as a non-runnable
replacement of the old package pair; it is not a shared Windows product
fact. Windows has no matching Flathub or Snapd catalog row in this revision.
The registered source, deployment, and recovery differences remain
intentional. No unexplained shared-contract drift was found. Recheck if
either platform adds a remote or package-manager handler, changes ownership
or recovery semantics, or reaches release review.

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
this revision. Linux records non-runnable decisions and a direct tool
handoff, with no new catalog/profile/run-state field or shared contract
change. No unexplained drift was found. Recheck if Linux adds an external
repository or policy handler, Windows adds a corresponding product, or
release review begins.

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
profile uses the existing schema. The two high-risk publisher outcomes and
the hypervisor-conditional outcome are non-runnable, with no new handler or
state field. These platform deployments and decisions are intentional; no
unexplained shared-contract drift was found. Recheck if Windows adds a
corresponding product, Linux adds portable or hypervisor-specific deployment,
or release review begins.

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
AppImage or publisher RPM inverse. Linux records non-runnable decisions and
does not share a platform installer. Windows has no matching Arduino IDE,
Atom, or Vivaldi catalog row in this revision. No Linux catalog, profile, or
run-state field changes in this batch; no unexplained shared-contract drift
was found. Recheck if Linux adds an owned portable or publisher RPM handler,
Windows changes the shared product facts, or release review begins.

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
is a separate per-user setting still awaiting typed state and exact restore;
the RPM operation makes no claim to it. No shared product or lifecycle
semantics changed. Recheck when the iBus setting is added, either schema
changes, Windows adds this product, or a release candidate is prepared.
