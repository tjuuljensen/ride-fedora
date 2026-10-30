# `package.speedtest-cli` acceptance

Status: **PASS; supported** on Fedora 44 x86_64 Workstation. Reviewer: Codex,
2026-10-30. The v2 Speedtest CLI pair installs and removes the Fedora
`speedtest-cli` RPM. The [Fedora package record](https://packages.fedoraproject.org/pkgs/speedtest-cli/speedtest-cli/)
provided the current source and Apache-2.0 license. RIDE installs the command
but does not perform a network bandwidth test.

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

The test checked an absent plan without a journal, applied with
`--allow-candidate`, verified a complete changed journal, Fedora signature
and files, `speedtest-cli --version`, installed status, and an unchanged
repeat. Restore and explicit remove returned the complete RPM inventory to
its pre-operation state. No manual session was needed. Promotion changes only
catalog status and acceptance path; source, target, DNF handler, and recovery
stay unchanged. The [batch record](../migrations/native-rpm-03.md) and
[Windows alignment review](../windows-alignment.md#fedora-workstation-package-batch-03-2026-10-30)
cover source ownership and cross-platform scope.
