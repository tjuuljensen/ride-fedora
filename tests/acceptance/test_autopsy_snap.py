"""Autopsy Snap package lifecycle, interface state, and snapshot recovery."""

import pytest


PROFILE = "fedora-autopsy"
CASE_SENTINEL = "/home/ride-test/Documents/ride-autopsy-case-preserve.txt"
SNAP_SENTINEL = "/home/ride-test/snap/autopsy/common/ride-acceptance.txt"


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_autopsy_snap_lifecycle_and_snapshot_recovery(vm):
    vm.ride("apply", "--profile", "snap-runtime", "--allow-candidate", timeout=1200)
    vm.run("systemctl is-active snapd.socket && snap version", timeout=300)
    vm.run("mkdir -p /home/ride-test/Documents")
    vm.run(f"printf 'case output sentinel\\n' > {CASE_SENTINEL}")
    original_case = vm.run(f"sha256sum {CASE_SENTINEL}").stdout.split()[0]

    plan = vm.ride("plan", "--profile", PROFILE)
    assert "package.autopsy" in plan.stdout and "candidate" in plan.stdout
    refused = vm.ride("apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    vm.ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=1500)
    vm.run("snap info autopsy | grep -F 'Sleuth Kit Labs'")
    vm.run("snap list autopsy | grep -F autopsy")
    vm.run("snap connections autopsy > /tmp/autopsy-connections.txt")
    connection_table = vm.run("cat /tmp/autopsy-connections.txt").stdout
    assert "Interface" in connection_table and "block-devices" in connection_table
    connections = {}
    for line in connection_table.splitlines()[1:]:
        fields = line.split()
        if len(fields) >= 3:
            connections.setdefault(fields[0], []).append(fields[2])
    # The Snap Store publisher has explicit auto-connect grants for these
    # otherwise super-privileged interfaces. Record that actual exposure.
    for interface in ("block-devices", "dm-crypt", "fuse-support"):
        assert connections[interface] == [f":{interface}"]
    assert connections["system-files"] == ["-", "-"]

    vm.run("mkdir -p /home/ride-test/snap/autopsy/common")
    vm.run(f"printf 'snap app state sentinel\\n' > {SNAP_SENTINEL}")
    vm.ride("remove", "--profile", PROFILE, "--allow-candidate", timeout=900)
    assert vm.run("snap list autopsy", check=False).returncode != 0
    saved = vm.run("sudo snap saved").stdout
    snapshot_id = next(line.split()[0] for line in saved.splitlines()
                       if len(line.split()) >= 7 and line.split()[1] == "autopsy" and line.split()[6] == "auto")
    assert vm.run(f"sha256sum {CASE_SENTINEL}").stdout.split()[0] == original_case
    assert vm.run(f"test ! -e {SNAP_SENTINEL}", check=False).returncode == 0

    vm.ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=1200)
    vm.run(f"sudo snap restore {snapshot_id} autopsy", timeout=300)
    assert vm.run(f"cat {SNAP_SENTINEL}").stdout.strip() == "snap app state sentinel"
    assert vm.run(f"sha256sum {CASE_SENTINEL}").stdout.split()[0] == original_case
    vm.ride("remove", "--profile", PROFILE, "--allow-candidate", timeout=900)
