"""Fedora 44 sudoers scope and exact recovery for SSH-triggered reboot policy."""

import json
from pathlib import Path
import time

import pytest

ROOT = Path(__file__).resolve().parents[2]
OPERATION = "setting.ssh-reboot"
PRINCIPAL = "ride-ssh-target"
RULE = f"/etc/sudoers.d/allowsshreboot_{PRINCIPAL}"
UNRELATED = "/etc/sudoers.d/ride-ssh-reboot-unrelated"
CONFLICT = "/etc/sudoers.d/allowsshreboot_ride-conflict"


def fixtures(vm):
    catalog = json.loads((ROOT / "catalog/operations.json").read_text(encoding="utf-8"))
    profile = {
        "schemaVersion": 1,
        "id": "ssh-reboot-acceptance",
        "description": "Disposable named-user SSH reboot sudoers lifecycle.",
        "operations": [{"id": OPERATION, "state": "configured", "value": PRINCIPAL}],
    }
    conflict_profile = {
        "schemaVersion": 1,
        "id": "ssh-reboot-conflict-acceptance",
        "description": "Refuse an existing principal-specific sudoers file.",
        "operations": [{"id": OPERATION, "state": "configured", "value": "ride-conflict"}],
    }
    return (
        vm.put_json("ssh-reboot-acceptance-catalog", catalog),
        vm.put_json("ssh-reboot-acceptance-profile", profile),
        vm.put_json("ssh-reboot-conflict-profile", conflict_profile),
    )


def sha256(vm, path):
    result = vm.run(f"sudo sha256sum {path}")
    return result.stdout.split()[0]


def ssh_command(vm, user, command, *, timeout=45):
    return vm._command(
        ["ssh", *vm._ssh_options(), "-p", str(vm.port),
         f"{user}@127.0.0.1", command],
        timeout=timeout,
        check=False,
    )


def reboot_and_reconnect(vm, unrelated_hash):
    public_key = vm.key.with_suffix(".pub").read_text(encoding="ascii").strip()
    assert public_key.startswith("ssh-ed25519 ")
    vm.run(
        f"sudo install -d -m 0700 -o {PRINCIPAL} -g {PRINCIPAL} "
        f"/home/{PRINCIPAL}/.ssh && printf '%s\\n' {json.dumps(public_key)} | "
        f"sudo tee /home/{PRINCIPAL}/.ssh/authorized_keys >/dev/null && "
        f"sudo chown {PRINCIPAL}:{PRINCIPAL} /home/{PRINCIPAL}/.ssh/authorized_keys && "
        f"sudo chmod 0600 /home/{PRINCIPAL}/.ssh/authorized_keys && "
        "sudo systemctl enable --now sshd.service"
    )
    old_boot_id = vm.run("cat /proc/sys/kernel/random/boot_id").stdout.strip()

    # No -t option is passed: this exercises the command through non-TTY SSH.
    request = ssh_command(vm, PRINCIPAL, "sudo -n /usr/bin/systemctl reboot")
    assert request.returncode in (0, 255), (request.stdout, request.stderr)

    deadline = time.monotonic() + 600
    new_boot_id = ""
    while time.monotonic() < deadline:
        probe = vm.run("cat /proc/sys/kernel/random/boot_id", timeout=20, check=False)
        if probe.returncode == 0:
            observed = probe.stdout.strip()
            if observed and observed != old_boot_id:
                new_boot_id = observed
                break
        time.sleep(3)
    assert new_boot_id and new_boot_id != old_boot_id, "guest did not reboot and return over SSH"

    reconnected = ssh_command(vm, PRINCIPAL, "id -un")
    assert reconnected.returncode == 0, reconnected.stderr
    assert reconnected.stdout.strip() == PRINCIPAL
    listing = vm.run(f"sudo sudo -l -U {PRINCIPAL}").stdout
    assert f"(root) NOPASSWD: /usr/bin/systemctl reboot" in listing
    assert sha256(vm, UNRELATED) == unrelated_hash
    vm.run("sudo visudo -c")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_named_user_reboot_rule_is_scoped_and_exactly_restored(vm):
    catalog, profile, conflict_profile = fixtures(vm)
    vm.run(f"sudo useradd --create-home --shell /bin/bash {PRINCIPAL}")
    vm.run("sudo useradd --create-home --shell /bin/bash ride-conflict")
    vm.run("printf '# RIDE acceptance seeded unrelated policy\\n' | sudo tee "
           f"{UNRELATED} >/dev/null && sudo chown root:root {UNRELATED} && sudo chmod 0440 {UNRELATED}")
    vm.run("sudo visudo -c")
    unrelated_hash = sha256(vm, UNRELATED)
    vm.run(f"sudo test ! -e {RULE} && sudo test ! -L {RULE}")

    planned = vm.ride("plan", "--profile", profile, catalog=catalog)
    assert OPERATION in planned.stdout
    applied = vm.ride("apply", "--profile", profile, "--allow-candidate", catalog=catalog)
    run_id = applied.stdout.split("Run ID: ", 1)[1].splitlines()[0]
    vm.run(f"sudo test -f {RULE} && sudo test ! -L {RULE}")
    vm.run(f"sudo test \"$(sudo stat -c '%u:%g:%a' {RULE})\" = 0:0:440")
    vm.run(f"sudo grep -Fx '{PRINCIPAL} ALL=(root) NOPASSWD: /usr/bin/systemctl reboot' {RULE}")
    listing = vm.run(f"sudo sudo -l -U {PRINCIPAL}").stdout
    assert f"(root) NOPASSWD: /usr/bin/systemctl reboot" in listing
    assert "NOPASSWD: ALL" not in listing
    assert f"/usr/bin/systemctl " not in listing.replace(
        f"/usr/bin/systemctl reboot", ""
    )
    vm.run("sudo visudo -c")
    assert sha256(vm, UNRELATED) == unrelated_hash

    repeated = vm.ride("apply", "--profile", profile, "--allow-candidate", catalog=catalog)
    assert "unchanged" in repeated.stdout
    status = vm.ride("status", OPERATION, "--value", PRINCIPAL, catalog=catalog)
    assert "configured" in status.stdout
    unprivileged_status = vm.run(
        f"{vm.repo}/ride.sh status {OPERATION} --value {PRINCIPAL}"
    )
    assert "requires-root" in unprivileged_status.stdout

    vm.run(f"printf '# seeded conflicting file\\n' | sudo tee {CONFLICT} >/dev/null && "
           f"sudo chown root:root {CONFLICT} && sudo chmod 0440 {CONFLICT}")
    conflict_hash = sha256(vm, CONFLICT)
    refused = vm.ride("apply", "--profile", conflict_profile, "--allow-candidate",
                      catalog=catalog, check=False)
    assert "pre-existing or modified" in refused.stderr or "already exists" in refused.stderr
    assert sha256(vm, CONFLICT) == conflict_hash

    reboot_and_reconnect(vm, unrelated_hash)

    vm.ride("restore", "--run-id", run_id, "--allow-candidate", catalog=catalog)
    vm.run(f"sudo test ! -e {RULE} && sudo test ! -L {RULE}")
    assert sha256(vm, UNRELATED) == unrelated_hash
    vm.run("sudo visudo -c")
    vm.run(f"sudo rm -f {UNRELATED} {CONFLICT} && sudo userdel -r {PRINCIPAL} && "
           "sudo userdel -r ride-conflict")
    vm.run("sudo visudo -c")
