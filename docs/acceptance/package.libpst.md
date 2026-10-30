# `package.libpst` acceptance

Status: **PASS; supported** on Fedora 44 x86_64 Workstation, 2026-10-30.
The v2 `InstallLibpst`/`RemoveLibpst` pair maps to the signed Fedora
[`libpst` RPM](https://packages.fedoraproject.org/pkgs/libpst/libpst/).
RIDE installs the `readpst` tool; it does not convert user mail data.

VM evidence: pinned Workstation image SHA-256:
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay:
`20261030T111844Z-test-remaining-native-repository-batch-a48d4efa`;
catalog SHA-256:
`b2ddd2a00a03adb2dd164900eb7b435da01d9001bc844630537732129e5ecd63`.
The retained `transcript.jsonl`, `metadata.json`, and
`.acceptance-runs/native-rpm-05.xml` show a passing absent plan, apply,
signed RPM and files, `readpst` command detection, status, unchanged repeat,
restore, and explicit remove. Both inverse paths returned the full RPM
inventory to baseline. The unchanged DNF handler's focused mocked failure
evidence is recorded in [base package checks](package.exfatprogs.md).
See the [batch result](../migrations/native-rpm-05.md).
