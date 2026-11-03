"""Deep Fedora 44 recovery and boot checks for one selected LUKS mount."""

import json
import shlex
import time
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
OPERATION = "setting.keyfile-mounts"
MAPPER = "ride-acceptance-data"
KEYFILE = "/root/keyfile_ride_acceptance"
MOUNT = "/mnt/ride-acceptance-data"
DISK_ID = "/dev/disk/by-id/virtio-rideextra0"
SENTINEL = MOUNT + "/survives-config-removal.txt"


def reboot_and_wait(vm):
    before = vm.run("cat /proc/sys/kernel/random/boot_id").stdout.strip()
    request = vm.run("sudo systemctl reboot", timeout=30, check=False)
    assert request.returncode in (0, 255), (request.stdout, request.stderr)
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        probe = vm.run("cat /proc/sys/kernel/random/boot_id", timeout=20, check=False)
        if probe.returncode == 0 and probe.stdout.strip() != before:
            return
        time.sleep(3)
    raise AssertionError("Fedora guest did not reboot and reconnect")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
@pytest.mark.vm_extra_disk(size_mib=128)
def test_selected_keyfile_mount_remove_restore_and_boot_recovery(vm):
    catalog = json.loads((ROOT / "catalog/operations.json").read_text(encoding="utf-8"))
    operation = next(item for item in catalog["operations"] if item["id"] == OPERATION)
    assert operation["status"] == "candidate"
    guest_catalog = vm.put_json("keyfile-mounts-acceptance-catalog", catalog)
    profile = {
        "schemaVersion": 1,
        "id": "keyfile-mounts-acceptance",
        "description": "Disposable single-mapper LUKS recovery fixture.",
        "operations": [{"id": OPERATION, "state": "absent", "value": MAPPER}],
    }
    guest_profile = vm.put_json("keyfile-mounts-acceptance-profile", profile)
    vm.run("sudo dnf install -y cryptsetup e2fsprogs util-linux", timeout=600)
    vm.run(f"sudo test -b {DISK_ID}")
    vm.run(f"sudo test ! -e /dev/mapper/{MAPPER} && sudo test ! -L /dev/mapper/{MAPPER}")
    vm.run(f"sudo install -o root -g root -m 0400 /dev/null {KEYFILE}")
    vm.run(f"sudo head -c 64 /dev/urandom | sudo tee {KEYFILE} >/dev/null")
    vm.run(f"sudo chmod 0400 {KEYFILE}")
    vm.run(f"sudo cryptsetup luksFormat --batch-mode --type luks2 --key-file {KEYFILE} {DISK_ID}",
           timeout=300)
    vm.run(f"sudo cryptsetup open --key-file {KEYFILE} {DISK_ID} {MAPPER}", timeout=120)
    vm.run(f"sudo mkfs.ext4 -F /dev/mapper/{MAPPER}", timeout=300)
    vm.run(f"sudo mkdir -p {MOUNT} && sudo mount /dev/mapper/{MAPPER} {MOUNT}")
    vm.run(f"printf 'synthetic encrypted sentinel\\n' | sudo tee {SENTINEL} >/dev/null")
    sentinel_hash = vm.run(f"sudo sha256sum {SENTINEL}").stdout.split()[0]
    vm.run(f"sudo sync && sudo umount {MOUNT} && sudo cryptsetup close {MAPPER}")

    key_hash = vm.run(f"sudo sha256sum {KEYFILE}").stdout.split()[0]
    disk_hash = vm.run(f"sudo sha256sum {DISK_ID}", timeout=120).stdout.split()[0]
    vm.run(f"sudo cryptsetup luksDump {DISK_ID} >/dev/null")
    crypttab_row = f"{MAPPER} {DISK_ID} {KEYFILE} luks\n"
    fstab_row = f"/dev/mapper/{MAPPER} {MOUNT} ext4 defaults 0 2\n"
    vm.run(
        f"printf %s {shlex.quote(crypttab_row)} | sudo tee -a /etc/crypttab >/dev/null && "
        f"printf %s {shlex.quote(fstab_row)} | sudo tee -a /etc/fstab >/dev/null"
    )
    before_crypttab = vm.run("sudo sha256sum /etc/crypttab").stdout.split()[0]
    before_fstab = vm.run("sudo sha256sum /etc/fstab").stdout.split()[0]

    plan = vm.ride("plan", "--profile", guest_profile, "--allow-candidate", catalog=guest_catalog)
    assert OPERATION in plan.stdout and "configured" in plan.stdout and "absent" in plan.stdout
    applied = vm.ride("apply", "--profile", guest_profile, "--allow-candidate", catalog=guest_catalog)
    run_id = applied.stdout.split("Run ID: ", 1)[1].splitlines()[0]
    repeated = vm.ride("apply", "--profile", guest_profile, "--allow-candidate", catalog=guest_catalog)
    assert "unchanged" in repeated.stdout
    status = vm.ride("status", OPERATION, "--value", MAPPER, catalog=guest_catalog)
    assert status.stdout.splitlines()[-1].split("\t")[2] == "absent"
    vm.run(f"sudo test ! -e /dev/mapper/{MAPPER} && sudo test ! -L /dev/mapper/{MAPPER}")
    vm.run(f"! sudo grep -Fq '{MAPPER} ' /etc/crypttab && ! sudo grep -Fq '/dev/mapper/{MAPPER} ' /etc/fstab")
    recovery = vm.run(
        f"sudo find /var/lib/ride-fedora/owned-tools/setting.keyfile-mounts "
        "-name recovery.json -type f -printf '%m:%u:%g\\n'"
    ).stdout.strip()
    assert recovery == "600:root:root"

    reboot_and_wait(vm)
    vm.run(f"sudo test ! -e /dev/mapper/{MAPPER} && sudo test ! -L /dev/mapper/{MAPPER}")
    vm.run(f"! findmnt -rn --mountpoint {MOUNT}")
    assert vm.run(f"sudo sha256sum {KEYFILE}").stdout.split()[0] == key_hash
    assert vm.run(f"sudo sha256sum {DISK_ID}", timeout=120).stdout.split()[0] == disk_hash

    vm.ride("restore", "--run-id", run_id, "--allow-candidate", catalog=guest_catalog)
    assert vm.run("sudo sha256sum /etc/crypttab").stdout.split()[0] == before_crypttab
    assert vm.run("sudo sha256sum /etc/fstab").stdout.split()[0] == before_fstab
    reboot_and_wait(vm)
    vm.run(f"sudo test -b /dev/mapper/{MAPPER}")
    vm.run(f"findmnt -rn --mountpoint {MOUNT} | grep -F '/dev/mapper/{MAPPER}'")
    assert vm.run(f"sudo cat {SENTINEL}").stdout.strip() == "synthetic encrypted sentinel"
    assert vm.run(f"sudo sha256sum {SENTINEL}").stdout.split()[0] == sentinel_hash
    assert vm.run(f"sudo sha256sum {KEYFILE}").stdout.split()[0] == key_hash
    assert vm.run(
        "sudo find /var/lib/ride-fedora/owned-tools/setting.keyfile-mounts "
        "-name recovery.json -type f -print"
    ).stdout == ""
