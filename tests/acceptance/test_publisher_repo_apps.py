"""Publisher RPM repository lifecycle preserves unrelated package and profile state."""

import re

import pytest


RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")
APPS = (
    ("fedora-vscode", "package.visual-studio-code", "code", "ride-vscode", "code --version"),
    ("fedora-brave", "package.brave", "brave-browser", "ride-brave-browser", "brave-browser --version"),
)
PROFILE_DATA = "/home/ride-test/.config/ride-publisher-test/preserve.txt"


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_publisher_repository_rpm_lifecycle_and_user_profile_recovery(vm):
    vm.run("command -v curl && command -v gpg")
    vm.run("mkdir -p /home/ride-test/.config/ride-publisher-test")
    vm.run(f"printf 'publisher app data\\n' > {PROFILE_DATA}")
    original = vm.run(f"sha256sum {PROFILE_DATA}").stdout.split()[0]
    for profile, operation_id, package, repo_id, probe in APPS:
        assert vm.run(f"rpm -q --quiet {package}", check=False).returncode != 0
        assert vm.run(f"test ! -e /etc/yum.repos.d/{repo_id}.repo").returncode == 0
        plan = vm.ride("plan", "--profile", profile)
        assert operation_id in plan.stdout and "candidate" in plan.stdout
        refused = vm.ride("apply", "--profile", profile, check=False)
        assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
        applied = vm.ride("apply", "--profile", profile, "--allow-candidate", timeout=1500)
        assert RUN_ID.search(applied.stdout), applied.stdout
        assert vm.run(f"rpm -q {package}").returncode == 0
        assert vm.run(f"grep -E '^gpgcheck=1$' /etc/yum.repos.d/{repo_id}.repo").returncode == 0
        assert vm.run(probe, check=False).returncode == 0
        repeated = vm.ride("apply", "--profile", profile, "--allow-candidate", timeout=600)
        assert "unchanged" in repeated.stdout

    vm.ride("remove", "--profile", "fedora-vscode", "--allow-candidate", timeout=900)
    assert vm.run("rpm -q --quiet code", check=False).returncode != 0
    assert vm.run("test ! -e /etc/yum.repos.d/ride-vscode.repo").returncode == 0
    assert vm.run("rpm -q --quiet brave-browser").returncode == 0
    assert vm.run("test -f /etc/yum.repos.d/ride-brave-browser.repo").returncode == 0
    vm.ride("remove", "--profile", "fedora-brave", "--allow-candidate", timeout=900)
    assert vm.run("rpm -q --quiet brave-browser", check=False).returncode != 0
    assert vm.run("test ! -e /etc/yum.repos.d/ride-brave-browser.repo").returncode == 0
    current = vm.run(f"sha256sum {PROFILE_DATA}").stdout.split()[0]
    assert current == original
