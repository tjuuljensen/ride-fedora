"""Fedora 44 Server migration check for v2 InstallRequired RPMs."""

import hashlib
import json
import re

import pytest

PROFILE = "server-required-tools"
FIREWALL_PROFILE = "server-firewall-package"
TOOLS = {
    "package.open-vm-tools": ("open-vm-tools", "test -x /usr/bin/vmtoolsd"),
    "package.server-nano": ("nano", "nano --version"),
    "package.wget": ("wget2-wget", "wget --version"),
    "package.unzip": ("unzip", "unzip -v"),
    "package.git": ("git", "git --version"),
    "package.cifs-utils": ("cifs-utils", "sudo mount.cifs -V"),
    "package.samba-client": ("samba-client", "smbclient --version"),
    "package.samba-common": ("samba-common", "rpm -ql samba-common"),
    "package.cronie": ("cronie", "test -x /usr/sbin/crond"),
    "package.screen": ("screen", "screen --version"),
}
FIREWALL = {"package.firewalld": ("firewalld", "firewall-cmd --version")}
RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")


def inventory(vm):
    return vm.run(
        "rpm -qa --qf '%{NAME}.%{ARCH}\\t%{VERSION}-%{RELEASE}\\t%{RSAHEADER:pgpsig}\\n' | sort"
    ).stdout


def inventory_rows(output):
    return {row.split("\t", 1)[0]: row.split("\t")[1]
            for row in output.splitlines()}


def run_id(output):
    match = RUN_ID.search(output)
    assert match, output
    return match.group(1)


def service_state(vm, units):
    result = {}
    for unit in units:
        active = vm.run(f"systemctl is-active {unit}", check=False).stdout.strip()
        enabled = vm.run(f"systemctl is-enabled {unit}", check=False).stdout.strip()
        result[unit] = (active, enabled)
    return result


def firewalld_files(vm):
    output = vm.run(
        "sudo sh -c 'if test -d /etc/firewalld; then find /etc/firewalld -type f -print0 | "
        "sort -z | xargs -0r sha256sum; fi'",
        check=False,
    ).stdout
    return hashlib.sha256(output.encode()).hexdigest()


@pytest.mark.vm_target("fedora-44-server-x86_64")
def test_server_required_tools_and_firewall_installation_are_opt_in_and_bounded(vm):
    units = ("vmtoolsd.service", "vgauthd.service", "crond.service", "firewalld.service")
    before_inventory = inventory(vm)
    before_rows = inventory_rows(before_inventory)
    before_names_arch = set(before_rows)
    before_services = service_state(vm, units)
    before_firewalld_files = firewalld_files(vm)
    before_firewalld_active = vm.run("sudo firewall-cmd --state", check=False).stdout.strip()
    assert "firewalld.x86_64" in before_names_arch
    assert before_firewalld_active == "running"

    plan = vm.ride("plan", "--profile", PROFILE)
    for operation in TOOLS:
        assert operation in plan.stdout
    refused = vm.ride("apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr

    applied = vm.ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=1500)
    identifier = run_id(applied.stdout)
    journal = json.loads(vm.run(f"sudo cat /var/lib/ride-fedora/runs/{identifier}.json").stdout)
    assert journal["status"] == "complete"
    assert {step["id"] for step in journal["steps"]} == set(TOOLS)

    after_tools_inventory = inventory(vm)
    after_tools_rows = inventory_rows(after_tools_inventory)
    after_tools_names_arch = set(after_tools_rows)
    after_tools_services = service_state(vm, units)
    assert after_tools_services["firewalld.service"] == before_services["firewalld.service"]
    assert after_tools_services["crond.service"] == before_services["crond.service"]
    assert after_tools_services["vmtoolsd.service"] == ("inactive", "enabled")
    assert after_tools_services["vgauthd.service"] == ("inactive", "enabled")
    assert after_tools_names_arch >= before_names_arch
    for operation, (rpm, command) in TOOLS.items():
        assert vm.run(f"rpm -q {rpm}").returncode == 0
        signature = vm.run(f"rpm -q --qf '%{{RSAHEADER:pgpsig}}\\n' {rpm}").stdout.lower()
        assert signature.strip() and "(none)" not in signature
        vm.run(f"sudo rpm -V {rpm}")
        vm.run(command)
        assert operation in vm.ride("status", operation).stdout

    repeated = vm.ride("apply", "--profile", PROFILE, "--allow-candidate")
    assert all(f"unchanged {operation}" in repeated.stdout for operation in TOOLS)
    removed = vm.ride("remove", "--profile", PROFILE, "--allow-candidate")
    assert all(f"kept one-way prerequisite {operation}" in removed.stdout
               for operation in TOOLS)
    after_remove_rows = inventory_rows(inventory(vm))
    assert set(after_remove_rows) == after_tools_names_arch
    assert set(after_remove_rows) >= before_names_arch
    removed_names = after_tools_names_arch - set(after_remove_rows)
    for operation, (rpm, _) in TOOLS.items():
        assert vm.run(f"rpm -q {rpm}").returncode == 0

    firewall_plan = vm.ride("plan", "--profile", FIREWALL_PROFILE)
    assert "package.firewalld" in firewall_plan.stdout
    firewall_applied = vm.ride(
        "apply", "--profile", FIREWALL_PROFILE, "--allow-candidate", timeout=900
    )
    firewall_id = run_id(firewall_applied.stdout)
    firewall_journal = json.loads(
        vm.run(f"sudo cat /var/lib/ride-fedora/runs/{firewall_id}.json").stdout
    )
    assert firewall_journal["status"] == "complete"
    assert {step["id"] for step in firewall_journal["steps"]} == set(FIREWALL)
    assert vm.run("rpm -q firewalld").returncode == 0
    vm.run("sudo rpm -V firewalld")
    vm.run("sudo firewall-cmd --version")
    after_firewalld_services = service_state(vm, units)
    assert after_firewalld_services["firewalld.service"] == before_services["firewalld.service"]
    assert firewalld_files(vm) == before_firewalld_files
    assert vm.run("sudo firewall-cmd --state", check=False).stdout.strip() == before_firewalld_active

    print("Initial RPMs:", len(before_names_arch))
    print("After required tools RPMs:", len(after_tools_names_arch))
    print("New names:", sorted(after_tools_names_arch - before_names_arch))
    print("Changed pre-existing RPM versions:", {
        key: (before_rows[key], after_tools_rows[key])
        for key in sorted(before_names_arch & after_tools_names_arch)
        if before_rows[key] != after_tools_rows[key]
    })
    print("RPMs removed with newly installed nano:", sorted(removed_names))
    print("Service state before tools:", before_services)
    print("Service state after tools:", after_tools_services)
    print("Service state after firewalld:", after_firewalld_services)
    print("firewalld active before and after:", before_firewalld_active)
    print("firewalld config hash:", before_firewalld_files)
    print("DNF history:", vm.run("dnf history info last", check=False).stdout)
