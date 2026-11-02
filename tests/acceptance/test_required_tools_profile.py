"""Fedora 44 Workstation migration check for v2 InstallRequired tools."""

import json
import re

import pytest

PROFILE = "required-tools"
PACKAGES = {
    "package.coreutils": ("coreutils", ("/usr/bin/id", "--version")),
    "package.git": ("git", ("git", "--version")),
    "package.gnupg2": ("gnupg2", ("gpg", "--version")),
    "package.python-command": ("python-unversioned-command", ("python", "--version")),
    "package.tar": ("tar", ("tar", "--version")),
    "package.wget": ("wget2-wget", ("wget", "--version")),
    "package.gcc": ("gcc", ("gcc", "--version")),
}
RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")


def inventory(vm):
    return vm.run("rpm -qa --qf '%{NAME}.%{ARCH}\\t%{VERSION}-%{RELEASE}\\t%{RSAHEADER:pgpsig}\\n' | sort").stdout


def run_id(output):
    match = RUN_ID.search(output)
    assert match, output
    return match.group(1)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_required_tools_profile_keeps_one_way_rpm_capabilities(vm):
    before = inventory(vm)
    initial_names_arch = {row.split("\t", 1)[0] for row in before.splitlines()}
    assert "wget2-wget.x86_64" in initial_names_arch
    planned = vm.ride("plan", "--profile", PROFILE)
    for identifier in PACKAGES:
        assert identifier in planned.stdout and "candidate" in planned.stdout
    refused = vm.ride("apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr

    applied = vm.ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=1500)
    identifier = run_id(applied.stdout)
    journal = json.loads(vm.run(f"sudo cat /var/lib/ride-fedora/runs/{identifier}.json").stdout)
    assert journal["status"] == "complete"
    assert {step["id"] for step in journal["steps"]} == set(PACKAGES)

    installed_inventory = inventory(vm)
    installed_names_arch = {row.split("\t", 1)[0] for row in installed_inventory.splitlines()}
    assert installed_names_arch >= initial_names_arch
    for operation, (rpm, command) in PACKAGES.items():
        assert vm.run(f"rpm -q {rpm}").returncode == 0
        signature = vm.run(f"rpm -q --qf '%{{RSAHEADER:pgpsig}}\\n' {rpm}").stdout.lower()
        assert "(none)" not in signature and signature.strip()
        vm.run(f"rpm -V {rpm}")
        vm.run(" ".join(command))
        assert operation in vm.ride("status", operation).stdout

    repeated = vm.ride("apply", "--profile", PROFILE, "--allow-candidate")
    assert all(f"unchanged {operation}" in repeated.stdout for operation in PACKAGES)
    removed = vm.ride("remove", "--profile", PROFILE, "--allow-candidate")
    assert all(f"kept one-way prerequisite {operation}" in removed.stdout for operation in PACKAGES)
    assert inventory(vm) == installed_inventory
    assert {row.split("\t", 1)[0] for row in installed_inventory.splitlines()} >= initial_names_arch
    print("Initial RPM count:", len(initial_names_arch))
    print("Post-apply RPM count:", len(installed_names_arch))
    print("New name.arch entries:", sorted(installed_names_arch - initial_names_arch))
    print("DNF history:", vm.run("dnf history info last", check=False).stdout)
