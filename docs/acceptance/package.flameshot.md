# `package.flameshot` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 x86_64 Workstation,
2026-10-30. The v2 `InstallFlameshot`/`RemoveFlameshot` pair maps to the
signed Fedora [`flameshot` RPM](https://packages.fedoraproject.org/pkgs/flameshot/flameshot/).

Pinned Workstation image SHA-256:
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay:
`20261030T110635Z-test-native-desktop-applications-lifecycle-1891f3ec`;
catalog SHA-256:
`f6cc32d95206073c3460196d4e03d2021b0578dbc3a31c576d205e628704c12b`.
The retained `transcript.jsonl`, `metadata.json`, and
`.acceptance-runs/native-rpm-04-desktop.xml` show the passing absent plan,
apply with `--allow-candidate`, signed RPM and file verification, installed
desktop launcher, status, unchanged repeat, restore, and explicit remove.
Both inverse paths returned the full RPM inventory to baseline. Screenshot
capture in a graphical session was not exercised; visual behavior and broader
failure recovery remain v3.1 H002/H003 checks. See the
[batch record](../migrations/native-rpm-04.md).
