"""Disposable Flatpak runtime install preserves remotes and user data."""

import json
from pathlib import Path
import pytest


ID = "package.flatpak"
REMOTE_NAME = "ride-flatpak-runtime-sentinel"
DATA = "/home/ride-test/.var/app/org.example.RideSentinel/data/important.txt"


def remotes(vm, scope):
    return json.loads(vm.run(f"flatpak remotes --{scope} --columns=name,url,options --json").stdout)


def applications(vm, scope):
    output = vm.run(f"flatpak list --{scope} --columns=application,origin --json").stdout
    return json.loads(output or "[]")


def remote_config_state(vm):
    return vm.run(
        "for path in /var/lib/flatpak/repo/config "
        "/home/ride-test/.local/share/flatpak/repo/config; do "
        "if test -f \"$path\"; then sudo sha256sum \"$path\"; "
        "else printf 'missing %s\\n' \"$path\"; fi; done"
    ).stdout


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_flatpak_runtime_install_only_preserves_remotes_and_user_data(vm):
    catalog = json.loads((Path(__file__).resolve().parents[2] / "catalog" / "operations.json").read_text())
    operation = next(item for item in catalog["operations"] if item["id"] == ID)
    assert operation["status"] in {"candidate", "supported"}
    candidate_args = ["--allow-candidate"] if operation["status"] == "candidate" else []
    vm.run("rpm -q flatpak")
    vm.run("flatpak remote-add --user " + REMOTE_NAME + " https://dl.flathub.org/repo/flathub.flatpakrepo", timeout=900)
    vm.run("mkdir -p /home/ride-test/.var/app/org.example.RideSentinel/data")
    vm.run("printf 'preserve this user data\\n' > " + DATA)
    vm.run("chmod 0600 " + DATA)
    original_system_remotes = remotes(vm, "system")
    original_user_remotes = remotes(vm, "user")
    original_system_apps = applications(vm, "system")
    original_user_apps = applications(vm, "user")
    original_remote_configs = remote_config_state(vm)
    original_data = vm.run("sha256sum " + DATA).stdout
    original_meta = vm.run("stat -c '%u:%g:%a' " + DATA).stdout
    original_rpms = set(vm.run("rpm -qa --qf '%{NAME}\\n'").stdout.splitlines())

    removed = vm.run("sudo rpm -e --nodeps flatpak")
    removed_names = original_rpms - set(vm.run("rpm -qa --qf '%{NAME}\\n'").stdout.splitlines())
    assert removed_names == {"flatpak"}, (removed.stdout, sorted(removed_names))
    assert remote_config_state(vm) == original_remote_configs
    assert vm.run("sha256sum " + DATA).stdout == original_data
    assert vm.run("stat -c '%u:%g:%a' " + DATA).stdout == original_meta

    planned = vm.ride("plan", "--profile", "flatpak-runtime")
    assert ID in planned.stdout and "absent" in planned.stdout
    if operation["status"] == "candidate":
        assert "candidate" in planned.stdout
        refused = vm.ride("apply", "--profile", "flatpak-runtime", check=False)
        assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    changed = vm.ride("apply", "--profile", "flatpak-runtime", *candidate_args, timeout=900)
    assert "changed" in changed.stdout
    assert vm.run("rpm -q --qf '%{RSAHEADER:pgpsig}\\n' flatpak | grep -qv '(none)'").returncode == 0
    vm.run("rpm -V flatpak")
    assert "installed" in vm.ride("status", ID).stdout
    repeated = vm.ride("apply", "--profile", "flatpak-runtime", *candidate_args)
    assert "unchanged" in repeated.stdout
    unavailable_restore = vm.ride("restore", "--run-id", changed.stdout.split("Run ID: ", 1)[1].splitlines()[0], check=False)
    assert unavailable_restore.returncode != 0 and "exact recovery is unavailable" in unavailable_restore.stderr
    remove = vm.ride("remove", ID, *candidate_args, check=False)
    assert remove.returncode != 0 and "invalid state absent" in remove.stderr

    assert remotes(vm, "system") == original_system_remotes
    assert remotes(vm, "user") == original_user_remotes
    assert remote_config_state(vm) == original_remote_configs
    assert applications(vm, "system") == original_system_apps
    assert applications(vm, "user") == original_user_apps
    assert vm.run("sha256sum " + DATA).stdout == original_data
    assert vm.run("stat -c '%u:%g:%a' " + DATA).stdout == original_meta
