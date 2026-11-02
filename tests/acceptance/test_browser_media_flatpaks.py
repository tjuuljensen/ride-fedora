"""Fedora 44 lifecycle for kept browser and Spotify Flathub packages."""

import json
from pathlib import PurePosixPath

import pytest


REMOTE_PROFILE = "flathub-system"
CASES = [
    ("fedora-chrome", "package.chrome", "com.google.Chrome"),
    ("fedora-edge", "package.edge", "com.microsoft.Edge"),
    ("fedora-spotify", "package.spotify", "com.spotify.Client"),
    ("fedora-vivaldi", "package.vivaldi", "com.vivaldi.Vivaldi"),
    ("fedora-xmind", "package.xmind", "net.xmind.XMind"),
]


def flatpak_apps(vm):
    output = vm.run("flatpak list --system --columns=application,origin --json").stdout
    return json.loads(output or "[]")


def application_id(row):
    return row.get("application_id", row.get("application"))


def flatpak_remotes(vm):
    return json.loads(vm.run(
        "flatpak remotes --system --columns=name,url,options --json").stdout)


def verify_flatpak_lifecycle(vm, profile, operation, app_id):
    data = PurePosixPath("/home/ride-test/.var/app") / app_id / "config/ride-sentinel"
    vm.run(f"mkdir -p {data.parent}")
    vm.run(f"printf '%s\\n' {app_id} > {data}")
    original = vm.run(f"sha256sum {data}").stdout
    assert not any(application_id(row) == app_id for row in flatpak_apps(vm))

    plan = vm.ride("plan", "--profile", profile)
    assert operation in plan.stdout and "absent" in plan.stdout
    refused = vm.ride("apply", "--profile", profile, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    vm.ride("apply", "--profile", profile, "--allow-candidate", timeout=1500)
    installed = [row for row in flatpak_apps(vm) if application_id(row) == app_id]
    assert len(installed) == 1 and installed[0]["origin"] == "flathub"
    assert f"{operation}\tflathub-flatpak\tinstalled" in vm.ride(
        "status", operation).stdout
    repeated = vm.ride("apply", "--profile", profile, "--allow-candidate")
    assert f"unchanged {operation}" in repeated.stdout

    vm.ride("remove", "--profile", profile, "--allow-candidate", timeout=1200)
    assert not any(application_id(row) == app_id for row in flatpak_apps(vm))
    assert vm.run(f"sha256sum {data}").stdout == original
    assert any(row.get("name") == "flathub" for row in flatpak_remotes(vm))


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_browser_and_spotify_flatpak_lifecycles_preserve_user_state(vm):
    vm.run("flatpak --version")
    assert not any(remote.get("name") == "flathub" for remote in flatpak_remotes(vm))
    vm.ride("apply", "--profile", REMOTE_PROFILE, "--allow-candidate", timeout=900)
    remote = next(row for row in flatpak_remotes(vm) if row["name"] == "flathub")
    assert remote["url"] == "https://dl.flathub.org/repo/"
    assert "no-gpg-verify" not in remote["options"]

    for profile, operation, app_id in CASES:
        verify_flatpak_lifecycle(vm, profile, operation, app_id)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_vivaldi_and_xmind_flatpak_lifecycles_preserve_user_state(vm):
    vm.run("flatpak --version")
    if not any(remote.get("name") == "flathub" for remote in flatpak_remotes(vm)):
        vm.ride("apply", "--profile", REMOTE_PROFILE, "--allow-candidate", timeout=900)
    verify_flatpak_lifecycle(
        vm, "fedora-vivaldi", "package.vivaldi", "com.vivaldi.Vivaldi")
    verify_flatpak_lifecycle(
        vm, "fedora-xmind", "package.xmind", "net.xmind.XMind")
