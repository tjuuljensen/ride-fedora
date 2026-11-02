"""Pinned Eza portable binary ownership and inverse behavior."""

import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
BINARY = b"#!/usr/bin/env bash\nprintf 'eza - v0.23.5\\n'\n"


class EzaPortableTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.archive = self.root / "release.tar.gz"
        self.write_archive()
        curl = self.bin / "curl"
        curl.write_text("#!/usr/bin/env bash\n"
                        "while (($#)); do if [[ $1 == -o ]]; then out=$2; shift 2; "
                        "else uri=$1; shift; fi; done\n"
                        "[[ ${EZA_CURL_FAIL:-0} == 0 ]] || exit 22\n"
                        "case $uri in */eza_x86_64-unknown-linux-gnu.tar.gz) "
                        "cp \"$FIXTURE_ARCHIVE\" \"$out\" ;; *) exit 23 ;; esac\n")
        curl.chmod(0o755)
        catalog = json.loads((ROOT / "catalog/operations.json").read_text())
        entry = next(row for row in catalog["operations"] if row["id"] == "package.eza-portable")
        entry["sourceSha256"] = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.entry = self.root / "entry.json"
        self.entry.write_text(json.dumps(entry))
        self.environment = self.home / ".local/opt/ride-fedora/eza/0.23.5"
        self.link = self.home / ".local/bin/eza"
        self.manifest = self.home / ".local/share/ride-fedora/owned-tools/package.eza-portable.json"
        self.keep = self.home / ".local/share/ride-fedora/owned-tools/keep.txt"
        self.keep.parent.mkdir(parents=True)
        self.keep.write_text("preserve sibling data\n")
        self.env = os.environ | {"HOME": str(self.home), "RIDE_ROOT": str(ROOT),
                                 "PATH": f"{self.bin}:{os.environ['PATH']}",
                                 "FIXTURE_ARCHIVE": str(self.archive)}

    def write_archive(self, name="eza"):
        with tarfile.open(self.archive, "w:gz") as tar:
            info = tarfile.TarInfo(f"eza_x86_64-unknown-linux-gnu/{name}")
            info.size, info.mode = len(BINARY), 0o755
            tar.addfile(info, io.BytesIO(BINARY))

    def call(self, function, state=None, env=None):
        entry = f'"$(cat {self.entry})"'
        args = f'{entry} {state}' if state is not None else entry
        command = ('source "$RIDE_ROOT/lib/v3/common.sh"; '
                   'source "$RIDE_ROOT/lib/v3/providers.sh"; '
                   f'ride_{function}_eza_portable {args}')
        return subprocess.run(["bash", "-c", command], env=env or self.env,
                              capture_output=True, text=True)

    def test_install_repeat_observe_remove_and_preserve_sibling_data(self):
        result = self.call("change", "installed")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.link.readlink(), self.environment / "eza")
        self.assertEqual((self.environment / "eza").read_bytes(), BINARY)
        self.assertEqual(self.call("observe").stdout.strip(), "installed")
        self.assertEqual(self.call("change", "installed").returncode, 0)
        self.assertEqual(self.call("change", "absent").returncode, 0)
        self.assertFalse(self.environment.exists())
        self.assertFalse(self.link.is_symlink())
        self.assertFalse(self.manifest.exists())
        self.assertEqual(self.keep.read_text(), "preserve sibling data\n")

    def test_download_and_digest_failures_leave_no_install(self):
        failed = self.call("change", "installed", self.env | {"EZA_CURL_FAIL": "1"})
        self.assertNotEqual(failed.returncode, 0)
        entry = json.loads(self.entry.read_text())
        entry["sourceSha256"] = "0" * 64
        self.entry.write_text(json.dumps(entry))
        self.assertNotEqual(self.call("change", "installed").returncode, 0)
        self.assertFalse(self.environment.exists())
        self.assertEqual(self.keep.read_text(), "preserve sibling data\n")

    def test_collision_and_modified_install_are_preserved(self):
        self.link.parent.mkdir(parents=True)
        self.link.write_text("user-owned")
        self.assertNotEqual(self.call("change", "installed").returncode, 0)
        self.assertEqual(self.link.read_text(), "user-owned")
        self.link.unlink()
        self.assertEqual(self.call("change", "installed").returncode, 0)
        (self.environment / "notes").write_text("user data")
        refused = self.call("change", "absent")
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual((self.environment / "notes").read_text(), "user data")

    def test_archive_without_expected_binary_is_rejected(self):
        self.write_archive("unexpected")
        entry = json.loads(self.entry.read_text())
        entry["sourceSha256"] = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.entry.write_text(json.dumps(entry))
        result = self.call("change", "installed")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.environment.exists())

    def test_path_traversal_archive_member_is_rejected(self):
        with tarfile.open(self.archive, "w:gz") as tar:
            info = tarfile.TarInfo("../eza")
            info.size, info.mode = len(BINARY), 0o755
            tar.addfile(info, io.BytesIO(BINARY))
        entry = json.loads(self.entry.read_text())
        entry["sourceSha256"] = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.entry.write_text(json.dumps(entry))
        result = self.call("change", "installed")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.environment.exists())
        self.assertFalse((self.home / ".local/bin/eza").exists())


if __name__ == "__main__":
    unittest.main()
