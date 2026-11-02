"""Explicit QEMU and VMware guest-tool package profiles have scoped inverses."""

import pytest


PROFILES = (
    ("fedora-qemu-guest-tools", ("spice-vdagent", "spice-webdavd")),
    ("fedora-vmware-guest-tools", ("open-vm-tools",)),
)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
@pytest.mark.recovery("remove-new-install")
def test_guest_tools_profiles_install_repeat_status_remove(vm):
    # The pinned Workstation image seeds all three package sets. Its
    # open-vm-tools-desktop RPM depends on open-vm-tools, so remove that exact
    # pair together in this disposable overlay to exercise absent state.
    vm.run("sudo rpm -e spice-vdagent spice-webdavd open-vm-tools-desktop open-vm-tools")
    for profile, packages in PROFILES:
        plan = vm.ride("plan", "--profile", profile)
        assert "candidate" in plan.stdout
        refused = vm.ride("apply", "--profile", profile, check=False)
        assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
        applied = vm.ride("apply", "--profile", profile, "--allow-candidate", timeout=900)
        for package in packages:
            assert vm.run(f"rpm -q --quiet {package}").returncode == 0
        assert "unchanged" in vm.ride(
            "apply", "--profile", profile, "--allow-candidate", timeout=300
        ).stdout
        for package in packages:
            assert package in vm.ride("status", f"package.{package}").stdout
        vm.ride("remove", "--profile", profile, "--allow-candidate", timeout=900)
        for package in packages:
            assert vm.run(f"rpm -q --quiet {package}", check=False).returncode != 0
