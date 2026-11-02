"""Pinned LibreSpeed CLI extraction, ownership, and inverse behavior."""

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
BINARY = b"#!/usr/bin/env bash\nprintf 'librespeed-cli version v1.0.14\\n'\nprintf x >> \"$HOME/version-probes\"\n"
LICENSE = b"LGPL-3.0-only fixture license\n"


class LibreSpeedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.archive = self.root / "release.tar.gz"
        self.manifest = self.root / "checksums.txt"
        with tarfile.open(self.archive, "w:gz") as tar:
            for name, content, mode in (("librespeed-cli", BINARY, 0o755), ("LICENSE", LICENSE, 0o644)):
                info = tarfile.TarInfo(f"librespeed-cli_1.0.14/{name}")
                info.size, info.mode = len(content), mode
                tar.addfile(info, io.BytesIO(content))
        archive_sha = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.manifest.write_text(f"{archive_sha}  librespeed-cli_1.0.14_linux_amd64.tar.gz\n")
        manifest_sha = hashlib.sha256(self.manifest.read_bytes()).hexdigest()
        curl = self.bin / "curl"
        curl.write_text("#!/usr/bin/env bash\n"
                        "while (($#)); do if [[ $1 == -o ]]; then out=$2; shift 2; "
                        "else uri=$1; shift; fi; done\n"
                        "[[ ${LIBRESPEED_CURL_FAIL:-0} == 0 ]] || exit 22\n"
                        "case $uri in */checksums.txt) cp \"$FIXTURE_MANIFEST\" \"$out\" ;; "
                        "*/librespeed-cli_1.0.14_linux_amd64.tar.gz) cp \"$FIXTURE_ARCHIVE\" \"$out\" ;; *) exit 23 ;; esac\n")
        curl.chmod(0o755)
        catalog = json.loads((ROOT / "catalog/operations.json").read_text())
        entry = next(row for row in catalog["operations"] if row["id"] == "package.librespeed-cli")
        entry["sourceSha256"] = archive_sha
        entry["manifestSha256"] = manifest_sha
        self.entry = self.root / "entry.json"
        self.entry.write_text(json.dumps(entry))
        self.environment = self.home / ".local/opt/ride-fedora/librespeed-cli/1.0.14"
        self.link = self.home / ".local/bin/librespeed-cli"
        self.manifest_path = self.home / ".local/share/ride-fedora/owned-tools/package.librespeed-cli.json"
        self.sentinel = self.home / ".local/share/ride-fedora/owned-tools/keep.txt"
        self.sentinel.parent.mkdir(parents=True)
        self.sentinel.write_text("keep user data\n")
        self.env = os.environ | {"HOME": str(self.home), "RIDE_ROOT": str(ROOT),
                                 "PATH": f"{self.bin}:{os.environ['PATH']}",
                                 "FIXTURE_ARCHIVE": str(self.archive),
                                 "FIXTURE_MANIFEST": str(self.manifest)}

    def call(self, function, state=None, env=None):
        entry = f'"$(cat {self.entry})"'
        args = f'{entry} {state}' if state is not None else entry
        command = ('source "$RIDE_ROOT/lib/v3/common.sh"; '
                   'source "$RIDE_ROOT/lib/v3/providers.sh"; '
                   f'ride_{function}_librespeed {args}')
        return subprocess.run(["bash", "-c", command], env=env or self.env,
                              capture_output=True, text=True)

    def test_install_repeat_observe_remove_and_keep_sibling_data(self):
        result = self.call("change", "installed")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.link.readlink(), self.environment / "librespeed-cli")
        self.assertEqual((self.environment / "librespeed-cli").read_bytes(), BINARY)
        self.assertEqual((self.environment / "LICENSE").read_bytes(), LICENSE)
        obs = self.call("observe")
        self.assertEqual(obs.stdout.strip(), "installed")
        result = self.call("change", "installed")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.call("change", "absent").returncode, 0)
        self.assertFalse(self.environment.exists())
        self.assertFalse(self.link.is_symlink())
        self.assertFalse(self.manifest_path.exists())
        self.assertEqual(self.sentinel.read_text(), "keep user data\n")

    def test_download_and_digest_failures_leave_no_install(self):
        failed = self.call("change", "installed", self.env | {"LIBRESPEED_CURL_FAIL": "1"})
        self.assertNotEqual(failed.returncode, 0)
        entry = json.loads(self.entry.read_text())
        entry["sourceSha256"] = "0" * 64
        self.entry.write_text(json.dumps(entry))
        self.assertNotEqual(self.call("change", "installed").returncode, 0)
        entry["sourceSha256"] = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        entry["manifestSha256"] = "0" * 64
        self.entry.write_text(json.dumps(entry))
        self.assertNotEqual(self.call("change", "installed").returncode, 0)
        self.assertFalse(self.environment.exists())
        self.assertEqual(self.sentinel.read_text(), "keep user data\n")

    def test_collision_and_modified_install_are_preserved(self):
        self.link.parent.mkdir(parents=True)
        self.link.write_text("user-owned")
        self.assertNotEqual(self.call("change", "installed").returncode, 0)
        self.assertEqual(self.link.read_text(), "user-owned")
        self.link.unlink()
        result = self.call("change", "installed")
        self.assertEqual(result.returncode, 0, result.stderr)
        (self.environment / "notes").write_text("user data")
        refused = self.call("change", "absent")
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual((self.environment / "notes").read_text(), "user data")
        self.assertTrue(self.link.is_symlink())

    def test_unsafe_archive_member_is_rejected(self):
        with tarfile.open(self.archive, "w:gz") as tar:
            info = tarfile.TarInfo("../librespeed-cli")
            info.size = len(BINARY)
            tar.addfile(info, io.BytesIO(BINARY))
            info = tarfile.TarInfo("LICENSE")
            info.size = len(LICENSE)
            tar.addfile(info, io.BytesIO(LICENSE))
        archive_sha = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        entry = json.loads(self.entry.read_text())
        entry["sourceSha256"] = archive_sha
        self.entry.write_text(json.dumps(entry))
        self.manifest.write_text(f"{archive_sha}  librespeed-cli_1.0.14_linux_amd64.tar.gz\n")
        entry["manifestSha256"] = hashlib.sha256(self.manifest.read_bytes()).hexdigest()
        self.entry.write_text(json.dumps(entry))
        result = self.call("change", "installed")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.environment.exists())


if __name__ == "__main__":
    unittest.main()
