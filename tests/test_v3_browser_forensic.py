"""Pinned browser-forensic source build ownership and failure cleanup."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent


class BrowserForensicTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "Cargo.toml").write_text("[workspace]\n")
        archive = self.root / "source.tar.gz"
        with tarfile.open(archive, "w:gz") as bundle:
            bundle.add(self.source / "Cargo.toml", arcname="browser-forensic-pin/Cargo.toml")
        self.archive = archive
        self.binary = self.root / "br4n6-fixture"
        self.binary.write_text("#!/usr/bin/env bash\n[[ $1 == --version ]] && { echo 'br4n6 0.3.0'; exit 0; }\nexit 0\n")
        self.binary.chmod(0o755)

        curl = self.bin / "curl"
        curl.write_text("#!/usr/bin/env bash\n"
                        "while (($#)); do\n"
                        "  if [[ $1 == -o ]]; then output=$2; shift 2; else shift; fi\n"
                        "done\n"
                        "[[ ${BROWSER_FORENSIC_CURL_FAIL:-0} == 0 ]] || exit 22\n"
                        "cp \"$BROWSER_FORENSIC_ARCHIVE\" \"$output\"\n")
        curl.chmod(0o755)

        cargo = self.bin / "cargo"
        cargo.write_text("#!/usr/bin/env bash\n"
                         "[[ ${BROWSER_FORENSIC_BUILD_FAIL:-0} == 0 ]] || exit 23\n"
                         "[[ \" $* \" == *' --package browser-forensic-cli '* ]] || exit 24\n"
                         "mkdir -p \"$CARGO_TARGET_DIR/release\"\n"
                         "cp \"$BROWSER_FORENSIC_BINARY\" \"$CARGO_TARGET_DIR/release/br4n6\"\n"
                         "chmod +x \"$CARGO_TARGET_DIR/release/br4n6\"\n")
        cargo.chmod(0o755)
        rustc = self.bin / "rustc"
        rustc.write_text("#!/usr/bin/env bash\necho 'rustc 1.99.1'\n")
        rustc.chmod(0o755)

        entry = next(row for row in json.loads((ROOT / "catalog/operations.json").read_text())["operations"]
                     if row["id"] == "package.browser-forensic")
        entry["sourceSha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
        self.entry = self.root / "entry.json"
        self.entry.write_text(json.dumps(entry))
        self.environment = self.home / ".local/share/ride-fedora/tools/browser-forensic"
        self.link = self.home / ".local/bin/br4n6"
        self.sibling = self.environment.parent / "keep.txt"
        self.sibling.parent.mkdir(parents=True)
        self.sibling.write_text("keep")
        self.env = os.environ | {
            "HOME": str(self.home),
            "RIDE_ROOT": str(ROOT),
            "PATH": f"{self.bin}:{os.environ['PATH']}",
            "BROWSER_FORENSIC_ARCHIVE": str(archive),
            "BROWSER_FORENSIC_BINARY": str(self.binary),
        }

    def change(self, state, env=None):
        command = ('source "$RIDE_ROOT/lib/v3/common.sh"; '
                   'source "$RIDE_ROOT/lib/v3/providers.sh"; '
                   f'ride_change_browser_forensic "$(cat {self.entry})" {state}')
        return subprocess.run(["bash", "-c", command], env=env or self.env,
                              capture_output=True, text=True)

    def test_install_observe_remove_preserves_sibling(self):
        installed = self.change("installed")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertTrue(self.link.is_symlink())
        self.assertEqual(self.link.resolve(), self.environment / "br4n6")
        observe = subprocess.run(
            ["bash", "-c", 'source "$RIDE_ROOT/lib/v3/common.sh"; '
             'source "$RIDE_ROOT/lib/v3/providers.sh"; '
             f'ride_observe_browser_forensic "$(cat {self.entry})"'],
            env=self.env, capture_output=True, text=True)
        self.assertEqual(observe.returncode, 0, observe.stderr)
        self.assertEqual(observe.stdout.strip(), "installed")
        self.assertEqual(self.change("absent").returncode, 0)
        self.assertFalse(self.environment.exists())
        self.assertFalse(self.link.is_symlink())
        self.assertEqual(self.sibling.read_text(), "keep")

    def test_failed_download_digest_and_build_clean_owned_destination(self):
        failed_download = self.change("installed", self.env | {"BROWSER_FORENSIC_CURL_FAIL": "1"})
        self.assertNotEqual(failed_download.returncode, 0)
        self.assertFalse(self.environment.exists())
        entry = json.loads(self.entry.read_text())
        entry["sourceSha256"] = "0" * 64
        self.entry.write_text(json.dumps(entry))
        wrong_digest = self.change("installed")
        self.assertNotEqual(wrong_digest.returncode, 0)
        self.assertFalse(self.environment.exists())
        entry["sourceSha256"] = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.entry.write_text(json.dumps(entry))
        failed_build = self.change("installed", self.env | {"BROWSER_FORENSIC_BUILD_FAIL": "1"})
        self.assertNotEqual(failed_build.returncode, 0)
        self.assertFalse(self.environment.exists())
        self.assertFalse(self.link.exists())
        self.assertEqual(self.sibling.read_text(), "keep")

    def test_unowned_and_modified_destinations_are_refused(self):
        self.environment.mkdir()
        (self.environment / "user-data").write_text("keep")
        refused = self.change("absent")
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual((self.environment / "user-data").read_text(), "keep")
        (self.environment / "user-data").unlink()
        self.environment.rmdir()
        self.assertEqual(self.change("installed").returncode, 0)
        (self.environment / "notes").write_text("user data")
        refused = self.change("absent")
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual((self.environment / "notes").read_text(), "user data")
        self.assertTrue(self.link.is_symlink())


if __name__ == "__main__":
    unittest.main()
