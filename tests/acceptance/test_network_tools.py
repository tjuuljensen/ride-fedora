"""Disposable Workstation lifecycle for the two v2 network-tool bundles."""

import json
import re

import pytest


NETWORK = ("tcpdump", "wireshark", "tftp-server", "nmap", "macchanger", "flow-tools", "nethogs")
COMMS = ("minicom", "putty", "remmina")
RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")


def rpm_names(vm):
    return set(vm.run("rpm -qa --qf '%{NAME}\\n'").stdout.splitlines())


def assert_tftp_off(vm):
    enabled = vm.run("systemctl is-enabled tftp.socket", check=False)
    active = vm.run("systemctl is-active tftp.socket", check=False)
    assert enabled.stdout.strip() != "enabled", enabled.stdout
    assert active.stdout.strip() != "active", active.stdout


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_network_package_bundles(vm):
    original = rpm_names(vm)
    if "tcpdump" in original:
        vm.run("sudo dnf -y remove tcpdump", timeout=900)
        assert original - rpm_names(vm) == {"tcpdump"}, "preparation removed another pre-existing RPM"
    baseline = rpm_names(vm)
    assert not (set(NETWORK + COMMS) & baseline), "network pilot requires absent package baseline"
    assert_tftp_off(vm)
    for package in NETWORK + COMMS:
        identifier = f"package.{package}"
        fixture = vm.put_json(f"network-{package}", {
            "schemaVersion": 1, "id": f"network-{package}",
            "description": "Disposable network RPM lifecycle",
            "operations": [{"id": identifier, "state": "installed"}],
        })
        plan = vm.ride("plan", "--profile", fixture)
        assert f"{identifier}\tfedora-rpm\tabsent\tinstalled\tcandidate" in plan.stdout
        gated = vm.ride("apply", "--profile", fixture, check=False)
        assert gated.returncode != 0 and "--allow-candidate" in gated.stderr
        changed = vm.ride("apply", "--profile", fixture, "--allow-candidate", timeout=900)
        match = RUN_ID.search(changed.stdout)
        assert match, changed.stdout
        record = json.loads(vm.run(f"sudo cat /var/lib/ride-fedora/runs/{match.group(1)}.json").stdout)
        assert record["status"] == "complete"
        assert record["steps"][0]["result"] == "changed"
        assert package in rpm_names(vm)
        signature = vm.run(f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}").stdout
        assert any(line.strip() not in ("", "(none)") for line in signature.splitlines())
        vm.run(f"rpm -V {package}")
        repeat = vm.ride("apply", "--profile", fixture, "--allow-candidate")
        assert "unchanged" in repeat.stdout
        assert f"{identifier}\tfedora-rpm\tinstalled" in vm.ride("status", identifier).stdout
        if package == "tftp-server":
            assert_tftp_off(vm)
        vm.ride("restore", "--run-id", match.group(1), "--dry-run")
        vm.ride("restore", "--run-id", match.group(1), "--allow-candidate", timeout=900)
        assert package not in rpm_names(vm)
        assert not (baseline - rpm_names(vm)), "RIDE removed a pre-existing RPM"

    for profile, packages in (("network-analysis-tools", NETWORK), ("remote-comms-tools", COMMS)):
        planned = vm.ride("plan", "--profile", profile)
        assert all(f"package.{package}" in planned.stdout for package in packages)
        changed = vm.ride("apply", "--profile", profile, "--allow-candidate", timeout=1200)
        match = RUN_ID.search(changed.stdout)
        assert match, changed.stdout
        assert set(packages) <= rpm_names(vm)
        assert_tftp_off(vm)
        repeated = vm.ride("apply", "--profile", profile, "--allow-candidate", timeout=900)
        assert repeated.stdout.count("unchanged") == len(packages)
        vm.ride("restore", "--run-id", match.group(1), "--allow-candidate", timeout=1200)
        assert not (set(packages) & rpm_names(vm))
        assert not (baseline - rpm_names(vm)), "RIDE removed a pre-existing RPM"
