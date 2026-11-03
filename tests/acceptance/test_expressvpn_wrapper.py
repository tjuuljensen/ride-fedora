"""RIDE-owned ExpressVPN install and inverse on disposable Fedora 44 targets."""

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
INSTALLER = ROOT / ".acceptance-runs" / "expressvpn-linux-universal-14.3.1.15429_release.run"
SIGNATURE = ROOT / ".acceptance-runs" / "expressvpn-linux-universal-14.3.1.15429_release.run.asc"
PUBLIC_KEY = ROOT / ".acceptance-runs" / "expressvpn-release-public-key.asc"
PROFILE = "fedora-expressvpn"


def test_expressvpn_wrapper_exact_install_repeat_remove(vm):
    target_id = vm.target["id"]
    if target_id not in {"fedora-44-workstation-x86_64", "fedora-44-server-x86_64"}:
        pytest.skip(f"ExpressVPN wrapper is not declared for {target_id}")
    if not all(path.is_file() and not path.is_symlink()
               for path in (INSTALLER, SIGNATURE, PUBLIC_KEY)):
        pytest.fail("stage the owner-supplied installer, signature, and published key under .acceptance-runs")

    for guest_name, local_file, staged_name, mode in (
        ("expressvpn-installer-run", INSTALLER, "expressvpn-linux-universal-14.3.1.15429_release.run", "0700"),
        ("expressvpn-installer-asc", SIGNATURE, "expressvpn-linux-universal-14.3.1.15429_release.run.asc", "0600"),
        ("expressvpn-signing-key-asc", PUBLIC_KEY, "expressvpn_release_public_key_0xAFF2A1415F6A3A38.asc", "0600"),
    ):
        guest_file = vm.put_file(guest_name, local_file)
        vm.run(f"sudo install -d -o root -g root -m 0700 /var/cache/ride-fedora/artifacts/package.expressvpn && "
               f"sudo install -o root -g root -m {mode} {guest_file} "
               f"/var/cache/ride-fedora/artifacts/package.expressvpn/{staged_name}")

    vm.run("sudo dnf -y install gnupg2", timeout=600)
    guest_profile = f"{vm.repo}/profiles/{PROFILE}.json"
    vm.run(
        "sudo install -d -m 0755 /etc/NetworkManager/conf.d /etc/iproute2 && "
        "printf '# RIDE ExpressVPN recovery fixture\\n' | sudo tee "
        "/etc/NetworkManager/conf.d/wgexpressvpn.conf >/dev/null && "
        "printf '# RIDE ExpressVPN route fixture\\n' | sudo tee -a /etc/iproute2/rt_tables >/dev/null && "
        "sudo install -d -m 0700 /root/.config/expressvpn && "
        "printf 'seeded root preference\\n' | sudo tee "
        "/root/.config/expressvpn/ride-owner-marker >/dev/null && "
        "sudo chmod 0600 /root/.config/expressvpn/ride-owner-marker"
    )
    vm.run("sudo ip rule add priority 100 lookup main")
    before = vm.run(
        "sudo sha256sum /etc/NetworkManager/conf.d/wgexpressvpn.conf "
        "/etc/iproute2/rt_tables /root/.config/expressvpn/ride-owner-marker"
    ).stdout.splitlines()
    before_hashes = [line.split()[0] for line in before]

    planned = vm.ride("plan", "--profile", guest_profile, "--allow-candidate")
    assert "package.expressvpn" in planned.stdout and "candidate" in planned.stdout
    installed = vm.ride("apply", "--profile", guest_profile, "--allow-candidate", timeout=1800)
    assert "package.expressvpn" in installed.stdout
    assert vm.run("test -x /opt/expressvpn/bin/expressvpnctl").returncode == 0
    assert vm.run("systemctl is-enabled expressvpn-service.service").stdout.strip() == "enabled"
    assert vm.run("sudo ip -o rule show | grep -E 'lookup evpnFwdrt|suppress_prefixlength 1'").returncode == 0
    active_rules = vm.run("sudo ip -o rule show").stdout.replace("\t", " ")
    assert "100: from all lookup main" in active_rules, active_rules
    status = vm.run("sudo /opt/expressvpn/bin/expressvpnctl status", check=False).stdout
    assert "not logged in" in status.lower()
    repeated = vm.ride("apply", "--profile", guest_profile, "--allow-candidate", timeout=1800)
    assert "unchanged package.expressvpn" in repeated.stdout

    removed = vm.ride("remove", "package.expressvpn", "--allow-candidate", timeout=1800)
    assert "package.expressvpn" in removed.stdout
    assert vm.run("test ! -e /opt/expressvpn && test ! -e /etc/systemd/system/expressvpn-service.service").returncode == 0
    assert vm.run("systemctl is-active expressvpn-service.service", check=False).stdout.strip() != "active"
    assert vm.run("sudo ip -o rule show | grep -E 'lookup evpnFwdrt|suppress_prefixlength 1'", check=False).returncode != 0
    assert vm.run("sudo ip -o rule show | grep -E '^100:[[:space:]]+from all lookup main$'").returncode == 0
    after = vm.run(
        "sudo sha256sum /etc/NetworkManager/conf.d/wgexpressvpn.conf "
        "/etc/iproute2/rt_tables /root/.config/expressvpn/ride-owner-marker"
    ).stdout.splitlines()
    assert [line.split()[0] for line in after] == before_hashes
    assert "absent" in vm.ride("status", "package.expressvpn").stdout
    assert vm.run("test ! -e /var/lib/ride-fedora/expressvpn").returncode == 0


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
