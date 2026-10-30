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
