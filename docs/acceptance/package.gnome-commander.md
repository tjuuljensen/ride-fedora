# `package.gnome-commander` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 x86_64 Workstation,
2026-10-30. Fedora's signed
[`gnome-commander`](https://packages.fedoraproject.org/pkgs/gnome-commander/gnome-commander/)
RPM supplies the twin-panel graphical file manager. The package declares
GPL-3.0-or-later, GFDL-1.3-or-later, and CC0-1.0 components.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T130122Z-test-commander-file-managers-opt-in-packages-and-profile-09dd68d5`;
candidate catalog SHA-256
`e1be762304c04802276ff721d5c3ec9783e7382d4aac1156c9ef76904eb95f31`.
The retained transcript and `.acceptance-runs/publisher-apps-09-commander.xml`
record one passing shared test. The RPM was absent at baseline. It passed
plan, candidate-gated apply, signature/files, executable presence,
installed status, unchanged repeat, restore, and explicit install/remove.
The `commander-file-managers` profile installed and restored it with
`package.mc`, preserving pre-existing RPM identities. Mocked DNF failure
evidence is reused from [base acceptance](package.exfatprogs.md).

A GNOME session visual check and broader recovery are
[v3.1 item H014](../migrations/progress.md). See the
[batch review](../migrations/publisher-apps-09.md).
