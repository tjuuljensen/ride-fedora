"""Chepy's isolated user installation rejects bad sources and unowned paths."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
SOURCE = b"pinned chepy fixture"


class ChepyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.binary = self.root / "bin"
        self.binary.mkdir()
        fixture = self.root / "chepy-7.6.0.tar.gz"
        fixture.write_bytes(SOURCE)
        curl = self.binary / "curl"
        curl.write_text("#!/usr/bin/env bash\n"
                        "while (($#)); do\n"
                        "  if [[ $1 == -o ]]; then output=$2; shift 2; else shift; fi\n"
                        "done\n"
                        "[[ ${CHEPY_CURL_FAIL:-0} == 0 ]] || exit 22\n"
                        "cp \"$CHEPY_FIXTURE\" \"$output\"\n")
        curl.chmod(0o755)
        python = self.binary / "python3.12"
        python.write_text("#!/usr/bin/env bash\n"
                          "[[ $1 == -m && $2 == venv ]] || exit 24\n"
                          "mkdir -p \"$3/bin\"\n"
                          "cat > \"$3/bin/python\" <<'STUB'\n"
                          "#!/usr/bin/env bash\n"
                          "[[ ${CHEPY_PIP_FAIL:-0} == 0 ]] || exit 23\n"
                          "if [[ $1 == -m && $2 == pip && $4 == freeze ]]; then printf 'chepy==7.6.0\\n'; fi\n"
                          "exit 0\n"
                          "STUB\n"
                          "printf '#!/bin/sh\\nexit 0\\n' > \"$3/bin/chepy\"\n"
                          "chmod +x \"$3/bin/python\" \"$3/bin/chepy\"\n")
        python.chmod(0o755)
        entry = next(x for x in json.loads((ROOT / "catalog/operations.json").read_text())["operations"]
                     if x["id"] == "package.chepy")
        entry["sourceSha256"] = hashlib.sha256(SOURCE).hexdigest()
        self.entry = self.root / "entry.json"
        self.entry.write_text(json.dumps(entry))
        self.environment = self.home / ".local/share/ride-fedora/tools/chepy"
        self.link = self.home / ".local/bin/chepy"
        self.sibling = self.environment.parent / "keep.txt"
        self.sibling.parent.mkdir(parents=True)
        self.sibling.write_text("keep")
        self.env = os.environ | {
            "HOME": str(self.home), "RIDE_ROOT": str(ROOT),
            "PATH": f"{self.binary}:{os.environ['PATH']}",
            "CHEPY_FIXTURE": str(fixture),
        }

    def change(self, state, env=None):
        script = ('source "$RIDE_ROOT/lib/v3/common.sh"; '
                  'source "$RIDE_ROOT/lib/v3/providers.sh"; '
                  f'ride_change_chepy "$(cat {self.entry})" {state}')
        return subprocess.run(["bash", "-c", script], env=env or self.env,
                              text=True, capture_output=True)

    def test_install_observe_and_remove_preserve_sibling(self):
        installed = self.change("installed")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual(self.link.readlink(), self.environment / "venv/bin/chepy")
        observed = subprocess.run(["bash", "-c", 'source "$RIDE_ROOT/lib/v3/common.sh"; '
                                   'source "$RIDE_ROOT/lib/v3/providers.sh"; '
                                   f'ride_observe_chepy "$(cat {self.entry})"'],
                                  env=self.env, capture_output=True, text=True)
        self.assertEqual(observed.stdout.strip(), "installed")
        removed = self.change("absent")
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertFalse(self.environment.exists())
        self.assertFalse(self.link.is_symlink())
        self.assertEqual(self.sibling.read_text(), "keep")

    def test_failed_download_bad_digest_and_occupied_link(self):
        failed = self.change("installed", self.env | {"CHEPY_CURL_FAIL": "1"})
        self.assertNotEqual(failed.returncode, 0)
        self.assertFalse(self.environment.exists())
        entry = json.loads(self.entry.read_text())
        entry["sourceSha256"] = "0" * 64
        self.entry.write_text(json.dumps(entry))
        bad_hash = self.change("installed")
        self.assertNotEqual(bad_hash.returncode, 0)
        self.assertFalse(self.environment.exists())
        self.link.parent.mkdir(parents=True, exist_ok=True)
        self.link.write_text("user command")
        occupied = self.change("installed")
        self.assertNotEqual(occupied.returncode, 0)
        self.assertEqual(self.link.read_text(), "user command")
        self.assertEqual(self.sibling.read_text(), "keep")

    def test_unowned_remove_refused(self):
        self.environment.mkdir()
        (self.environment / "user-data").write_text("keep")
        refused = self.change("absent")
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual((self.environment / "user-data").read_text(), "keep")

    def test_failed_venv_install_cleans_new_destination(self):
        failed = self.change("installed", self.env | {"CHEPY_PIP_FAIL": "1"})
        self.assertNotEqual(failed.returncode, 0)
        self.assertFalse(self.environment.exists())
        self.assertFalse(self.link.exists())
        self.assertEqual(self.sibling.read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
