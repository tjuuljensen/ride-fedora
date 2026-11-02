# GStreamer bad freeworld package acceptance

Status: **PASS — operable opt-in candidate**, 2026-10-31.

Operation ID: `package.gstreamer1-plugins-bad-freeworld`.

Target: Fedora 44 Workstation x86_64, disposable TCG VM based on the pinned
Workstation image. Test: `test_rpmfusion_bad_freeworld_source_pin_coexists_and_removes`.
Artifacts: `/tmp/ride-fedora-codecs-rpmfusion/fedora-44-workstation-x86_64/20261031T060412Z-test-rpmfusion-bad-freeworld-source-pin-coexists-and-removes-53a971cc/`.

The test first confirmed that `gstreamer1-plugins-bad-freeworld` was absent and
Fedora's `gstreamer1-plugins-bad-free` was installed. It prepared RPM Fusion
through the separate `rpmfusion` profile, then installed the add-on through the
`fedora-codecs-rpmfusion` profile. The v3 DNF handler selected
`rpmfusion-free-updates` explicitly. DNF installed
`gstreamer1-plugins-bad-freeworld-1.28.8-1.fc44.x86_64`; its RPM signature
reported key ID `e06f8ecdd651ff2e`. RPM verification passed, the Fedora
`bad-free` package remained installed, and all baseline RPM identities were
preserved. A repeated apply reported `unchanged`.

Removing the add-on removed its three newly introduced runtime dependencies
(`libde265`, `svt-hevc-libs`, and `x265-libs`) as part of the same DNF
transaction. The package status became absent. Removing the separate RPM
Fusion profile then succeeded, and the final RPM identity set exactly matched
the pre-test baseline.

Focused mocked coverage confirms the install command includes only
`--from-repo=rpmfusion-free-updates`; an unknown source is rejected before DNF
runs. The package remains an opt-in candidate because it depends on the
separately managed RPM Fusion trust profile. Broader RPM Fusion trust failure
and recovery hardening remains in `provider-foundation-02`.
