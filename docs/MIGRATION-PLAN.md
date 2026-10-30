# Legacy Fedora default migration ledger

Source: `default.preset` on `master` at `43ba467`. All 76 active lines have an
initial disposition below. The v3 default profile is intentionally small;
deferred items are not silently executed. Current progress for the full scoped
v2 inventory is authoritative in `migration/outcomes.json` and its
[generated report](migrations/progress.md), not in these initial decisions.

The [scoped workstation and server burndown](workstation-server-burndown.md)
also covers non-active library functions and the three server presets, apart
from outcomes the owner excluded as obsolete or host-specific.

| Legacy action | Disposition | v3 target or rationale |
| --- | --- | --- |
| `DisableScreensaver` | retired | Conflicts with EnableScreenSaver in the same legacy preset; review a single desired state later. |
| `SetupUserDefaultDirs` | deferred | Review directory ownership and user scope. |
| `EnableFastDNF` | replaced | DNF5 defaults need current evidence; no legacy config edit. |
| `UpdateFedora` | deferred | Add explicit non-reversible system update operation after VM acceptance. |
| `InstallRequired` | replaced | The global seven-package bundle is replaced by bootstrap and handler prerequisite checks. Optional developer tools need a separate requested profile; see [provider foundation batch 01](migrations/provider-foundation-01.md). |
| `InstallShellTools` | supported | Split into supported `package.pv` and `package.strace` in the opt-in `shell-tools` profile; see [VM acceptance](acceptance/provider-shell-tools.md). |
| `InstallRPMfusionRepos` | deferred | [Provider batch 02](migrations/provider-foundation-02.md) records the signing-key and owned-recovery work required before a runnable operation. |
| `InstallKernelTools` | supported | Split into signed Fedora `kernel-devel` and `kernel-headers` package installs; [VM evidence](acceptance/provider-kernel-tools.md) does not establish a matching module-build environment. |
| `InstallDNFutils` | replaced | Fedora 44 Workstation has DNF5 and plugins; current `config-manager` and `download` commands passed the disposable-VM check. See [provider foundation batch 03](migrations/provider-foundation-03.md). |
| `InstallEzaGitHub` | replaced | Prefer Fedora repository package after verification. |
| `InstallFlathub` | deferred | [Flathub remote ownership](migrations/provider-foundation-09.md) needs scoped trust, detection, and inverse review. |
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
| `InstallPythonPip` | supported | Fedora `python3-pip` passed [VM lifecycle acceptance](acceptance/package.python3-pip.md); omit the v2 global pip self-upgrade. |
| `InstallPackagingTools` | replaced | Fedora `7zip` and `unar` passed [VM package acceptance](acceptance/provider-archive-tools.md); `unar` is a different CLI from `unrar`. |
| `InstallBasicEditors` | supported | Split into Fedora `nano` and `vim-enhanced` package installs with [VM evidence](acceptance/provider-basic-editors.md). |
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
| `InstallGnomeExtInstaller` | unsupported | [Archived upstream](migrations/provider-foundation-10.md), unpinned clone, and unowned path removal lack Fedora 44 compatibility and safe recovery. |
| `InstallBrave` | deferred | Third-party repository and license review. |
| `InstallChromium` | deferred | Candidate distro repository package. |
| `SetFirefoxPreferences` | replaced | Review settings against current Firefox policy; avoid legacy file overwrite. |
| `InstallFirefoxAddons` | deferred | Keep existing verified policy helper; integrate with v3 lifecycle later. |
| `InstallYouTubeDownloader` | replaced | Review maintained yt-dlp packaging instead of legacy youtube-dl. |
| `InstallGnomeTools` | opt-in candidate | Fedora printer UI and GNOME Tweaks passed [package VM acceptance](acceptance/provider-gnome-tools.md); visual checks remain v3.1, and v2's unowned `gparted` removal is excluded. |
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

## V3 release envelope and target matrix

The initial v3 release envelope is the small, data-only Linux client and its
declared Fedora package baselines. It does not imply replay of the 76-action
legacy default preset. A deferred ledger row is migration inventory, not a
release blocker unless a later scope decision selects it. Every required row
below needs target-specific acceptance before its profile or operation is
advertised as supported.

| Target and scope | Required v3 outcome | Current decision and evidence |
| --- | --- | --- |
| Fedora 44 x86_64 Workstation | `default`: `package.less`, `package.openssh-clients`, `package.exfatprogs` installed through the Fedora RPM provider. | Accepted for this edition after the [package batch](acceptance/workstation-package-batch-1-pilot.md), [OpenSSH client](acceptance/openssh-clients-workstation-pilot.md), and [combined profile](acceptance/workstation-default-profile-pilot.md) VM checks. Each operation links its acceptance record in the catalog. |
| Fedora 44 x86_64 Server | `server-base`: `package.less` and `package.openssh-clients` as a generic baseline. | Accepted for this edition after the [Server pilot](acceptance/server-base-package-pilot.md) and per-operation review. Other server functions remain in `network-devices`. |
| Fedora 44 x86_64 Cloud Base | Generic `package.exfatprogs` handler pilot. | Accepted only for `package.exfatprogs` after its [Cloud Base pilot](acceptance/package.exfatprogs-cloud-base-pilot.md) and edition gate; it does not establish Workstation or Server support. |
| Optional Fedora outcomes | `forensics` profile, unselected audit, artifact, and Python package candidates, and scoped deferred workstation/server outcomes. | Review in separate batches with explicit selectors and target evidence. Their absence does not block the package baselines above. |
| Unsupported targets and private behavior | Other Fedora releases or architectures, Debian/Ubuntu, and host-specific server values. | Fail closed. Add adapters or targets only after their own implementation and VM evidence; keep identities, secrets, and site values outside this repository. |

The official [Fedora 44 Workstation download](https://fedoraproject.org/workstation/download/)
offers an x86_64 Live ISO, not the qcow2 accepted by the current harness. Its
published 44-1.7 ISO SHA-256 is
`1620295f6a00c27c3208f0c00b8ece4eab1ec69b9002152d97488bf26a426ddf`.
Anaconda [does not support Kickstart installation from a Live ISO](https://anaconda-installer.readthedocs.io/en/latest/user-guide/troubleshooting/common-bugs.html#automatic-installation-in-live-os).
For automated base preparation, use a signed-checksum-verified Fedora 44
[Everything network installer](https://fedoraproject.org/en/misc/) with the
Workstation environment selected in Kickstart. The [2026-10-30 build](acceptance/fedora-44-workstation-image.md)
identified as `VARIANT_ID=workstation`; its installer and recipe checksums and
derived qcow2 digest are pinned in the [target matrix](../tests/acceptance/targets.json).
A modified Cloud Base image does not count as Workstation or Server evidence.
The [Server image build](acceptance/fedora-44-server-image.md) also uses the
verified Everything installer and a separate Kickstart environment selection;
its `VARIANT_ID=server` and qcow2 digest are pinned in the target matrix.

## Full scoped v2 migration program

The v3.0 program covers 165 grouped workstation and 15 grouped generic server
outcomes, including functions absent from active presets. Install/remove and
analogous state pairs share one outcome. The two owner-excluded Citrix
functions and 13 host-specific server functions stay visible in the ledger's
exclusion list, outside the 180-outcome completion denominator. The three
already supported base package operations remain valid release-envelope
evidence but do not automatically resolve a v2 outcome with different intent.

`migration/outcomes.json` assigns every outcome exactly one small batch, a
planned Fedora 44 x86_64 target, risk, source function mapping, current
disposition and progress, v3 operation IDs, evidence, blocker, and next action.
The generated [burndown](workstation-server-burndown.md) keeps the initial
legacy assessment alongside its current batch and progress. Process active
selectors first within each family. Ordinary batches contain at most six
related outcomes; security, storage, encryption, and difficult recovery
changes are isolated, while related user-state checks may share a batch. The family order is Fedora
repository packages, package-source foundations, forensic and isolated tools,
publisher applications, desktop and user state, system/network/security,
generic server, and explicit resolution decisions.

From the repository root as a regular user, these commands read the ledger,
source inventory, catalog, and evidence without changing the host or writing
files. No recovery is needed. CI runs `--check` on every migration-branch push.

```bash
python3 tools/migration_progress.py --summary
python3 tools/migration_progress.py --json
python3 tools/migration_progress.py --check
```

The percentage counts supported operations, evidence-backed opt-in candidates,
and documented non-operable resolutions separately; the report never presents
a retirement, private handoff, or unsupported decision as an install. An
unreviewed or merely implemented candidate stays unresolved. The linked
v3.1 hardening queue records broader coverage without weakening v3.0 safety.

The first [native RPM batch](migrations/native-rpm-01.md) passed on 2026-10-30:
six v2 CLI package outcomes are supported on Fedora 44 x86_64 Workstation in
the opt-in `cli-tools` profile. The [resolution record](migrations/resolution-decisions.md)
retires information-only, placeholder, and obsolete behavior without claiming
those outcomes as installs. [Native RPM batch 02](migrations/native-rpm-02.md)
passed four more exact-target packages. Its investigated `alien` recovery
retains one named DNF dependency without losing or changing pre-existing RPMs;
that cleanup question is in the v3.1 queue.
[Native RPM batch 03](migrations/native-rpm-03.md) closed its two unavailable
Nautilus integrations as unsupported, accepted Speedtest CLI as supported,
and recorded HexChat and Chromium as operable opt-in candidates with desktop
hardening in v3.1. [Native RPM batch 04](migrations/native-rpm-04.md) passed
`dc3dd` as supported and four desktop RPMs as operable opt-in candidates;
each passed install and inverse checks in the disposable Workstation VM.
[Native RPM batch 05](migrations/native-rpm-05.md) passed Libpst and Lynis as
supported and Dia, Wine, and VLC as opt-in candidates. Dia retained named
GTK2 dependencies; Wine and VLC updated named pre-existing RPMs without
losing their package identities.
[Provider foundation batch 01](migrations/provider-foundation-01.md) replaced
the global `Required` install bundle with explicit prerequisite checks and
accepted `pv` and `strace` as supported operations in the opt-in
`shell-tools` profile. [RPM Fusion provider batch 02](migrations/provider-foundation-02.md)
is assessed and remains blocked on trust and owned recovery.
[Provider foundation batch 03](migrations/provider-foundation-03.md) accepted
kernel development and Python pip RPM installs, documented DNF5 as the
replacement for `dnf-utils`, and accepted Fedora 7zip/unar package operations
as a changed-CLI archive replacement.
[Provider foundation batch 04](migrations/provider-foundation-04.md) accepted
the editor RPMs as supported, the GNOME utility RPMs as opt-in candidates,
and DNF5 versionlock as a non-runnable replacement. The archived GNOME
extension installer was resolved as unsupported. Flathub, snapd, and the
broad codec group remain isolated for their data, service, and source gates.
The remaining outcomes stay visible in the progress report.

For low-risk Fedora RPMs, use a focused automated plan/apply/repeat/status,
signature/files, and declared remove/restore check on each exact target; reuse
failure-injection evidence for an unchanged handler within the batch. For
third-party or desktop behavior, a VM happy path and focused mocked checks may
establish an opt-in candidate, with broader coverage in v3.1. Data, storage,
encryption, security policy, and difficult recovery require deeper safety and
inverse evidence before becoming runnable. Unsupported or private decisions
need a documented reason and review trigger. Keep candidate operations out of
`default` and `server-base`; add curated opt-in profiles as related operations
are ready. Manual checks are limited to behavior automation cannot observe.

The full v3.0 migration is ready for release review when all 180 outcomes have
an operable implementation or documented resolution, supported profiles pass
their declared targets, relevant CI and generated-doc checks pass, and no
shared Windows contract drift remains unexplained. A v3 tag and movement of
the `master` release line are separate publication decisions.

## Release gates

- Candidates remain blocked by default and require `--allow-candidate` for an
  explicit change. An implemented outcome counts as operable only after its
  risk-appropriate focused evidence; support still requires a passing VM on
  the exact declared target.
- The Firefox extension manager remains maintained and tested, but its v3 catalog lifecycle is pending. Its legacy direct function call is not reused.
- Generic server actions remain in `network-devices` until source, consumers, ownership, and rollback are reconciled. No host-specific preset is moved into this repository.
- Debian and Ubuntu adapters remain outside the supported target matrix until their own VM checks pass.

## Batch delivery and evidence

Use this plan as the handoff record for phased migration. A batch names its
operation IDs or legacy outcomes, source owner, target VM, dependencies,
expected prior and final state, recovery limit, acceptance checks, status,
revision, dated evidence, and exact next action. Keep source readiness separate
from runtime activation and verified behavior. The three base package
operations are verified on their declared editions; optional operations remain
candidates.

| Stage | Agent work | Owner or runtime input | Completion evidence |
| --- | --- | --- | --- |
| Select | Group a small related outcome set; identify catalog IDs and deferred neighbors. | Choose a target and provide a disposable VM when runtime testing begins. | Named scope, target distro/release/CPU, owner, and exclusions in this plan. |
| Assess | Trace legacy behavior, consumers, upstream source, data ownership, dependencies, detection, and inverse. Compare catalog, profile, and run-state fields and their semantics with the Windows development branch. | Resolve host-specific values only if the selected operation needs them. | Current-to-v3 mapping, risks, recovery limits, and any intentional schema or behavior differences recorded in `windows-alignment.md`. |
| Implement | Prepare catalog, handler, profile, docs, and focused tests; run static and mocked checks. | Review only decisions that cannot be derived from source or established scope. | Reviewable patch and `source-ready` status after relevant CI passes. |
| Activate | Apply the prepared revision only in a disposable target VM; record exact command and snapshot. | Supply VM access or run the documented commands. | VM log and `deployed-awaiting-verification` status. |
| Verify | Check plan, apply, repeat apply, status, removal or restore, partial failure, and package or artifact evidence. | Confirm any user-visible desktop behavior that automation cannot observe. | Dated `docs/acceptance/<operation-id>.md` results and `verified` or failed status. |
| Close or recover | Recheck the shared contract after implementation; promote only accepted target rows. Otherwise restore the VM snapshot, retain candidate status, and record the failure. | Provide further observations only when a check depends on them. | Updated catalog, migration row, Windows alignment review, evidence, and concrete next action. |

### Practical test scope for remaining batches

- Define completion criteria before testing: the selected operation and target,
  expected prior and final states, required lifecycle and failure checks,
  artifact or signature proof, recovery limit, evidence location, and any
  user-visible observation. State which result permits promotion and which
  leaves the operation a candidate.
- Run focused automated checks for changed code and reuse dated evidence for
  unchanged handlers or contracts when its revision, target, source, and
  behavior still apply. Record that reasoning in the batch evidence. A Cloud
  Base result cannot substitute for Workstation or Server target acceptance.
- Automate VM preparation, command execution, evidence collection, and
  recovery. Use one brief manual session only when user-visible behavior needs
  direct observation, such as desktop integration; record its exact checks.
- Expand coverage for changes involving user data, storage, encryption,
  security policy, or difficult recovery. Keep optional additions and
  unsupported scenarios in their own queue unless they are required for the
  selected migration outcome or a declared supported target.
- Investigate a failed run and record its cause or current uncertainty before
  retrying. Fix the defect or test environment first; do not repeat an
  unchanged long-running scenario merely to seek a pass.

Repeat the cross-repository schema and behavior review for every package batch
and at release-candidate preparation. Compare product identity, distribution,
deployment, provider selection, artifact evidence, profile selection, run-state
ownership, and recovery semantics. Alignment is required for shared behavior,
not for platform-specific syntax or handlers. Record each deliberate difference
with its reason and next review trigger in
[Windows alignment](windows-alignment.md). Record the compared branches or
revisions and review date in the batch evidence; treat an unexplained
difference as unfinished migration work.

The first Fedora 44 x86_64 Workstation VM package pilot covers `package.less`
and `package.exfatprogs`. Run CI first, then use `plan`, `apply`,
repeat `apply`, `status`, `remove`, and `restore` as applicable. Keep the VM
snapshot until recovery is checked. A green static check or source commit alone
does not promote an operation to `supported`. Server, Firefox, third-party
artifact, and Waydroid work should use separate batches because their state
and recovery differ.

The [disposable VM harness](acceptance/VM-HARNESS.md) provides Fedora 44 Cloud
Base and Workstation package pilots. The [Cloud Base pilot](acceptance/package.exfatprogs-cloud-base-pilot.md)
passed lifecycle and partial-failure scenarios on clean commit `9cc6416`; the
[Workstation pilot](acceptance/workstation-package-batch-1-pilot.md) passed its
focused scenarios on the pinned edition image. The Cloud result informs the
shared handler review but cannot replace edition-specific acceptance.
`package.exfatprogs` was a candidate during those pilots; its declared Cloud
Base and Workstation targets are now accepted in the per-operation record.

### Workstation package batch 1: completion criteria

Scope: `package.less` and `package.exfatprogs`, Fedora 44 x86_64 Workstation,
default `fedora-rpm` source, system scope. Fedora owns the RPMs; RIDE owns the
catalog selection, DNF handler, and run journal. The required prior state is
the observed, recorded package inventory of each fresh VM overlay. If either
package is already present in the installed image, use a separate disposable
overlay with that package deliberately removed to test the install path; do
not count an unchanged apply as install evidence.
The [Windows schema and behavior preflight](windows-alignment.md#fedora-workstation-package-batch-preflight-2026-10-30)
compared Linux `0bfd3c0` and Windows `17f9cef` on 2026-10-30; repeat it if the
package contract changes before promotion.

Pass only if the pinned Workstation guest identifies as Fedora 44 x86_64 with
`VARIANT_ID=workstation`; read-only plan changes nothing; apply installs absent packages;
repeat apply is unchanged; status matches RPM observation; RPM signature and
files verify; restore and explicit remove recover RIDE-owned new installs;
package inventory returns to its recorded baseline after recovery; and a
focused injected failure leaves an accurate journal and recoverable completed
steps. Record any limit on reinstalling a pre-existing package. Use the clean
Cloud Base pilot as evidence for unchanged DNF handler logic, while recording
why that reuse applies; run the edition-specific lifecycle checks here. These
command-line packages need no desktop manual session.

Status: focused pilot PASS for both operations on the pinned Workstation target
as recorded in the [batch evidence](acceptance/workstation-package-batch-1-pilot.md).
The [edition gate pilot](acceptance/fedora-44-variant-gate-pilot.md) then passed
on Cloud Base and Workstation for the declared operation/edition pairs. Both
were candidates at that stage: source was dirty during the VM runs, and the
target row change invalidated signatures of any older run. Subsequent source
equivalence, edition gate, technical review, and the owner's confirmation that
no non-disposable v3 runs exist cleared those gates. The full Workstation
default profile also passed with `package.openssh-clients`.

### Workstation package batch 2: completion criteria

Scope: `package.openssh-clients` on Fedora 44 x86_64 Workstation only, with the
default `fedora-rpm` source and system scope. The selected v3 baseline is not
an equivalent replacement for legacy `InstallRequired`. Its seven-package
bundle was later resolved as a non-runnable prerequisite-check replacement in
[provider foundation batch 01](migrations/provider-foundation-01.md). Fedora's [OpenSSH client package](https://packages.fedoraproject.org/pkgs/openssh/openssh-clients/)
provides `ssh`, `scp`, `sftp`, and client configuration; the catalog records its
Fedora license expression and repository GPG verification. RIDE owns the
selection, DNF handler, and run journal, not existing SSH configuration.

The pinned Workstation base has `openssh-clients` installed. On an intact
overlay, require a read-only plan, unchanged apply and repeat, matching status,
unchanged client configuration bytes, `ssh -V`, RPM signature and file checks,
and continuing SSH server availability. DNF cannot remove this package while
GNOME depends on `ssh-add` and `ssh-agent`. To test installation, make it absent
only in a separate disposable overlay with `rpm -e --nodeps`; this deliberately
broken dependency state is a test fixture, never a default-profile action.
Require RIDE apply to repair it, `dnf check` to pass, repeat apply to be
unchanged, and the client and server checks to pass. Inject a later missing
package, require an accurate failed journal, and verify that restore and
explicit remove refuse unsupported reversal without changing the guest.
Recovery of the artificial state is by discarding the overlay. This
security-related batch gets its own failure/recovery run. The operation must
declare installed-only state and `recovery: none`; no exact restoration of
pre-existing SSH configuration is promised. No desktop manual session is
needed.

Status: the [first VM run and focused rerun](acceptance/openssh-clients-workstation-pilot.md)
retain the investigated preparation failure and show three applicable VM
scenarios passing under the installed-only contract. Mocked recovery and
catalog validation also pass. The Server variant was added after its separate
[pilot](acceptance/server-base-package-pilot.md). Technical review and the
owner's no-run confirmation now support the accepted target rows.

Before accepting the Workstation `default` profile as a whole, run one
combined smoke check on the pinned image. Require a read-only plan of exactly
its three installed operations, an unchanged apply journal in profile order,
matching individual status, identical package inventory and SSH client
configuration, and an active SSH server. Reuse the package-specific install,
failure, and recovery results above; this combined check tests profile
selection and interaction, not another full lifecycle.

Status: the [combined profile pilot](acceptance/workstation-default-profile-pilot.md)
passed on 2026-10-30. Its three operations are accepted on the pinned
Workstation target.

### Server base package batch: completion criteria

Scope: `server-base` with `package.less` and `package.openssh-clients` on a
separately installed Fedora 44 x86_64 Server guest. The Fedora repository and
RIDE catalog/provider ownership match the Workstation batches; no
`network-devices` server function or host-specific value is transferred. The
Server image must be built from the verified 44-1.7 Everything netinstaller
with the Server environment selected, pinned by recipe and qcow2 digests, and
identified by the harness as `VARIANT_ID=server`. Define a Server target row
only after the image is verified. The [Windows OpenSSH preflight](windows-alignment.md#fedora-workstation-openssh-client-batch-preflight-2026-10-30)
and first package batch review apply to the unchanged package and journal
fields; recheck the exact Server target declarations before promotion.

Pass only if read-only plan, apply, repeat apply, and status match RPM state on
this edition. Exercise a new `less` install and its declared remove/restore
in a disposable overlay with package inventory recovery. For OpenSSH, retain
the installed-only `recovery: none` contract; check client version, signed
RPM/files, unchanged configuration, active SSH server, and refusal of remove
or restore. Use a separate disposable overlay for an artificially absent
client and injected later failure if needed to establish Server-specific
installation and journal behavior; never remove the client on a persistent
host. Reuse Workstation/Cloud DNF handler failure evidence only where the
handler and source are unchanged. Run one combined `server-base` profile smoke
check, then create per-operation acceptance records before any Server target
is promoted. These command-line checks need no manual desktop session.

Status: the Server image and target matrix are pinned. The
[focused pilot](acceptance/server-base-package-pilot.md) passed for both
operations and the combined profile on 2026-10-30. Their per-operation records
and the owner's no-run confirmation support the accepted Server target rows.

Candidate milestone `17849c4` records the implementation, target-specific VM
pilots, and per-operation acceptance drafts. The repository validation gates
passed: shell syntax and ShellCheck, generated documentation and schema,
burndown, executable modes, 49 unit tests, and acceptance collection. A
post-commit byte comparison found all 11 runtime source files in representative
Server VM archives identical to the committed candidate. At that milestone,
the only remaining working-tree change was an unrelated user deletion of
`docs/v3-migration.md`.
Local `/var/lib/ride-fedora/runs` was absent. The owner confirmed on
2026-10-30 that no non-disposable machine has v3 runs. This resolves the
original-catalog recovery gate for this promotion. The VM pilots need not be
repeated for unchanged runtime files.

On each non-disposable machine where v3 may have run, start in this repository
root as a regular user and run the following read-only inventory. Use `sudo`
only if the private run directory denies read access. It prints run IDs,
status, and changed operation IDs, but not saved state values; it writes
nothing and needs no recovery. A `review` row needs an original-catalog
recovery decision before using a newer catalog. An `invalid` row makes the
command exit 2 and also needs inspection. A zero-journal result confirms only
that machine, so record the machine list separately.

```bash
python3 tools/audit_v3_runs.py
```

The 2026-10-30 local result was `journals=0 review=0`; six focused audit
unit tests passed, including failed, orphaned, and symlinked journal handling. Other
machines can use the command if future catalog target changes need an
inventory; no non-disposable v3 runs existed before this promotion.

The per-operation acceptance records include a 2026-10-30 technical review
of the Fedora package records, archived JUnit results, and source equivalence.
Across the Cloud Base, Workstation, and Server pilots, the archived Fedora
package handler and journal module are byte identical to candidate commit
`81f604f`. The older Workstation operation rows differ from the current
catalog only in their edition target declarations; the edition gate and
current Server pilots cover those additions. The owner confirmed there are no
non-disposable v3 runs; the declared targets are accepted after this review.

### Supported-state promotion check

The owner confirmed on 2026-10-30 that no non-disposable machine has run v3.
Promote only the three base package operations with acceptance records for
every declared edition. Before accepting the promoted revision, require
catalog/schema and generated-doc checks, mocked CLI and recovery tests, and
one focused disposable VM check of the supported execution path on each
declared profile target: Workstation `default` and Server `server-base` must
plan and apply without `--allow-candidate`, report supported status and an
unchanged journal, and preserve inventory, SSH configuration, and server
availability. Cloud Base `package.exfatprogs` must install without the
override, repeat unchanged, verify signed RPM/files and status, then restore
the new install and recover package inventory. Reuse the earlier target gates,
failure injection, and inverse checks because their handler, targets, and
recovery logic did not change. The status and acceptance path do not enter the
run source signature. No manual session is needed for these command-line
operations. Record the final VM outcome and remote CI before closing this
batch.

The [supported-state promotion check](acceptance/fedora-44-supported-promotion.md)
passed on 2026-10-30: Cloud Base exfatprogs installed and restored without
the candidate override, while Workstation `default` and Server `server-base`
planned and applied with supported status and unchanged journals. All three
JUnit runs passed. Local shell, catalog, generated-doc, burndown, mocked,
Firefox, Python compilation, and acceptance collection gates passed. The
only unrelated working-tree change remains the user's deletion of
`docs/v3-migration.md`, which is excluded from the promotion commit.

Promotion commit `cc96362` passed the remote
[v3 validation workflow](https://github.com/tjuuljensen/ride-fedora/actions/runs/41031081441)
and [shell executable-mode workflow](https://github.com/tjuuljensen/ride-fedora/actions/runs/41031081445).
The v3 job passed shell syntax and ShellCheck, catalog and generated docs,
55 mocked and Firefox tests, and acceptance collection. The required v3
package envelope is accepted on its declared Fedora targets; optional and
unsupported outcomes remain scoped separately above. A v3 release tag has
not been published and `master` remains the v2 release line.

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
