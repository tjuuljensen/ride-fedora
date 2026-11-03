# ExpressVPN schedule migration paths

Status: **user-scoped rotation utility implemented; unattended schedule remains unverified**, 2026-11-03.
This review covers the kept workstation `ExpressVPNafterBoot` and
`ScheduleExpVPNChange` outcomes and the generic Server `VPNRandomizerPersistent`
outcome. It preserves the upstream `network-devices` source and its consumers.

## Current upstream path

ExpressVPN's official Linux CLI guide was updated 2026-10-05 and lists 64-bit
Fedora 39 and newer as supported. The app uses `expressvpnctl`, not the legacy
`expressvpn` CLI. Connection commands require the GUI to be running or
`expressvpnctl background enable`; the guide documents `connect` and `get
regions`, but does not document autoconnect preference inspection or mutation.
The command `expressvpnctl set autoconnect true` appears in the v4.0.1 release
notes from 2025-03-04. The current release notes list version 14.3.1 and GUI
auto-connect rules, but do not establish that the older CLI command or its
state/output contract applies to v14. The current GUI setup guide, updated
2026-10-30, documents launch-on-startup and publisher-managed auto-connect
rules for Wi-Fi and Ethernet, including connect or disconnect choices. Those
settings are user-configured in the GUI; the current CLI guide does not
document a corresponding v14 getter/setter. The account portal supplies the
`.run` installer and detached `.asc` signature, and activation requires an
account login or activation code.

A read-only inspection of the host's existing vendor binary on 2026-11-03
identified it as `4.0.1-beta+9292`. Its `-h` output lists `get autoconnect`
and `set autoconnect`; `expressvpnctl get autoconnect` returned `false` while
the ExpressVPN service was inactive. No setting was changed. This confirms
the observation command and boolean output for that beta binary only; it does
not validate v14 or Fedora 44 VM behavior.

The owner supplied the current v14.3.1.15429 `.run` and detached signature;
the signature verifies against ExpressVPN's published key fingerprint. The
installer has not been run, so current CLI behavior and Fedora 44 network
recovery remain unverified. Use the separate package-only review before
testing schedule behavior on a disposable Fedora target.

The same beta CLI help says startup autoconnect requires background mode. It
also says disabling background mode while the GUI is not running disconnects
the VPN and deactivates Split Tunnel. RIDE must not toggle background mode as
an incidental prerequisite: first establish its current-version behavior and
preserve its prior state, or require it to be enabled before changing only the
autoconnect preference. The official current CLI guide, last updated
2026-10-05, documents Fedora 39+, `expressvpnctl connect`, `get regions`, and
background mode, but does not document an autoconnect getter/setter. The
official 14.3.1 notes (2026-09-22) mention auto-connect rules but do not
confirm that the v4.0.1 CLI setting remains supported in v14.

- [Official Linux CLI setup](https://www.expressvpn.com/support/vpn-setup/app-for-linux-cli/)
- [Official Linux GUI setup and auto-connect](https://www.expressvpn.com/support/vpn-setup/app-for-linux/)
- [Official PGP verification instructions](https://www.expressvpn.com/support/vpn-setup/pgp-for-linux/)
- [Official Linux release notes](https://www.expressvpn.com/support/vpn-setup/release-notes/linux-app/)
- [Official Linux app setup](https://www.expressvpn.com/support/vpn-setup/app-for-linux/)

## v2 behavior and replacement candidates

| Kept outcome | v2 behavior | Better v3 path to investigate | Remaining evidence |
| --- | --- | --- | --- |
| `ExpressVPNafterBoot` | The inverse removes the exact text `@reboot sleep 10 && expressvpn connect` from the user's crontab, regardless of who created it. Its paired v2 action writes that job. | **Replaced for v3.0** by ExpressVPN's publisher-managed GUI auto-connect to the last location on startup, with optional network-specific rules. Follow the [replacement procedure](../../reference/expressvpn-autoconnect.md); RIDE does not manipulate vendor preferences or add a custom timer. | The current official GUI guide documents the preference for Fedora 39+ on 64-bit Linux. Existing v2 crontab cleanup remains manual because the line has no ownership marker; inspect with the owner and preserve unrelated entries. |
| `ScheduleExpVPNChange` | The v2 inverse removes any crontab line exactly matching `0 */6 * * * /usr/sbin/expressvpn-randomizer.sh`, regardless of ownership. The paired action runs a mutable script every six hours. | A user-scoped utility now reads an explicit allowlist and submits `expressvpnctl connect LOCATION` without disconnecting first. See [ExpressVPN rotation tool](../../reference/expressvpn-rotation.md). It does not install a timer. | Verify current v14 command behavior and connection recovery on a disposable authenticated Fedora target before adding unattended scheduling. Preserve active VPN state and unrelated jobs on failure and removal. |
| Server `VPNRandomizerPersistent` | The active `network-devices` implementation writes both a reboot connect cron line and the six-hour randomizer cron line. `complete` and `streambox` presets consume it. | Reuse the same current-client interfaces, with an explicit server-owned service identity, boot preference, allowed-region list, and systemd timer. Keep the product installer and activation private. | Confirm service identity and consumers with the `network-devices` owner before moving ownership. Test boot/reconnect, route/DNS preservation, timer failure, and rollback on a disposable Fedora 44 Server with a permitted test account. |

## Server source ownership checkpoint

Read-only inspection on 2026-11-03 found the authoritative server source at
`/home/tjuuljensen/git/network-devices/operations/provisioning/ride/lib-fedora-server.sh`
in `network-devices/master` commit
`dfcda01f90a5568ecff093fec8e9c6a3111fe76d`; that checkout was clean. Its
`complete.preset` and `streambox.preset` select
`SetVPNRandomizerPersistent`; `plexserver.preset` comments it out. The source
creates `/usr/sbin/expressvpn-randomizer.sh`, which runs the legacy
disconnect-first `expressvpn` sequence, and appends reboot and six-hour jobs to
the crontab of the user executing the preset. It does not record that user's
identity or provide an exact inverse. `INSTALL2` only manages command
symlinks; the current `network-devices` checkout contains no preset executor,
and the `RequireAdmin` helper invoked by the presets is not defined there.
The related `network-devices/inventory/components.yaml` record names the
`ride-legacy` owner as Torsten and describes deployment as "INSTALL2 and
preset-driven shell library", but marks `usage_status: unknown` and
`last_verified: null`. This identifies the source owner and recorded
deployment model; it does not identify deployed hosts, an executor, or the
runtime crontab owner.
Therefore the actual deployed machines, executor identity, runtime crontab
owner, publication/deployment route, job history, and recovery were not
verified. Do not treat this missing runtime trail as evidence of inactivity.
Do not remove or replace this source until its owner confirms deployed
consumers and agrees on the handoff and rollback.

## Completion checks before implementation

- Keep publisher installation/activation separate from scheduling; RIDE must
  not store activation codes, inspect account profiles, or connect during apply.
- For startup preference, detect and save the exact prior value without putting
  private app state in the journal; repeat and restore only that value.
- Treat background mode as a separate state. If the selected client requires
  it, refuse the migration unless its current state and exact inverse are
  proven; never disconnect an active VPN or change Split Tunnel state as a
  side effect of applying or restoring autoconnect.
- For timed rotation, use a named allowed-location list and an owned timer;
  preserve unrelated timers, user services, route, DNS, and connection state
  on apply failure and remove/restore.
- Run mocked parser/ownership/recovery tests first. Then require one focused
  disposable Fedora 44 x86_64 happy path for each edition whose behavior
  differs. Exercise a failure before retrying it. A fake `expressvpnctl` can
  validate command construction but cannot establish route, DNS, kill-switch,
  or reconnect safety.
- Keep the implementation out of base profiles. Promote only after the
  publisher CLI and network recovery evidence pass the high-risk gate.

The older randomizer command sequence (`expressvpn refresh`, `disconnect`,
`list all`, then `connect`) is not carried forward. The new user-scoped tool
accepts a newline-delimited allowlist, avoids repeating its last successful
request when another location is configured, defaults to a no-change preview,
and writes state only after `expressvpnctl connect LOCATION` exits successfully.
It does not query the current connection or confirm tunnel, route, or DNS state;
do not treat the CLI response as full recovery evidence or schedule it unattended
yet. The local beta's autoconnect
getter narrows one observation gap, but there is no owner-authorized v14 client
in the disposable test image. Keep these outcomes unresolved until current
version behavior and private authenticated runtime are verified.
