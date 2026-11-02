# Fedora optional codec package lifecycle

Status: **PASS on Fedora 44 Workstation x86_64**, 2026-10-31.

The `fedora-codecs-optional` profile contains six explicit Fedora RPMs that
were selected from the v2 `gstreamer1-plugins-bad-*` and `lame*` globs:
`gstreamer1-plugins-bad-free-extras`, `gstreamer1-plugins-bad-free-fluidsynth`,
`gstreamer1-plugins-bad-free-lv2`, `gstreamer1-plugins-bad-free-wildmidi`,
`gstreamer1-plugins-bad-free-zbar`, and `lame`. They use the Fedora-signed
repository source and generic owned DNF package handler. Existing packages
from other owners remain unchanged. The profile is opt-in and does not alter
the `default` profile.

The automated checks are
`tests/acceptance/test_package_contract.py::test_fedora_optional_codec_plugins_batch_and_profile`.
The first VM pilot completed all six operations' absent-state apply, repeat,
status, RPM file verification, restore, install, and remove checks. Its
combined profile phase was cut short when repeated transactions exhausted the
local temporary-storage quota. The streamlined second pilot checked the
public profile's exact six operation plan, combined apply, repeat, status,
RPM file verification, and remove lifecycle.

The combined apply added the six declared packages and 18 package
dependencies. It updated the existing `gstreamer1-plugins-bad-free` and
`gstreamer1-plugins-bad-free-libs` RPM versions. The inverse retained every
pre-existing RPM name and architecture and removed all newly added RPMs,
including dependencies; no residue remained.

| Field | Evidence |
| --- | --- |
| Target | Fedora 44 Workstation x86_64 |
| Source inventory | Read-only Fedora 44 repository metadata and DNF package records, 2026-10-31 |
| Individual VM run | `20261031T042018Z-test-fedora-optional-codec-plugins-batch-and-profile-a889d3e0`; each per-package lifecycle passed before the repeated-transaction phase hit temporary-storage quota. |
| Combined profile VM run | `20261031T044932Z-test-fedora-optional-codec-plugins-batch-and-profile-551832f5`; 1 passed in 713.18 seconds using TCG. |
| Transcript | `/tmp/ride-fedora-codecs-optional-2/fedora-44-workstation-x86_64/20261031T044932Z-test-fedora-optional-codec-plugins-batch-and-profile-551832f5/transcript.jsonl` |
| Image | SHA-256 `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a` |
| Result | Individual and combined profile lifecycles passed; prior package upgrades and complete inverse were checked. |

This batch does not cover the rest of the v2 package globs, the Multimedia
group members, or RPM Fusion's `gstreamer1-plugins-bad-freeworld` alternative.
Those remain in the provider-foundation-05 migration queue.
