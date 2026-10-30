# `package.easyeffects` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 x86_64 Workstation,
2026-10-30. Fedora's signed
[`easyeffects`](https://packages.fedoraproject.org/pkgs/easyeffects/easyeffects/)
RPM supplies a PipeWire audio effects and equalizer application under
GPL-3.0-or-later. It replaces the intended equalizer outcome of v2
`PulseAudioEq`, whose code installed only the traditional PulseAudio server.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T131005Z-test-easyeffects-opt-in-package-and-profile-d28a35b9`;
candidate catalog SHA-256
`b1f0d12283d153feedfa4e3239fe2aa9abd7b28893a7547ef34e607d07b2d2f5`.
The retained transcript and `.acceptance-runs/publisher-apps-11-easyeffects.xml`
record one passing test. The RPM was absent at baseline. It passed plan,
candidate-gated apply, signature/files, executable presence, installed
status, unchanged repeat, restore, and explicit install/remove. The
`audio-effects` profile passed plan/apply/repeat/restore. Pre-existing RPM
identities were preserved. `pipewire-pulseaudio` stayed installed and the
traditional `pulseaudio` server stayed absent throughout. The unchanged DNF
handler's mocked failure evidence is reused from
[base acceptance](package.exfatprogs.md).

No audio playback, preset, or visual session was exercised. These and
broader recovery are [v3.1 item H016](../migrations/progress.md). See the
[batch review](../migrations/publisher-apps-11.md).
