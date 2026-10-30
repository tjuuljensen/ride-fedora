# Flatpak runtime and application-preserving inverse

Status: **replaced by Fedora Workstation's supplied runtime; no v3.0 RIDE
install**, 2026-10-30.
The commented v2 `InstallFlatpak` installs the Fedora Flatpak RPM. Its
`RemoveFlatpak` runs `flatpak uninstall --all` before `dnf autoremove -y
flatpak`, so it can delete applications and runtimes RIDE did not install.
The current [Fedora Flatpak package](https://packages.fedoraproject.org/pkgs/flatpak/flatpak/)
is available for Fedora 44 and is pre-installed in the pinned Workstation
image. Pre-installation in one image does not prove a safe v3 installation
or inverse on all declared hosts.

## Completion criteria defined before resolution

- Inspect the runtime package and remote/application baseline on the pinned
  Fedora 44 x86_64 Workstation image. Check the current distribution contract.
- Allow a runnable v3 operation only with an installed-only or ownership-aware
  package lifecycle that preserves seeded user Flatpak apps, remotes, and data
  through apply, repeat, failure, and recovery in a disposable VM. Never use
  `uninstall --all` or blanket `autoremove` as an inverse.
- Otherwise record a documented non-runnable replacement or unsupported
  decision with a review trigger; do not count baseline package presence as
  an accepted RIDE install.

## Fedora 44 inspection and v3.0 decision

[Flathub's Fedora setup](https://flathub.org/en/setup/Fedora) states that
Flatpak is installed by default on Fedora Workstation. In the pinned
Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`,
disposable overlay `provider-flatpak-snap-inventory`, read-only checks found
Fedora `flatpak` 1.17.6, the Fedora OCI system remote, no user remote, and
no installed apps. The separate
[Flathub remote](provider-foundation-09.md) is not supplied by this package
baseline. The query made no state change and does not establish preservation
of seeded user data through a RIDE lifecycle.

The commented v2 `Flatpak` package pair is **replaced for v3.0 by the Fedora
Workstation supplied runtime**, with no RIDE operation or managed removal.
This is a documented, non-runnable replacement, not a working RIDE install.
The destructive v2 inverse is retired from execution. Reopen if RIDE must
repair an absent runtime on a declared Workstation host; then prove a
data-preserving installed-only contract or an owned inverse with seeded
apps, remotes, and data in a disposable VM. Other editions still require
their own support evidence.
