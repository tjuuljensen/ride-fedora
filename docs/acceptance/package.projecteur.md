# `package.projecteur` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 x86_64 Workstation,
2026-10-30. Fedora's signed
[`projecteur`](https://packages.fedoraproject.org/pkgs/projecteur/projecteur/)
RPM supplies the Logitech Spotlight pointer application and packaged udev
rule under MIT. The operation installs the package but does not configure
or drive a hardware remote.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T131827Z-test-projecteur-and-cheat-native-packages-90ab3f93`;
candidate catalog SHA-256
`5a63636b2a21a1e668b0b50fa70be2bc24e0891848c8a0e540c4f0868d491e3f`.
The retained transcript and `.acceptance-runs/publisher-apps-13-16-native.xml`
record one passing shared test. The RPM was absent at baseline. It passed
plan, candidate-gated apply, RPM signature/files, executable and udev-rule
presence, installed status, unchanged repeat, restore, and explicit
install/remove. The `spotlight-pointer` profile passed plan/apply/repeat/
restore. Pre-existing RPM identities were preserved; mocked DNF failure
evidence is reused from [base acceptance](package.exfatprogs.md).

No Spotlight device or desktop visual behavior was exercised. These and
broader recovery are [v3.1 item H017](../migrations/progress.md). See the
[batch review](../migrations/publisher-apps-13.md).
