"""CyberChef's ZIP extraction and inverse refuse unowned or modified data."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "lib/v3/cyberchef_archive.py"
LICENSE = b"Apache-2.0 fixture\n"


class CyberchefTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.binary = self.root / "bin"
        self.binary.mkdir()
        self.archive = self.root / "release.zip"
        self.make_archive()
        self.license = self.root / "LICENSE"
        self.license.write_bytes(LICENSE)
        curl = self.binary / "curl"
        curl.write_text("#!/usr/bin/env bash\n"
                        "while (($#)); do\n"
                        "  if [[ $1 == -o ]]; then output=$2; shift 2; else uri=$1; shift; fi\n"
                        "done\n"
                        "[[ ${CYBERCHEF_CURL_FAIL:-0} == 0 ]] || exit 22\n"
                        "case $uri in */LICENSE) cp \"$CYBERCHEF_FIXTURE_LICENSE\" \"$output\" ;;\n"
                        "  *.zip) cp \"$CYBERCHEF_FIXTURE_ARCHIVE\" \"$output\" ;;\n"
                        "  *) exit 23 ;; esac\n")
        curl.chmod(0o755)
        firefox = self.binary / "firefox"
        firefox.write_text("#!/bin/sh\nexit 0\n")
        firefox.chmod(0o755)
        self.environment = self.root / "opt/ride-fedora/cyberchef"
        self.link = self.root / "applications/ride-cyberchef.desktop"
        self.link.parent.mkdir(parents=True)
        sibling = self.environment.parent / "keep.txt"
        sibling.parent.mkdir(parents=True)
        sibling.write_text("keep")
        self.sibling = sibling
        row = next(x for x in json.loads((ROOT / "catalog/operations.json").read_text())["operations"]
                   if x["id"] == "package.cyberchef")
        row["sourceSha256"] = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        row["licenseSha256"] = hashlib.sha256(LICENSE).hexdigest()
        self.entry = self.root / "entry.json"
        self.entry.write_text(json.dumps(row))
        self.env = os.environ | {
            "RIDE_ROOT": str(ROOT), "PATH": f"{self.binary}:{os.environ['PATH']}",
            "CYBERCHEF_FIXTURE_ARCHIVE": str(self.archive),
            "CYBERCHEF_FIXTURE_LICENSE": str(self.license),
        }

    def make_archive(self, unsafe=False):
        with zipfile.ZipFile(self.archive, "w", zipfile.ZIP_DEFLATED) as bundle:
            for name in ("CyberChef_v11.5.0.html", "images/cyberchef-128x128.png",
                         "assets/main.js", "assets/main.css"):
                bundle.writestr(name, b"fixture")
            for index in range(30):
                bundle.writestr(f"modules/module{index}.LICENSE.txt", b"notice")
            if unsafe:
                bundle.writestr("../escape", b"bad")

    def run_change(self, state, env=None):
        script = ('source "$RIDE_ROOT/lib/v3/common.sh"; '
                  'source "$RIDE_ROOT/lib/v3/providers.sh"; '
                  f'ride_cyberchef_environment() {{ printf "%s\\n" "{self.environment}"; }}; '
                  f'ride_cyberchef_link() {{ printf "%s\\n" "{self.link}"; }}; '
                  f'ride_change_cyberchef "$(cat {self.entry})" {state}')
        return subprocess.run(["bash", "-c", script], env=env or self.env,
                              text=True, capture_output=True)

    def test_install_observe_and_exact_remove(self):
        installed = self.run_change("installed")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual(self.link.readlink(), self.environment / "payload/ride-cyberchef.desktop")
        self.assertEqual((self.environment / "payload/LICENSE").read_bytes(), LICENSE)
        script = ('source "$RIDE_ROOT/lib/v3/common.sh"; '
                  'source "$RIDE_ROOT/lib/v3/providers.sh"; '
                  f'ride_cyberchef_environment() {{ printf "%s\\n" "{self.environment}"; }}; '
                  f'ride_cyberchef_link() {{ printf "%s\\n" "{self.link}"; }}; '
                  f'ride_observe_cyberchef "$(cat {self.entry})"')
        observed = subprocess.run(["bash", "-c", script], env=self.env,
                                  text=True, capture_output=True)
        self.assertEqual(observed.stdout.strip(), "installed")
        removed = self.run_change("absent")
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertFalse(self.environment.exists())
        self.assertFalse(self.link.is_symlink())
        self.assertEqual(self.sibling.read_text(), "keep")

    def test_bad_digest_failed_download_and_existing_path(self):
        failed = self.run_change("installed", self.env | {"CYBERCHEF_CURL_FAIL": "1"})
        self.assertNotEqual(failed.returncode, 0)
        self.assertFalse(self.environment.exists())
        row = json.loads(self.entry.read_text())
        row["sourceSha256"] = "0" * 64
        self.entry.write_text(json.dumps(row))
        bad_hash = self.run_change("installed")
        self.assertNotEqual(bad_hash.returncode, 0)
        self.assertFalse(self.environment.exists())
        self.link.write_text("user entry")
        occupied = self.run_change("installed")
        self.assertNotEqual(occupied.returncode, 0)
        self.assertEqual(self.link.read_text(), "user entry")
        self.assertEqual(self.sibling.read_text(), "keep")

    def test_unsafe_archive_and_modified_payload_are_refused(self):
        self.make_archive(unsafe=True)
        row = json.loads(self.entry.read_text())
        row["sourceSha256"] = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.entry.write_text(json.dumps(row))
        unsafe = self.run_change("installed")
        self.assertNotEqual(unsafe.returncode, 0)
        self.assertFalse(self.environment.exists())
        self.assertFalse((self.root / "escape").exists())
        self.make_archive()
        row["sourceSha256"] = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.entry.write_text(json.dumps(row))
        self.assertEqual(self.run_change("installed").returncode, 0)
        (self.environment / "payload/user-data").write_text("keep")
        refused = self.run_change("absent")
        self.assertNotEqual(refused.returncode, 0)
        self.assertTrue(self.link.is_symlink())
        self.assertEqual((self.environment / "payload/user-data").read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
