"""Pinned Volatility 2 and PyPy bundle lifecycle on Fedora 44 Workstation."""

import hashlib
import shlex

import pytest


PROFILE = "fedora-volatility2"
BUNDLE = "/home/ride-test/.local/share/ride-fedora/tools/volatility2"
SENTINEL = "/home/ride-test/.local/share/volatility2-unrelated.txt"


def user_ride(vm, *args, check=True, timeout=180):
    return vm.run(shlex.join([f"{vm.repo}/ride.sh", *args]), check=check, timeout=timeout)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
@pytest.mark.recovery("remove-new-install")
def test_volatility2_pypy_bundle_lifecycle(vm):
    vm.run("mkdir -p /home/ride-test/.local/share")
    vm.run(f"printf 'keep this file\\n' > {SENTINEL}")
    before = hashlib.sha256(vm.run(f"cat {SENTINEL}").stdout.encode()).hexdigest()
    refused = user_ride(vm, "apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0
    assert "--allow-candidate" in refused.stdout + refused.stderr
    assert vm.run(f"test ! -e {BUNDLE}").returncode == 0

    plan = user_ride(vm, "plan", "--profile", PROFILE, "--allow-candidate")
    assert "package.volatility2" in plan.stdout
    user_ride(vm, "apply", "--profile", PROFILE, "--allow-candidate", timeout=1200)
    info = vm.run(f"{BUNDLE}/bin/vol2 --info", check=False)
    assert info.returncode == 0
    assert "Volatility Foundation Volatility Framework 2.6.1" in info.stdout + info.stderr
    assert "package.volatility2" in user_ride(vm, "status", "package.volatility2").stdout
    repeated = user_ride(vm, "apply", "--profile", PROFILE, "--allow-candidate")
    assert "unchanged package.volatility2" in repeated.stdout

    user_ride(vm, "remove", "--profile", PROFILE, "--allow-candidate")
    assert vm.run(f"test ! -e {BUNDLE}").returncode == 0
    after = hashlib.sha256(vm.run(f"cat {SENTINEL}").stdout.encode()).hexdigest()
    assert after == before
