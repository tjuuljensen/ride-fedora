"""Disposable Fedora 44 VeraCrypt install recovery preserves test volumes."""

import re

import pytest


RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")
PROFILE = "fedora-veracrypt"
VOLUME = "/var/tmp/ride-veracrypt-acceptance.hc"
MOUNT = "/mnt/ride-veracrypt-acceptance"
PASSWORD = "ride-acceptance-only-password"
SENTINEL = MOUNT + "/survives-package-removal.txt"


def apply(vm):
    result = vm.ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=1200)
    match = RUN_ID.search(result.stdout)
    assert match, result.stdout
    return match.group(1)


def fail_dnf_before_transaction(vm):
    mock_bin = "/tmp/ride-veracrypt-fail-bin"
    mock_tmp = "/tmp/ride-veracrypt-fail-tmp"
    vm.run(f"sudo mkdir -p {mock_bin} {mock_tmp}")
    vm.run(f"printf '#!/bin/sh\\nexit 75\\n' | sudo tee {mock_bin}/dnf >/dev/null")
    vm.run(f"sudo chmod 0755 {mock_bin}/dnf")
    failed = vm.run(
        f"sudo env PATH={mock_bin}:$PATH TMPDIR={mock_tmp} "
        f"{vm.repo}/ride.sh apply --profile {PROFILE} --allow-candidate",
        check=False, timeout=1200)
    assert failed.returncode != 0
    assert "package.veracrypt" in failed.stdout + failed.stderr
    assert vm.run("rpm -q --quiet veracrypt", check=False).returncode != 0
    assert vm.run(f"sudo find {mock_tmp} -mindepth 1 -maxdepth 1 | grep -q .", check=False).returncode != 0
    vm.run(f"sudo rm -rf {mock_bin} {mock_tmp}")


def mount(vm):
    vm.run(
        f"printf '%s\\n' '{PASSWORD}' | sudo veracrypt -t --non-interactive --stdin "
        f"--pim=0 --protect-hidden=no {VOLUME} {MOUNT}", timeout=120)


def unmount(vm):
    vm.run(f"sudo veracrypt -t --unmount {VOLUME}", timeout=120)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_veracrypt_rpm_lifecycle_preserves_mounted_and_unmounted_test_volume(vm):
    vm.run("sudo dnf install -y cryptsetup fuse3 util-linux", timeout=300)
    vm.run(f"sudo mkdir -p {MOUNT}")
    vm.run(f"sudo rm -f {VOLUME}")
    refused = vm.ride("apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    assert vm.run("rpm -q --quiet veracrypt", check=False).returncode != 0
    plan = vm.ride("plan", "--profile", PROFILE, "--allow-candidate")
    assert "package.veracrypt" in plan.stdout
    fail_dnf_before_transaction(vm)
    apply(vm)
    vm.run("rpm -q veracrypt")
    help_result = vm.run("veracrypt -t --help", check=False)
    assert help_result.returncode == 0, help_result.stderr
    vm.run(
        f"printf 'y\\n' | sudo veracrypt -t --create {VOLUME} --volume-type=normal --encryption=AES "
        f"--hash=SHA-512 --filesystem=FAT --size=16M --password={PASSWORD} "
        "--pim=0 --keyfiles= --random-source=/dev/urandom --quick", timeout=600)
    mount(vm)
    vm.run(f"printf 'preserved volume data\\n' | sudo tee {SENTINEL} >/dev/null")

    # Refuse removal while mounted, leaving the app and volume untouched.
    blocked = vm.ride("remove", "--profile", PROFILE, "--allow-candidate",
                      check=False, timeout=1200)
    assert blocked.returncode != 0
    assert "unmount them before removing" in blocked.stderr
    assert vm.run(f"sudo cat {SENTINEL}").stdout.strip() == "preserved volume data"
    assert vm.run("rpm -q --quiet veracrypt").returncode == 0
    unmount(vm)
    volume_hash = vm.run(f"sudo sha256sum {VOLUME}").stdout.split()[0]
    vm.ride("remove", "--profile", PROFILE, "--allow-candidate", timeout=1200)
    assert vm.run("rpm -q --quiet veracrypt", check=False).returncode != 0
    assert vm.run(f"sudo sha256sum {VOLUME}").stdout.split()[0] == volume_hash

    # A second package install leaves an unmounted volume intact and readable.
    apply(vm)
    mount(vm)
    assert vm.run(f"sudo cat {SENTINEL}").stdout.strip() == "preserved volume data"
    unmount(vm)
    assert vm.run(f"sudo sha256sum {VOLUME}").stdout.split()[0] == volume_hash
    vm.ride("remove", "--profile", PROFILE, "--allow-candidate", timeout=1200)
    assert vm.run("rpm -q --quiet veracrypt", check=False).returncode != 0
