# File managers and legacy publisher applications

Status: **one opt-in candidate and five non-runnable decisions**, 2026-10-30. This batch maps the commented v2
`CommanderFileMgrs`, `PowerShell`, `MicrosoftTeams`, `WoeUSB`, and
`BalenaEtcher` outcomes and the active `SonosPlayer` outcome. v2 installs
`gnome-commander` and `mc` together; its inverse removes both by name.
PowerShell adds a RHEL 7 Microsoft repository and key; Teams scrapes a
publisher RPM listing; WoeUSB requests a Fedora RPM; Etcher scrapes a moving
GitHub RPM; Sonos downloads a moving AppImage into `~/Applications` and its
inverse deletes matching names.

## Completion criteria defined before implementation

- Split the two signed Fedora file-manager RPMs into separate operations and
  a curated opt-in profile. On the exact Fedora 44 x86_64 Workstation VM,
  check absent plan, apply, signed RPM/files, CLI or desktop-entry probe,
  repeat, status, restore, explicit remove, and profile smoke. Reuse the
  unchanged DNF handler's mocked failure evidence. Do not claim a visual
  GNOME session without one.
- For external applications, verify current publisher method, target and
  license. Any runnable external RPM or AppImage needs pinned provenance,
  owned destination/key, safe detection and inverse, focused mocked tests,
  and a disposable-VM happy path. Keep user data and removable media outside
  the package install inverse. If these conditions cannot be met in v3.0,
  record a specific non-runnable disposition and reopen trigger.
- Compare Windows schemas and behavior, update ledger and generated docs,
  and investigate VM failures before retrying.

## External application decisions

- **PowerShell: unsupported and non-runnable in v3.0.** The v2 method adds
  Microsoft's RHEL 7 repository to Fedora and imports a system-wide key.
  [Microsoft's current PowerShell RPM instructions](https://learn.microsoft.com/en-us/powershell/scripting/install/install-rhel)
  cover supported RHEL versions and a universal RPM, but do not establish
  Fedora 44 support or ownership of an existing Microsoft repository/key.
  Reopen for a requested Fedora deployment with pinned RPM/source, owned
  repository/key handling, and a VM apply/inverse that preserves pre-existing
  Microsoft products.
- **Microsoft Teams: documented non-runnable replacement.**
  [Microsoft no longer supports a Linux desktop client](https://learn.microsoft.com/microsoftteams/get-clients)
  and directs users to Teams on the web. Do not scrape the old `ms-teams`
  RPM listing. Reopen only if Microsoft publishes a supported Fedora desktop
  client or an explicit browser/PWA operation is requested with owned state.
- **WoeUSB: unsupported and non-runnable in v3.0.**
  [Fedora's WoeUSB package](https://packages.fedoraproject.org/pkgs/WoeUSB/WoeUSB/)
  is orphaned and its release table ends at Fedora 41. The v2 DNF name does
  not provide a Fedora 44 package. A requested WoeUSB-ng successor needs
  a reviewed source/license and a safe package inverse; writing USB media
  remains an explicit user action outside RIDE apply.
- **balenaEtcher: unsupported and non-runnable in v3.0.** The publisher
  [does ship a versioned x86_64 RPM with a SHA-256](https://github.com/balena-io/etcher/releases),
  but v2 selects a moving GitHub release URL and the v3 catalog has no
  pinned external-RPM acquisition handler. Choose a pinned
  publisher RPM with verified bytes, installed-package detection, collision
  handling, and disposable-VM happy path. Flashing media is separate from
  installing the application and must be user-initiated.

  The owner retained this optional USB imaging application for migration on
  2026-10-30. The next implementation batch should pin the publisher RPM and
  prove installed identity, collision handling, and Fedora 44 recovery;
  retaining the product does not authorize the v2 moving-release scrape.
- **SonosPlayer: retired and non-runnable.** The source
  [declares the unofficial controller deprecated](https://github.com/pascalopitz/unoffical-sonos-controller-for-linux)
  and its latest release is an AppImage-only release candidate. The v2
  moving download and name-glob inverse can delete a pre-existing portable
  app. Reopen only for an explicitly requested maintained client with a
  pinned license/artifact, owned destination, and app-data-preserving VM
  lifecycle.

## Fedora 44 file-manager result

`package.gnome-commander` and `package.mc` each passed absent plan,
candidate-gated apply, signed RPM/file checks, installed status, unchanged
repeat, restore, and explicit install/remove in the pinned disposable
Workstation VM. GNOME Commander shipped an executable; Midnight Commander
reported its version when the headless SSH probe set `TERM=xterm`. The first
attempt failed only on that missing test terminal environment; the corrected
probe passed in a fresh overlay. The curated `commander-file-managers`
profile passed plan/apply/repeat/restore. Pre-existing RPM identities were
preserved. Mocked failure evidence is reused from the unchanged DNF handler.
See [`package.gnome-commander`](../acceptance/package.gnome-commander.md)
and [`package.mc`](../acceptance/package.mc.md).

The source `CommanderFileMgrs` outcome is an **operable opt-in candidate**;
the profile requires `--allow-candidate` and stays outside `default`.
GNOME session visual behavior and broader recovery are H014 in v3.1.
