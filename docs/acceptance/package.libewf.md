# `package.libewf` acceptance

Status: **PASS; supported** on Fedora 44 x86_64 Workstation. Reviewer: Codex,
2026-10-30. The v2 `InstallLibEWF`/`RemoveLibEWF` pair used Fedora DNF to
install and remove `libewf`. The RPM is the EWF library, separate from the already cataloged `package.ewftools` utilities candidate. The [Fedora package record](https://packages.fedoraproject.org/pkgs/libewf/libewf/)
supplied the current source and license review.

VM acceptance evidence: pinned Workstation image SHA-256 `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`,
`VARIANT_ID=workstation`, overlay `20261030T102031Z-test-native-forensic-and-package-tools-batch-d11e5c1a`, candidate catalog SHA-256
`f8d098dd274add75ca7ba99dd9af859af6499a2f095ca7332b4a00139e4dc7a4`. The retained `.acceptance-runs/native-rpm-02-final.xml` reports one
batch test passed with zero failures, errors, or skips. The overlay
`metadata.json` and `transcript.jsonl` record the image, source bundle,
preparation, and guest commands. The test refreshed Fedora packages in the
isolated overlay before taking its recovery baseline.

The test established `libewf` absent, planned without a journal, then
applied with `--allow-candidate`. It verified a complete changed journal,
installed signed RPM and its files, installed status, and an unchanged repeat.
Restore and explicit remove both completed. The complete RPM inventory returned to its refreshed baseline after both restore and explicit remove.
The unchanged Fedora DNF handler's separate failure and recovery evidence is
in the [accepted base package checks](package.exfatprogs.md). No manual session
was needed for this package-install outcome.

The [batch assessment](../migrations/native-rpm-02.md) records the investigated
failure on the older VM image and the revised recovery criterion. The
[Windows alignment review](../windows-alignment.md#fedora-rpm-package-batch-02-2026-10-30)
records the cross-platform scope. Promotion changes only the catalog status
and acceptance path, not the handler, source, target, or recovery semantics.
