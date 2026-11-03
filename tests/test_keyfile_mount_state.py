#!/usr/bin/env python3
"""Focused tests for the explicit keyfile-mount configuration lifecycle."""
from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "tools/keyfile-mount-state.py"
SPEC = importlib.util.spec_from_file_location("keyfile_mount_state", HELPER)
assert SPEC and SPEC.loader
STATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(STATE)


class KeyfileMountStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.base = Path(self.temp.name)
        self.crypttab = self.base / "crypttab"
        self.fstab = self.base / "fstab"
        self.mountinfo = self.base / "mountinfo"
        self.state_root = self.base / "state"
        self.test_root = self.base / "root"
        self.test_root.mkdir()
        (self.test_root / "root").mkdir()
        self.keyfile = self.test_root / "root/keyfile_1234"
        self.keyfile.write_bytes(b"synthetic-disposable-key-material")
        self.keyfile.chmod(0o400)
        self.before_crypttab = (
            b"# preserved crypttab comment\n"
            b"unrelated UUID=1111 none luks\n"
            b"ride-data UUID=2222 /root/keyfile_1234 luks\n"
            b"other UUID=3333 none luks\n"
        )
        self.before_fstab = (
            b"# preserved fstab comment\n"
            b"UUID=4444 /unrelated ext4 defaults 0 2\n"
            b"/dev/mapper/ride-data /secure ext4 defaults 0 2\n"
            b"UUID=5555 /other xfs defaults 0 0\n"
        )
        self.crypttab.write_bytes(self.before_crypttab)
        self.fstab.write_bytes(self.before_fstab)
        self.crypttab.chmod(0o644)
        self.fstab.chmod(0o644)
        self.mountinfo.write_text("", encoding="utf-8")
        self.env = os.environ.copy()
        self.env.update(
            {
                "RIDE_TEST_MODE": "1",
                "RIDE_KEYFILE_MOUNTS_TEST_CRYPTTAB": str(self.crypttab),
                "RIDE_KEYFILE_MOUNTS_TEST_FSTAB": str(self.fstab),
                "RIDE_KEYFILE_MOUNTS_TEST_MOUNTINFO": str(self.mountinfo),
                "RIDE_KEYFILE_MOUNTS_TEST_STATE_ROOT": str(self.state_root),
                "RIDE_KEYFILE_MOUNTS_TEST_ROOT": str(self.test_root),
            }
        )

    def tearDown(self):
        self.temp.cleanup()

    def call(self, action: str, mapper: str = "ride-data") -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(HELPER), action, "--mapper", mapper],
            text=True,
            capture_output=True,
            env=self.env,
            check=False,
        )

    def test_exact_remove_repeat_and_restore_preserves_keyfile_and_other_rows(self):
        key_digest = hashlib.sha256(self.keyfile.read_bytes()).hexdigest()
        self.assertEqual(self.call("observe").stdout.strip(), "configured")
        self.assertEqual(self.call("remove").stdout.strip(), "absent")
        self.assertNotIn(b"ride-data", self.crypttab.read_bytes())
        self.assertNotIn(b"/dev/mapper/ride-data", self.fstab.read_bytes())
        self.assertIn(b"unrelated UUID=1111", self.crypttab.read_bytes())
        self.assertIn(b"UUID=4444 /unrelated", self.fstab.read_bytes())
        self.assertEqual(self.call("remove").stdout.strip(), "absent")
        recovery = next(self.state_root.iterdir())
        self.assertEqual(recovery.stat().st_mode & 0o777, 0o700)
        self.assertEqual((recovery / "recovery.json").stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.call("restore").stdout.strip(), "configured")
        self.assertEqual(self.crypttab.read_bytes(), self.before_crypttab)
        self.assertEqual(self.fstab.read_bytes(), self.before_fstab)
        self.assertEqual(hashlib.sha256(self.keyfile.read_bytes()).hexdigest(), key_digest)
        self.assertEqual(list(self.state_root.iterdir()), [])

    def test_active_or_mounted_target_is_refused(self):
        device = self.test_root / "dev/mapper/ride-data"
        device.parent.mkdir(parents=True)
        device.touch()
        result = self.call("remove")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("active encrypted mapping", result.stderr)
        self.assertEqual(self.crypttab.read_bytes(), self.before_crypttab)
        device.unlink()
        self.mountinfo.write_text("36 25 253:0 / /secure rw - ext4 /dev/mapper/ride-data rw\n")
        result = self.call("remove")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("mounted encrypted target", result.stderr)

    def test_duplicate_missing_and_malformed_rows_are_refused(self):
        self.crypttab.write_bytes(self.before_crypttab + b"ride-data UUID=9999 /root/keyfile_1234 luks\n")
        self.assertNotEqual(self.call("remove").returncode, 0)
        self.crypttab.write_bytes(self.before_crypttab)
        self.fstab.write_bytes(b"# no selected mount\n")
        self.assertNotEqual(self.call("remove").returncode, 0)
        self.crypttab.write_bytes(b"ride-data\n")
        self.fstab.write_bytes(self.before_fstab)
        self.assertNotEqual(self.call("remove").returncode, 0)

    def test_unsafe_keyfile_and_mapper_name_are_refused(self):
        self.keyfile.chmod(0o644)
        self.assertNotEqual(self.call("remove").returncode, 0)
        self.keyfile.chmod(0o400)
        self.assertNotEqual(self.call("remove", "../ride-data").returncode, 0)

    def test_external_changes_are_preserved_and_recovery_refuses_overwrite(self):
        self.assertEqual(self.call("remove").stdout.strip(), "absent")
        changed = self.fstab.read_bytes() + b"UUID=6666 /new ext4 defaults 0 2\n"
        self.fstab.write_bytes(changed)
        result = self.call("restore")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("configuration changed since removal", result.stderr)
        self.assertEqual(self.fstab.read_bytes(), changed)
        self.assertTrue(next(self.state_root.iterdir()).exists())

    def test_keyfile_change_blocks_restore_and_keeps_recovery(self):
        self.assertEqual(self.call("remove").stdout.strip(), "absent")
        self.keyfile.chmod(0o600)
        self.keyfile.write_bytes(b"changed")
        self.keyfile.chmod(0o400)
        result = self.call("restore")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("keyfile changed", result.stderr)
        self.assertNotIn(b"ride-data", self.crypttab.read_bytes())
        self.assertTrue(next(self.state_root.iterdir()).exists())

    def test_second_file_failure_rolls_back_first_and_discards_snapshot(self):
        original = STATE.atomic_replace
        calls = 0

        def fail_fstab_once(path, expected, replacement, metadata):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise STATE.Refusal("simulated fstab write failure")
            return original(path, expected, replacement, metadata)

        with mock.patch.dict(os.environ, self.env), mock.patch.object(STATE, "atomic_replace", side_effect=fail_fstab_once):
            with self.assertRaisesRegex(STATE.Refusal, "simulated fstab write failure"):
                STATE.remove("ride-data")
        self.assertEqual(self.crypttab.read_bytes(), self.before_crypttab)
        self.assertEqual(self.fstab.read_bytes(), self.before_fstab)
        self.assertEqual(list(self.state_root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
