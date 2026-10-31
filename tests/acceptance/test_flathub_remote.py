"""Disposable system Flathub remote ownership and recovery lifecycle."""

import json
import re

import pytest


RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")
REMOTE = "https://dl.flathub.org/repo/"
ID = "setting.flathub-system-remote"


def run_id(output):
    match = RUN_ID.search(output)
    assert match, output
    return match.group(1)


def remotes(vm, scope):
    return json.loads(vm.run(f"flatpak remotes --{scope} --columns=name,url,options --json").stdout)


def applications(vm, scope):
    output = vm.run(f"flatpak list --{scope} --columns=application,origin --json").stdout
    return json.loads(output or "[]")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_flathub_system_remote_owned_lifecycle(vm):
    vm.run("flatpak --version")
    before_system = remotes(vm, "system")
    before_user = remotes(vm, "user")
    before_apps = applications(vm, "system")
    assert not any(item["name"] == "flathub" for item in before_system), before_system
    assert not any(item.get("origin") == "flathub" for item in before_apps), before_apps

    planned = vm.ride("plan", "--profile", "flathub-system")
    assert ID in planned.stdout and "absent" in planned.stdout and "candidate" in planned.stdout
    refused = vm.ride("apply", "--profile", "flathub-system", check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr

    changed = vm.ride("apply", "--profile", "flathub-system", "--allow-candidate", timeout=900)
    identifier = run_id(changed.stdout)
    record = json.loads(vm.run(f"sudo cat /var/lib/ride-fedora/runs/{identifier}.json").stdout)
    assert record["status"] == "complete"
    assert record["steps"][0]["id"] == ID
    assert record["steps"][0]["result"] == "changed"
    current = remotes(vm, "system")
    selected = [item for item in current if item["name"] == "flathub"]
    assert len(selected) == 1
    assert selected[0]["url"] == REMOTE
    assert "no-gpg-verify" not in selected[0]["options"]
    assert applications(vm, "system") == before_apps
    assert remotes(vm, "user") == before_user
    assert "configured" in vm.ride("status", ID).stdout

    repeated = vm.ride("apply", "--profile", "flathub-system", "--allow-candidate")
    assert "unchanged" in repeated.stdout
    vm.ride("restore", "--run-id", identifier, "--dry-run")
    vm.ride("restore", "--run-id", identifier, "--allow-candidate")
    assert remotes(vm, "system") == before_system
    assert remotes(vm, "user") == before_user
    assert applications(vm, "system") == before_apps

    vm.ride("apply", "--profile", "flathub-system", "--allow-candidate", timeout=900)
    vm.ride("remove", "--profile", "flathub-system", "--allow-candidate")
    assert remotes(vm, "system") == before_system
    assert remotes(vm, "user") == before_user
    assert applications(vm, "system") == before_apps
