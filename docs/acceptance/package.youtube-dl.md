# `package.youtube-dl` acceptance

Status: **PASS; supported Fedora RPM** on Fedora 44 x86_64 Workstation,
2026-10-30. This retains the v2 `YouTubeDownloader` package identity through
Fedora's signed [`youtube-dl`](https://packages.fedoraproject.org/pkgs/youtube-dl/youtube-dl/)
RPM (Unlicense). The VM observed `youtube-dl --version` as `2025.04.07`.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T124400Z-test-publisher-native-video-and-monitor-packages-5fb9ff3a`;
candidate catalog SHA-256
`be7a3c79de4260036bc83459e70fe519733c9bcfc494e4bc413cf17c9370fd22`.
The retained transcript and `.acceptance-runs/publisher-apps-05-native.xml`
record one passing shared test. The RPM was absent at baseline. It passed
absent plan, candidate-gated apply, RPM signature and file verification,
CLI startup, installed status, unchanged repeat, restore, and explicit
install/remove. The inverse removed the named RPM and preserved pre-existing
RPM identities; any retained dependencies were introduced by this test.
The final supported status removes the temporary candidate gate with the
same handler and target. Mocked DNF failure evidence is reused from
[base package acceptance](package.exfatprogs.md).

The test did not fetch user media or prove a particular online video site.
See the [batch review](../migrations/publisher-apps-05.md).
