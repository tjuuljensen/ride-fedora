# `package.mc` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 x86_64 Workstation,
2026-10-30. Fedora's signed
[`mc`](https://packages.fedoraproject.org/pkgs/mc/mc/) RPM supplies GNU
Midnight Commander under GPL-3.0-or-later.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T130122Z-test-commander-file-managers-opt-in-packages-and-profile-09dd68d5`;
candidate catalog SHA-256
`e1be762304c04802276ff721d5c3ec9783e7382d4aac1156c9ef76904eb95f31`.
The retained transcript and `.acceptance-runs/publisher-apps-09-commander.xml`
record one passing shared test. The RPM was absent at baseline. It passed
plan, candidate-gated apply, signature/files, `mc --version` with a test
`TERM`, installed status, unchanged repeat, restore, and explicit
install/remove. The `commander-file-managers` profile installed and restored
it with `package.gnome-commander`, preserving pre-existing RPM identities.
Mocked DNF failure evidence is reused from
[base acceptance](package.exfatprogs.md).

Interactive terminal behavior and broader recovery are
[v3.1 item H014](../migrations/progress.md). See the
[batch review](../migrations/publisher-apps-09.md).
