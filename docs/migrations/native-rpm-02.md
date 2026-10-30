# Native RPM batch 02: forensic utilities and package conversion

Status: **PASS; four supported operations**, 2026-10-30. This batch covers
four direct `dnf install`/`dnf remove` v2 pairs on Fedora 44 x86_64
Workstation. `Terminator` was moved to a user-setting batch because its v2
function changes an iBus hotkey. `SmartMonTools` was moved to a storage batch
because its RPM contains a service and system configuration. Neither can be
counted as a simple package migration.

| v2 outcome | RPM | Fedora 44 source and license |
| --- | --- | --- |
| `package.LibEWF` | `libewf` | [Fedora `libewf`](https://packages.fedoraproject.org/pkgs/libewf/libewf/), LGPL-3.0-or-later. This library is distinct from the existing `package.ewftools` utilities candidate. |
| `package.Exif` | `exif` | [Fedora `exif`](https://packages.fedoraproject.org/pkgs/exif/exif/), LGPL-2.1-or-later. |
| `package.Md5deep` | `md5deep` | [Fedora `md5deep`](https://packages.fedoraproject.org/pkgs/md5deep/md5deep/), GPL-2.0-only. |
| `package.Alien` | `alien` | [Fedora `alien`](https://packages.fedoraproject.org/pkgs/alien/alien/), GPL-2.0-or-later. RIDE installs the tool but does not convert or install foreign packages. |

## Completion criteria defined before testing

- Add four individually selectable candidate catalog operations with the
  existing `dnf-package` handler, explicit Fedora RPM source, and Workstation
  target. Preserve the v2 install/remove intent without evaluating legacy
  functions. Do not select them in `default` or `server-base`.
- Run focused mocked plan/apply/repeat/status/restore tests and catalog/target
  validation. Reuse the accepted DNF handler failure evidence only if the
  handler and journal contract remain unchanged.
- In one pinned disposable Workstation overlay, check each RPM's prior state,
  plan, install, repeat, status, Fedora signature/files, restore, explicit
  remove, and RPM inventory recovery. If an RPM is preinstalled,
  investigate the removal transaction before preparing absence; do not erase
  other packages merely to force a pass.
- Promote only passed exact-target operations with individual acceptance
  records. Record failures and their causes before any retry. No manual
  session is required for these package-only changes.

## Investigated VM failure and revised recovery check

The initial overlay (`20261030T100729Z-test-native-forensic-and-package-tools-batch-c6568f54`)
passed `libewf`, `exif`, and `md5deep`. Installing `alien` also upgraded older
RPM, glibc, and related packages from the pinned image. Removal correctly
removed `alien`, but did not downgrade those system packages; the original
full-inventory equality assertion failed. The second overlay
(`20261030T101129Z-test-native-forensic-and-package-tools-batch-659186aa`)
ran `dnf upgrade --refresh` as disposable-VM preparation before the baseline.
It again passed the first three packages and narrowed the post-restore
difference to one retained `systemd-rpm-macros` dependency. The requested
`alien` RPM was absent, and no original RPM was removed or changed.

The v3.0 contract for this low-risk package install is that the named package
can be restored or removed and no pre-existing RPM is lost or changed.
Fedora DNF may retain a dependency; the acceptance check names and limits
that residue instead of treating a perfectly identical RPM inventory as a
release gate. A fresh overlay must still pass explicit `alien` install/remove
and the same no-loss check before promotion. Dependency cleanup can be
reviewed for v3.1 without deleting packages RIDE does not own.

The final fresh overlay
`20261030T102031Z-test-native-forensic-and-package-tools-batch-d11e5c1a`
passed all four lifecycle checks, including `alien` explicit install/remove.
`.acceptance-runs/native-rpm-02-final.xml` reports one pass and no failures,
errors, or skips. The four [per-operation acceptance records](../acceptance/package.libewf.md)
link the exact target and catalog digest; `alien` retains the named dependency
review as v3.1 hardening item H005. No manual session was needed.

The Windows development branch at `17f9cef` has no matching Linux RPM
installers; this batch uses the previously reviewed Linux catalog schema 3,
profile schema 1, and run schema 2 package semantics. Recheck product facts or
shared behavior before promotion and at release-candidate preparation.
