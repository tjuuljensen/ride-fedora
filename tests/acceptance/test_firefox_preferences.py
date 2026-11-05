"""Owned Fedora Firefox AutoConfig lifecycle and startup smoke test."""

import json
from pathlib import Path

import pytest


PROFILE = "fedora-firefox-preferences"
ROOT = Path(__file__).resolve().parents[2]
OPERATION = "setting.firefox-preferences"
FILES = (
    "/usr/lib64/firefox/mozilla.cfg",
    "/usr/lib64/firefox/defaults/pref/autoconfig.js",
    "/usr/lib64/firefox/browser/override.ini",
)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_firefox_preferences_lifecycle_and_startup(vm):
    catalog_data = json.loads((ROOT / "catalog/operations.json").read_text(encoding="utf-8"))
    operation = next(item for item in catalog_data["operations"] if item["id"] == OPERATION)
    operation["unsetState"] = "absent"
    catalog = vm.put_json("firefox-preferences-acceptance-catalog", catalog_data)
    vm.run("rpm -q firefox")
    for path in FILES:
        vm.run(f"test ! -e {path} && test ! -L {path}")
    plan = vm.ride("plan", "--profile", PROFILE, catalog=catalog)
    assert "setting.firefox-preferences" in plan.stdout
    refused = vm.ride("apply", "--profile", PROFILE, catalog=catalog, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    applied = vm.ride("apply", "--profile", PROFILE, "--allow-candidate", catalog=catalog)
    apply_run_id = applied.stdout.split("Run ID: ", 1)[1].splitlines()[0]
    vm.run("sudo jq -e '.schemaVersion == 1 and (.files | length == 3)' "
           "/var/lib/ride-fedora/owned-firefox/setting.firefox-preferences.json")
    for path in FILES:
        vm.run(f"sudo test -s {path}")
    assert "configured" in vm.ride("status", OPERATION, catalog=catalog).stdout
    repeat = vm.ride("apply", "--profile", PROFILE, "--allow-candidate", catalog=catalog)
    assert "unchanged setting.firefox-preferences" in repeat.stdout

    vm.run("mkdir -p /tmp/ride-firefox-profile")
    # Firefox remains open as a GUI process; a clean bounded timeout proves it
    # started and stayed alive with AutoConfig loaded.
    startup = vm.run("timeout 25 firefox --headless --no-remote --profile "
                     "/tmp/ride-firefox-profile about:blank", timeout=45, check=False)
    assert startup.returncode == 124, startup
    assert "headless mode" in (startup.stdout + startup.stderr).lower()
    vm.run("test -d /tmp/ride-firefox-profile")

    unset = vm.ride("unset", OPERATION, "--allow-candidate", catalog=catalog)
    unset_run_id = unset.stdout.split("Run ID: ", 1)[1].splitlines()[0]
    for path in FILES:
        vm.run(f"sudo test ! -e {path}")
    assert "absent" in vm.ride("status", OPERATION, catalog=catalog).stdout
    repeated_unset = vm.ride("unset", OPERATION, "--allow-candidate", catalog=catalog)
    assert "unchanged setting.firefox-preferences" in repeated_unset.stdout

    vm.ride("restore", "--run-id", unset_run_id, "--allow-candidate", catalog=catalog)
    for path in FILES:
        vm.run(f"sudo test -s {path}")
    assert "configured" in vm.ride("status", OPERATION, catalog=catalog).stdout
    vm.ride("restore", "--run-id", apply_run_id, "--allow-candidate", catalog=catalog)
    for path in FILES:
        vm.run(f"sudo test ! -e {path}")
    assert "absent" in vm.ride("status", OPERATION, catalog=catalog).stdout
