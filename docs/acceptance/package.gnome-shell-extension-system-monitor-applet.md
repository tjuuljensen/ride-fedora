# `package.gnome-shell-extension-system-monitor-applet` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 x86_64 Workstation,
2026-10-30. Fedora's signed
[`gnome-shell-extension-system-monitor-applet`](https://packages.fedoraproject.org/pkgs/gnome-shell-extension-system-monitor-applet/gnome-shell-extension-system-monitor-applet/)
RPM supplies the System Monitor Next extension. The related
`package.lm-sensors` RPM supplies hardware sensor commands. Neither package
enables the extension for a user or runs privileged hardware detection.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
package lifecycle overlay
`20261030T124400Z-test-publisher-native-video-and-monitor-packages-5fb9ff3a`;
opt-in profile overlay
`20261030T124548Z-test-workstation-monitoring-opt-in-profile-32128808`;
candidate catalog SHA-256
`be7a3c79de4260036bc83459e70fe519733c9bcfc494e4bc413cf17c9370fd22`.
The retained transcripts and `.acceptance-runs/publisher-apps-05-native.xml`
plus `.acceptance-runs/publisher-apps-05-profile.xml` each record one passing
test. The package was absent at baseline. It passed absent plan,
candidate-gated apply, signature/files and shipped extension metadata,
status, repeat, restore, and explicit install/remove. The curated
`workstation-monitoring` profile installed and restored both candidate
packages together. Pre-existing RPM identities were preserved. The
unchanged DNF handler's mocked failure evidence is in
[base package acceptance](package.exfatprogs.md).

This is a package and profile happy path, not a claim that the applet was
enabled or visually checked in a GNOME session. That desktop check and
broader recovery are [v3.1 item H012](../migrations/progress.md). See the
[batch review](../migrations/publisher-apps-05.md).
