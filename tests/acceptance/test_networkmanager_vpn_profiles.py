"""Exact-state NetworkManager VPN profile removal on Fedora 44 Workstation."""

import json
from pathlib import Path
import re
import shlex

import pytest


ROOT = Path(__file__).resolve().parents[2]
OPERATION = "setting.networkmanager-vpn-profiles"
UUIDS = (
    "c5f9fa90-29d8-4a88-801e-a56a5a3d8201",
    "de96ea18-94f8-4e5a-86a8-0a5e3aa60002",
)
UNRELATED = "038b9389-2399-4fd3-9f4a-51c3d7650003"
SECRETS = ("vpn-fixture-secret-one", "vpn-fixture-secret-two", "vpn-fixture-secret-unrelated")
RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")


def _profile(uuid, name, secret):
    return (
        "[connection]\n"
        f"id={name}\n"
        f"uuid={uuid}\n"
        "type=vpn\n"
        "autoconnect=false\n"
        "[vpn]\n"
        "service-type=org.freedesktop.NetworkManager.openvpn\n"
        "[vpn-secrets]\n"
        f"password={secret}\n"
    )


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_uuid_scoped_vpn_profile_lifecycle_and_exact_restore(vm):
    catalog = json.loads((ROOT / "catalog/operations.json").read_text(encoding="utf-8"))
    operation = next(item for item in catalog["operations"] if item["id"] == OPERATION)
    assert operation["status"] == "supported"
    guest_catalog = vm.put_json("vpn-profiles-supported-catalog", catalog)
    value = ",".join(UUIDS)
    profile = {
        "schemaVersion": 1,
        "id": "vpn-profiles-acceptance",
        "description": "Disposable VPN profile exact-state lifecycle fixture.",
        "operations": [{"id": OPERATION, "state": "absent", "value": value}],
    }
    guest_profile = vm.put_json("vpn-profiles-acceptance-profile", profile)

    vm.run("systemctl is-active NetworkManager.service | grep -Fx active")

    fixture_dir = "/etc/NetworkManager/system-connections"
    names = ("ride-vpn-fixture-one", "ride-vpn-fixture-two", "ride-vpn-fixture-unrelated")
    fixtures = list(zip((UUIDS[0], UUIDS[1], UNRELATED), names, SECRETS))
    commands = ["sudo test -d " + fixture_dir]
    for uuid, name, secret in fixtures:
        content = _profile(uuid, name, secret)
        commands.append(
            f"printf %s {shlex.quote(content)} | sudo tee "
            f"{fixture_dir}/{name}.nmconnection >/dev/null"
        )
        commands.append(f"sudo chmod 0600 {fixture_dir}/{name}.nmconnection")
    commands.extend((
        "sudo nmcli connection reload",
        f"sudo nmcli -g connection.type connection show {UUIDS[0]} | grep -Fx vpn",
        f"sudo nmcli -g connection.type connection show {UUIDS[1]} | grep -Fx vpn",
        f"sudo nmcli -g connection.type connection show {UNRELATED} | grep -Fx vpn",
    ))
    vm.run(" && ".join(commands))
    before = vm.run(
        "sudo python3 - <<'PY'\n"
        "import hashlib, json, os, pathlib, stat\n"
        f"root = pathlib.Path({fixture_dir!r})\n"
        f"names = {list(names)!r}\n"
        "out = {}\n"
        "for name in names:\n"
        " p = root / (name + '.nmconnection'); s = p.stat()\n"
        " try: attrs = {n: os.getxattr(p, n).hex() for n in os.listxattr(p)}\n"
        " except OSError: attrs = {}\n"
        " out[name] = [hashlib.sha256(p.read_bytes()).hexdigest(), s.st_uid, s.st_gid, stat.S_IMODE(s.st_mode), s.st_mtime_ns, attrs]\n"
        "print(json.dumps(out, sort_keys=True))\n"
        "PY"
    ).stdout.strip()

    plan = vm.ride("plan", "--profile", guest_profile, catalog=guest_catalog)
    assert OPERATION in plan.stdout and "supported" in plan.stdout
    applied = vm.ride("apply", "--profile", guest_profile, catalog=guest_catalog)
    run_id = RUN_ID.search(applied.stdout).group(1)
    for uuid in UUIDS:
        assert vm.run(f"sudo nmcli -g connection.type connection show {uuid}", check=False).returncode != 0
    status = vm.ride("status", OPERATION, "--value", value, catalog=guest_catalog)
    assert status.stdout.splitlines()[-1].split("\t")[2] == "absent"
    vm.run(f"sudo test -e {fixture_dir}/{names[2]}.nmconnection")
    journal = vm.run(f"sudo cat /var/lib/ride-fedora/runs/{run_id}.json").stdout
    for secret in SECRETS:
        assert secret not in journal
    assert value in journal

    repeated = vm.ride("apply", "--profile", guest_profile, catalog=guest_catalog)
    assert "unchanged" in repeated.stdout
    vm.ride("restore", "--run-id", run_id, catalog=guest_catalog)
    after = vm.run(
        "sudo python3 - <<'PY'\n"
        "import hashlib, json, os, pathlib, stat\n"
        f"root = pathlib.Path({fixture_dir!r})\n"
        f"names = {list(names)!r}\n"
        "out = {}\n"
        "for name in names:\n"
        " p = root / (name + '.nmconnection'); s = p.stat()\n"
        " try: attrs = {n: os.getxattr(p, n).hex() for n in os.listxattr(p)}\n"
        " except OSError: attrs = {}\n"
        " out[name] = [hashlib.sha256(p.read_bytes()).hexdigest(), s.st_uid, s.st_gid, stat.S_IMODE(s.st_mode), s.st_mtime_ns, attrs]\n"
        "print(json.dumps(out, sort_keys=True))\n"
        "PY"
    ).stdout.strip()
    assert json.loads(after) == json.loads(before)

    vm.run(
        "sudo rm -f " + " ".join(f"{fixture_dir}/{name}.nmconnection" for name in names) +
        " && sudo nmcli connection reload"
    )
