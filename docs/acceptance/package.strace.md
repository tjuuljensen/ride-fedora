# `package.strace` acceptance

Status: **PASS; supported** on Fedora 44 x86_64 Workstation, 2026-10-30.
The v2 `InstallShellTools`/`RemoveShellTools` pair is split into
`package.pv` and `package.strace`. Fedora's signed
[`strace` RPM](https://packages.fedoraproject.org/pkgs/strace/strace/)
supplies the system call tracer. RIDE installs the tool; it does not trace a
process.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T112939Z-test-provider-shell-tools-batch-and-profile-7f5f4462`;
catalog SHA-256
`950a222c71a6be7e56ffd0c1e1f22a9d7d90cf0e91c273d8099ce2e053fbaf95`.
The retained transcript and
`.acceptance-runs/provider-foundation-01-shell-tools.xml` show absent plan,
apply, signed RPM and files, `strace` command detection, status, unchanged
repeat, restore, and explicit remove. The full RPM inventory returned to
baseline. The [combined profile acceptance](provider-shell-tools.md) records
the `shell-tools` profile and both operations.
