# ExpressVPN current Linux handoff

Status: **kept, private publisher handoff for v3.0**. This decision covers the
workstation `InstallExpressVPN`/`RemoveExpressVPN` source and the shared Server
`InstallExpressVPN` source. It retains the product and its migration record;
it does not claim a RIDE-managed install or remove operation.

## Current official Fedora path

ExpressVPN's current Linux setup pages support Fedora 39 and newer on 64-bit
systems. The vendor directs users to sign into the account setup portal, choose
Linux, and download an account-provided `.run` installer. The installer runs
with administrator authorization and starts the app. Account activation then
requires sign-in or an activation code. The current CLI guide documents
`expressvpnctl` and an `expressvpn-uninstall.sh` script; the GUI app provides an
interactive in-app uninstaller. The older DNF `expressvpn` package removal
instructions apply to the legacy CLI app, not the current GUI installer.

Sources: [official Linux GUI setup](https://www.expressvpn.com/support/vpn-setup/app-for-linux/),
[official Linux CLI setup](https://www.expressvpn.com/support/vpn-setup/app-for-linux-cli/),
[official uninstall instructions](https://www.expressvpn.com/support/troubleshooting/uninstall-expressvpn-app/),
and [official Fedora support matrix](https://www.expressvpn.com/vpn-download/vpn-linux).

## Why RIDE does not automate this installer in v3.0

- The installer is retrieved from the authenticated customer portal; no public,
  stable Fedora RPM URL or publisher checksum/signature procedure is documented
  for RIDE to pin and verify.
- Installing and removing the current app are vendor-owned privileged paths.
  The installer launches the app, and initial setup can enable startup behavior,
  network lock, routing, DNS, and a VPN connection.
- Activation material, connection profiles, service state, and the prior host
  routing/DNS/firewall state are private and security-sensitive. RIDE has no
  owner-supplied state boundary or recovery evidence for those mutations.

For now, users keep the current vendor portal, installer, activation, and
vendor uninstaller as an explicit private handoff outside RIDE profiles. This
is not a retirement of ExpressVPN. Do not copy activation codes, portal URLs,
installer artifacts, profiles, or network state into this repository.

## Reopen trigger

Reopen when the owner provides a permitted acquisition path with verifiable
publisher provenance and a disposable Fedora 44 package-only test can prove
install/remove without activating, connecting, changing startup or network-lock
preferences, or losing seeded NetworkManager profiles and existing routing/DNS
state. Server and Workstation editions require their own exact-target evidence.
