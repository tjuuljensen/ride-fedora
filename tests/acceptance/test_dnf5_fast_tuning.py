"""Fedora DNF5 tuning candidate lifecycle acceptance."""

import shlex

import pytest


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_owned_dnf5_tuning_profile_applies_repeats_and_restores(vm):
    vm.run("command -v dnf5 && test -d /etc/dnf/libdnf5.conf.d")
    before = vm.run("sudo dnf5 --dump-main-config", check=False).stdout
    assert "fastestmirror" in before
    plan = vm.run(f"{vm.repo}/ride.sh plan --profile fedora-fast-dnf")
    assert "setting.dnf5-fast-tuning" in plan.stdout
    refused = vm.run(f"{vm.repo}/ride.sh apply --profile fedora-fast-dnf", check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    applied = vm.run(f"sudo {vm.repo}/ride.sh apply --profile fedora-fast-dnf --allow-candidate")
    assert "configured" in vm.run(f"sudo {vm.repo}/ride.sh status setting.dnf5-fast-tuning").stdout
    effective = vm.run("sudo dnf5 --dump-main-config").stdout
    assert "fastestmirror = 1" in effective
    assert "max_parallel_downloads = 15" in effective
    repeated = vm.run(f"sudo {vm.repo}/ride.sh apply --profile fedora-fast-dnf --allow-candidate")
    assert "unchanged setting.dnf5-fast-tuning" in repeated.stdout
    run_id = applied.stdout.split("Run ID: ", 1)[1].splitlines()[0]
    vm.run(f"sudo {vm.repo}/ride.sh restore --run-id {shlex.quote(run_id)} --allow-candidate")
    assert "absent" in vm.run(f"sudo {vm.repo}/ride.sh status setting.dnf5-fast-tuning").stdout
    assert vm.run("sudo test ! -e /etc/dnf/libdnf5.conf.d/99-ride-fastdnf.conf", check=False).returncode == 0
