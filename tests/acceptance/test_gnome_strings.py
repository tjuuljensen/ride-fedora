"""Disposable Workstation lifecycle for explicit GNOME string values."""

import json
import re
import shlex

import pytest


RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")


def user_ride(vm, *args, check=True):
    return vm.run("dbus-run-session -- " + shlex.join([f"{vm.repo}/ride.sh", *args]), check=check)


def gsettings(vm, *args):
    return vm.run("dbus-run-session -- " + shlex.join(["gsettings", *args])).stdout.strip()


def dconf(vm, path):
    return vm.run("dbus-run-session -- " + shlex.join(["dconf", "read", path])).stdout.strip()


def journal(vm, output):
    match = RUN_ID.search(output)
    assert match, output
    return json.loads(vm.run(
        f"cat /home/ride-test/.local/state/ride-fedora/runs/{match.group(1)}.json"
    ).stdout)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_gnome_region_and_three_window_layouts(vm):
    vm.run("test \"$(id -u)\" != 0")
    vm.run("sudo dnf -y install dbus-daemon", timeout=900)
    vm.run("command -v dbus-run-session && command -v gsettings && command -v dconf")
    region_schema, region_key, region_path = (
        "org.gnome.system.locale", "region", "/system/locale/region")
    button_schema, button_key, button_path = (
        "org.gnome.desktop.wm.preferences", "button-layout",
        "/org/gnome/desktop/wm/preferences/button-layout")
    assert gsettings(vm, "range", region_schema, region_key) == "type s"
    assert gsettings(vm, "range", button_schema, button_key) == "type s"
    assert gsettings(vm, "writable", region_schema, region_key) == "true"
    assert gsettings(vm, "writable", button_schema, button_key) == "true"
    assert "da_DK.utf8" in vm.run("locale -a").stdout.splitlines()

    gsettings(vm, "set", region_schema, region_key, "'en_US.UTF-8'")
    assert dconf(vm, region_path) == "'en_US.UTF-8'"
    plan = user_ride(vm, "plan", "--profile", "gnome-region-da-dk")
    assert "configured:da_DK.UTF-8" in plan.stdout
    refused = user_ride(vm, "apply", "--profile", "gnome-region-da-dk", check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    changed = user_ride(vm, "apply", "--profile", "gnome-region-da-dk", "--allow-candidate")
    first = journal(vm, changed.stdout)
    assert first["status"] == "complete" and first["steps"][0]["result"] == "changed"
    assert first["steps"][0]["selectedValue"] == "da_DK.UTF-8"
    assert first["steps"][0]["observedBefore"].startswith("user:")
    assert dconf(vm, region_path) == "'da_DK.UTF-8'"
    repeat = user_ride(vm, "apply", "--profile", "gnome-region-da-dk", "--allow-candidate")
    assert journal(vm, repeat.stdout)["steps"][0]["result"] == "unchanged"
    gsettings(vm, "set", region_schema, region_key, "'fr_FR.UTF-8'")
    conflict = user_ride(vm, "restore", "--run-id", first["runId"],
                         "--allow-candidate", check=False)
    assert conflict.returncode != 0 and "restore conflict" in conflict.stderr
    assert dconf(vm, region_path) == "'fr_FR.UTF-8'"
    gsettings(vm, "set", region_schema, region_key, "'da_DK.UTF-8'")
    user_ride(vm, "restore", "--run-id", first["runId"], "--dry-run")
    user_ride(vm, "restore", "--run-id", first["runId"], "--allow-candidate")
    assert dconf(vm, region_path) == "'en_US.UTF-8'"

    gsettings(vm, "reset", region_schema, region_key)
    assert dconf(vm, region_path) == ""
    changed = user_ride(vm, "apply", "--profile", "gnome-region-da-dk", "--allow-candidate")
    second = journal(vm, changed.stdout)
    assert second["steps"][0]["observedBefore"] == "unset"
    user_ride(vm, "restore", "--run-id", second["runId"], "--allow-candidate")
    assert dconf(vm, region_path) == ""

    gsettings(vm, "set", button_schema, button_key, "'menu:minimize,close'")
    assert dconf(vm, button_path) == "'menu:minimize,close'"
    for profile, value in (
        ("gnome-window-buttons-minmax", ":minimize,maximize,close"),
        ("gnome-window-buttons-appmenu", ":appmenu:close"),
        ("gnome-window-buttons-left", "close,minimize,maximize:"),
    ):
        plan = user_ride(vm, "plan", "--profile", profile)
        assert f"configured:{value}" in plan.stdout
        changed = user_ride(vm, "apply", "--profile", profile, "--allow-candidate")
        record = journal(vm, changed.stdout)
        assert record["steps"][0]["selectedValue"] == value
        assert dconf(vm, button_path) == f"'{value}'"
        repeat = user_ride(vm, "apply", "--profile", profile, "--allow-candidate")
        assert journal(vm, repeat.stdout)["steps"][0]["result"] == "unchanged"
        user_ride(vm, "restore", "--run-id", record["runId"], "--allow-candidate")
        assert dconf(vm, button_path) == "'menu:minimize,close'"
