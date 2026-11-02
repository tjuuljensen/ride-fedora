# System and security batch 28: ClamAV package and initial signatures

Status: **kept for v3.0; implementation path is being scoped**, 2026-10-30.
The v2 apply installs `clamav` and `clamav-update`, then runs `freshclam` once.
Removal uninstalls the RPMs but leaves the signature database. The v3 path must
preserve that user-facing initial signature update without silently enabling a
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
- Detect and preserve pre-existing `/var/lib/clamav` state. Document that
  removing the RPMs retains signature data, matching v2.
- On a disposable Fedora 44 Workstation VM, verify plan, apply, repeat,
  status, RPM signatures, successful freshclam result, removal, and seeded
  existing-database protection. Capture database state and demonstrate that a
  failed update does not get reported as successful.
- Keep scanning, automatic update scheduling, quarantine, and user-file access
  out of this package batch; review them separately before adding behavior.

The security signature and service lifecycle is still a deep gate. If the
bounded one-shot update and failure reporting cannot pass before v3.0 release
review, keep the outcome visible as unresolved rather than retire it or expose a
package-only result as equivalent.
