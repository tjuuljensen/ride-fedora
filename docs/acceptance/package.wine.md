# `package.wine` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 x86_64 Workstation,
2026-10-30. The v2 `InstallWine`/`RemoveWine` pair maps to the signed Fedora
[`wine` RPM](https://packages.fedoraproject.org/pkgs/wine/wine/).
RIDE installs the broad Wine meta-package; it does not run a Windows program
or create a user Wine prefix.

VM evidence: pinned Workstation image SHA-256:
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay:
`20261030T111844Z-test-remaining-native-repository-batch-a48d4efa`;
catalog SHA-256:
`b2ddd2a00a03adb2dd164900eb7b435da01d9001bc844630537732129e5ecd63`.
The retained `transcript.jsonl`, `metadata.json`, and
`.acceptance-runs/native-rpm-05.xml` show a passing absent plan, apply with
`--allow-candidate`, signed RPM and files, `wine` command detection, status,
unchanged repeat, restore, and explicit remove. The named package and all
112 newly introduced RPM identities were absent after both inverse paths.
DNF updated eight pre-existing `samba`/`libldb` family RPMs; their
name/architecture identities remained, and RIDE did not downgrade them.
Broader failure recovery, desktop behavior, and package-driven update review
are v3.1 H002/H003/H008. See the
[batch result](../migrations/native-rpm-05.md).
