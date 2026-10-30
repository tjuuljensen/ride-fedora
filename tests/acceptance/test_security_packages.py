"""Isolated package-only lifecycle and seeded-state safety on Fedora Workstation."""

import copy
import json
from pathlib import Path
import re

import pytest


RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")
ROOT = Path(__file__).resolve().parents[2]
BATCHES = (
    ("vpn-libreswan-plugin", ("NetworkManager-libreswan", "NetworkManager-libreswan-gnome")),
    ("vpn-l2tp-plugin", ("NetworkManager-l2tp", "NetworkManager-l2tp-gnome")),
    ("keepassxc", ("keepassxc",)),
)


def rpm_names(vm):
    return set(vm.run("rpm -qa --qf '%{NAME}\\n'").stdout.splitlines())


def state(vm):
    """Observe only state the package operation must preserve."""
    services = {}
    for unit in ("smartd.service", "ipsec.service", "xl2tpd.service", "NetworkManager.service"):
        enabled = vm.run(f"systemctl is-enabled {unit}", check=False).stdout.strip()
        active = vm.run(f"systemctl is-active {unit}", check=False).stdout.strip()
        services[unit] = (enabled == "enabled", active == "active")
    return {
        "rpm": rpm_names(vm),
        "connections": vm.run("nmcli -t -f UUID connection show").stdout,
        "activeConnections": vm.run("nmcli -t -f UUID connection show --active").stdout,
        "vault": vm.run("sha256sum /home/ride-test/seeded.kdbx").stdout,
        "services": services,
    }


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_package_only_security_lifecycles(vm):
    # A deterministic placeholder exercises byte preservation without storing
    # a real encrypted database or credential in acceptance artifacts.
    vm.run("printf 'RIDE seeded vault preservation check\\n' > /home/ride-test/seeded.kdbx")
    original = rpm_names(vm)
    packages = {name for _, group in BATCHES for name in group}
    already = packages & original
    if already:
        vm.run("sudo dnf -y remove " + " ".join(sorted(already)), timeout=900)
        assert original - rpm_names(vm) == already, "preparation removed another pre-existing RPM"
    baseline = state(vm)
    assert not (packages & baseline["rpm"])

    for profile, group in BATCHES:
        plan = vm.ride("plan", "--profile", profile)
        assert all(f"package.{name.lower()}\tfedora-rpm\tabsent\tinstalled\tsupported" in plan.stdout
                   for name in group)
        changed = vm.ride("apply", "--profile", profile, timeout=1200)
        match = RUN_ID.search(changed.stdout)
        assert match, changed.stdout
        record = json.loads(vm.run(f"sudo cat /var/lib/ride-fedora/runs/{match.group(1)}.json").stdout)
        assert record["status"] == "complete"
        assert {step["id"] for step in record["steps"]} == {"package." + name.lower() for name in group}
        for package in group:
            assert package in rpm_names(vm)
            signature = vm.run(f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}").stdout
            assert any(line.strip() not in ("", "(none)") for line in signature.splitlines())
            vm.run(f"rpm -V {package}")
            assert "installed" in vm.ride("status", "package." + package.lower()).stdout
        during = state(vm)
        for key in ("connections", "activeConnections", "vault", "services"):
            assert during[key] == baseline[key], f"{profile} changed {key}"
        repeated = vm.ride("apply", "--profile", profile, timeout=900)
        assert repeated.stdout.count("unchanged") == len(group)
        vm.ride("restore", "--run-id", match.group(1), "--dry-run")
        vm.ride("restore", "--run-id", match.group(1), timeout=1200)
        restored = state(vm)
        assert restored == baseline, f"{profile} did not restore seeded state or RPM baseline"
        installed = vm.ride("apply", "--profile", profile, timeout=1200)
        assert RUN_ID.search(installed.stdout)
        for package in group:
            vm.ride("remove", "package." + package.lower(), timeout=900)
        assert state(vm) == baseline, f"{profile} explicit remove did not restore baseline"


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_vpn_plugin_partial_failure_preserves_seeded_state(vm):
    vm.run("printf 'RIDE seeded vault preservation check\\n' > /home/ride-test/seeded.kdbx")
    baseline = state(vm)
    assert "NetworkManager-libreswan" not in baseline["rpm"]
    catalog = json.loads((ROOT / "catalog" / "operations.json").read_text(encoding="utf-8"))
    first_id = "package.networkmanager-libreswan"
    missing_id = "package.ride-acceptance-vpn-missing"
    first = next(row for row in catalog["operations"] if row["id"] == first_id)
    missing = copy.deepcopy(first)
    missing.update(id=missing_id, name="Deliberately absent VPN test RPM",
                   description="Test-only missing package, never published.",
                   status="candidate",
                   packageName="ride-acceptance-vpn-package-that-does-not-exist",
                   productId="ride-acceptance-vpn-missing",
                   productUri="https://example.org/ride-acceptance-vpn-missing",
                   sourceUri="https://example.org/ride-acceptance-vpn-missing",
                   licenseUri="https://example.org/ride-acceptance-vpn-missing")
    missing.pop("acceptanceEvidence", None)
    catalog["operations"].append(missing)
    guest_catalog = vm.put_json("vpn-failure-catalog", catalog)
    guest_profile = vm.put_json("vpn-failure-profile", {
        "schemaVersion": 1, "id": "vpn-failure-profile",
        "description": "Disposable partial failure probe",
        "operations": [{"id": first_id, "state": "installed"},
                       {"id": missing_id, "state": "installed"}],
    })
    failed = vm.ride("apply", "--profile", guest_profile, "--allow-candidate",
                     catalog=guest_catalog, timeout=900, check=False)
    assert failed.returncode != 0
    match = RUN_ID.search(failed.stdout)
    assert match, failed.stdout
    record = json.loads(vm.run(f"sudo cat /var/lib/ride-fedora/runs/{match.group(1)}.json").stdout)
    assert record["status"] == "failed"
    assert [(step["id"], step["result"]) for step in record["steps"]] == [
        (first_id, "changed"), (missing_id, "failed")]
    changed = state(vm)
    assert "NetworkManager-libreswan" in changed["rpm"]
    for key in ("connections", "activeConnections", "vault", "services"):
        assert changed[key] == baseline[key]
    vm.ride("restore", "--run-id", match.group(1), "--allow-candidate",
            catalog=guest_catalog, timeout=900)
    assert state(vm) == baseline
