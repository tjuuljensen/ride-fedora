"""Exact-tree snapshots for ClamAV signature data."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("clamav_state", ROOT / "tools/clamav-state.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ClamAVTreeTests(unittest.TestCase):
    def test_copy_and_restore_preserve_bytes_mode_and_absence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            (source / "nested").mkdir()
            item = source / "nested" / "signature.cvd"
            item.write_bytes(b"original signature bytes\n")
            item.chmod(0o640)
            digest = MODULE.tree_hash(source)
            snapshot = root / "snapshots" / "before"
            MODULE.copy_tree(source, snapshot)
            item.write_bytes(b"mutated signature bytes\n")
            MODULE.restore_tree(snapshot, source, True)
            self.assertEqual(MODULE.tree_hash(source), digest)
            self.assertEqual((source / "nested/signature.cvd").read_bytes(), b"original signature bytes\n")
            self.assertEqual((source / "nested/signature.cvd").stat().st_mode & 0o777, 0o640)
            MODULE.restore_tree(snapshot, source, False)
            self.assertEqual(MODULE.tree_hash(source), "absent")

    def test_symlinks_are_rejected_before_snapshot_or_replacement(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            (source / "outside-link").symlink_to(root / "missing")
            with self.assertRaises(ValueError):
                MODULE.tree_hash(source)
            destination = root / "destination"
            destination.symlink_to(root)
            with self.assertRaises(ValueError):
                MODULE.restore_tree(root / "missing-snapshot", destination, False)


if __name__ == "__main__":
    unittest.main()
