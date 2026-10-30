# `package.hexchat` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 x86_64 Workstation.
Reviewer: Codex, 2026-10-30. The v2 HexChat pair installs and removes the
Fedora `hexchat` RPM. The [Fedora package record](https://packages.fedoraproject.org/pkgs/hexchat/hexchat/)
shows the exact source and license; the package is presently orphaned in Fedora.
RIDE does not change IRC accounts or user settings.

VM evidence: pinned Fedora 44 x86_64 Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`,
`VARIANT_ID=workstation`, disposable overlay
`20261030T104045Z-test-native-active-workstation-applications-batch-be719a0d`,
candidate catalog SHA-256
`f0eea6b9232e5025fbfaf06f5e0a537e90fa4713483a08904ce934d05f318a09`.
The retained `transcript.jsonl` and `metadata.json` record the refreshed image
preparation, source bundle, guest commands, and full RPM inventories. The
batch JUnit file `.acceptance-runs/native-rpm-03-retry.xml` ended failed only
at the later Chromium executable-name probe; the completed operation steps
below are individually passing evidence. The unchanged Fedora DNF handler's
failure-injection evidence remains in [base package checks](package.exfatprogs.md).

The HexChat test checked an absent plan without a journal, applied with
`--allow-candidate`, verified a complete changed journal, signed RPM and
files, `hexchat --version`, installed status, and an unchanged repeat. Restore
and explicit remove both removed `hexchat`. DNF retained `gtk2`, `ibus-gtk2`,
and `libcanberra-gtk2`, all introduced by the HexChat install; no pre-existing
RPM was lost or changed. The [batch investigation](../migrations/native-rpm-03.md)
records the first failed inventory assertion and the revised opt-in candidate
criterion. Broader dependency cleanup, failure/recovery, and visual checks are
in the named v3.1 queue. No manual session was required to establish the
package-install outcome. Keep `--allow-candidate` explicit.
