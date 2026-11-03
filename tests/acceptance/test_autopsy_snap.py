"""Autopsy Snap package lifecycle, interface state, and snapshot recovery."""

import pytest


PROFILE = "fedora-autopsy"
CASE_PARENT = "/home/ride-test/Documents/ride-autopsy-cases"
CASE_NAME = "ride-v3-empty-case"
CASE_SENTINEL = "/home/ride-test/Documents/ride-autopsy-case-preserve.txt"
SNAP_SENTINEL = "/home/ride-test/snap/autopsy/common/ride-acceptance.txt"


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_autopsy_snap_lifecycle_and_snapshot_recovery(vm):
    vm.ride("apply", "--profile", "snap-runtime", "--allow-candidate", timeout=1200)
    vm.run("systemctl is-active snapd.socket && snap version", timeout=300)
    vm.run("mkdir -p /home/ride-test/Documents")
    vm.run(f"printf 'case output sentinel\\n' > {CASE_SENTINEL}")
    original_case = vm.run(f"sha256sum {CASE_SENTINEL}").stdout.split()[0]

    plan = vm.ride("plan", "--profile", PROFILE)
    assert "package.autopsy" in plan.stdout and "candidate" in plan.stdout
    refused = vm.ride("apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    vm.ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=1500)
    vm.run("snap info autopsy | grep -F 'Sleuth Kit Labs'")
    vm.run("snap list autopsy | grep -F autopsy")
    vm.run("snap connections autopsy > /tmp/autopsy-connections.txt")
    connection_table = vm.run("cat /tmp/autopsy-connections.txt").stdout
    assert "Interface" in connection_table and "block-devices" in connection_table
    connections = {}
    for line in connection_table.splitlines()[1:]:
        fields = line.split()
        if len(fields) >= 3:
            connections.setdefault(fields[0], []).append(fields[2])
    # Record the connections snapd actually established on this Fedora target.
    for interface in ("block-devices", "dm-crypt", "fuse-support"):
        assert connections[interface] == [f":{interface}"]
    assert connections["system-files"] == ["-", "-"]

    # Create a real, empty Autopsy case without opening devices or ingesting
    # evidence. Its case folder is user-owned output outside Snap's data tree.
    vm.run(f"mkdir -p {CASE_PARENT}")
    vm.run(
        f"setsid snap run autopsy --nogui --createCase --caseName={CASE_NAME} "
        f"--caseBaseDir={CASE_PARENT} >/tmp/ride-autopsy-create.log 2>&1 "
        "</dev/null & echo $! >/tmp/ride-autopsy-create.pid"
    )
    case_dir = vm.run(
        f"for attempt in $(seq 1 180); do "
        f"case_dir=$(find {CASE_PARENT} -mindepth 1 -maxdepth 1 -type d "
        f"-name '{CASE_NAME}_*' -print -quit); "
        "db=\"$case_dir/autopsy.db\"; "
        "if [ -n \"$case_dir\" ] && [ -s \"$db\" ] && "
        "find \"$case_dir\" -maxdepth 1 -type f -name '*.aut' -print -quit | grep -q .; then "
        "size1=$(stat -c %s \"$db\"); sleep 5; size2=$(stat -c %s \"$db\"); "
        "if [ \"$size1\" = \"$size2\" ]; then printf '%s\\n' \"$case_dir\"; exit 0; fi; "
        "fi; sleep 5; done; cat /tmp/ride-autopsy-create.log; exit 1",
        timeout=960,
    ).stdout.strip()
    assert case_dir, "Autopsy did not create a stable synthetic case"
    vm.run(f"test -s '{case_dir}/{CASE_NAME}.aut' && test -s '{case_dir}/autopsy.db'")
    vm.run(
        "python3 -c 'import sqlite3,sys; "
        "db=sqlite3.connect(sys.argv[1]); "
        "assert db.execute(\"PRAGMA integrity_check\").fetchone()[0] == \"ok\"' "
        f"'{case_dir}/autopsy.db'"
    )
    # Case creation leaves the Autopsy/Solr application resident. Terminate
    # only its own session after files stabilize and the database passes check.
    vm.run(
        "pid=$(cat /tmp/ride-autopsy-create.pid); "
        "pgid=$(ps -o pgid= -p \"$pid\" | tr -d ' '); "
        "test -n \"$pgid\" && test \"$pgid\" = \"$pid\"; "
        "kill -TERM -- \"-$pgid\"; "
        "for attempt in $(seq 1 60); do "
        "if ! pgrep -g \"$pgid\" >/dev/null; then exit 0; fi; sleep 2; done; "
        "pgrep -a -g \"$pgid\"; exit 1",
        timeout=150,
    )
    case_tree_hash = vm.run(
        f"find '{case_dir}' -type f -print0 | sort -z | "
        "xargs -0 sha256sum | sha256sum | cut -d' ' -f1"
    ).stdout.strip()

    vm.run("mkdir -p /home/ride-test/snap/autopsy/common")
    vm.run(f"printf 'snap app state sentinel\\n' > {SNAP_SENTINEL}")
    vm.ride("remove", "--profile", PROFILE, "--allow-candidate", timeout=900)
    assert vm.run("snap list autopsy", check=False).returncode != 0
    saved = vm.run("sudo snap saved").stdout
    snapshot_id = next(line.split()[0] for line in saved.splitlines()
                       if len(line.split()) >= 7 and line.split()[1] == "autopsy" and line.split()[6] == "auto")
    assert vm.run(f"sha256sum {CASE_SENTINEL}").stdout.split()[0] == original_case
    assert vm.run(
        f"find '{case_dir}' -type f -print0 | sort -z | "
        "xargs -0 sha256sum | sha256sum | cut -d' ' -f1"
    ).stdout.strip() == case_tree_hash
    assert vm.run(f"test ! -e {SNAP_SENTINEL}", check=False).returncode == 0

    vm.ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=1200)
    vm.run(f"sudo snap restore {snapshot_id} autopsy", timeout=300)
    assert vm.run(f"cat {SNAP_SENTINEL}").stdout.strip() == "snap app state sentinel"
    assert vm.run(f"sha256sum {CASE_SENTINEL}").stdout.split()[0] == original_case
    assert vm.run(
        f"find '{case_dir}' -type f -print0 | sort -z | "
        "xargs -0 sha256sum | sha256sum | cut -d' ' -f1"
    ).stdout.strip() == case_tree_hash
    vm.ride("remove", "--profile", PROFILE, "--allow-candidate", timeout=900)
