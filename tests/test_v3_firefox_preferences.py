"""Ownership and exact recovery checks for Firefox AutoConfig files."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/v3/firefox.sh"


class FirefoxPreferencesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ride-firefox-policy-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.firefox = self.root / "firefox"
        for relative in ("defaults/pref", "browser"):
            (self.firefox / relative).mkdir(parents=True)
        self.files = [self.firefox / "mozilla.cfg",
                      self.firefox / "defaults/pref/autoconfig.js",
                      self.firefox / "browser/override.ini"]
        self.owner = self.root / "owned/setting.firefox-preferences.json"

    def shell(self, body):
        script = f"""set -euo pipefail
source {MODULE}
ride_firefox_preferences_files() {{ printf '%s\\n' {self.files[0]} {self.files[1]} {self.files[2]}; }}
ride_firefox_preferences_manifest() {{ printf '%s\\n' {self.owner}; }}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
{body}
"""
        return subprocess.run(["bash", "-c", script], env=os.environ.copy(),
                              text=True, capture_output=True, check=False)

    def test_apply_repeat_and_remove_exact_owned_file_set(self):
        result = self.shell(
            'ride_firefox_preferences_observe\n'
            'ride_firefox_preferences_change configured\n'
            'ride_firefox_preferences_observe\n'
            'ride_firefox_preferences_change configured\n'
            'ride_firefox_preferences_change absent\n'
            'ride_firefox_preferences_observe'
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["absent", "configured", "absent"])
        self.assertFalse(self.owner.exists())
        self.assertTrue(all(not path.exists() for path in self.files))

    def test_unowned_file_blocks_without_claim_or_overwrite(self):
        self.files[0].write_text("user configuration\n", encoding="utf-8")
        result = self.shell('ride_firefox_preferences_change configured')
        self.assertEqual(result.returncode, 42)
        self.assertEqual(self.files[0].read_text(encoding="utf-8"), "user configuration\n")
        self.assertFalse(self.owner.exists())
        self.assertTrue(all(not path.exists() for path in self.files[1:]))

    def test_modified_owned_file_blocks_all_removal(self):
        result = self.shell('ride_firefox_preferences_change configured')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.files[0].write_text("external modification\n", encoding="utf-8")
        result = self.shell('ride_firefox_preferences_change absent')
        self.assertEqual(result.returncode, 42)
        self.assertTrue(all(path.exists() for path in self.files))
        self.assertTrue(self.owner.exists())


if __name__ == "__main__":
    unittest.main()
