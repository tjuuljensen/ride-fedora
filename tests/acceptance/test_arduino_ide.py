"""Install and remove the pinned Arduino IDE AppImage without touching sketches."""

import re
import shlex

import pytest


PROFILE = "fedora-arduino-ide"
APPIMAGE = "/home/ride-test/Applications/arduino-ide_2.3.10_Linux_64bit.AppImage"
MANIFEST = "/home/ride-test/.local/share/ride-fedora/owned-tools/package.arduino-ide.json"
SKETCH = "/home/ride-test/Documents/Arduino/acceptance-sketch.ino"
SOURCE_SHA = "79c8590a1744c220d72cbed0ea91c6e2a7f4594292699b2fb3364ebd713cd566"
JOPLIN_PROFILE = "fedora-joplin"
JOPLIN_APPIMAGE = "/home/ride-test/Applications/Joplin-3.7.22.AppImage"
JOPLIN_MANIFEST = "/home/ride-test/.local/share/ride-fedora/owned-tools/package.joplin.json"
JOPLIN_STATE = "/home/ride-test/.config/joplin-desktop/ride-preserved-state.txt"
JOPLIN_SOURCE_SHA = "2b0b1ee82999f00883d21d950c2fb5dff28ccc3d2f570248b3abd40e5100dfdc"
RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")


def run_id(output):
    match = RUN_ID.search(output)
    assert match, output
    return match.group(1)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_arduino_ide_private_appimage_lifecycle(vm):
    vm.run(f"mkdir -p /home/ride-test/Documents/Arduino && printf 'keep sketch\\n' > {SKETCH}")
    vm.run(f"test ! -e {APPIMAGE} && test ! -e {MANIFEST}")

    def user_ride(*args, timeout=180, check=True):
        return vm.run(shlex.join((f"{vm.repo}/ride.sh", *args)), timeout=timeout, check=check)

    plan = user_ride("plan", "--profile", PROFILE)
    assert "package.arduino-ide" in plan.stdout
    gate = user_ride("apply", "--profile", PROFILE, check=False)
    assert gate.returncode != 0 and "--allow-candidate" in gate.stderr
    applied = user_ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=600)
    operation_run = run_id(applied.stdout)
    assert "package.arduino-ide" in applied.stdout
    vm.run(f"test -x {APPIMAGE} && test -f {MANIFEST}")
    digest = vm.run(f"sha256sum {APPIMAGE}").stdout.split()[0]
    assert digest == SOURCE_SHA
    vm.run(f"test \"$(head -c4 {APPIMAGE})\" = \"$(printf '\\177ELF')\"")
    vm.run(f"{APPIMAGE} --appimage-version", timeout=90)
    assert "package.arduino-ide\tgithub-release-pinned\tinstalled" in user_ride(
        "status", "package.arduino-ide").stdout
    repeated = user_ride("apply", "--profile", PROFILE, "--allow-candidate")
    assert "unchanged" in repeated.stdout
    user_ride("restore", "--run-id", operation_run, "--allow-candidate")
    vm.run(f"test ! -e {APPIMAGE} && test ! -e {MANIFEST} && test \"$(cat {SKETCH})\" = 'keep sketch'")
    user_ride("install", "package.arduino-ide", "--allow-candidate", timeout=600)
    user_ride("remove", "package.arduino-ide", "--allow-candidate")
    vm.run(f"test ! -e {APPIMAGE} && test ! -e {MANIFEST} && test \"$(cat {SKETCH})\" = 'keep sketch'")

    vm.run(f"mkdir -p /home/ride-test/.config/joplin-desktop && printf 'keep notebook state\\n' > {JOPLIN_STATE}")
    vm.run(f"test ! -e {JOPLIN_APPIMAGE} && test ! -e {JOPLIN_MANIFEST}")
    joplin_plan = user_ride("plan", "--profile", JOPLIN_PROFILE)
    assert "package.joplin" in joplin_plan.stdout
    joplin_gate = user_ride("apply", "--profile", JOPLIN_PROFILE, check=False)
    assert joplin_gate.returncode != 0 and "--allow-candidate" in joplin_gate.stderr
    joplin_applied = user_ride("apply", "--profile", JOPLIN_PROFILE,
                               "--allow-candidate", timeout=600)
    joplin_run = run_id(joplin_applied.stdout)
    assert vm.run(f"sha256sum {JOPLIN_APPIMAGE}").stdout.split()[0] == JOPLIN_SOURCE_SHA
    vm.run(f"{JOPLIN_APPIMAGE} --appimage-version", timeout=90)
    assert "package.joplin\tgithub-release-pinned\tinstalled" in user_ride(
        "status", "package.joplin").stdout
    joplin_repeat = user_ride("apply", "--profile", JOPLIN_PROFILE, "--allow-candidate")
    assert "unchanged" in joplin_repeat.stdout
    user_ride("restore", "--run-id", joplin_run, "--allow-candidate")
    vm.run(f"test ! -e {JOPLIN_APPIMAGE} && test ! -e {JOPLIN_MANIFEST} && test \"$(cat {JOPLIN_STATE})\" = 'keep notebook state'")
    user_ride("install", "package.joplin", "--allow-candidate", timeout=600)
    user_ride("remove", "package.joplin", "--allow-candidate")
    vm.run(f"test ! -e {JOPLIN_APPIMAGE} && test ! -e {JOPLIN_MANIFEST} && test \"$(cat {JOPLIN_STATE})\" = 'keep notebook state'")
