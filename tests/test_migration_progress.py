"""The progress ledger must not hide or falsely complete v2 outcomes."""

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import migration_progress


class MigrationProgressTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = migration_progress.read_json(migration_progress.LEDGER)

    def validate_copy(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "outcomes.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with patch.object(migration_progress, "LEDGER", path):
                return migration_progress.validate()

    def test_pinned_source_and_exclusions_are_covered(self):
        data = self.validate_copy(copy.deepcopy(self.data))
        self.assertEqual(len(data["outcomes"]), 180)
        self.assertEqual(len(data["exclusions"]), 15)

    def test_missing_or_duplicate_outcome_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["outcomes"].pop()
        with self.assertRaisesRegex(ValueError, "exactly 180"):
            self.validate_copy(data)
        data = copy.deepcopy(self.data)
        data["outcomes"][1] = copy.deepcopy(data["outcomes"][0])
        with self.assertRaisesRegex(ValueError, "duplicate or invalid outcome key"):
            self.validate_copy(data)

    def test_false_operable_and_supported_claims_are_rejected(self):
        data = copy.deepcopy(self.data)
        row = next(item for item in data["outcomes"] if item["key"] == "workstation:package.Volatility3")
        row.update(disposition="migrate", progress="operable", blocker="",
                   v3Ids=["package.exfatprogs"],
                   evidence=["docs/acceptance/package.volatility3.md"], v31Hardening=["H002"])
        with self.assertRaisesRegex(ValueError, "catalog status or target disagrees"):
            self.validate_copy(data)
        row["v3Ids"] = ["package.volatility3"]
        row["evidence"] = ["docs/acceptance/package.exfatprogs.md"]
        with self.assertRaisesRegex(ValueError, "lacks passing VM acceptance evidence"):
            self.validate_copy(data)
        row["evidence"] = ["docs/acceptance/package.volatility3.md"]
        row["progress"] = "supported"
        with self.assertRaisesRegex(ValueError, "catalog status or target disagrees"):
            self.validate_copy(data)

    def test_high_risk_candidate_cannot_count_as_complete(self):
        data = copy.deepcopy(self.data)
        row = next(item for item in data["outcomes"] if item["risk"] == "high")
        row.update(disposition="migrate", progress="operable", blocker="",
                   v3Ids=["package.less"], evidence=["docs/MIGRATION-PLAN.md"])
        with self.assertRaisesRegex(ValueError, "high-risk"):
            self.validate_copy(data)

    def test_non_operable_resolution_needs_evidence(self):
        data = copy.deepcopy(self.data)
        row = data["outcomes"][0]
        row.update(disposition="retire", progress="resolved", blocker="")
        with self.assertRaisesRegex(ValueError, "documented non-operable resolution"):
            self.validate_copy(data)

    def test_replacement_is_resolved_but_not_counted_as_runnable(self):
        data = copy.deepcopy(self.data)
        row = next(item for item in data["outcomes"] if item["progress"] == "unresolved")
        row.update(disposition="replace", progress="resolved", blocker="",
                   reason="The replacement is described in the migration plan.",
                   reviewTrigger="Revisit when the replacement behavior changes.",
                   evidence=["docs/MIGRATION-PLAN.md"])
        self.validate_copy(data)
        report = migration_progress.summarize(data)
        prior = migration_progress.summarize(self.data)
        self.assertEqual(report["replaced"], prior["replaced"] + 1)
        self.assertEqual(report["runnable"], prior["runnable"])
        self.assertEqual(report["requiresAllowCandidate"], prior["requiresAllowCandidate"])

    def test_status_does_not_count_unresolved_rows(self):
        data = copy.deepcopy(self.data)
        before = migration_progress.summarize(data)
        row = next(item for item in data["outcomes"] if item["progress"] == "unresolved")
        row.update(disposition="migrate", progress="assessed")
        after = migration_progress.summarize(data)
        self.assertEqual(before["total"], 180)
        self.assertEqual(before["complete"], after["complete"])
        self.assertEqual(before["unresolved"], after["unresolved"])


if __name__ == "__main__":
    unittest.main()
