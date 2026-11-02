# Fedora DNF5 automatic-update setting acceptance

Status: **PASS on Fedora 44 Server x86_64; opt-in candidate**.

Acceptance run: 2026-11-02 on pinned target `fedora-44-server-x86_64`, using
TCG. Image SHA-256:
`efb75956d6dbde0801059fdac4a8a1451f06ecc843344ecdb71bb3e8d247af90`.
Transcript:
`.acceptance-runs/generic-server-03-autoupdate-acceptance-final/transcript.jsonl`.
Transcript SHA-256:
`de1c8299baffcd9cdb8e0a9c9f49e21cac6fc8080de1fbe4dbbff2830f0d861a`.

`setting.dnf5-automatic` is an opt-in Fedora 44 Server x86_64 candidate. It
uses a RIDE-owned `dnf5-automatic.service.d` drop-in with the documented
`--installupdates` argument, and enables the vendor `dnf5-automatic.timer`.
It does not edit `/etc/dnf/automatic.conf`, replace the vendor unit, or alter
Cockpit's PackageKit update page.

The handler refuses an enabled or active timer without RIDE ownership, any
pre-existing service override, invalid package/service state, a modified
RIDE-owned drop-in, or a timer state changed outside RIDE. Restore removes
only the exact owned override and returns the timer to its disabled/inactive
baseline. The operation depends on `package.dnf5-plugin-automatic`.

Acceptance verified plan, candidate gating, apply/repeat/status, RPM unit-file
presence, the effective `ExecStart=/usr/bin/dnf5 automatic --timer
--installupdates`, and enabled/active timer state. Restore removed the owned
drop-in, returned RIDE status to the disabled baseline, and removed the package;
systemd reports the timer as `not-found`/inactive after its unit is removed.
The run deliberately did not wait for the daily timer or execute a system-wide
update. H101 tracks scheduled-run, overlap, and reboot/failure behavior for
v3.1.

Source: [DNF5 automatic command and timer](https://dnf5.readthedocs.io/en/stable/dnf5_plugins/automatic.8.html).
