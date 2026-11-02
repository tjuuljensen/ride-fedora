"""Owned Fedora Firefox AutoConfig lifecycle and startup smoke test."""

import pytest


PROFILE = "fedora-firefox-preferences"
FILES = (
    "/usr/lib64/firefox/mozilla.cfg",
    "/usr/lib64/firefox/defaults/pref/autoconfig.js",
    "/usr/lib64/firefox/browser/override.ini",
)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_firefox_preferences_lifecycle_and_startup(vm):
    vm.run("rpm -q firefox")
    for path in FILES:
        vm.run(f"test ! -e {path} && test ! -L {path}")
    plan = vm.ride("plan", "--profile", PROFILE)
    assert "setting.firefox-preferences" in plan.stdout
    refused = vm.ride("apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    vm.ride("apply", "--profile", PROFILE, "--allow-candidate")
    vm.run("sudo jq -e '.schemaVersion == 1 and (.files | length == 3)' "
           "/var/lib/ride-fedora/owned-firefox/setting.firefox-preferences.json")
    for path in FILES:
        vm.run(f"sudo test -s {path}")
    assert "configured" in vm.ride("status", "setting.firefox-preferences").stdout
    repeat = vm.ride("apply", "--profile", PROFILE, "--allow-candidate")
    assert "unchanged setting.firefox-preferences" in repeat.stdout

    vm.run("mkdir -p /tmp/ride-firefox-profile")
    # Firefox remains open as a GUI process; a clean bounded timeout proves it
    # started and stayed alive with AutoConfig loaded.
    startup = vm.run("timeout 25 firefox --headless --no-remote --profile "
                     "/tmp/ride-firefox-profile about:blank", timeout=45, check=False)
    assert startup.returncode == 124, startup
    assert "headless mode" in (startup.stdout + startup.stderr).lower()
    vm.run("test -d /tmp/ride-firefox-profile")

    vm.ride("remove", "--profile", PROFILE, "--allow-candidate")
    for path in FILES:
        vm.run(f"sudo test ! -e {path}")
    assert "absent" in vm.ride("status", "setting.firefox-preferences").stdout
