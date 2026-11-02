"""Disposable Fedora 44 Flathub Gear Lever lifecycle and user-data recovery."""

import json
import re

import pytest


RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")
APP_ID = "it.mijorus.gearlever"
PROFILE = "fedora-appimage-manager"
REMOTE_PROFILE = "flathub-system"
DATA = "/home/ride-test/.var/app/it.mijorus.gearlever/config/keep.txt"
APPIMAGE = "/home/ride-test/Applications/legacy-tool.AppImage"
DESKTOP = "/home/ride-test/.local/share/applications/legacy-tool.desktop"


def run_id(output):
    match = RUN_ID.search(output)
    assert match, output
    return match.group(1)


def apps(vm):
    result = vm.run("flatpak list --system --columns=application,origin --json").stdout
    return json.loads(result or "[]")


def app_id(row):
    return row.get("application_id", row.get("application"))


def remotes(vm):
    return json.loads(vm.run(
        "flatpak remotes --system --columns=name,url,options --json").stdout)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_gearlever_flatpak_lifecycle_preserves_existing_appimages_and_user_state(vm):
    vm.run("flatpak --version")
    legacy_package = vm.run("rpm -q --quiet appimagelauncher", check=False)
    assert legacy_package.returncode != 0, "legacy AppImageLauncher RPM must be removed before Gear Lever"
    assert not any(app_id(app) == APP_ID for app in apps(vm))
    assert not any(remote.get("name") == "flathub" for remote in remotes(vm))
    vm.run("mkdir -p /home/ride-test/.var/app/it.mijorus.gearlever/config")
    vm.run("mkdir -p /home/ride-test/Applications /home/ride-test/.local/share/applications")
    vm.run("printf 'keep Gear Lever profile\\n' > " + DATA)
    vm.run("printf 'legacy AppImage bytes\\n' > " + APPIMAGE)
    vm.run("printf '[Desktop Entry]\\nName=Legacy Tool\\nExec=/home/ride-test/Applications/legacy-tool.AppImage\\n' > " + DESKTOP)
    vm.run("chmod 0600 " + DATA + " " + APPIMAGE + " " + DESKTOP)
    originals = {
        path: vm.run("sha256sum " + path).stdout for path in (DATA, APPIMAGE, DESKTOP)
    }
    modes = {
        path: vm.run("stat -c '%u:%g:%a' " + path).stdout for path in (DATA, APPIMAGE, DESKTOP)
    }

    remote_plan = vm.ride("plan", "--profile", REMOTE_PROFILE)
    assert "setting.flathub-system-remote" in remote_plan.stdout
    vm.ride("apply", "--profile", REMOTE_PROFILE, "--allow-candidate", timeout=900)
    selected = next(item for item in remotes(vm) if item["name"] == "flathub")
    assert selected["url"] == "https://dl.flathub.org/repo/"
    assert "no-gpg-verify" not in selected["options"]

    planned = vm.ride("plan", "--profile", PROFILE)
    assert "package.gearlever" in planned.stdout and "absent" in planned.stdout
    assert "candidate" in planned.stdout
    refused = vm.ride("apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    applied = vm.ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=1200)
    identifier = run_id(applied.stdout)
    record = json.loads(vm.run(
        f"sudo cat /var/lib/ride-fedora/runs/{identifier}.json").stdout)
    assert record["status"] == "complete"
    assert record["steps"][0]["result"] == "changed"
    installed = [app for app in apps(vm) if app_id(app) == APP_ID]
    assert len(installed) == 1 and installed[0]["origin"] == "flathub"
    assert "package.gearlever\tflathub-flatpak\tinstalled" in vm.ride(
        "status", "package.gearlever").stdout
    help_result = vm.run(f"flatpak run --system {APP_ID} --help", check=False)
    assert help_result.returncode == 0, help_result.stderr
    repeated = vm.ride("apply", "--profile", PROFILE, "--allow-candidate")
    assert "unchanged package.gearlever" in repeated.stdout

    vm.ride("remove", "--profile", PROFILE, "--allow-candidate", timeout=900)
    assert not any(app_id(app) == APP_ID for app in apps(vm))
    for path in (DATA, APPIMAGE, DESKTOP):
        assert vm.run("sha256sum " + path).stdout == originals[path]
        assert vm.run("stat -c '%u:%g:%a' " + path).stdout == modes[path]
    assert vm.run("test -d /home/ride-test/Applications").returncode == 0
    assert any(remote.get("name") == "flathub" for remote in remotes(vm))
