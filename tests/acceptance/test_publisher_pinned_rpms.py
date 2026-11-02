"""Pinned Microsoft and balena publisher RPM lifecycles; no media is written."""

import pytest


RIDE = "/home/ride-test/ride/ride.sh"


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
@pytest.mark.recovery("remove-new-install")
@pytest.mark.parametrize(("profile", "operation", "package", "probe"), [
    ("fedora-powershell", "package.powershell", "powershell", "pwsh -NoLogo -NoProfile -Command '$PSVersionTable.PSVersion.ToString()'"),
    ("fedora-balena-etcher", "package.balena-etcher", "balena-etcher", None),
    ("fedora-discord", "package.discord", "discord", None),
])
def test_pinned_publisher_rpm_lifecycle(vm, profile, operation, package, probe):
    if package == "discord":
        vm.run("mkdir -p ~/.config/discord && printf 'preserve-me\\n' > ~/.config/discord/ride-migration-sentinel")
    assert vm.run(f"rpm -q --quiet {package}", check=False).returncode != 0
    refused = vm.ride("apply", "--profile", profile, check=False)
    assert refused.returncode != 0
    refusal_text = refused.stdout + refused.stderr
    assert "--allow-candidate" in refusal_text or "candidate" in refusal_text.lower()
    assert vm.run(f"rpm -q --quiet {package}", check=False).returncode != 0

    plan = vm.ride("plan", "--profile", profile, "--allow-candidate")
    assert operation in plan.stdout
    vm.ride("apply", "--profile", profile, "--allow-candidate", timeout=1200)
    assert vm.run(f"rpm -q {package}").returncode == 0
    if probe:
        assert vm.run(probe).returncode == 0
    else:
        files = vm.run(f"rpm -ql {package}").stdout
        assert any(line.endswith(".desktop") for line in files.splitlines())
    assert operation in vm.ride("status", operation).stdout
    repeated = vm.ride("apply", "--profile", profile, "--allow-candidate")
    assert f"unchanged {operation}" in repeated.stdout
    vm.ride("remove", "--profile", profile, "--allow-candidate", timeout=900)
    assert vm.run(f"rpm -q --quiet {package}", check=False).returncode != 0
    if package == "discord":
        sentinel = vm.run("cat ~/.config/discord/ride-migration-sentinel").stdout.strip()
        assert sentinel == "preserve-me"
