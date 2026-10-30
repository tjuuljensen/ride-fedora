# `package.binwalk` acceptance

Status: **PASS; supported Fedora RPM** on Fedora 44 x86_64 Workstation,
2026-10-30. The signed Fedora
[`binwalk`](https://packages.fedoraproject.org/pkgs/binwalk/binwalk/) RPM
provides Binwalk 3.1.0. This is a Rust-based upstream revision; its CLI and
plugin behavior may differ from the older v2-era Python release. The v3
operation installs the RPM, not firmware samples or legacy plugins.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T123040Z-test-forensic-binwalk-and-autopep8-fedora-packages-a3f34aa7`;
candidate catalog SHA-256
`dd622850634ed07bf5f723a6be1b0b77dd25a64f99a8ad7c5e60f0d64099e9c6`.
The retained transcript and `.acceptance-runs/forensic-isolated-03-native.xml`
record one passing shared test. Binwalk was absent initially. It passed
absent plan, candidate-gated apply, RPM signature and file verification,
`/usr/bin/binwalk --version`, installed status, unchanged repeat, restore,
and explicit install/remove. The inverse removed Binwalk and preserved
pre-existing RPM identities; any retained dependencies were introduced by
this test. The final supported catalog status removes the temporary
candidate flag; handler and target are unchanged. The unchanged DNF
handler's mocked failure check is recorded in the
[base package evidence](package.exfatprogs.md).

No firmware extraction, plugin compatibility, or other distro/edition was
accepted. See the [batch review](../migrations/forensic-isolated-03.md).
