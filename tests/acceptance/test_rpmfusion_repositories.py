"""Disposable Fedora 44 lifecycle check for the opt-in RPM Fusion source."""

from pathlib import Path
import json
import pytest


ROOT = Path(__file__).resolve().parents[2]
OPERATION = "setting.rpmfusion-repositories"


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_rpmfusion_repository_install_repeat_metadata_and_inverse(vm):
    catalog = json.loads((ROOT / "catalog" / "operations.json").read_text())
    operation = next(item for item in catalog["operations"] if item["id"] == OPERATION)
    assert operation["status"] == "candidate"
    candidate_args = ["--allow-candidate"]

    assert vm.run("rpm -q rpmfusion-free-release rpmfusion-nonfree-release", check=False).returncode != 0
    original_fedora_repo_files = vm.run("find /etc/yum.repos.d -maxdepth 1 -name 'rpmfusion-*.repo' -printf '%f\n' | sort").stdout
    assert original_fedora_repo_files.splitlines() == ["rpmfusion-nonfree-nvidia-driver.repo", "rpmfusion-nonfree-steam.repo"]
    for repo_file in original_fedora_repo_files.splitlines():
        owner = vm.run(f"rpm -qf --qf '%{{NAME}}\n' /etc/yum.repos.d/{repo_file}").stdout.strip()
        assert owner == "fedora-workstation-repositories"
    vm.run("sudo install -d -m 0755 /etc/yum.repos.d /etc/pki/rpm-gpg")
    vm.run("sudo sh -c 'printf \"[ride-unrelated]\nname=RIDE unrelated sentinel\nenabled=0\ngpgcheck=1\nbaseurl=https://example.invalid/repo/\n\" > /etc/yum.repos.d/ride-unrelated.repo'")
    vm.run("sudo sh -c 'printf \"keep this unrelated key file\\n\" > /etc/pki/rpm-gpg/ride-unrelated.key'")
    unrelated_repo = vm.run("sha256sum /etc/yum.repos.d/ride-unrelated.repo").stdout
    unrelated_key = vm.run("sha256sum /etc/pki/rpm-gpg/ride-unrelated.key").stdout

    plan = vm.ride("plan", "--profile", "rpmfusion", *candidate_args)
    assert OPERATION in plan.stdout and "absent" in plan.stdout
    applied = vm.ride("apply", "--profile", "rpmfusion", *candidate_args, timeout=1200)
    assert "changed" in applied.stdout
    vm.run("rpm -V distribution-gpg-keys")
    vm.run("rpm -V rpmfusion-free-release rpmfusion-nonfree-release")
    assert vm.run("rpm -q --qf '%{VERSION}-%{RELEASE}\n' rpmfusion-free-release").stdout.strip() == "44-3"
    assert vm.run("rpm -q --qf '%{VERSION}-%{RELEASE}\n' rpmfusion-nonfree-release").stdout.strip() == "44-3"
    repo_files = vm.run("rpm -ql rpmfusion-free-release rpmfusion-nonfree-release | grep '^/etc/yum.repos.d/rpmfusion-.*.repo$'").stdout.splitlines()
    assert len(repo_files) >= 2
    for repo_file in repo_files:
        assert "gpgcheck=1" in vm.run(f"sudo cat {repo_file}").stdout.replace(" ", "")
    vm.run("sudo dnf5 makecache --refresh", timeout=1200)

    repeated = vm.ride("apply", "--profile", "rpmfusion", *candidate_args)
    assert "unchanged" in repeated.stdout
    assert "configured" in vm.ride("status", OPERATION).stdout

    vm.run("sudo dnf5 install -y --from-repo=rpmfusion-free-updates redumper", timeout=1200)
    vm.run("sudo dnf5 install -y --from-repo=rpmfusion-nonfree-updates unrar", timeout=1200)
    signed_packages = vm.run("rpm -q --qf '%{NAME}\\t%{RSAHEADER:pgpsig}\\n' redumper unrar").stdout.lower()
    assert "redumper" in signed_packages and "e06f8ecdd651ff2e" in signed_packages
    assert "unrar" in signed_packages and "6a2af96194843c65" in signed_packages
    refused_remove = vm.ride("remove", "--profile", "rpmfusion", *candidate_args, check=False)
    assert refused_remove.returncode != 0
    assert "signed packages still depend on them" in refused_remove.stderr
    assert "configured" in vm.ride("status", OPERATION).stdout

    vm.run("sudo dnf5 remove -y redumper unrar", timeout=1200)
    removed = vm.ride("remove", "--profile", "rpmfusion", *candidate_args, timeout=1200)
    assert "changed" in removed.stdout
    assert vm.run("rpm -q rpmfusion-free-release rpmfusion-nonfree-release", check=False).returncode != 0
    assert vm.run("find /etc/yum.repos.d -maxdepth 1 -name 'rpmfusion-*.repo' -printf '%f\n' | sort").stdout == original_fedora_repo_files
    assert vm.run("sha256sum /etc/yum.repos.d/ride-unrelated.repo").stdout == unrelated_repo
    assert vm.run("sha256sum /etc/pki/rpm-gpg/ride-unrelated.key").stdout == unrelated_key


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_rpmfusion_bad_freeworld_source_pin_coexists_and_removes(vm):
    operation_id = "package.gstreamer1-plugins-bad-freeworld"
    package = "gstreamer1-plugins-bad-freeworld"
    profile = "fedora-codecs-rpmfusion"
    codec = next(item for item in json.loads(
        (ROOT / "catalog" / "operations.json").read_text())["operations"]
        if item["id"] == operation_id)
    assert codec["status"] == "candidate"
    candidate_args = ["--allow-candidate"]

    assert vm.run("rpm -q gstreamer1-plugins-bad-freeworld", check=False).returncode != 0
    vm.run("rpm -q gstreamer1-plugins-bad-free")
    baseline = set(vm.run("rpm -qa --qf '%{NAME}.%{ARCH}\\n'").stdout.splitlines())
    assert "gstreamer1-plugins-bad-free.x86_64" in baseline

    vm.ride("plan", "--profile", "rpmfusion", *candidate_args)
    vm.ride("apply", "--profile", "rpmfusion", *candidate_args, timeout=1200)
    vm.run("sudo dnf5 makecache --refresh", timeout=1200)
    planned = vm.ride("plan", "--profile", profile, *candidate_args)
    assert operation_id in planned.stdout and "rpmfusion-free-updates" in planned.stdout

    first = vm.ride("apply", "--profile", profile, *candidate_args, timeout=1200)
    assert "changed" in first.stdout
    vm.run(f"rpm -q {package} gstreamer1-plugins-bad-free")
    signature = vm.run(f"rpm -q --qf '%{{RSAHEADER:pgpsig}}\\n' {package}").stdout.lower()
    assert "e06f8ecdd651ff2e" in signature
    vm.run(f"rpm -V {package}")
    assert set(vm.run("rpm -qa --qf '%{NAME}.%{ARCH}\\n'").stdout.splitlines()) >= baseline
    repeated = vm.ride("apply", "--profile", profile, *candidate_args)
    assert "unchanged" in repeated.stdout
    assert "installed" in vm.ride("status", operation_id).stdout

    removed = vm.ride("remove", "--profile", profile, *candidate_args, timeout=1200)
    assert "changed" in removed.stdout
    assert vm.run(f"rpm -q {package}", check=False).returncode != 0
    assert "absent" in vm.ride("status", operation_id).stdout
    source_removed = vm.ride("remove", "--profile", "rpmfusion", *candidate_args,
                             timeout=1200, check=False)
    if source_removed.returncode != 0:
        remaining = vm.run(
            "rpm -qa --qf '%{NAME}\\t%{RSAHEADER:pgpsig}\\n' | "
            "grep -Ei 'e06f8ecdd651ff2e|6a2af96194843c65' || true").stdout
        pytest.fail("RPM Fusion profile cleanup remains blocked after codec removal; "
                    f"inspect signed package residue before retrying: {remaining}")
    assert set(vm.run("rpm -qa --qf '%{NAME}.%{ARCH}\\n'").stdout.splitlines()) == baseline
