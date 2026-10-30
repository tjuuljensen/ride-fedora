# `package.cheat` acceptance

Status: **PASS; supported Fedora RPM** on Fedora 44 x86_64 Workstation,
2026-10-30. Fedora's signed
[`cheat`](https://packages.fedoraproject.org/pkgs/cheat/cheat/) RPM replaces
the v2 moving binary download into `/bin`. The upstream program is MIT;
the Fedora RPM lists Apache-2.0, BSD, ISC, and MIT component licenses.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T131827Z-test-projecteur-and-cheat-native-packages-90ab3f93`;
candidate catalog SHA-256
`5a63636b2a21a1e668b0b50fa70be2bc24e0891848c8a0e540c4f0868d491e3f`.
The retained transcript and `.acceptance-runs/publisher-apps-13-16-native.xml`
record one passing shared test. `/bin/cheat` was not RPM-owned at baseline
and the package was absent. It passed plan, candidate-gated apply, RPM
signature/files, `cheat --version` (4.4.2), installed status, unchanged
repeat, restore, and explicit install/remove. Pre-existing RPM identities
were preserved. The final supported status removes the temporary candidate
gate with the same target and DNF handler. Mocked DNF failure evidence is
reused from [base acceptance](package.exfatprogs.md).

The test did not fetch or edit personal cheatsheets. See the
[batch review](../migrations/publisher-apps-16.md).
