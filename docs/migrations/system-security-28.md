# System and security batch 28: ClamAV package and initial signatures

Status: **kept for v3.0; operable opt-in candidate after exact-target lifecycle
acceptance**, 2026-11-02. The v2 apply installs `clamav` and
`clamav-update`, then runs
`freshclam` once. Fedora 44 maps the updater to `clamav-freshclam`. An owned v3
path must preserve the initial signature update without silently enabling a
daemon or claiming a fresh database after an update failure.

Fedora 44 currently packages ClamAV 1.4.6 under GPL-2.0-only. Its package
layout uses `clamav-freshclam` for `freshclam` and its optional service; Fedora
also publishes `clamav-data`. The old `clamav-update` name is not the Fedora 44
package path. See the [Fedora ClamAV package](https://packages.fedoraproject.org/pkgs/clamav/clamav/),
[Fedora freshclam subpackage](https://packages.fedoraproject.org/pkgs/clamav/clamav-freshclam/),
[Fedora signature data subpackage](https://packages.fedoraproject.org/pkgs/clamav/clamav-data/),
and the [upstream signature update guide](https://docs.clamav.net/manual/Usage/SignatureManagement.html).
Upstream documents signature verification, failure behavior, and that freshclam
can update existing databases or replace a corrupted database.

## Completion checks before a runnable implementation

- Select signed Fedora RPM dependencies and confirm their service presets on
  the pinned Workstation target.
- Run exactly one initial `freshclam` update as v2 did; do not enable the
  `clamav-freshclam` service or scan files during apply.
- Before changing state, snapshot the complete existing `/var/lib/clamav`
  contents and ownership metadata into a private, run-owned recovery location.
  Refuse symlinks or unsupported file types unless the snapshot and restore
  implementation proves they are handled safely.
- On removal, remove only RPMs introduced by this run, then restore the exact
  prior signature-directory state. A successful first install must also be
  exactly reversible when `/var/lib/clamav` did not exist before the run.
- If `freshclam` fails or its output cannot prove a successful update, stop
  the operation and restore the pre-apply package, database, and unit state;
  never leave a partially updated database reported as installed.
- On a disposable Fedora 44 Workstation VM, verify plan, apply, repeat,
  status, RPM signatures, successful freshclam result, removal, and seeded
  existing-database protection. Capture hashes and metadata before and after
  restore, and inject a failed update to demonstrate rollback.
- Record and preserve the prior states of `clamav-freshclam.service`, the
  one-shot service, and any associated timer. Do not enable recurring updates.
- Keep scanning, automatic update scheduling, quarantine, and user-file access
  out of this package batch; review them separately before adding behavior.

## Fedora 44 Workstation package behavior probe

The direct Fedora package probe passed on a disposable Fedora 44 Workstation
x86_64 VM. It installed signed `clamav` and `clamav-freshclam` 1.4.6-1.fc44,
plus `clamav-filesystem` and `clamav-lib`; the separate `clamav-data` package
was not installed. `rpm -V` reported no changes. The `clamav-freshclam.service`
was disabled and inactive after installation. A single `freshclam --verbose`
run downloaded `main.cvd`, `daily.cvd`, and `bytecode.cvd`; it tested the
downloaded database and reported success. No file scan was run.

Removing `clamav` and `clamav-freshclam` removed all four RPMs and deleted the
signature databases and `freshclam.dat` created by that update. A pre-seeded
unowned marker in `/var/lib/clamav` survived. Therefore the package transaction
does not provide an exact inverse: the v3 handler must snapshot and restore the
full prior signature-directory state and remove databases created by the run.
The v2 package-remove function does not explicitly preserve those files, so
the migration decision documents this safer recovery behavior as an intentional
improvement over v2.

- Probe: `tests/acceptance/test_clamav_package_and_update.py`
- Result: 1 passed in 365.65 seconds
- Transcript: `.acceptance-runs/fedora-44-workstation-x86_64/20261102T143545Z-test-fedora-clamav-packages-one-shot-update-and-data-retention-3ea19033/transcript.jsonl`
- Transcript SHA-256: `72c47a98df6f3627a24dbcef514b27d1098e18b3d840cae9c9fa5b2e96850881`
- Overlay SHA-256: `08d5be99232965a23a57593b9732e343f69dbb736de95b7b50a46dab5769bd47`
- Base image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`
- Fedora package source and license: [clamav](https://packages.fedoraproject.org/pkgs/clamav/clamav/index.html),
  [clamav-freshclam](https://packages.fedoraproject.org/pkgs/clamav/clamav-freshclam/index.html),
  [clamav-data](https://packages.fedoraproject.org/pkgs/clamav/clamav-data/)
- Upstream update behavior: [ClamAV signature management](https://docs.clamav.net/manual/Usage/SignatureManagement.html)

These direct DNF probes are package evidence, not RIDE v3 acceptance.

### Follow-up service and timer probe, 2026-11-02

The direct package probe was rerun under the harness's TCG acceleration after
extending it to enumerate all FreshClam service and timer units. On the pinned
Fedora 44 Workstation x86_64 image, `clamav-freshclam.service`,
`clamav-freshclam-once.service`, and `clamav-freshclam-once.timer` were all
disabled and inactive after installation and remained so after the successful
one-shot update. RPM verification returned no modified files. Removing the
packages removed the four RPMs and the new signature databases while preserving
the pre-seeded marker. This verifies Fedora's default package side effects; it
does not yet prove that a RIDE handler can preserve customized prior unit or
database state, roll back a failed update, or restore its package transaction.

- Probe: `tests/acceptance/test_clamav_package_and_update.py`
- Result: 1 passed in 389.31 seconds with TCG acceleration
- Transcript: `.acceptance-runs/clamav-unit-state-tcg/fedora-44-workstation-x86_64/20261102T144734Z-test-fedora-clamav-packages-one-shot-update-and-data-retention-6e234b9e/transcript.jsonl`
- Transcript SHA-256: `372cd0a3e824f365902b58428e52982e85510c21f877d0fc70b9fb1c5ba91581`
- Overlay SHA-256: `0e93eacd397d30706c3913b4381eb7d19698860ff90fe84468977ce22a9be0eb`
- Metadata SHA-256: `0457f9b8ce28264203bec33daa340e5768a71d69c937b0ec1c5f8c3cbdc9979b`
- Base image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`

## RIDE v3 candidate implementation, 2026-11-02

`package.clamav` now uses the dedicated `clamav-initial-signatures` handler in
the opt-in `fedora-clamav-initial-signatures` profile. It snapshots the
supported `/var/lib/clamav` tree, including file contents, mode, ownership,
timestamps, and extended attributes; refuses symbolic links and special files;
installs Fedora's signed `clamav` and `clamav-freshclam` RPMs; runs one
`freshclam --verbose`; and requires a successful exit plus evidence of a tested
or current signature database. It captures prior and resulting package and
FreshClam unit state, never starts recurring services, and removes only the
two package roots that were absent before the RIDE run. Removal restores the
exact prior signature tree, including the case where the data directory did
not exist before apply. A changed post-install database or unit state blocks
removal rather than overwriting later state.

The focused mocked suite passes **6 tests** across both lifecycle and tree
snapshot helpers: `tests/test_v3_clamav.py` and `tests/test_clamav_state.py`.
The RIDE lifecycle passed on Fedora 44 Workstation x86_64 under QEMU TCG:
**1 passed in 785.09 seconds**. It verified failed-update rollback, a tested
successful signature update, repeat/status, RPM verification, and exact
restoration of seeded signature data and package/unit state. The initial VM
run exposed a cold-install lookup ordering bug; the handler now checks for
`freshclam` after installing its provider RPM. RPM verification excludes
mutable `%ghost` signature files, which the test verifies separately.

Run ID: `20261102T180958Z-3898-14394`; evidence directory:
`../.acceptance-runs/clamav/fedora-44-workstation-x86_64/20261102T180252Z-test-clamav-failure-rollback-and-exact-signature-recovery-d06789a1/`.
Transcript SHA-256: `1b344dc49c5692560f3c24331c136e9bc1cf8a0e4ac26d27b15e5955aa061065`;
metadata SHA-256: `27e422476082d720bf7163e0b92243d2b03b02467ff0de44fd81eed0d6b340df`;
overlay SHA-256: `19ed949d29f7db5461dc0a7c4a45dbd397c9b39fd66ce0a9481c15f89f050633`.

Keep the operation opt-in and candidate-gated. The remaining H109 hardening
covers broader signature database lifecycle and update behavior; it is not a
v3.0 migration blocker for this bounded operation.
