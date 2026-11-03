"""Validation tests for the structured Windows capability register."""

import copy
import unittest

from tools.check_alignment_register import validate_register, CONTRACT_REF, REGISTER
from tools.check_behavior_scenarios import _read_json, ROOT


class CapabilityDifferenceTests(unittest.TestCase):
    def setUp(self):
        self.register = _read_json(ROOT, REGISTER)
        self.contract_reference = _read_json(ROOT, CONTRACT_REF)

    def test_current_register_is_valid_and_pinned(self):
        self.assertEqual(validate_register(self.register, self.contract_reference), [])

    def test_duplicate_ids_are_rejected(self):
        register = copy.deepcopy(self.register)
        register["entries"].append(copy.deepcopy(register["entries"][0]))
        self.assertIn("register entry IDs must be unique",
                      validate_register(register, self.contract_reference))

    def test_temporary_gap_requires_a_review_trigger(self):
        register = copy.deepcopy(self.register)
        register["entries"][0]["disposition"] = "temporary-gap"
        register["entries"][0]["linkedWork"] = ["ALIGN-04"]
        register["entries"][0]["reviewRemovalTrigger"] = ""
        self.assertTrue(any("lacks reviewRemovalTrigger" in error
                            for error in validate_register(register, self.contract_reference)))


if __name__ == "__main__":
    unittest.main()
