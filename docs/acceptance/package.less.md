# `package.less` acceptance draft

Status: `candidate`; target-specific VM checks passed on 2026-10-30, with
promotion review pending. Product: Fedora `less` RPM, installed deployment,
`fedora-rpm` source, system scope, `remove-new-install` recovery. The selected
source and DNF handler are unchanged from the earlier Cloud Base package
pilot. The scoped [Windows comparison](../windows-alignment.md) found no
unexplained shared-contract drift.

| Exact target | Outcome and evidence |
| --- | --- |
| Fedora 44 Workstation x86_64, `VARIANT_ID=workstation` | PASS: pinned image SHA-256 `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`; lifecycle overlay `20261030T071555Z-test-package-apply-repeat-status-restore-and-remove-410a0bce` and [batch record](workstation-package-batch-1-pilot.md). The [edition gate](fedora-44-variant-gate-pilot.md) passed separately. |
| Fedora 44 Server x86_64, `VARIANT_ID=server` | PASS: pinned image SHA-256 `efb75956d6dbde0801059fdac4a8a1451f06ecc843344ecdb71bb3e8d247af90`; lifecycle overlay `20261030T075528Z-test-package-apply-repeat-status-restore-and-remove-ca299d76`, failure overlay `20261030T075630Z-test-partial-failure-records-completed-step-and-can-restore-78ec4dfa`, edition gate, and [Server record](server-base-package-pilot.md). |

The tests checked read-only plan, absent-state install in a disposable overlay,
repeat apply, status, RPM signature/files, dry-run restore, restore, explicit
install/remove, and package inventory recovery. The Server failure injection
recorded a changed step followed by a failed missing package and restored the
completed step. The unchanged DNF handler and source let this failure result
cover the Workstation `less` batch without another identical failure run. The
[default](workstation-default-profile-pilot.md) and `server-base` profile
smokes passed. No manual session was needed.

Source was uncommitted during the VM pilots. Workstation lifecycle catalog
SHA-256 was `3d01f975860b02f7f87b4ec06bb6824c3b8df269eaab8bdfb0ca90a564a72dd0`;
the Server pilot used
`27e2a8310a56123488a25a3c9dd74631365e4acbe8085e542247d9280f4d6bf5`.
The later Server target addition changes this operation's source signature;
the old Workstation overlay is behavior evidence, and its journal must be
recovered with its original catalog. Each overlay's `metadata.json` and
`transcript.jsonl` retain commands and exact source bundle hashes. Reviewer:
pending. Local non-disposable run directory was absent; other hosts have not
yet been inventoried.
