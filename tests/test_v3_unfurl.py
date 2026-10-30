"""UnfURL installation touches only a new, marked user environment."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent


class UnfurlTests(unittest.TestCase):
    def test_failed_pinned_install_cleans_only_new_environment(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            binary = root / "bin"
            binary.mkdir()
            python = binary / "python3"
            python.write_text("#!/bin/sh\n"
                              "test \"$1\" = -m && test \"$2\" = venv || exit 24\n"
                              "mkdir -p \"$3/bin\"\n"
                              "printf '#!/bin/sh\\nexit 23\\n' > \"$3/bin/python\"\n"
                              "chmod +x \"$3/bin/python\"\n")
            python.chmod(0o755)
            environment = root / "ride-fedora" / "tools" / "dfir-unfurl"
            sibling = environment.parent / "keep.txt"
            sibling.parent.mkdir(parents=True)
            sibling.write_text("keep")
            env = os.environ | {"XDG_DATA_HOME": temp, "RIDE_ROOT": str(ROOT),
                                "PATH": f"{binary}:{os.environ['PATH']}"}
            script = ('source "$RIDE_ROOT/lib/v3/common.sh"; '
                      'source "$RIDE_ROOT/lib/v3/providers.sh"; '
                      'ride_change_unfurl installed')
            failed = subprocess.run(["bash", "-c", script], env=env, text=True,
                                    capture_output=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertFalse(environment.exists())
            self.assertEqual(sibling.read_text(), "keep")

    def test_remove_refuses_unowned_and_preserves_sibling(self):
        with tempfile.TemporaryDirectory() as temp:
            environment = Path(temp) / "ride-fedora" / "tools" / "dfir-unfurl"
            environment.mkdir(parents=True)
            (environment / "user-file").write_text("keep")
            sibling = environment.parent / "keep.txt"
            sibling.write_text("keep")
            env = os.environ | {"XDG_DATA_HOME": temp, "RIDE_ROOT": str(ROOT)}
            script = ('source "$RIDE_ROOT/lib/v3/common.sh"; '
                      'source "$RIDE_ROOT/lib/v3/providers.sh"; '
                      'ride_change_unfurl absent')
            refused = subprocess.run(["bash", "-c", script], env=env, text=True,
                                     capture_output=True)
            self.assertNotEqual(refused.returncode, 0)
            self.assertTrue(environment.exists())
            marker = environment / ".ride-owned"
            marker.write_text("ride-fedora package.dfir-unfurl 20261007\n")
            removed = subprocess.run(["bash", "-c", script], env=env, text=True,
                                     capture_output=True)
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertFalse(environment.exists())
            self.assertEqual(sibling.read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
