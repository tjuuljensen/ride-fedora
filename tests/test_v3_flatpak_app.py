"""Owned system Flatpak app behavior for Halloy and Gear Lever."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/v3/flatpak.sh"
REMOTE_URL = "https://dl.flathub.org/repo/"
class HalloyFlatpakTests(unittest.TestCase):
    APP_ID = "org.squidowl.halloy"

    def setUp(self):
        self.app_id = self.APP_ID
        self.entry = json.dumps({"applicationId": self.app_id})
        self.temp = tempfile.TemporaryDirectory(prefix="ride-halloy-flatpak-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.remotes = self.root / "remotes.json"
        self.apps = self.root / "apps.json"
        self.calls = self.root / "calls.txt"
        self.data = self.root / "halloy-data.txt"
        self.write_remotes([{"name": "flathub", "url": REMOTE_URL, "options": ""}])
        self.write_apps([])
        self.data.write_text("preserve profile\n", encoding="utf-8")

    def write_remotes(self, rows):
        self.remotes.write_text(json.dumps(rows) + "\n", encoding="utf-8")

    def write_apps(self, rows):
        self.apps.write_text(json.dumps(rows) + "\n", encoding="utf-8")

    def shell(self, body):
        script = f"""set -euo pipefail
source {MODULE}
ride_require_command() {{ :; }}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
rpm() {{ [[ "${{HF_OLD_APPIMAGELAUNCHER:-0}}" == 1 ]]; }}
flatpak() {{
  printf '%s\\n' "$*" >> "$HF_CALLS"
  case "$*" in
    'remotes --system --columns=name,url,options --json') cat "$HF_REMOTES" ;;
    'list --system --columns=application,origin --json') cat "$HF_APPS" ;;
    'install --system --noninteractive flathub {self.app_id}')
      [[ "${{HF_FAIL_INSTALL:-0}}" != 1 ]] || return 3
      python3 -c 'import json,os; p=os.environ["HF_APPS"]; x=json.load(open(p)); x.append({{"application_id":"{self.app_id}","origin":"flathub"}}); json.dump(x,open(p,"w"))' ;;
    'uninstall --system --noninteractive {self.app_id}')
      python3 -c 'import json,os; p=os.environ["HF_APPS"]; x=[a for a in json.load(open(p)) if a.get("application_id",a.get("application")) != "{self.app_id}"]; json.dump(x,open(p,"w"))' ;;
    *) printf 'unexpected flatpak call: %s\\n' "$*" >&2; return 2 ;;
  esac
}}
{body}
"""
        env = os.environ.copy()
        env.update(HF_REMOTES=str(self.remotes), HF_APPS=str(self.apps), HF_CALLS=str(self.calls),
                   HF_ENTRY=self.entry,
                   HF_FAIL_INSTALL="0", HF_OLD_APPIMAGELAUNCHER="0")
        return subprocess.run(["bash", "-c", script], env=env, text=True,
                              capture_output=True, check=False)

    def test_install_repeat_status_and_remove_preserves_data(self):
        result = self.shell(
            'ride_flatpak_app_preflight "$HF_ENTRY" installed\n'
            'ride_flatpak_app_change "$HF_ENTRY" installed\n'
            'ride_flatpak_app_state "$HF_ENTRY"\n'
            'ride_flatpak_app_preflight "$HF_ENTRY" installed\n'
            'ride_flatpak_app_change "$HF_ENTRY" absent\n'
            'ride_flatpak_app_state "$HF_ENTRY"'
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["installed", "absent"])
        self.assertEqual(self.data.read_text(encoding="utf-8"), "preserve profile\n")
        calls = self.calls.read_text(encoding="utf-8").splitlines()
        self.assertIn(f"install --system --noninteractive flathub {self.app_id}", calls)
        self.assertIn(f"uninstall --system --noninteractive {self.app_id}", calls)
        self.assertFalse(any("delete-data" in call for call in calls))

    def test_wrong_origin_is_refused(self):
        self.write_apps([{"application_id": self.app_id, "origin": "other-remote"}])
        result = self.shell('ride_flatpak_app_preflight "$HF_ENTRY" absent')
        self.assertEqual(result.returncode, 42)
        self.assertIn("installed from an unexpected origin", result.stderr)

    def test_missing_remote_blocks_first_install(self):
        self.write_remotes([])
        result = self.shell('ride_flatpak_app_preflight "$HF_ENTRY" installed')
        self.assertEqual(result.returncode, 42)
        self.assertIn("GPG-verified system Flathub remote is required", result.stderr)

    def test_unverified_or_wrong_remote_blocks_first_install(self):
        for row in (
            {"name": "flathub", "url": "https://mirror.example/repo/", "options": ""},
            {"name": "flathub", "url": REMOTE_URL, "options": "no-gpg-verify"},
        ):
            with self.subTest(row=row):
                self.write_remotes([row])
                result = self.shell('ride_flatpak_app_preflight "$HF_ENTRY" installed')
                self.assertEqual(result.returncode, 42)

    def test_duplicate_flathub_remotes_block_first_install(self):
        self.write_remotes([
            {"name": "flathub", "url": REMOTE_URL, "options": ""},
            {"name": "flathub", "url": REMOTE_URL, "options": ""},
        ])
        result = self.shell('ride_flatpak_app_preflight "$HF_ENTRY" installed')
        self.assertEqual(result.returncode, 42)

    def test_failed_install_leaves_app_absent(self):
        script = f"""set -euo pipefail
source {MODULE}
ride_require_command() {{ :; }}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
rpm() {{ return 1; }}
flatpak() {{
  case "$*" in
    'remotes --system --columns=name,url,options --json') cat "$HF_REMOTES" ;;
    'list --system --columns=application,origin --json') cat "$HF_APPS" ;;
    'install --system --noninteractive flathub {self.app_id}') return 3 ;;
  esac
}}
ride_flatpak_app_change "$HF_ENTRY" installed
"""
        env = os.environ.copy()
        env.update(HF_REMOTES=str(self.remotes), HF_APPS=str(self.apps), HF_ENTRY=self.entry)
        result = subprocess.run(["bash", "-c", script], env=env, text=True,
                                capture_output=True, check=False)
        self.assertEqual(result.returncode, 3)
        self.assertEqual(json.loads(self.apps.read_text(encoding="utf-8")), [])


class GearLeverFlatpakTests(HalloyFlatpakTests):
    APP_ID = "it.mijorus.gearlever"

    def test_legacy_appimagelauncher_package_conflict_is_refused(self):
        script = f"""set -euo pipefail
source {MODULE}
ride_require_command() {{ :; }}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
rpm() {{ return 0; }}
flatpak() {{
  case "$*" in
    'remotes --system --columns=name,url,options --json') cat "$HF_REMOTES" ;;
    'list --system --columns=application,origin --json') cat "$HF_APPS" ;;
    *) return 2 ;;
  esac
}}
ride_flatpak_app_preflight "$HF_ENTRY" installed
"""
        env = os.environ.copy()
        env.update(HF_REMOTES=str(self.remotes), HF_APPS=str(self.apps), HF_ENTRY=self.entry)
        result = subprocess.run(["bash", "-c", script], env=env, text=True,
                                capture_output=True, check=False)
        self.assertEqual(result.returncode, 42)
        self.assertIn("AppImageLauncher RPM is installed", result.stderr)


if __name__ == "__main__":
    unittest.main()
