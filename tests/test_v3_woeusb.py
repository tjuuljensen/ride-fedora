"""Pinned WoeUSB deployment stays private and removes only its exact files."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = b"#!/usr/bin/env bash\nprintf 'WoeUSB fixture\\n'\n"
LICENSE = b"GPL fixture\n"


class WoeUsbTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        (self.root / "fixture-script").write_bytes(SCRIPT)
        (self.root / "fixture-license").write_bytes(LICENSE)
        curl = self.bin / "curl"
        curl.write_text("#!/usr/bin/env bash\n"
                        "while (($#)); do if [[ $1 == -o ]]; then output=$2; shift 2; "
                        "else uri=$1; shift; fi; done\n"
                        "[[ ${WOEUSB_CURL_FAIL:-0} == 0 ]] || exit 22\n"
                        "case $uri in */woeusb-5.2.4.bash) cp \"$WOEUSB_FIXTURE_SCRIPT\" \"$output\" ;;\n"
                        "*/GPL-3.0-or-later.txt) cp \"$WOEUSB_FIXTURE_LICENSE\" \"$output\" ;; *) exit 23 ;; esac\n")
        curl.chmod(0o755)
        entry = next(row for row in json.loads((ROOT / "catalog/operations.json").read_text())["operations"]
                     if row["id"] == "package.woeusb")
        entry["sourceSha256"] = hashlib.sha256(SCRIPT).hexdigest()
        entry["licenseSha256"] = hashlib.sha256(LICENSE).hexdigest()
        self.entry = self.root / "entry.json"
        self.entry.write_text(json.dumps(entry))
        self.environment = self.home / ".local/opt/ride-fedora/woeusb/5.2.4"
        self.link = self.home / ".local/bin/woeusb"
        self.sibling = self.home / ".local/opt/ride-fedora/woeusb/keep.txt"
        self.sibling.parent.mkdir(parents=True)
        self.sibling.write_text("preserve")
        self.env = os.environ | {
            "HOME": str(self.home), "RIDE_ROOT": str(ROOT),
            "PATH": f"{self.bin}:{os.environ['PATH']}",
            "WOEUSB_FIXTURE_SCRIPT": str(self.root / "fixture-script"),
            "WOEUSB_FIXTURE_LICENSE": str(self.root / "fixture-license"),
        }

    def call(self, function, *args, env=None):
        command = ('source "$RIDE_ROOT/lib/v3/common.sh"; '
                   'source "$RIDE_ROOT/lib/v3/providers.sh"; '
                   f'{function} "$(cat {self.entry})"' + (f' {args[0]}' if args else ''))
        return subprocess.run(["bash", "-c", command], env=env or self.env,
                              capture_output=True, text=True)

    def test_install_observe_and_remove_preserve_sibling(self):
        installed = self.call("ride_change_woeusb", "installed")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual(self.link.readlink(), self.environment / "woeusb-5.2.4.bash")
        self.assertEqual((self.environment / "woeusb-5.2.4.bash").read_bytes(), SCRIPT)
        self.assertEqual(self.call("ride_observe_woeusb").stdout.strip(), "installed")
        self.assertEqual(self.call("ride_change_woeusb", "absent").returncode, 0)
        self.assertFalse(self.environment.exists())
        self.assertFalse(self.link.is_symlink())
        self.assertEqual(self.sibling.read_text(), "preserve")

    def test_bad_download_or_modified_ownership_refuses_change(self):
        failed = self.call("ride_change_woeusb", "installed",
                           env=self.env | {"WOEUSB_CURL_FAIL": "1"})
        self.assertNotEqual(failed.returncode, 0)
        self.assertFalse(self.environment.exists())
        entry = json.loads(self.entry.read_text())
        entry["sourceSha256"] = "0" * 64
        self.entry.write_text(json.dumps(entry))
        bad_hash = self.call("ride_change_woeusb", "installed")
        self.assertNotEqual(bad_hash.returncode, 0)
        self.assertFalse(self.environment.exists())
        self.assertEqual(self.sibling.read_text(), "preserve")

        entry = next(
            row for row in json.loads((ROOT / "catalog/operations.json").read_text())["operations"]
            if row["id"] == "package.woeusb")
        entry["sourceSha256"] = hashlib.sha256(SCRIPT).hexdigest()
        entry["licenseSha256"] = hashlib.sha256(LICENSE).hexdigest()
        self.entry.write_text(json.dumps(entry))
        self.assertEqual(self.call("ride_change_woeusb", "installed").returncode, 0)
        (self.environment / "notes").write_text("user data")
        refused = self.call("ride_change_woeusb", "absent")
        self.assertNotEqual(refused.returncode, 0)
        self.assertTrue((self.environment / "notes").exists())
