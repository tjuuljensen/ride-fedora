"""Disposable Fedora 44 system Flathub Halloy package lifecycle."""

import json
import re

import pytest


RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")
APP_ID = "org.squidowl.halloy"
PROFILE = "fedora-irc-halloy"
DATA = "/home/ride-test/.var/app/org.squidowl.halloy/config/keep.txt"
REMOTE_PROFILE = "flathub-system"


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
def test_halloy_flatpak_app_lifecycle_preserves_user_data(vm):
    vm.run("flatpak --version")
    assert not any(app_id(app) == APP_ID for app in apps(vm))
    assert not any(remote.get("name") == "flathub" for remote in remotes(vm))
    vm.run("mkdir -p /home/ride-test/.var/app/org.squidowl.halloy/config")
    vm.run("printf 'keep Halloy user data\\n' > " + DATA)
    vm.run("chmod 0600 " + DATA)
    original = vm.run("sha256sum " + DATA).stdout
    original_mode = vm.run("stat -c '%u:%g:%a' " + DATA).stdout

    remote_plan = vm.ride("plan", "--profile", REMOTE_PROFILE)
    assert "setting.flathub-system-remote" in remote_plan.stdout
    vm.ride("apply", "--profile", REMOTE_PROFILE, "--allow-candidate", timeout=900)
    selected = next(item for item in remotes(vm) if item["name"] == "flathub")
    assert selected["url"] == "https://dl.flathub.org/repo/"
    assert "no-gpg-verify" not in selected["options"]

    planned = vm.ride("plan", "--profile", PROFILE)
    assert "package.halloy" in planned.stdout and "absent" in planned.stdout
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
    assert "package.halloy\tflathub-flatpak\tinstalled" in vm.ride(
        "status", "package.halloy").stdout
    repeated = vm.ride("apply", "--profile", PROFILE, "--allow-candidate")
    assert "unchanged package.halloy" in repeated.stdout

    vm.ride("remove", "--profile", PROFILE, "--allow-candidate", timeout=900)
    assert not any(app_id(app) == APP_ID for app in apps(vm))
    assert vm.run("sha256sum " + DATA).stdout == original
    assert vm.run("stat -c '%u:%g:%a' " + DATA).stdout == original_mode
    assert any(remote.get("name") == "flathub" for remote in remotes(vm))
    assert vm.run("sha256sum " + DATA).stdout == original
