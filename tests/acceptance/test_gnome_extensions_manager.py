"""Fedora 44 GNOME Extensions manager package profile lifecycle."""

import pytest


PROFILE = "fedora-gnome-extensions"
OPERATIONS = ("package.gnome-extensions-app", "package.gnome-browser-connector")
PACKAGES = ("gnome-extensions-app", "gnome-browser-connector")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_gnome_extensions_manager_profile_lifecycle(vm):
    vm.run("gnome-extensions --version")
    before = vm.run("rpm -qa --qf '%{NAME}\\t%{ARCH}\\n' | sort").stdout
    extension_dir = "/home/ride-test/.local/share/gnome-shell/extensions/rideacceptance@example.test"
    vm.run(f"mkdir -p {extension_dir}")
    vm.run(f"printf 'pre-existing extension fixture\\n' > {extension_dir}/metadata.json")
    extension_before = vm.run(f"sha256sum {extension_dir}/metadata.json").stdout
    plan = vm.ride("plan", "--profile", PROFILE)
    assert all(operation in plan.stdout for operation in OPERATIONS)
    refused = vm.ride("apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    vm.ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=900)
    for package in PACKAGES:
        vm.run(f"rpm -q {package}")
        vm.run(f"rpm -V {package}")
    vm.run("test -x /usr/bin/gnome-extensions-app")
    vm.run("test -x /usr/bin/gnome-browser-connector-host")
    for operation in OPERATIONS:
        assert operation in vm.ride("status", operation).stdout
    repeat = vm.ride("apply", "--profile", PROFILE, "--allow-candidate")
    assert all(f"unchanged {operation}" in repeat.stdout for operation in OPERATIONS)
    vm.ride("remove", "--profile", PROFILE, "--allow-candidate", timeout=900)
    after = vm.run("rpm -qa --qf '%{NAME}\\t%{ARCH}\\n' | sort").stdout
    expected_removed = {f"{package}\tx86_64" for package in PACKAGES}
    assert set(before.splitlines()) - set(after.splitlines()) <= expected_removed
    assert set(after.splitlines()) - set(before.splitlines()) == set()
    assert vm.run(f"sha256sum {extension_dir}/metadata.json").stdout == extension_before
