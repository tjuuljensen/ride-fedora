# `package.acpi` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 x86_64 Workstation,
2026-10-30. Fedora's signed
[`acpi`](https://packages.fedoraproject.org/pkgs/acpi/acpi/) RPM provides a
read-only battery and thermal CLI (GPL-2.0-or-later).

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T125426Z-test-logitech-unifying-opt-in-packages-and-profile-28d30baa`;
candidate catalog SHA-256
`392492a4f9290eacd3fcdc7ac115685293869465fe44c43fbe31a7ce868345a1`.
The retained transcript and `.acceptance-runs/publisher-apps-07-solaar.xml`
record one passing shared test. The package was absent at baseline and passed
plan, candidate-gated apply, RPM signature and files, installed status,
unchanged repeat, restore, and explicit install/remove. `acpi --version`
printed 1.8 and returned exit 1 by its own CLI convention; the focused probe
checks the output. The `logitech-unifying` profile installed and restored it
with `package.solaar`. Pre-existing RPM identities were preserved. The DNF
handler's mocked failure evidence is reused from
[base package acceptance](package.exfatprogs.md).

The VM has no physical battery; battery readings are outside this package
installation claim. See the [batch review](../migrations/publisher-apps-07.md).
