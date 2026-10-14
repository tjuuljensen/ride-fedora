"""DNF download must publish only RPMs accepted by rpmkeys."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent


class PackageVerificationTests(unittest.TestCase):
    def test_verified_download_and_rejected_signature(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            binaries = root / "bin"
            binaries.mkdir()
            dnf = binaries / "dnf"
            dnf.write_text("""#!/bin/sh
while [ "$#" -gt 0 ]; do
  if [ "$1" = --destdir ]; then target=$2; shift 2; else shift; fi
done
printf 'rpm content' > "$target/example-1.x86_64.rpm"
""")
            dnf.chmod(0o755)
            rpmkeys = binaries / "rpmkeys"
            rpmkeys.write_text("""#!/bin/sh
[ "$1" = --define ] || exit 2
[ "$2" = '_pkgverify_level all' ] || exit 2
[ "$3" = --checksig ] || exit 2
[ "${RIDE_TEST_SIGNATURE_OK:-0}" = 1 ]
""")
            rpmkeys.chmod(0o755)
            entry = '{"handler":"dnf-package","packageName":"example"}'
            script = ('source "$RIDE_ROOT/lib/v3/common.sh"; '
                      'source "$RIDE_ROOT/lib/v3/providers.sh"; '
                      'RIDE_OS_ID=fedora; '
                      'ride_download_package "$RIDE_TEST_ENTRY" "$RIDE_TEST_DESTINATION"')
            env = os.environ | {
                "PATH": f"{binaries}:{os.environ['PATH']}",
                "RIDE_ROOT": str(ROOT), "RIDE_TEST_ENTRY": entry,
                "RIDE_TEST_DESTINATION": str(root / "output"),
            }
            rejected = subprocess.run(["bash", "-c", script], env=env, text=True, capture_output=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(list((root / "output").glob("*.rpm")), [])
            env["RIDE_TEST_SIGNATURE_OK"] = "1"
            accepted = subprocess.run(["bash", "-c", script], env=env, text=True, capture_output=True)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            rpm = root / "output" / "example-1.x86_64.rpm"
            self.assertTrue(rpm.exists())
            self.assertTrue((root / "output" / "example-1.x86_64.rpm.sha256").exists())


if __name__ == "__main__":
    unittest.main()
