"""Exercise the supported TMOG AppImage on a disposable Fedora Workstation VM."""

import re
import shlex

import pytest


PROFILE = "fedora-tmog"
RUNTIME_PROFILE = "fedora-tmog-runtime"
APPIMAGE = "/home/ride-test/.local/opt/ride-fedora/tmog/1.1.1/TaskManagerOG-1.1.1-x86_64.AppImage"
APPDIR = "/home/ride-test/.local/opt/ride-fedora/tmog/1.1.1/appdir"
ICON = f"{APPDIR}/usr/share/icons/hicolor/256x256/apps/tmog-task-manager.png"
DESKTOP = "/home/ride-test/.local/share/applications/com.tmog.taskmanager.desktop"
MANIFEST = "/home/ride-test/.local/share/ride-fedora/owned-tools/package.tmog.json"
SENTINEL = "/home/ride-test/.config/TMOG/Task Manager TMOG/ride-sentinel.txt"
LICENSE = "/home/ride-test/.config/TMOG/Task Manager TMOG/license.json"
SOURCE_SHA = "12a1f2ed60c28b0749a13eeaec4696f241a425fb6715d9e7747807ce62d3b139"
RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_tmog_appimage_lifecycle_preserves_user_data(vm):
    vm.run("mkdir -p '/home/ride-test/.config/TMOG/Task Manager TMOG' && "
           "printf 'keep settings\\n' > " + shlex.quote(SENTINEL) + " && "
           "printf 'synthetic entitlement\\n' > " + shlex.quote(LICENSE))
    vm.run(f"test ! -e {APPIMAGE} && test ! -e {APPDIR} && "
           f"test ! -e {DESKTOP} && test ! -e {MANIFEST}")

    def user_ride(*args, timeout=180, check=True):
        return vm.run(shlex.join((f"{vm.repo}/ride.sh", *args)), timeout=timeout, check=check)

    runtime_plan = vm.run(f"sudo {vm.repo}/ride.sh plan --profile {RUNTIME_PROFILE}")
    assert "package.squashfs-tools" in runtime_plan.stdout
    vm.run(f"sudo {vm.repo}/ride.sh apply --profile {RUNTIME_PROFILE}", timeout=600)
    vm.run("rpm -q squashfs-tools && rpm -qf /usr/bin/unsquashfs && rpm -V squashfs-tools")
    runtime_status = vm.run(f"sudo {vm.repo}/ride.sh status package.squashfs-tools")
    assert "installed" in runtime_status.stdout
    runtime_repeat = vm.run(f"sudo {vm.repo}/ride.sh apply --profile {RUNTIME_PROFILE}")
    assert "unchanged" in runtime_repeat.stdout
    assert "package.tmog" in user_ride("plan", "--profile", PROFILE).stdout
    applied = user_ride("apply", "--profile", PROFILE, timeout=600)
    match = RUN_ID.search(applied.stdout)
    assert match, applied.stdout
    run_id = match.group(1)
    assert vm.run(f"sha256sum {APPIMAGE}").stdout.split()[0] == SOURCE_SHA
    vm.run(f"test -f {MANIFEST} && test -f {DESKTOP} && test -x {APPIMAGE} && "
           f"test -x {APPDIR}/AppRun && test -f {ICON}")
    vm.run(f"grep -F 'Exec=\"{APPDIR}/AppRun\"' {DESKTOP}")
    vm.run(f"grep -Fx 'Icon={ICON}' {DESKTOP}")
    xvfb_preinstalled = vm.run("rpm -q xorg-x11-server-Xvfb", check=False).returncode == 0
    if not xvfb_preinstalled:
        vm.run("sudo dnf -y install xorg-x11-server-Xvfb", timeout=600)
    vm.run("mkdir -p /tmp/ride-tmog-gui-config")
    gui = vm.run(f"timeout --signal=TERM 15s xvfb-run -a env "
                 f"XDG_CONFIG_HOME=/tmp/ride-tmog-gui-config {APPDIR}/AppRun",
                 check=False, timeout=35)
    assert gui.returncode == 124, gui.stderr
    assert "package.tmog\ttmog-publisher-appimage-pinned\tinstalled" in user_ride(
        "status", "package.tmog").stdout
    assert "unchanged" in user_ride("apply", "--profile", PROFILE).stdout

    user_ride("restore", "--run-id", run_id)
    vm.run(f"test ! -e {APPIMAGE} && test ! -e {APPDIR} && "
           f"test ! -e {DESKTOP} && test ! -e {MANIFEST} && "
           f"test \"$(cat {shlex.quote(SENTINEL)})\" = 'keep settings' && "
           f"test \"$(cat {shlex.quote(LICENSE)})\" = 'synthetic entitlement'")
    user_ride("install", "package.tmog", timeout=600)
    vm.run(f"cp -p {APPIMAGE} /tmp/ride-tmog-acceptance.AppImage && "
           f"printf 'modified' >> {APPIMAGE}")
    refused = user_ride("remove", "package.tmog", check=False)
    assert refused.returncode != 0
    vm.run(f"mv -f /tmp/ride-tmog-acceptance.AppImage {APPIMAGE}")
    user_ride("remove", "package.tmog")
    vm.run(f"test ! -e {APPIMAGE} && test ! -e {APPDIR} && "
           f"test ! -e {DESKTOP} && test ! -e {MANIFEST} && "
           f"test \"$(cat {shlex.quote(SENTINEL)})\" = 'keep settings' && "
           f"test \"$(cat {shlex.quote(LICENSE)})\" = 'synthetic entitlement'")
    vm.run(f"sudo {vm.repo}/ride.sh remove --profile {RUNTIME_PROFILE}",
           timeout=600)
    assert vm.run("rpm -q squashfs-tools", check=False).returncode != 0
    if not xvfb_preinstalled:
        vm.run("sudo dnf -y remove xorg-x11-server-Xvfb", timeout=600)
