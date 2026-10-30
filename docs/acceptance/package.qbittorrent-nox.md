# `package.qbittorrent-nox` acceptance

Status: **PASS; supported** on Fedora 44 Server x86_64. Reviewer: Codex,
2026-10-30. The source `InstallqBittorrentServer` function installs the Fedora
[`qbittorrent-nox` RPM](https://packages.fedoraproject.org/pkgs/qbittorrent/qbittorrent-nox/)
only. Its neighboring service, user, firewall, SSH key, and download actions
remain separate in `network-devices`.

The focused disposable VM test passed (one test, 385.49 seconds) on the pinned
Fedora 44 Server x86_64 image SHA-256
`efb75956d6dbde0801059fdac4a8a1451f06ecc843344ecdb71bb3e8d247af90`.
The guest reported `VARIANT_ID=server`. The retained overlay is
`20261030T193152Z-test-qbittorrent-nox-package-only-lifecycle-015ec064`
under `.acceptance-runs/generic-server-15/fedora-44-server-x86_64/`.
Its `metadata.json` records QEMU `tcg` acceleration and candidate catalog
SHA-256 `efd8c28092108aa0732d28049780a358c796a758db81ccdc88d9d0237bdde645`;
`transcript.jsonl` and `.acceptance-runs/generic-server-15-tcg.xml` retain
the command and test results. The VM source bundle included uncommitted
harness changes; the tested catalog row and unchanged DNF handler are recorded
by the metadata hash and source revision `35bea5b`.

The test checked absent plan, apply, complete changed journal, signed RPM,
`rpm -V`, executable path, installed status, unchanged repeat, dry-run and
actual restore, and explicit install/remove. Both recovery paths returned the
full RPM inventory to baseline. It compared the custom service unit and
`qbittorrent` account before and after, and confirmed no test service instance
was active or enabled. It did not start a network-facing service. The unchanged
DNF handler's failure evidence is in [base package checks](package.exfatprogs.md).
No manual session was needed. The [batch record](../migrations/generic-server-15.md)
and [Windows alignment](../windows-alignment.md#fedora-server-qbittorrent-package-preflight-2026-10-30)
define scope. Promotion adds an opt-in package-only profile and changes the
catalog status; service provisioning needs its own migration and recovery.
