"""Volatility 2 bundle removal is restricted to its exact RIDE-owned path."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent


class Volatility2Tests(unittest.TestCase):
    def test_remove_refuses_unowned_destination(self):
        with tempfile.TemporaryDirectory() as temp:
            environment = Path(temp) / "ride-fedora" / "tools" / "volatility2"
            environment.mkdir(parents=True)
            (environment / "user-data").write_text("preserve")
            env = os.environ | {"XDG_DATA_HOME": temp, "RIDE_ROOT": str(ROOT)}
            script = ('source "$RIDE_ROOT/lib/v3/common.sh"; '
                      'source "$RIDE_ROOT/lib/v3/providers.sh"; '
                      'ride_change_volatility2 "${RIDE_ENTRY}" absent')
            env["RIDE_ENTRY"] = Path(ROOT / "catalog/operations.json").read_text()
            env["RIDE_ENTRY"] = subprocess.run(
                ["jq", '-c', '.operations[] | select(.id == "package.volatility2")',
                 str(ROOT / "catalog/operations.json")], check=True, text=True,
                capture_output=True).stdout.strip()
            refused = subprocess.run(["bash", "-c", script], env=env, text=True,
                                     capture_output=True)
            self.assertNotEqual(refused.returncode, 0)
            self.assertEqual((environment / "user-data").read_text(), "preserve")


if __name__ == "__main__":
    unittest.main()
