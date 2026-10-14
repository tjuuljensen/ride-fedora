"""Volatility3 user environment removal is limited to RIDE-owned paths."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent


class VolatilityTests(unittest.TestCase):
    def test_remove_requires_exact_ownership_marker(self):
        with tempfile.TemporaryDirectory() as temp:
            environment = Path(temp) / "ride-fedora" / "tools" / "volatility3"
            environment.mkdir(parents=True)
            (environment / "user-file").write_text("keep")
            env = os.environ | {"XDG_DATA_HOME": temp, "RIDE_ROOT": str(ROOT)}
            script = ('source "$RIDE_ROOT/lib/v3/common.sh"; '
                      'source "$RIDE_ROOT/lib/v3/providers.sh"; '
                      'ride_change_volatility absent')
            refused = subprocess.run(["bash", "-c", script], env=env, text=True, capture_output=True)
            self.assertNotEqual(refused.returncode, 0)
            self.assertTrue(environment.exists())
            marker = environment / ".ride-owned"
            marker.write_text("ride-fedora package.volatility3 2.28.2\n")
            removed = subprocess.run(["bash", "-c", script], env=env, text=True, capture_output=True)
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertFalse(environment.exists())


if __name__ == "__main__":
    unittest.main()
