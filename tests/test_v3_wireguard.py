"""Focused ownership and recovery checks for WireGuard key generation."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/v3/wireguard.sh"


class WireGuardKeypairTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ride-wireguard-test-")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "wireguard"
        self.directory.mkdir(mode=0o700)
        self.private = self.directory / "privatekey"
        self.public = self.directory / "publickey"
        self.marker = self.directory / ".ride-owned-keypair"

    def shell(self, body, *, fail_pubkey=False):
        script = f"""set -euo pipefail
source {MODULE}
ride_wireguard_dir() {{ printf '%s\\n' "$WG_TEST_DIR"; }}
ride_wireguard_owner_ok() {{ return 0; }}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 1; }}
ride_require_command() {{ command -v "$1" >/dev/null; }}
rpm() {{ return 0; }}
if [[ "${{WG_FAIL_PUBKEY:-0}}" == 1 ]]; then
  wg() {{ if [[ "${{1:-}}" == pubkey ]]; then return 1; fi; command wg "$@"; }}
fi
{body}
"""
        env = os.environ.copy()
        env.update(WG_TEST_DIR=str(self.directory), WG_FAIL_PUBKEY="1" if fail_pubkey else "0")
        return subprocess.run(["bash", "-c", script], env=env, text=True,
                              capture_output=True, check=False)

    def test_generate_repeat_validate_and_remove_only_owned_pair(self):
        result = self.shell('ride_wireguard_change configured\nride_wireguard_observe\n'
                            'ride_wireguard_change configured\nride_wireguard_change absent\nride_wireguard_observe')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["configured", "absent"])
        self.assertFalse(self.private.exists())
        self.assertFalse(self.public.exists())
        self.assertFalse(self.marker.exists())

    def test_private_pair_permissions_and_marker_do_not_expose_key(self):
        result = self.shell('ride_wireguard_change configured\nride_wireguard_observe')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "configured")
        self.assertEqual(self.private.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.public.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.marker.stat().st_mode & 0o777, 0o600)
        self.assertNotIn(self.private.read_text().strip(), self.marker.read_text())

    def test_preexisting_files_tampering_and_unrelated_config_refused(self):
        self.private.write_text("existing secret\n")
        self.private.chmod(0o600)
        result = self.shell('ride_wireguard_change configured')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.private.read_text(), "existing secret\n")
        self.private.unlink()
        self.private.symlink_to(self.public)
        result = self.shell('ride_wireguard_change configured')
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(self.private.is_symlink())
        self.private.unlink()
        (self.directory / "wg0.conf").write_text("private config\n")
        result = self.shell('ride_wireguard_change configured')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.directory / "wg0.conf").read_text(), "private config\n")

    def test_key_tampering_blocks_remove(self):
        result = self.shell('ride_wireguard_change configured')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.private.write_text("changed\n")
        result = self.shell('ride_wireguard_change absent')
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(self.private.exists())
        self.assertTrue(self.public.exists())

    def test_generation_failure_cleans_temporary_material(self):
        result = self.shell('ride_wireguard_change configured', fail_pubkey=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(self.directory.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
