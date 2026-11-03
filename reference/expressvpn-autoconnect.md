# ExpressVPN startup auto-connect replacement

Status: **documented v3.0 replacement for the Workstation startup-connect
capability**. This procedure keeps the behavior through ExpressVPN's own Linux
app setting. RIDE does not set VPN preferences, install or activate the client,
connect, or manage VPN credentials.

## Fedora target and publisher path

ExpressVPN's current Linux GUI supports 64-bit Fedora 39 and newer, which
includes the declared Fedora 44 Workstation target. The publisher's GUI setup
guide documents both connecting to the last used location on startup and
auto-connect rules for secure Wi-Fi, unsecured Wi-Fi, and Ethernet. The rules
can connect or disconnect according to the user's choice.

The app is proprietary and is downloaded from the account portal. The publisher
provides a detached `.asc` signature for the installer and publishes the PGP
key fingerprint. RIDE does not redistribute the installer or accept account or
activation data.

## Configure startup connection

1. Install and sign in to the ExpressVPN Linux app using the publisher's
   current account instructions.
2. In the app, select **Profile > Settings > Auto-connect**.
3. Enable auto-connect to the last location on startup.
4. If needed, add network-specific rules for secure Wi-Fi, unsecured Wi-Fi, or
   Ethernet, choosing **Connect to VPN** or **Disconnect from VPN** for each.
5. Confirm the app reports the selected location and preference. Do not enable
   a rule that changes an existing connection unless that is the user's intent.

The app owns this preference and its UI provides the inverse: disable
auto-connect or remove an individual network rule. The current official Linux
CLI guide documents connection and location commands but does not document a
v14 auto-connect getter/setter. RIDE therefore leaves this preference
user-managed instead of writing unsupported vendor state or creating a new
cron/systemd job.

## Existing v2 crontab lines

The v2 action appended `@reboot sleep 10 && expressvpn connect` to the invoking
user's crontab, without an ownership marker. RIDE must not delete a matching
line automatically. Before enabling the GUI replacement, inspect the user's
crontab and remove that exact line only if the user confirms it is the obsolete
RIDE v2 job. Preserve unrelated crontab entries.

## Reopen trigger

Reopen if the publisher removes or changes Linux startup auto-connect, if a
supported v14 CLI state interface becomes available and the user requests RIDE
management, or if the migration requires automated cleanup of legacy jobs. Any
RIDE-managed VPN setting must first prove exact prior-state capture, restore,
boot/reconnect behavior, and network recovery on a disposable Fedora 44
Workstation; do not activate or connect on an ordinary host for migration
acceptance.

## Publisher sources

- [Official Linux GUI setup and auto-connect](https://www.expressvpn.com/support/vpn-setup/app-for-linux/)
- [Official Linux CLI setup](https://www.expressvpn.com/support/vpn-setup/app-for-linux-cli/)
- [Official Linux installer PGP verification](https://www.expressvpn.com/support/vpn-setup/pgp-for-linux/)
- [Official Linux release notes](https://www.expressvpn.com/support/vpn-setup/release-notes/linux-app/)
