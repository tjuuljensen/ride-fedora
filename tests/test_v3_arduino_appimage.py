"""Pinned Arduino AppImage ownership and removal preserve user state."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
APPIMAGE = b"\x7fELF Arduino fixture\n"


class ArduinoAppimageTests(unittest.TestCase):
    OPERATION_ID = "package.arduino-ide"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        (self.root / "fixture-appimage").write_bytes(APPIMAGE)
        curl = self.bin / "curl"
        curl.write_text("#!/usr/bin/env bash\n"
                        "while (($#)); do if [[ $1 == -o ]]; then output=$2; shift 2; "
                        "else uri=$1; shift; fi; done\n"
                        "[[ ${ARDUINO_CURL_FAIL:-0} == 0 ]] || exit 22\n"
                        "[[ $uri == https://github.com/*/releases/download/*/* ]] || exit 23\n"
                        "cp \"$ARDUINO_FIXTURE_APPIMAGE\" \"$output\"\n")
        curl.chmod(0o755)
        entry = next(row for row in json.loads((ROOT / "catalog/operations.json").read_text())["operations"]
                     if row["id"] == self.OPERATION_ID)
        entry["sourceSha256"] = hashlib.sha256(APPIMAGE).hexdigest()
        self.entry = self.root / "entry.json"
        self.entry.write_text(json.dumps(entry))
        self.app = self.home / "Applications" / entry["assetName"]
        self.manifest = self.home / ".local/share/ride-fedora/owned-tools" / f"{self.OPERATION_ID}.json"
        self.sketch = self.home / "Documents/Arduino/valuable-sketch.ino"
        self.sketch.parent.mkdir(parents=True)
        self.sketch.write_text("user sketch")
        self.env = os.environ | {
            "HOME": str(self.home), "RIDE_ROOT": str(ROOT),
            "PATH": f"{self.bin}:{os.environ['PATH']}",
            "ARDUINO_FIXTURE_APPIMAGE": str(self.root / "fixture-appimage"),
        }

    def call(self, function, state=None, env=None):
        args = f' "{state}"' if state else ""
        command = ('source "$RIDE_ROOT/lib/v3/common.sh"; '
                   'source "$RIDE_ROOT/lib/v3/providers.sh"; '
                   f'{function} "$(cat {self.entry})"{args}')
        return subprocess.run(["bash", "-c", command], env=env or self.env,
                              capture_output=True, text=True)

    def test_install_repeat_observe_and_remove_only_owned_files(self):
        self.assertEqual(self.call("ride_change_publisher_appimage", "installed").returncode, 0)
        self.assertEqual(self.call("ride_change_publisher_appimage", "installed").returncode, 0)
        self.assertEqual(self.call("ride_observe_publisher_appimage").stdout.strip(), "installed")
        self.assertEqual(self.app.read_bytes(), APPIMAGE)
        self.assertEqual(json.loads(self.manifest.read_text())["destination"], str(self.app))
        self.assertEqual(self.call("ride_change_publisher_appimage", "absent").returncode, 0)
        self.assertFalse(self.app.exists())
        self.assertFalse(self.manifest.exists())
        self.assertEqual(self.sketch.read_text(), "user sketch")

    def test_download_failure_digest_mismatch_and_collision_are_safe(self):
        failure = self.call("ride_change_publisher_appimage", "installed",
                            env=self.env | {"ARDUINO_CURL_FAIL": "1"})
        self.assertNotEqual(failure.returncode, 0)
        self.assertFalse(self.app.exists())
        entry = json.loads(self.entry.read_text())
        entry["sourceSha256"] = "0" * 64
        self.entry.write_text(json.dumps(entry))
        mismatch = self.call("ride_change_publisher_appimage", "installed")
        self.assertNotEqual(mismatch.returncode, 0)
        self.assertFalse(self.app.exists())
        self.assertEqual(self.sketch.read_text(), "user sketch")

        entry["sourceSha256"] = hashlib.sha256(APPIMAGE).hexdigest()
        self.entry.write_text(json.dumps(entry))
        self.app.parent.mkdir(parents=True)
        self.app.write_text("unowned existing file")
        refused = self.call("ride_change_publisher_appimage", "installed")
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual(self.app.read_text(), "unowned existing file")
        self.assertEqual(self.sketch.read_text(), "user sketch")


class JoplinAppimageTests(ArduinoAppimageTests):
    OPERATION_ID = "package.joplin"
