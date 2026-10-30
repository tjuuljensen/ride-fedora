"""Focused checks for the read-only v3 journal inventory."""

import json
from pathlib import Path
import tempfile
import unittest

from tools.audit_v3_runs import inventory


class RunInventoryTests(unittest.TestCase):
    def test_absent_state_directory_has_no_runs(self):
        with tempfile.TemporaryDirectory() as name:
            self.assertEqual(inventory(Path(name) / "missing"), ([], 0))

    def test_changed_run_is_reviewed_until_completed_restore(self):
        original = "20261030T080000Z-1-2"
        inverse = "20261030T080100Z-3-4"
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            (directory / f"{original}.json").write_text(json.dumps({
                "schemaVersion": 2, "runId": original, "action": "apply",
                "status": "complete", "steps": [
                    {"id": "package.less", "result": "changed"},
                    {"id": "package.openssh-clients", "result": "unchanged"}],
            }), encoding="utf-8")
            self.assertEqual(inventory(directory),
                             ([(original, "complete", "review", "package.less")], 0))
            (directory / f"{inverse}.json").write_text(json.dumps({
                "schemaVersion": 2, "runId": inverse, "action": f"restore:{original}",
                "status": "complete", "steps": [{"id": "package.less", "result": "changed"}],
            }), encoding="utf-8")
            rows, invalid = inventory(directory)
            self.assertEqual(invalid, 0)
            self.assertEqual(rows[0], (original, "complete", "restored", "package.less"))
            self.assertEqual(rows[1], (inverse, "complete", "restore-record", "package.less"))

    def test_symlink_journal_is_flagged_without_reading_target(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            secret = directory / "private"
            secret.write_text("private", encoding="utf-8")
            link = directory / "20261030T080000Z-1-2.json"
            link.symlink_to(secret)
            rows, invalid = inventory(directory)
            self.assertEqual(invalid, 1)
            self.assertEqual(rows, [(json.dumps(link.name), "invalid", "review", "-")])

    def test_invalid_json_shape_is_flagged(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            path = directory / "20261030T080000Z-1-2.json"
            path.write_text("[]", encoding="utf-8")
            rows, invalid = inventory(directory)
            self.assertEqual(invalid, 1)
            self.assertEqual(rows[0][1:3], ("invalid", "review"))

    def test_failed_run_without_recorded_change_still_needs_review(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            identifier = "20261030T080000Z-1-2"
            (directory / f"{identifier}.json").write_text(json.dumps({
                "schemaVersion": 2, "runId": identifier, "action": "apply",
                "status": "failed", "steps": [
                    {"id": "package.less", "result": "failed"}],
            }), encoding="utf-8")
            self.assertEqual(inventory(directory),
                             ([(identifier, "failed", "review", "-")], 0))

    def test_restore_without_original_journal_needs_review(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            identifier = "20261030T080100Z-3-4"
            (directory / f"{identifier}.json").write_text(json.dumps({
                "schemaVersion": 2, "runId": identifier,
                "action": "restore:20261030T080000Z-1-2",
                "status": "complete", "steps": [],
            }), encoding="utf-8")
            self.assertEqual(inventory(directory),
                             ([(identifier, "complete", "review", "-")], 0))


if __name__ == "__main__":
    unittest.main()
