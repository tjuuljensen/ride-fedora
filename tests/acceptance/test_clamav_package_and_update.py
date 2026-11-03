"""Probe Fedora's ClamAV package, one-shot update, and data retention contract."""

import hashlib
import shlex

import pytest


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_clamav_packages_one_shot_update_and_data_retention(vm):
    vm.run("rpm -q clamav clamav-freshclam clamav-data", check=False)
    vm.run("sudo mkdir -p /var/lib/clamav")
    vm.run("printf 'RIDE seeded ClamAV state\\n' | sudo tee /var/lib/clamav/ride-seeded-marker >/dev/null")
    marker_hash = hashlib.sha256(b"RIDE seeded ClamAV state\n").hexdigest()
    vm.run("sudo dnf -y install clamav clamav-freshclam", timeout=900)

    packages = vm.run(
        "rpm -q --qf '%{NAME} %{VERSION}-%{RELEASE} %{ARCH}\\n' "
        "clamav clamav-freshclam"
    )
    print(f"ClamAV RPMs:\n{packages.stdout}")
    signature_package = vm.run("rpm -q clamav-data", check=False)
    print(f"Optional Fedora signature-data RPM: {signature_package.stdout}{signature_package.stderr}")
    verification = vm.run("sudo rpm -V clamav clamav-freshclam", check=False)
    print(f"RPM verification rc={verification.returncode}: {verification.stdout}{verification.stderr}")
    assert verification.returncode == 0, "Fedora RPM verification reported modified package files"

    units = vm.run(
        "systemctl list-unit-files --no-legend 'clamav-freshclam*' | "
        "awk '$1 ~ /\\.(service|timer)$/ {print $1}'"
    ).stdout.splitlines()

    def freshclam_unit_states():
        states = {}
        for unit in units:
            result = vm.run(
                f"printf '%s\\t' {shlex.quote(unit)}; "
                f"printf '%s\\t' \"$(systemctl is-enabled {shlex.quote(unit)} 2>/dev/null || true)\"; "
                f"systemctl is-active {shlex.quote(unit)} 2>/dev/null || true"
            ).stdout.strip().split("\t")
            assert len(result) == 3, f"could not record systemd state for {unit}: {result!r}"
            states[unit] = (result[1], result[2])
        return states

    installed_unit_states = freshclam_unit_states()
    print(f"FreshClam service and timer states after install: {installed_unit_states}")

    update = vm.run("sudo freshclam --verbose", timeout=600, check=False)
    print(f"freshclam rc={update.returncode}:\n{update.stdout[-12000:]}\n{update.stderr[-12000:]}")
    assert update.returncode == 0
    vm.run(f"test \"$(sha256sum /var/lib/clamav/ride-seeded-marker | cut -d' ' -f1)\" = {marker_hash}")
    after_update_unit_states = freshclam_unit_states()
    print(f"FreshClam service and timer states after one-shot update: {after_update_unit_states}")
    for unit, (enabled, active) in after_update_unit_states.items():
        if unit.endswith(".timer"):
            assert enabled != "enabled" and active != "active", (
                f"ClamAV timer unexpectedly enabled or active: {unit} {enabled}/{active}"
            )
        if unit.endswith(".service"):
            assert active != "active", f"ClamAV service unexpectedly active: {unit}"
    assert after_update_unit_states.get("clamav-freshclam.service", ("", ""))[0] != "enabled"
    databases = vm.run("find /var/lib/clamav -maxdepth 1 -type f -printf '%f %s bytes\\n' | sort")
    print(f"Signature database files after freshclam:\n{databases.stdout}")

    vm.run("sudo dnf -y remove clamav clamav-freshclam", timeout=600)
    vm.run(f"test \"$(sha256sum /var/lib/clamav/ride-seeded-marker | cut -d' ' -f1)\" = {marker_hash}")
    after_remove = vm.run(
        "rpm -q clamav clamav-freshclam clamav-data; "
        "find /var/lib/clamav -maxdepth 1 -type f -printf '%f %s bytes\\n' | sort",
        check=False,
    )
    print(f"After explicit package removal:\n{after_remove.stdout}{after_remove.stderr}")
