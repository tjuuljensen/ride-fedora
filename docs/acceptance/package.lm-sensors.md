# `package.lm-sensors` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 x86_64 Workstation,
2026-10-30. Fedora's signed
[`lm_sensors`](https://packages.fedoraproject.org/pkgs/lm_sensors/lm_sensors/)
RPM supplies `sensors` 3.6.0 for the v2 SystemMonitor package intent. It is
paired with `package.gnome-shell-extension-system-monitor-applet` in the
curated `workstation-monitoring` profile. RIDE does not execute
`sensors-detect`, enable services, or change hardware configuration.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
package lifecycle overlay
`20261030T124400Z-test-publisher-native-video-and-monitor-packages-5fb9ff3a`;
profile overlay
`20261030T124548Z-test-workstation-monitoring-opt-in-profile-32128808`;
candidate catalog SHA-256
`be7a3c79de4260036bc83459e70fe519733c9bcfc494e4bc413cf17c9370fd22`.
Both retained transcripts show passing focused tests. The RPM was absent
at baseline. It passed absent plan, candidate-gated apply, signed RPM and
file verification, CLI startup, status, repeat, restore, and explicit
install/remove. The profile applied and restored both candidate packages.
Pre-existing RPM identities were preserved. The unchanged DNF handler's
mocked failure evidence is in [base package acceptance](package.exfatprogs.md).

Hardware sensor availability varies by machine. Actual GNOME applet
visibility and broader recovery are [v3.1 item H012](../migrations/progress.md).
See the [batch review](../migrations/publisher-apps-05.md).
