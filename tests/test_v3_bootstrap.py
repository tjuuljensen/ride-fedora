"""Portable bootstrap flow with a local archive in place of the network."""

import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent


class BootstrapTests(unittest.TestCase):
    def test_dash_download_only(self):
        if not shutil.which("dash"):
            self.skipTest("dash is installed in CI")
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            source = directory / "source"
            source.mkdir()
            (source / "ride.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
            archive = directory / "release.tar.gz"
            with tarfile.open(archive, "w:gz") as package:
                package.add(source / "ride.sh", arcname="ride-fedora-fixture/ride.sh")
            fake_bin = directory / "bin"
            fake_bin.mkdir()
            curl = fake_bin / "curl"
            curl.write_text("""#!/bin/sh
while [ "$#" -gt 0 ]; do
  if [ "$1" = --output ]; then output=$2; shift 2; else shift; fi
done
cp "$RIDE_TEST_BOOTSTRAP_ARCHIVE" "$output"
""")
            curl.chmod(0o755)
            destination = directory / "downloaded"
            env = os.environ | {"PATH": f"{fake_bin}:{os.environ['PATH']}",
                                "RIDE_TEST_BOOTSTRAP_ARCHIVE": str(archive)}
            result = subprocess.run(
                ["dash", str(ROOT / "docs" / "bootstrap.sh"), "--branch", "fixture",
                 "--destination", str(destination), "--download-only"],
                env=env, text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((destination / "ride.sh").is_file())


if __name__ == "__main__":
    unittest.main()
