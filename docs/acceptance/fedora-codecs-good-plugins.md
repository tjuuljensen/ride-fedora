# Fedora GStreamer good-family add-on lifecycle

Status: **PASS on Fedora 44 Workstation x86_64**, 2026-10-31.

The opt-in `fedora-codecs-good-plugins` profile contains four explicit Fedora
RPMs selected from the v2 `gstreamer1-plugins-good-*` expansion:
`gstreamer1-plugins-good-extras`, `gstreamer1-plugins-good-gtk`,
`gstreamer1-plugins-good-qt`, and `gstreamer1-plugins-good-qt6`. GTK and Qt6
are present in the pinned Fedora 44 Workstation image, so those operations
are installed-only one-way prerequisites and profile removal preserves them.
Extras and Qt remain exact reversible package operations. All use the
Fedora-signed repository and generic DNF package handler. The profile stays
separate from `default` and from the RPM Fusion option.

The predeclared acceptance check is
`tests/acceptance/test_package_contract.py::test_fedora_good_codec_plugins_batch_and_profile`.
It verified the four-package plan against the Workstation baseline, changed
steps for Extras and Qt, unchanged steps for preinstalled GTK and Qt6, repeat,
RPM signature metadata, `rpm -V`, status, and profile removal. GTK and Qt6
remained installed as one-way packages; Extras and Qt returned to absent. All
prior RPM name/architecture identities remained, and no newly added
dependency residue survived. Applying Extras and Qt added 12 dependencies
and updated the existing GStreamer good-family and Qt6 RPM versions; these
package-manager effects are included in the inventory comparison.

The first preflight run found `gstreamer1-plugins-good-gtk` already present
and stopped before apply. The adjusted model makes GTK and Qt6 installed-only
operations; the passing run below verified they remain when the profile is
removed.

| Field | Evidence |
| --- | --- |
| Target | Fedora 44 Workstation x86_64 |
| Package metadata | Read-only Fedora 44 DNF repository metadata, 2026-10-31 |
| Preflight | `20261031T050517Z-test-fedora-good-codec-plugins-batch-and-profile-9af1eba9`; confirmed GTK/Qt6 in baseline and stopped before apply |
| Lifecycle VM run | `20261031T050859Z-test-fedora-good-codec-plugins-batch-and-profile-455e1e56`; 1 passed in 498.15 seconds using TCG |
| Transcript | `/tmp/ride-fedora-codecs-good-plugins-2/fedora-44-workstation-x86_64/20261031T050859Z-test-fedora-good-codec-plugins-batch-and-profile-455e1e56/transcript.jsonl` |
| Image | SHA-256 `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a` |
| Result | PASS; two reversible operations and two one-way Workstation packages behaved as declared. |
