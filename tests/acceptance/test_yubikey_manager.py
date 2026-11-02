"""The Fedora ykman package has an owned package-only lifecycle."""

import pytest


PROFILE = "fedora-yubikey-tools"


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
@pytest.mark.recovery("remove-new-install")
def test_yubikey_manager_cli_package_lifecycle(vm):
    # This runs only in a disposable overlay. Do not contact or mutate a key.
    vm.run("if rpm -q --quiet yubikey-manager; then sudo rpm -e yubikey-manager; fi")
    plan = vm.ride("plan", "--profile", PROFILE)
    assert "package.yubikey-manager" in plan.stdout
    assert "absent" in plan.stdout
    vm.ride("apply", "--profile", PROFILE, timeout=900)
    assert vm.run("rpm -q --quiet yubikey-manager").returncode == 0
    version = vm.run("ykman --version")
    assert version.returncode == 0 and "5." in version.stdout
    repeated = vm.ride("apply", "--profile", PROFILE, timeout=300)
    assert "unchanged" in repeated.stdout
    assert "package.yubikey-manager" in vm.ride("status", "package.yubikey-manager").stdout
    vm.ride("remove", "--profile", PROFILE, timeout=900)
    assert vm.run("rpm -q --quiet yubikey-manager", check=False).returncode != 0
