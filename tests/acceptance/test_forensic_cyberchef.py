"""Pinned offline CyberChef lifecycle on a disposable Fedora Workstation."""

import json
import re

import pytest


OPERATION = "package.cyberchef"
RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")
ENVIRONMENT = "/opt/ride-fedora/cyberchef"
LINK = "/usr/share/applications/ride-cyberchef.desktop"
HTML = f"{ENVIRONMENT}/payload/CyberChef_v11.5.0.html"
LICENSE_SHA = "58d1e17ffe5109a7ae296caafcadfdbe6a7d176f0bc4ab01e12a689b0499d8bd"


def run_id(output):
    match = RUN_ID.search(output)
    assert match, output
    return match.group(1)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_cyberchef_offline_desktop_lifecycle(vm):
    vm.run("command -v firefox && command -v python3")
    vm.run(f"test ! -e {ENVIRONMENT} && test ! -e {LINK}")
    vm.run("sudo mkdir -p /opt/ride-fedora && printf keep | sudo tee /opt/ride-fedora/keep.txt >/dev/null")
    vm.run("mkdir -p ~/Documents && printf keep > ~/Documents/keep.txt")
    plan = vm.ride("plan", "--profile", "forensic-cyberchef")
    assert f"{OPERATION}\tgithub-release-pinned\tabsent\tinstalled\tcandidate" in plan.stdout
    gated = vm.ride("apply", "--profile", "forensic-cyberchef", check=False)
    assert gated.returncode != 0 and "--allow-candidate" in gated.stderr
    applied = vm.ride("apply", "--profile", "forensic-cyberchef",
                      "--allow-candidate", timeout=900)
    first = run_id(applied.stdout)
    record = json.loads(vm.run(f"sudo cat /var/lib/ride-fedora/runs/{first}.json").stdout)
    assert record["status"] == "complete" and record["steps"][0]["result"] == "changed"
    vm.run(f"test -f {HTML} && test -f {ENVIRONMENT}/payload/assets/main.js")
    vm.run(f"test -L {LINK} && test \"$(readlink {LINK})\" = {ENVIRONMENT}/payload/ride-cyberchef.desktop")
    digest = vm.run(f"sha256sum {ENVIRONMENT}/payload/LICENSE").stdout.split()[0]
    assert digest == LICENSE_SHA
    vm.run(f"sudo python3 {vm.repo}/lib/v3/cyberchef_archive.py verify {ENVIRONMENT}/payload {ENVIRONMENT}/manifest.json")
    vm.run(f"grep -F 'Exec=firefox file://{HTML}' {LINK}")
    vm.run("mkdir -p /tmp/ride-cyberchef-firefox")
    vm.run(f"timeout 120 firefox --headless --no-remote --profile /tmp/ride-cyberchef-firefox "
           f"--screenshot /tmp/ride-cyberchef.png file://{HTML}", timeout=150)
    vm.run("test -s /tmp/ride-cyberchef.png")
    assert f"{OPERATION}\tgithub-release-pinned\tinstalled" in vm.ride("status", OPERATION).stdout
    repeated = vm.ride("apply", "--profile", "forensic-cyberchef", "--allow-candidate")
    assert "unchanged" in repeated.stdout
    vm.ride("restore", "--run-id", first, "--allow-candidate", timeout=300)
    vm.run(f"test ! -e {ENVIRONMENT} && test ! -e {LINK}")
    vm.run("test \"$(cat /opt/ride-fedora/keep.txt)\" = keep && test \"$(cat ~/Documents/keep.txt)\" = keep")
    vm.ride("install", OPERATION, "--allow-candidate", timeout=900)
    vm.ride("remove", OPERATION, "--allow-candidate", timeout=300)
    vm.run(f"test ! -e {ENVIRONMENT} && test ! -e {LINK}")
    vm.run("test \"$(cat /opt/ride-fedora/keep.txt)\" = keep && test \"$(cat ~/Documents/keep.txt)\" = keep")
