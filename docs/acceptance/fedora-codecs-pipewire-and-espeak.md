# Fedora PipeWire and conditional eSpeak acceptance

Status: **PASS** on Fedora 44 Workstation x86_64, 2026-10-31.

Batch 05F contains the final four Fedora Workstation Multimedia group packages:
PipeWire PulseAudio compatibility, PipeWire utilities, WirePlumber, and the
conditional GStreamer eSpeak plugin. Fedora 44 repository metadata confirmed
eSpeak is available. The three PipeWire/WirePlumber packages were present in
the pinned image and use installed-only one-way operations. eSpeak was absent
and uses exact remove-new-install recovery.

The acceptance test
`tests/acceptance/test_package_contract.py::test_fedora_pipewire_espeak_batch_and_profile`
asserted the baseline before apply, then checked plan, apply, repeat, Fedora
signature metadata, `rpm -V`, status, profile removal, and RPM inventory
recovery. Apply changed only eSpeak; repeat was unchanged; profile removal
removed eSpeak and kept all three baseline packages. All prior RPM identities
remained. These operations were promoted to `supported` after the evidence
passed.

| Field | Evidence |
| --- | --- |
| Target | Fedora 44 Workstation x86_64 |
| Package source and license | Fedora 44 repository metadata, queried 2026-10-31; package pages are linked from each catalog operation |
| Lifecycle VM run | `20261031T055131Z-test-fedora-pipewire-espeak-batch-and-profile-cf965e0b`; 1 passed in 362.63 seconds using TCG |
| Transcript | `/tmp/ride-fedora-codecs-pipewire-espeak/fedora-44-workstation-x86_64/20261031T055131Z-test-fedora-pipewire-espeak-batch-and-profile-cf965e0b/transcript.jsonl` |
| Metadata | `/tmp/ride-fedora-codecs-pipewire-espeak/fedora-44-workstation-x86_64/20261031T055131Z-test-fedora-pipewire-espeak-batch-and-profile-cf965e0b/metadata.json` |
| Image | SHA-256 `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a` |
