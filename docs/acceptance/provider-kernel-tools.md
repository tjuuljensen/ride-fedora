# Kernel tools acceptance: `package.kernel-devel` and `package.kernel-headers`

Status: **PASS; supported package installs** on Fedora 44 x86_64 Workstation,
2026-10-30. The active v2 `InstallKernelTools`/`RemoveKernelTools` bundle is
split into two Fedora RPM operations. The disposable overlay
`20261030T113742Z-test-provider-kernel-and-python-packages-batch-79fd1c85`
used pinned image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`
and candidate catalog SHA-256
`819b73be3d9d30dec5dfcf9fdd9b2be5013443cf471a33026fdb0ee556897a9c`.
The retained transcript and
`.acceptance-runs/provider-foundation-03-kernel-python.xml` record one
passing test. Both operations passed absent plan, apply, signature/files,
status, unchanged repeat, restore, and explicit remove. No pre-existing RPM
identity was lost. `kernel-devel` caused DNF to update 14 existing RPMs and
its version did not match the VM's running kernel; this acceptance is for
package installation only. See the [batch review](../migrations/provider-foundation-03.md).
