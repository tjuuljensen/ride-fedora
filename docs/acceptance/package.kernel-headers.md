# `package.kernel-headers` acceptance

Status: **PASS; supported package install** on Fedora 44 x86_64 Workstation,
2026-10-30. The v2 `InstallKernelTools`/`RemoveKernelTools` bundle splits into
`package.kernel-devel` and `package.kernel-headers`. The signed Fedora
[`kernel-headers` RPM](https://packages.fedoraproject.org/pkgs/kernel-headers/kernel-headers/)
provides userspace kernel headers.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T113742Z-test-provider-kernel-and-python-packages-batch-79fd1c85`;
candidate catalog SHA-256
`819b73be3d9d30dec5dfcf9fdd9b2be5013443cf471a33026fdb0ee556897a9c`.
The retained transcript and
`.acceptance-runs/provider-foundation-03-kernel-python.xml` show absent
plan, apply, signed RPM and files, status, unchanged repeat, restore, and
explicit remove. Both inverse paths returned the full RPM inventory to the
operation baseline. See the [bundle result](provider-kernel-tools.md).
