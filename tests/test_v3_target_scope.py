"""Supported catalog entries must name the tested Linux edition."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import validate_v3


class TargetScopeTests(unittest.TestCase):
    def test_supported_operation_needs_variant_id_before_acceptance_evidence(self):
        catalog = json.loads(validate_v3.CATALOG.read_text(encoding="utf-8"))
        entry = next(item for item in catalog["operations"] if item["id"] == "package.less")
        entry["status"] = "supported"
        entry["targets"]["fedora"].pop("variantIds")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            path.write_text(json.dumps(catalog), encoding="utf-8")
            with patch.object(validate_v3, "CATALOG", path):
                with self.assertRaisesRegex(ValueError, "unscoped supported edition"):
                    validate_v3.validate()
                entry["targets"]["fedora"]["variantIds"] = ["workstation"]
                path.write_text(json.dumps(catalog), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "without acceptance evidence"):
                    validate_v3.validate()


if __name__ == "__main__":
    unittest.main()
