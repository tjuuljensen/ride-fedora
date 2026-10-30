# Shell tools acceptance: `package.pv` and `package.strace`

Status: **PASS; supported** on Fedora 44 x86_64 Workstation, 2026-10-30.
The active v2 `InstallShellTools`/`RemoveShellTools` pair splits into two
Fedora RPM operations, `package.pv` and `package.strace`, selected together
by the opt-in `shell-tools` profile. Fedora package and license records:
[`pv`](https://packages.fedoraproject.org/pkgs/pv/pv/) and
[`strace`](https://packages.fedoraproject.org/pkgs/strace/strace/).

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T112939Z-test-provider-shell-tools-batch-and-profile-7f5f4462`;
candidate catalog SHA-256
`950a222c71a6be7e56ffd0c1e1f22a9d7d90cf0e91c273d8099ce2e053fbaf95`.
The retained `transcript.jsonl`, `metadata.json`, and
`.acceptance-runs/provider-foundation-01-shell-tools.xml` record one passing
test. Each operation passed absent plan, apply with `--allow-candidate`,
signed RPM and file verification, command detection, installed status,
unchanged repeat, restore, and explicit remove. The opt-in profile passed
combined plan, apply, repeat, and restore. All three inverse checks returned
the full RPM inventory to baseline, with no retained dependencies or changed
pre-existing RPMs. The unchanged DNF handler's focused mocked failure
evidence is in [base package checks](package.exfatprogs.md). See the
[batch decision](../migrations/provider-foundation-01.md) and
[Windows alignment](../windows-alignment.md#fedora-provider-foundation-batch-01-2026-10-30).
