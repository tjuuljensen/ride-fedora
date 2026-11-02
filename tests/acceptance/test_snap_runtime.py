"""Disposable Snap runtime acceptance preserves pre-existing state."""

import json
from pathlib import Path
import re

import pytest


ID = "package.snapd"
SYSTEM_DATA = "/var/lib/snapd/data/ride-sentinel/important.txt"
USER_DATA = "/home/ride-test/snap/ride-sentinel/important.txt"


def data_state(vm, path):
    return vm.run(f"sudo sha256sum {path}").stdout, vm.run(f"sudo stat -c '%u:%g:%a' {path}").stdout


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_snap_runtime_install_only_preserves_state_and_runs_test_snap(vm):
    catalog = json.loads((Path(__file__).resolve().parents[2] / "catalog" / "operations.json").read_text())
    operation = next(item for item in catalog["operations"] if item["id"] == ID)
    assert operation["status"] in {"candidate", "supported"}
    candidate_args = ["--allow-candidate"] if operation["status"] == "candidate" else []

    assert vm.run("rpm -q snapd", check=False).returncode != 0
    vm.run("sudo install -d -m 0700 /var/lib/snapd/data/ride-sentinel")
    vm.run("sudo sh -c \"printf 'keep snap system data\\n' > " + SYSTEM_DATA + "\"")
    vm.run("sudo chmod 0600 " + SYSTEM_DATA)
    vm.run("mkdir -p /home/ride-test/snap/ride-sentinel")
    vm.run("printf 'keep snap user data\\n' > " + USER_DATA)
    vm.run("chmod 0600 " + USER_DATA)
    original_system_data = data_state(vm, SYSTEM_DATA)
    original_user_data = data_state(vm, USER_DATA)
    original_rpms = set(vm.run("rpm -qa --qf '%{NAME}\\n'").stdout.splitlines())
    original_classic_path = vm.run("if test -L /snap; then readlink /snap; elif test -e /snap; then stat -c '%F:%u:%g:%a' /snap; else printf absent; fi").stdout

    planned = vm.ride("plan", "--profile", "snap-runtime")
    assert ID in planned.stdout and "absent" in planned.stdout
    if operation["status"] == "candidate":
        assert "candidate" in planned.stdout
        refused = vm.ride("apply", "--profile", "snap-runtime", check=False)
        assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    changed = vm.ride("apply", "--profile", "snap-runtime", *candidate_args, timeout=1200)
    assert "changed" in changed.stdout
    assert vm.run("rpm -q --qf '%{RSAHEADER:pgpsig}\\n' snapd | grep -qv '(none)'").returncode == 0
    vm.run("rpm -V snapd")
    vm.run("systemctl is-enabled snapd.socket")
    vm.run("snap version", timeout=300)
    vm.run("systemctl is-active snapd.socket")

    install_snap = vm.run("sudo snap install hello-world", timeout=1200)
    assert "hello-world" in install_snap.stdout and "installed" in install_snap.stdout
    hello = vm.run("snap run hello-world", timeout=300)
    assert "Hello World!" in hello.stdout
    snap_info = vm.run("snap info --verbose hello-world").stdout
    assert re.search(r"(?m)^\s*confinement:\s+strict\s*$", snap_info)
    assert vm.run("snap debug confinement").stdout.strip() == "partial"
    assert vm.run("getenforce").stdout.strip() == "Enforcing"

    assert data_state(vm, SYSTEM_DATA) == original_system_data
    assert data_state(vm, USER_DATA) == original_user_data
    current_classic_path = vm.run("if test -L /snap; then readlink /snap; elif test -e /snap; then stat -c '%F:%u:%g:%a' /snap; else printf absent; fi").stdout
    assert current_classic_path == original_classic_path
    assert original_rpms.issubset(set(vm.run("rpm -qa --qf '%{NAME}\\n'").stdout.splitlines()))
    assert "installed" in vm.ride("status", ID).stdout
    repeated = vm.ride("apply", "--profile", "snap-runtime", *candidate_args)
    assert "unchanged" in repeated.stdout
    unavailable_restore = vm.ride(
        "restore", "--run-id", changed.stdout.split("Run ID: ", 1)[1].splitlines()[0], check=False
    )
    assert unavailable_restore.returncode != 0 and "exact recovery is unavailable" in unavailable_restore.stderr
    remove = vm.ride("remove", ID, *candidate_args, check=False)
    assert remove.returncode != 0 and "invalid state absent" in remove.stderr

    vm.run("sudo snap remove hello-world", timeout=300)
    assert data_state(vm, SYSTEM_DATA) == original_system_data
    assert data_state(vm, USER_DATA) == original_user_data
