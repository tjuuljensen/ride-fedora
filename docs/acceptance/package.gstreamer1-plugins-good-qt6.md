# GStreamer good qt6 Fedora package acceptance

Status: **PASS** on Fedora 44 Workstation x86_64.

- Operation: `package.gstreamer1-plugins-good-qt6`
- Source: `fedora-rpm`; Fedora repository GPG verification
- VM test: `tests/acceptance/test_package_contract.py::test_fedora_good_codec_plugins_batch_and_profile`
- Run: `20261031T050859Z-test-fedora-good-codec-plugins-batch-and-profile-455e1e56`
- Package verification: `rpm -V gstreamer1-plugins-good-qt6` passed; signature metadata was present.
- Target state: the pinned Workstation image already included this package; apply was unchanged.
- Recovery: installed-only operation. Removing the profile kept this one-way package installed.

See the [good-family batch acceptance record](fedora-codecs-good-plugins.md) for the profile transcript and dependency-update inventory.
