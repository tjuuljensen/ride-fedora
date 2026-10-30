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
| `MulticastDNS` | **Unsupported.** v2 comments and appends `hosts:` lines in `/etc/nsswitch.conf`; inverse re-enables every commented `#hosts` line and can discard administrator edits. | Add a line-scoped, owned resolver setting with exact original-file and DNS-order recovery on a disposable target. |
| `Wireguard` | **Unsupported.** v2 installs `wireguard-tools`, creates private/public keys under `/etc/wireguard`, and removal recursively deletes that directory, including potentially pre-existing secrets. | Separate the signed RPM from private key ownership; require seeded-key preservation and key/connection recovery before any runnable profile. |
| `OpenconnectVPN` | **Unsupported.** v2 installs build dependencies, clones a moving Git source over `git://`, and runs `make install` into `/usr` without provenance or inverse. | Use a reviewed Fedora or publisher package and test service/profile preservation; do not reuse the unpinned source build. |
| `ImportOpenVPNProfiles` | **Unsupported.** v2 searches several working and source directories for `.ovpn`, then imports connection profiles through `nmcli`; input ownership and credentials are implicit. | Define an explicit private profile source, name/UUID conflict policy, secret handling, and exact NetworkManager rollback. |
| `VPNProfiles` | **Unsupported.** The remove-only v2 function deletes every NetworkManager VPN connection, including unowned ones. | Restrict deletion to recorded RIDE-owned connection UUIDs and pass seeded unrelated-profile preservation. |
| `ExpressVPNProfiles` | **Unsupported.** The remove-only function matches names containing `expressvpn`, then deletes connections without ownership proof. | Bind exact owned UUIDs to a private ExpressVPN deployment and restore seeded user connections. |
| `ExpressVPN` | **Unsupported.** v2 scrapes a moving publisher RPM URL and may prompt for an activation code; removal leaves activation, connection profiles, and user state unaccounted for. | Pin and verify the publisher artifact, identify licensed deployment scope, keep activation private, and prove profile-safe inverse. |
| `StartExpressVPNafterBoot` | **Unsupported.** v2 appends an `@reboot` line to the current crontab without owning the rest of the file. | Use an owned service/timer tied to an accepted VPN deployment and test seeded crontab and connection recovery. |
| `ExpressVPNafterBoot` | **Unsupported.** The remove-only inverse filters a matching crontab string, which can remove an unowned job. | Reconcile as the inverse of an owned boot connection schedule. |
| `CreateExpVPNrandomizer` | **Unsupported.** v2 appends executable shell text to `/usr/sbin/expressvpn-randomizer.sh`, without source verification, idempotence, or inverse. | Define a reviewed, owned script with bounded VPN selection, failure handling, and private connection state. |
| `ScheduleRandomExpVPNChange` | **Unsupported.** v2 inserts a six-hour crontab job for that unowned script. | First accept the script and VPN deployment, then use an owned schedule with exact crontab preservation. |
| `ScheduleExpVPNChange` | **Unsupported.** The remove-only inverse deletes matching crontab lines without checking origin. | Reopen only as a scoped inverse of an owned schedule. |

## VMware and kernel modules

| Outcome | v2 behavior and v3.0 decision | Reopen when |
| --- | --- | --- |
| `VMwareWorkstation` | **Unsupported.** v2 follows a moving installer redirect, reads a host-specific serial variable, installs build prerequisites, and runs a publisher bundle with no pinned artifact or complete inverse. | Choose a current licensed publisher build, verify provenance, isolate serials, and test VM inventory plus module recovery on a disposable host. |
| `PatchVMwareModules` | **Unsupported.** v2 clones or pulls a moving third-party module tree, stops the VMware service, checks out a version branch, and builds for a kernel without a verified rollback. | Pin a licensed module source and exact kernel/VMware pair; pass boot, service, and previous-module recovery tests. |

## LUKS, disk layout, and sudo policy

| Outcome | v2 behavior and v3.0 decision | Reopen when |
| --- | --- | --- |
| `AddExtraLUKSpasswords` | **Unsupported.** v2 loops over all detected LUKS devices and prompts to add keys without a named target or key-slot journal. | Choose one explicit disposable block device and private secret source; prove header backup, slot selection, failure recovery, and non-target preservation. |
| `EncryptUnpartitionedDisks` | **Unsupported.** v2 scans disks and can erase/encrypt any disk without a partition table after a prompt; its warning explicitly acknowledges data loss. | Require explicit device allowlisting, independent backup, exact plan, destructive disposable-disk tests, and rollback/recovery procedure. |
| `ReclaimEncryptDWUnmntPrt` | **Unsupported.** v2 can reclaim unmounted partitions based on heuristic disk enumeration and alter encryption/mount state without a reliable inverse. | Require an explicit device map, backup, mount/crypttab ownership, and destructive disposable-disk recovery evidence. |
| `KeyfileMounts` | **Unsupported.** The remove-only function deletes every matching keyfile line from `/etc/crypttab` and related `/etc/fstab` lines while leaving encrypted volumes in place. | Reconcile as the inverse of individually owned mappings, preserving unrelated mounts and bootability. |
| `SSHreboot` | **Unsupported.** v2 writes a user-specific sudoers file granting passwordless reboot and removal deletes it without prior-owner checks or validation. | Add a private principal, file-ownership and `visudo` checks, scoped command semantics, and recovery from a seeded sudoers policy. |

No state-changing acceptance was run for these non-runnable decisions. The
v2 source in `lib-fedora.sh` supplies the observed mutation and inverse
facts. A later implementation must perform its own current upstream,
license, target, and recovery review before promotion.
