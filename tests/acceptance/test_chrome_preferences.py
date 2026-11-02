"""Chrome recommended policies flow through the Flathub wrapper and recover exactly."""

import json

import pytest


PROFILE = "fedora-chrome-preferences"
POLICY = "/etc/opt/chrome/policies/recommended/ride-fedora.json"
OWNER = "/var/lib/ride-fedora/owned-chrome/setting.chrome-preferences.json"


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_chrome_preferences_policy_lifecycle_and_flatpak_import(vm):
    vm.ride("apply", "--profile", "flathub-system", "--allow-candidate", timeout=900)
    plan = vm.ride("plan", "--profile", PROFILE)
    assert "package.chrome" in plan.stdout and "setting.chrome-preferences" in plan.stdout
    refused = vm.ride("apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr

    vm.ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=1500)
    expected = {
        "HomepageLocation": "https://www.google.com",
        "HomepageIsNewTabPage": False,
        "ShowHomeButton": True,
        "DefaultBrowserSettingEnabled": False,
        "SafeBrowsingEnabled": False,
        "SafeBrowsingExtendedReportingEnabled": False,
        "NetworkPredictionOptions": 2,
        "BookmarkBarEnabled": True,
    }
    observed = json.loads(vm.run(f"sudo cat {POLICY}").stdout)
    assert observed == expected
    assert vm.run(f"sudo stat -c %a {OWNER}").stdout.strip() == "600"
    assert "configured" in vm.ride("status", "setting.chrome-preferences").stdout
    repeated = vm.ride("apply", "--profile", PROFILE, "--allow-candidate")
    assert "unchanged setting.chrome-preferences" in repeated.stdout

    # The currently reviewed Flathub wrapper merges /run/host/etc/opt/chrome/
    # policies into its policy directories before launching Chrome. Confirm
    # that deployment grants this host path; user-visible policy state is H091.
    permissions = vm.run("flatpak info --show-permissions com.google.Chrome").stdout
    assert "host-etc" in permissions

    vm.ride("remove", "--profile", PROFILE, "--allow-candidate", timeout=1200)
    vm.run(f"sudo test ! -e {POLICY} && sudo test ! -e {OWNER}")
    assert "absent" in vm.ride("status", "setting.chrome-preferences").stdout
