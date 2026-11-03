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
        self.assertEqual(len(data["outcomes"]), 185)
        self.assertEqual(len(data["exclusions"]), 11)
        self.assertNotIn("workstation:package.CitrixClient",
                         {row["key"] for row in data["outcomes"]})
        self.assertNotIn("workstation:package.Opera",
                         {row["key"] for row in data["outcomes"]})
        self.assertEqual(
            {item["sourceFunction"] for item in data["exclusions"] if item["source"] == "workstation"},
            {"InstallCitrixClient", "RemoveCitrixClient", "InstallOpera", "RemoveOpera"})

    def test_security_lab_member_inventory_is_visible_and_reconciled(self):
        report = migration_progress.summarize(self.data)
        self.assertEqual(report["securityLab"], {
            "total": 137, "profiled": 137, "catalogOnly": 0, "unmapped": 0,
        })

    def test_security_lab_duplicate_inventory_member_is_rejected(self):
        inventory = migration_progress.read_json(migration_progress.SECURITY_LAB_INVENTORY)
        inventory["packages"][1]["packageName"] = inventory["packages"][0]["packageName"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "security-lab-inventory.json"
            path.write_text(json.dumps(inventory), encoding="utf-8")
            with patch.object(migration_progress, "SECURITY_LAB_INVENTORY", path):
                with self.assertRaisesRegex(ValueError, "duplicate or invalid Security Lab package"):
                    migration_progress.validate()

    def test_missing_or_duplicate_outcome_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["outcomes"].pop()
        with self.assertRaisesRegex(ValueError, "exactly 185"):
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
        with self.assertRaisesRegex(ValueError, "no candidate operation requiring opt-in"):
            self.validate_copy(data)
        row["v3Ids"] = ["package.volatility3"]
        row["evidence"] = ["docs/acceptance/package.exfatprogs.md"]
        with self.assertRaisesRegex(ValueError, "lacks passing VM acceptance evidence"):
            self.validate_copy(data)
        row["evidence"] = ["docs/acceptance/package.volatility3.md"]
        row["progress"] = "supported"
        with self.assertRaisesRegex(ValueError, "catalog status or target disagrees"):
            self.validate_copy(data)

    def test_unclassified_high_risk_candidate_cannot_count_as_complete(self):
        data = copy.deepcopy(self.data)
        row = next(item for item in data["outcomes"] if item["key"] == "workstation:package.Autopsy")
        row.pop("safetyDomains", None)
        row.update(disposition="migrate", progress="operable", blocker="",
                   v3Ids=["package.autopsy"],
                   evidence=["docs/acceptance/package.autopsy.md"],
                   v31Hardening=["H087"])
        with self.assertRaisesRegex(ValueError, "explicit safety-domain classification"):
            self.validate_copy(data)

    def test_deep_safety_domain_still_requires_deeper_gate(self):
        data = copy.deepcopy(self.data)
        row = next(item for item in data["outcomes"] if item["key"] == "server:package.AutoUpdate")
        row["safetyDomains"] = ["security"]
        with self.assertRaisesRegex(ValueError, "deep safety gate"):
            self.validate_copy(data)

    def test_deep_security_review_can_count_with_linked_domain_evidence(self):
        data = copy.deepcopy(self.data)
        row = next(item for item in data["outcomes"] if item["key"] == "workstation:setting.SSHreboot")
        row.update(progress="operable", blocker="", v3Ids=["setting.ssh-reboot"],
                   safetyDomains=["security"], v31Hardening=["H112"],
                   evidence=["docs/migrations/system-security-18-ssh-reboot.md",
                             "docs/acceptance/setting.ssh-reboot.md",
                             "tests/test_v3_ssh_reboot.py", "tests/acceptance/test_ssh_reboot.py"],
                   safetyReview={
                       "status": "passed", "domains": ["security"],
                       "checks": ["scoped-privilege", "conflict-refusal", "real-action",
                                  "reconnect", "exact-recovery",
                                  "unrelated-policy-preservation"],
                       "evidence": ["docs/acceptance/setting.ssh-reboot.md"],
                   })
        validated = self.validate_copy(data)
        report = migration_progress.summarize(validated)
        self.assertEqual(report["v30PackageSetting"]["operable"], 148)
        self.assertEqual(report["v30PackageSetting"]["gap"], 5)

    def test_storage_and_encryption_candidate_requires_domain_specific_evidence(self):
        data = copy.deepcopy(self.data)
        row = next(item for item in data["outcomes"]
                   if item["key"] == "workstation:package.KeyfileMounts")
        row.update(progress="operable", blocker="", v3Ids=["setting.keyfile-mounts"],
                   v31Hardening=["H117"],
                   evidence=["docs/migrations/system-security-risk-decisions.md",
                             "docs/migrations/system-security-25-keyfile-mounts.md",
                             "docs/acceptance/setting.keyfile-mounts.md",
                             "tests/test_keyfile_mount_state.py",
                             "tests/acceptance/test_keyfile_mounts.py"],
                   safetyDomains=["storage", "encryption"],
                   safetyReview={
                       "status": "passed", "domains": ["storage", "encryption"],
                       "checks": ["exact-configuration-recovery", "unrelated-entry-preservation",
                                  "active-or-mounted-refusal", "keyfile-preservation",
                                  "encrypted-data-preservation", "boot-recovery"],
                       "evidence": ["docs/acceptance/setting.keyfile-mounts.md"],
                   })
        validated = self.validate_copy(data)
        report = migration_progress.summarize(validated)
        self.assertEqual(report["v30PackageSetting"]["operable"], 148)
        self.assertEqual(report["v30PackageSetting"]["gap"], 5)

    def test_deep_data_review_requires_output_boundary_evidence(self):
        data = copy.deepcopy(self.data)
        row = next(item for item in data["outcomes"]
                   if item["key"] == "workstation:package.NetworkMiner")
        row.pop("safetyReview", None)
        with self.assertRaisesRegex(ValueError, "deep safety gate"):
            self.validate_copy(data)
        self.validate_copy(self.data)

    def test_operable_outcome_can_combine_supported_and_candidate_operations(self):
        data = copy.deepcopy(self.data)
        row = next(item for item in data["outcomes"]
                   if item["key"] == "workstation:package.Codecs")
        row.update(risk="medium", progress="operable", blocker="",
                   v31Hardening=["H037"])
        self.validate_copy(data)
        report = migration_progress.summarize(data)
        self.assertEqual(report["v30PackageSetting"]["operable"], 148)
        self.assertEqual(report["v30PackageSetting"]["gap"], 5)

    def test_non_operable_resolution_needs_evidence(self):
        data = copy.deepcopy(self.data)
        row = data["outcomes"][0]
        row.update(disposition="retire", progress="resolved", blocker="", evidence=[])
        with self.assertRaisesRegex(ValueError, "documented non-operable resolution"):
            self.validate_copy(data)

    def test_replacement_is_resolved_but_not_counted_as_runnable(self):
        data = copy.deepcopy(self.data)
        row = next(item for item in data["outcomes"] if item["key"] == "workstation:package.Pwgen")
        row.update(disposition="replace", progress="resolved", blocker="", v3Ids=[],
                   v31Hardening=[],
                   reason="The replacement is described in the migration plan.",
                   reviewTrigger="Revisit when the replacement behavior changes.",
                   evidence=["docs/MIGRATION-PLAN.md"])
        self.validate_copy(data)
        report = migration_progress.summarize(data)
        prior = migration_progress.summarize(self.data)
        self.assertEqual(report["replaced"], prior["replaced"] + 1)
        self.assertEqual(report["runnable"], prior["runnable"] - 1)
        self.assertEqual(report["requiresAllowCandidate"], prior["requiresAllowCandidate"])
        self.assertEqual(report["v30PackageSetting"]["operable"],
                         prior["v30PackageSetting"]["operable"] - 1)

    def test_v30_package_setting_coverage_tracks_all_scoped_packages(self):
        report = migration_progress.summarize(self.data)
        coverage = report["v30PackageSetting"]
        self.assertEqual(coverage["ledgered"], 169)
        self.assertEqual(coverage["excludedPackages"], 0)
        self.assertEqual(coverage["total"], 169)
        self.assertEqual(coverage["operable"], 148)
        self.assertEqual(coverage["retired"], 10)
        self.assertEqual(coverage["kept"], 103)
        self.assertEqual(coverage["deferred"], 1)
        self.assertEqual(coverage["replaced"], 6)
        self.assertEqual(coverage["gap"], 5)
        startup = next(item for item in self.data["outcomes"]
                       if item["key"] == "workstation:package.ExpressVPNafterBoot")
        self.assertEqual((startup["disposition"], startup["progress"],
                          startup["v30Coverage"]), ("replace", "resolved", "replacement"))
        self.assertIn("reference/expressvpn-autoconnect.md", startup["evidence"])
        server_batch = next(batch for batch in report["batches"] if batch["id"] == "generic-server-15")
        self.assertEqual(server_batch["complete"], 1)
        self.assertEqual(server_batch["v30Operable"], 1)
        self.assertEqual(server_batch["v30Gap"], 0)

    def test_standalone_replacement_requires_direct_evidence(self):
        data = copy.deepcopy(self.data)
        row = next(item for item in data["outcomes"] if item["key"] == "workstation:package.Macvendor")
        row["evidence"] = ["docs/migrations/forensic-isolated-03.md"]
        with self.assertRaisesRegex(ValueError, "replacement lacks direct evidence"):
            self.validate_copy(data)

    def test_status_does_not_count_unresolved_rows(self):
        data = copy.deepcopy(self.data)
        before = migration_progress.summarize(data)
        row = next(item for item in data["outcomes"] if item["key"] == "workstation:package.Pwgen")
        row.update(disposition="migrate", progress="assessed", blocker="Assessment is pending")
        after = migration_progress.summarize(data)
        self.assertEqual(before["total"], 185)
        self.assertEqual(after["complete"], before["complete"] - 1)
        self.assertEqual(after["unresolved"], before["unresolved"] + 1)


if __name__ == "__main__":
    unittest.main()
