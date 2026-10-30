# `package.dc3dd` acceptance

Status: **PASS; supported** on Fedora 44 x86_64 Workstation. Reviewer: Codex,
2026-10-30. The v2 `InstallDc3dd`/`RemoveDc3dd` pair installs and removes the
Fedora `dc3dd` RPM. RIDE v3 does not run a disk copy or wipe command. The
[Fedora package record](https://packages.fedoraproject.org/pkgs/dc3dd/dc3dd/)
provided the current source and GPL-3.0-or-later license.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`,
`VARIANT_ID=workstation`, disposable overlay
`20261030T105721Z-test-native-forensic-and-desktop-applications-batch-a296a16c`,
candidate catalog SHA-256
`03894b8a038c052e7e6a488e33f755e9644babc93b62feb5ca68e9b72510aa10`.
The retained `transcript.jsonl` and `metadata.json` show the Fedora update
preparation and exact guest commands. The batch JUnit file
`.acceptance-runs/native-rpm-04.xml` later failed at qBittorrent's headless
launcher probe; the complete earlier `dc3dd` lifecycle is independently
passing evidence.

The `dc3dd` test checked an absent plan without a journal, applied with
`--allow-candidate`, verified a complete changed journal, signed RPM and
files, `dc3dd --version`, installed status, and an unchanged repeat. Restore
and explicit remove both returned the complete RPM inventory to baseline.
No manual session was needed. The unchanged DNF handler's separate
failure-injection evidence is in [base package checks](package.exfatprogs.md).
The [batch investigation](../migrations/native-rpm-04.md) and
[Windows alignment review](../windows-alignment.md#fedora-workstation-package-batch-04-2026-10-30)
record source and target scope. Promotion changes only catalog status and
acceptance path.
