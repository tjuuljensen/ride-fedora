"""Chrome recommended policy ownership and exact recovery tests."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/v3/chrome_preferences.sh"
COMMON = ROOT / "lib/v3/common.sh"
POLICIES = [
    "homepage", "homepage-not-newtab", "home-button", "no-default-browser-prompt",
    "disable-safe-browsing", "no-safe-browsing-reporting",
    "disable-network-prediction", "bookmark-bar",
]


class ChromePreferencesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.policy = self.root / "etc/opt/chrome/policies/recommended/ride-fedora.json"
        self.manifest = self.root / "var/lib/ride-fedora/owned-chrome/setting.chrome-preferences.json"

    def tearDown(self):
        self.temp.cleanup()

    def run_handler(self, action, selected=None, check=True):
        entry = {"selectedValue": json.dumps(selected or POLICIES)}
        script = (
            f"source {COMMON}; source {MODULE}; "
            f"ride_chrome_preferences_change '{json.dumps(entry)}' {action}; "
            "ride_chrome_preferences_observe"
        )
        env = os.environ | {
            "RIDE_CHROME_POLICY_FILE": str(self.policy),
            "RIDE_CHROME_POLICY_MANIFEST": str(self.manifest),
        }
        return subprocess.run(["bash", "-c", script], env=env, text=True, capture_output=True, check=check)

    def test_apply_repeat_status_and_exact_remove(self):
        self.run_handler("configured")
        initial = self.policy.read_text()
        document = json.loads(initial)
        self.assertEqual(document["HomepageLocation"], "https://www.google.com")
        self.assertIs(document["SafeBrowsingEnabled"], False)
        self.assertEqual(self.manifest.stat().st_mode & 0o777, 0o600)
        self.run_handler("configured")
        self.assertEqual(self.policy.read_text(), initial)
        self.run_handler("absent")
        self.assertFalse(self.policy.exists())
        self.assertFalse(self.manifest.exists())

    def test_unowned_and_modified_policy_are_preserved(self):
        self.policy.parent.mkdir(parents=True)
        self.policy.write_text('{"UserPolicy":true}\n')
        result = self.run_handler("configured", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.policy.read_text(), '{"UserPolicy":true}\n')
        self.policy.unlink()
        self.run_handler("configured")
        self.policy.write_text(self.policy.read_text().replace("HomepageLocation", "ChangedPolicy"))
        result = self.run_handler("absent", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(self.policy.exists())
        self.assertTrue(self.manifest.exists())

    def test_selection_is_fixed_and_unknown_policy_is_rejected(self):
        result = self.run_handler("configured", ["HomepageLocation\":\"https://evil.invalid\""], check=False)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
