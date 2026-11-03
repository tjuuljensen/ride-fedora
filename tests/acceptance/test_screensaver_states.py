"""Disposable lifecycle checks for the two retained v2 screensaver states."""

import re
import shlex

import pytest


def ride(vm, *args, check=True):
    return vm.run("dbus-run-session -- " + shlex.join([f"{vm.repo}/ride.sh", *args]), check=check)


def gsettings(vm, *args):
    return vm.run("dbus-run-session -- " + shlex.join(["gsettings", *args])).stdout.strip()


def run_id(output):
    match = re.search(r"Run ID: (\S+)", output)
    assert match, output
    return match.group(1)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_legacy_screensaver_states_preserve_lock_delay_and_restore(vm):
    vm.run("sudo dnf -y install dbus-daemon", timeout=900)
    original = {
        ("org.gnome.desktop.session", "idle-delay"): "uint32 720",
        ("org.gnome.desktop.screensaver", "idle-activation-enabled"): "false",
        ("org.gnome.desktop.screensaver", "lock-enabled"): "false",
        ("org.gnome.desktop.screensaver", "lock-delay"): "uint32 40",
    }
    for (schema, key), value in original.items():
        gsettings(vm, "set", schema, key, value)

    cases = (
        ("fedora-screensaver-enabled", "uint32 300", "true", "true"),
        ("fedora-screensaver-disabled", "uint32 0", "false", "false"),
    )
    for profile, idle, activation, locked in cases:
        plan = ride(vm, "plan", "--profile", profile)
        assert "setting.gnome-lock-timing" in plan.stdout
        applied = ride(vm, "apply", "--profile", profile)
        run = run_id(applied.stdout)
        assert gsettings(vm, "get", "org.gnome.desktop.session", "idle-delay") == idle
        assert gsettings(vm, "get", "org.gnome.desktop.screensaver", "idle-activation-enabled") == activation
        assert gsettings(vm, "get", "org.gnome.desktop.screensaver", "lock-enabled") == locked
        assert gsettings(vm, "get", "org.gnome.desktop.screensaver", "lock-delay") == "uint32 40"
        assert "configured" in ride(vm, "status", "setting.gnome-lock-timing").stdout
        assert "unchanged setting.gnome-lock-timing" in ride(vm, "apply", "--profile", profile).stdout
        ride(vm, "restore", "--run-id", run)
        for (schema, key), value in original.items():
            assert gsettings(vm, "get", schema, key) == value
