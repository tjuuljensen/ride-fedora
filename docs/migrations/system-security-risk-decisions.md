# Network, credential, virtualization, and storage safety decisions

Status: **non-runnable v3.0 decisions**, 2026-10-30. This review covers the
isolated high-risk system-security batches whose v2 code cannot satisfy the
declared v3.0 safety and inverse gate. It does not declare their technologies
unsupported by Fedora. The package-only NetworkManager VPN and security
application batches remain separate for exact-target review.

## Completion criteria for these decisions

- Inspect each v2 function's source, mutation, current-state detection, and
  inverse. Never run a v2 function as fallback. Do not expose a runnable
  candidate for VPN credentials, disk encryption, sudo policy, network name
  resolution, or a moving kernel-module source without the deeper gate.
- Keep host identities, VPN profiles, activation codes, encryption keys, and
  disk topology out of this public repository. Require an explicit owner and
  seeded-state preservation check before moving any behavior to a private
  target or adding a public parameterized handler.
- Record a concrete reopening trigger and risk-specific disposable-VM
  recovery test for each outcome. A failure must be investigated before retry;
  a green package or syntax check alone is not acceptance.

## Name resolution and VPN state

| Outcome | v2 behavior and v3.0 decision | Reopen when |
| --- | --- | --- |
| `MulticastDNS` | **Kept by owner; operable opt-in v3.0 candidate.** Fedora 44 manages generated `nsswitch.conf` through authselect. `setting.multicast-dns` uses the selected profile's `with-mdns4` feature, records the exact profile selection, and refuses restore after an external authselect change. The Fedora 44 Workstation lifecycle, resolver probe, conflict check, and exact restore passed. It does not edit generated resolver files directly. | Keep the candidate opt-in. H100 covers alternate profiles, generated-file ownership, and future Fedora/authselect behavior before adding targets. |
| `Wireguard` | **Migrated for local tools and key generation.** The signed Fedora tools RPM and owned key pair passed the [Workstation acceptance](../acceptance/system-security-wireguard.md). The v3 inverse removes only unchanged RIDE-owned keys and marker. | Keep the opt-in profile; review interfaces, peers, routes, and key rotation under H032 before extending behavior. |
| `OpenconnectVPN` | **Migrated, package-only.** The signed Fedora OpenConnect CLI, `vpnc-script`, and GNOME editor passed the [Workstation lifecycle](../acceptance/system-security-openconnect-packages.md). The v2 moving source build remains excluded. | Keep the opt-in package profile; review real connection, routing, DNS, credential, and GNOME dialog behavior under H031 before extending scope. |
| `ImportOpenVPNProfiles` | **Unsupported.** v2 searches several working and source directories for `.ovpn`, then imports connection profiles through `nmcli`; input ownership and credentials are implicit. | Define an explicit private profile source, name/UUID conflict policy, secret handling, and exact NetworkManager rollback. |
| `VPNProfiles` | **Kept by owner for v3.0.** The remove-only v2 function deletes every NetworkManager VPN connection. Replace it with an opt-in operation that accepts explicit UUIDs, refuses active or unsupported profiles, snapshots the exact keyfiles privately, and restores only the selected profiles. | Before adding discovery by name/type, profile import, activation, or routing changes, review credential storage and network recovery. See [VPN profile batch](system-security-20-vpn-profiles.md). |
| `ExpressVPNProfiles` | **Kept and mapped to the supported UUID-scoped v3 operation.** The v2 remove-only function matches names containing `expressvpn`, then deletes connections without ownership proof. In v3, the operator supplies only the exact ExpressVPN profile UUIDs to remove; unrelated and non-selected profiles are preserved and selected keyfiles can be restored exactly. | Reopen only if the vendor profile format, credential storage, or the supported keyfile backend changes; see [owned VPN profile batch](system-security-20-vpn-profiles.md). |
| `ExpressVPN` | **Kept by owner; opt-in v3 wrapper is operable on Fedora 44 Workstation and Server.** The wrapper verifies the local publisher-signed installer, avoids activation and connection, restores seeded NetworkManager, route-table, root config, and unrelated policy-rule state, and removes app/service residue. Shared RPM dependencies remain installed. | Retain candidate gating; use H002 for broader failure, upgrade, and publisher recovery checks. See [ExpressVPN path review](system-security-10-expressvpn.md) and [acceptance evidence](../acceptance/package.expressvpn.md). |
| `StartExpressVPNafterBoot` | **Kept; documented replacement.** ExpressVPN's Linux GUI can reconnect to the last location on startup and supports publisher-managed auto-connect rules. See the [startup auto-connect procedure](../../reference/expressvpn-autoconnect.md). | Keep this preference user-managed. RIDE must not create a systemd job or remove an unowned crontab line. Reopen if the publisher removes the feature or the user requests RIDE-managed state. |
| `ExpressVPNafterBoot` | **Kept; documented replacement.** The GUI's auto-connect preference replaces the v2 boot-connect behavior. The v2 removal helper can delete an unowned matching crontab line, so RIDE does not automate that cleanup. See the [startup auto-connect procedure](../../reference/expressvpn-autoconnect.md). | Review old crontab lines manually with the owner; preserve unrelated entries. Reopen if a supported, observable v14 setting API or a safe ownership marker becomes available. |
| `CreateExpVPNrandomizer` | **Replaced by a user-scoped reference utility.** `tools/expressvpn-rotate.sh` reads an explicit allowlist, defaults to preview, and calls the current `expressvpnctl connect LOCATION` interface without disconnecting first. It is not installed or scheduled by RIDE. | See [rotation tool guide](../../reference/expressvpn-rotation.md). Keep unattended scheduling unresolved until v14 connection recovery is verified. |
| `ScheduleRandomExpVPNChange` | **Unsupported.** v2 inserts a six-hour crontab job for that unowned script. | First accept the script and VPN deployment, then use an owned schedule with exact crontab preservation. |
| `ScheduleExpVPNChange` | **Kept by owner, subject to behavior review and rewrite.** The remove-only inverse deletes matching crontab lines without checking origin. The v2 randomizer uses a legacy ExpressVPN CLI and disconnect-first script. | If six-hour rotation remains desired, use a named allowed-location list, the current `expressvpnctl` interface, and an owned systemd timer after proving connection-switch and network recovery. See [VPN automation paths](system-security-vpn-automation.md). |

## VMware and kernel modules

| Outcome | v2 behavior and v3.0 decision | Reopen when |
| --- | --- | --- |
| `VMwareWorkstation` | **Full capability retired by owner on 2026-10-30.** The v2 mapping is retained as evidence; no v3 implementation is required. | Reopen only on explicit owner request. |
| `PatchVMwareModules` | **Unsupported.** v2 clones or pulls a moving third-party module tree, stops the VMware service, checks out a version branch, and builds for a kernel without a verified rollback. | Pin a licensed module source and exact kernel/VMware pair; pass boot, service, and previous-module recovery tests. |

## LUKS, disk layout, and sudo policy

| Outcome | v2 behavior and v3.0 decision | Reopen when |
| --- | --- | --- |
| `AddExtraLUKSpasswords` | **Unsupported.** v2 loops over all detected LUKS devices and prompts to add keys without a named target or key-slot journal. | Choose one explicit disposable block device and private secret source; prove header backup, slot selection, failure recovery, and non-target preservation. |
| `EncryptUnpartitionedDisks` | **Unsupported.** v2 scans disks and can erase/encrypt any disk without a partition table after a prompt; its warning explicitly acknowledges data loss. | Require explicit device allowlisting, independent backup, exact plan, destructive disposable-disk tests, and rollback/recovery procedure. |
| `ReclaimEncryptDWUnmntPrt` | **Unsupported.** v2 can reclaim unmounted partitions based on heuristic disk enumeration and alter encryption/mount state without a reliable inverse. | Require an explicit device map, backup, mount/crypttab ownership, and destructive disposable-disk recovery evidence. |
| `KeyfileMounts` | **Kept and operable as a v3.0 opt-in candidate.** `setting.keyfile-mounts` removes or restores one explicitly selected mapper, never creates keys or volumes, and passed Fedora 44 Workstation encrypted-data and reboot recovery. It remains outside base profiles. | Reopen if the supported keyfile/mount contract, crypttab/fstab semantics, or exact recovery changes; see [batch 25](system-security-25-keyfile-mounts.md) and [acceptance](../acceptance/setting.keyfile-mounts.md). |
| `SSHreboot` | **Migrated as an opt-in Fedora 44 Workstation candidate.** `setting.ssh-reboot` requires a private per-invocation Linux principal and grants only passwordless `/usr/bin/systemctl reboot`; the owned sudoers file is validated and exactly restored. | Before promotion, invoke reboot over non-TTY SSH in a disposable VM and verify reconnect and unrelated-policy preservation (H112). See [batch design](system-security-18-ssh-reboot.md) and [acceptance evidence](../acceptance/setting.ssh-reboot.md). |

The owner kept `VPNProfiles`, `ExpressVPNProfiles`, `ExpressVPNafterBoot`,
`ScheduleExpVPNChange`, and `KeyfileMounts` for migration. The generic
UUID-scoped `setting.networkmanager-vpn-profiles` operation now covers both
profile-removal outcomes; its existing Fedora 44 Workstation acceptance proves
selected-profile recovery and preservation of unrelated connections. The two
scheduling outcomes still need owned schedule implementations. Keyfile mounts
have a focused [v3.0 implementation and acceptance record](system-security-25-keyfile-mounts.md)
and still need isolated disposable-disk and boot recovery evidence. Keeping
these outcomes does not approve the broad v2 deletion functions.

No state-changing acceptance was run for the remaining non-runnable decisions.
The v2 source in `lib-fedora.sh` supplies the observed mutation and inverse
facts. MulticastDNS uses Fedora's authselect-managed feature path and has a
focused Fedora 44 Workstation acceptance pilot. Later implementations must
perform their own current upstream, license, target, and recovery review before
promotion.
