# Fedora codec runtime and OpenCV acceptance

Status: **PASS** on Fedora 44 Workstation x86_64, 2026-10-31.

Batch 05D contains the remaining bad-free runtime libraries, the optional
OpenCV plugin, GStreamer base, and LAME runtime libraries. The pinned
Workstation baseline contained three packages; OpenCV was absent. Three
installed-only operations preserve existing packages. OpenCV uses
remove-new-install recovery and remains opt-in.

The acceptance test
`tests/acceptance/test_package_contract.py::test_fedora_codec_runtime_and_opencv_batch_and_profile`
asserted the baseline before apply, then checked plan, apply, repeat, Fedora
signature metadata, `rpm -V`, status, package removal, and RPM inventory
recovery. Apply changed only OpenCV, then repeat was unchanged. Fedora's DNF
transaction installed 91 dependency packages, upgraded 2 and replaced 2
existing RPM versions; the inverse removed the 91 introduced packages. All
pre-existing RPM name/architecture identities remained, and OpenCV was absent
after removal. The operations were promoted to `supported` after this evidence
passed.

The first acceptance run returned from the package command but the host ran
out of `/tmp` quota while recording its large DNF output. That run is not used
as acceptance evidence. The cause was investigated, stopped disposable VM
overlays were removed, and the complete fresh-image rerun below passed.

| Field | Evidence |
| --- | --- |
| Target | Fedora 44 Workstation x86_64 |
| Package source and license | Fedora 44 repository metadata, queried 2026-10-31; package pages are linked from each catalog operation |
| Lifecycle VM run | `20261031T053305Z-test-fedora-codec-runtime-and-opencv-batch-and-profile-903f0641`; 1 passed in 617.30 seconds using TCG |
| Transcript | `/tmp/ride-fedora-codecs-runtime-opencv-retry/fedora-44-workstation-x86_64/20261031T053305Z-test-fedora-codec-runtime-and-opencv-batch-and-profile-903f0641/transcript.jsonl` |
| Metadata | `/tmp/ride-fedora-codecs-runtime-opencv-retry/fedora-44-workstation-x86_64/20261031T053305Z-test-fedora-codec-runtime-and-opencv-batch-and-profile-903f0641/metadata.json` |
| Image | SHA-256 `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a` |
