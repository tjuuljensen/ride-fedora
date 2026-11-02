"""SmartMonTools package lifecycle with its Fedora smartd enablement side effect."""

import json
from pathlib import Path
import re

import pytest


ROOT = Path(__file__).resolve().parents[2]
PROFILE = "fedora-workstation-smartmontools"
RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")


def rpm_names(vm):
    return set(vm.run("rpm -qa --qf '%{NAME}\\n'").stdout.splitlines())


def smartd_state(vm):
    enabled = vm.run("systemctl is-enabled smartd.service", check=False).stdout.strip()
    active = vm.run("systemctl is-active smartd.service", check=False).stdout.strip()
    return enabled, active


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_smartmontools_package_lifecycle_keeps_smartd_disabled(vm):
    catalog = json.loads((ROOT / "catalog" / "operations.json").read_text(encoding="utf-8"))
    catalog["operations"] = [entry for entry in catalog["operations"]
                             if entry["id"] == "package.smartmontools"]
    guest_catalog = vm.put_json("smartmontools-test-catalog", catalog)
    original = rpm_names(vm)
    if "smartmontools" in original:
        vm.run("sudo dnf -y remove smartmontools", timeout=900)
        assert original - rpm_names(vm) == {"smartmontools"}
    baseline = rpm_names(vm)
    assert "smartmontools" not in baseline
    assert smartd_state(vm)[0] == "not-found"

    plan = vm.ride("plan", "--profile", PROFILE)
    assert "package.smartmontools\tfedora-rpm\tabsent\tinstalled\tcandidate" in plan.stdout
    refused = vm.ride("apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    applied = vm.ride("apply", "--profile", PROFILE, "--allow-candidate",
                      catalog=guest_catalog, timeout=900)
    run_id = RUN_ID.search(applied.stdout).group(1)
    assert "smartmontools" in rpm_names(vm)
    vm.run("rpm -V smartmontools")
    signature = vm.run("rpm -q --qf '%{RSAHEADER:pgpsig}\\n' smartmontools").stdout.strip()
    assert signature and signature != "(none)"
    assert smartd_state(vm) == ("disabled", "inactive")
    vm.run("! pgrep -x smartd")
    vm.run("smartctl --version")
    assert "installed" in vm.ride("status", "package.smartmontools",
                                   catalog=guest_catalog).stdout
    assert "unchanged package.smartmontools" in vm.ride(
        "apply", "--profile", PROFILE, "--allow-candidate", catalog=guest_catalog
    ).stdout

    record = json.loads(vm.run(
        f"sudo cat /var/lib/ride-fedora/runs/{run_id}.json"
    ).stdout)
    assert record["status"] == "complete"
    vm.ride("restore", "--run-id", run_id, "--dry-run", "--allow-candidate",
            catalog=guest_catalog)
    vm.ride("restore", "--run-id", run_id, "--allow-candidate",
            catalog=guest_catalog, timeout=900)
    assert "smartmontools" not in rpm_names(vm)
    assert smartd_state(vm)[0] == "not-found"
    assert rpm_names(vm) == baseline

    vm.ride("install", "package.smartmontools", "--allow-candidate",
            catalog=guest_catalog, timeout=900)
    assert smartd_state(vm) == ("disabled", "inactive")
    vm.ride("remove", "package.smartmontools", "--allow-candidate",
            catalog=guest_catalog, timeout=900)
    assert "smartmontools" not in rpm_names(vm)
    assert rpm_names(vm) == baseline
