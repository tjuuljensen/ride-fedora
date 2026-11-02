"""Disposable Fedora 44 user-local Eza release install with RPM coexistence."""

import json
import shlex

import pytest

PROFILE = "fedora-eza-portable"
DATA = "/home/ride-test/.local/share/ride-fedora/owned-tools/keep.txt"


def user_ride(vm, *args, check=True, timeout=180):
    command = shlex.join([f"{vm.repo}/ride.sh", *args])
    return vm.run(command, check=check, timeout=timeout)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
@pytest.mark.recovery("remove-new-install")
def test_eza_portable_pinned_user_install_coexists_with_fedora_rpm(vm):
    vm.run("test \"$(id -u)\" != 0")
    system_was_installed = vm.run("rpm -q --quiet eza", check=False).returncode == 0
    if not system_was_installed:
        vm.run("sudo dnf install -y eza", timeout=600)
    vm.run("mkdir -p /home/ride-test/.local/share/ride-fedora/owned-tools")
    vm.run("printf 'keep user data\\n' > " + DATA)
    vm.run("chmod 0600 " + DATA)
    before_data = vm.run("sha256sum " + DATA).stdout
    before_mode = vm.run("stat -c '%u:%g:%a' " + DATA).stdout
    rpm_before = vm.run("rpm -q eza").stdout

    planned = user_ride(vm, "plan", "--profile", PROFILE)
    assert "package.eza-portable" in planned.stdout and "candidate" in planned.stdout
    refused = user_ride(vm, "apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    user_ride(vm, "apply", "--profile", PROFILE, "--allow-candidate", timeout=600)

    manifest = json.loads(vm.run(
        "cat /home/ride-test/.local/share/ride-fedora/owned-tools/package.eza-portable.json").stdout)
    assert manifest["id"] == "package.eza-portable" and manifest["version"] == "0.23.5"
    version = vm.run("/home/ride-test/.local/bin/eza --version").stdout
    assert "0.23.5" in version
    assert "package.eza-portable\tgithub-release-pinned\tinstalled" in user_ride(
        vm, "status", "package.eza-portable").stdout
    repeated = user_ride(vm, "apply", "--profile", PROFILE, "--allow-candidate")
    assert "unchanged package.eza-portable" in repeated.stdout

    user_ride(vm, "remove", "--profile", PROFILE, "--allow-candidate")
    vm.run("test ! -e /home/ride-test/.local/bin/eza")
    vm.run("test ! -e /home/ride-test/.local/share/ride-fedora/owned-tools/package.eza-portable.json")
    assert vm.run("rpm -q eza").stdout == rpm_before
    assert vm.run("sha256sum " + DATA).stdout == before_data
    assert vm.run("stat -c '%u:%g:%a' " + DATA).stdout == before_mode
    if not system_was_installed:
        vm.run("sudo dnf remove -y eza", timeout=600)
