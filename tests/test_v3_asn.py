"""Pinned ASN acquisition and ownership preserve adjacent user state."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = b"#!/usr/bin/env bash\nprintf 'ASN fixture\\n'\n"
LICENSE = b"MIT fixture\n"


class AsnTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.binary = self.root / "bin"
        self.binary.mkdir()
        (self.root / "fixture-asn").write_bytes(SCRIPT)
        (self.root / "fixture-license").write_bytes(LICENSE)
        curl = self.binary / "curl"
        curl.write_text("#!/usr/bin/env bash\n"
                        "while (($#)); do\n"
                        "  if [[ $1 == -o ]]; then output=$2; shift 2; else uri=$1; shift; fi\n"
                        "done\n"
                        "[[ ${ASN_CURL_FAIL:-0} == 0 ]] || exit 22\n"
                        "case $uri in */LICENSE) cp \"$ASN_FIXTURE_LICENSE\" \"$output\" ;;\n"
                        "  */asn) cp \"$ASN_FIXTURE_SCRIPT\" \"$output\" ;;\n"
                        "  *) exit 23 ;; esac\n")
        curl.chmod(0o755)
        entry = next(row for row in json.loads((ROOT / "catalog/operations.json").read_text())["operations"]
                     if row["id"] == "package.asn")
        entry["sourceSha256"] = hashlib.sha256(SCRIPT).hexdigest()
        entry["licenseSha256"] = hashlib.sha256(LICENSE).hexdigest()
        self.entry = self.root / "entry.json"
        self.entry.write_text(json.dumps(entry))
        self.environment = self.home / ".local/share/ride-fedora/tools/asn"
        self.link = self.home / ".local/bin/asn"
        self.sibling = self.environment.parent / "keep.txt"
        self.sibling.parent.mkdir(parents=True)
        self.sibling.write_text("keep")
        self.env = os.environ | {
            "HOME": str(self.home), "RIDE_ROOT": str(ROOT),
            "PATH": f"{self.binary}:{os.environ['PATH']}",
            "ASN_FIXTURE_SCRIPT": str(self.root / "fixture-asn"),
            "ASN_FIXTURE_LICENSE": str(self.root / "fixture-license"),
        }

    def change(self, state, env=None):
        command = ('source "$RIDE_ROOT/lib/v3/common.sh"; '
                   'source "$RIDE_ROOT/lib/v3/providers.sh"; '
                   f'ride_change_asn "$(cat {self.entry})" {state}')
        return subprocess.run(["bash", "-c", command], env=env or self.env,
                              capture_output=True, text=True)

    def test_install_observe_and_remove_preserve_sibling(self):
        installed = self.change("installed")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual(self.link.readlink(), self.environment / "asn")
        self.assertEqual((self.environment / "asn").read_bytes(), SCRIPT)
        self.assertEqual((self.environment / "LICENSE").read_bytes(), LICENSE)
        observed = subprocess.run(["bash", "-c", 'source "$RIDE_ROOT/lib/v3/common.sh"; '
                                   'source "$RIDE_ROOT/lib/v3/providers.sh"; '
                                   f'ride_observe_asn "$(cat {self.entry})"'],
                                  env=self.env, capture_output=True, text=True)
        self.assertEqual(observed.stdout.strip(), "installed")
        removed = self.change("absent")
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertFalse(self.environment.exists())
        self.assertFalse(self.link.is_symlink())
        self.assertEqual(self.sibling.read_text(), "keep")

    def test_failed_download_and_bad_digest_leave_no_install(self):
        failed = self.change("installed", self.env | {"ASN_CURL_FAIL": "1"})
        self.assertNotEqual(failed.returncode, 0)
        self.assertFalse(self.environment.exists())
        entry = json.loads(self.entry.read_text())
        entry["sourceSha256"] = "0" * 64
        self.entry.write_text(json.dumps(entry))
        bad_hash = self.change("installed")
        self.assertNotEqual(bad_hash.returncode, 0)
        self.assertFalse(self.environment.exists())
        self.assertEqual(self.sibling.read_text(), "keep")

    def test_existing_and_modified_destinations_are_preserved(self):
        self.link.parent.mkdir(parents=True)
        self.link.write_text("user-owned")
        refused = self.change("installed")
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual(self.link.read_text(), "user-owned")
        self.link.unlink()
        self.assertEqual(self.change("installed").returncode, 0)
        (self.environment / "notes").write_text("user data")
        refused = self.change("absent")
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual((self.environment / "notes").read_text(), "user data")
        self.assertTrue(self.link.is_symlink())


if __name__ == "__main__":
    unittest.main()
