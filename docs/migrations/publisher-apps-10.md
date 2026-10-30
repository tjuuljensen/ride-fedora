# Legacy editor, portable IDE, and communication applications

Fast-track owner decisions: keep Arduino IDE, Discord, Joplin, and Vivaldi;
retire Atom editor and its plugin capability.

Status: **in review**, 2026-10-30. This v2 source batch maps
`ArduinoIDE`, `AtomEditor`, `AtomPlugins`, `Discord`, `Joplin`, and
`Vivaldi`. v2 downloads moving Arduino/Joplin AppImages to
`~/Applications`; adds an Atom repository with package signature checks
disabled and edits `~/.atom/init.coffee`; installs Atom plugins into user
state; requests a `discord` RPM; and fetches a Vivaldi RPM from a scraped
download page.

## Completion criteria defined before decisions

- For a runnable AppImage, pin the publisher artifact and hash, record its
  license, store an owned manifest outside user files, and prove that
  apply/repeat/status/inverse preserve an existing portable app and its data
  in a disposable Fedora 44 x86_64 Workstation VM. Do not run a remote
  installation script or delete by name glob.
- For a runnable third-party RPM or user plugin, prove current source and
  license, owned repository/key or plugin identity, detection, and inverse;
  run focused mocks and one Fedora VM happy path. Keep application
  configuration and user data out of package removal.
- Retire discontinued upstream paths with a concrete replacement or reopen
  trigger. Compare Windows schema/behavior, update ledger and generated
  docs. Keep these applications outside the small v3 base profiles until
  their declared deployment and recovery checks pass.

## Source decisions

The current source review finds
[Arduino IDE's executable](https://github.com/arduino/arduino-ide) under
AGPLv3 with component exceptions, [Atom](https://github.com/atom/atom/blob/master/LICENSE.md)
under MIT, [Joplin code](https://github.com/laurent22/joplin/blob/dev/LICENSE)
under AGPL-3.0-or-later with asset exceptions, and
[Discord](https://discord.com/terms) and
[Vivaldi](https://vivaldi.com/privacy/vivaldi-end-user-license-agreement/)
under their publisher terms. These licenses and terms do not transfer
Windows installer evidence to the Linux deployment.

- **ArduinoIDE: unsupported, non-runnable.** The publisher's
  [current Linux AppImage release](https://github.com/arduino/arduino-ide/releases)
  includes a versioned asset and SHA-256, but the v2 `latest` scrape and
  name-glob removal do not establish file ownership. Choose a pinned
  deployment with collision-safe storage and Fedora 44 VM
  lifecycle. Hardware upload is separate from the application install.

  The owner retained Arduino IDE as an optional v3 outcome on 2026-10-30.
  Choose the deployment form during migration and test its pinned acquisition,
  ownership, and inverse. The v2 moving AppImage path remains non-runnable.
- **AtomEditor: retired, non-runnable.** GitHub
  [sunset and archived Atom](https://github.blog/2022-06-08-sunsetting-atom/)
  in 2022. v2 also disables RPM package signature checks and overwrites a
  user's Atom initialization file. Reopen only for a specifically requested
  maintained successor with separate source and user-state ownership.
- **AtomPlugins: retired, non-runnable.** Its ten `apm` commands depend on
  the sunset Atom editor and can remove plugins installed independently by
  the user. Reopen for a maintained editor's explicit plugin set with
  per-user inventory and inverse.
- **Discord: unsupported, non-runnable.** The
  [publisher offers a Linux RPM](https://discord.com/download), but the v2
  `dnf install discord` request has no declared Fedora 44 source in v3, and
  v3 has no pinned publisher-RPM handler. Choose a
  publisher RPM or an owned Flathub deployment with verified bytes/source,
  preserved user profile, and disposable-VM happy path.
- **Joplin: unsupported, non-runnable.** The
  [publisher's Linux guidance](https://joplinapp.org/help/install/) uses a
  remote installation script; RIDE must not run it in a default profile.
  The v2 moving AppImage and glob inverse can overwrite or delete an
  existing app, while notebooks belong to the user. Reopen for a pinned
  portable deployment with notebook-preserving recovery and VM evidence.
- **Vivaldi: unsupported, non-runnable.**
  [Vivaldi supports Fedora 43+](https://help.vivaldi.com/desktop/install-update/install-the-vivaldi-browser/),
  but the v2 scraped RPM and publisher-managed repository/key lack an owned
  inverse. Reopen for a requested exact-version RPM with verified publisher
  origin, repository/key ownership, preserved browser profile, and VM
  happy path.

The owner retained optional Discord and Joplin for migration on 2026-10-30,
alongside Arduino IDE. Their v2 acquisition methods remain non-runnable.
Choose Discord's owned publisher RPM or Flathub source and prove user-profile
preservation; pin Joplin's deployment and prove notebook-safe recovery on
Fedora 44 Workstation.

The owner deferred the Vivaldi keep-or-retire decision on 2026-10-30. Its
v3.0 disposition remains non-runnable while source and browser-profile
recovery are clarified.
