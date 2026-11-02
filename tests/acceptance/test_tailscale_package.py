"""Fedora 44 Server package-only Tailscale lifecycle."""

import pytest


PROFILE = "fedora-server-tailscale"
STATE = "/var/lib/tailscale/tailscaled.state"
REPO = "/etc/yum.repos.d/ride-tailscale.repo"


@pytest.mark.vm_target("fedora-44-server-x86_64")
def test_tailscale_package_does_not_authenticate_or_remove_local_identity_state(vm):
    vm.run("! rpm -q --quiet tailscale")
    vm.run(f"sudo test ! -e {REPO}")
    vm.run("! systemctl is-active --quiet tailscaled.service")
    vm.run("! systemctl is-enabled --quiet tailscaled.service")
    vm.run("sudo install -d -m 0700 /var/lib/tailscale")
    vm.run(f"printf 'opaque preexisting node identity\\n' | sudo tee {STATE} >/dev/null")
    original = vm.run(f"sudo sha256sum {STATE}").stdout.split()[0]

    plan = vm.ride("plan", "--profile", PROFILE)
    assert "package.tailscale" in plan.stdout and "candidate" in plan.stdout
    refused = vm.ride("apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    applied = vm.ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=1800)
    run_id = applied.stdout.split("Run ID: ", 1)[1].splitlines()[0]

    vm.run("rpm -q tailscale")
    # DNF completed the install with the exact RIDE repo forced to gpgcheck=1.
    vm.run(f"sudo grep -Fx 'repo_gpgcheck=1' {REPO}")
    vm.run(f"sudo grep -Fx 'gpgcheck=1' {REPO}")
    vm.run("command -v tailscale && command -v tailscaled")
    vm.run("! systemctl is-active --quiet tailscaled.service")
    vm.run("! systemctl is-enabled --quiet tailscaled.service")
    vm.run(f"test \"$(sudo sha256sum {STATE} | cut -d' ' -f1)\" = {original}")

    repeated = vm.ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=600)
    assert "unchanged" in repeated.stdout
    assert "package.tailscale" in vm.ride("status", "package.tailscale").stdout
    vm.ride("restore", "--run-id", run_id, "--allow-candidate", timeout=1800)
    vm.run("! rpm -q --quiet tailscale")
    vm.run(f"sudo test ! -e {REPO}")
    vm.run("! systemctl is-active --quiet tailscaled.service")
    vm.run("! systemctl is-enabled --quiet tailscaled.service")
    vm.run(f"test \"$(sudo sha256sum {STATE} | cut -d' ' -f1)\" = {original}")
