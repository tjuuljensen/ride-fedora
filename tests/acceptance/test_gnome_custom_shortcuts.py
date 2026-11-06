"""Owned custom shortcut lifecycle and scoped recovery on Fedora 44."""

import json
import re
import shlex
from pathlib import Path

import pytest


RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")
MEDIA = "org.gnome.settings-daemon.plugins.media-keys"
WM = "org.gnome.desktop.wm.keybindings"
BASE = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings"
USER_PATH = f"{BASE}/custom100/"
ROOT = Path(__file__).resolve().parents[2]


def user_ride(vm, *args, catalog=None, check=True):
    command = [f"{vm.repo}/ride.sh", *args]
    prefix = "env RIDE_CATALOG_PATH=" + shlex.quote(catalog) + " " if catalog else ""
    return vm.run("dbus-run-session -- " + prefix + shlex.join(command), check=check)


def gsettings(vm, *args):
    return vm.run("dbus-run-session -- " + shlex.join(["gsettings", *args])).stdout.strip()


def journal(vm, output):
    match = RUN_ID.search(output)
    assert match, output
    return json.loads(vm.run(
        f"cat /home/ride-test/.local/state/ride-fedora/runs/{match.group(1)}.json"
    ).stdout)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_custom_shortcuts_merge_and_restore_only_ride_owned_entries(vm):
    catalog_data = json.loads((ROOT / "catalog/operations.json").read_text(encoding="utf-8"))
    operation = next(item for item in catalog_data["operations"]
                     if item["id"] == "setting.gnome-custom-shortcuts")
    operation["unsetState"] = "absent"
    catalog = vm.put_json("gnome-custom-shortcuts-acceptance-catalog", catalog_data)
    vm.run("sudo dnf -y install dbus-daemon", timeout=900)
    vm.run("command -v dbus-run-session && command -v gsettings && command -v dconf")
    custom_key = f"{MEDIA}.custom-keybinding:{USER_PATH}"
    original_paths = f"['{USER_PATH}']"
    gsettings(vm, "set", MEDIA, "custom-keybindings", original_paths)
    gsettings(vm, "set", custom_key, "name", "'User shortcut'")
    gsettings(vm, "set", custom_key, "command", "'user-command'")
    gsettings(vm, "set", custom_key, "binding", "'<Super>u'")
    gsettings(vm, "set", WM, "show-desktop", "['<Control>Escape']")
    gsettings(vm, "set", WM, "switch-windows", "['<Alt>Tab']")

    value = json.dumps({
        "global": {
            "showDesktop": ["<Super>d"],
            "switchWindows": ["<Alt>Tab"],
        },
        "shortcuts": [
            {"name": "Files home folder", "command": "nautilus", "binding": "<Super>e"},
            {"name": "Terminal", "command": "gnome-terminal", "binding": "<Super><Control>t"},
        ],
    }, separators=(",", ":"))
    profile = vm.put_json("custom-shortcuts", {
        "schemaVersion": 1,
        "id": "custom-shortcuts-fixture",
        "description": "Acceptance profile for owned GNOME shortcuts",
        "operations": [{
            "id": "setting.gnome-custom-shortcuts",
            "state": "configured",
            "value": value,
        }],
    })
    plan = user_ride(vm, "plan", "--profile", profile, catalog=catalog)
    assert "setting.gnome-custom-shortcuts" in plan.stdout
    refused = user_ride(vm, "apply", "--profile", profile, catalog=catalog, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr

    applied = user_ride(vm, "apply", "--profile", profile, "--allow-candidate", catalog=catalog)
    record = journal(vm, applied.stdout)
    assert record["steps"][0]["selectedValue"] == value
    owner = "/home/ride-test/.local/share/ride-fedora/owned/setting.gnome-custom-shortcuts.json"
    vm.run(f"test \"$(stat -c %a {owner})\" = 600")
    manifest = json.loads(vm.run(f"cat {owner}").stdout)
    assert manifest["originalPaths"] == [USER_PATH]
    assert len(manifest["entries"]) == 2
    registered = gsettings(vm, "get", MEDIA, "custom-keybindings")
    for entry in manifest["entries"]:
        assert entry["path"] in registered
        custom = f"{MEDIA}.custom-keybinding:{entry['path']}"
        assert gsettings(vm, "get", custom, "name") == f"'{entry['name']}'"
    assert gsettings(vm, "get", WM, "show-desktop") == "['<Control>Escape', '<Super>d']"
    assert gsettings(vm, "get", WM, "switch-windows") == "['<Alt>Tab']"
    assert gsettings(vm, "get", custom_key, "name") == "'User shortcut'"
    assert "configured" in user_ride(vm, "status", "setting.gnome-custom-shortcuts", catalog=catalog).stdout
    repeated = user_ride(vm, "apply", "--profile", profile, "--allow-candidate", catalog=catalog)
    assert journal(vm, repeated.stdout)["steps"][0]["result"] == "unchanged"

    changed_binding = "'<Super>F9'"
    first = manifest["entries"][0]
    first_key = f"{MEDIA}.custom-keybinding:{first['path']}"
    gsettings(vm, "set", first_key, "binding", changed_binding)
    conflict = user_ride(vm, "restore", "--run-id", record["runId"],
                         "--allow-candidate", catalog=catalog, check=False)
    assert conflict.returncode != 0 and "changed outside RIDE" in conflict.stderr
    assert gsettings(vm, "get", first_key, "binding") == changed_binding
    gsettings(vm, "set", first_key, "binding", f"'{first['binding']}'")
    user_ride(vm, "restore", "--run-id", record["runId"], "--allow-candidate", catalog=catalog)
    assert gsettings(vm, "get", MEDIA, "custom-keybindings") == original_paths
    assert gsettings(vm, "get", WM, "show-desktop") == "['<Control>Escape']"
    assert gsettings(vm, "get", WM, "switch-windows") == "['<Alt>Tab']"
    assert gsettings(vm, "get", custom_key, "name") == "'User shortcut'"
    vm.run(f"test ! -e {owner}")

    applied_again = user_ride(vm, "apply", "--profile", profile, "--allow-candidate", catalog=catalog)
    apply_again_id = journal(vm, applied_again.stdout)["runId"]
    unset = user_ride(vm, "unset", "setting.gnome-custom-shortcuts", "--allow-candidate", catalog=catalog)
    unset_record = journal(vm, unset.stdout)
    assert gsettings(vm, "get", MEDIA, "custom-keybindings") == original_paths
    assert gsettings(vm, "get", WM, "show-desktop") == "['<Control>Escape']"
    assert gsettings(vm, "get", WM, "switch-windows") == "['<Alt>Tab']"
    assert "absent" in user_ride(vm, "status", "setting.gnome-custom-shortcuts", catalog=catalog).stdout
    repeated_unset = user_ride(vm, "unset", "setting.gnome-custom-shortcuts", "--allow-candidate", catalog=catalog)
    assert journal(vm, repeated_unset.stdout)["steps"][0]["result"] == "unchanged"
    user_ride(vm, "restore", "--run-id", unset_record["runId"], "--allow-candidate", catalog=catalog)
    assert "configured" in user_ride(vm, "status", "setting.gnome-custom-shortcuts", catalog=catalog).stdout
    assert "<Super>d" in gsettings(vm, "get", WM, "show-desktop")
    user_ride(vm, "restore", "--run-id", apply_again_id, "--allow-candidate", catalog=catalog)
    assert "absent" in user_ride(vm, "status", "setting.gnome-custom-shortcuts", catalog=catalog).stdout

    final_apply = user_ride(vm, "apply", "--profile", profile, "--allow-candidate", catalog=catalog)
    final_apply_id = journal(vm, final_apply.stdout)["runId"]
    manifest = json.loads(vm.run(f"cat {owner}").stdout)
    added_path = f"{BASE}/custom101/"
    added_key = f"{MEDIA}.custom-keybinding:{added_path}"
    gsettings(vm, "set", added_key, "name", "'Later user shortcut'")
    gsettings(vm, "set", added_key, "command", "'later-command'")
    gsettings(vm, "set", added_key, "binding", "'<Super>l'")
    gsettings(vm, "set", MEDIA, "custom-keybindings", f"['{USER_PATH}', '{added_path}', "
               + ", ".join(f"'{item['path']}'" for item in manifest["entries"]) + "]")
    gsettings(vm, "set", WM, "show-desktop", "['<Control>Escape', '<Super>d', '<Control>F12']")
    user_ride(vm, "restore", "--run-id", final_apply_id, "--allow-candidate", catalog=catalog)
    remaining = gsettings(vm, "get", MEDIA, "custom-keybindings")
    assert USER_PATH in remaining and added_path in remaining
    assert all(item["path"] not in remaining for item in manifest["entries"])
    assert gsettings(vm, "get", added_key, "name") == "'Later user shortcut'"
    assert gsettings(vm, "get", WM, "show-desktop") == "['<Control>Escape', '<Control>F12']"
    assert gsettings(vm, "get", WM, "switch-windows") == "['<Alt>Tab']"
    vm.run(f"test ! -e {owner}")
