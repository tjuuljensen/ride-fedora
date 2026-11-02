# Generic Server 03: automatic package updates

Status: **Operable opt-in candidates on Fedora 44 Server x86_64**, 2026-11-02.
The owner kept this v2 capability for v3.0 and asked that it be reconciled with
Cockpit. The disposable VM lifecycle passed; automatic execution of the
scheduled package update remains in the v3.1 hardening queue.

## Current Fedora path

- Fedora 44 provides the signed `dnf5-plugin-automatic` package. It ships the
  DNF5 automatic command and `dnf5-automatic.service` / `.timer` units.
- DNF5 documents the timer as the scheduler and supports an explicit
  `dnf5 automatic --installupdates` invocation. This gives RIDE a supported
  systemd service override path instead of editing the package-owned
  `/etc/dnf/automatic.conf`.
- Cockpit's Software Updates page uses PackageKit over D-Bus for interactive
  update discovery and application. It is not the DNF5 timer configuration
  surface. The two paths remain separate owners, although an interactive
  transaction and a scheduled one may overlap in time.
- On the pinned Fedora 44 Server image, `cockpit-packagekit` was already
  installed. The DNF5 automatic RPM was absent. Installing it upgraded eight
  existing DNF/libdnf packages and installed the plugin plus one dependency;
  those package upgrades are not reversed by removing the plugin.

Sources: [Fedora DNF5 package](https://packages.fedoraproject.org/pkgs/dnf5/dnf5/),
[Fedora 44 automatic plugin package files](https://packages.fedoraproject.org/pkgs/dnf5/dnf5-plugin-automatic/fedora-44.html),
[DNF5 automatic command](https://dnf5.readthedocs.io/en/stable/dnf5_plugins/automatic.8.html),
[Cockpit Package Updates](https://docs.cockpit-project.org/cockpit-guide/360/guide/feature-packagekit.html),
[Cockpit Software Updates FAQ](https://cockpit-project.org/faq).

## Completion checks defined before implementation

- Add the signed Fedora RPM as a distinct package operation and make it a
  dependency of an opt-in Server setting.
- Use a RIDE-owned `dnf5-automatic.service.d` drop-in to request automatic
  installation through the documented command flag. Never overwrite the RPM
  configuration file or replace the vendor unit.
- Record the prior timer enabled/active state, refuse an already managed timer
  or unowned service override, and restore only the exact RIDE-owned drop-in
  and prior timer state.
- On disposable Fedora 44 Server, test package provenance, install effects,
  plan/apply/repeat/status, timer enablement, the effective service command,
  exact drop-in/timer restore, and package removal while recording DNF
  upgrades that remain. Do not wait for the daily timer to run as part of the
  lifecycle test.
- Confirm Cockpit's PackageKit path remains installed and unchanged; do not
  add a Cockpit timer or alter its interactive update page.

The timer and exact recovery evidence passed on the declared Fedora 44 Server
target, so both operations count as an opt-in candidate capability. The test
did not wait for the daily timer or permit it to update the VM. Broader timer
execution, Cockpit transaction overlap, reboot recovery, and injected failure
behavior are tracked by H101.

Acceptance transcript: `.acceptance-runs/generic-server-03-autoupdate-acceptance-final/transcript.jsonl`
(SHA-256 `de1c8299baffcd9cdb8e0a9c9f49e21cac6fc8080de1fbe4dbbff2830f0d861a`);
source bundle SHA-256 `8e93f719c0fcc10f1e83896c3383b8fae8c7956546fed97104e83888deba35a`.
