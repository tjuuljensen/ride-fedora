"""Explicit DNF5 whole-system update pilot on disposable Fedora 44 Workstation."""

import shlex

import pytest


def verify_system_update(vm):
    ride = f"{vm.repo}/ride.sh"
    planned = vm.run(
        f"sudo {shlex.quote(ride)} update system.update-all-packages --dry-run --allow-candidate",
        timeout=900,
    )
    assert "system.update-all-packages" in planned.stdout
    applied = vm.run(
        f"sudo {shlex.quote(ride)} update system.update-all-packages --allow-candidate",
        timeout=3600,
    )
    assert "DNF5 system update report:" in applied.stdout
    run_id = applied.stdout.split("Run ID: ", 1)[1].splitlines()[0]
    journal = vm.run(f"sudo jq -c '.steps[0]' /var/lib/ride-fedora/runs/{shlex.quote(run_id)}.json").stdout
    assert '"updateReport"' in journal
    assert '"transactionId"' in journal
    assert vm.run(
        f"sudo {shlex.quote(ride)} status system.update-all-packages", timeout=900
    ).stdout.rstrip().endswith("current")
    restore = vm.run(f"sudo {shlex.quote(ride)} restore --run-id {shlex.quote(run_id)}", check=False)
    assert restore.returncode != 0
    assert "exact recovery is unavailable" in restore.stderr


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_system_update_workstation_is_reported_and_nonrestorable(vm):
    verify_system_update(vm)


@pytest.mark.vm_target("fedora-44-server-x86_64")
def test_system_update_server_is_reported_and_nonrestorable(vm):
    verify_system_update(vm)
