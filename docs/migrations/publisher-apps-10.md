# Legacy editor, portable IDE, and communication applications

Fast-track owner decisions: keep Arduino IDE, Discord, Joplin, and Vivaldi;
retire Atom editor and its plugin capability.

Status: **Arduino IDE, Joplin, and Discord are operable opt-in candidates;
Vivaldi is an operable opt-in Flatpak candidate; two Atom outcomes
retired**, updated
2026-11-01. This v2 source batch maps
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

## Current v3 paths and source review

- **Arduino IDE:** owner-kept. Upstream publishes Arduino IDE 2.3.10 as a
  versioned Linux x86_64 AppImage with the release API's SHA-256. Upstream says
  its distribution is AGPL-3.0-or-later and includes compatible third-party
  licenses. RIDE pins the AppImage and installs it under `~/Applications` with
  an owned manifest. Sketches, board data, USB permissions, and board uploads
  remain outside the operation. The install lifecycle is implemented; exact
  Fedora 44 acceptance remains pending. See
  [Arduino acceptance](../acceptance/package.arduino-ide.md).
- **AtomEditor:** retired. GitHub sunset and archived Atom in 2022. v2 also
  disables RPM package signature checks and overwrites the user's Atom init
  file. Reopen only on a specific maintained successor request.
- **AtomPlugins:** retired. Its `apm` plugin set depends on the sunset editor
  and its name-based inverse can remove independently installed plugins.
- **Discord:** owner-kept. The official download page's stable RPM currently
  resolves to Discord 1.0.168. RIDE pins the versioned RPM URL and its observed
  SHA-256, checks RPM name/version/architecture before installation, and
  removes only the `discord` package. Discord does not publish a verifiable
  signature for this direct RPM, so the operation remains an opt-in candidate
  with digest plus metadata verification. A disposable VM acceptance path
  checks profile preservation. Login, voice, and screen sharing remain v3.1
  checks. See [Discord acceptance](../acceptance/package.discord.md).
- **Joplin:** owner-kept. Joplin 3.7.22 has a versioned Linux AppImage and a
  GitHub release SHA-256; the source is AGPL-3.0-or-later with separately
  licensed assets. The current Flathub build remains at 3.6.14, below Joplin's
  3.7.0 sync compatibility requirement, so v3 pins the newer publisher
  AppImage. The v3.7.18 AppImage had a Fedora 44 launch report; acceptance
  checks the newer release runtime while leaving notebooks and configuration
  untouched. Do not use the publisher's moving install script. See
  [Joplin acceptance](../acceptance/package.joplin.md).
- **Vivaldi:** retained in the v3.0 scope under the owner's instruction that
  every kept v2 outcome remains available. The initial path is the documented
  Flathub Flatpak, an opt-in candidate authenticated by the signed Flathub
  system remote. Its profile remains under `~/.var/app/com.vivaldi.Vivaldi`
  after removal. Acceptance is pending; native messaging, sign-in, sync, and
  browser behavior are tracked in H080. A separately selectable official RPM
  remains possible after explicit repository/key ownership and exact rollback
  are implemented. Do not use the publisher's `--nogpgcheck` bootstrap.

Source links: [Arduino 2.3.10 release](https://github.com/arduino/arduino-ide/releases/tag/2.3.10),
[Arduino IDE license](https://raw.githubusercontent.com/arduino/arduino-ide/2.3.10/LICENSE.txt),
[Arduino IDE project license notes](https://github.com/arduino/arduino-ide),
[Arduino Linux download guidance](https://support.arduino.cc/hc/en-us/articles/360019833020-Download-and-install-Arduino-IDE),
[Discord Linux downloads](https://discord.com/download),
[Joplin 3.7.22 release](https://github.com/laurent22/joplin/releases/tag/v3.7.22),
[Joplin Flathub package](https://flathub.org/en/apps/net.cozic.joplin_desktop),
[Joplin Fedora 44 AppImage issue](https://github.com/laurent22/joplin/issues/16558),
[Vivaldi Fedora support](https://help.vivaldi.com/desktop/install-update/install-the-vivaldi-browser/),
[Vivaldi package signing](https://help.vivaldi.com/desktop/install-update/obtaining-official-builds/),
[Vivaldi Flatpak instructions](https://help.vivaldi.com/desktop/install-update/install-vivaldi-on-flatpak/),
[Vivaldi Flathub package](https://flathub.org/en/apps/com.vivaldi.Vivaldi).

The owner kept Arduino IDE, Discord, and Joplin on 2026-10-30 and later
clarified that all kept v2 outcomes remain in v3.0 scope. Vivaldi's documented
Flathub deployment is therefore included as an opt-in candidate; its official
RPM remains a separately managed deployment that can be added after its
repository lifecycle is owned and verified.
