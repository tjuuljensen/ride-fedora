"""Configurable GNOME favorite list apply and exact recovery on Fedora 44."""

import json
import re
import shlex

import pytest


RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")


def user_ride(vm, *args, check=True):
    return vm.run("dbus-run-session -- " + shlex.join([f"{vm.repo}/ride.sh", *args]), check=check)


def gsettings(vm, *args):
    return vm.run("dbus-run-session -- " + shlex.join(["gsettings", *args])).stdout.strip()


def dconf(vm):
    return vm.run("dbus-run-session -- dconf read /org/gnome/shell/favorite-apps").stdout.strip()


def run_journal(vm, output):
    match = RUN_ID.search(output)
    assert match, output
    return json.loads(vm.run(
        f"cat /home/ride-test/.local/state/ride-fedora/runs/{match.group(1)}.json"
    ).stdout)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_configurable_favorites_preserve_and_restore_exact_list(vm):
    vm.run("sudo dnf -y install dbus-daemon", timeout=900)
    vm.run("command -v dbus-run-session && command -v gsettings && command -v dconf")
    schema, key = "org.gnome.shell", "favorite-apps"
    assert gsettings(vm, "range", schema, key) == "type as"
    assert gsettings(vm, "writable", schema, key) == "true"
    before = "['org.gnome.Nautilus.desktop']"
    gsettings(vm, "set", schema, key, before)
    assert dconf(vm) == before

    value = json.dumps(["firefox.desktop", "org.gnome.Nautilus.desktop"])
    profile_path = vm.put_json("favorites-fixture", {
        "schemaVersion": 1,
        "id": "favorites-fixture",
        "description": "Acceptance profile for configurable GNOME favorites",
        "operations": [{"id": "setting.gnome-favorite-apps", "state": "configured", "value": value}],
    })
    plan = user_ride(vm, "plan", "--profile", profile_path)
    assert value in plan.stdout
    refused = user_ride(vm, "apply", "--profile", profile_path, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    applied = user_ride(vm, "apply", "--profile", profile_path, "--allow-candidate")
    record = run_journal(vm, applied.stdout)
    assert record["steps"][0]["selectedValue"] == value
    configured = "['firefox.desktop', 'org.gnome.Nautilus.desktop']"
    assert dconf(vm) == configured
    repeated = user_ride(vm, "apply", "--profile", profile_path, "--allow-candidate")
    assert run_journal(vm, repeated.stdout)["steps"][0]["result"] == "unchanged"

    conflict_value = "['org.gnome.Nautilus.desktop', 'org.gnome.Software.desktop']"
    gsettings(vm, "set", schema, key, conflict_value)
    conflict = user_ride(vm, "restore", "--run-id", record["runId"],
                         "--allow-candidate", check=False)
    assert conflict.returncode != 0 and "restore conflict" in conflict.stderr
    assert dconf(vm) == conflict_value
    gsettings(vm, "set", schema, key, configured)
    user_ride(vm, "restore", "--run-id", record["runId"], "--allow-candidate")
    assert dconf(vm) == before
