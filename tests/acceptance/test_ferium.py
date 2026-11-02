"""Disposable Fedora 44 Server lifecycle for the user-local Ferium CLI."""

import json
import shlex

import pytest


PROFILE = "fedora-server-ferium"
CONFIG = "/home/ride-test/.config/ferium/config.json"
MOD = "/home/ride-test/minecraft/mods/keep.jar"


def user_ride(vm, *args, check=True, timeout=180):
    command = shlex.join([f"{vm.repo}/ride.sh", *args])
    return vm.run(command, check=check, timeout=timeout)


@pytest.mark.vm_target("fedora-44-server-x86_64")
@pytest.mark.recovery("remove-new-install")
def test_ferium_server_candidate_lifecycle_preserves_user_data(vm):
    vm.run("test \"$(id -u)\" != 0")
    vm.run(
        "mkdir -p /home/ride-test/.config/ferium /home/ride-test/minecraft/mods && "
        f"printf '%s\\n' '{{\"profiles\":[\"retained\"]}}' > {CONFIG} && "
        f"printf 'keep existing mod\\n' > {MOD}"
    )
    config_before = vm.run(f"sha256sum {CONFIG}").stdout
    mod_before = vm.run(f"sha256sum {MOD}").stdout

    planned = user_ride(vm, "plan", "--profile", PROFILE)
    assert "package.ferium-portable" in planned.stdout and "candidate" in planned.stdout
    refused = user_ride(vm, "apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    user_ride(vm, "apply", "--profile", PROFILE, "--allow-candidate", timeout=600)

    manifest = json.loads(vm.run(
        "cat /home/ride-test/.local/share/ride-fedora/owned-tools/"
        "package.ferium-portable.json").stdout)
    assert manifest["id"] == "package.ferium-portable"
    assert manifest["version"] == "4.7.1"
    assert len(manifest["archiveSha256"]) == 64
    assert len(manifest["binarySha256"]) == 64
    assert "4.7.1" in vm.run("/home/ride-test/.local/bin/ferium --version").stdout
    assert "package.ferium-portable\tgithub-release-tagged\tinstalled" in user_ride(
        vm, "status", "package.ferium-portable").stdout
    repeated = user_ride(vm, "apply", "--profile", PROFILE, "--allow-candidate")
    assert "unchanged package.ferium-portable" in repeated.stdout

    user_ride(vm, "remove", "--profile", PROFILE, "--allow-candidate")
    vm.run("test ! -e /home/ride-test/.local/bin/ferium")
    vm.run("test ! -e /home/ride-test/.local/share/ride-fedora/owned-tools/"
           "package.ferium-portable.json")
    assert vm.run(f"sha256sum {CONFIG}").stdout == config_before
    assert vm.run(f"sha256sum {MOD}").stdout == mod_before
