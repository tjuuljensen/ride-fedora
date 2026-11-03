"""Firefox global XPI install, restart, removal, and recovery contract."""

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
PROFILE = "fedora-firefox-addons"
APP_ID = "{ec8030f7-c20a-464f-9b0e-13a3a9e97384}"
TARGET = f"/usr/lib64/mozilla/extensions/{APP_ID}"
POLICY = "/etc/firefox/policies/policies.json"
STATE = "/var/lib/ride-fedora/firefox-global-xpis.json"
BACKUP = "/var/lib/ride-fedora/firefox-global-xpi-removal"
UNRELATED_POLICY = (
    '{"policies":{"Homepage":{"URL":"https://example.invalid"},'
    '"ExtensionSettings":{"unrelated@example.invalid":'
    '{"installation_mode":"allowed"}}}}'
)


def run_firefox(vm):
    return vm.run(
        "timeout 60 firefox --headless --no-remote --profile "
        "/home/ride-test/.mozilla/firefox/ride-global-xpi-test about:blank",
        timeout=75,
        check=False,
    )


def addon_ids(vm):
    result = vm.run(
        "jq -r '.addons[]?.id' "
        "/home/ride-test/.mozilla/firefox/ride-global-xpi-test/extensions.json "
        "2>/dev/null | sort"
    )
    return set(result.stdout.splitlines())


def read_policy(vm):
    return json.loads(vm.run(f"sudo cat {POLICY}").stdout)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_firefox_global_xpi_lifecycle_and_restart_recovery(vm):
    catalog = json.loads((ROOT / "catalog" / "operations.json").read_text())
    operation = next(entry for entry in catalog["operations"]
                     if entry["id"] == "setting.firefox-addons")
    assert operation["status"] == "candidate"
    guest_catalog = vm.put_json("firefox-test-catalog", catalog)
    manifest = json.loads((ROOT / "policies/firefox-extensions.json").read_text())
    ids = {extension["id"] for extension in manifest["extensions"]}

    vm.run("rpm -q firefox && firefox --version")
    vm.run(f"sudo test ! -e {STATE} && sudo test ! -e {BACKUP}")
    for extension_id in ids:
        vm.run(f"sudo test ! -e {TARGET}/{extension_id}.xpi")
    vm.run(
        "mkdir -p /home/ride-test/.mozilla/firefox/ride-global-xpi-test && "
        "cat > /home/ride-test/.mozilla/firefox/profiles.ini <<'EOF'\n"
        "[Profile0]\nName=RIDE acceptance\nIsRelative=1\n"
        "Path=ride-global-xpi-test\nDefault=1\nEOF\n"
        "printf 'preserve profile data\\n' > /home/ride-test/.mozilla/firefox/"
        "ride-global-xpi-test/user-data.txt"
    )
    existing_policy = vm.run(f"sudo test -f {POLICY}", check=False).returncode == 0
    if not existing_policy:
        vm.run("sudo mkdir -p /etc/firefox/policies")
        vm.run(f"printf '%s\\n' {json.dumps(UNRELATED_POLICY)} | "
               f"sudo tee {POLICY} >/dev/null")
    original_policy = read_policy(vm)

    plan = vm.ride("plan", "--profile", PROFILE)
    assert "setting.firefox-addons" in plan.stdout
    refused = vm.ride("apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    vm.ride("apply", "--profile", PROFILE, "--allow-candidate", catalog=guest_catalog,
            timeout=1200)
    assert "configured" in vm.ride("status", "setting.firefox-addons",
                                   catalog=guest_catalog).stdout
    repeat = vm.ride("apply", "--profile", PROFILE, "--allow-candidate",
                     catalog=guest_catalog)
    assert "unchanged setting.firefox-addons" in repeat.stdout
    assert read_policy(vm) == original_policy
    assert int(vm.run(f"sudo find {TARGET} -maxdepth 1 -name '*.xpi' | wc -l").stdout) == len(ids)

    startup = run_firefox(vm)
    assert startup.returncode == 124, startup
    vm.run("! pgrep -x firefox")
    assert ids <= addon_ids(vm), sorted(ids - addon_ids(vm))
    assert read_policy(vm) == original_policy

    removal = vm.ride("remove", "--profile", PROFILE, "--allow-candidate",
                      catalog=guest_catalog)
    pending_id = removal.stdout.split("Run ID: ", 1)[1].splitlines()[0]
    journal = json.loads(vm.run(
        f"sudo cat /var/lib/ride-fedora/runs/{pending_id}.json"
    ).stdout)
    assert journal["status"] == "pending"
    assert "removal-pending" in vm.ride("status", "setting.firefox-addons",
                                        catalog=guest_catalog).stdout
    assert int(vm.run(f"sudo find {BACKUP} -maxdepth 1 -name '*.xpi' | wc -l").stdout) == len(ids)
    assert not vm.run(f"sudo find {TARGET} -maxdepth 1 -name '*.xpi'").stdout.strip()
    assert read_policy(vm) == original_policy

    restored = vm.ride("restore", "--run-id", pending_id, "--allow-candidate",
                       catalog=guest_catalog)
    assert "changed setting.firefox-addons: removal-pending -> configured" in restored.stdout
    assert "configured" in vm.ride("status", "setting.firefox-addons",
                                   catalog=guest_catalog).stdout
    assert not vm.run(f"sudo test -e {BACKUP}", check=False).returncode == 0

    vm.ride("remove", "--profile", PROFILE, "--allow-candidate",
            catalog=guest_catalog)
    blocked_startup = run_firefox(vm)
    assert blocked_startup.returncode == 124, blocked_startup
    vm.run("! pgrep -x firefox")
    assert not (ids & addon_ids(vm))
    vm.ride("set", "setting.firefox-addons", "--state", "absent", "--allow-candidate",
            catalog=guest_catalog)
    assert "absent" in vm.ride("status", "setting.firefox-addons",
                               catalog=guest_catalog).stdout
    assert not vm.run(f"sudo test -e {STATE}", check=False).returncode == 0
    assert not vm.run(f"sudo test -e {BACKUP}", check=False).returncode == 0
    assert read_policy(vm) == original_policy
    vm.run("test -f /home/ride-test/.mozilla/firefox/ride-global-xpi-test/user-data.txt")
