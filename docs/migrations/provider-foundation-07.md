# Provider foundation batch 07: HandBrake RPM Fusion source

Status: **unsupported on the declared v3.0 target until its provider is
accepted**, 2026-10-30. The commented v2 pair `InstallHandBrake` and
`RemoveHandBrake` invokes DNF for `HandBrake`. The
[RPM Fusion Fedora 44 x86_64 index](https://download1.rpmfusion.org/free/fedora/updates/44/x86_64/h/)
lists `HandBrake` 1.11.2 and a separate `HandBrake-gui` RPM. The
[HandBrake project](https://handbrake.fr/project_information.php) describes
its GPL-2.0 license and points Linux users to Flathub. RPM Fusion is a
third-party package source, not an automatically trusted Fedora repository.

## Completion criteria defined before resolution

- Preserve the v2 DNF package intent and distinguish the CLI RPM from the
  GUI RPM; do not infer that `HandBrake` alone supplies the desktop app.
- Permit an opt-in candidate only after the RPM Fusion provider has an
  accepted trust and owned recovery contract, HandBrake's exact package and
  dependencies are reviewed, focused mocked failure checks pass, and a
  disposable Fedora 44 x86_64 Workstation VM passes its package happy path.
  Keep it out of `default` and `server-base`.
- Otherwise give the source outcome a non-runnable v3.0 disposition with a
  clear review trigger. An upstream Flatpak alternative requires its own
  remote, application, data, and inverse evidence; it is not an implicit
  fallback for this RPM outcome.

## v3.0 decision

The separate [RPM Fusion source batch](provider-foundation-02.md) has not
established independent signing-key trust or ownership of repository files
and keys. The current Fedora DNF handler cannot install from this provider
without that prerequisite. The v2 function does not declare a repository
source, cannot prove the RPM's provenance, and has no GUI selection. A
HandBrake operation would therefore fail the declared third-party candidate
gate before its exact-target VM happy path.

This source outcome is **unsupported in v3.0**, with no runnable catalog row
or install acceptance. The owner retained HandBrake as an optional migration
outcome on 2026-10-30. Accept the RPM Fusion trust and recovery gate, choose
the CLI or GUI scope, then test that deployment on the declared Workstation
VM. Separately review Flathub only if a Flatpak distribution is requested.
This decision does not claim HandBrake itself or Fedora 44 is unsupported by
its publisher.
