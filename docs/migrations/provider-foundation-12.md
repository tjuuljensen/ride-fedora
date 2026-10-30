# Snapd service and package-manager ownership

Status: **unsupported as a runnable v3.0 operation**, 2026-10-30.
The owner chose **keep** for optional Snap enablement in the v3.0 fast-track
review, for occasional user-selected snap installations. This does not add
snap applications to a base profile. Model the daemon/runtime lifecycle and
preserve pre-existing snaps and data.
The commented v2 `InstallSnap`/`RemoveSnap` pair installs or removes the
Fedora [`snapd` RPM](https://packages.fedoraproject.org/pkgs/snapd/snapd/).
Snapd is a privileged package manager with service and application state;
package presence alone does not prove a usable or safely removable Snap
installation. The v3.0 catalog has no runnable operation for this outcome.

## Completion criteria defined before resolution

- Check current Fedora 44 package and publisher instructions, plus the
  declared Workstation VM baseline. Distinguish RPM presence from an
  activated daemon and a usable installed snap.
- Permit a runnable operation only after defining service activation,
  confinement, existing snap detection, and an inverse that preserves
  unowned apps and data, with focused failure tests and an isolated VM seeded
  with app/data state through recovery.
- Otherwise record a reasoned non-runnable v3.0 disposition and review
  trigger. A high-risk candidate cannot bypass the safety gate.

## Fedora 44 inspection and v3.0 decision

Fedora publishes a [`snapd` RPM](https://packages.fedoraproject.org/pkgs/snapd/snapd/)
for release 44 under GPL-3.0-only. The
[publisher's Fedora setup](https://snapcraft.io/docs/tutorials/install-the-daemon/fedora/)
requires a session restart for paths, offers an additional `/snap` symlink
for classic snaps, and tests usability by installing and running a snap.
The pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`
had no `snapd` RPM in disposable read-only overlay
`provider-flatpak-snap-inventory`.

The commented v2 pair only installs/removes the RPM. It does not define
service state, classic confinement, a usable snap, or preservation of
pre-existing snap data on removal. The current v3 DNF package handler does
not journal those effects, and no seeded-state recovery VM evidence exists.
`Snap` is therefore **unsupported as a v3.0 operation**; no install or
runtime acceptance is claimed. Reopen only for an explicit Snap use case
with its required confinement mode, app/data ownership, safe inverse, and
exact-target VM lifecycle. Do not add it to a base profile by default.
