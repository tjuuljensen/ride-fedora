"""Verify Fedora 44 RPM Fusion release RPMs with Fedora-packaged keys."""

import pytest


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_rpmfusion_release_rpms_verify_with_fedora_packaged_keys(vm):
    if vm.run("rpm -q distribution-gpg-keys", check=False).returncode != 0:
        vm.run("sudo dnf5 install -y distribution-gpg-keys", timeout=1200)
    vm.run("rpm -V distribution-gpg-keys")

    artifacts = vm.run("mktemp -d /tmp/ride-rpmfusion-trust.XXXXXX").stdout.strip()
    packages = {
        "free": {
            "fingerprint": "E9A491A3DE247814E7E067EAE06F8ECDD651FF2E",
            "key": "/usr/share/distribution-gpg-keys/rpmfusion/RPM-GPG-KEY-rpmfusion-free-fedora-44",
            "url": "https://download1.rpmfusion.org/free/fedora/updates/44/x86_64/r/rpmfusion-free-release-44-3.noarch.rpm",
            "name": "rpmfusion-free-release",
        },
        "nonfree": {
            "fingerprint": "79BDB88F9BBF73910FD4095B6A2AF96194843C65",
            "key": "/usr/share/distribution-gpg-keys/rpmfusion/RPM-GPG-KEY-rpmfusion-nonfree-fedora-44",
            "url": "https://download1.rpmfusion.org/nonfree/fedora/updates/44/x86_64/r/rpmfusion-nonfree-release-44-3.noarch.rpm",
            "name": "rpmfusion-nonfree-release",
        },
    }

    packaged_fingerprints = vm.run(
        "find /usr/share/distribution-gpg-keys/rpmfusion -maxdepth 1 -type f -print0 "
        "| xargs -0 -r -n1 gpg --show-keys --with-colons --fingerprint 2>/dev/null "
        "| awk -F: '$1 == \"fpr\" { print toupper($10) }'"
    ).stdout.upper().split()

    for family, package in packages.items():
        rpm_path = f"{artifacts}/{family}.rpm"
        fingerprint = vm.run(
            f"gpg --show-keys --with-colons --fingerprint {package['key']} "
            "| awk -F: '$1 == \"fpr\" { print $10; exit }'"
        ).stdout.strip()
        assert fingerprint.upper() == package["fingerprint"]

        vm.run(f"curl --fail --location --proto '=https' --tlsv1.2 --output {rpm_path} {package['url']}", timeout=300)
        metadata = vm.run(
            f"rpm -qp --qf '%{{NAME}} %{{VERSION}}-%{{RELEASE}} %{{LICENSE}} %{{ARCH}}\\n' {rpm_path}"
        ).stdout.strip()
        assert metadata.startswith(f"{package['name']} 44-3 ")
        assert metadata.endswith(" noarch")
        signature = vm.run(f"rpm -qp --qf '%{{RSAHEADER:pgpsig}}\\n' {rpm_path}").stdout.lower()
        assert fingerprint[-16:].lower() in signature

        paths = vm.run(f"rpm -qp --queryformat '[%{{FILENAMES}}\\n]' {rpm_path}").stdout
        assert f"/etc/yum.repos.d/rpmfusion-{family}" in paths
        assert "/etc/pki/rpm-gpg/" in paths
        assert any(item.endswith(fingerprint[-16:]) for item in packaged_fingerprints)
        vm.run(f"sudo rpm --import {package['key']}")
        check = vm.run(f"rpm --checksig --verbose {rpm_path}")
        assert f"key fingerprint: {fingerprint.lower()}: OK" in check.stdout
        assert "Payload SHA256 digest: OK" in check.stdout
