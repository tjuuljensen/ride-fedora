"""Fedora 44 Server SSH root-login policy and session-preserving recovery."""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
OPERATION = "setting.ssh-root-login"
DROPIN = "/etc/ssh/sshd_config.d/00-ride-root-login.conf"


def fixtures(vm):
    catalog = json.loads((ROOT / "catalog/operations.json").read_text(encoding="utf-8"))
    profile = {
        "schemaVersion": 1,
        "id": "sshd-root-login-acceptance",
        "description": "Disposable SSH root-login policy lifecycle fixture.",
        "operations": [{"id": OPERATION, "state": "configured"}],
    }
    return (vm.put_json("sshd-root-login-acceptance-catalog", catalog),
            vm.put_json("sshd-root-login-acceptance-profile", profile))


def effective_root_policy(vm):
    return vm.run(
        "host=$(hostname -f 2>/dev/null || hostname); "
        "sudo sshd -T -C \"user=root,host=$host,addr=127.0.0.1\" | "
        "awk 'tolower($1) == \"permitrootlogin\" {print tolower($2); exit}'"
    ).stdout.strip()


@pytest.mark.vm_target("fedora-44-server-x86_64")
def test_sshd_root_login_policy_reload_and_exact_restore(vm):
    catalog, profile = fixtures(vm)
    vm.run("systemctl is-active sshd.service | grep -Fx active")
    vm.run("sudo sshd -t")
    vm.run(f"sudo test ! -e {DROPIN} && sudo test ! -L {DROPIN}")
    prior_policy = effective_root_policy(vm)
    assert prior_policy in {"yes", "prohibit-password", "forced-commands-only", "no"}

    planned = vm.ride("plan", "--profile", profile, catalog=catalog)
    assert OPERATION in planned.stdout
    applied = vm.ride("apply", "--profile", profile, "--allow-candidate", catalog=catalog)
    run_id = applied.stdout.split("Run ID: ", 1)[1].splitlines()[0]
    vm.run("sudo sshd -t")
    assert effective_root_policy(vm) == "no"
    vm.run(f"sudo grep -Fx 'PermitRootLogin no' {DROPIN}")
    vm.run("systemctl is-active sshd.service | grep -Fx active")
    vm.run("id -un | grep -Fx ride-test")  # A new SSH channel works after reload.

    repeated = vm.ride("apply", "--profile", profile, "--allow-candidate", catalog=catalog)
    assert "unchanged" in repeated.stdout
    assert OPERATION in vm.ride("status", OPERATION, catalog=catalog).stdout

    vm.ride("restore", "--run-id", run_id, "--allow-candidate", catalog=catalog)
    vm.run("sudo test ! -e " + DROPIN)
    vm.run("sudo sshd -t")
    assert effective_root_policy(vm) == prior_policy
    vm.run("systemctl is-active sshd.service | grep -Fx active")
    vm.run("id -un | grep -Fx ride-test")
