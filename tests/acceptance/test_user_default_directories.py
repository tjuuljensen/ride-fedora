"""Fedora 44 lifecycle and recovery for opt-in default user directories."""

import pytest


PROFILE = "/home/ride-test/ride/profiles/fedora-user-default-directories.json"
HOME = "/tmp/ride-user-default-directories"
RIDE = "/home/ride-test/ride/ride.sh"


def user_ride(vm, *args, check=True):
    command = " ".join([RIDE, *args])
    return vm.run(
        f"HOME={HOME} XDG_STATE_HOME={HOME}/state {command}", check=check
    )


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_user_default_directories_lifecycle_and_recovery(vm):
    vm.run(f"rm -rf {HOME} && mkdir -p {HOME}/git && printf 'keep\\n' > {HOME}/git/user-file")
    plan = user_ride(vm, "plan", "--profile", PROFILE)
    assert "setting.user-default-directories" in plan.stdout
    refused = user_ride(vm, "apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    user_ride(vm, "apply", "--profile", PROFILE, "--allow-candidate")
    vm.run(f"test -d {HOME}/bin && test -f {HOME}/git/user-file")
    repeat = user_ride(vm, "apply", "--profile", PROFILE, "--allow-candidate")
    assert "unchanged setting.user-default-directories" in repeat.stdout

    vm.run(f"printf 'user data\\n' > {HOME}/bin/tool")
    refused_remove = user_ride(vm, "remove", "--profile", PROFILE,
                               "--allow-candidate", check=False)
    assert refused_remove.returncode != 0
    vm.run(f"test -f {HOME}/bin/tool && test -f {HOME}/git/user-file")
    vm.run(f"rm {HOME}/bin/tool")
    user_ride(vm, "remove", "--profile", PROFILE, "--allow-candidate")
    vm.run(f"test ! -e {HOME}/bin && test -f {HOME}/git/user-file")

    vm.run(f"ln -s {HOME}/git {HOME}/bin")
    blocked = user_ride(vm, "apply", "--profile", PROFILE,
                        "--allow-candidate", check=False)
    assert blocked.returncode != 0
    vm.run(f"test -L {HOME}/bin && test -f {HOME}/git/user-file")
