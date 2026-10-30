# Generic Server 15: qBittorrent headless package

Status: **source-ready candidate; Server VM acceptance pending**, 2026-10-30.
This batch migrates only `InstallqBittorrentServer` from the active
`network-devices/operations/provisioning/ride/lib-fedora-server.sh`. That
function installs `qbittorrent-nox` through DNF. The adjacent v2 functions
create a service user, firewall rule, systemd unit, and SSH keys; they remain
owned by `network-devices` and are not implied by a package install.
`streambox` and `complete` select the function, while `plexserver` comments it
out. Actual deployments and runtime users are unverified. No source or
consumer is removed from `network-devices` in this batch.

## Completion checks defined before implementation

- Declare a stable, system-scoped `package.qbittorrent-nox` operation for the
  signed Fedora 44 x86_64 Server RPM. Keep it out of `server-base`. The
  [Fedora package record](https://packages.fedoraproject.org/pkgs/qbittorrent/qbittorrent-nox/)
  identifies the headless subpackage and GPL-2.0-or-later license.
- Reuse the unchanged Fedora DNF handler's mocked failure and run-journal
  evidence. In one disposable pinned Server VM, check absent plan, apply,
  repeat, status, RPM signature and files, the executable path, restore, and
  explicit remove. Compare the full RPM inventory before and after recovery;
  investigate any retained dependency before retrying.
- Verify that package apply and restore do not create or delete a service
  user, custom systemd unit, firewall rule, SSH key, download, or qBittorrent
  profile. The Fedora RPM itself [ships a vendor
  `qbittorrent-nox@.service` template](https://packages.fedoraproject.org/pkgs/qbittorrent/qbittorrent-nox/fedora-44.html);
  verify no instance is enabled or started by RIDE. Do not start a
  network-facing service to verify the package. A future
  service operation needs its own ownership, private value, and recovery gate.
- Only after the exact Server target passes, add an opt-in profile, record an
  operation acceptance file, and promote the catalog row to `supported`.
  Reconcile Windows catalog/profile/run-state semantics for this batch.

## Current boundary

The current session has the pinned Server image at
`.acceptance-runs/server-image/server.qcow2`, matching the digest in
`tests/acceptance/targets.json`, but no `/dev/kvm`. The acceptance harness
requires KVM, so no VM result or supported status is claimed here. A focused
acceptance test may be prepared now and run when a KVM-capable host is
available. The package-only catalog candidate is not selected by a profile.

On a KVM-capable host, run the focused test from the repository root as a
regular user with access to `/dev/kvm`. It changes only a disposable overlay,
retains its transcript and image for review, and stops the VM on exit. The
verified base image remains unchanged. If the test fails, inspect the retained
transcript and overlay before retrying; deleting an overlay is the recovery
for this disposable test, not a recovery action on a real server.

```bash
python3 -m venv /tmp/ride-acceptance-venv
/tmp/ride-acceptance-venv/bin/python -m pip install -r tests/acceptance/requirements.txt
/tmp/ride-acceptance-venv/bin/python -m pytest tests/acceptance/test_server_qbittorrent.py -v \
  -p no:cacheprovider --rootdir=. \
  --vm-target fedora-44-server-x86_64 \
  --vm-image "$(pwd)/.acceptance-runs/server-image/server.qcow2" \
  --vm-output "$(pwd)/.acceptance-runs/generic-server-15" \
  --junitxml="$(pwd)/.acceptance-runs/generic-server-15.xml"
```
