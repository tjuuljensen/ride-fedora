"""Disposable Fedora 44 pinned Bitwarden AppImage preserves user vault files."""

import json
import shlex

import pytest

PROFILE = "fedora-bitwarden-appimage"
SENTINEL = "/home/ride-test/.config/Bitwarden/.ride-migration-fixture/encrypted.json"
RIDE = "/home/ride-test/ride/ride.sh"


def user_ride(vm, *args, check=True, timeout=180):
    return vm.run(shlex.join([RIDE, *args]), check=check, timeout=timeout)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
@pytest.mark.recovery("remove-new-install")
def test_bitwarden_appimage_lifecycle_preserves_vault_files(vm):
    vm.run('test "$(id -u)" != 0')
    rpm_before = vm.run("rpm -q --quiet bitwarden", check=False).returncode
    vm.run("mkdir -p /home/ride-test/.config/Bitwarden/.ride-migration-fixture")
    vm.run("printf '%s\\n' 'synthetic encrypted vault fixture' > " + SENTINEL)
    vm.run("chmod 0600 " + SENTINEL)
    before_hash = vm.run("sha256sum " + SENTINEL).stdout.split()[0]
    before_mode = vm.run("stat -c '%u:%g:%a' " + SENTINEL).stdout.strip()

    plan = user_ride(vm, "plan", "--profile", PROFILE)
    assert "package.bitwarden-appimage" in plan.stdout and "supported" in plan.stdout
    applied = user_ride(vm, "apply", "--profile", PROFILE, timeout=900)
    assert "package.bitwarden-appimage" in applied.stdout
    path = "/home/ride-test/Applications/Bitwarden-2026.10.1-x86_64.AppImage"
    manifest_path = "/home/ride-test/.local/share/ride-fedora/owned-tools/package.bitwarden-appimage.json"
    manifest = json.loads(vm.run("cat " + manifest_path).stdout)
    assert manifest["id"] == "package.bitwarden-appimage"
    assert manifest["version"] == "2026.10.1"
    assert vm.run("test -x " + path).returncode == 0
    runtime = vm.run("timeout 30 " + path + " --appimage-version", timeout=60)
    assert "Version:" in runtime.stdout + runtime.stderr
    assert "package.bitwarden-appimage" in user_ride(vm, "status", "package.bitwarden-appimage").stdout
    repeated = user_ride(vm, "apply", "--profile", PROFILE)
    assert "unchanged package.bitwarden-appimage" in repeated.stdout

    user_ride(vm, "remove", "--profile", PROFILE)
    vm.run("test ! -e " + path)
    vm.run("test ! -e " + manifest_path)
    after = vm.run("sha256sum " + SENTINEL).stdout.split()[0]
    assert after == before_hash
    assert vm.run("stat -c '%u:%g:%a' " + SENTINEL).stdout.strip() == before_mode
    assert vm.run("rpm -q --quiet bitwarden", check=False).returncode == rpm_before
