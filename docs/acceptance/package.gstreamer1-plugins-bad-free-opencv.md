# gstreamer1-plugins-bad-free-opencv Fedora package acceptance

Status: **PASS** on Fedora 44 Workstation x86_64.

- Operation: `package.gstreamer1-plugins-bad-free-opencv`
- Source: Fedora 44 signed RPM repository; current Fedora package metadata and license recorded in the catalog.
- VM test: `tests/acceptance/test_package_contract.py::test_fedora_codec_runtime_and_opencv_batch_and_profile`
- Run: `20261031T053305Z-test-fedora-codec-runtime-and-opencv-batch-and-profile-903f0641`; package and profile lifecycle passed.
- Package verification: signature metadata was present and `rpm -V gstreamer1-plugins-bad-free-opencv` passed.
- Recovery: `remove-new-install`; the newly installed OpenCV plugin was removed after apply.

See the [codec runtime batch record](fedora-codecs-runtime-and-opencv.md).
