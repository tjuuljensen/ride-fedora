# `package.htop` acceptance

Status: **PASS; supported** on Fedora 44 x86_64 Workstation. Reviewer: Codex, 2026-10-30.
The v2 `InstallHtop`/`RemoveHtop` pair used only `dnf -y` on the `htop` RPM.
The v3 operation keeps that installed-package behavior, uses the existing
Fedora RPM provider and `remove-new-install` recovery, and does not modify
user configuration. The [Fedora package record](https://packages.fedoraproject.org/pkgs/htop/htop/) supplied the Fedora 44
source and license review.

VM acceptance evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`,
`VARIANT_ID=workstation`, overlay
`20261030T095336Z-test-native-cli-tools-batch-a7b5f543`, candidate catalog
SHA-256 `7ee457d64387bfc206b6953c2547691aa047926eae4e68893db74b1857c55b7e`.
The retained `.acceptance-runs/native-cli-01.xml` reports one batch test passed,
zero failures, errors, or skips. Its overlay `metadata.json` and
`transcript.jsonl` record the image, source bundle, and guest commands.

The test established `htop` absent, planned an install without creating a
journal, then applied with the explicit candidate override. It verified a
complete changed journal, installed RPM, Fedora signature and files, installed
status, and an unchanged repeat. Restore removed the new install and recovered
the complete RPM inventory; explicit install and remove did the same. The
unchanged Fedora DNF handler's separate failure and recovery evidence is in
the [accepted base package checks](package.exfatprogs.md). No manual session
was needed for this command-line package.

The [batch assessment](../migrations/native-rpm-01.md) and
[Windows alignment review](../windows-alignment.md#fedora-cli-package-batch-01-2026-10-30)
record source ownership and cross-platform scope. The [supported `cli-tools` profile check](../migrations/native-rpm-01.md)
passed without `--allow-candidate` in disposable overlay
`20261030T095818Z-test-native-cli-tools-supported-profile-smoke-87f60ec2`.
Its catalog SHA-256 was
`5b0ff0f1c03cfd2518f2d9564b09b38d7bbe42fe581d2a0abe30999437ffcca7`;
`.acceptance-runs/native-cli-01-supported.xml` reports one pass and no
failures, errors, or skips. The profile installed all six packages, repeated
unchanged, reported supported status, and restored the original inventory.
Only catalog status and acceptance paths changed between the two VM runs;
handler, target, source, and recovery fields remained unchanged.
