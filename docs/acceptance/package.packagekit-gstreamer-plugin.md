# PackageKit-gstreamer-plugin Fedora package acceptance

Status: **PASS** on Fedora 44 Workstation x86_64.

- Operation: `package.packagekit-gstreamer-plugin`
- RPM name: `PackageKit-gstreamer-plugin`
- Source: Fedora 44 signed RPM repository; current Fedora package metadata and license recorded in the catalog.
- VM test: `tests/acceptance/test_package_contract.py::test_fedora_multimedia_audio_video_integration_batch_and_profile`
- Run: `20261031T054506Z-test-fedora-multimedia-audio-video-integration-batch-and-profile-f4c0a2f1`; apply and repeat were unchanged.
- Package verification: signature metadata was present and `rpm -V PackageKit-gstreamer-plugin` passed.
- Recovery: installed-only; profile removal preserved this package.

See the [audio/video integration batch record](fedora-codecs-audio-video-integration.md).
