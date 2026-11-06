"""Chrome recommended policies flow through the Flathub wrapper and recover exactly."""

import json
import re

import pytest


PROFILE = "fedora-chrome-preferences"
POLICY = "/etc/opt/chrome/policies/recommended/ride-fedora.json"
OWNER = "/var/lib/ride-fedora/owned-chrome/setting.chrome-preferences.json"
RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_chrome_preferences_policy_lifecycle_and_flatpak_import(vm):
    vm.ride("apply", "--profile", "flathub-system", "--allow-candidate", timeout=900)
    plan = vm.ride("plan", "--profile", PROFILE)
    assert "package.chrome" in plan.stdout and "setting.chrome-preferences" in plan.stdout
    refused = vm.ride("apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr

    applied = vm.ride("apply", "--profile", PROFILE, "--allow-candidate", timeout=1500)
    apply_run_id = RUN_ID.search(applied.stdout).group(1)
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

    unset = vm.ride("unset", "setting.chrome-preferences", "--allow-candidate")
    unset_run_id = RUN_ID.search(unset.stdout).group(1)
    unset_record = json.loads(vm.run(
        f"sudo cat /var/lib/ride-fedora/runs/{unset_run_id}.json"
    ).stdout)
    assert unset_record["steps"][0]["selectedValue"] == (
        '["homepage","homepage-not-newtab","home-button","no-default-browser-prompt",'
        '"disable-safe-browsing","no-safe-browsing-reporting","disable-network-prediction","bookmark-bar"]'
    )
    vm.run(f"sudo test ! -e {POLICY} && sudo test ! -e {OWNER}")
    assert "absent" in vm.ride("status", "setting.chrome-preferences").stdout
    repeated_unset = vm.ride("unset", "setting.chrome-preferences", "--allow-candidate")
    assert "unchanged setting.chrome-preferences" in repeated_unset.stdout

    vm.ride("restore", "--run-id", unset_run_id, "--allow-candidate")
    assert json.loads(vm.run(f"sudo cat {POLICY}").stdout) == expected
    assert "configured" in vm.ride("status", "setting.chrome-preferences").stdout
    vm.ride("restore", "--run-id", apply_run_id, "--allow-candidate")
    vm.run(f"sudo test ! -e {POLICY} && sudo test ! -e {OWNER}")
    assert "absent" in vm.ride("status", "setting.chrome-preferences").stdout

    vm.ride("remove", "--profile", PROFILE, "--allow-candidate", timeout=1200)
    vm.run(f"sudo test ! -e {POLICY} && sudo test ! -e {OWNER}")
    assert "absent" in vm.ride("status", "setting.chrome-preferences").stdout
