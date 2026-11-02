"""Install and remove the private WoeUSB tool without touching media."""

import json
import re
import shlex

import pytest


RUNTIME_PROFILE = "fedora-woeusb-runtime"
TOOL_PROFILE = "fedora-woeusb"
PACKAGES = ("parted", "dosfstools", "ntfs-3g", "ntfsprogs", "wimlib-utils",
            "grub2-tools-extra", "wget2-wget")
ENVIRONMENT = "/home/ride-test/.local/opt/ride-fedora/woeusb/5.2.4"
LINK = "/home/ride-test/.local/bin/woeusb"
SCRIPT_SHA = "0b9e502313c6461346cc4d150459b2e1341d30f9ffda005e160829ad9d5bfffc"
LICENSE_SHA = "2ca9503d76d1ffab14f599b4741382eec11face60ad1f0d7a41897809003a286"
RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")


def run_id(output):
    match = RUN_ID.search(output)
    assert match, output
    return match.group(1)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_woeusb_private_tool_lifecycle(vm):
    original = set(vm.run("rpm -qa --qf '%{NAME}\\n'").stdout.splitlines())
    vm.run(f"test ! -e {ENVIRONMENT} && test ! -e {LINK}")
    runtime_applied = vm.ride("apply", "--profile", RUNTIME_PROFILE, "--allow-candidate", timeout=1500)
    runtime_run = run_id(runtime_applied.stdout)
    installed_rpms = set(vm.run("rpm -qa --qf '%{NAME}\\n'").stdout.splitlines())
    assert set(PACKAGES) <= installed_rpms
    for package in PACKAGES:
        vm.run(f"rpm -V {package}")
    for command in ("parted", "wimlib-imagex", "mkfs.vfat", "mkntfs", "wget"):
        vm.run(f"command -v {command}")
    assert vm.run("command -v grub2-install || command -v grub-install", check=False).returncode == 0
    runtime_repeat = vm.ride("apply", "--profile", RUNTIME_PROFILE, "--allow-candidate")
    assert runtime_repeat.stdout.count("unchanged") == len(PACKAGES)
    for package in PACKAGES:
        assert f"package.{package}" in vm.ride("status", f"package.{package}").stdout

    def user_ride(*args, timeout=120, check=True):
        return vm.run(shlex.join((f"{vm.repo}/ride.sh", *args)), timeout=timeout, check=check)

    plan = user_ride("plan", "--profile", TOOL_PROFILE)
    assert "package.woeusb" in plan.stdout
    gate = user_ride("apply", "--profile", TOOL_PROFILE, check=False)
    assert gate.returncode != 0 and "--allow-candidate" in gate.stderr
    applied = user_ride("apply", "--profile", TOOL_PROFILE, "--allow-candidate", timeout=300)
    user_run = run_id(applied.stdout)
    record = json.loads(vm.run(f"cat /home/ride-test/.local/state/ride-fedora/runs/{user_run}.json").stdout)
    assert record["status"] == "complete"
    assert vm.run(f"test -x {ENVIRONMENT}/woeusb-5.2.4.bash && test -L {LINK}")
    hashes = vm.run(f"sha256sum {ENVIRONMENT}/woeusb-5.2.4.bash {ENVIRONMENT}/LICENSE").stdout.splitlines()
    assert hashes[0].split()[0] == SCRIPT_SHA
    assert hashes[1].split()[0] == LICENSE_SHA
    version = vm.run(f"{LINK} --version", timeout=120)
    assert "5.2.4" in version.stdout + version.stderr
    help_text = vm.run(
        f"TERM=xterm python3 -c 'import pty; pty.spawn([\"{LINK}\", \"--help\"])'",
        timeout=120)
    assert "--device" in help_text.stdout + help_text.stderr
    assert "package.woeusb\tgithub-release-pinned\tinstalled" in user_ride(
        "status", "package.woeusb").stdout
    repeated = user_ride("apply", "--profile", TOOL_PROFILE, "--allow-candidate")
    assert "unchanged" in repeated.stdout
    user_ride("restore", "--run-id", user_run, "--allow-candidate")
    vm.run(f"test ! -e {ENVIRONMENT} && test ! -e {LINK}")
    user_ride("install", "package.woeusb", "--allow-candidate", timeout=300)
    user_ride("remove", "package.woeusb", "--allow-candidate")
    vm.run(f"test ! -e {ENVIRONMENT} && test ! -e {LINK}")
    vm.ride("restore", "--run-id", runtime_run, "--allow-candidate", timeout=1200)
    final = set(vm.run("rpm -qa --qf '%{NAME}\\n'").stdout.splitlines())
    assert set(PACKAGES) & original <= final
    assert not (set(PACKAGES) - original) & final
