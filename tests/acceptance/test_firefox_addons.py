"""Firefox ExtensionSettings install, restart, removal, and recovery contract."""

import json
from pathlib import Path

import pytest


PROFILE = "fedora-firefox-addons"
IDS = (
    "chrome-gnome-shell@gnome.org",
    "uBlock0@raymondhill.net",
    "jid1-MnnxcxisBPnSXQ@jetpack",
    "{73a6fe31-595d-460b-a920-fcc0f8843232}",
    "jid0-YQz0l1jthOIz179ehuitYAOdBEs@jetpack",
    "disable-html5-autoplay@afnankhan",
    "{b9db16a4-6edc-47ec-a1f4-b86292ed211d}",
    "{0b457cAA-602d-484a-8fe7-c1d894a011ba}",
    "nimbusscreencaptureff@everhelper.me",
    "wayback_machine@mozilla.org",
    "error404waybackmachine@lafleur.com",
    "exif_viewer@mozilla.doslash.org",
    "linkgopher@oooninja.com",
    "{9efc0280-b125-400e-b53d-2d09d7effab4}",
    "{446900e4-71c2-419f-a6a7-df9c091e268b}",
    "firefox-addon@expressvpn.com",
)
UNRELATED_POLICY = '{"policies":{"Homepage":{"URL":"https://example.invalid"},"ExtensionSettings":{"unrelated@example.invalid":{"installation_mode":"allowed"}}}}'


def run_firefox(vm):
    return vm.run(
        "timeout 60 firefox --headless --no-remote --profile "
        "/home/ride-test/.mozilla/firefox/ride-policy-test about:blank",
        timeout=75,
        check=False,
    )


def addon_ids(vm):
    result = vm.run(
        "jq -r '.addons[]?.id' "
        "/home/ride-test/.mozilla/firefox/ride-policy-test/extensions.json "
        "2>/dev/null | sort"
    )
    return set(result.stdout.splitlines())


def policy(vm):
    return json.loads(vm.run("sudo cat /etc/firefox/policies/policies.json").stdout)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_firefox_addon_policy_lifecycle_and_restart_recovery(vm):
    catalog = json.loads((Path(__file__).resolve().parents[2] /
                         "catalog" / "operations.json").read_text())
    catalog["operations"] = [entry for entry in catalog["operations"]
                             if entry["id"] == "setting.firefox-addons"]
    catalog["operations"][0]["status"] = "candidate"
    guest_catalog = vm.put_json("firefox-test-catalog", catalog)

    vm.run("rpm -q firefox")
    vm.run("sudo test ! -e /etc/firefox/policies/policies.json")
    vm.run(
        "mkdir -p /home/ride-test/.mozilla/firefox/ride-policy-test && "
        "cat > /home/ride-test/.mozilla/firefox/profiles.ini <<'EOF'\n"
        "[Profile0]\nName=RIDE acceptance\nIsRelative=1\n"
        "Path=ride-policy-test\nDefault=1\nEOF\n"
        "printf 'preserve profile data\\n' > "
        "/home/ride-test/.mozilla/firefox/ride-policy-test/user-data.txt"
    )
    vm.run("sudo mkdir -p /etc/firefox/policies")
    vm.run(f"printf '%s\\n' {json.dumps(UNRELATED_POLICY)} | "
           "sudo tee /etc/firefox/policies/policies.json >/dev/null")

    plan = vm.ride("plan", "--profile", PROFILE)
    assert "setting.firefox-addons" in plan.stdout
    refused = vm.ride("apply", "--profile", PROFILE, check=False)
    assert refused.returncode != 0 and "operation is blocked" in refused.stderr
    vm.ride("apply", "--profile", PROFILE, "--allow-candidate", catalog=guest_catalog,
            timeout=900)
    configured_policy = policy(vm)
    settings = configured_policy["policies"]["ExtensionSettings"]
    assert all(settings[identifier]["installation_mode"] == "normal_installed"
               for identifier in IDS)
    assert settings["unrelated@example.invalid"] == {"installation_mode": "allowed"}
    assert "configured" in vm.ride("status", "setting.firefox-addons",
                                   catalog=guest_catalog).stdout
    repeat = vm.ride("apply", "--profile", PROFILE, "--allow-candidate",
                     catalog=guest_catalog)
    assert "unchanged setting.firefox-addons" in repeat.stdout

    startup = run_firefox(vm)
    assert startup.returncode == 124, startup
    vm.run("! pgrep -x firefox")
    installed = addon_ids(vm)
    assert set(IDS) <= installed, sorted(set(IDS) - installed)

    removal = vm.ride("remove", "--profile", PROFILE, "--allow-candidate",
                      catalog=guest_catalog)
    pending_id = removal.stdout.split("Run ID: ", 1)[1].splitlines()[0]
    journal = json.loads(vm.run(
        f"sudo cat /var/lib/ride-fedora/runs/{pending_id}.json"
    ).stdout)
    assert journal["status"] == "pending"
    assert "removal-pending" in vm.ride("status", "setting.firefox-addons",
                                        catalog=guest_catalog).stdout
    blocked = policy(vm)["policies"]["ExtensionSettings"]
    assert all(blocked[identifier] == {"installation_mode": "blocked"} for identifier in IDS)
    assert blocked["unrelated@example.invalid"] == {"installation_mode": "allowed"}
    vm.run("test -f /home/ride-test/.mozilla/firefox/ride-policy-test/user-data.txt")

    restored = vm.ride("restore", "--run-id", pending_id, "--allow-candidate",
                       catalog=guest_catalog)
    assert "changed setting.firefox-addons: removal-pending -> configured" in restored.stdout
    assert policy(vm)["policies"]["ExtensionSettings"][IDS[0]]["installation_mode"] == "normal_installed"

    vm.ride("remove", "--profile", PROFILE, "--allow-candidate",
            catalog=guest_catalog)
    blocked_startup = run_firefox(vm)
    assert blocked_startup.returncode == 124, blocked_startup
    vm.run("! pgrep -x firefox")
    assert not (set(IDS) & addon_ids(vm))
    vm.ride("set", "setting.firefox-addons", "--state", "absent", "--allow-candidate",
            catalog=guest_catalog)
    finalized = policy(vm)
    assert "ExtensionSettings" in finalized["policies"]
    assert finalized["policies"]["ExtensionSettings"] == {
        "unrelated@example.invalid": {"installation_mode": "allowed"}
    }
    assert "absent" in vm.ride("status", "setting.firefox-addons",
                               catalog=guest_catalog).stdout
    vm.run("test -f /home/ride-test/.mozilla/firefox/ride-policy-test/user-data.txt")
