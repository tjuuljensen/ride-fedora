"""Pin and adapter checks for the shared RIDE behavior scenarios."""

import copy
import unittest

from tools.check_behavior_scenarios import _read_json, validate_envelope, validate_repository


class BehaviorScenarioTests(unittest.TestCase):
    def test_shared_scenario_revision_and_fedora_adapter_are_pinned(self):
        errors, count, revision = validate_repository()
        self.assertEqual(errors, [])
        self.assertEqual(revision, "1.1.0")
        self.assertEqual(count, 12)

    def test_seeded_scenario_revision_mismatch_is_rejected(self):
        from tools.check_behavior_scenarios import ROOT, ADAPTER_PATH, REFERENCE_PATH, SCENARIO_PATH

        scenario_set = _read_json(ROOT, SCENARIO_PATH)
        scenario_set["scenarioRevision"] = "9.9.9"
        adapter = _read_json(ROOT, ADAPTER_PATH)
        reference = _read_json(ROOT, REFERENCE_PATH)
        errors = validate_envelope(scenario_set, adapter, reference)
        self.assertIn("scenario revision differs from the Fedora adapter pin", errors)

    def test_seeded_missing_case_mapping_is_rejected(self):
        from tools.check_behavior_scenarios import ROOT, ADAPTER_PATH, REFERENCE_PATH, SCENARIO_PATH

        scenario_set = _read_json(ROOT, SCENARIO_PATH)
        adapter = _read_json(ROOT, ADAPTER_PATH)
        adapter = copy.deepcopy(adapter)
        adapter["mappings"].pop()
        reference = _read_json(ROOT, REFERENCE_PATH)
        errors = validate_envelope(scenario_set, adapter, reference)
        self.assertIn("Fedora adapter must map every shared scenario exactly once", errors)


if __name__ == "__main__":
    unittest.main()
