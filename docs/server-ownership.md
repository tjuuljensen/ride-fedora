# Server library boundary

The existing server source is
`network-devices/operations/provisioning/ride/lib-fedora-server.sh`. Its
`complete`, `plexserver`, and `streambox` presets are consumers. Keep that
source and those presets there; move only generic behavior after its v3
equivalent has been tested on disposable server VMs.
No source file in that repository is modified by this branch.

| Existing function family | Generic RIDE outcome | Ownership decision |
| --- | --- | --- |
| `UpdateFedora`, `InstallRequired`, `InstallAutoUpdate` | Update and baseline packages | Candidate generic server operations after package lists and timer behavior are reviewed. |
| `InstallDocker`, `InstallTailscale`, `InstallGlances`, `InstallSelenium` | Optional services and tools | Split into opt-in operations with independent source and recovery checks. |
| `SetNoRootLogin`, `GenerateSSHkeysRSA` | SSH policy and key material | Policy needs exact backup and restore; private keys must remain outside catalog and run state. |
| `SetHostname` | Host identity | Hostname is a private profile value; only generic behavior remains under review. |
| ExpressVPN and VPN randomizer | VPN client and scheduling | Keep provider and subscription details private; review deterministic disable and removal first. |

The current library defines a fixed private NAS address and contains interactive host
setup. The public catalog must not absorb either value or prompt. Owner-excluded
service and configuration functions stay outside the generic v3 migration queue;
their existing server consumers remain in that repository. The initial
`server-base` profile deliberately contains only the small common package baseline.

The [scoped outcome burndown](workstation-server-burndown.md) records selector
coverage for generic server candidates, including inactive functions. The
source-only name snapshot remains in `migration/server-inventory.json`.
