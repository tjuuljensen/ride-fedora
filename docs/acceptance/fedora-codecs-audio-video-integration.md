# Fedora Workstation audio and video integration acceptance

Status: **PASS** on Fedora 44 Workstation x86_64, 2026-10-31.

Batch 05E contains six Fedora Workstation Multimedia group prerequisites:
PackageKit's GStreamer helper, ALSA UCM configuration and utilities, Intel
VA-API media driver, and PipeWire ALSA/GStreamer integrations. All six were
present in the pinned image and are modeled as installed-only one-way
operations in an opt-in profile.

The acceptance test
`tests/acceptance/test_package_contract.py::test_fedora_multimedia_audio_video_integration_batch_and_profile`
asserted the baseline before apply, then checked plan, apply, repeat, signature
metadata, `rpm -V`, status, removal, and prior RPM identity preservation. All
six apply steps and all repeated steps were unchanged. Removal retained all
six one-way packages. The operations were promoted to `supported` after this
evidence passed.

| Field | Evidence |
| --- | --- |
| Target | Fedora 44 Workstation x86_64 |
| Package source and license | Fedora 44 repository metadata, queried 2026-10-31; package pages are linked from each catalog operation |
| Lifecycle VM run | `20261031T054506Z-test-fedora-multimedia-audio-video-integration-batch-and-profile-f4c0a2f1`; 1 passed in 246.03 seconds using TCG |
| Transcript | `/tmp/ride-fedora-codecs-audio-video/fedora-44-workstation-x86_64/20261031T054506Z-test-fedora-multimedia-audio-video-integration-batch-and-profile-f4c0a2f1/transcript.jsonl` |
| Metadata | `/tmp/ride-fedora-codecs-audio-video/fedora-44-workstation-x86_64/20261031T054506Z-test-fedora-multimedia-audio-video-integration-batch-and-profile-f4c0a2f1/metadata.json` |
| Image | SHA-256 `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a` |
