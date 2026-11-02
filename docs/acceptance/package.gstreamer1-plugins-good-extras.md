# GStreamer good extras Fedora package acceptance

Status: **PASS** on Fedora 44 Workstation x86_64.

- Operation: `package.gstreamer1-plugins-good-extras`
- Source: `fedora-rpm`; Fedora repository GPG verification
- VM test: `tests/acceptance/test_package_contract.py::test_fedora_good_codec_plugins_batch_and_profile`
- Run: `20261031T050859Z-test-fedora-good-codec-plugins-batch-and-profile-455e1e56`
- Package verification: `rpm -V gstreamer1-plugins-good-extras` passed; signature metadata was present.
- Lifecycle: absent-state apply, repeat, status, RPM verification, and profile removal passed.
- Inverse: package returned to absent; all prior RPM name/architecture identities remained and no dependency residue remained.

See the [good-family batch acceptance record](fedora-codecs-good-plugins.md) for the profile transcript and dependency-update inventory.
