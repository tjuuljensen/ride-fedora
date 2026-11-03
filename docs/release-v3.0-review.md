# v3.0 migration release review

Status: **coverage review reopened**, 2026-11-03. No v3 release tag has been published;
`master` remains the release line. The checked-in
[progress report](migrations/progress.md) is authoritative for current
counts. At the earlier candidate revision, all 180 then-scoped v2 outcomes had a
decision: 28 supported, 26 operable opt-in candidates, 13 replaced,
17 retired, and 96 unsupported. Thus 54 source outcomes are runnable; 26
of those require `--allow-candidate`. The 126 non-runnable decisions do
not represent working installs. The two Citrix and 13 host-specific server
exclusions remained outside that historical denominator. The current ledger
has 185 outcomes and eleven exclusions. The owner's later
[v3.0 capability clarification](migrations/v30-path-reassessment.md) makes
working package and setting paths or explicit owner retirement part of v3.0
completion. The current ledger reports 180/185 outcomes dispositioned (97.3%)
and 148/169 package/setting capabilities operable (87.6%), with five unresolved
source outcomes and five capability gaps. ExpressVPN Workstation startup
auto-connect now has a documented publisher-GUI replacement; old unowned cron
cleanup remains manual. The ExpressVPN Workstation and Server package outcomes
remain open pending authenticated artifacts and exact-target lifecycle
evidence. The remaining gaps are VMFS6 access, ExpressVPN package installation
on both editions, Workstation scheduled rotation, and Server VPN rotation.
The experimental pinned VMFS6 CLI is available through an explicit opt-in
install profile for owner testing; that install path does not close the VMFS6
access gap or establish read-only behavior against a genuine VMFS6 image.
Citrix and Opera remain out of scope. This review is not release-ready; use the
generated progress report for current batch evidence and next actions.
The standalone MAC vendor lookup scripts are a separately counted functional
replacement; their RIDE-managed lifecycle is in the v3.1 queue.

The support matrix is Fedora 44 x86_64 on the edition declared by each
operation. The small `default` and `server-base` profiles retain their
separate VM acceptance. Optional supported packages and settings live in
curated profiles; they are not silently added to either base profile.

## Candidate use in v3.0

Candidate operations are blocked by default. An operator must explicitly
select the operation or opt-in profile and pass `--allow-candidate` for
state-changing commands. Their focused happy-path evidence is linked from
the [operation reference](OPERATIONS.md); named broader work is in the
[v3.1 hardening queue](migrations/progress.md). Candidate profile membership
changes with migration batches; the current [profile definitions](../profiles/)
and generated [operation reference](OPERATIONS.md) are authoritative. A
candidate absent from profiles remains individually selectable only through
the explicit candidate gate. Neither catalog presence nor opt-in selection
adds an operation to `default` or `server-base` or claims behavior beyond its
recorded target and evidence.

Security, storage, encryption, VPN credentials, Docker service and data,
host-specific server behavior, and other unsupported source outcomes remain
non-runnable until their ledger review triggers are met. Package-only
KeePassXC and NetworkManager plugin support covers signed RPM lifecycle and
seeded-state preservation; it does not manage vaults or VPN connections.
`package.smartmontools` is an opt-in candidate whose Fedora 44 Workstation
handler disables and stops the `smartd` service after package installation;
the acceptance record verifies package lifecycle without scanning devices.

## Cross-platform alignment gate, 2026-11-01

The user added [ALIGN-01 through ALIGN-09](MIGRATION-PLAN.md#cross-platform-alignment-for-final-v3)
to final-v3 goals in both repositories. Contract 1.1.0, matching digest references
and reciprocal AGENTS rules are adopted (ALIGN-01/02). This does not close the
runtime/test/release work or replace the scoped capability requirements above.

- [ ] Complete ALIGN-03 through ALIGN-08, or record explicit owner-approved
  deferrals, with applicable native/mock evidence and tracked platform differences.
- [ ] Complete ALIGN-09: published immutable contract reference, verified pins,
  final consumer review and no unexplained shared-contract drift.

As of 2026-11-03, Fedora has implemented and focused-tested its ALIGN-03 CLI
selection/removal rules and ALIGN-04 candidate download and restore-preview
preflight. The shared scenario set is revision 1.1.0 with 12 mapped cases;
Fedora's scenario checker and six focused tests pass, including privilege
refusal and dependency-removal order. The Windows adapter and Pester tests are
present and parse successfully, but Pester is not installed in this environment,
so Windows execution remains unverified. Fedora's 20-entry capability register
and batch-reconciliation index validate successfully. Fedora also implements
the ALIGN-08 `show --stdin` interface with schema-1 JSON records and focused CLI
coverage. Explicit status ID/view selectors are now implemented in both clients
with their existing positional syntax preserved. Paired profile/status and
state-preview examples are in both READMEs. Focused Windows Pester tests are
added but await execution. Machine-output verification, ALIGN-07 drift
reporting, and ALIGN-09 immutable contract publication remain open. These
updates do not close the paired ALIGN-03 through ALIGN-08 tasks.

The historical checks below remain evidence for their stated revisions; they
do not certify the newly adopted shared contract or final release source.

## Review checks

- [x] Verify the final generated catalog, burndown, and progress reports,
  mocked and Firefox tests, shell checks, and acceptance test collection.
- [x] Verify the promoted optional package-only profiles on the pinned
  Workstation VM without a candidate override; retain other valid VM
  evidence for unchanged handlers and profiles.
- [x] Verify migration-branch CI and the last Windows catalog, profile,
  run-state, and product alignment record.

Implementation commit `445810a` passed the
[v3 validation workflow](https://github.com/tjuuljensen/ride-fedora/actions/runs/41070406118)
and [shell executable-mode workflow](https://github.com/tjuuljensen/ride-fedora/actions/runs/41070406164).
The [final Windows comparison](windows-alignment.md#package-only-security-batch-and-final-v30-alignment-2026-10-30)
found no unexplained shared-contract drift at `4c90577`.

## Current worktree validation, 2026-11-03

The current Fedora worktree passes `migration_progress.py --check`,
`validate_v3.py --check-docs` (354 operations and 164 profiles),
`build_burndown.py --check` (185 source outcome rows),
`check_alignment_register.py` (21 entries),
`check_behavior_scenarios.py --check` (12 mapped cases),
`check-shell-executable.sh`, and `git diff --check`. The complete mocked
Python suite passes **337/337 tests**; pytest collects **159 acceptance tests**.
This is a local run, not a new GitHub Actions or Fedora VM acceptance result.
Windows Pester remains unexecuted in this environment. The current v3.0
coverage gaps and their required evidence remain listed above and in the
generated progress report.

Publishing a v3 tag and moving `master` are separate release decisions. This
migration branch does neither automatically.
