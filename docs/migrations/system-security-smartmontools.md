# SmartMonTools storage monitoring decision

Status: **kept by owner for v3.0; operable opt-in candidate passed Fedora 44 Workstation x86_64 acceptance**, 2026-11-02.
The v2 pair only installs and removes the signed Fedora `smartmontools` RPM.
Fedora 44 publishes `smartmontools` 7.5 and the RPM includes `smartd.service`.
The upstream project describes `smartctl` and `smartd` as utilities for SMART
control and monitoring and publishes its GPL-2.0 license. See the
[Fedora 44 package record](https://packages.fedoraproject.org/pkgs/smartmontools/smartmontools/fedora-44.html)
and [upstream project and license](https://github.com/smartmontools/smartmontools).

The generic RPM pilot on 2026-10-30 found that package installation enabled
`smartd.service` while leaving it inactive. It was disabled before installation.
The previous experiment stopped before restore and its transcript is retained
in the acceptance run journal. Do not reuse generic DNF lifecycle evidence.

The v3 implementation is `package.smartmontools` in the opt-in
`fedora-workstation-smartmontools` profile. Its Fedora-specific handler installs
the signed RPM, then disables and stops `smartd.service`. It refuses package
removal if the service is enabled or active, so a later administrator decision
to turn monitoring on is not silently undone. The operation does not edit
`smartd.conf`, select devices, run SMART polling, or read device data.

The full lifecycle passed on 2026-11-02, including plan, candidate gating,
apply, RPM signature and files, stopped/disabled service, repeat, status, restore,
explicit remove, and exact package baseline recovery. Transcript and image hashes
are recorded in [the acceptance record](../acceptance/package.smartmontools.md).
The package remains opt-in and candidate-gated. Hardware monitoring
configuration and device selection remain in the named v3.1 hardening queue.
