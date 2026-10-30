# Native RPM batch 01: six v2 command-line tools

Status: **PASS; six operations supported on Fedora 44 x86_64 Workstation**,
2026-10-30. Reviewer: Codex.
Source: the six `Install*`/`Remove*` pairs in `lib-fedora.sh` at v2 commit
`43ba467`. Each pair only calls `dnf -y install` or `dnf -y remove` for its
named RPM; no user configuration or downloaded script is part of its behavior.
The v3 replacement is one stable package operation per tool, installed from
Fedora's signature-enforced repository on Fedora 44 x86_64 Workstation only.

| v2 outcome | Fedora 44 RPM | Current Fedora package record | License recorded by Fedora |
| --- | --- | --- | --- |
| `package.Pwgen` | `pwgen` | [pwgen](https://packages.fedoraproject.org/pkgs/pwgen/pwgen/) | GPL-1.0-or-later |
| `package.Htop` | `htop` | [htop](https://packages.fedoraproject.org/pkgs/htop/htop/) | GPL-2.0-or-later |
| `package.Bat` | `bat` | [bat](https://packages.fedoraproject.org/pkgs/rust-bat/bat/) | Fedora's multi-license Rust dependency expression |
| `package.Ncdu` | `ncdu` | [ncdu](https://packages.fedoraproject.org/pkgs/ncdu/ncdu/) | MIT |
| `package.Ripgrep` | `ripgrep` | [ripgrep](https://packages.fedoraproject.org/pkgs/rust-ripgrep/ripgrep/) | Fedora's Rust dependency expression |
| `package.Fd` | `fd-find` | [fd-find](https://packages.fedoraproject.org/pkgs/rust-fd-find/fd-find/) | Fedora's Rust dependency expression |

The Fedora package records show a Fedora 44 build for each RPM. `fd-find` is
the v2 package name; do not substitute a similarly named `fd` package. Source
selection, product identity, and license are recorded per operation in the
catalog. The Linux Fedora RPM provider and journal behavior are unchanged.

## Completion criteria defined before the VM run

- Keep `default` unchanged. Add one opt-in `cli-tools` profile containing these
  six operations only after catalog and mocked checks pass. Scope each new row
  to Fedora 44 x86_64 Workstation and start as `candidate`.
- Mock plan/apply, repeat, status, explicit remove, and restore routing for the
  six IDs. Check unknown editions fail closed and the candidate gate remains.
- In one disposable pinned Workstation overlay, establish each package's prior
  RPM state, then verify plan, install, repeat unchanged, status, Fedora RPM
  signature/files, declared remove or restore, and package inventory recovery.
  If an RPM is preinstalled, use `dnf remove --assumeno` first and remove it in
  the overlay only when the transaction affects no other installed package;
  otherwise retain an installed-only contract and record that limit.
- Reuse the previously accepted Fedora DNF handler failure and journal evidence
  only if the provider and source signature fields remain unchanged. A failure
  in the new batch is investigated before any retry. No manual session is
  needed for these command-line packages.
- Promote only the operations that pass on this exact target, with their own
  acceptance records. Update the six ledger rows and this batch's evidence;
  leave failures unresolved with a concrete blocker and next action.

Windows development branch `codex/ride-v3-migration` at `17f9cef` has no
matching catalog IDs for these six Fedora CLI packages. Linux catalog schema 3,
profile schema 1, and run schema 2 keep the already reviewed installed RPM
identity, explicit source, and recovery semantics. No shared product or
package-contract change is introduced. Recheck at this batch's promotion and
at release-candidate preparation.

## Dated acceptance result

The candidate lifecycle ran in pinned Workstation overlay
`20261030T095336Z-test-native-cli-tools-batch-a7b5f543` against catalog
SHA-256 `7ee457d64387bfc206b6953c2547691aa047926eae4e68893db74b1857c55b7e`.
All six packages were absent initially. One automated test passed, with zero
failures, errors, or skips. Each operation passed plan, install, repeat,
status, Fedora RPM signature/files, restore, explicit remove, and complete
package inventory recovery. The unchanged Fedora DNF provider's earlier
[failure and recovery evidence](../acceptance/package.exfatprogs.md) applies
to this batch. Per-operation records:
[pwgen](../acceptance/package.pwgen.md),
[htop](../acceptance/package.htop.md),
[bat](../acceptance/package.bat.md),
[ncdu](../acceptance/package.ncdu.md),
[ripgrep](../acceptance/package.ripgrep.md), and
[fd-find](../acceptance/package.fd-find.md).

After status and acceptance-path promotion, a second disposable Workstation
overlay `20261030T095818Z-test-native-cli-tools-supported-profile-smoke-87f60ec2`
ran catalog SHA-256
`5b0ff0f1c03cfd2518f2d9564b09b38d7bbe42fe581d2a0abe30999437ffcca7`.
`cli-tools` planned and applied all six without `--allow-candidate`, repeated
unchanged, reported supported status, and restored the original inventory.
Its JUnit file `.acceptance-runs/native-cli-01-supported.xml` reports one
pass, zero failures, errors, or skips. Both overlays used pinned image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
their metadata and transcripts retain exact source bundle hashes. No manual
session was needed.
