# GStreamer bad free LV2 plugin Fedora package acceptance

Status: **PASS** on Fedora 44 Workstation x86_64.

- Operation: `package.gstreamer1-plugins-bad-free-lv2`
- Source: `fedora-rpm`; Fedora repository GPG verification
- VM: `tests/acceptance/test_package_contract.py::test_fedora_optional_codec_plugins_batch_and_profile`
- Individual lifecycle run: `20261031T042018Z-test-fedora-optional-codec-plugins-batch-and-profile-a889d3e0`
- Package verification: `rpm -V gstreamer1-plugins-bad-free-lv2` passed; RPM signature metadata was present.
- Lifecycle: absent-state plan, apply, repeat, status, restore, install, and remove passed.

The [combined codec acceptance record](fedora-codecs-optional.md) links the individual transcript and the separate passing profile run, including dependency-update details.
