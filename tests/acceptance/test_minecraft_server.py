"""Disposable Fedora 44 Server lifecycle for the official Minecraft JAR."""

import json
import shlex

import pytest


PROFILE = "fedora-server-minecraft-server"
RUNTIME_PROFILE = "fedora-server-java-25-runtime"
WORLD = "/home/ride-test/minecraft/world/level.dat"
CONFIG = "/home/ride-test/minecraft/server.properties"
EULA = "/home/ride-test/minecraft/eula.txt"


def user_ride(vm, *args, check=True, timeout=240, sudo=False):
    prefix = ["sudo"] if sudo else []
    command = shlex.join([*prefix, f"{vm.repo}/ride.sh", *args])
    return vm.run(command, check=check, timeout=timeout)


@pytest.mark.vm_target("fedora-44-server-x86_64")
@pytest.mark.recovery("remove-new-install")
def test_minecraft_server_artifact_install_preserves_world_state(vm):
    vm.run("test \"$(id -u)\" != 0")
    vm.run(
        "mkdir -p /home/ride-test/minecraft/world && "
        f"printf 'seeded world data\\n' > {WORLD} && "
        f"printf 'level-name=world\\n' > {CONFIG} && "
        f"printf 'eula=false\\n' > {EULA}"
    )
    before = [vm.run(f"sha256sum {path}").stdout for path in (WORLD, CONFIG, EULA)]

    runtime_refused = user_ride(vm, "apply", "--profile", RUNTIME_PROFILE, check=False, sudo=True)
    assert runtime_refused.returncode != 0 and "--allow-candidate" in runtime_refused.stderr
    user_ride(vm, "apply", "--profile", RUNTIME_PROFILE, "--allow-candidate",
              timeout=900, sudo=True)

    planned = user_ride(vm, "plan", "--profile", PROFILE)
    assert "package.minecraft-server" in planned.stdout
    refused = user_ride(vm, "apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    user_ride(vm, "apply", "--profile", PROFILE, "--allow-candidate", timeout=900)

    assert "openjdk version \"25" in vm.run("java -version").stderr.lower() or \
        "openjdk 25" in vm.run("java -version").stderr.lower()
    jar = "/home/ride-test/.local/opt/ride-fedora/minecraft-server/26.3/server.jar"
    manifest_path = "/home/ride-test/.local/opt/ride-fedora/minecraft-server/26.3/.ride-owned"
    manifest = json.loads(vm.run(f"cat {manifest_path}").stdout)
    assert manifest["id"] == "package.minecraft-server"
    assert manifest["version"] == "26.3"
    assert manifest["sourceSha1"] == "33680f5f2ac32864d6d7cf5e56a705fdb3e05f4c"
    assert len(manifest["sha256"]) == 64
    vm.run(
        "python3 -c 'import zipfile,sys; "
        f"assert zipfile.is_zipfile(sys.argv[1])' {shlex.quote(jar)}"
    )
    assert "package.minecraft-server\tmojang-server-pinned\tinstalled" in user_ride(
        vm, "status", "package.minecraft-server").stdout
    repeat = user_ride(vm, "apply", "--profile", PROFILE, "--allow-candidate")
    assert "unchanged package.minecraft-server" in repeat.stdout

    runtime_repeat = user_ride(vm, "apply", "--profile", RUNTIME_PROFILE,
                               "--allow-candidate", sudo=True)
    assert "unchanged package.java-25-openjdk-headless" in runtime_repeat.stdout
    user_ride(vm, "remove", "--profile", PROFILE, "--allow-candidate")
    vm.run(f"test ! -e {jar} && test ! -e {manifest_path}")
    user_ride(vm, "remove", "--profile", RUNTIME_PROFILE, "--allow-candidate",
              timeout=900, sudo=True)
    assert [vm.run(f"sha256sum {path}").stdout for path in (WORLD, CONFIG, EULA)] == before
