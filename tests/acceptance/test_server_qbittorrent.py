"""Package-only lifecycle for the Fedora Server qBittorrent headless RPM."""

import json
import re

import pytest


RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")
OPERATION = "package.qbittorrent-nox"
PACKAGE = "qbittorrent-nox"


def package_inventory(vm):
    return vm.run("rpm -qa --qf '%{NAME}\\t%{EPOCH}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' | sort").stdout


def run_id(output):
    match = RUN_ID.search(output)
    assert match, output
    return match.group(1)


@pytest.mark.vm_target("fedora-44-server-x86_64")
def test_qbittorrent_nox_package_only_lifecycle(vm):
    initial = package_inventory(vm)
    if vm.run(f"rpm -q --quiet {PACKAGE}", check=False).returncode == 0:
        vm.run(f"sudo dnf -y remove {PACKAGE}", timeout=900)
        assert PACKAGE not in vm.run("rpm -qa --qf '%{NAME}\\n'").stdout.splitlines()
    baseline = package_inventory(vm)
    unit_before = vm.run("test -e /etc/systemd/system/qbittorrent.service", check=False).returncode
    user_before = vm.run("getent passwd qbittorrent", check=False).stdout
    profile = vm.put_json("qbittorrent-package-profile", {
        "schemaVersion": 1,
        "id": "qbittorrent-package-acceptance",
        "description": "Disposable package-only acceptance",
        "operations": [{"id": OPERATION, "state": "installed"}],
    })

    plan = vm.ride("plan", "--profile", profile)
    assert f"{OPERATION}\tfedora-rpm\tabsent\tinstalled\tcandidate" in plan.stdout
    applied = vm.ride("apply", "--profile", profile, "--allow-candidate", timeout=900)
    first = run_id(applied.stdout)
    record = json.loads(vm.run(f"sudo cat /var/lib/ride-fedora/runs/{first}.json").stdout)
    assert record["status"] == "complete"
    assert record["steps"][0]["result"] == "changed"
    signature = vm.run(f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {PACKAGE}").stdout
    assert any(line.strip() not in ("", "(none)") for line in signature.splitlines())
    vm.run(f"rpm -V {PACKAGE}")
    vm.run("test -x /usr/bin/qbittorrent-nox")
    assert f"{OPERATION}\tfedora-rpm\tinstalled" in vm.ride("status", OPERATION).stdout
    repeated = vm.ride("apply", "--profile", profile, "--allow-candidate")
    assert "unchanged " + OPERATION in repeated.stdout
    assert vm.run("test -e /etc/systemd/system/qbittorrent.service", check=False).returncode == unit_before
    assert vm.run("getent passwd qbittorrent", check=False).stdout == user_before
    assert vm.run("systemctl is-active qbittorrent-nox@ride-test.service",
                  check=False).stdout.strip() != "active"
    enabled = vm.run("systemctl is-enabled qbittorrent-nox@ride-test.service", check=False)
    assert enabled.stdout.strip() not in ("enabled", "enabled-runtime")

    vm.ride("restore", "--run-id", first, "--allow-candidate", "--dry-run")
    vm.ride("restore", "--run-id", first, "--allow-candidate", timeout=900)
    assert vm.run(f"rpm -q --quiet {PACKAGE}", check=False).returncode != 0
    assert package_inventory(vm) == baseline
    installed = vm.ride("install", OPERATION, "--allow-candidate", timeout=900)
    assert RUN_ID.search(installed.stdout)
    vm.ride("remove", OPERATION, "--allow-candidate", timeout=900)
    assert vm.run(f"rpm -q --quiet {PACKAGE}", check=False).returncode != 0
    assert package_inventory(vm) == baseline
    assert vm.run("test -e /etc/systemd/system/qbittorrent.service", check=False).returncode == unit_before
    assert vm.run("getent passwd qbittorrent", check=False).stdout == user_before
    assert vm.run("systemctl is-active qbittorrent-nox@ride-test.service",
                  check=False).stdout.strip() != "active"
    assert not (set(initial.splitlines()) - set(baseline.splitlines())) - {
        line for line in initial.splitlines() if line.startswith(PACKAGE + "\t")
    }
