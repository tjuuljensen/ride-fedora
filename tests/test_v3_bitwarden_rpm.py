"""Pinned Bitwarden RPM install and inverse preserve owned package state."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/v3/providers.sh"
SHA256 = "2aa3b7a675432bef75e73f513ba365b055a8c16ec2a42610f019f4b6f7d0a61b"


class BitwardenRpmTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ride-bitwarden-rpm-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.calls = self.root / "calls.txt"
        self.entry = json.dumps({
            "id": "package.bitwarden-rpm", "packageName": "bitwarden",
            "version": "2026.10.1", "targets": {"fedora": {"architectures": ["x86_64"]}},
            "sourceUri": "https://example.invalid/Bitwarden-2026.10.1-x86_64.rpm",
            "sourceSha256": SHA256,
        })

    def run_change(self, *, state="installed", installed=False,
                   checksum="valid", identity="valid"):
        script = f"""set -euo pipefail
source {MODULE}
RIDE_OS_ID=fedora
ride_require_command() {{ :; }}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
rpm() {{
  printf 'rpm %s\\n' "$*" >> "$BW_CALLS"
  case "$*" in
    '-q --quiet bitwarden') [[ "$BW_INSTALLED" == 1 ]] ;;
    '-qp --queryformat %{{NAME}} %{{VERSION}} %{{ARCH}}'*)
      [[ "$BW_IDENTITY" == valid ]] && printf 'bitwarden 2026.10.1 x86_64\\n' || printf 'other 0 x86_64\\n' ;;
    *) return 2 ;;
  esac
}}
curl() {{
  printf 'curl %s\\n' "$*" >> "$BW_CALLS"
  while (($#)); do
    if [[ "$1" == --output ]]; then shift; printf 'rpm fixture\\n' > "$1"; return 0; fi
    shift
  done
  return 2
}}
sha256sum() {{ printf 'sha256sum %s\\n' "$*" >> "$BW_CALLS"; [[ "$BW_CHECKSUM" == valid ]]; }}
dnf() {{ printf 'dnf %s\\n' "$*" >> "$BW_CALLS"; }}
ride_change_pinned_rpm "$BW_ENTRY" "$BW_STATE"
"""
        env = os.environ.copy()
        env.update(BW_CALLS=str(self.calls), BW_ENTRY=self.entry,
                   BW_STATE=state, BW_INSTALLED="1" if installed else "0",
                   BW_CHECKSUM=checksum, BW_IDENTITY=identity, TMPDIR=str(self.root))
        return subprocess.run(["bash", "-c", script], env=env, text=True,
                              capture_output=True, check=False)

    def test_verified_release_asset_installs_from_temporary_file(self):
        result = self.run_change()
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.calls.read_text().splitlines()
        self.assertTrue(any("curl --fail --location" in line for line in calls))
        self.assertTrue(any(line.startswith("sha256sum --check --status") for line in calls))
        self.assertTrue(any(line.startswith("rpm -qp --queryformat") for line in calls))
        self.assertTrue(any(line.startswith("dnf --setopt=localpkg_gpgcheck=0 install -y ") for line in calls))
        self.assertFalse(list(self.root.glob("ride-pinned-rpm.*")))

    def test_checksum_mismatch_blocks_dnf_and_cleans_tempfile(self):
        result = self.run_change(checksum="invalid")
        self.assertEqual(result.returncode, 42)
        self.assertIn("SHA-256 mismatch", result.stderr)
        self.assertFalse(any(line.startswith("dnf ") for line in self.calls.read_text().splitlines()))
        self.assertFalse(list(self.root.glob("ride-pinned-rpm.*")))

    def test_wrong_rpm_identity_blocks_dnf(self):
        result = self.run_change(identity="invalid")
        self.assertEqual(result.returncode, 42)
        self.assertIn("identity does not match", result.stderr)
        self.assertFalse(any(line.startswith("dnf ") for line in self.calls.read_text().splitlines()))

    def test_existing_install_is_unchanged(self):
        result = self.run_change(installed=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls.read_text().splitlines(), ["rpm -q --quiet bitwarden"])

    def test_remove_deletes_only_the_named_package(self):
        result = self.run_change(state="absent", installed=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls.read_text().splitlines(), [
            "rpm -q --quiet bitwarden", "dnf remove -y bitwarden"])


if __name__ == "__main__":
    unittest.main()
