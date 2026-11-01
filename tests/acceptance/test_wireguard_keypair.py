"""Disposable signed WireGuard package and owned key-pair lifecycle."""

import json
import re

import pytest


RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")
IDS = ("package.wireguard-tools", "setting.wireguard-keypair")
PRIVATE = "/etc/wireguard/privatekey"
PUBLIC = "/etc/wireguard/publickey"
MARKER = "/etc/wireguard/.ride-owned-keypair"
SEEDED = "/etc/NetworkManager/system-connections/ride-seeded-wg.nmconnection"


def run_id(output):
    match = RUN_ID.search(output)
    assert match, output
    return match.group(1)


def journal(vm, identifier):
    return json.loads(vm.run(f"sudo cat /var/lib/ride-fedora/runs/{identifier}.json").stdout)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_wireguard_keypair_owned_lifecycle(vm):
    vm.run("sudo install -d -m 0700 /etc/wireguard")
    vm.run("sudo test ! -e " + SEEDED)
    vm.run("printf '[connection]\\nid=ride-seeded-wg\\nuuid=01e524df-034f-4a86-a8f4-cc38e5f388c4\\n"
           "type=vpn\\nautoconnect=false\\n[vpn]\\nservice-type=org.freedesktop.NetworkManager.wireguard\\n'"
           " | sudo tee " + SEEDED + " >/dev/null")
    vm.run("sudo chmod 0600 " + SEEDED)
    seeded = vm.run("sudo sha256sum " + SEEDED).stdout
    connections = vm.run("nmcli -t -f UUID connection show").stdout
    service = vm.run("systemctl is-active NetworkManager.service", check=False).stdout

    # A pre-existing legacy key must make profile preflight fail before DNF runs.
    vm.run("printf 'pre-existing-key\\n' | sudo tee " + PRIVATE + " >/dev/null")
    vm.run("sudo chmod 0600 " + PRIVATE)
    rpm_before = vm.run("rpm -q wireguard-tools", check=False).returncode
    refused = vm.ride("apply", "--profile", "wireguard-keypair", "--allow-candidate", check=False)
    assert refused.returncode != 0 and "not owned by RIDE" in refused.stderr
    assert vm.run("rpm -q wireguard-tools", check=False).returncode == rpm_before
    assert vm.run("sudo cat " + PRIVATE).stdout == "pre-existing-key\n"
    vm.run("sudo rm -f " + PRIVATE)

    planned = vm.ride("plan", "--profile", "wireguard-keypair")
    assert all(identifier in planned.stdout for identifier in IDS)
    assert planned.stdout.count("candidate") == len(IDS)
    changed = vm.ride("apply", "--profile", "wireguard-keypair", "--allow-candidate", timeout=1200)
    identifier = run_id(changed.stdout)
    record = journal(vm, identifier)
    assert record["status"] == "complete"
    assert [step["id"] for step in record["steps"]] == list(IDS)
    assert all(step["result"] == "changed" for step in record["steps"])
    assert all("private" not in json.dumps(step).lower() for step in record["steps"])
    assert vm.run("sudo stat -c '%a' " + PRIVATE).stdout.strip() == "600"
    assert vm.run("sudo stat -c '%a' " + PUBLIC).stdout.strip() == "600"
    derived_public = vm.run("sudo sh -c 'wg pubkey < " + PRIVATE + "'").stdout
    assert derived_public == vm.run("sudo cat " + PUBLIC).stdout
    vm.run("rpm -q --qf '%{RSAHEADER:pgpsig}\\n' wireguard-tools | grep -qv '(none)'")
    vm.run("rpm -V wireguard-tools")
    repeated = vm.ride("apply", "--profile", "wireguard-keypair", "--allow-candidate")
    assert repeated.stdout.count("unchanged") == len(IDS)
    vm.ride("restore", "--run-id", identifier, "--dry-run")
    vm.ride("restore", "--run-id", identifier, "--allow-candidate")
    vm.run("sudo test ! -e " + PRIVATE + " && sudo test ! -e " + PUBLIC + " && sudo test ! -e " + MARKER)
    assert vm.run("sudo sha256sum " + SEEDED).stdout == seeded
    assert vm.run("nmcli -t -f UUID connection show").stdout == connections
    assert vm.run("systemctl is-active NetworkManager.service", check=False).stdout == service

    installed = vm.ride("apply", "--profile", "wireguard-keypair", "--allow-candidate", timeout=1200)
    assert RUN_ID.search(installed.stdout)
    vm.ride("remove", "--profile", "wireguard-keypair", "--allow-candidate", timeout=1200)
    assert vm.run("rpm -q wireguard-tools", check=False).returncode != 0
    vm.run("sudo test ! -e " + PRIVATE + " && sudo test ! -e " + PUBLIC + " && sudo test ! -e " + MARKER)
    assert vm.run("sudo sha256sum " + SEEDED).stdout == seeded
