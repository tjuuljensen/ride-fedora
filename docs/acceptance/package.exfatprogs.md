# `package.exfatprogs` acceptance

Status: **PASS; supported** on the two declared Fedora 44 x86_64 editions.
Reviewer: Codex, 2026-10-30. The owner confirmed no non-disposable v3 runs,
so no older run journal needs original-catalog recovery before promotion.
VM acceptance evidence for each declared edition is listed below.
Product: Fedora `exfatprogs` RPM, installed deployment, `fedora-rpm` source,
system scope, `remove-new-install` recovery. The [Windows comparison](../windows-alignment.md)
found no unexplained shared package-contract drift. No Windows installer fact
was copied into this Fedora operation.

| Exact target | Outcome and evidence |
| --- | --- |
| Fedora 44 Cloud Base x86_64, `VARIANT_ID=cloud` | PASS: pinned image SHA-256 `28680fe5b371a5a82ebf43a31926e086a168e59949d03969c5093e7071f90b7f`; clean-commit lifecycle and injected failure in the [Cloud Base pilot](package.exfatprogs-cloud-base-pilot.md), plus [edition gate](fedora-44-variant-gate-pilot.md). This is a generic package target, not Workstation or Server evidence. |
| Fedora 44 Workstation x86_64, `VARIANT_ID=workstation` | PASS: pinned image SHA-256 `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`; lifecycle overlay `20261030T071040Z-test-package-apply-repeat-status-restore-and-remove-e0ca920e`, injected-failure overlay `20261030T071417Z-test-partial-failure-records-completed-step-and-can-restore-9db5a3bb`, and [batch record](workstation-package-batch-1-pilot.md). |

The tests checked read-only plan, absent-state install, repeat apply, status,
RPM signature/files, dry-run restore, restore, explicit install/remove,
inventory recovery, and partial-failure journal/recovery. The unchanged DNF
handler and source connect the Cloud Base and Workstation observations, while
the Workstation lifecycle and edition gate separately establish that target.
The [default profile smoke](workstation-default-profile-pilot.md) passed. No
manual session was needed.

Workstation lifecycle catalog SHA-256 was
`3d01f975860b02f7f87b4ec06bb6824c3b8df269eaab8bdfb0ca90a564a72dd0`;
the edition gate used
`884bcf10405caabee27b8d8ae32a66a06f309680a20339f64d6b6e50c5f6b3b0`.
The Workstation source was uncommitted during both runs; each overlay retains
`metadata.json` and `transcript.jsonl` with exact bundle hashes. Technical
review on 2026-10-30: Codex checked the Fedora
[package record](https://packages.fedoraproject.org/pkgs/exfatprogs/exfatprogs/)
against the catalog product, Fedora 44 build, upstream link, and license;
the cited Cloud Base and Workstation JUnit suites have no failures. The
archived `lib/v3/providers.sh` and `lib/v3/state.sh` match commit `81f604f`
byte for byte. Relative to the Workstation lifecycle archive, this operation
changed only its target declaration; the later Cloud Base and Workstation
edition gate covered that change. The local non-disposable run directory was
also absent. The catalog links this record as its `acceptanceEvidence`.

The [supported-state promotion check](fedora-44-supported-promotion.md) passed
on all declared Fedora 44 editions without `--allow-candidate`.
