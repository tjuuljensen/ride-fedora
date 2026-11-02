# Flatpak runtime install and safe inverse boundary

Status: **PASS; supported** on Fedora 44 Workstation x86_64, 2026-10-31.
The owner subsequently chose **keep** for the Flatpak runtime capability in
the v3.0 fast-track review, separately from the Flathub remote. Add an
optional absent-runtime installation path while refusing to remove the
runtime or its app/data stores. Its presence on the pinned image remains
baseline evidence only.
The commented v2 `InstallFlatpak` installs the Fedora Flatpak RPM. Its
`RemoveFlatpak` runs `flatpak uninstall --all` before `dnf autoremove -y
flatpak`, so it can delete applications and runtimes RIDE did not install.
The current [Fedora Flatpak package](https://packages.fedoraproject.org/pkgs/flatpak/flatpak/)
is available for Fedora 44 and is pre-installed in the pinned Workstation
image. Pre-installation in one image does not prove a safe v3 installation
or inverse on all declared hosts.

## Completion criteria defined before implementation

- Add `package.flatpak` with `states: ["installed"]` and `recovery: "none"`.
  Keep the operation opt-in; do not make package absence an exposed desired
  state. This retains repair/install while making the unsafe legacy removal
  unavailable. Reuse the Fedora DNF handler and its focused failure evidence.
- Before a disposable VM run, seed a user remote, a system remote, and user
  data under `~/.var/app`; capture package inventory, remote records, and
  sentinel metadata. Prepare absence with `rpm -e --nodeps flatpak` in the
  disposable overlay so the scenario tests installation while leaving reverse
  dependencies, other RPMs, and remote configuration in place. This is test
  setup only; it is not a supported RIDE operation.
- Verify plan, candidate gate, signed RPM install, repeat, status, and RPM
  files. Since recovery is none, restore and remove must refuse. Apply must
  leave seeded remotes and app data identical. Confirm the CLI can list the
  retained remotes and user data remains owned by its original user.
- Run the profile smoke with supported status after absent-state install
  checks pass; the install acceptance is recorded separately in the evidence
  report.
  Never call `flatpak uninstall --all` or blanket `autoremove` as an inverse.
- Retain broader app and runtime upgrades, per-app data lifecycle, and
  Flatpak/RPM coexistence under H033. These are not part of installing the
  Flatpak runtime itself.

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

The prior replacement decision predated the owner's v3.0 keep decision.
RIDE provides an installed-only runtime operation for Fedora 44 Workstation.
The v2 `flatpak uninstall --all` and blanket autoremove behavior remain
excluded from execution because they can delete unrelated apps and data.
The Fedora 44 Workstation install path is supported; other editions require
their own target evidence.

The first disposable acceptance attempt applied `dnf remove flatpak` in its
throwaway overlay. DNF removed 21 packages, including `gnome-software`,
`fedora-flathub-remote`, and 18 packages it classified as unused dependencies.
The test's exact-set assertion failed after that transaction. The guest was
stopped and the overlay retained only as failure evidence; the pinned base
image and host were unchanged. This confirms normal DNF removal is not a safe
inverse for the runtime or its dependents.
The second attempt confirmed that only the Flatpak RPM was erased. Its test
then correctly encountered that the absent package also removes the `flatpak`
CLI used to query remotes. Compare registered remote configuration file
hashes while the package is absent; query remote listings again after RIDE
installs the RPM. This preparation and preservation check passed, followed
by a separate profile smoke using the supported catalog status without
`--allow-candidate`. See the [acceptance record](../acceptance/package.flatpak.md).
