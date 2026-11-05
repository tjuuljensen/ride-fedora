# v3 release preparation and travel work plan

Status checked: 2026-11-05. This is an execution checklist for the next v3.0
release-candidate work period. The current release decision and generated
migration report remain authoritative when this checklist becomes stale.

## Current starting point

- `docs/release-v3.0-review.md` says **not ready for a release tag**.
- Release target decided: Fedora 44 and Fedora 45 x86_64. The current target
  matrix and harness still need Fedora 45 Workstation and Server images,
  target entries, and target-specific acceptance.
- Migration progress reports 182/185 v2 outcomes dispositioned, with three
  unresolved; 150/169 scoped package and setting outcomes have an operable
  v3.0 path. Workstation ExpressVPN rotation and Server VPN rotation stay in
  v3 scope and need implementation and target evidence. VMFS6 stays an install
  candidate in v3.0; fixture-backed access tests are deferred to v3.1 under
  H118. Check the current progress report before relying on migration counts.
- Shared contract alignment items ALIGN-03 through ALIGN-05 and ALIGN-07
  through ALIGN-09 remain open. Windows-side checks and final contract
  publication are not established by Fedora-only results.
- Required local gates still include correcting three tracked shell file
  modes and assessing full ShellCheck diagnostics, as recorded in the release
  review.
- Recheck `git status` before each work session. The travel-plan and release
  review edits are in progress; preserve existing user changes and do not
  assume earlier test counts apply to the current revision.
- The acceptance harness normally lets Fedora guests reach Fedora package
  repositories through QEMU user networking. An offline host therefore needs
  package artifacts and metadata already available to the guests, or an
  isolated local repository service/media that the guest can reach.

## Decisions to settle before travel

- [x] Release target: Fedora 44 and 45 x86_64. Update the release review and
  pinned target matrix, then accept Workstation and Server independently.
- [x] Keep Workstation ExpressVPN rotation and Server VPN rotation in v3
  scope. Ownership, implementation, and disposable target evidence remain
  required; no deferral is authorized.
- [x] VMFS6 boundary: ship the installer as an opt-in candidate in v3.0;
  defer genuine VMFS6 fixture/access validation to v3.1 under H118. Do not
  claim VMFS6 image access in v3.0.
- [ ] Review and disposition the 87 functions in the supplementary legacy
  source audit and the ten unmatched Flatpak install/remove pairs. Record
  whether each group is reference-only, standalone, or deferred; do not
  create catalog operations merely to clear an inventory count.
- [ ] Confirm which optional package and setting candidates are actually in
  the v3.0 release claim. The large candidate inventory is not a requirement
  to promote every candidate.
- [ ] Decide whether offline acceptance itself belongs in the v3.0 promise.
  Architecture is decided: use local offline Fedora package mirrors (or
  Fedora DVD media) plus a set of downloaded install files. Prepare this
  setup for travel either way; do not claim offline install support in RIDE
  unless the release scope selects it and the client path is implemented and
  accepted.

### Contract alignment, in plain language

The shared behavior contract is the common agreement for how the Linux and
Windows clients handle commands, previews, errors, recovery, and output. It
does not require the two clients to use identical command syntax or package
catalogs. Each ALIGN item below closes a specific gap in that agreement.

- [ ] **ALIGN-03 — predictable command meaning.** A command should not silently
  change behavior because an option is missing, contradictory, or irrelevant.
  `set` applies a declared state; `unset` removes a declared override or
  refuses when none exists. It must not generically mean `disabled`.
  `restore` recovers the captured prior state. Align each client's declaration
  and help wording, decide which operation classes a profile may remove, and
  require an explicit operation or profile for `remove`. Invalid combinations
  must fail before writing state. Close with paired Linux and Windows tests
  proving refusal before mutation and recovery after valid explicit changes.
  See the [setting lifecycle decision](../windows-alignment.md#align-03-setting-lifecycle-decision-2026-11-05).
- [ ] **ALIGN-04 — safe previews and downloads.** Downloading files is not the
  same as accepting a target to execute changes on. A preview must check the
  same target and identity conditions as execution, and must not create a run,
  write files, or mutate a machine. Decide and document the narrow exception
  for an already-installed package that needs no change. Close by running the
  paired preview scenarios on both clients and proving they are write-free
  while actual changes still require their normal gates.
- [ ] **ALIGN-05 — one shared behavior test set.** Linux and Windows need to
  run the same named scenarios for candidate/target/privilege checks, invalid
  arguments, unset/remove, dependencies, partial failure, restore, downloads,
  and completion. The adapters may be Bash/Python and Pester; the expected
  result for each scenario must be shared and version-pinned. Close when both
  suites report the same scenario revision and a deliberate mismatch makes
  the suite fail. Run the Windows Pester suite; Linux passing alone is not
  enough.
- [ ] **ALIGN-07 — notice future drift.** When one client or the shared contract
  changes, reviewers need a template that links the related change and asks
  whether the other client is affected. A read-only drift report should flag
  newer contract or peer capabilities; it must not update pins or merge code
  automatically. Close by detecting a deliberate test drift and recording
  the resulting review task on each affected repository.
- [ ] **ALIGN-08 — compatible ways to select and inspect work.** Both clients
  should let callers explicitly select an operation/profile and ask for
  status by operation ID or supported view. Machine-readable output needs a
  versioned schema so scripts can rely on it. Native CLI syntax may differ.
  Close with paired examples and tests for selectors, output fields, ordering,
  and source/variant distinctions on Windows and Linux.
- [ ] **ALIGN-09 — pin the final agreement.** The current contract text is on a
  development branch and has no immutable published commit reference. Publish
  or otherwise freeze the reviewed contract, record its commit and digest in
  both repositories, then review each client against that exact text. Close
  only when the references match and prior ALIGN items are complete or have
  explicit owner-approved deferrals with reasons and review triggers.

## Prepare before travel

### A. Freeze the work and tools

- [ ] Review `git diff` and `git status`; identify the intent of each modified
  and untracked file. Save a reviewed patch or create a clearly named
  checkpoint commit before travel.
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

Use the prepared helper from the repository root:

```bash
tools/travel-preflight.sh report
tools/travel-preflight.sh wheelhouse
tools/travel-preflight.sh verify-wheelhouse
tools/travel-preflight.sh manifest
```

`report` saves a timestamped readiness report and full tracked diff under
`.acceptance-runs/travel-prep/`; read and review these outputs before packing.
`wheelhouse` needs Internet access. `verify-wheelhouse` creates a temporary
venv and installs with pip index access disabled. `manifest` records the
source revision, tracked diff and untracked-file digests, catalog digest, and
acceptance-requirements digest. These commands do not commit or discard
worktree changes.

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

The image helper runs the documented image flow and keeps files below
`.acceptance-runs/fedora-images/`:

```bash
tools/build-acceptance-images.sh fetch 45 workstation
tools/build-acceptance-images.sh build 45 workstation
tools/build-acceptance-images.sh build 45 server
tools/build-acceptance-images.sh inspect 45 workstation
tools/build-acceptance-images.sh inspect 45 server
```

The Fedora 44 images are already present and pinned. Check them with
`qemu-img check`, `virt-cat`, and the boot method below; rebuild them only if
they fail. To reproduce a Fedora 44 image, use the same `fetch` and `build`
commands with `44` in place of `45`.

#### Preparation run recorded 2026-11-05

- Fedora 44 Workstation and Server passed fresh-overlay boot checks under
  QEMU TCG. Evidence is under
  `.acceptance-runs/travel-prep/boot-fedora44-workstation-r2/` and
  `.acceptance-runs/travel-prep/boot-fedora44-server/`. This proves boot,
  identity, cloud-init, SSH, and client-bundle readiness only.
- Fedora 45 installer media was downloaded and its Fedora-signed checksum
  verified. Both the Workstation and Server net installers then failed to
  download packages from their configured public repository. Their logs are
  under `.acceptance-runs/fedora-images/fedora-45-{workstation,server}-x86_64/`.
  Neither partial image contains an operating system, and neither was
  registered as a target.
- Fedora 45 therefore needs a package source available to the guest: prepare a
  complete local Fedora 45 x86_64 mirror or use verified DVD media, then rerun
  the image build. The current Kickstarts use a public net installer source;
  point them at the local mirror or otherwise make that source reachable from
  the guest. Do not register either Fedora 45 target until build, inspect, and
  boot all pass.
- A failed build can leave a partial qcow2 even though `qemu-img check` says
  its container metadata is healthy. `virt-cat` failing to find `/etc/os-release`
  means there is no installed guest OS. The build helper now writes to a
  temporary image, preserves failed images with a `.failed-*` name, and writes
  a final image and manifest only after guest validation. To move earlier
  incomplete canonical images aside without deleting their evidence, run:

  ```bash
  tools/build-acceptance-images.sh discard-incomplete 45 workstation
  tools/build-acceptance-images.sh discard-incomplete 45 server
  ```

  Do not retry the install until guest access to the package source is fixed.
- The Python wheelhouse preparation and offline pip-install verification
  passed. Its timestamped preflight record and wheelhouse are under
  `.acceptance-runs/travel-prep/`.

Register a successfully built Fedora 45 image only after `inspect` passes:

```bash
python3 tools/register-acceptance-target.py \
  .acceptance-runs/fedora-images/fedora-45-workstation-x86_64/workstation.qcow2 \
  45 workstation .acceptance-runs/fedora-images/fedora-45-workstation-x86_64
python3 tools/register-acceptance-target.py \
  .acceptance-runs/fedora-images/fedora-45-server-x86_64/server.qcow2 \
  45 server .acceptance-runs/fedora-images/fedora-45-server-x86_64
```

`fetch` verifies the Fedora-signed checksum file and ISO digest before image
installation. `build` records an image manifest after checking the qcow2 and
guest release/variant. Only after those checks pass, run the boot check:

```bash
for release in 44 45; do
  tools/build-acceptance-images.sh boot "$release" workstation
  tools/build-acceptance-images.sh boot "$release" server
done
```

`boot` uses the acceptance VM launcher with a fresh overlay and verifies
cloud-init, SSH, guest identity, architecture, and the bundled client. Its
output directory contains the image digest, metadata, identity output, and
transcript. After successful boot checks, add the verified image digest and
installer/recipe provenance to `tests/acceptance/targets.json` with the
registration helper above, then update the acceptance target docs.

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

- [ ] Record the settled Fedora 44/45 target, VPN rotation scope, VMFS6
  boundary, and offline architecture in the release review, migration plan,
  and Windows alignment register as appropriate. Record offline acceptance
  inclusion as undecided until the owner chooses it.
- [ ] Review ALIGN-03–05 and ALIGN-07–09 against the current Windows branch;
  identify exact counterpart commits/tests and what can be completed locally
  versus what requires Windows execution or contract publication.
- [ ] Plan implementation and acceptance for both VPN rotation outcomes;
  reconcile Server runtime ownership before moving its timer. Keep VMFS6
  image access deferred to v3.1 and the install operation candidate-gated.
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
- [ ] For offline package acceptance, confirm public egress is blocked and the
  guest can reach only the prepared local repository/media. The image boot
  check itself uses a local seed and makes no package transactions. Use only
  disposable VM overlays; never run state-changing acceptance on the host.

The boot verifier needs loopback sockets for the harness SSH port forward. If
a sandbox blocks socket creation, run it in the approved development
environment; do not remove the SSH verification or weaken the VM harness.

Generate the work-session record with:

```bash
tools/travel-preflight.sh report
tools/travel-preflight.sh manifest
```

Review the saved status, diff patch, tool list, disk mount, commit, and catalog
digest before running an acceptance command. The report is a record; it does
not decide whether a user change is ready to commit. Verify each offline asset
against its manifest using `sha256sum --check` before use.

### 1. Confirm target and acceptance infrastructure

- [ ] Verify each guest's Fedora release, edition `VARIANT_ID`, and x86_64
  identity against its pinned manifest.
- [ ] Boot-check each image with
  `tools/build-acceptance-images.sh boot RELEASE EDITION`; confirm the fresh
  overlay reaches cloud-init/SSH and reports the pinned target identity.
- [ ] If offline acceptance is selected for v3.0, run one package lifecycle
  per declared edition/release with public network access blocked and only the
  local mirror/DVD source plus retained install files enabled. Offline
  acceptance remains undecided for v3.0; do not treat the image boot check as
  offline package-install evidence.
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

- [ ] Work through the ALIGN-03 through ALIGN-09 explanations above; record
  completion evidence or approved deferrals for each item.
- [ ] Run the Windows Pester shared scenarios against the pinned contract and
  matching source revision.
- [ ] Publish the immutable contract reference, verify both repositories'
  digest pins, and review each consumer against that exact reference.
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

## Review queue: supplementary legacy source functions

Review these 87 functions against the source code and their callers before
choosing a disposition. The numbered line links point to the function
definitions. These are review items, not a request to migrate each function.
The group counts match [the audit](../legacy-source-audit.md).

### `lib-upgrade.sh` (3)

- [ ] `CheckNextVersionRepos` — [definition, line 39](../../lib-upgrade.sh#L39)
- [ ] `UpgradeFedora` — [definition, line 72](../../lib-upgrade.sh#L72)
- [ ] `InstallKernelHeaders` — [definition, line 85](../../lib-upgrade.sh#L85)

### `lib/distro/lib-distro.sh` (21)

- [ ] `GetDebian` — [line 25](../../lib/distro/lib-distro.sh#L25)
- [ ] `GetDebianTorrent` — [line 35](../../lib/distro/lib-distro.sh#L35)
- [ ] `GetDebianNetinst` — [line 44](../../lib/distro/lib-distro.sh#L44)
- [ ] `GetUbuntu` — [line 57](../../lib/distro/lib-distro.sh#L57)
- [ ] `GetUbuntuTorrent` — [line 67](../../lib/distro/lib-distro.sh#L67)
- [ ] `GetUbuntuServer` — [line 77](../../lib/distro/lib-distro.sh#L77)
- [ ] `GetUbuntuServerTorrent` — [line 87](../../lib/distro/lib-distro.sh#L87)
- [ ] `GetFedora` — [line 100](../../lib/distro/lib-distro.sh#L100)
- [ ] `GetFedoraTorrent` — [line 107](../../lib/distro/lib-distro.sh#L107)
- [ ] `GetFedoraServer` — [line 116](../../lib/distro/lib-distro.sh#L116)
- [ ] `GetFedoraServerTorrent` — [line 123](../../lib/distro/lib-distro.sh#L123)
- [ ] `GetKali` — [line 137](../../lib/distro/lib-distro.sh#L137)
- [ ] `GetKaliTorrent` — [line 145](../../lib/distro/lib-distro.sh#L145)
- [ ] `GetKaliLive` — [line 153](../../lib/distro/lib-distro.sh#L153)
- [ ] `GetKaliLiveTorrent` — [line 161](../../lib/distro/lib-distro.sh#L161)
- [ ] `GetMint` — [line 173](../../lib/distro/lib-distro.sh#L173)
- [ ] `GetTailsTorrent` — [line 186](../../lib/distro/lib-distro.sh#L186)
- [ ] `GetRaspiOSTorrent` — [line 199](../../lib/distro/lib-distro.sh#L199)
- [ ] `GetSlackwareTorrent` — [line 233](../../lib/distro/lib-distro.sh#L233)
- [ ] `GetArchTorrent` — [line 250](../../lib/distro/lib-distro.sh#L250)
- [ ] `GetSecurityOnion` — [line 267](../../lib/distro/lib-distro.sh#L267)

### `lib/vm/lib-vm.sh` (6)

- [ ] `GetRemnuxVmware` — [line 36](../../lib/vm/lib-vm.sh#L36)
- [ ] `GetRemnuxVbox` — [line 46](../../lib/vm/lib-vm.sh#L46)
- [ ] `GetKaliVMware` — [line 56](../../lib/vm/lib-vm.sh#L56)
- [ ] `GetKaliVbox` — [line 65](../../lib/vm/lib-vm.sh#L65)
- [ ] `GetSANSsift` — [line 74](../../lib/vm/lib-vm.sh#L74)
- [ ] `GetSOFelk` — [line 93](../../lib/vm/lib-vm.sh#L93)

### `lib/flatpak/lib-flatpak.sh`: unmatched product pairs (20 functions)

- [ ] `InstallJohn` — [line 109](../../lib/flatpak/lib-flatpak.sh#L109);
  `RemoveJohn` — [line 113](../../lib/flatpak/lib-flatpak.sh#L113)
- [ ] `InstallAuthy` — [line 117](../../lib/flatpak/lib-flatpak.sh#L117);
  `RemoveAuthy` — [line 121](../../lib/flatpak/lib-flatpak.sh#L121)
- [ ] `InstallUpscaler` — [line 130](../../lib/flatpak/lib-flatpak.sh#L130);
  `RemoveUpscaler` — [line 135](../../lib/flatpak/lib-flatpak.sh#L135)
- [ ] `InstallGtkhsh` — [line 139](../../lib/flatpak/lib-flatpak.sh#L139);
  `RemoveGtkhsh` — [line 144](../../lib/flatpak/lib-flatpak.sh#L144)
- [ ] `InstallGhidra` — [line 148](../../lib/flatpak/lib-flatpak.sh#L148);
  `RemoveGhidra` — [line 153](../../lib/flatpak/lib-flatpak.sh#L153)
- [ ] `InstallUEFItool` — [line 157](../../lib/flatpak/lib-flatpak.sh#L157);
  `RemoveUEFItool` — [line 162](../../lib/flatpak/lib-flatpak.sh#L162)
- [ ] `InstallSlack` — [line 178](../../lib/flatpak/lib-flatpak.sh#L178);
  `RemoveSlack` — [line 182](../../lib/flatpak/lib-flatpak.sh#L182)
- [ ] `InstallSignal` — [line 186](../../lib/flatpak/lib-flatpak.sh#L186);
  `RemoveSignal` — [line 190](../../lib/flatpak/lib-flatpak.sh#L190)
- [ ] `InstallColorPicker` — [line 215](../../lib/flatpak/lib-flatpak.sh#L215);
  `RemoveColorPicker` — [line 219](../../lib/flatpak/lib-flatpak.sh#L219)
- [ ] `InstallPDFtricks` — [line 223](../../lib/flatpak/lib-flatpak.sh#L223);
  `RemovePDFtricks` — [line 227](../../lib/flatpak/lib-flatpak.sh#L227)

### `lib/funstuff/funstuff.sh` (28)

- [ ] `InstallSl` — [line 12](../../lib/funstuff/funstuff.sh#L12)
- [ ] `RemoveSl` — [line 16](../../lib/funstuff/funstuff.sh#L16)
- [ ] `InstallLolcat` — [line 22](../../lib/funstuff/funstuff.sh#L22)
- [ ] `RemoveLolcat` — [line 26](../../lib/funstuff/funstuff.sh#L26)
- [ ] `InstallCmatrix` — [line 31](../../lib/funstuff/funstuff.sh#L31)
- [ ] `RemoveCmatrix` — [line 35](../../lib/funstuff/funstuff.sh#L35)
- [ ] `InstallAfire` — [line 40](../../lib/funstuff/funstuff.sh#L40)
- [ ] `RemoveAfire` — [line 44](../../lib/funstuff/funstuff.sh#L44)
- [ ] `InstallOneko` — [line 49](../../lib/funstuff/funstuff.sh#L49)
- [ ] `RemoveOneko` — [line 53](../../lib/funstuff/funstuff.sh#L53)
- [ ] `InstallXeyes` — [line 58](../../lib/funstuff/funstuff.sh#L58)
- [ ] `RemoveXeyes` — [line 62](../../lib/funstuff/funstuff.sh#L62)
- [ ] `InstallCowsay` — [line 67](../../lib/funstuff/funstuff.sh#L67)
- [ ] `RemoveCowsay` — [line 71](../../lib/funstuff/funstuff.sh#L71)
- [ ] `InstallAsciiaquarium` — [line 76](../../lib/funstuff/funstuff.sh#L76)
- [ ] `RemoveAsciiaquarium` — [line 80](../../lib/funstuff/funstuff.sh#L80)
- [ ] `InstallFiglet` — [line 85](../../lib/funstuff/funstuff.sh#L85)
- [ ] `RemoveFiglet` — [line 89](../../lib/funstuff/funstuff.sh#L89)
- [ ] `InstallToilet` — [line 94](../../lib/funstuff/funstuff.sh#L94)
- [ ] `RemoveToilet` — [line 98](../../lib/funstuff/funstuff.sh#L98)
- [ ] `InstallFortune` — [line 103](../../lib/funstuff/funstuff.sh#L103)
- [ ] `RemoveFortune` — [line 107](../../lib/funstuff/funstuff.sh#L107)
- [ ] `InstallThefuck` — [line 112](../../lib/funstuff/funstuff.sh#L112)
- [ ] `RemoveThefuck` — [line 116](../../lib/funstuff/funstuff.sh#L116)
- [ ] `InstallFunnyManpages` — [line 121](../../lib/funstuff/funstuff.sh#L121)
- [ ] `RemoveFunnyManpages` — [line 140](../../lib/funstuff/funstuff.sh#L140)
- [ ] `InstallAview` — [line 148](../../lib/funstuff/funstuff.sh#L148)
- [ ] `RemoveAview` — [line 158](../../lib/funstuff/funstuff.sh#L158)

### `lib/osint/lib-osint.sh` (6)

- [ ] `InstallTheHarvester` — [line 33](../../lib/osint/lib-osint.sh#L33)
- [ ] `RemoveTheHarvester` — [line 61](../../lib/osint/lib-osint.sh#L61)
- [ ] `InstallYETI` — [line 68](../../lib/osint/lib-osint.sh#L68)
- [ ] `RemoveYETI` — [line 178](../../lib/osint/lib-osint.sh#L178)
- [ ] `InstallSpiderFoot` — [line 219](../../lib/osint/lib-osint.sh#L219)
- [ ] `RemoveSpiderFoot` — [line 264](../../lib/osint/lib-osint.sh#L264)

### `lib/artcraft/lib-artcraft.sh` (3)

- [x] `CheckArtCraftDownloads` — [line 6](../../lib/artcraft/lib-artcraft.sh#L6);
  standalone archive reference, not a v3 operation.
- [x] `GetArtCraft` — [line 12](../../lib/artcraft/lib-artcraft.sh#L12);
  standalone archive reference, not the v3 installation route.
- [x] `GetArtCraftDependencies` — [line 19](../../lib/artcraft/lib-artcraft.sh#L19);
  standalone archive reference, not the v3 installation route.

The owner selected the [publisher OCI Flatpak path](../migrations/artcraft-flatpaks.md)
for ArtCraft Launcher and the published Craft apps on Fedora 44 and 45
Workstation x86_64. Candidate acceptance requires install, launch without
errors, and uninstall on each target. All 14 refs passed on Fedora 44
Workstation; Fedora 45 is pending a verified image. See the
[acceptance record](../acceptance/package.artcraft-oci.md). The archive
script remains separate.

## Review feedback contract

For every checked item, copy this block into the review notes or reply with
one block per item. A group decision may cover several functions only when
the old functions have the same behavior and the decision explicitly names
every affected function. I will treat only these stated decisions as
authorization to update migration records or implement changes.

```text
Source function(s):
Source file and line(s):
Observed behavior (include commands, packages, files, network/service effects):
Current consumers or presets:
Decision: retain as reference | standalone utility | map to existing v3 operation | migrate in v3.0 | defer to v3.1+ | retire
If mapping/migrating: v3 operation ID or proposed capability:
Target(s): Fedora release, edition, architecture (or none)
Reason and required user outcome:
Source/license or publisher concern:
Data/state ownership and recovery expectations:
Evidence needed before claiming supported:
Related functions/products reviewed together:
Owner/reviewer and date:
```

For the ten Flatpak pairs, make the decision for the pair and explicitly say
whether the old per-user Flatpak behavior is equivalent to an existing v3
deployment. “Same product” alone is not an equivalence decision. For any
decision that changes shared CLI/catalog meaning, retain the explicit target,
source, scope, deployment, and recovery distinctions required by the behavior
contract.
