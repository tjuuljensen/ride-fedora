"""Retained Fedora VM shortcut and GNOME favorites profiles preserve prior state."""

import ast
import json
import re
import shlex

import pytest


def ride(vm, *args, check=True):
    command = [f"{vm.repo}/ride.sh", *args]
    return vm.run("dbus-run-session -- " + shlex.join(command), check=check)


def gsettings(vm, *args):
    return vm.run("dbus-run-session -- " + shlex.join(["gsettings", *args])).stdout.strip()


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_vm_shortcut_and_favorite_profiles_exactly_restore(vm):
    vm.run("sudo dnf -y install dbus-daemon", timeout=900)
    vm.run("command -v dbus-run-session && command -v gsettings && command -v dconf")

    shortcut_schema = "org.gnome.settings-daemon.plugins.media-keys"
    custom_path = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/ride-seed/"
    gsettings(vm, "set", "org.gnome.desktop.wm.keybindings", "show-desktop", "['<Super>d']")
    gsettings(vm, "set", shortcut_schema, "custom-keybindings", json.dumps([custom_path]))
    custom_schema = f"{shortcut_schema}.custom-keybinding:{custom_path}"
    gsettings(vm, "set", custom_schema, "name", "User owned shortcut")
    gsettings(vm, "set", custom_schema, "command", "nautilus")
    gsettings(vm, "set", custom_schema, "binding", "<Super><Alt>u")

    plan = ride(vm, "plan", "--profile", "fedora-vm-keyboard-shortcuts")
    assert "setting.gnome-custom-shortcuts" in plan.stdout
    refused = ride(vm, "apply", "--profile", "fedora-vm-keyboard-shortcuts", check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    applied = ride(vm, "apply", "--profile", "fedora-vm-keyboard-shortcuts", "--allow-candidate")
    assert "configured" in ride(vm, "status", "setting.gnome-custom-shortcuts").stdout
    repeat = ride(vm, "apply", "--profile", "fedora-vm-keyboard-shortcuts", "--allow-candidate")
    assert "unchanged setting.gnome-custom-shortcuts" in repeat.stdout
    registered = gsettings(vm, "get", shortcut_schema, "custom-keybindings")
    assert "ride-seed" in registered and registered.count("ridefedora-") == 2
    ride(vm, "remove", "--profile", "fedora-vm-keyboard-shortcuts", "--allow-candidate")
    assert gsettings(vm, "get", shortcut_schema, "custom-keybindings") == f"['{custom_path}']"
    assert gsettings(vm, "get", "org.gnome.desktop.wm.keybindings", "show-desktop") == "['<Super>d']"
    assert gsettings(vm, "get", custom_schema, "name") == "'User owned shortcut'"

    favorites = "org.gnome.shell"
    original = "['org.gnome.Nautilus.desktop']"
    gsettings(vm, "set", favorites, "favorite-apps", original)
    expected = {
        "fedora-default-favorites": [
            "org.mozilla.firefox.desktop", "org.gnome.Calendar.desktop",
            "org.gnome.Nautilus.desktop", "org.gnome.Software.desktop",
            "org.gnome.TextEditor.desktop", "org.gnome.Calculator.desktop",
        ],
        "fedora-minimal-favorites": [
            "org.mozilla.firefox.desktop", "org.gnome.Nautilus.desktop",
            "org.gnome.Console.desktop",
        ],
    }
    for profile, app_ids in expected.items():
        plan = ride(vm, "plan", "--profile", profile)
        assert "setting.gnome-favorite-apps" in plan.stdout
        refused = ride(vm, "apply", "--profile", profile, check=False)
        assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
        applied = ride(vm, "apply", "--profile", profile, "--allow-candidate")
        observed = ast.literal_eval(gsettings(vm, "get", favorites, "favorite-apps"))
        assert observed == app_ids
        repeated = ride(vm, "apply", "--profile", profile, "--allow-candidate")
        assert "unchanged setting.gnome-favorite-apps" in repeated.stdout
        run_id = re.search(r"Run ID: (\S+)", applied.stdout).group(1)
        ride(vm, "restore", "--run-id", run_id, "--allow-candidate")
        assert gsettings(vm, "get", favorites, "favorite-apps") == original

    # These values change future idle/lock timing only. The four related keys
    # are seeded to non-default user values, and each profile must restore them.
    lock_values = {
        ("org.gnome.desktop.session", "idle-delay"): "uint32 720",
        ("org.gnome.desktop.screensaver", "idle-activation-enabled"): "false",
        ("org.gnome.desktop.screensaver", "lock-enabled"): "false",
        ("org.gnome.desktop.screensaver", "lock-delay"): "uint32 40",
    }
    for (schema, key), value in lock_values.items():
        gsettings(vm, "set", schema, key, value)
    for minutes, idle_seconds in ((10, "uint32 600"), (15, "uint32 900")):
        profile = f"fedora-screen-lock-{minutes}-5"
        plan = ride(vm, "plan", "--profile", profile)
        assert "setting.gnome-lock-timing" in plan.stdout
        applied = ride(vm, "apply", "--profile", profile, "--allow-candidate")
        assert "configured" in ride(vm, "status", "setting.gnome-lock-timing").stdout
        assert gsettings(vm, "get", "org.gnome.desktop.session", "idle-delay") == idle_seconds
        assert gsettings(vm, "get", "org.gnome.desktop.screensaver", "idle-activation-enabled") == "true"
        assert gsettings(vm, "get", "org.gnome.desktop.screensaver", "lock-enabled") == "true"
        assert gsettings(vm, "get", "org.gnome.desktop.screensaver", "lock-delay") == "uint32 300"
        repeated = ride(vm, "apply", "--profile", profile, "--allow-candidate")
        assert "unchanged setting.gnome-lock-timing" in repeated.stdout
        run_id = re.search(r"Run ID: (\S+)", applied.stdout).group(1)
        ride(vm, "restore", "--run-id", run_id, "--allow-candidate")
        for (schema, key), value in lock_values.items():
            assert gsettings(vm, "get", schema, key) == value


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_gnome_lock_unset_resets_overrides_and_restores_prior_values(vm):
    vm.run("sudo dnf -y install dbus-daemon", timeout=900)
    vm.run("command -v dbus-run-session && command -v gsettings && command -v dconf")
    values = {
        ("org.gnome.desktop.session", "idle-delay", "/org/gnome/desktop/session/idle-delay"): "uint32 720",
        ("org.gnome.desktop.screensaver", "idle-activation-enabled", "/org/gnome/desktop/screensaver/idle-activation-enabled"): "false",
        ("org.gnome.desktop.screensaver", "lock-enabled", "/org/gnome/desktop/screensaver/lock-enabled"): "false",
        ("org.gnome.desktop.screensaver", "lock-delay", "/org/gnome/desktop/screensaver/lock-delay"): "uint32 40",
    }
    for (schema, key, path), value in values.items():
        gsettings(vm, "set", schema, key, value)
        actual = vm.run("dbus-run-session -- " + shlex.join(["dconf", "read", path])).stdout.strip()
        assert actual == value

    changed = ride(vm, "unset", "setting.gnome-lock-timing")
    run_id = re.search(r"Run ID: (\S+)", changed.stdout).group(1)
    assert "absent" in ride(vm, "status", "setting.gnome-lock-timing").stdout
    for _, _, path in values:
        actual = vm.run("dbus-run-session -- " + shlex.join(["dconf", "read", path])).stdout.strip()
        assert actual == ""
    repeated = ride(vm, "unset", "setting.gnome-lock-timing")
    assert "unchanged setting.gnome-lock-timing" in repeated.stdout

    ride(vm, "restore", "--run-id", run_id, "--dry-run")
    ride(vm, "restore", "--run-id", run_id)
    for (schema, key, path), value in values.items():
        assert gsettings(vm, "get", schema, key) == value
        actual = vm.run("dbus-run-session -- " + shlex.join(["dconf", "read", path])).stdout.strip()
        assert actual == value

    explicit = ride(vm, "set", "setting.gnome-lock-timing", "--state", "absent")
    explicit_run_id = re.search(r"Run ID: (\S+)", explicit.stdout).group(1)
    assert "absent" in ride(vm, "status", "setting.gnome-lock-timing").stdout
    for _, _, path in values:
        actual = vm.run("dbus-run-session -- " + shlex.join(["dconf", "read", path])).stdout.strip()
        assert actual == ""
    ride(vm, "restore", "--run-id", explicit_run_id)
    for (schema, key, path), value in values.items():
        assert gsettings(vm, "get", schema, key) == value
        actual = vm.run("dbus-run-session -- " + shlex.join(["dconf", "read", path])).stdout.strip()
        assert actual == value
