# Host identity, DNF tuning, update, and Docker decisions

Status: **Hostname is supported on Fedora 44 Workstation and Server; FastDNF is an opt-in candidate; UpdateFedora is implemented pending target acceptance; Docker Engine is supported as an opt-in explicit operation on Fedora 44 Workstation and Server.**

## Completion criteria defined for this review

- Identify the exact v2 mutation, current Fedora 44 mechanism, declared
  desired state, and any inverse before allowing a catalog operation.
- Preserve administrator-owned files and Docker data. For UpdateFedora, require a refreshed update check, a transaction preview that refuses package removals and downgrades, no automatic reboot, a persisted DNF5 transaction inventory and reboot assessment, and an explicit non-restorable result. Verify the full path on disposable Fedora 44 Workstation and Server VMs.
- Compare catalog, profile, and run-state contracts with Windows; document a
  specific reopening trigger rather than adding release-blocking optional
  coverage.

| Outcome | Decision and reason | Reopen when |
| --- | --- | --- |
| `Hostname` | **Kept by owner.** v3 operation `setting.hostname` accepts a validated static hostname as a private `--value`, records the prior static name, and restores it exactly. The value is not stored in a public profile. | Revisit if systemd hostname semantics change or if testing finds prior static hostnames that cannot be restored exactly. |
| `FastDNF` | **Kept by owner for a DNF5 replacement.** v2 edits `/etc/dnf/dnf.conf` in place for `fastestmirror=true` and 15 parallel downloads; its inverse deletes matching lines rather than restoring prior administrator values. [DNF5's current reference](https://dnf5.readthedocs.io/en/stable/dnf5.conf.5.html) still documents a default of three parallel downloads, so defaults are not an equivalent replacement. | Use the DNF5 user configuration drop-in `/etc/dnf/libdnf5.conf.d/99-ride-fastdnf.conf` with `fastestmirror=True` and `max_parallel_downloads=15`. Before apply, detect values in `/etc/dnf/dnf.conf` and later-loaded configuration that would override the RIDE file; refuse conflicts rather than editing administrator files. Verify the effective values with DNF5 configuration output, repeat apply, then remove only the exact RIDE-owned file. Test Fedora 44 conflict, precedence, and restore behavior in a disposable VM. |
| `UpdateFedora` | **Migrated as explicit operation `system.update-all-packages`.** Uses DNF5 whole-system upgrade only through `ride.sh update`; it previews first, refuses removals and downgrades, never reboots automatically, and journals the transaction inventory and reboot assessment. It is not part of profiles and cannot be restored. | Revisit if Fedora changes DNF5 transaction or reboot-report formats, or if acceptance finds an update that bypasses the preview checks. |
| `Docker` | **Kept by owner; supported explicit operation `system.docker-engine`.** v2 installs Docker CE, CLI, and containerd from Docker's repository and starts (but does not enable) the daemon. Workstation and Server seeded image/volume recovery passed. | Reopen if Docker drops Fedora 44 support, changes its signing-key fingerprint, or remove/reinstall alters pre-existing image or volume data. |

## Docker v3.0 migration path

The v2 outcome maps to the publisher's Docker Engine (`docker-ce`,
`docker-ce-cli`, and `containerd.io`) plus an explicit `docker.service` state.
Keep this as an opt-in, source-owned deployment: Docker's current Fedora
instructions list Fedora 44, install from the Docker RPM repository, identify
the expected signing-key fingerprint as
`060A61C51B558A7F742B77AAC52FEB6B621E9F35`, and do not add users to the
`docker` group. The Fedora `moby-engine`/`docker-cli` packages are a viable
native-RPM alternative for a separately named deployment; they conflict as an
engine choice and should not be mixed into the Docker CE profile.

The v3 operation owns only its exact repository file, locally staged
publisher key, the three v2 packages, and the service state it changes. DNF
weak dependencies are disabled, leaving Compose, Buildx, and rootless extras
as separate optional outcomes. The daemon starts on apply but is not enabled,
matching v2; an owned installed engine is observed as `stopped` after reboot,
and applying `configured` starts it again. Before
install, reject an existing unowned Docker repository or key file, a
conflicting Fedora Moby engine, or an existing Docker service unit. Before
remove, refuse running containers and preserve `/var/lib/docker` and
`/var/lib/containerd`; never delete images, volumes, container metadata, or
administrator repository content. The journal identifies the exact package
set, repository, and signing-key fingerprint. Fedora 44 DNF5 verifies packages
from the repository's local key file without adding a persistent `gpg-pubkey`
RPM entry; removing this RIDE-owned file therefore does not alter shared RPM
database trust.
Add Buildx and Compose as separate optional operations because current Docker
instructions recommend those plugins but v2 did not install them.

Completion checks: mocked conflict and exact-state tests; disposable Fedora 44
Workstation and Server tests passed after seeding an image and named volume,
exercising apply/repeat/status and removal/reinstall, then confirming seeded
data, owned repository state, and RPM key-database trust boundary. Refuse
removal while the daemon is stopped so RIDE can inspect running containers;
refuse it when any container is running. If either edition fails seeded
recovery, keep that edition outside the runnable target matrix and investigate
the evidence before retrying. Primary references:
[Docker Engine on Fedora](https://docs.docker.com/engine/install/fedora/),
[Fedora 44 Moby Engine](https://packages.fedoraproject.org/pkgs/moby-engine/moby-engine/fedora-44.html).

The DNF5 reference confirms `max_parallel_downloads` remains supported (maximum 20, default 3) and `fastestmirror` remains supported. Its documented configuration order loads user drop-ins before `/etc/dnf/dnf.conf`, so the planned handler must detect main-file overrides and verify effective values before reporting configured. See [DNF5 configuration reference](https://dnf5.readthedocs.io/en/stable/dnf5.conf.5.html).

The DNF5 implementation is now available as candidate `setting.dnf5-fast-tuning` in the opt-in `fedora-fast-dnf` profile. Mocked lifecycle tests and Fedora 44 Workstation acceptance cover repeat, refusal, effective values, and exact removal.

Static hostname management is available as supported operation `setting.hostname` on Fedora 44 Workstation and Server; acceptance covers private input, status, repeat, and exact prior-name restore. Supply the host identity with `--value` in a private invocation; do not put it in tracked profiles. The operation changes only the static hostname and journals the prior static name. It refuses an unset or invalid prior static name because exact restore cannot otherwise be guaranteed. The private value must stay out of tracked profiles. The Workstation and Server VM records are in [hostname acceptance](../acceptance/setting.hostname.md).

## UpdateFedora v3.0 completion checks

- `plan` observes current versus available whole-system updates from DNF5.
- Before mutation, refresh metadata and preview the transaction; refuse any
  removal or downgrade and print the proposed transaction for inspection.
- Apply with DNF5 without rebooting automatically; verify that no updates remain.
- Capture the DNF5 transaction ID, status, and changed package NEVRAs in the
  local run journal. Record reboot-required state, or explicitly report that
  the DNF5 reboot checker is unavailable.
- Mark the operation non-restorable in the catalog and make `restore` refuse it.
- Test lifecycle, preview refusal, history parsing, reboot assessment parsing,
  and failure reporting with mocked tests, then run the full update on disposable Fedora 44 Workstation and Server targets.

The operation uses `dnf5 check-upgrade --json` for current state and the
DNF5 history JSON interfaces for transaction status and changed NEVRAs. A
successful DNF transaction can still report reboot assessment unavailable if
the optional `needs-restarting` command is absent or returns an unrecognized
result; that limitation is explicit in the journal. See the [DNF5 check-upgrade
reference](https://dnf5.readthedocs.io/en/stable/commands/check-upgrade.8.html),
[history reference](https://dnf5.readthedocs.io/en/stable/commands/history.8.html),
and [needs-restarting reference](https://dnf5.readthedocs.io/en/latest/dnf5_plugins/needs_restarting.8.html).

The operation is invoked explicitly and is never included in a profile.
Implementation and acceptance details are recorded in [system update
acceptance](../acceptance/system.update-all-packages.md). Docker's v3.0
implementation follows the owned publisher-source and data-recovery path above.

SmartMonTools is kept in v3.0 as the opt-in `package.smartmontools` RPM path.
The dedicated handler disables and stops Fedora's `smartd.service` after the
RPM's installation side effect and refuses removal if that service is later
running or enabled. It never chooses devices or starts monitoring; see
[SmartMonTools migration evidence](system-security-smartmontools.md) and the
[acceptance contract](../acceptance/package.smartmontools.md).
