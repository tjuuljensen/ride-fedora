"""Ownership and exact recovery checks for the system Flathub remote."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/v3/flatpak.sh"
URL = "https://dl.flathub.org/repo/"


class FlathubRemoteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ride-flathub-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.marker_dir = self.root / "owned-remotes"
        self.marker = self.marker_dir / "system-flathub.json"
        self.remotes = self.root / "system-remotes.json"
        self.apps = self.root / "system-apps.json"
        self.write_remotes([])
        self.apps.write_text("[]\n", encoding="utf-8")

    def write_remotes(self, rows):
        self.remotes.write_text(json.dumps(rows) + "\n", encoding="utf-8")

    def shell(self, body, *, marker_failure=False):
        script = f"""set -euo pipefail
source {MODULE}
ride_flathub_marker_dir() {{ printf '%s\\n' "$FH_TEST_MARKER_DIR"; }}
ride_flathub_marker_metadata_ok() {{ [[ "$(stat -c '%a:%h' -- "$1")" == 600:1 ]]; }}
ride_flathub_marker_dir_ok() {{ [[ -d "$1" && ! -L "$1" && "$(stat -c '%a' -- "$1")" == 700 ]]; }}
ride_flathub_write_marker() {{
  [[ "${{FH_FAIL_MARKER:-0}}" != 1 ]] || return 1
  mkdir -p -m 700 "$FH_TEST_MARKER_DIR"
  ride_flathub_marker_content > "$(ride_flathub_marker)"
  chmod 600 "$(ride_flathub_marker)"
}}
ride_require_command() {{ command -v "$1" >/dev/null; }}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 1; }}
ride_error() {{ printf '%s\\n' "$*" >&2; }}
flatpak() {{
  case "$*" in
    'remotes --system --columns=name,url,options --json') cat "$FH_TEST_REMOTES" ;;
    'list --system --columns=application,origin --json') cat "$FH_TEST_APPS" ;;
    'remote-add --system flathub https://dl.flathub.org/repo/flathub.flatpakrepo')
      python3 -c 'import json,os; p=os.environ["FH_TEST_REMOTES"]; x=json.load(open(p)); x.append({{"name":"flathub","url":"{URL}","options":""}}); json.dump(x,open(p,"w"))' ;;
    'remote-delete --system flathub')
      python3 -c 'import json,os; p=os.environ["FH_TEST_REMOTES"]; x=[r for r in json.load(open(p)) if r["name"] != "flathub"]; json.dump(x,open(p,"w"))' ;;
    *) printf 'unexpected flatpak call: %s\\n' "$*" >&2; return 2 ;;
  esac
}}
{body}
"""
        env = os.environ.copy()
        env.update(FH_TEST_MARKER_DIR=str(self.marker_dir), FH_TEST_REMOTES=str(self.remotes),
                   FH_TEST_APPS=str(self.apps), FH_FAIL_MARKER="1" if marker_failure else "0")
        return subprocess.run(["bash", "-c", script], env=env, text=True,
                              capture_output=True, check=False)

    def test_add_repeat_and_remove_owned_remote(self):
        self.write_remotes([{"name": "fedora", "url": "oci+https://registry.fedoraproject.org", "options": "oci"}])
        result = self.shell('ride_flathub_change configured\nride_flathub_remote_state\n'
                            'ride_flathub_change configured\nride_flathub_change absent\nride_flathub_remote_state')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["configured", "absent"])
        self.assertEqual(json.loads(self.remotes.read_text()), [
            {"name": "fedora", "url": "oci+https://registry.fedoraproject.org", "options": "oci"}])
        self.assertFalse(self.marker.exists())

    def test_preexisting_remote_and_marker_drift_refused(self):
        self.write_remotes([{"name": "flathub", "url": URL, "options": ""}])
        result = self.shell('ride_flathub_change configured')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("already exists", result.stderr)
        self.marker_dir.mkdir(mode=0o700)
        self.marker.write_text('{"changed":true}\n', encoding="utf-8")
        self.marker.chmod(0o600)
        result = self.shell('ride_flathub_change absent')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(self.remotes.read_text())[0]["url"], URL)

    def test_attached_apps_block_owned_remote_removal(self):
        made = self.shell('ride_flathub_change configured')
        self.assertEqual(made.returncode, 0, made.stderr)
        self.apps.write_text('[{"application":"org.example.App","origin":"flathub"}]\n', encoding="utf-8")
        result = self.shell('ride_flathub_change absent')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("apps use it", result.stderr)
        self.assertEqual(json.loads(self.remotes.read_text())[0]["name"], "flathub")

    def test_url_or_gpg_verification_drift_blocks_removal(self):
        made = self.shell('ride_flathub_change configured')
        self.assertEqual(made.returncode, 0, made.stderr)
        for changed in (
            {"name": "flathub", "url": "https://mirror.example/repo/", "options": ""},
            {"name": "flathub", "url": URL, "options": "no-gpg-verify"},
        ):
            self.write_remotes([changed])
            result = self.shell('ride_flathub_change absent')
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(self.remotes.read_text()), [changed])
        self.write_remotes([{"name": "flathub", "url": URL, "options": ""}])
        result = self.shell('ride_flathub_change absent')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_marker_write_failure_rolls_back_remote(self):
        result = self.shell('ride_flathub_change configured', marker_failure=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(self.remotes.read_text()), [])
        self.assertFalse(self.marker.exists())


if __name__ == "__main__":
    unittest.main()
