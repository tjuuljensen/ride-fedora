"""Pinned Bitwarden RPM coexists with the AppImage and preserves vault files."""

import shlex

import pytest


PROFILE_RPM = "fedora-bitwarden-rpm"
PROFILE_APPIMAGE = "fedora-bitwarden-appimage"
SENTINEL = "/home/ride-test/.config/Bitwarden/.ride-migration-fixture/rpm-encrypted.json"
APPIMAGE = "/home/ride-test/Applications/Bitwarden-2026.10.1-x86_64.AppImage"
RIDE = "/home/ride-test/ride/ride.sh"


def user_ride(vm, *args, check=True, timeout=180):
    return vm.run(shlex.join([RIDE, *args]), check=check, timeout=timeout)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
@pytest.mark.recovery("remove-new-install")
def test_bitwarden_rpm_coexists_with_appimage_and_preserves_vault(vm):
    assert vm.run("rpm -q --quiet bitwarden", check=False).returncode != 0
    vm.run("mkdir -p /home/ride-test/.config/Bitwarden/.ride-migration-fixture")
    vm.run("printf '%s\\n' 'synthetic encrypted vault fixture' > " + SENTINEL)
    vm.run("chmod 0600 " + SENTINEL)
    vault_hash = vm.run("sha256sum " + SENTINEL).stdout.split()[0]

    user_ride(vm, "apply", "--profile", PROFILE_APPIMAGE)
    appimage_hash = vm.run("sha256sum " + APPIMAGE).stdout.split()[0]
    plan = vm.ride("plan", "--profile", PROFILE_RPM)
    assert "package.bitwarden-rpm" in plan.stdout and "supported" in plan.stdout
    applied = vm.ride("apply", "--profile", PROFILE_RPM, timeout=900)
    assert "package.bitwarden-rpm" in applied.stdout
    assert vm.run("rpm -q bitwarden").returncode == 0
    assert vm.run("test -x " + APPIMAGE).returncode == 0
    assert vm.run("sha256sum " + APPIMAGE).stdout.split()[0] == appimage_hash
    assert vm.run("sha256sum " + SENTINEL).stdout.split()[0] == vault_hash
    assert "package.bitwarden-rpm" in vm.ride("status", "package.bitwarden-rpm").stdout
    repeated = vm.ride("apply", "--profile", PROFILE_RPM)
    assert "unchanged package.bitwarden-rpm" in repeated.stdout

    vm.ride("remove", "--profile", PROFILE_RPM, timeout=600)
    assert vm.run("rpm -q --quiet bitwarden", check=False).returncode != 0
    assert vm.run("test -x " + APPIMAGE).returncode == 0
    assert vm.run("sha256sum " + SENTINEL).stdout.split()[0] == vault_hash
    user_ride(vm, "remove", "--profile", PROFILE_APPIMAGE)
    assert vm.run("test ! -e " + APPIMAGE).returncode == 0
    assert vm.run("sha256sum " + SENTINEL).stdout.split()[0] == vault_hash
