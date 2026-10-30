# `package.kernel-devel` acceptance

Status: **PASS; supported package install** on Fedora 44 x86_64 Workstation,
2026-10-30. The v2 `InstallKernelTools`/`RemoveKernelTools` bundle splits into
`package.kernel-devel` and `package.kernel-headers`. The signed Fedora
[`kernel-devel` RPM](https://packages.fedoraproject.org/pkgs/kernel/kernel-devel/)
provides kernel development files. This operation installs the RPM; it does
not claim a working build against the running kernel.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T113742Z-test-provider-kernel-and-python-packages-batch-79fd1c85`;
candidate catalog SHA-256
`819b73be3d9d30dec5dfcf9fdd9b2be5013443cf471a33026fdb0ee556897a9c`.
The retained transcript and
`.acceptance-runs/provider-foundation-03-kernel-python.xml` show absent
plan, apply, signed RPM and files, status, unchanged repeat, restore, and
explicit remove. The named package and 13 introduced RPM identities were
absent after both inverse paths. No pre-existing RPM identity was lost.
DNF updated 14 pre-existing `glibc`, `gcc` runtime, `elfutils`, and `openssl`
family RPMs; RIDE did not downgrade them. The VM ran
`6.19.10-300.fc44.x86_64` while DNF installed
`kernel-devel-7.2.13-200.fc44.x86_64`. Matching module-build coverage is
queued for v3.1. See the [bundle result](provider-kernel-tools.md).
