"""CubeCoders AMP manager RPM source, candidate gate, and package recovery."""

import pytest


PROFILE = "fedora-server-amp"


@pytest.mark.vm_target("fedora-44-server-x86_64")
@pytest.mark.recovery("remove-new-install")
def test_amp_manager_rpm_preserves_operator_home_and_firewall(vm):
    vm.run("! rpm -q --quiet ampinstmgr")
    vm.run("! id amp >/dev/null 2>&1 && sudo test ! -e /home/amp")
    vm.run("sudo useradd --create-home --shell /bin/bash amp")
    amp_uid = vm.run("id -u amp").stdout.strip()
    amp_gid = vm.run("id -g amp").stdout.strip()
    marker = "/home/amp/.ampdata/instances/private-amp/ride-v3-preserve.marker"
    vm.run(f"sudo install -d -o amp -g amp -m 0750 /home/amp/.ampdata/instances/private-amp")
    vm.run(f"printf 'private AMP state seed\\n' | sudo -u amp tee '{marker}' >/dev/null")
    vm.run(f"sudo sha256sum '{marker}' > /home/ride-test/amp-state.before")
    firewall_before = vm.run("sudo firewall-cmd --list-all-zones").stdout

    plan = vm.ride("plan", "--profile", PROFILE)
    assert "package.amp-installer" in plan.stdout
    refused = vm.ride("apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    applied = vm.ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=1800)
    run_id = applied.stdout.split("Run ID: ", 1)[1].splitlines()[0]

    vm.run("rpm -q ampinstmgr")
    vm.run("sudo test -x /opt/cubecoders/amp/ampinstmgr")
    vm.run("sudo test -e /etc/systemd/system/ampfirewall.timer")
    for unit in ("ampinstmgr.service", "ampfirewall.service", "ampfirewall.timer",
                 "amptasks.service", "amptasks.timer"):
        vm.run(f"! sudo systemctl is-enabled --quiet {unit}")
        vm.run(f"! sudo systemctl is-active --quiet {unit}")
    vm.run("test \"$(id -u amp)\" = " + amp_uid)
    vm.run("test \"$(id -g amp)\" = " + amp_gid)
    vm.run(f"sudo sha256sum -c /home/ride-test/amp-state.before")
    assert vm.run("sudo firewall-cmd --list-all-zones").stdout == firewall_before

    repeated = vm.ride("apply", "--profile", PROFILE, "--allow-candidate")
    assert "unchanged" in repeated.stdout
    assert "package.amp-installer" in vm.ride("status", "package.amp-installer").stdout
    vm.ride("restore", "--run-id", run_id, "--allow-candidate", timeout=1800)

    vm.run("! rpm -q --quiet ampinstmgr")
    for path in ("/opt/cubecoders", "/etc/systemd/system/ampinstmgr.service",
                 "/etc/systemd/system/ampfirewall.service", "/etc/systemd/system/ampfirewall.timer",
                 "/etc/systemd/system/amptasks.service", "/etc/systemd/system/amptasks.timer"):
        vm.run(f"sudo test ! -e {path}")
    vm.run("test \"$(id -u amp)\" = " + amp_uid)
    vm.run("test \"$(id -g amp)\" = " + amp_gid)
    vm.run(f"sudo sha256sum -c /home/ride-test/amp-state.before")
    assert vm.run("sudo firewall-cmd --list-all-zones").stdout == firewall_before
