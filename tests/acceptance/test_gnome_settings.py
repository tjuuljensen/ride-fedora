"""Disposable Workstation happy path for opt-in GNOME user settings."""

import json
import re
import shlex

import pytest


RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")
SETTINGS = (
    ("org.gnome.desktop.interface", "clock-show-date", "false", "true"),
    ("org.gnome.desktop.calendar", "show-weekdate", "false", "true"),
    ("org.gnome.desktop.interface", "gtk-enable-primary-paste", "false", "true"),
    ("org.gnome.system.location", "enabled", "true", "false"),
    ("org.gnome.desktop.privacy", "report-technical-problems", "true", "false"),
)


def user_ride(vm, *args, check=True):
    return vm.run("dbus-run-session -- " + shlex.join([f"{vm.repo}/ride.sh", *args]), check=check)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_gnome_boolean_profiles_apply_repeat_and_restore(vm):
    vm.run("test \"$(id -u)\" != 0")
    # The pinned Workstation image has a broker-backed desktop bus but its
    # headless SSH session has no user bus or dbus-run-session helper.
    vm.run("sudo dnf -y install dbus-daemon", timeout=900)
    vm.run("command -v dbus-run-session && command -v gsettings")
    for schema, key, baseline, _ in SETTINGS:
        vm.run("dbus-run-session -- " + shlex.join(["gsettings", "set", schema, key, baseline]))
        actual = vm.run("dbus-run-session -- " + shlex.join(["gsettings", "get", schema, key])).stdout.strip()
        assert actual == baseline, (schema, key, actual)


    for profile in ("gnome-shell-preferences", "gnome-privacy"):
        planned = user_ride(vm, "plan", "--profile", profile)
        assert "candidate" in planned.stdout
        refused = user_ride(vm, "apply", "--profile", profile, check=False)
        assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
        changed = user_ride(vm, "apply", "--profile", profile, "--allow-candidate")
        match = RUN_ID.search(changed.stdout)
        assert match, changed.stdout
        run_id = match.group(1)
        record = json.loads(vm.run(f"cat /home/ride-test/.local/state/ride-fedora/runs/{run_id}.json").stdout)
        assert record["status"] == "complete"
        assert all(step["result"] == "changed" for step in record["steps"])
        repeated = user_ride(vm, "apply", "--profile", profile, "--allow-candidate")
        repeat_id = RUN_ID.search(repeated.stdout)
        assert repeat_id, repeated.stdout
        repeat = json.loads(vm.run(f"cat /home/ride-test/.local/state/ride-fedora/runs/{repeat_id.group(1)}.json").stdout)
        assert all(step["result"] == "unchanged" for step in repeat["steps"])
        user_ride(vm, "status", "--profile", profile)
        user_ride(vm, "restore", "--run-id", run_id, "--dry-run")
        restored = user_ride(vm, "restore", "--run-id", run_id, "--allow-candidate")
        assert RUN_ID.search(restored.stdout)

    for schema, key, baseline, _ in SETTINGS:
        actual = vm.run("dbus-run-session -- " + shlex.join(["gsettings", "get", schema, key])).stdout.strip()
        assert actual == baseline, (schema, key, actual)

@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_terminator_ibus_hotkey_custom_and_unset_recovery(vm):
    vm.run("test \"$(id -u)\" != 0")
    vm.run("sudo dnf -y install dbus-daemon", timeout=900)
    vm.run("command -v dbus-run-session && command -v gsettings && command -v dconf")
    schema = "org.freedesktop.ibus.panel.emoji"
    key = "hotkey"
    target = "['<Control><Alt><Shift>e']"
    custom = "['<Alt>F8']"
    path = "/desktop/ibus/panel/emoji/hotkey"

    def setting(*args):
        return vm.run("dbus-run-session -- " + shlex.join(["gsettings", *args])).stdout.strip()

    def override():
        return vm.run("dbus-run-session -- " + shlex.join(["dconf", "read", path])).stdout.strip()

    assert setting("range", schema, key) == "type as"
    assert setting("writable", schema, key) == "true"
    setting("set", schema, key, custom)
    assert setting("get", schema, key) == custom and override() == custom
    plan = user_ride(vm, "plan", "--profile", "terminator-hotkey")
    assert "setting.ibus-emoji-hotkey" in plan.stdout and "candidate" in plan.stdout
    refused = user_ride(vm, "apply", "--profile", "terminator-hotkey", check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    changed = user_ride(vm, "apply", "--profile", "terminator-hotkey", "--allow-candidate")
    run_id = RUN_ID.search(changed.stdout).group(1)
    journal = json.loads(vm.run(f"cat /home/ride-test/.local/state/ride-fedora/runs/{run_id}.json").stdout)
    assert journal["status"] == "complete"
    assert journal["steps"][0]["observedBefore"].startswith("user:")
    assert journal["steps"][0]["observedAfter"] == "enabled"
    assert setting("get", schema, key) == target and override() == target
    repeat = user_ride(vm, "apply", "--profile", "terminator-hotkey", "--allow-candidate")
    repeated_id = RUN_ID.search(repeat.stdout).group(1)
    repeated = json.loads(vm.run(f"cat /home/ride-test/.local/state/ride-fedora/runs/{repeated_id}.json").stdout)
    assert repeated["steps"][0]["result"] == "unchanged"
    setting("set", schema, key, "['<Alt>F9']")
    conflict = user_ride(vm, "restore", "--run-id", run_id, "--allow-candidate", check=False)
    assert conflict.returncode != 0 and "restore conflict" in conflict.stderr
    assert override() == "['<Alt>F9']"
    setting("set", schema, key, target)
    user_ride(vm, "restore", "--run-id", run_id, "--dry-run")
    user_ride(vm, "restore", "--run-id", run_id, "--allow-candidate")
    assert setting("get", schema, key) == custom and override() == custom

    setting("reset", schema, key)
    assert override() == ""
    changed = user_ride(vm, "apply", "--profile", "terminator-hotkey", "--allow-candidate")
    run_id = RUN_ID.search(changed.stdout).group(1)
    journal = json.loads(vm.run(f"cat /home/ride-test/.local/state/ride-fedora/runs/{run_id}.json").stdout)
    assert journal["steps"][0]["observedBefore"] == "unset"
    assert override() == target
    user_ride(vm, "restore", "--run-id", run_id, "--allow-candidate")
    assert override() == ""
    assert vm.run("rpm -q --quiet terminator", check=False).returncode != 0
