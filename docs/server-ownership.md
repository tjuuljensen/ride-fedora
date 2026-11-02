# Server library boundary

The existing server source is
`network-devices/operations/provisioning/ride/lib-fedora-server.sh`. Its
`complete`, `plexserver`, and `streambox` presets are consumers. Keep that
source and those presets there; move only generic behavior after its v3
equivalent has been tested on disposable server VMs.
No source file in that repository is modified by this branch.

| Existing function family | Generic RIDE outcome | Ownership decision |
| --- | --- | --- |
| `UpdateFedora`, `InstallRequired`, `InstallAutoUpdate` | Update and baseline packages | Non-runnable v3.0 decisions with bounded update, role split, and timer recovery triggers. |
| `InstallDocker`, `InstallTailscale`, `InstallGlances`, `InstallPlexServer`, `InstallPlexAutoUpdate`, `InstallSelenium` | Optional services and tools | Docker is supported on Workstation and Server; Glances package and loopback service are supported on both declared targets; Tailscale is an operable package-only candidate on Fedora 44 Server; Plex package and service are supported on Fedora 44 Server with an opt-in profile; Plex's mutable updater is replaced by signed RPM/DNF updates; Selenium bindings are an opt-in Fedora 44 Server candidate, while browser/driver and Grid lifecycle stay outside RIDE. |
| `InstallAMP` | AMP game-server manager | The unsigned CubeCoders RPM is a Fedora 44 Server opt-in candidate pinned by version and SHA-256, with RPM scriptlets suppressed. Controller setup, credentials, license activation, network exposure, and private AMP state remain operator-managed. |
| `SetNoRootLogin`, `GenerateSSHkeysRSA` | SSH policy and key material | Policy needs exact backup and restore; private keys must remain outside catalog and run state. |
| `SetHostname` | Host identity | Hostname is a private profile value; only generic behavior remains under review. |
| ExpressVPN and VPN randomizer | VPN client and scheduling | Keep provider and subscription details private; review deterministic disable and removal first. |

The current library defines a fixed private NAS address and contains interactive host
setup. The public catalog must not absorb either value or prompt. Owner-excluded
service and configuration functions stay outside the generic v3 migration queue;
their existing server consumers remain in that repository. The initial
`server-base` profile deliberately contains only the small common package baseline.

OpenCTI Community Edition is a [planned post-v3.0 generic server
operation](migrations/opencti-server.md). It has no v2 source function, is
outside the scoped migration denominator, and is not a v3.0 release gate.
Its future opt-in deployment needs an explicit container runtime and
data-preserving recovery; it is not part of `server-base`.

The [scoped outcome burndown](workstation-server-burndown.md) records selector
coverage for generic server candidates, including inactive functions. The
source-only name snapshot remains in `migration/server-inventory.json`.
The [server decision record](migrations/generic-server-decisions.md) covers
the exact v2 mutations and reopening triggers; the shared
[`python3-pip` operation](migrations/generic-server-python.md) passed a
disposable Fedora 44 Server VM lifecycle. `server-base` and that opt-in
package profile are the only accepted Server profiles from this review.

For a later ownership transfer, `network-devices` remains the authoritative
v2 source and its three presets are known consumers. Its
`operations/provisioning/ride/README.md` describes the migration-stage
location, and `INSTALL2` records a historical `~/bin` symlink publication
path; active use of that path is unverified. The source executes as the
calling administrator or prompted user and touches host, service, user,
VPN, firewall, and Python state described in the decision record. RIDE v3
uses its own catalog/profile release, run journals under
`/var/lib/ride-fedora/runs`, and declared inverse; it does not invoke the
v2 library. Before deleting or redirecting the old source, identify actual
runtime consumers and deployment identities, preserve their state, and
record a tested rollback. No consumer is assumed inactive from absence of
a local v3 journal.
