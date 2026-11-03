"""Disposable Fedora 44 lifecycle and failure rollback for ClamAV signatures."""

import json
from pathlib import Path
import re

import pytest


ROOT = Path(__file__).resolve().parents[2]
PROFILE = "fedora-clamav-initial-signatures"
RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")


def _rpm_names(vm):
    return set(vm.run("rpm -qa --qf '%{NAME}\\n'").stdout.splitlines())


def _unit_state(vm, unit):
    enabled = vm.run(f"systemctl is-enabled {unit}", check=False).stdout.strip()
    active = vm.run(f"systemctl is-active {unit}", check=False).stdout.strip()
    return enabled or "unknown", active or "unknown"


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_clamav_failure_rollback_and_exact_signature_recovery(vm):
    vm.run("test ! -e /usr/local/bin/freshclam")
    initial_packages = _rpm_names(vm)
    assert "clamav" not in initial_packages
    assert "clamav-freshclam" not in initial_packages

    profile = json.loads((ROOT / "profiles" / f"{PROFILE}.json").read_text(encoding="utf-8"))
    guest_profile = vm.put_json("clamav-v3-profile", profile)
    vm.run(
        "sudo mkdir -p /var/lib/clamav && "
        "printf 'prior ClamAV state\\n' | sudo tee /var/lib/clamav/ride-seeded-marker >/dev/null && "
        "sudo chmod 0640 /var/lib/clamav/ride-seeded-marker"
    )
    before_tree = vm.run(
        f"sudo python3 {vm.repo}/tools/clamav-state.py hash /var/lib/clamav"
    ).stdout.strip()

    plan = vm.ride("plan", "--profile", guest_profile)
    assert "package.clamav" in plan.stdout and "candidate" in plan.stdout
    refused = vm.ride("apply", "--profile", guest_profile, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert _rpm_names(vm) == initial_packages

    vm.run(
        "sudo install -d -m 0755 /usr/local/bin && "
        "printf '#!/usr/bin/env bash\\nexit 17\\n' | "
        "sudo tee /usr/local/bin/freshclam >/dev/null && "
        "sudo chmod 0755 /usr/local/bin/freshclam"
    )
    failed = vm.run(
        f"sudo env PATH=/usr/local/bin:/usr/bin:/bin {vm.repo}/ride.sh apply "
        f"--profile {guest_profile} --allow-candidate",
        timeout=1200,
        check=False,
    )
    assert failed.returncode != 0 and "initial FreshClam update failed" in failed.stderr
    vm.run("sudo rm -f /usr/local/bin/freshclam")
    assert _rpm_names(vm) == initial_packages
    assert vm.run(
        f"sudo python3 {vm.repo}/tools/clamav-state.py hash /var/lib/clamav"
    ).stdout.strip() == before_tree
    vm.run("test ! -e /var/lib/ride-fedora/owned-tools/package.clamav/state.json")

    # Preserve a separately pre-existing main RPM while RIDE adds only the
    # missing updater package and runs the initial signature refresh.
    vm.run("sudo dnf -y install clamav", timeout=900)
    preexisting_packages = _rpm_names(vm)
    assert "clamav" in preexisting_packages and "clamav-freshclam" not in preexisting_packages
    preexisting_data_tree = vm.run(
        f"sudo python3 {vm.repo}/tools/clamav-state.py hash /var/lib/clamav"
    ).stdout.strip()

    applied = vm.ride("apply", "--profile", guest_profile, "--allow-candidate", timeout=1200)
    run_id = RUN_ID.search(applied.stdout).group(1)
    assert {"clamav", "clamav-freshclam"} <= _rpm_names(vm)
    # FreshClam intentionally changes package %ghost signature-database files;
    # verify package-owned files separately from the managed database state.
    vm.run("sudo rpm -V --noghost clamav clamav-freshclam")
    assert vm.run("find /var/lib/clamav -maxdepth 1 -type f -name '*.cvd' -size +0c | grep .").returncode == 0
    assert vm.run("test -e /var/lib/clamav/ride-seeded-marker")
    for unit in (
        "clamav-freshclam.service",
        "clamav-freshclam-once.service",
        "clamav-freshclam-once.timer",
    ):
        assert _unit_state(vm, unit) == ("disabled", "inactive")
    assert "installed" in vm.ride("status", "package.clamav").stdout
    assert "unchanged package.clamav" in vm.ride(
        "apply", "--profile", guest_profile, "--allow-candidate"
    ).stdout

    journal = json.loads(vm.run(f"sudo cat /var/lib/ride-fedora/runs/{run_id}.json").stdout)
    assert journal["status"] == "complete"
    vm.ride("restore", "--run-id", run_id, "--dry-run", "--allow-candidate")
    vm.ride("restore", "--run-id", run_id, "--allow-candidate", timeout=1200)
    assert _rpm_names(vm) == preexisting_packages
    assert vm.run(
        f"sudo python3 {vm.repo}/tools/clamav-state.py hash /var/lib/clamav"
    ).stdout.strip() == preexisting_data_tree
    for unit in (
        "clamav-freshclam.service",
        "clamav-freshclam-once.service",
        "clamav-freshclam-once.timer",
    ):
        assert _unit_state(vm, unit) == ("not-found", "inactive")
    assert "absent" in vm.ride("status", "package.clamav").stdout
