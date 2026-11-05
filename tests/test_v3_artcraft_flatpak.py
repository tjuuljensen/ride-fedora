"""Owned ArtCraft OCI user remote and candidate app lifecycle tests."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/v3/flatpak.sh"
CATALOG = ROOT / "catalog/operations.json"
APP_ID = "ai.storyteller.photocraft"


class ArtcraftFlatpakTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ride-artcraft-flatpak-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.remotes = self.root / "remotes.json"
        self.apps = self.root / "apps.json"
        self.calls = self.root / "calls.txt"
        self.data = self.root / "project.txt"
        self.remotes.write_text(json.dumps([{
            "name": "flathub", "url": "https://dl.flathub.org/repo/", "options": ""
        }]) + "\n")
        self.apps.write_text("[]\n")
        self.data.write_text("user project\n")

    def shell(self, body, *, fail_install=False):
        script = f'''set -euo pipefail
source "{MODULE}"
ride_require_command() {{ :; }}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
ride_error() {{ printf '%s\\n' "$*" >&2; }}
flatpak() {{
  printf '%s\\n' "$*" >> "$ART_CALLS"
  case "$*" in
    'remotes --user --columns=name,url,options --json') cat "$ART_REMOTES" ;;
    'list --user --columns=application,origin --json') cat "$ART_APPS" ;;
    'remote-add --user artcraft-oci https://getartcraft.com/artcraft-oci.flatpakrepo')
      python3 -c 'import json,os; p=os.environ["ART_REMOTES"]; x=json.load(open(p)); x.append({{"name":"artcraft-oci","url":"oci+https://getartcraft.com","options":"no-gpg-verify"}}); json.dump(x,open(p,"w"))' ;;
    'remote-delete --user artcraft-oci')
      python3 -c 'import json,os; p=os.environ["ART_REMOTES"]; x=[a for a in json.load(open(p)) if a["name"]!="artcraft-oci"]; json.dump(x,open(p,"w"))' ;;
    'install --user --noninteractive artcraft-oci {APP_ID}')
      [[ "${{ART_FAIL_INSTALL:-0}}" != 1 ]] || return 3
      python3 -c 'import json,os; p=os.environ["ART_APPS"]; json.dump([{{"application_id":"{APP_ID}","origin":"artcraft-oci"}}],open(p,"w"))' ;;
    'uninstall --user --noninteractive {APP_ID}')
      printf '[]\\n' > "$ART_APPS" ;;
    *) printf 'unexpected Flatpak call: %s\\n' "$*" >&2; return 2 ;;
  esac
}}
{body}
'''
        env = os.environ.copy()
        env.update(ART_REMOTES=str(self.remotes), ART_APPS=str(self.apps),
                   ART_CALLS=str(self.calls), ART_FAIL_INSTALL="1" if fail_install else "0",
                   XDG_DATA_HOME=str(self.root / "data"),
                   ART_ENTRY=json.dumps({"applicationId": APP_ID}))
        return subprocess.run(["bash", "-c", script], env=env, text=True,
                              capture_output=True, check=False)

    def test_remote_and_app_lifecycle_preserves_user_data(self):
        result = self.shell(
            'ride_artcraft_remote_change configured\n'
            'ride_artcraft_remote_state\n'
            'ride_artcraft_app_change "$ART_ENTRY" installed\n'
            'ride_artcraft_app_state "$ART_ENTRY"\n'
            'ride_artcraft_app_change "$ART_ENTRY" absent\n'
            'ride_artcraft_app_state "$ART_ENTRY"\n'
            'ride_artcraft_remote_change absent\n'
            'ride_artcraft_remote_state'
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(),
                         ["configured", "installed", "absent", "absent"])
        self.assertEqual(self.data.read_text(), "user project\n")
        self.assertFalse((self.root / "data/ride-fedora/owned-remotes/artcraft-oci.json").exists())
        self.assertNotIn("--delete-data", self.calls.read_text())

    def test_app_requires_exact_remote_and_refuses_other_origin(self):
        missing = self.shell('ride_artcraft_app_preflight "$ART_ENTRY" installed')
        self.assertEqual(missing.returncode, 42)
        self.assertIn("official ArtCraft user OCI remote", missing.stderr)
        self.remotes.write_text(json.dumps([{
            "name": "flathub", "url": "https://dl.flathub.org/repo/", "options": ""
        }, {
            "name": "artcraft-oci", "url": "oci+https://other.example", "options": ""
        }]))
        wrong_remote = self.shell('ride_artcraft_app_preflight "$ART_ENTRY" installed')
        self.assertEqual(wrong_remote.returncode, 42)
        self.remotes.write_text(json.dumps([{
            "name": "artcraft-oci", "url": "oci+https://getartcraft.com", "options": "no-gpg-verify"
        }]))
        missing_runtime = self.shell('ride_artcraft_app_preflight "$ART_ENTRY" installed')
        self.assertEqual(missing_runtime.returncode, 42)
        self.assertIn("GPG-verified user Flathub remote", missing_runtime.stderr)
        self.remotes.write_text(json.dumps([{
            "name": "flathub", "url": "https://dl.flathub.org/repo/", "options": ""
        }, {
            "name": "artcraft-oci", "url": "oci+https://getartcraft.com", "options": "no-gpg-verify"
        }]))
        self.apps.write_text(json.dumps([{"application_id": APP_ID, "origin": "other"}]))
        wrong_app = self.shell('ride_artcraft_app_preflight "$ART_ENTRY" absent')
        self.assertEqual(wrong_app.returncode, 42)
        self.assertIn("unexpected Flatpak origin", wrong_app.stderr)

    def test_remote_refuses_removal_while_apps_use_it(self):
        self.assertEqual(self.shell('ride_artcraft_remote_change configured').returncode, 0)
        self.apps.write_text(json.dumps([{"application_id": APP_ID, "origin": "artcraft-oci"}]))
        refused = self.shell('ride_artcraft_remote_change absent')
        self.assertEqual(refused.returncode, 42)
        self.assertIn("while user apps use it", refused.stderr)
        self.assertEqual(self.shell('ride_artcraft_remote_state').stdout.strip(), "configured")

    def test_unowned_remote_and_failed_install_are_not_removed(self):
        self.remotes.write_text(json.dumps([{
            "name": "flathub", "url": "https://dl.flathub.org/repo/", "options": ""
        }, {
            "name": "artcraft-oci", "url": "oci+https://getartcraft.com", "options": "no-gpg-verify"
        }]))
        self.assertEqual(self.shell('ride_artcraft_remote_state').stdout.strip(), "unowned")
        refused = self.shell('ride_artcraft_remote_change absent')
        self.assertEqual(refused.returncode, 42)
        failed = self.shell('ride_artcraft_app_change "$ART_ENTRY" installed', fail_install=True)
        self.assertEqual(failed.returncode, 3)
        self.assertEqual(json.loads(self.apps.read_text()), [])

    def test_catalog_has_only_published_x86_64_refs(self):
        catalog = json.loads(CATALOG.read_text())
        entries = [row for row in catalog["operations"] if row["handler"] == "artcraft-oci-app"]
        self.assertEqual(len(entries), 14)
        for entry in entries:
            self.assertEqual(entry["applicationId"], "ai.storyteller." + entry["id"].removeprefix("package."))
            self.assertEqual(entry["status"], "candidate")
            self.assertEqual(entry["targets"]["fedora"]["releases"], ["44", "45"])
            self.assertEqual(entry["scope"], "user")


if __name__ == "__main__":
    unittest.main()
