"""Fedora 44 Server lifecycle for the distro-packaged Selenium bindings."""

import json
import re

import pytest


RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")


def rpm_names(vm):
    return set(vm.run("rpm -qa --qf '%{NAME}\\n'").stdout.splitlines())


@pytest.mark.vm_target("fedora-44-server-x86_64")
def test_server_selenium_bindings_lifecycle(vm):
    original = rpm_names(vm)
    if "python3-selenium" in original:
        vm.run("sudo dnf -y remove python3-selenium", timeout=900)
        assert original - rpm_names(vm) == {"python3-selenium"}
    baseline = rpm_names(vm)

    planned = vm.ride("plan", "--profile", "server-selenium")
    assert "package.python3-selenium\tfedora-rpm\tabsent\tinstalled\tsupported" in planned.stdout
    applied = vm.ride("apply", "--profile", "server-selenium", timeout=900)
    match = RUN_ID.search(applied.stdout)
    assert match, applied.stdout
    journal = json.loads(vm.run(f"sudo cat /var/lib/ride-fedora/runs/{match.group(1)}.json").stdout)
    assert journal["status"] == "complete"
    assert journal["steps"][0]["result"] == "changed"
    assert "python3-selenium" in rpm_names(vm)
    vm.run("rpm -V python3-selenium")
    assert "4.20" in vm.run("python3 -c 'import selenium; print(selenium.__version__)'").stdout
    signature = vm.run("rpm -q --qf '%{RSAHEADER:pgpsig}\\n' python3-selenium").stdout
    assert signature.strip() and "(none)" not in signature.lower()

    repeated = vm.ride("apply", "--profile", "server-selenium")
    assert "unchanged package.python3-selenium" in repeated.stdout
    assert "package.python3-selenium\tfedora-rpm\tinstalled\tsupported" in vm.ride("status", "package.python3-selenium").stdout
    vm.ride("restore", "--run-id", match.group(1), "--dry-run")
    vm.ride("restore", "--run-id", match.group(1), timeout=900)
    assert "python3-selenium" not in rpm_names(vm)
    assert not (baseline - rpm_names(vm)), "RIDE removed a pre-existing RPM"

    installed = vm.ride("install", "package.python3-selenium", timeout=900)
    assert RUN_ID.search(installed.stdout)
    vm.ride("remove", "package.python3-selenium", timeout=900)
    assert "python3-selenium" not in rpm_names(vm)
    assert not (baseline - rpm_names(vm)), "RIDE removed a pre-existing RPM"
