# SmartMonTools storage-monitoring decision

Status: **decision deferred by owner; unsupported for v3.0**, 2026-10-30. The active v2 pair only
installs and removes the signed Fedora [`smartmontools` RPM](https://packages.fedoraproject.org/pkgs/smartmontools/smartmontools/).
The package also supplies `smartd`, so its service state must be observed
before treating a package-only lifecycle as safe. No storage device is
probed by RIDE during this review.

The predefined gate required plan, signed apply, repeat, status, inverse,
RPM inventory recovery, and unchanged smartd service state on the pinned
Fedora 44 x86_64 Workstation VM. The disposable overlay
`20261030T140047Z-test-package-only-security-lifecycles-ed37222c` found
that installing the RPM **enabled `smartd.service`** while it stayed
inactive. It was disabled before installation. The test stopped on that
new service enablement before restore; its overlay and transcript are
retained. A generic `dnf-package` handler would misrepresent the side effect
and its service recovery. The experimental catalog row and opt-in profile
were removed rather than promoted as a runnable candidate.

Reopen when a dedicated operation can record prior smartd enable/active
state, preserve administrator configuration and device selection, and pass
apply, partial failure, remove, and restore on the disposable target.
Hardware SMART polling remains a separate opt-in review. This failure was
investigated; no unchanged VM retry was made.

The owner deferred the v3.0 capability decision in the fast-track review on
2026-10-30. The service-state evidence above remains the reopening gate.
