"""Yubico Authenticator has an owned user-scoped archive lifecycle."""

import shlex

import pytest

PROFILE = "fedora-yubico-authenticator"


def user_ride(vm, *args, check=True, timeout=180):
    command = shlex.join([f"{vm.repo}/ride.sh", *args])
    return vm.run(command, check=check, timeout=timeout)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
@pytest.mark.recovery("remove-new-install")
def test_yubico_authenticator_owned_archive_lifecycle(vm):
    # Synthetic state and unrelated Applications content must survive install/remove.
    vm.run("mkdir -p ~/.config/yubico-authenticator ~/.local/share/applications ~/Applications")
    vm.run("printf 'keep-me\\n' > ~/.config/yubico-authenticator/recovery-sentinel")
    vm.run("printf 'unrelated\\n' > ~/Applications/unrelated-app.txt")
    vm.run("test \"$(id -u)\" != 0")
    plan = user_ride(vm, "plan", "--profile", PROFILE)
    assert "package.yubico-authenticator" in plan.stdout and "absent" in plan.stdout
    refused = user_ride(vm, "apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    user_ride(vm, "apply", "--profile", PROFILE, "--allow-candidate", timeout=900)
    assert vm.run("test -x ~/.local/opt/ride-fedora/yubico-authenticator/7.4.1/authenticator").returncode == 0
    assert vm.run("test -L ~/.local/bin/yubico-authenticator").returncode == 0
    assert vm.run("test -f ~/.local/share/applications/com.yubico.yubioath.desktop").returncode == 0
    assert vm.run("test -f ~/.local/share/icons/hicolor/256x256/apps/com.yubico.yubioath.png").returncode == 0
    assert vm.run("cat ~/.config/yubico-authenticator/recovery-sentinel").stdout == "keep-me\n"
    assert vm.run("cat ~/Applications/unrelated-app.txt").stdout == "unrelated\n"
    repeated = user_ride(vm, "apply", "--profile", PROFILE, "--allow-candidate", timeout=300)
    assert "unchanged" in repeated.stdout
    assert "package.yubico-authenticator" in user_ride(vm, "status", "package.yubico-authenticator").stdout
    user_ride(vm, "remove", "--profile", PROFILE, "--allow-candidate", timeout=900)
    assert vm.run("test ! -e ~/.local/opt/ride-fedora/yubico-authenticator/7.4.1").returncode == 0
    assert vm.run("test ! -e ~/.local/bin/yubico-authenticator").returncode == 0
    assert vm.run("cat ~/.config/yubico-authenticator/recovery-sentinel").stdout == "keep-me\n"
    assert vm.run("cat ~/Applications/unrelated-app.txt").stdout == "unrelated\n"
