"""NetworkMiner's pinned user-local lifecycle preserves application output."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_SHA = "daceec649fb4fe59b11e4a9e4ecd5f51c1dd37824280dfbeac67bec27b6b6d60"


class NetworkMinerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.archive = self.root / "release.zip"
        self.write_archive()
        curl = self.bin / "curl"
        curl.write_text("""#!/usr/bin/env bash
while (($#)); do
  if [[ $1 == -o ]]; then output=$2; shift 2; else uri=$1; shift; fi
done
[[ ${NETWORKMINER_CURL_FAIL:-0} == 0 ]] || exit 22
cp -- "$NETWORKMINER_FIXTURE_ARCHIVE" "$output"
""")
        curl.chmod(0o755)
        sha256 = self.bin / "sha256sum"
        sha256.write_text(f"""#!/usr/bin/env bash
if [[ ${{NETWORKMINER_BAD_SHA:-0}} == 1 ]]; then
  printf '%s  %s\\n' '{'0'*64}' "$1"
else
  printf '%s  %s\\n' '{ARCHIVE_SHA}' "$1"
fi
""")
        sha256.chmod(0o755)
        mono = self.bin / "mono"
        mono.write_text("#!/bin/sh\nexit 0\n")
        mono.chmod(0o755)
        row = next(item for item in json.loads((ROOT / "catalog/operations.json").read_text())["operations"]
                   if item["id"] == "package.networkminer")
        self.entry = self.root / "entry.json"
        self.entry.write_text(json.dumps(row))
        self.env = os.environ | {
            "HOME": str(self.home),
            "PATH": f"{self.bin}:{os.environ['PATH']}",
            "RIDE_ROOT": str(ROOT),
            "NETWORKMINER_FIXTURE_ARCHIVE": str(self.archive),
        }
        self.environment = self.home / ".local/opt/ride-fedora/networkminer/3.2"
        self.launcher = self.home / ".local/bin/networkminer"
        self.desktop = self.home / ".local/share/applications/networkminer.desktop"
        self.data = self.home / ".local/share/networkminer"

    def write_archive(self):
        with zipfile.ZipFile(self.archive, "w", zipfile.ZIP_DEFLATED) as bundle:
            bundle.writestr("NetworkMiner_3-2/NetworkMiner.exe", b"exe fixture")
            bundle.writestr("NetworkMiner_3-2/PacketParser.dll", b"dll fixture")
            bundle.writestr("NetworkMiner_3-2/Fingerprints/mac-ages_LICENSE", b"GPL-2.0 notice")
            bundle.writestr("NetworkMiner_3-2/Fingerprints/mac-ages.txt", b"fixture")

    def change(self, state, overrides=None):
        script = ('source "$RIDE_ROOT/lib/v3/common.sh"; '
                  'source "$RIDE_ROOT/lib/v3/providers.sh"; '
                  f'ride_change_networkminer "$(cat {self.entry})" {state}')
        return subprocess.run(["bash", "-c", script], env=self.env | (overrides or {}),
                              text=True, capture_output=True)

    def observe(self):
        script = ('source "$RIDE_ROOT/lib/v3/common.sh"; '
                  'source "$RIDE_ROOT/lib/v3/providers.sh"; '
                  f'ride_observe_networkminer "$(cat {self.entry})"')
        return subprocess.run(["bash", "-c", script], env=self.env,
                              text=True, capture_output=True)

    def test_apply_repeat_status_and_remove_preserve_output(self):
        installed = self.change("installed")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual(self.observe().stdout.strip(), "installed")
        self.assertEqual(self.launcher.readlink(), self.environment / "bin/networkminer")
        self.assertEqual(self.desktop.readlink(), self.environment / "networkminer.desktop")
        self.assertEqual((self.environment / "payload/Fingerprints/mac-ages_LICENSE").read_bytes(),
                         b"GPL-2.0 notice")
        self.assertEqual(self.data.stat().st_mode & 0o777, 0o700)
        repeated = self.change("installed")
        self.assertEqual(repeated.returncode, 0, repeated.stderr)

        captures = self.data / "Captures/seed.pcap"
        assembled = self.data / "AssembledFiles/seed.txt"
        captures.parent.mkdir()
        assembled.parent.mkdir()
        captures.write_bytes(b"seeded capture stays untouched")
        assembled.write_bytes(b"seeded output stays untouched")
        removed = self.change("absent")
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertFalse(self.environment.exists())
        self.assertFalse(self.launcher.is_symlink())
        self.assertFalse(self.desktop.is_symlink())
        self.assertEqual(captures.read_bytes(), b"seeded capture stays untouched")
        self.assertEqual(assembled.read_bytes(), b"seeded output stays untouched")

    def test_digest_download_archive_and_owned_file_conflicts_fail_closed(self):
        bad_digest = self.change("installed", {"NETWORKMINER_BAD_SHA": "1"})
        self.assertNotEqual(bad_digest.returncode, 0)
        self.assertFalse(self.environment.exists())

        failed_download = self.change("installed", {"NETWORKMINER_CURL_FAIL": "1"})
        self.assertNotEqual(failed_download.returncode, 0)
        self.assertFalse(self.environment.exists())

        occupied = self.home / ".local/opt/ride-fedora/networkminer/3.2"
        occupied.parent.mkdir(parents=True, exist_ok=True)
        occupied.mkdir()
        (occupied / "keep").write_text("user content")
        conflict = self.change("installed")
        self.assertNotEqual(conflict.returncode, 0)
        self.assertEqual((occupied / "keep").read_text(), "user content")

    def test_unsafe_zip_member_and_modified_payload_are_refused(self):
        with zipfile.ZipFile(self.archive, "w") as bundle:
            bundle.writestr("NetworkMiner_3-2/NetworkMiner.exe", b"exe")
            bundle.writestr("NetworkMiner_3-2/PacketParser.dll", b"dll")
            bundle.writestr("NetworkMiner_3-2/Fingerprints/mac-ages_LICENSE", b"notice")
            bundle.writestr("../escape", b"bad")
        unsafe = self.change("installed")
        self.assertNotEqual(unsafe.returncode, 0)
        self.assertFalse((self.root / "escape").exists())
        self.assertFalse(self.environment.exists())

        self.write_archive()
        self.assertEqual(self.change("installed").returncode, 0)
        (self.environment / "payload/NetworkMiner.exe").write_bytes(b"user modification")
        refused = self.change("absent")
        self.assertNotEqual(refused.returncode, 0)
        self.assertTrue(self.launcher.is_symlink())
        self.assertEqual((self.environment / "payload/NetworkMiner.exe").read_bytes(), b"user modification")


if __name__ == "__main__":
    unittest.main()
