"""NetworkMiner user-local lifecycle and output preservation on Fedora 44."""

import shlex
import re

import pytest


RUNTIME_PROFILE = "forensic-networkminer-runtime"
APP_PROFILE = "forensic-networkminer"
APP = "/home/ride-test/.local/opt/ride-fedora/networkminer/3.2"
DATA = "/home/ride-test/.local/share/networkminer"
RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")


def user_ride(vm, *args, check=True, timeout=180):
    return vm.run(shlex.join([f"{vm.repo}/ride.sh", *args]), check=check, timeout=timeout)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
@pytest.mark.recovery("remove-new-install")
def test_networkminer_user_program_and_output_data_lifecycle(vm):
    vm.run("test \"$(id -u)\" != 0")
    vm.run("test ! -e " + APP)
    plan = vm.ride("plan", "--profile", APP_PROFILE)
    assert "package.networkminer" in plan.stdout and "candidate" in plan.stdout

    runtime_plan = vm.run(f"sudo {vm.repo}/ride.sh plan --profile {RUNTIME_PROFILE}")
    assert all(package in runtime_plan.stdout for package in
               ("package.gtk2", "package.mono-core", "package.mono-winforms"))
    vm.run(f"sudo {vm.repo}/ride.sh apply --profile {RUNTIME_PROFILE} --allow-candidate", timeout=1200)
    vm.run("sudo rpm -q gtk2 mono-core mono-winforms")
    xvfb_preinstalled = vm.run("rpm -q xorg-x11-server-Xvfb", check=False).returncode == 0
    if not xvfb_preinstalled:
        vm.run("sudo dnf -y install xorg-x11-server-Xvfb", timeout=600)

    gated = user_ride(vm, "apply", "--profile", APP_PROFILE, check=False)
    assert gated.returncode != 0 and "--allow-candidate" in gated.stderr
    applied = user_ride(vm, "apply", "--profile", APP_PROFILE, "--allow-candidate", timeout=900)
    match = RUN_ID.search(applied.stdout)
    assert match, applied.stdout
    run_id = match.group(1)
    journal = vm.run(f"cat /home/ride-test/.local/state/ride-fedora/runs/{run_id}.json")
    assert '"status": "complete"' in journal.stdout
    vm.run(f"test -f {APP}/payload/NetworkMiner.exe && test -f {APP}/payload/PacketParser.dll")
    vm.run(f"test -f {APP}/payload/Fingerprints/mac-ages_LICENSE")
    marker = vm.run(f"cat {APP}/.ride-owned").stdout.strip()
    assert marker == ("ride-fedora package.networkminer 3.2 "
                      "daceec649fb4fe59b11e4a9e4ecd5f51c1dd37824280dfbeac67bec27b6b6d60")
    vm.run("test -L /home/ride-test/.local/bin/networkminer && "
           "test -L /home/ride-test/.local/share/applications/networkminer.desktop")
    vm.run(f"test \"$(stat -c '%a' {DATA})\" = 700")

    vm.run(f"mkdir -p {DATA}/Captures {DATA}/AssembledFiles && "
           f"printf 'seed capture\\n' > {DATA}/Captures/seed.pcap && "
           f"printf 'seed output\\n' > {DATA}/AssembledFiles/seed.txt")
    before = vm.run(f"sha256sum {DATA}/Captures/seed.pcap {DATA}/AssembledFiles/seed.txt").stdout

    # A timeout is the expected result for a GUI process kept alive under Xvfb.
    gui = vm.run(f"timeout --signal=TERM 15s xvfb-run -a mono {APP}/payload/NetworkMiner.exe",
                 check=False, timeout=30)
    assert gui.returncode == 124, gui.stderr
    assert "package.networkminer\t" in user_ride(vm, "status", "package.networkminer").stdout
    repeated = user_ride(vm, "apply", "--profile", APP_PROFILE, "--allow-candidate")
    assert "unchanged" in repeated.stdout

    user_ride(vm, "restore", "--run-id", run_id, "--allow-candidate", timeout=300)
    vm.run(f"test ! -e {APP} && test ! -e /home/ride-test/.local/bin/networkminer")
    assert vm.run(f"sha256sum {DATA}/Captures/seed.pcap {DATA}/AssembledFiles/seed.txt").stdout == before

    user_ride(vm, "apply", "--profile", APP_PROFILE, "--allow-candidate", timeout=900)
    user_ride(vm, "remove", "--profile", APP_PROFILE, "--allow-candidate", timeout=300)
    vm.run(f"test ! -e {APP} && test ! -e /home/ride-test/.local/bin/networkminer && "
           "test ! -e /home/ride-test/.local/share/applications/networkminer.desktop")
    assert vm.run(f"sha256sum {DATA}/Captures/seed.pcap {DATA}/AssembledFiles/seed.txt").stdout == before
    vm.run(f"sudo {vm.repo}/ride.sh remove --profile {RUNTIME_PROFILE} --allow-candidate", timeout=900)
    runtime_removed = vm.run("rpm -q gtk2 mono-core mono-winforms", check=False)
    assert runtime_removed.returncode != 0
    if not xvfb_preinstalled:
        vm.run("sudo dnf -y remove xorg-x11-server-Xvfb", timeout=600)
