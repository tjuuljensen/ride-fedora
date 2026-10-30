"""Pinned Chepy sdist and Python 3.12 lifecycle on disposable Workstation."""

import json
import re
import shlex

import pytest


RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")
ENVIRONMENT = "/home/ride-test/.local/share/ride-fedora/tools/chepy"
LINK = "/home/ride-test/.local/bin/chepy"
SOURCE_SHA = "f6084689e43d128748c18f79c79d75539abb67ac8245e950b678cfa0da2f5010"


def run_id(output):
    match = RUN_ID.search(output)
    assert match, output
    return match.group(1)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_chepy_runtime_and_user_cli(vm):
    original = set(vm.run("rpm -qa --qf '%{NAME}\\n'").stdout.splitlines())
    sibling = "/home/ride-test/.local/share/ride-fedora/tools/keep.txt"
    vm.run(f"mkdir -p {ENVIRONMENT.rsplit('/', 1)[0]} && printf keep > {sibling}")
    vm.run(f"test ! -e {ENVIRONMENT} && test ! -e {LINK}")

    system_plan = vm.ride("plan", "--profile", "chepy-runtime")
    assert "package.python3.12" in system_plan.stdout
    system_apply = vm.ride("apply", "--profile", "chepy-runtime", "--allow-candidate",
                           timeout=1800)
    system_run = run_id(system_apply.stdout)
    system_record = json.loads(vm.run(
        f"sudo cat /var/lib/ride-fedora/runs/{system_run}.json").stdout)
    assert system_record["status"] == "complete"
    vm.run("rpm -q python3.12")
    signature = vm.run("rpm -q --qf '%{SIGPGP:pgpsig}\\n%{RSAHEADER:pgpsig}\\n' python3.12").stdout
    assert any(line.strip() not in ("", "(none)") for line in signature.splitlines())
    vm.run("rpm -V python3.12")
    vm.run("python3.12 --version")
    repeat_system = vm.ride("apply", "--profile", "chepy-runtime", "--allow-candidate")
    assert "unchanged" in repeat_system.stdout

    def ride(*args, timeout=120, check=True):
        return vm.run(shlex.join((f"{vm.repo}/ride.sh", *args)), timeout=timeout,
                      check=check)

    plan = ride("plan", "--profile", "forensic-chepy")
    assert "package.chepy\tpypi-sdist-venv\tabsent\tinstalled\tcandidate" in plan.stdout
    gate = ride("apply", "--profile", "forensic-chepy", check=False)
    assert gate.returncode != 0 and "--allow-candidate" in gate.stderr
    applied = ride("apply", "--profile", "forensic-chepy", "--allow-candidate",
                   timeout=1800)
    user_run = run_id(applied.stdout)
    user_record = json.loads(vm.run(
        f"cat /home/ride-test/.local/state/ride-fedora/runs/{user_run}.json").stdout)
    assert user_record["status"] == "complete"
    assert user_record["steps"][0]["result"] == "changed"
    vm.run(f"test -x {ENVIRONMENT}/venv/bin/chepy && test -L {LINK} && "
           f"test \"$(readlink {LINK})\" = {ENVIRONMENT}/venv/bin/chepy")
    source_hash = vm.run(f"sha256sum {ENVIRONMENT}/chepy-7.6.0.tar.gz").stdout.split()[0]
    assert source_hash == SOURCE_SHA
    vm.run(f"{ENVIRONMENT}/venv/bin/python -c 'import chepy; import importlib.metadata as m; "
           "assert m.version(\"chepy\") == \"7.6.0\"'")
    help_result = vm.run(f"timeout 120 {LINK} --help", timeout=150)
    assert "Chepy" in help_result.stdout + help_result.stderr or "chepy" in help_result.stdout + help_result.stderr
    vm.run(f"cat {ENVIRONMENT}/dependencies.txt")
    assert "package.chepy\tpypi-sdist-venv\tinstalled" in ride("status", "package.chepy").stdout
    repeat_user = ride("apply", "--profile", "forensic-chepy", "--allow-candidate")
    assert "unchanged" in repeat_user.stdout
    ride("restore", "--run-id", user_run, "--allow-candidate")
    vm.run(f"test ! -e {ENVIRONMENT} && test ! -e {LINK} && test \"$(cat {sibling})\" = keep")
    ride("install", "package.chepy", "--allow-candidate", timeout=1800)
    ride("remove", "package.chepy", "--allow-candidate")
    vm.run(f"test ! -e {ENVIRONMENT} && test ! -e {LINK} && test \"$(cat {sibling})\" = keep")
    vm.ride("restore", "--run-id", system_run, "--allow-candidate", timeout=1800)
    restored = set(vm.run("rpm -qa --qf '%{NAME}\\n'").stdout.splitlines())
    assert not (original - restored), "restore removed a pre-existing RPM"
