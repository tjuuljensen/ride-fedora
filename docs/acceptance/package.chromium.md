# `package.chromium` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 x86_64 Workstation.
Reviewer: Codex, 2026-10-30. The v2 Chromium pair installs and removes the
Fedora `chromium` RPM. The [Fedora package record](https://packages.fedoraproject.org/pkgs/chromium/chromium/)
provided the current source and composite license. RIDE does not change
browser profiles or system defaults.

VM acceptance evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`,
`VARIANT_ID=workstation`, disposable overlay
`20261030T105029Z-test-native-chromium-probe-and-lifecycle-7d5b7140`,
candidate catalog SHA-256
`f0eea6b9232e5025fbfaf06f5e0a537e90fa4713483a08904ce934d05f318a09`.
The retained `.acceptance-runs/native-rpm-03-chromium.xml` reports one pass,
zero failures, errors, or skips. Overlay `metadata.json` and
`transcript.jsonl` record the refreshed image preparation, source bundle, and
guest commands.

The test checked an absent plan without creating a journal, applied with
`--allow-candidate`, verified a complete changed journal, signed RPM and
files, `chromium-browser --version`, installed status, and an unchanged
repeat. Restore and explicit remove both removed `chromium` and returned the
complete RPM inventory to baseline. The [Fedora 44 file
list](https://packages.fedoraproject.org/pkgs/chromium/chromium/fedora-44.html)
confirms the executable name and desktop entry. The [batch
record](../migrations/native-rpm-03.md) documents the earlier test-probe
failure; the package installer itself did not fail. The unchanged Fedora DNF
handler's separate failure-injection evidence is in [base package
checks](package.exfatprogs.md).

This is a v3.0 opt-in candidate because broader desktop failure, recovery,
visual, and accessibility checks remain in the named v3.1 queue. No manual
session was needed to establish the package-install outcome. Keep
`--allow-candidate` explicit.
