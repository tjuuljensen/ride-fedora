# Generic server v2 outcomes without a runnable v3.0 lifecycle

Status: **non-runnable decisions**, 2026-10-30. The pinned server source is
`network-devices/operations/provisioning/ride/lib-fedora-server.sh` at SHA-256
`e9f42f3cbc4c71dd32f2148069fff302a608057a653cccb56da4da416cd67aa0`.
It remains authoritative for its `complete`, `plexserver`, and `streambox`
presets. This review changes no code or publication path in that repository.
Unknown use of its library is unverified. `server-base` remains the accepted
small baseline; the [Python pip package](generic-server-python.md) has its
separate Server VM evidence.

## Completion criteria for this review

- Inspect each v2 function's actual mutations and missing inverse. Keep
  host names, VPN activation, SSH keys, users, and credentials outside the
  public catalog. A one-time command or broad bundle is not a successful
  declarative operation merely because its source exists.
- Map shared Fedora package behavior only when the declared Server target
  passes. Require owned configuration, detection, seeded-state preservation,
  and recovery for services, security settings, VPN state, and external
  repositories before any runnable operation. Retain a specific review
  trigger for a later, bounded batch.
- Do not retire or transfer the `network-devices` library, presets, or
  deployment links. Before a cross-repository move, identify consumers,
  publication path, runtime principal, persistent state, and rollback.

| Source outcome | v2 behavior and v3.0 decision | Reopen when |
| --- | --- | --- |
| `UpdateFedora` | **Unsupported.** Runs a broad `dnf update -y` without a planned transaction, repeat-state contract, or rollback. | Add a bounded update action with package inventory, failure/reboot reporting, and disposable Server recovery evidence. |
| `Required` | **Unsupported.** Installs 11 mixed role RPMs, including VM guest tools, firewall, Samba clients, cron, and editors. A single generic desired state would imply services and dependencies that `server-base` does not own. | Split packages by role, verify the requested Server use case, and test each exact profile and inverse. |
| `AutoUpdate` | **Unsupported.** Installs `dnf-automatic`, enables its install timer, and edits `/etc/dnf/automatic.conf`; the attempted timer edit omits `-i` and does not persist. No original config or timer state is journaled. | Add owned DNF5 timer/config state, update scheduling policy, dry-run observation, and seeded configuration restore. |
| `Hostname` | **Unsupported.** Interactive prompt sets a static host identity with no declared profile value or prior-name restore. | Define a validated private input and exact hostname journal/restore on a disposable Server. |
| `Docker` | **Unsupported.** Adds an external repo, packages, a user to the `docker` group, and an enabled daemon without preserving existing repository, group, image, or volume state. | Review publisher key/repository, named runtime user, owned group/service state, seeded-volume preservation, and rollback. |
| `Tailscale` | **Unsupported.** Pipes a remote installer into `sh`; no pinned artifact, current-state check, credential boundary, or inverse. | Use a verified publisher repository/package and explicitly preserve node identity, tailnet state, and service recovery. |
| `Glances` | **Unsupported.** Rebuilds `/opt/glances` Python environment from moving packages, overwrites a systemd unit, opens firewall port 61208, and starts a web service; no inverse is defined. | Pin the environment, own the unit and firewall rule, verify the service and seeded-file recovery, and use an opt-in Server profile. |
| `Selenium` | **Unsupported.** Installs into the global pip environment with no version, isolation, or inverse; the supported `python3-pip` RPM does not fulfill this outcome. | Define a requested browser/driver target and pinned isolated environment with exact removal and Server VM evidence. |
| `NoRootLogin` | **Unsupported.** An in-place substitution may alter administrator SSH policy without backup, syntax check, reload result, or inverse. | Use a scoped owned drop-in, `sshd -t`, session-preserving VM checks, and exact prior-state recovery. |
| `GenerateSSHkeysRSA` | **Unsupported.** Generates private RSA keys in an interactive user's home; existing-key behavior is prompt driven and the code creates `.ssh` with mode 755. | Move secret handling to an explicit private owner, preserve existing keys, enforce secure permissions, and prove no key material enters logs or run state. |
| `ExpressVPN` | **Unsupported.** Scrapes a moving publisher RPM URL, installs it, then prompts for activation; account and connection state have no inverse. | Pin and verify a licensed artifact, keep activation private, and prove service/profile/credential recovery on a disposable Server. |
| `CreateVPNrandomizer` | **Unsupported.** Appends unverified shell text to `/usr/sbin`, assumes ExpressVPN activation, and has an unbounded array selection with no inverse. | First accept the VPN client; then own a reviewed deterministic script, selection failure behavior, and previous-file restore. |
| `VPNRandomizerPersistent` | **Unsupported.** Rewrites current crontab with reboot and six-hour VPN jobs without an owned schedule boundary or inverse. | Use an owned timer tied to an accepted VPN client and preserve unrelated crontab, routing, and connection state. |

These decisions describe the v2 source and v3.0 safety boundary, not absence
of Fedora packages or a claim that these services have no legitimate use.
No state-changing VM session is appropriate for a non-runnable disposition.
A future implementation batch must review current upstream, license,
source verification, and exact-target recovery before promotion.
