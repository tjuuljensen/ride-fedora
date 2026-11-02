# gstreamer1-plugins-bad-free Fedora package acceptance

Status: **PASS** on Fedora 44 Workstation x86_64.

- Operation: `package.gstreamer1-plugins-bad-free`
- Source: Fedora 44 signed RPM repository; current Fedora package metadata and license recorded in the catalog.
- VM test: `tests/acceptance/test_package_contract.py::test_fedora_multimedia_group_gstreamer_batch_and_profile`
- Run: `20261031T052014Z-test-fedora-multimedia-group-gstreamer-batch-and-profile-86433818`; apply and repeat were unchanged.
- Package verification: signature metadata was present and `rpm -V gstreamer1-plugins-bad-free` passed.
- Recovery: installed-only operation; profile removal kept this package.

See the [Multimedia group batch record](fedora-codecs-multimedia-group.md).
