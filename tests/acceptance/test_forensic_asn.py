"""Pinned ASN script and Fedora prerequisites on a disposable Workstation."""

import json
import re
import shlex

import pytest


PACKAGES = ("curl", "whois", "bind-utils", "mtr", "jq", "nmap",
            "nmap-ncat", "ipcalc", "aha", "grepcidr")
OPERATION_IDS = ("curl", "whois", "dns-utils", "mtr", "jq", "nmap",
                 "ncat", "ipcalc", "aha", "grepcidr")
RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")
ENVIRONMENT = "/home/ride-test/.local/share/ride-fedora/tools/asn"
LINK = "/home/ride-test/.local/bin/asn"
SCRIPT_SHA = "dee866df4d5d8ea26784611512d5dc962a1a6dbe33cbb20d9d23e7b492378d75"
LICENSE_SHA = "7ba6dff361f2da0b9712fcc13960ba3d04d85cb9d073c97c5367241fdc2c8868"


def run_id(output):
    match = RUN_ID.search(output)
    assert match, output
    return match.group(1)


def rpm_names(vm):
    return set(vm.run("rpm -qa --qf '%{NAME}\\n'").stdout.splitlines())


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_asn_runtime_and_user_tool(vm):
    original = rpm_names(vm)
    sibling = "/home/ride-test/.local/share/ride-fedora/tools/keep.txt"
    vm.run(f"mkdir -p {ENVIRONMENT.rsplit('/', 1)[0]} && printf keep > {sibling}")
    vm.run(f"test ! -e {ENVIRONMENT} && test ! -e {LINK}")
    system_plan = vm.ride("plan", "--profile", "asn-runtime").stdout
    assert all(f"package.{name}" in system_plan for name in OPERATION_IDS)
    system_apply = vm.ride("apply", "--profile", "asn-runtime", "--allow-candidate",
                           timeout=1800)
    system_run = run_id(system_apply.stdout)
    system_record = json.loads(vm.run(f"sudo cat /var/lib/ride-fedora/runs/{system_run}.json").stdout)
    assert system_record["status"] == "complete"
    assert len(system_record["steps"]) == len(PACKAGES)
    assert set(PACKAGES) <= rpm_names(vm)
    for package in PACKAGES:
        signature = vm.run(f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}").stdout
        assert any(line.strip() not in ("", "(none)") for line in signature.splitlines())
        vm.run(f"rpm -V {package}")
    repeated = vm.ride("apply", "--profile", "asn-runtime", "--allow-candidate",
                       timeout=900)
    assert repeated.stdout.count("unchanged") == len(PACKAGES)

    def user_ride(*args, timeout=120, check=True):
        return vm.run(shlex.join((f"{vm.repo}/ride.sh", *args)), timeout=timeout,
                      check=check)

    plan = user_ride("plan", "--profile", "asn-tool")
    assert "package.asn\tgithub-raw-pinned\tabsent\tinstalled\tcandidate" in plan.stdout
    gated = user_ride("apply", "--profile", "asn-tool", timeout=120, check=False)
    assert gated.returncode != 0 and "--allow-candidate" in gated.stderr
    applied = user_ride("apply", "--profile", "asn-tool", "--allow-candidate", timeout=300)
    user_run = run_id(applied.stdout)
    user_record = json.loads(vm.run(f"cat /home/ride-test/.local/state/ride-fedora/runs/{user_run}.json").stdout)
    assert user_record["status"] == "complete"
    assert user_record["steps"][0]["result"] == "changed"
    vm.run(f"test -x {ENVIRONMENT}/asn && test -L {LINK} && test \"$(readlink {LINK})\" = {ENVIRONMENT}/asn")
    hashes = vm.run(f"sha256sum {ENVIRONMENT}/asn {ENVIRONMENT}/LICENSE").stdout.splitlines()
    assert hashes[0].split()[0] == SCRIPT_SHA
    assert hashes[1].split()[0] == LICENSE_SHA
    help_result = vm.run(f"{LINK} -h", timeout=120)
    assert "ASN" in help_result.stdout + help_result.stderr
    assert "package.asn\tgithub-raw-pinned\tinstalled" in user_ride("status", "package.asn").stdout
    repeat_user = user_ride("apply", "--profile", "asn-tool", "--allow-candidate")
    assert "unchanged" in repeat_user.stdout
    user_ride("restore", "--run-id", user_run, "--allow-candidate")
    vm.run(f"test ! -e {ENVIRONMENT} && test ! -e {LINK} && test \"$(cat {sibling})\" = keep")
    user_ride("install", "package.asn", "--allow-candidate", timeout=300)
    user_ride("remove", "package.asn", "--allow-candidate")
    vm.run(f"test ! -e {ENVIRONMENT} && test ! -e {LINK} && test \"$(cat {sibling})\" = keep")
    vm.ride("restore", "--run-id", system_run, "--allow-candidate", timeout=1800)
    assert not (original - rpm_names(vm)), "restore removed a pre-existing RPM"
