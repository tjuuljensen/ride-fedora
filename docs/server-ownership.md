# Server library boundary

The existing server source is
`network-devices/operations/provisioning/ride/lib-fedora-server.sh`. Its
`complete`, `plexserver`, and `streambox` presets are consumers. Keep them
there until equivalent v3 profiles have been tested on disposable server VMs.
No source file in that repository is modified by this branch.

| Existing function family | Generic RIDE outcome | Ownership decision |
| --- | --- | --- |
| `UpdateFedora`, `InstallRequired`, `InstallAutoUpdate` | Update and baseline packages | Candidate generic server operations after package lists and timer behavior are reviewed. |
| `InstallDocker`, `InstallTailscale`, `InstallGlances`, `InstallSelenium` | Optional services and tools | Split into opt-in operations with independent source and recovery checks. |
| `SetNoRootLogin`, `GenerateSSHkeysRSA` | SSH policy and key material | Policy needs exact backup and restore; private keys must remain outside catalog and run state. |
| `SetHostname`, `MountNASSMBfolders` | Host identity and NAS mounts | Hostname, NAS address, share names, credentials, user IDs and mount paths stay in a private overlay. Generic mount behavior can be extracted later. |
| ExpressVPN and VPN randomizer | VPN client and scheduling | Keep provider and subscription details private; review deterministic disable and removal first. |
| qBittorrent, Plex, AMP, Ferium and Minecraft | Application services | Migrate as separate opt-in profiles; service users, firewall ports, media paths and credentials remain host-owned. |

The current library defines a fixed private NAS address and contains interactive host
setup. The public catalog must not absorb either value or prompt. A migration
is complete only when the existing presets have v3 replacements, consumers
are moved, and rollback of service files, firewall rules and user creation is
documented. The initial `server-base` profile deliberately contains only the
small common package baseline.

The [complete outcome burndown](workstation-server-burndown.md) covers all 28
server functions, including the five absent from active server presets, and
records the exact selector coverage of each preset.
