"""Pinned Bitwarden AppImage ownership and vault-data preservation."""

import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
APPIMAGE = b"\x7fELFBitwarden AppImage fixture\n"


class BitwardenAppImageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.appimage = self.root / "Bitwarden.AppImage"
        self.appimage.write_bytes(APPIMAGE)
        self.sha512 = base64.b64encode(hashlib.sha512(APPIMAGE).digest()).decode()
        manifest_bytes = (
            "version: 2026.10.1\n"
            "files:\n"
            "  - url: Bitwarden-2026.10.1-x86_64.AppImage\n"
            f"    sha512: {self.sha512}\n"
            "path: Bitwarden-2026.10.1-x86_64.AppImage\n"
            f"sha512: {self.sha512}\n"
        ).encode()
        self.manifest_source = self.root / "latest-linux.yml"
        self.manifest_source.write_bytes(manifest_bytes)
        self.manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
        curl = self.bin / "curl"
        curl.write_text(
            "#!/usr/bin/env bash\n"
            "while (($#)); do if [[ $1 == -o ]]; then out=$2; shift 2; "
            "elif [[ $1 == http* ]]; then uri=$1; shift; else shift; fi; done\n"
            "[[ ${BW_CURL_FAIL:-0} == 0 ]] || exit 22\n"
            "case $uri in */latest-linux.yml) cp \"$BW_MANIFEST\" \"$out\" ;; "
            "*/Bitwarden-2026.10.1-x86_64.AppImage) cp \"$BW_APPIMAGE\" \"$out\" ;; *) exit 23 ;; esac\n"
        )
        curl.chmod(0o755)
        catalog = json.loads((ROOT / "catalog/operations.json").read_text())
        entry = next(row for row in catalog["operations"] if row["id"] == "package.bitwarden-appimage")
        entry["sourceSha512"] = self.sha512
        entry["manifestSha256"] = self.manifest_sha
        self.entry = self.root / "entry.json"
        self.entry.write_text(json.dumps(entry))
        self.path = self.home / "Applications/Bitwarden-2026.10.1-x86_64.AppImage"
        self.state = self.home / ".local/share/ride-fedora/owned-tools/package.bitwarden-appimage.json"
        self.vault = self.home / ".config/Bitwarden/data.json"
        self.vault.parent.mkdir(parents=True)
        self.vault.write_text('{"encryptedFixture":"keep"}\n')
        self.vault_hash = hashlib.sha256(self.vault.read_bytes()).hexdigest()
        self.env = os.environ | {
            "HOME": str(self.home), "RIDE_ROOT": str(ROOT),
            "PATH": f"{self.bin}:{os.environ['PATH']}",
            "BW_APPIMAGE": str(self.appimage), "BW_MANIFEST": str(self.manifest_source),
        }

    def call(self, function, state=None, env=None):
        entry = f'"$(cat {self.entry})"'
        args = f"{entry} {state}" if state is not None else entry
        command = ('source "$RIDE_ROOT/lib/v3/common.sh"; '
                   'source "$RIDE_ROOT/lib/v3/providers.sh"; '
                   f"ride_{function}_bitwarden_appimage {args}")
        return subprocess.run(["bash", "-c", command], env=env or self.env,
                              capture_output=True, text=True)

    def test_install_repeat_observe_remove_preserves_vault(self):
        self.assertEqual(self.call("change", "installed").returncode, 0)
        self.assertTrue(self.path.is_file() and os.access(self.path, os.X_OK))
        self.assertEqual(self.call("observe").stdout.strip(), "installed")
        self.assertEqual(self.call("change", "installed").returncode, 0)
        self.assertEqual(self.call("change", "absent").returncode, 0)
        self.assertFalse(self.path.exists())
        self.assertFalse(self.state.exists())
        self.assertEqual(hashlib.sha256(self.vault.read_bytes()).hexdigest(), self.vault_hash)

    def test_download_and_manifest_failures_leave_no_install(self):
        failed = self.call("change", "installed", self.env | {"BW_CURL_FAIL": "1"})
        self.assertNotEqual(failed.returncode, 0)
        entry = json.loads(self.entry.read_text())
        entry["manifestSha256"] = "0" * 64
        self.entry.write_text(json.dumps(entry))
        self.assertNotEqual(self.call("change", "installed").returncode, 0)
        self.assertFalse(self.path.exists())

    def test_destination_collision_and_modified_file_are_preserved(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("user file\n")
        self.assertNotEqual(self.call("change", "installed").returncode, 0)
        self.assertEqual(self.path.read_text(), "user file\n")
        self.path.unlink()
        self.assertEqual(self.call("change", "installed").returncode, 0)
        self.path.write_bytes(b"modified")
        self.assertNotEqual(self.call("change", "absent").returncode, 0)
        self.assertEqual(self.path.read_bytes(), b"modified")


if __name__ == "__main__":
    unittest.main()
