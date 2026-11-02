"""Fedora authselect mDNS feature and exact recovery acceptance."""

import pytest


PROFILE = "fedora-multicast-dns-disabled"
OPERATION = "setting.multicast-dns"


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_multicast_dns_authselect_lifecycle_and_exact_restore(vm):
    ride = f"{vm.repo}/ride.sh"
    vm.run("authselect check")
    before = vm.run("authselect current --raw").stdout.strip()
    assert "with-mdns4" in before.split()
    vm.run("authselect current --raw > /tmp/ride-mdns-before-profile")
    vm.run("grep '^hosts:' /etc/nsswitch.conf > /tmp/ride-mdns-before-hosts")

    planned = vm.ride("plan", "--profile", PROFILE)
    assert OPERATION in planned.stdout
    refused = vm.ride("apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    applied = vm.ride("apply", "--profile", PROFILE, "--allow-candidate")
    run_id = applied.stdout.split("Run ID: ", 1)[1].splitlines()[0]
    managed = vm.run("authselect current --raw").stdout.strip()
    assert "with-mdns4" not in managed.split()
    assert "disabled" in vm.ride("status", OPERATION).stdout
    vm.run("authselect check")
    vm.run("grep '^hosts:' /etc/nsswitch.conf | grep -q 'files.*resolve.*dns'")
    vm.run("! grep '^hosts:' /etc/nsswitch.conf | grep -q mdns4_minimal")
    vm.run("getent hosts localhost")

    repeated = vm.ride("apply", "--profile", PROFILE, "--allow-candidate")
    assert "unchanged setting.multicast-dns" in repeated.stdout

    # An unrelated authselect feature change makes the owned selection differ;
    # restore must refuse until that external change is returned to its baseline.
    vm.run("sudo authselect enable-feature with-mdns6")
    conflict = vm.ride("restore", "--run-id", run_id, "--allow-candidate", check=False)
    assert conflict.returncode != 0 and "changed outside RIDE" in conflict.stderr
    vm.run("sudo authselect disable-feature with-mdns6")
    vm.ride("restore", "--run-id", run_id, "--allow-candidate")
    vm.run("cmp /tmp/ride-mdns-before-profile <(authselect current --raw)")
    vm.run("cmp /tmp/ride-mdns-before-hosts <(grep '^hosts:' /etc/nsswitch.conf)")
    vm.run("authselect check")
    assert "enabled" in vm.ride("status", OPERATION).stdout
