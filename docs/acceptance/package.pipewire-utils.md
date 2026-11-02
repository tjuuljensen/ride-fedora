# pipewire-utils Fedora package acceptance

Status: **PASS** on Fedora 44 Workstation x86_64.

- Operation: `package.pipewire-utils`
- Source: Fedora 44 signed RPM repository; current Fedora package metadata and license recorded in the catalog.
- VM test: `tests/acceptance/test_package_contract.py::test_fedora_pipewire_espeak_batch_and_profile`
- Run: `20261031T060002Z-test-fedora-pipewire-espeak-batch-and-profile-cf965e0b`; package and profile lifecycle passed.
- Package verification: signature metadata was present and `rpm -V pipewire-utils` passed.
- Recovery: installed-only; profile removal preserved this baseline package.

See the [PipeWire and eSpeak batch record](fedora-codecs-pipewire-and-espeak.md).
