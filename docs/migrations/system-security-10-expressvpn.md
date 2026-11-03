# ExpressVPN signed installer path review

Status: **kept; opt-in candidate passed mocked and disposable-VM lifecycle
checks on Fedora 44 Workstation and Server**. This review covers the
workstation `InstallExpressVPN`/`RemoveExpressVPN` source and the shared Server
`InstallExpressVPN` source. It retains the product and its migration record;
the wrapper does not activate or connect the client.

## Current official Fedora path

ExpressVPN's current Linux setup pages support Fedora 39 and newer on 64-bit
systems. The vendor directs users to sign into the account setup portal, choose
Linux, and download an account-provided `.run` installer. The installer runs
with administrator authorization and starts the app. Account activation then
requires sign-in or an activation code. The current CLI guide documents
`expressvpnctl` and an `expressvpn-uninstall.sh` script; the GUI app provides an
interactive in-app uninstaller. The older DNF `expressvpn` package removal
instructions apply to the legacy CLI app, not the current GUI installer.

The publisher also documents a detached PGP signature for the portal-downloaded
installer. Its current verification guide publishes key ID
`AFF2A1415F6A3A38`, fingerprint
`1D0B09AD6C93FEE93FDDBD9DAFF2A1415F6A3A38`, and the `.asc` signature workflow.
This gives RIDE a verifiable artifact path if an owner obtains the installer
and signature from the authenticated portal. The bytes and signature must stay
outside the public repository.

Sources: [official Linux GUI setup](https://www.expressvpn.com/support/vpn-setup/app-for-linux/),
[official Linux CLI setup](https://www.expressvpn.com/support/vpn-setup/app-for-linux-cli/),
[official Linux installer PGP verification](https://www.expressvpn.com/support/vpn-setup/pgp-for-linux/),
[official Linux release notes](https://www.expressvpn.com/support/vpn-setup/release-notes/linux-app/),
[official uninstall instructions](https://www.expressvpn.com/support/troubleshooting/uninstall-expressvpn-app/),
and [official Fedora support matrix](https://www.expressvpn.com/vpn-download/vpn-linux).

## Local artifact check, 2026-11-03

The owner supplied the current `expressvpn-linux-universal-14.3.1.15429_release.run`
and its `.asc` companion outside the repository. The installer SHA-256 is
`f784af6628564f4fcb0a82064d4dc1f22520c3c917bb1c882bd61eb621b31efb`. The
signature was checked in an isolated GnuPG home against the key retrieved from
ExpressVPN's published key URL. Its full fingerprint
`1D0B09AD6C93FEE93FDDBD9DAFF2A1415F6A3A38` matches the publisher's current
verification guide, and GnuPG reports a good signature dated 2026-09-22. The
key's trust warning is expected for a fresh keyring; trust was established by
comparing the full fingerprint with the independently published fingerprint.
The artifact was later executed in disposable Fedora 44 Server and Workstation
pilots, documented in
[`docs/acceptance/package.expressvpn.md`](../acceptance/package.expressvpn.md).
The installer and signature remain outside this repository.

Static inspection of its Makeself payload identifies version `14.3.1+15429`
and an x86_64 installer. The install script installs dependencies, places the
application under `/opt/expressvpn`, enables and restarts the ExpressVPN
systemd service, adds a desktop entry and CLI symlink, and may add a
NetworkManager unmanaged-device rule for ExpressVPN WireGuard interfaces. On
the headless Server pilot, the bundled shell uninstaller stopped neither the
actual `expressvpn-service.service` unit nor the policy-routing rules, and it
deleted a pre-existing NetworkManager config. The publisher's GUI support page
documents a separate Profile → Actions → Uninstall ExpressVPN path. A
Workstation GUI launch under Xvfb and Openbox with a persistent D-Bus session
rendered the app and exposed the documented uninstall path. The owner completed
the uninstall confirmation in the disposable VM. It removed app files and
policy-routing rules, but left `expressvpn-service.service` enabled in a failed
state and deleted a seeded NetworkManager config and user config marker. The
unrelated NetworkManager fixture remained unchanged. The test used Openbox
rather than a GDM-launched GNOME session because the SSH boot had no user
systemd manager; the app controls themselves were visible and operable. These
findings are separate from the Server shell path and do not establish a safe
RIDE inverse.

A local file named `expressvpn-linux-universal-5.1.0.12141_release.run` was
found with SHA-256
`e1c81b6c08ba94dbba88d4afb2c3d757187754b3c85691a9429424096df51eca`.
Static inspection identifies a Makeself 2.5.0 self-extracting archive. Its
header has an empty `SIGNATURE` field and a zero-filled `SHA` field; the
download directory contained no matching `.asc`, `.sig`, or checksum file.
The file has not been extracted or executed and is not accepted as an
authenticated publisher artifact.

The publisher release notes date v5.1.0 to 2026-01-27 and list v14.3.1 on
2026-09-22. The local v5.1.0 file therefore does not provide the current v14
installer/runtime needed for the migration. The owner supplied the current
portal installer and detached `.asc` pair, and that exact pair was used for
Fedora 44 acceptance.

A follow-up filename and companion-file scan under `~/Downloads` initially
found only the older `expressvpn-linux-universal-4.0.1.9292.run` from
2025-03-23 and the 5.1.0.12141 file above. The 4.0.1 artifact is the old beta
client whose CLI behavior is recorded in the schedule review; it does not
authenticate the newer package path. The separately supplied v14.3.1.15429
pair is documented at the start of this section.

## v3 wrapper and current boundary

The `package.expressvpn` operation stages the account-portal `.run`, matching
`.asc`, and publisher key locally. Before execution it checks the pinned
SHA-256, imports the key into a temporary private GnuPG home, compares the full
fingerprint, and verifies the detached signature. Installation is headless
(`--no-gui --force-update`) and does not sign in, activate, or connect. The
wrapper snapshots the exact pre-existing NetworkManager config, routing table
registry, and root ExpressVPN config under private RIDE state. Removal refuses
an active VPN connection, invokes the vendor uninstaller, disables the actual
service unit, removes only the exact ExpressVPN policy rules, and restores
those snapshots. It refuses to overwrite state changed after install.
`libatomic` and other vendor-added RPM dependencies remain installed after
removal because they are shared system packages.

The operation is `candidate` and appears only in the opt-in
[`fedora-expressvpn`](../../profiles/fedora-expressvpn.json) profile. Stage the
owner-obtained installer and signature, then fetch the public signing key:

```bash
sudo install -d -o root -g root -m 0700 /var/cache/ride-fedora/artifacts/package.expressvpn
sudo install -o root -g root -m 0700 \
  "$HOME/Downloads/expressvpn-linux-universal-14.3.1.15429_release.run" \
  /var/cache/ride-fedora/artifacts/package.expressvpn/
sudo install -o root -g root -m 0600 \
  "$HOME/Downloads/expressvpn-linux-universal-14.3.1.15429_release.run.asc" \
  /var/cache/ride-fedora/artifacts/package.expressvpn/
sudo curl --fail --location --output \
  /var/cache/ride-fedora/artifacts/package.expressvpn/expressvpn_release_public_key_0xAFF2A1415F6A3A38.asc \
  https://www.expressvpn.com/expressvpn_release_public_key_0xAFF2A1415F6A3A38.asc
sudo chown root:root /var/cache/ride-fedora/artifacts/package.expressvpn/expressvpn_release_public_key_0xAFF2A1415F6A3A38.asc
sudo chmod 0600 /var/cache/ride-fedora/artifacts/package.expressvpn/expressvpn_release_public_key_0xAFF2A1415F6A3A38.asc
sudo ./ride.sh plan --profile profiles/fedora-expressvpn.json --allow-candidate
sudo ./ride.sh apply --profile profiles/fedora-expressvpn.json --allow-candidate
```

To remove the app, run `sudo ./ride.sh remove package.expressvpn --allow-candidate`.
Seven focused mocked tests pass for signed artifact identity, apply/repeat/remove,
connected-client refusal, changed or missing-state refusal, conflicting
policy-rule refusal, and incomplete-install refusal. The actual RIDE wrapper also passed install, no-activation status,
repeat, and removal on both declared Fedora 44 targets. See the target results
in [`docs/acceptance/package.expressvpn.md`](../acceptance/package.expressvpn.md).
The operation remains an opt-in `candidate`; broader recovery and upgrade
scenarios are tracked in the v3.1 hardening queue.

Do not copy activation codes, portal URLs, installer artifacts, signatures,
profiles, or network state into this repository. This investigation is not a
retirement of ExpressVPN.

## v3.1 hardening trigger

Extend failure injection, upgrades, DNS/startup behavior, and dependency
recovery under H002. Keep edition-specific evidence separate. The v3.0
candidate acceptance is complete for the declared install/remove lifecycle.
