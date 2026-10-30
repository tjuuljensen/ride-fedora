# Video downloader and GNOME monitoring packages

Status: **complete: one supported RPM and one operable opt-in package pair**,
2026-10-30. This active-preset batch covers `YouTubeDownloader` and
`SystemMonitor`, preserving their v2 function mappings. The first is one
Fedora RPM. The v2 SystemMonitor function installs the GNOME System Monitor
Next extension, hardware sensors, and two build development packages; it
does not enable the extension. The Fedora-built RPMs do not need those build
development packages.

## Completion criteria defined before implementation

- Use the Fedora 44 `youtube-dl` RPM for the v2 video downloader outcome.
  Check absent plan, apply, signed RPM/files, CLI startup, repeat, status,
  restore, and explicit remove in a disposable x86_64 Workstation VM.
  Do not fetch user media or claim that a third-party site works.
- Split SystemMonitor into the Fedora system-monitor-applet RPM and
  `lm_sensors` RPM; do not install build headers merely because v2 did.
  Verify both package lifecycles, shipped GNOME extension metadata and
  `sensors` CLI without running privileged hardware detection. Treat the
  combined desktop outcome as opt-in candidate after a happy path and
  focused mocked DNF failure evidence. Keep actual shell activation and
  desktop visual behavior in v3.1.
- Compare Windows contracts, update catalog, opt-in profile if the package
  pair passes, acceptance records, ledger, and generated reports. Investigate
  a failed VM run before retrying.

## Fedora 44 VM results

[`package.youtube-dl`](../acceptance/package.youtube-dl.md) passed the
Fedora-signed RPM plan/apply/repeat/status/restore/remove contract and is
**supported on Fedora 44 x86_64 Workstation**. Its CLI started, but no media
was downloaded; the user-visible operation remains the v2 package install,
not a claim that a particular site still works.

The SystemMonitor outcome is migrated to the distinct
[`package.gnome-shell-extension-system-monitor-applet`](../acceptance/package.gnome-shell-extension-system-monitor-applet.md)
and [`package.lm-sensors`](../acceptance/package.lm-sensors.md) RPMs.
Both passed their individual package lifecycle and the curated
`workstation-monitoring` profile passed plan/apply/repeat/restore in a
separate disposable overlay. The v2 build development packages are not
needed to install these Fedora-built RPMs. The pair is an **operable opt-in
candidate**; use `--allow-candidate`. Actual GNOME session activation,
visual behavior, and broader recovery are H012 in the v3.1 queue. The
profile remains separate from `default`.
