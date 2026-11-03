# ClamAV package and initial signatures

Status: **operable opt-in candidate; Fedora 44 Workstation x86_64 RIDE lifecycle passed**, 2026-11-02.

Target: Fedora 44 Workstation x86_64.

The opt-in `package.clamav` operation installs Fedora's signed `clamav` and
`clamav-freshclam` RPMs, performs one verified `freshclam --verbose` update,
and leaves recurring FreshClam services and timers in their prior state. It
does not scan files, enable scheduled updates, quarantine files, or read user
data.

Before apply, the handler snapshots the supported `/var/lib/clamav` tree into
a private RIDE-owned directory. It preserves bytes, mode, uid/gid, timestamps,
and extended attributes, and refuses symbolic links or special files. It
records whether each RPM root and each FreshClam unit existed before the run.
On update failure it removes only newly added RPM roots and restores the
pre-apply signature tree. On removal it refuses later signature or unit-state
changes, removes only RPM roots it introduced, and restores the prior tree.

## Automated evidence

- `tests/test_v3_clamav.py`: 4 mocked handler lifecycle tests covering
  apply/repeat/remove, failed-update rollback, and preservation of a
  pre-existing ClamAV RPM.
- `tests/test_clamav_state.py`: 2 tests covering tree metadata and content
  restore, absent-directory recovery, and refusal of symlinks.
- `tests/acceptance/test_clamav_v3_lifecycle.py`: exact-target scenario for
  candidate gating, injected failed-update rollback, successful RPM and
  signature update, repeat/status, and seeded-data/package/unit restoration.

Both focused suites pass: **6 passed**. The RIDE-specific Fedora 44 Workstation
VM acceptance passed: **1 passed in 785.09 seconds**, using QEMU TCG and the
pinned image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`. It covered
injected update failure and rollback, successful tested signature update,
repeat/status, RPM verification, and exact restore of the pre-existing data
tree and package/unit state. `rpm -V --noghost` verifies package-owned files;
ClamAV's mutable `%ghost` signature files are checked separately.

Run ID: `20261102T180958Z-3898-14394`. Evidence is retained under
`.acceptance-runs/clamav/fedora-44-workstation-x86_64/20261102T180252Z-test-clamav-failure-rollback-and-exact-signature-recovery-d06789a1/`.
Transcript SHA-256: `1b344dc49c5692560f3c24331c136e9bc1cf8a0e4ac26d27b15e5955aa061065`;
metadata SHA-256: `27e422476082d720bf7163e0b92243d2b03b02467ff0de44fd81eed0d6b340df`;
overlay SHA-256: `19ed949d29f7db5461dc0a7c4a45dbd397c9b39fd66ce0a9481c15f89f050633`.

Safety review checks: `private-output-boundary` (snapshots stay in private
root-owned RIDE state), `no-evidence-processing` (the operation never scans
user files), and `exact-output-preservation` (restore matches the exact
pre-apply signature tree). See the [batch record](../migrations/system-security-28.md).

Keep the operation opt-in. Broader signature database lifecycle, scheduled
update, scan, and quarantine behavior remain outside this operation.
