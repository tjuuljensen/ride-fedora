# v3.0 migration release review

Status: **not ready for a release tag**, reviewed 2026-11-05. No v3 tag has
been published; master remains the release line. The checked-in
[migration progress report](migrations/progress.md), generated from
migration/outcomes.json, is authoritative for batch counts and next actions.

The current ledger has **182/185 outcomes dispositioned**: 51 supported, 102
opt-in candidates, 10 replaced, 11 retired, 8 unsupported, and 3 unresolved.
For package and setting capabilities, **150/169 have an operable v3.0 path**;
10 are owner-retired, 6 have a functional replacement, and 3 remain gaps.
The currently tested target matrix is Fedora 44 x86_64 by declared edition.
Fedora Linux 45 was released on 2026-11-03, so v3.0 must make an explicit
support-target decision before the scope is frozen: either add Fedora 45 for
each claimed edition and rerun the applicable acceptance, or retain Fedora 44
as the only supported release with a recorded reason and follow-up. The accepted
default Workstation and server-base Server profiles remain small; Cloud Base
acceptance covers package.exfatprogs only. Fedora 45 release status is confirmed
by the [Fedora Linux 45 announcement](https://fedoramagazine.org/announcing-fedora-linux-45/).

## Current v3.0 gaps

Each gap needs a working, risk-appropriate v3 path or an explicit
owner-approved disposition before the release scope is frozen. Do not count
an implemented installer, similar product name, or candidate profile as proof
of the source capability.

| Outcome | Remaining issue | Recommendation |
| --- | --- | --- |
| [workstation:package.VMFStools](MIGRATION-PLAN.md#full-scoped-v2-migration-program) | The experimental reader installer is available as an opt-in candidate for owner testing. No genuine VMFS6 fixture has been read; image access, read-only behavior, and unchanged digest are unverified. | The owner approved deferring H118 fixture testing to v3.1 while keeping the opt-in install candidate available. Keep actual VMFS6 access unverified; complete fixture-backed read-only lifecycle evidence under H118 before claiming it. |
| workstation:package.ScheduleExpVPNChange | The old six-hour ExpressVPN rotation depends on mutable disconnect-first behavior. Current v14 location changes, safe connection replacement, and route/DNS recovery have not been verified on Workstation. | Do not recreate an unattended timer yet. Verify the current client and recovery on a disposable Workstation VM, or record an owner-approved retirement/deferral for v3.0. Keep manual rotation separate. |
| server:setting.VPNRandomizerPersistent | Source consumers exist in network-devices, but deployed hosts, executor identity, crontab owner, publication path, and rollback are unverified. VPN recovery is also unverified on Server. | Reconcile runtime ownership with the network-devices owner before moving behavior. Then test an owned timer and network recovery on disposable Server, or explicitly defer it while leaving the authoritative source in place. |

The [v3.0 path reassessment](migrations/v30-path-reassessment.md) records why
kept package and setting capabilities need a working path or an explicit
owner decision. The [progress report](migrations/progress.md) links each
gap to its batch record and current next action.

## Shared behavior and release alignment

The shared behavior contract is version 1.1.0. ALIGN-06 is complete; ALIGN-03
through ALIGN-05 and ALIGN-07 through ALIGN-09 remain open. The [final-v3
alignment register](MIGRATION-PLAN.md#cross-platform-alignment-for-final-v3)
has the owner and completion evidence for each task.

- Fedora has implementation and focused coverage for ALIGN-03 and ALIGN-04;
  the Windows counterparts and paired review remain open.
- Fedora pins and checks the 12-case shared scenario set for ALIGN-05. The
  Windows Pester adapter has not been executed in this environment.
- ALIGN-07 still needs linked-change review guidance and a read-only drift
  report.
- Fedora's ALIGN-08 output and status selectors are implemented with focused
  coverage. Paired machine-output review and Windows test execution remain.
- ALIGN-09 requires an immutable published contract reference, verified pins,
  and a final consumer review.

Complete the open tasks before release or record explicit owner-approved
deferrals and their reasons and review triggers. Candidate behavior remains
blocked by default. Promote support only with acceptance on the exact declared
target.

## Legacy source scope

The main ledger does not cover every helper library in the repository. The
[supplementary legacy source audit](legacy-source-audit.md) identifies 87
functions across seven older helper groups that are absent by exact name from
the 185-row ledger. This is not a request to add 87 catalog operations. Before
v3.0, record owner-approved decisions about whether those groups remain
reference-only, standalone utilities, or candidates for later migrations.
Review the ten unmatched Flatpak install/remove pairs individually; a similar
v3 product ID does not prove equivalent source or recovery behavior.

The Firefox add-on lifecycle is no longer a migration gap. Its 16-XPI
Workstation lifecycle passed as an opt-in setting.firefox-addons candidate.
Keep it candidate-gated while H115 reviews publisher license metadata,
updates, and profile migration behavior. Broader visual, compatibility, and
failure-matrix work remains in the v3.1 hardening queue.

## Recommended release sequence

1. Resolve the remaining package/setting gaps above, or carry forward
   explicit owner-approved deferrals. The VMFS6 reader install candidate may
   remain opt-in for owner testing; VMFS6 image access stays unverified until
   H118 passes in v3.1.
2. Close ALIGN-03 through ALIGN-09 or document approved deferrals with owners,
   reasons, evidence, and review triggers.
3. Confirm supplementary source groups are not advertised or executed as v3
   operations; add a checked inventory or explicit reference/standalone
   classification before freezing the scope.
4. Resolve the Fedora 45 target decision above. If Fedora 45 is supported,
   update the pinned image matrix and run acceptance for every claimed edition;
   retain Fedora 44 regression coverage if it remains in the support matrix.
   If support stays on Fedora 44, state why and record the Fedora 45 follow-up.
5. Regenerate the progress, burndown, command, and operation references from
   their sources. Run the repository's required syntax, ShellCheck, schema,
   mocked, Firefox, executable-mode, and generated-documentation checks.
6. Recheck CI and the declared Fedora VM acceptance records against the final
   release source. A previous source revision or a different Fedora edition
   does not establish the final target result.
7. Update release/bootstrap metadata and publish the immutable contract
   reference before creating the v3.0 tag. Do not move master as a side
   effect of preparing that tag.

The accepted base profiles and per-operation evidence are recorded in the
[migration plan](MIGRATION-PLAN.md) and [acceptance records](acceptance/README.md).
No new VM acceptance is claimed by this documentation review.

## Local validation follow-up, 2026-11-05

Two required checks still fail on this branch. `tools/check-shell-executable.sh`
reports Git mode `100644` for `lib/v3/email_header_analyzer.sh`,
`lib/v3/keyfile_mounts.sh`, and `lib/v3/networkmanager-vpn-profiles.sh`; the
repository policy requires `100755` for tracked `.sh` files. Full ShellCheck
on `ride.sh`, `lib/v3/catalog.sh`, and `lib/v3/providers.sh` reports only
existing diagnostics in `lib/v3/providers.sh` outside the TMOG handler
(SC2034, SC2016, SC2015, and SC2174). The earlier TMOG-focused run passed
with those codes excluded, which does not close the full ShellCheck gate.
The RIDE Fedora maintainer should fix the file modes and assess the specific
diagnostics, then rerun both checks before the v3.0 release review closes.
