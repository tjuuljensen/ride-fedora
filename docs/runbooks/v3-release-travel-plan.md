# v3 release preparation and travel work plan

Status checked: 2026-11-05. This is an execution checklist for the next v3.0
release-candidate work period. The current release decision and generated
migration report remain authoritative when this checklist becomes stale.

## Current starting point

- `docs/release-v3.0-review.md` says **not ready for a release tag**.
- Fedora 44 x86_64 is the only accepted release in the current target matrix.
  Fedora 45 was released on 2026-11-03; v3.0 must choose Fedora 45 support or
  explicitly retain Fedora 44 only. Supporting Fedora 45 requires fresh
  Workstation and Server images and target-specific acceptance.
- Migration progress reports 182/185 v2 outcomes dispositioned, with three
  unresolved; 150/169 scoped package and setting outcomes have an operable
  v3.0 path. The unresolved set includes the deferred VMFS6 access claim,
  Workstation ExpressVPN rotation, and Server VPN rotation. Check the current
  progress report before relying on this summary.
- Shared contract alignment items ALIGN-03 through ALIGN-05 and ALIGN-07
  through ALIGN-09 remain open. Windows-side checks and final contract
  publication are not established by Fedora-only results.
- Required local gates still include correcting three tracked shell file
  modes and assessing full ShellCheck diagnostics, as recorded in the release
  review.
- The working tree has five modified files and branch `codex/ride-v3-migration`
  is one commit ahead of its remote. Preserve and review this work; do not
  assume the review snapshot or prior local test counts apply to HEAD.
- The acceptance harness normally lets Fedora guests reach Fedora package
  repositories through QEMU user networking. An offline host therefore needs
  package artifacts and metadata already available to the guests, or an
  isolated local repository service/media that the guest can reach.

## Decisions to settle before travel

- [ ] Choose the v3.0 Fedora release target: Fedora 45 only, Fedora 44 only
  with a documented reason, or Fedora 44 and 45. Name the claimed editions
  (Workstation and/or Server) and x86_64 architecture.
- [ ] Decide whether Workstation ExpressVPN rotation and Server VPN rotation
  are required for v3.0. For each, choose implemented with target evidence or
  explicit owner-approved deferral/retirement with reason and review trigger.
- [ ] Confirm the VMFS6 boundary: v3.0 may ship an install candidate while
  actual VMFS6 access remains unverified and deferred to v3.1 under H118.
- [ ] Decide how to disposition the 87 functions in the supplementary legacy
  source audit and the ten unmatched Flatpak install/remove pairs. Record
  whether each group is reference-only, standalone, or deferred; do not
  create catalog operations merely to clear an inventory count.
- [ ] Confirm which optional package and setting candidates are actually in
  the v3.0 release claim. The large candidate inventory is not a requirement
  to promote every candidate.
- [ ] Assign owners and acceptable evidence/deferral for ALIGN-03–05 and
  ALIGN-07–09. Confirm access to the Windows checkout and ability to run its
  Pester suite before travel.
- [ ] Decide the offline acceptance strategy: locally mirrored Fedora
  repositories, a guest-reachable LAN repository, or a bounded set of
  pre-downloaded signed RPMs plus required metadata/dependencies. Confirm
  whether publisher artifacts can be tested from retained local copies and
  whether their handlers accept offline inputs.

## Prepare before travel

### A. Freeze the work and tools

- [ ] Review `git diff` and `git status`; identify the intent of each of the
  five modified files and the one-ahead commit. Save a reviewed patch or create
  a clearly named checkpoint commit before travel.
- [ ] Check free disk space and choose a disk-backed VM/run-artifact location;
  `.acceptance-runs` must not be on tmpfs. Keep enough space for base images,
  overlays, repository cache, transcripts, and retained artifacts.
- [ ] Confirm host tools: Python 3, QEMU (`qemu-system-x86_64`, `qemu-img`),
  `genisoimage`, SSH tools, KVM access if available, and the project's Python
  acceptance dependencies.
- [ ] Create a Python wheelhouse while online for the exact pinned test
  requirements. Verify an offline virtual-environment install from that
  wheelhouse; retain the requirements file and wheel hashes.
- [ ] Record the exact source commit/catalog digest to be tested. Keep the
  worktree and acceptance scripts at that same revision during each recorded
  run.

### B. Build and verify disposable target images

- [ ] Obtain Fedora 44 and Fedora 45 Everything x86_64 installer ISOs and
  verify Fedora-published checksums/signatures while online.
- [ ] Build separate Workstation and Server qcow2 images for each release
  selected above, using the repository's Kickstart recipes as the starting
  point. Keep target `VARIANT_ID`, release, architecture, recipe hash, ISO
  hash, qcow2 hash, and image build date in a target manifest.
- [ ] Do not treat Cloud Base as Workstation or Server evidence. Keep the
  existing Fedora 44 Cloud Base image only for its declared generic-package
  pilot unless scope explicitly requires it.
- [ ] Boot every image once, verify identity and SSH/cloud-init access, then
  shut it down cleanly. Retain immutable base images; acceptance must use fresh
  disposable overlays.
- [ ] Add pinned target entries and harness support for Fedora 45. The current
  `targets.json` contains only Fedora 44; do not relabel an older image as 45.

### C. Make the VM package source work without Internet

- [ ] Identify packages needed by the chosen acceptance batches, including
  transitive dependencies and packages that the kickstart recipe installs.
- [ ] While online, mirror or download the required Fedora 44/45 repository
  metadata, signed RPMs, and dependency closure for each chosen target. Keep
  release/architecture/repository boundaries separate and verify RPM
  signatures and checksums.
- [ ] Make the package source reachable by the guest without public Internet
  (for example, a host-only repository endpoint or attached read-only media).
  Configure disposable guest repo files through a test-only mechanism; do not
  change normal RIDE provider behavior just for the trip.
- [ ] Verify one package lifecycle on each selected target with external
  networking disabled. Prove install, repeat, status, restore/remove, and
  dependency inventory recovery use only the local source.
- [ ] Pre-download exact publisher artifacts needed for chosen offline work.
  Record source URI, version, filename, digest, signature/checksum evidence,
  and license. Verify handlers can consume retained artifacts offline; if they
  cannot, leave network-dependent tests for later rather than counting them
  as offline acceptance.
- [ ] Preload any other test inputs: synthetic evidence fixtures, browser
  test assets, source archives, or test data. Keep secrets and real evidence
  out of images, run logs, and repository files.

### D. Dry-run the travel workflow

- [ ] From a disconnected or network-blocked host, create a fresh overlay and
  run one RPM test from the repository root using an explicit disk-backed
  `--vm-output` path.
- [ ] Confirm the runner copies the exact checkout into the guest, records the
  correct target/image digest and acceleration mode, retains logs, and cleans
  up its VM process after both pass and failure.
- [ ] Run one non-networked mocked test and one VM acceptance case end to end.
  Reconnect afterward only to back up evidence; do not rely on connectivity
  during the trip.
- [ ] Copy the repo checkpoint, Fedora images, repository cache/media,
  wheelhouse, retained artifacts, and a checksum manifest onto the travel
  computer or encrypted external storage. Test reads from the copied location.

## Work to do before departure

- [ ] Complete the decisions above and record them in the release review,
  migration plan, and Windows alignment register as appropriate.
- [ ] Review ALIGN-03–05 and ALIGN-07–09 against the current Windows branch;
  identify exact counterpart commits/tests and what can be completed locally
  versus what requires Windows execution or contract publication.
- [ ] Triage the three unresolved migration outcomes and agree exact v3.0
  disposition text. Do not implement ExpressVPN/VPN rotation without verified
  ownership and safe recovery; do not claim VMFS6 data access without a
  fixture.
- [ ] Decide the minimal candidate batches that directly support the chosen
  release claim. For each batch, write operation IDs, target, baseline state,
  local artifacts/repository needs, checks, evidence path, and promotion gate.
- [ ] Review all current edits and reconcile generated files only after their
  source documents/catalog are settled.
- [ ] If Windows Pester cannot be run before departure, document it as a
  blocking release gate with a named follow-up; Fedora tests cannot substitute.

## Travel burndown: run in this order

### 0. Start each work session from a known state

- [ ] Check `git status --short --branch`; record current commit and any local
  changes in the session note.
- [ ] Check image, artifact, wheelhouse, and repository-cache checksums before
  running tests.
- [ ] Confirm no guest can reach the public Internet. Use only disposable VM
  overlays; never run state-changing acceptance on the host.

### 1. Confirm target and acceptance infrastructure

- [ ] Verify each guest's Fedora release, edition `VARIANT_ID`, and x86_64
  identity against its pinned manifest.
- [ ] Run one offline pilot lifecycle per declared edition and release.
- [ ] Record image/repository digests, source revision, VM acceleration,
  overlay ID, commands, transcript/JUnit paths, and actual outcome.
- [ ] Stop and investigate any missing artifact, repository fallback, package
  upgrade, or failed recovery before continuing the batch.

### 2. Close scope and migration dispositions

- [ ] For each unresolved v2 outcome, complete the selected implementation
  path with evidence or record the explicit owner-approved disposition.
- [ ] Record VMFS6 as install-only if deferred; make no claim of file access.
- [ ] Record source-audit and Flatpak pair dispositions so there is no hidden
  scope assumption in the release claim.
- [ ] Update migration outcomes and regenerate the progress/burndown reports.

### 3. Complete selected native package and setting acceptance

- [ ] Work one named batch at a time, using its documented order and current
  safety gates in `docs/migrations/progress.md`.
- [ ] For each operation, verify its own exact-target behavior and risk-based
  prior/apply/repeat/status/restore or removal/failure cases. Preserve
  pre-existing packages, configuration, user data, and evidence fixtures.
- [ ] Keep deeper scan, network, storage, encryption, service, or desktop
  claims blocked until their named safety/behavior review passes.
- [ ] Write or update each acceptance record; promote catalog status only for
  targets with sufficient evidence. Run the supported path without
  `--allow-candidate` after promotion.
- [ ] Keep optional candidates out of `default` and `server-base` unless the
  release scope explicitly selects them and their profile passes its target.

### 4. Close shared Windows/Linux contract gates

- [ ] Run the Windows Pester shared scenarios against the pinned contract and
  matching source revision.
- [ ] Finish ALIGN-03, ALIGN-04, ALIGN-05, ALIGN-07, and ALIGN-08 paired review
  with test evidence or approved deferrals.
- [ ] Publish the immutable contract reference, verify both repositories'
  digest pins, and complete ALIGN-09 consumer review.
- [ ] Update the alignment register with owner, compared revisions, result,
  intentional differences, and review triggers.

### 5. Freeze and validate the release candidate

- [ ] Fix the three tracked `.sh` modes and resolve the full ShellCheck
  diagnostics called out by `docs/release-v3.0-review.md`.
- [ ] Regenerate `docs/COMMANDS.md`, `docs/OPERATIONS.md`, migration progress,
  and burndown from their sources; verify generated output is clean.
- [ ] Run required shell syntax, ShellCheck, schema/catalog, mocked CLI,
  Firefox, Python compile/tests where relevant, executable-mode, and
  acceptance collection checks. Do not add test coverage beyond the agreed
  release gates during the trip.
- [ ] Run final supported-profile and selected operation acceptance on every
  claimed Fedora edition/release from fresh overlays, using the frozen
  revision. Attach evidence to the matching acceptance records.
- [ ] Confirm no unexplained Windows contract drift, unresolved required
  outcomes, or candidate profile in the supported claim.
- [ ] Reconcile final diffs and create one reviewable RC checkpoint. Record
  commit, target matrix, image/cache hashes, CI state, test evidence, known
  limitations, and follow-up owners. Tagging/publishing remains a separate
  release decision.

## Session close checklist

- [ ] Save transcripts, JUnit output, VM metadata, and checksums in the ignored
  acceptance run directory; update committed acceptance records with concise
  evidence references.
- [ ] Record pass, fail, or blocked result and the next exact action in the
  relevant batch/release document.
- [ ] Shut down guest processes and confirm no stale QEMU VMs remain.
- [ ] Preserve failed overlays until investigated; delete only reviewed,
  unneeded artifacts after backing up required evidence.
- [ ] Commit only a coherent reviewed batch. Do not commit VM secrets, user
  paths, real evidence, private credentials, or unreviewed run artifacts.

## Source documents

- [Release review](../release-v3.0-review.md)
- [Migration plan and alignment burndown](../MIGRATION-PLAN.md)
- [Generated migration progress](../migrations/progress.md)
- [VM acceptance harness](../acceptance/VM-HARNESS.md)
- [Acceptance record requirements](../acceptance/README.md)
- [Pinned Fedora targets](../../tests/acceptance/targets.json)
