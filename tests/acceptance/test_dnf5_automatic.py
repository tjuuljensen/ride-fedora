"""DNF5 automatic-update package and owned timer acceptance."""

import pytest


PROFILE = "fedora-server-auto-update"
PACKAGE = "package.dnf5-plugin-automatic"
SETTING = "setting.dnf5-automatic"
DROPIN = "/etc/systemd/system/dnf5-automatic.service.d/50-ride-fedora.conf"


@pytest.mark.vm_target("fedora-44-server-x86_64")
def test_dnf5_automatic_timer_lifecycle_and_exact_restore(vm):
    vm.run("rpm -qa --qf '%{NAME}.%{ARCH}\\n' | sort > /home/ride-test/ride-auto-rpm-before")
    absent = vm.run("rpm -q dnf5-plugin-automatic", check=False)
    assert absent.returncode != 0
    # The timer unit is absent until its dependency RPM is installed.
    vm.run("test \"$(systemctl is-enabled dnf5-automatic.timer 2>/dev/null || true)\" = not-found")
    vm.run("test \"$(systemctl is-active dnf5-automatic.timer 2>/dev/null || true)\" = inactive")
    vm.run(f"test ! -e {DROPIN} && test ! -L {DROPIN}")
    vm.run("test -z \"$(systemctl show --property=DropInPaths --value dnf5-automatic.service)\"")

    plan = vm.ride("plan", "--profile", PROFILE)
    assert PACKAGE in plan.stdout and SETTING in plan.stdout
    refused = vm.ride("apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    # DNF5 refresh and the automatic plugin's dependency transaction can take
    # several minutes under QEMU TCG on the pinned Server image.
    applied = vm.ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=600)
    run_id = applied.stdout.split("Run ID: ", 1)[1].splitlines()[0]
    vm.run("rpm -q dnf5-plugin-automatic")
    vm.run("rpm -V dnf5-plugin-automatic")
    vm.run(f"test -s {DROPIN}")
    vm.run("systemctl cat dnf5-automatic.service | grep -F -- '--timer --installupdates'")
    vm.run("test \"$(systemctl is-enabled dnf5-automatic.timer)\" = enabled")
    vm.run("test \"$(systemctl is-active dnf5-automatic.timer)\" = active")
    assert "enabled" in vm.ride("status", SETTING).stdout

    repeat = vm.ride("apply", "--profile", PROFILE, "--allow-candidate")
    assert f"unchanged {PACKAGE}" in repeat.stdout
    assert f"unchanged {SETTING}" in repeat.stdout

    vm.ride("restore", "--run-id", run_id, "--allow-candidate")
    vm.run(f"test ! -e {DROPIN} && test ! -L {DROPIN}")
    # Removing the dependency RPM removes its timer unit, so systemd reports
    # not-found; RIDE observes this as its original disabled baseline.
    vm.run("test \"$(systemctl is-enabled dnf5-automatic.timer 2>/dev/null || true)\" = not-found")
    vm.run("test \"$(systemctl is-active dnf5-automatic.timer 2>/dev/null || true)\" = inactive")
    assert "disabled" in vm.ride("status", SETTING).stdout
    vm.run("! rpm -q dnf5-plugin-automatic")
    # Store the snapshot in the test user's home because Fedora cleans /tmp
    # during boot; package versions may upgrade, but name/arch identities stay.
    vm.run("rpm -qa --qf '%{NAME}.%{ARCH}\\n' | sort > /home/ride-test/ride-auto-rpm-after")
    vm.run("! comm -23 /home/ride-test/ride-auto-rpm-before /home/ride-test/ride-auto-rpm-after | grep -q .")
