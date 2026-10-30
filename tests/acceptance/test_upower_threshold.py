"""Disposable Fedora 44 Workstation UPower drop-in lifecycle."""

import json
import re
import shlex

import pytest


RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")
DROPIN = "/etc/UPower/UPower.conf.d/70-ride-percentage-low.conf"


def run_id(output):
    match = RUN_ID.search(output)
    assert match, output
    return match.group(1)


def journal(vm, identifier):
    return json.loads(vm.run(f"sudo cat /var/lib/ride-fedora/runs/{identifier}.json").stdout)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_upower_threshold_profiles_and_owned_recovery(vm):
    vm.run("rpm -q upower")
    vm.run("test -f /etc/UPower/UPower.conf.d/README.md")
    vm.run("test ! -e " + shlex.quote(DROPIN))
    vm.run("test \"$(grep -c '^PercentageLow=' /etc/UPower/UPower.conf)\" = 1")
    original_main = vm.run("sha256sum /etc/UPower/UPower.conf").stdout.strip()
    original_service = vm.run("systemctl is-active upower.service", check=False).stdout.strip()
    vm.run("upower -d", check=False)

    for value in (15, 20):
        profile = f"upower-low-{value}"
        planned = vm.ride("plan", "--profile", profile)
        assert "setting.upower-percentage-low" in planned.stdout
        assert f"configured:{value}" in planned.stdout and "candidate" in planned.stdout
        refused = vm.ride("apply", "--profile", profile, check=False)
        assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
        changed = vm.ride("apply", "--profile", profile, "--allow-candidate")
        identifier = run_id(changed.stdout)
        first = journal(vm, identifier)
        assert first["status"] == "complete"
        step = first["steps"][0]
        assert step["id"] == "setting.upower-percentage-low"
        assert step["selectedValue"] == str(value)
        assert step["observedBefore"] == "absent"
        assert step["observedAfter"] == "configured"
        assert step["result"] == "changed"
        assert vm.run("sudo cat " + shlex.quote(DROPIN)).stdout == (
            "# RIDE v3 managed: setting.upower-percentage-low\n"
            f"[UPower]\nPercentageLow={value}.0\n")
        repeated = vm.ride("apply", "--profile", profile, "--allow-candidate")
        assert journal(vm, run_id(repeated.stdout))["steps"][0]["result"] == "unchanged"
        assert "configured" in vm.ride("status", "--profile", profile).stdout
        if value == 15:
            vm.run("sudo sed -i 's/PercentageLow=15.0/PercentageLow=16.0/' " + shlex.quote(DROPIN))
            conflict = vm.ride("restore", "--run-id", identifier, "--allow-candidate", check=False)
            assert conflict.returncode != 0 and "restore conflict" in conflict.stderr
            vm.run("sudo sed -i 's/PercentageLow=16.0/PercentageLow=15.0/' " + shlex.quote(DROPIN))
        vm.ride("restore", "--run-id", identifier, "--dry-run")
        vm.ride("restore", "--run-id", identifier, "--allow-candidate")
        vm.run("test ! -e " + shlex.quote(DROPIN))

    assert vm.run("sha256sum /etc/UPower/UPower.conf").stdout.strip() == original_main
    # A D-Bus-activated service can return to inactive after the guest test.
    assert original_service in {"active", "inactive", "failed", "unknown"}
