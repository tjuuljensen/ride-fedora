"""Fedora system hostname operation preserves the prior static name."""

import shlex

import pytest


def run_hostname_lifecycle(vm):
    original = vm.run("sudo hostnamectl --static").stdout.strip()
    assert original
    target = "ride-v3-hostname-pilot.example"
    applied = vm.run(f"sudo {vm.repo}/ride.sh set setting.hostname --state configured --value {target}")
    assert vm.run("sudo hostnamectl --static").stdout.strip() == target
    status = vm.run(f"sudo {vm.repo}/ride.sh status setting.hostname").stdout
    assert f"hostname:{target}" in status
    repeated = vm.run(f"sudo {vm.repo}/ride.sh set setting.hostname --state configured --value {target}")
    assert "unchanged setting.hostname" in repeated.stdout
    run_id = applied.stdout.split("Run ID: ", 1)[1].splitlines()[0]
    vm.run(f"sudo {vm.repo}/ride.sh restore --run-id {shlex.quote(run_id)}")
    assert vm.run("sudo hostnamectl --static").stdout.strip() == original


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_workstation_private_hostname_value_restores_exactly(vm):
    run_hostname_lifecycle(vm)


@pytest.mark.vm_target("fedora-44-server-x86_64")
def test_server_private_hostname_value_restores_exactly(vm):
    run_hostname_lifecycle(vm)
