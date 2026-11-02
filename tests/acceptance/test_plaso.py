"""Plaso package and GIFT COPR lifecycle on Fedora 44 Workstation."""

import hashlib

import pytest


PROFILE = "fedora-plaso"
REPOSITORY_FILE = "/etc/yum.repos.d/ride-gift-stable.repo"
CASE_SENTINEL = "/home/ride-test/.local/share/ride-plaso-acceptance/case-output.txt"


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_plaso_copr_package_lifecycle_preserves_case_output(vm):
    vm.run("command -v curl && command -v gpg")
    assert vm.run("rpm -q --quiet plaso-tools", check=False).returncode != 0
    assert vm.run(f"test ! -e {REPOSITORY_FILE}").returncode == 0
    vm.run("install -d -m 0700 /home/ride-test/.local/share/ride-plaso-acceptance")
    vm.run(f"printf 'preserve this case output\\n' > {CASE_SENTINEL}")
    before_hash = hashlib.sha256(vm.run(f"cat {CASE_SENTINEL}").stdout.encode()).hexdigest()

    plan = vm.ride("plan", "--profile", PROFILE)
    assert "package.plaso" in plan.stdout and "candidate" in plan.stdout
    refused = vm.ride("apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr

    vm.ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=1800)
    vm.run("rpm -q plaso-tools")
    vm.run(f"grep -Fxq 'gpgcheck=1' {REPOSITORY_FILE}")
    vm.run("log2timeline.py --version")
    assert "package.plaso\tgift-stable-copr\tinstalled" in vm.ride("status", "package.plaso").stdout
    repeated = vm.ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=900)
    assert "unchanged package.plaso" in repeated.stdout

    vm.ride("remove", "--profile", PROFILE, "--allow-candidate", timeout=1500)
    assert vm.run("rpm -q --quiet plaso-tools", check=False).returncode != 0
    assert vm.run(f"test ! -e {REPOSITORY_FILE}").returncode == 0
    after_hash = hashlib.sha256(vm.run(f"cat {CASE_SENTINEL}").stdout.encode()).hexdigest()
    assert after_hash == before_hash
