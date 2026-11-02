"""Disposable Fedora 44 user-local LibreSpeed CLI lifecycle; no speed test."""

import json
import shlex

import pytest

PROFILE = "fedora-network-librespeed-cli"
DATA = "/home/ride-test/.local/share/ride-fedora/owned-tools/keep.txt"


def user_ride(vm, *args, check=True, timeout=120):
    command = shlex.join([f"{vm.repo}/ride.sh", *args])
    return vm.run(command, check=check, timeout=timeout)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_librespeed_cli_pinned_user_install_lifecycle(vm):
    vm.run("test \"$(id -u)\" != 0")
    before_rpm = vm.run("rpm -q speedtest-cli", check=False).stdout
    vm.run("mkdir -p /home/ride-test/.local/share/ride-fedora/owned-tools")
    vm.run("printf 'keep user data\\n' > " + DATA)
    vm.run("chmod 0600 " + DATA)
    before_data = vm.run("sha256sum " + DATA).stdout
    before_mode = vm.run("stat -c '%u:%g:%a' " + DATA).stdout

    planned = user_ride(vm, "plan", "--profile", PROFILE)
    assert "package.librespeed-cli" in planned.stdout and "candidate" in planned.stdout
    refused = user_ride(vm, "apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    applied = user_ride(vm, "apply", "--profile", PROFILE, "--allow-candidate", timeout=600)
    installed = json.loads(vm.run(
        "cat /home/ride-test/.local/share/ride-fedora/owned-tools/package.librespeed-cli.json").stdout)
    assert installed["id"] == "package.librespeed-cli" and installed["version"] == "1.0.14"
    assert vm.run("/home/ride-test/.local/bin/librespeed-cli --version").stdout.lower().find("1.0.14") >= 0
    assert "package.librespeed-cli\tgithub-release-pinned\tinstalled" in user_ride(
        vm, "status", "package.librespeed-cli").stdout
    repeated = user_ride(vm, "apply", "--profile", PROFILE, "--allow-candidate")
    assert "unchanged package.librespeed-cli" in repeated.stdout

    user_ride(vm, "remove", "--profile", PROFILE, "--allow-candidate")
    vm.run("test ! -e /home/ride-test/.local/bin/librespeed-cli")
    vm.run("test ! -e /home/ride-test/.local/share/ride-fedora/owned-tools/package.librespeed-cli.json")
    assert vm.run("sha256sum " + DATA).stdout == before_data
    assert vm.run("stat -c '%u:%g:%a' " + DATA).stdout == before_mode
    assert vm.run("rpm -q speedtest-cli", check=False).stdout == before_rpm
    assert "package.librespeed-cli" in applied.stdout
