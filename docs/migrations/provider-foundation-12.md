# Snapd service and package-manager ownership

Status: **operable v3.0 opt-in candidate** on Fedora 44 Workstation x86_64,
2026-10-31.
The owner chose **keep** for optional Snap enablement in the v3.0 fast-track
review, for occasional user-selected snap installations. This does not add
snap applications to a base profile. Migrate an opt-in, installed-only Snap
runtime; RIDE must not remove user-installed snaps or their data.
The commented v2 `InstallSnap`/`RemoveSnap` pair installs or removes the
Fedora [`snapd` RPM](https://packages.fedoraproject.org/pkgs/snapd/snapd/).
The v3 operation installs the Fedora runtime only. Snap applications and
their data remain user-managed; RIDE has no remove or restore action.

## Completion criteria defined before resolution

- Use Fedora's signed `snapd` RPM and preserve the Fedora package manager as
  source of truth. Check whether the RPM enables `snapd.socket` by default and
  whether socket activation works in the declared Fedora 44 Workstation VM.
- Keep runtime management opt-in and installed-only. Do not enable classic
  confinement via a blanket `/snap` symlink unless a separate user need
  requires it. Do not expose RPM or Snap application removal as a RIDE inverse.
- Before the VM run, seed unrelated contents under `/var/lib/snapd` and a
  user-state sentinel. Define checks for plan, install, repeat, status,
  signature, socket activation, confined `hello-world` install/run, retained
  state, and refusal of remove/restore. A test-owned hello-world snap may be
  removed inside the disposable overlay after its output is verified.
- Treat the runtime as an opt-in candidate and disclose the observed host
  confinement mode. Do not describe a strict-confined test snap as proof that
  all Snap applications receive strict confinement on this Fedora host.

## Fedora 44 inspection and v3.0 decision

Fedora publishes `snapd-2.77.1-0.fc44` under GPL-3.0-only in its Fedora 44
updates repository ([package record](https://packages.fedoraproject.org/pkgs/snapd/snapd/)).
The [publisher's Fedora setup](https://snapcraft.io/docs/tutorials/install-the-daemon/fedora/)
uses `dnf install snapd`, advises a log out/in or restart so Snap paths are
updated, makes the `/snap` symlink optional for classic snaps, and verifies a
working install with the `hello-world` snap. Snapcraft documents that Fedora
updates snapd from its native package and does not use snapd re-execution
([distribution support](https://snapcraft.io/docs/reference/administration/distribution-support/)).
The pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`
had no `snapd` RPM in disposable read-only overlay
`provider-flatpak-snap-inventory`.

The commented v2 pair only installs/removes the RPM. The accepted v3 path is
`package.snapd` in the opt-in `snap-runtime` profile, using Fedora's signed
RPM and the existing DNF package handler. The declared Fedora 44 Workstation
VM confirmed `snapd.socket` is enabled and active, verified the RPM signature
and files, installed and ran the `hello-world` snap, confirmed that its Snap
metadata says `confinement: strict`, and confirmed the host reports
`snap debug confinement: partial` while SELinux is Enforcing. It also verified
repeat apply, installed status, preserved seeded system and user data, left
the `/snap` path unchanged, and refused RIDE remove and restore. The test-owned
`hello-world` snap was removed from the disposable VM after the smoke check.

The strict label on this test snap is not a guarantee of strict isolation on
the host: Snapcraft reports that AppArmor is not enabled, and Snap reports
`partial` best confinement. Keep this operation an explicit opt-in candidate.
The Fedora runtime path completes the requested v3.0 capability; AppArmor and
confinement behavior, Snap application lifecycle, user-data recovery, and
coexistence with RPM or Flatpak editions remain in v3.1 hardening item H034.
Do not add Snap applications or Snapd to a base profile.

The final disposable run passed in 566.83 seconds. The exact target image SHA-256
was `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
Its overlay is
`.acceptance-runs/provider-foundation-12-candidate-clean/fedora-44-workstation-x86_64/20261031T030157Z-test-snap-runtime-install-only-preserves-state-and-runs-test-snap-dc73f5f0/`;
JUnit is `.acceptance-runs/provider-foundation-12-candidate-clean.xml`.
The run used source revision `9da0526d412343076d6327c6cb3c5331be6d773a`
with uncommitted changes, catalog SHA-256
`7ad45d7f83d4de99915dd6ce8e95fcc045d5fd9ce4eedf062ae61bbcfd42a541` and source bundle SHA-256
`dd963d411a32ce3bf8803966d2ae6c4ceff91d5ad2702d081564f38acb3ca684`.
