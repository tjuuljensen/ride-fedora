"""Disposable Fedora Server lifecycle for the shared Python pip RPM."""

import json
import re

import pytest


RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")


def rpm_names(vm):
    return set(vm.run("rpm -qa --qf '%{NAME}\\n'").stdout.splitlines())


@pytest.mark.vm_target("fedora-44-server-x86_64")
def test_server_python3_pip_lifecycle(vm):
    original = rpm_names(vm)
    if "python3-pip" in original:
        vm.run("sudo dnf -y remove python3-pip", timeout=900)
        assert original - rpm_names(vm) == {"python3-pip"}
    baseline = rpm_names(vm)
    planned = vm.ride("plan", "--profile", "server-python-tools")
    assert "package.python3-pip\tfedora-rpm\tabsent\tinstalled\tsupported" in planned.stdout
    changed = vm.ride("apply", "--profile", "server-python-tools", timeout=900)
    match = RUN_ID.search(changed.stdout)
    assert match, changed.stdout
    record = json.loads(vm.run(f"sudo cat /var/lib/ride-fedora/runs/{match.group(1)}.json").stdout)
    assert record["status"] == "complete"
    assert record["steps"][0]["result"] == "changed"
    assert "python3-pip" in rpm_names(vm)
    signature = vm.run("rpm -q --qf '%{SIGPGP:pgpsig}\\n%{RSAHEADER:pgpsig}\\n' python3-pip").stdout
    assert any(line.strip() not in ("", "(none)") for line in signature.splitlines())
    vm.run("rpm -V python3-pip")
    assert "pip " in vm.run("python3 -m pip --version").stdout
    repeated = vm.ride("apply", "--profile", "server-python-tools")
    assert "unchanged package.python3-pip" in repeated.stdout
    assert "package.python3-pip\tfedora-rpm\tinstalled" in vm.ride("status", "package.python3-pip").stdout
    vm.ride("restore", "--run-id", match.group(1), "--dry-run")
    vm.ride("restore", "--run-id", match.group(1), timeout=900)
    assert "python3-pip" not in rpm_names(vm)
    assert not (baseline - rpm_names(vm)), "RIDE removed a pre-existing RPM"
    installed = vm.ride("install", "package.python3-pip", timeout=900)
    assert RUN_ID.search(installed.stdout)
    vm.ride("remove", "package.python3-pip", timeout=900)
    assert "python3-pip" not in rpm_names(vm)
    assert not (baseline - rpm_names(vm)), "RIDE removed a pre-existing RPM"
