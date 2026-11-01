"""Disposable OpenConnect package-only lifecycle with seeded VPN state."""

import json
import re
import shlex

import pytest


RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")
PACKAGES = ("vpnc-script", "openconnect", "NetworkManager-openconnect-gnome")
IDS = ("package.vpnc-script", "package.openconnect",
       "package.networkmanager-openconnect-gnome")
SEEDED = "/etc/NetworkManager/system-connections/ride-seeded-vpn.nmconnection"
EXPECTED_PREP_REMOVALS = {
    "NetworkManager-openconnect", "NetworkManager-openconnect-gnome",
    "NetworkManager-vpnc", "NetworkManager-vpnc-gnome", "libpskc",
    "libuser", "openconnect", "stoken-libs", "usermode", "vpnc",
    "vpnc-script",
}


def rpm_names(vm):
    return set(vm.run("rpm -qa --qf '%{NAME}\\n'").stdout.splitlines())


def journal(vm, identifier):
    return json.loads(vm.run(f"sudo cat /var/lib/ride-fedora/runs/{identifier}.json").stdout)


def run_id(output):
    match = RUN_ID.search(output)
    assert match, output
    return match.group(1)


def protected_state(vm):
    return {
        "connections": vm.run("nmcli -t -f UUID connection show").stdout,
        "activeConnections": vm.run("nmcli -t -f UUID connection show --active").stdout,
        "seeded": vm.run("sudo sha256sum " + shlex.quote(SEEDED)).stdout,
        "seededMeta": vm.run("sudo stat -c '%u:%g:%a' " + shlex.quote(SEEDED)).stdout,
        "service": (vm.run("systemctl is-enabled NetworkManager.service", check=False).stdout.strip(),
                    vm.run("systemctl is-active NetworkManager.service", check=False).stdout.strip()),
    }


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_openconnect_signed_packages_and_seeded_vpn_state(vm):
    vm.run("sudo test ! -e " + shlex.quote(SEEDED))
    vm.run("printf '[connection]\\nid=ride-seeded-vpn\\nuuid=6483e812-22ee-4f77-b22c-7f829ce01c89\\n"
           "type=vpn\\nautoconnect=false\\n[vpn]\\nservice-type=org.freedesktop.NetworkManager.openvpn\\n'"
           " | sudo tee " + shlex.quote(SEEDED) + " >/dev/null")
    vm.run("sudo chmod 0600 " + shlex.quote(SEEDED))
    original = rpm_names(vm)
    original_protected = protected_state(vm)
    already = set(PACKAGES) & original
    if already:
        vm.run("sudo dnf -y remove " + shlex.join(sorted(already)), timeout=900)
        removed_for_prep = original - rpm_names(vm)
        assert removed_for_prep == EXPECTED_PREP_REMOVALS, (
            "preparation dependency set changed; review before continuing",
            sorted(removed_for_prep),
        )
    else:
        removed_for_prep = set()
    baseline = rpm_names(vm)
    assert not (set(PACKAGES) & baseline)
    protected = protected_state(vm)

    planned = vm.ride("plan", "--profile", "openconnect-vpn-tools")
    assert all(identifier in planned.stdout for identifier in IDS)
    assert planned.stdout.count("supported") == len(IDS)
    changed = vm.ride("apply", "--profile", "openconnect-vpn-tools", timeout=1200)
    identifier = run_id(changed.stdout)
    record = journal(vm, identifier)
    assert record["status"] == "complete"
    assert [step["id"] for step in record["steps"]] == list(IDS)
    assert all(step["result"] == "changed" for step in record["steps"])
    for package, operation in zip(PACKAGES, IDS, strict=True):
        assert package in rpm_names(vm)
        signature = vm.run("rpm -q --qf '%{SIGPGP:pgpsig}\\n%{RSAHEADER:pgpsig}\\n' "
                           + shlex.quote(package)).stdout
        assert any(line.strip() not in ("", "(none)") for line in signature.splitlines())
        vm.run("rpm -V " + shlex.quote(package))
        assert "installed" in vm.ride("status", operation).stdout
    vm.run("openconnect --version")
    vm.run("test -f /etc/vpnc/vpnc-script")
    vm.run("rpm -ql NetworkManager-openconnect-gnome | grep -q nm-openconnect-auth-dialog")
    assert protected_state(vm) == protected
    repeated = vm.ride("apply", "--profile", "openconnect-vpn-tools", timeout=900)
    assert repeated.stdout.count("unchanged") == len(IDS)
    vm.ride("restore", "--run-id", identifier, "--dry-run")
    vm.ride("restore", "--run-id", identifier, timeout=1200)
    assert not (set(PACKAGES) & rpm_names(vm))
    assert protected_state(vm) == protected
    residual = sorted(rpm_names(vm) - baseline)
    print("dependency residue after restore:", residual)

    installed = vm.ride("apply", "--profile", "openconnect-vpn-tools", timeout=1200)
    assert RUN_ID.search(installed.stdout)
    for operation in reversed(IDS):
        vm.ride("remove", operation, timeout=900)
    assert not (set(PACKAGES) & rpm_names(vm))
    assert protected_state(vm) == protected
    if removed_for_prep:
        vm.run("sudo dnf -y install " + shlex.join(sorted(removed_for_prep)), timeout=1200)
        assert original <= rpm_names(vm), "pre-existing package names were not recovered"
        assert protected_state(vm) == original_protected


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_openconnect_supported_profile_gate(vm):
    """Metadata-only promotion must allow the profile without candidate opt-in."""
    baseline = rpm_names(vm)
    planned = vm.ride("plan", "--profile", "openconnect-vpn-tools")
    assert all(identifier in planned.stdout for identifier in IDS)
    assert planned.stdout.count("supported") == len(IDS)
    applied = vm.ride("apply", "--profile", "openconnect-vpn-tools")
    assert applied.stdout.count("unchanged") == len(IDS)
    assert rpm_names(vm) == baseline
