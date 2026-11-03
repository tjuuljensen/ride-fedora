# ExpressVPN v14.3.1.15429 install and uninstall acceptance

Status: **the vendor uninstall paths fail recovery checks; the RIDE wrapper
passes its Fedora 44 Server and Workstation lifecycle**

Target: Fedora 44 Server x86_64, image
`efb75956d6dbde0801059fdac4a8a1451f06ecc843344ecdb71bb3e8d247af90` from
`tests/acceptance/targets.json`. The test ran in a fresh QEMU overlay from the
repository's pinned Server image. No account activation or VPN connection was
performed.

## Artifact and preparation

The owner supplied the `.run` and matching `.asc` outside the repository. The
detached signature verified against ExpressVPN's published key fingerprint
`1D0B09AD6C93FEE93FDDBD9DAFF2A1415F6A3A38`. Installer SHA-256:
`f784af6628564f4fcb0a82064d4dc1f22520c3c917bb1c882bd61eb621b31efb`.

The installer rejects execution through `sudo` when `SUDO_USER` remains set.
The successful pilot invoked it as root with that variable removed, using
`--no-gui --force-update`. Before installation, the guest had no
`libatomic`; installing the vendor-listed Fedora `libatomic` prerequisite
allowed the installer to continue. The installer then installed `brotli` and
upgraded `libbrotli` through DNF.

The guest was seeded with a pre-existing
`/etc/NetworkManager/conf.d/wgexpressvpn.conf` and a marker under
`/home/ride-test/.config/expressvpn`. The file and marker were unchanged after
installation. There were no active VPN connections before or after install.

## Observed headless lifecycle

- Install exited 0. It created `/opt/expressvpn`, the desktop entry and CLI,
  the `expressvpn-service.service` unit, and ExpressVPN groups.
- `expressvpn-service` was enabled and active after install.
- The service added policy-routing rules at priorities 50 and 70. The main
  route table did not change. No VPN connection became active.
- The bundled `/opt/expressvpn/bin/expressvpn-uninstall.sh` exited 0, but left
  `expressvpn-service` enabled and
  active. The script looked for `expressvpn.service`, while the installer had
  created `expressvpn-service.service`.
- The uninstaller deleted the seeded NetworkManager config, even though the
  installer had left it unchanged because it already existed.
- The non-root user's seeded config marker remained. Root's ExpressVPN config
  was absent after removal.
- The uninstaller did not restore the pre-install policy-routing rules.
  `brotli` remained installed and `libbrotli` remained at the upgraded version.

This Server probe used `--no-gui` and invoked the bundled shell uninstaller.

## Workstation GUI lifecycle

Target: Fedora 44 Workstation x86_64, pinned image digest
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178` from
`tests/acceptance/targets.json`. The run used a fresh QEMU overlay, Xvfb, a
persistent D-Bus session, and Openbox. A full `gnome-session` could not start
under the SSH boot because the guest had no user systemd manager; the
ExpressVPN window itself rendered and the documented controls were reachable.
The installer SHA-256 matched the verified owner-supplied artifact above.

The GUI opened in a logged-out **Not Protected** state. No account login,
activation, or VPN connection occurred. The test followed the vendor's
[Profile → Actions → Uninstall ExpressVPN → Uninstall procedure](https://www.expressvpn.com/support/vpn-setup/app-for-linux/).
The GUI launched its bundled uninstaller in xterm, which required a second
`Proceed with uninstall? [y/N]` confirmation. It reported “Uninstall finished.”

Final state after the uninstaller closed:

- `/opt/expressvpn` and the desktop entry were removed.
- `expressvpn-service.service` remained enabled and failed because its
  executable under `/opt/expressvpn` had been removed.
- ExpressVPN policy-routing rules were removed; the normal route table and
  unrelated NetworkManager profile remained.
- The seeded `/etc/NetworkManager/conf.d/wgexpressvpn.conf` and
  `/home/ride-test/.config/expressvpn/owner-marker.txt` were deleted. The
  unrelated seeded NetworkManager file retained its exact SHA-256.
- Vendor-added `brotli` remained installed and `libbrotli` remained upgraded.
- The disposable overlay was stopped and discarded after evidence collection.

The Workstation test therefore confirms the GUI path's user-visible behavior,
but not a safe removal inverse. It is an X11/Openbox session on the pinned
Workstation image, not a GDM-launched GNOME session.

## Result and next action

Neither vendor uninstall path is a safe RIDE inverse as tested. The Workstation
GUI path leaves a failed enabled service and deletes user and NetworkManager
state; the Server headless path also leaves service, routing, and dependency
changes. Keep activation and connection outside migration scope. The RIDE
wrapper below owns the inverse and leaves shared RPM dependencies installed.

The Server transcript and overlay remain under
`.acceptance-runs/expressvpn-v14-server-lifecycle/`. Workstation screenshots,
final-state report, baseline, installer log, SSH test material, and transcript
are under
`.acceptance-runs/20261103T083035Z-expressvpn-v14-workstation-gnome-uninstall/`.
The overlay and generated private SSH key were deleted after shutdown; the
remaining local acceptance evidence is not published.

## RIDE wrapper acceptance, 2026-11-03

The `package.expressvpn` RIDE wrapper passed its complete install/repeat/remove scenario against
fresh pinned Fedora 44 Server and Workstation overlays using the owner-supplied
installer and detached signature plus ExpressVPN's public signing key. Both
target runs verified the signature, installed headlessly without login or
connection, repeated apply as unchanged, and removed through RIDE. They
confirmed the seeded NetworkManager config, route-table registry, and root
config were restored exactly; a seeded unrelated priority-100 policy rule was
restored; ExpressVPN service and rules were removed; and the status returned to
absent. The vendor-added `libatomic` dependency remains installed. No account
activation data was used.

Seven focused mocked tests pass for pinned artifact identity, repeat/remove,
connected-client refusal, changed or missing pre-existing-state refusal,
conflicting policy-rule refusal, and incomplete-install refusal. These are
opt-in `candidate` results; broader failure injection, upgrade, and publisher
recovery checks remain in the named v3.1 hardening queue.

Local evidence and transcripts are under:

- Server: `.acceptance-runs/expressvpn-wrapper/fedora-44-server-x86_64/20261103T103022Z-test-expressvpn-wrapper-exact-install-repeat-remove-fedora-44-server-x86-64-b47655d6/`
- Workstation: `.acceptance-runs/expressvpn-wrapper/fedora-44-workstation-x86_64/20261103T103325Z-test-expressvpn-wrapper-exact-install-repeat-remove-fedora-44-workstation-x86-64-24be62cd/`
