"""Pinned BulkExtractor Snap installation and automatic-snapshot recovery."""

import pytest


PROFILE = "forensic-bulk-extractor"
CASE_SENTINEL = "/home/ride-test/Documents/ride-bulk-extractor-case-preserve.txt"
SNAP_SENTINEL = "/home/ride-test/snap/bulk-extractor/common/ride-acceptance.txt"


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
@pytest.mark.recovery("remove-new-install")
def test_bulk_extractor_pinned_snap_lifecycle_and_snapshot_recovery(vm):
    vm.ride("apply", "--profile", "snap-runtime", "--allow-candidate", timeout=1200)
    vm.run("systemctl is-active snapd.socket && snap version", timeout=300)
    vm.run("mkdir -p /home/ride-test/Documents")
    vm.run(f"printf 'case sentinel\\n' > {CASE_SENTINEL}")
    original_case = vm.run(f"sha256sum {CASE_SENTINEL}").stdout.split()[0]

    plan = vm.ride("plan", "--profile", PROFILE)
    assert "package.bulk-extractor" in plan.stdout and "candidate" in plan.stdout
    refused = vm.ride("apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    vm.ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=1200)
    vm.run("snap list bulk-extractor | grep -F '2.2.0'")
    connections = vm.run("snap connections bulk-extractor").stdout
    block_rows = [line.split() for line in connections.splitlines()
                  if line.split() and line.split()[0] == "block-devices"]
    assert block_rows and all(row[-1] == "-" for row in block_rows)

    help_result = vm.run("snap run bulk-extractor --help", check=False, timeout=180)
    assert "bulk_extractor version 2.2.0" in help_result.stdout
    assert "Usage:" in help_result.stdout
    vm.run("mkdir -p /home/ride-test/snap/bulk-extractor/common")
    vm.run(f"printf 'snap app state sentinel\\n' > {SNAP_SENTINEL}")
    vm.ride("remove", "--profile", PROFILE, "--allow-candidate", timeout=900)
    assert vm.run("snap list bulk-extractor", check=False).returncode != 0
    saved = vm.run("sudo snap saved").stdout
    snapshot_id = next(
        line.split()[0] for line in saved.splitlines()
        if len(line.split()) >= 7 and line.split()[1] == "bulk-extractor"
        and line.split()[6] == "auto")
    assert vm.run(f"sha256sum {CASE_SENTINEL}").stdout.split()[0] == original_case
    assert vm.run(f"test ! -e {SNAP_SENTINEL}", check=False).returncode == 0

    vm.ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=1200)
    vm.run(f"sudo snap restore {snapshot_id} bulk-extractor", timeout=300)
    assert vm.run(f"cat {SNAP_SENTINEL}").stdout.strip() == "snap app state sentinel"
    assert vm.run(f"sha256sum {CASE_SENTINEL}").stdout.split()[0] == original_case
    vm.ride("remove", "--profile", PROFILE, "--allow-candidate", timeout=900)
