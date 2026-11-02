# Fedora Workstation Multimedia GStreamer prerequisite acceptance

Status: **PASS** on Fedora 44 Workstation x86_64, 2026-10-31.

Batch 05C contains the six current GStreamer packages selected from the Fedora
Workstation Multimedia group. The v2 `gstreamer1-libav` name is absent from
Fedora 44; `gstreamer1-plugin-libav` is the current Fedora group member. All
six packages were present in the pinned Workstation image, so the v3 operations
are installed-only and their opt-in profile is non-destructive on removal.

The acceptance test
`tests/acceptance/test_package_contract.py::test_fedora_multimedia_group_gstreamer_batch_and_profile`
asserted all six baseline packages were present before apply, checked profile
plan, apply, repeat, Fedora RPM signature metadata, `rpm -V`, status, and
remove-profile behavior, and confirmed all prior RPM identities remained. All
six apply steps were unchanged; profile removal reported each as a kept
one-way prerequisite. The run used `--allow-candidate`; the operations were
promoted to `supported` after this evidence passed. The initial sandboxed
attempt stopped before VM launch because loopback socket creation was denied;
the same check then passed with VM networking permission. That first attempt
created no VM or package state.

| Field | Evidence |
| --- | --- |
| Target | Fedora 44 Workstation x86_64 |
| Package source and license | Fedora 44 repository metadata, queried 2026-10-31; package pages are linked from each catalog operation |
| Lifecycle VM run | `20261031T052014Z-test-fedora-multimedia-group-gstreamer-batch-and-profile-86433818`; 1 passed in 244.40 seconds using TCG |
| Transcript | `/tmp/ride-fedora-codecs-multimedia-batch/fedora-44-workstation-x86_64/20261031T052014Z-test-fedora-multimedia-group-gstreamer-batch-and-profile-86433818/transcript.jsonl` |
| Metadata | `/tmp/ride-fedora-codecs-multimedia-batch/fedora-44-workstation-x86_64/20261031T052014Z-test-fedora-multimedia-group-gstreamer-batch-and-profile-86433818/metadata.json` |
| Image | SHA-256 `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a` |
