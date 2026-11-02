"""Autopsy Snap Store package presence and data-preserving removal tests."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/v3/providers.sh"


class SnapPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ride-snap-package-")
        self.addCleanup(self.temp.cleanup)
        self.calls = Path(self.temp.name) / "calls.txt"
        self.entry = json.dumps({"id": "package.autopsy", "packageName": "autopsy", "snapChannel": "latest/stable"})

    def shell(self, body, installed=False):
        script = f'''set -euo pipefail
source {MODULE}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
ride_require_command() {{ :; }}
snap() {{
  printf '%s\\n' "$*" >> "$TEST_CALLS"
  case "$1" in
    list)
      printf 'Name Version Rev Tracking Publisher Notes\\n'
      if [[ "$TEST_INSTALLED" == 1 ]]; then printf 'autopsy 4.22.1 123 latest/stable gregd-sleuthkit -\\n'; fi
      ;;
    install) TEST_INSTALLED=1 ;;
    remove) TEST_INSTALLED=0 ;;
    *) return 2 ;;
  esac
}}
{body}
'''
        env = os.environ.copy()
        env.update(TEST_CALLS=str(self.calls), TEST_ENTRY=self.entry,
                   TEST_INSTALLED="1" if installed else "0")
        return subprocess.run(["bash", "-c", script], env=env, text=True, capture_output=True, check=False)

    def test_observe_install_repeat_and_data_preserving_remove(self):
        result = self.shell(
            'test "$(ride_snap_store_package_observe "$TEST_ENTRY")" = absent\n'
            'ride_snap_store_package_change "$TEST_ENTRY" installed\n'
            'test "$(ride_snap_store_package_observe "$TEST_ENTRY")" = installed\n'
            'ride_snap_store_package_change "$TEST_ENTRY" installed\n'
            'ride_snap_store_package_change "$TEST_ENTRY" absent\n'
            'test "$(ride_snap_store_package_observe "$TEST_ENTRY")" = absent')
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.calls.read_text(encoding="utf-8").splitlines()
        self.assertIn("install autopsy --channel=latest/stable", calls)
        self.assertIn("remove autopsy", calls)
        self.assertNotIn("remove autopsy --purge", calls)
        self.assertEqual(calls.count("install autopsy --channel=latest/stable"), 1)

    def test_existing_snap_is_not_reinstalled(self):
        result = self.shell(
            'ride_snap_store_package_change "$TEST_ENTRY" installed\n'
            'test "$(ride_snap_store_package_observe "$TEST_ENTRY")" = installed',
            installed=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.calls.read_text(encoding="utf-8").splitlines()
        self.assertFalse(any(line.startswith("install ") for line in calls))

    def test_public_catalog_guard_accepts_autopsy_snap_operation(self):
        with tempfile.TemporaryDirectory(prefix="ride-snap-catalog-") as directory:
            root = Path(directory)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            snap = bin_dir / "snap"
            snap.write_text("#!/bin/sh\nprintf 'Name Version Rev Tracking Publisher Notes\\n'\n")
            snap.chmod(0o755)
            os_release = root / "os-release"
            os_release.write_text('ID=fedora\nVERSION_ID=44\nVARIANT_ID="workstation"\n')
            env = os.environ.copy()
            env.update({
                "PATH": f"{bin_dir}:{env['PATH']}",
                "RIDE_OS_RELEASE_FILE": str(os_release),
                "RIDE_STATE_DIR": str(root / "runs"),
                "RIDE_CACHE_DIR": str(root / "cache"),
            })
            result = subprocess.run(
                [str(ROOT / "ride.sh"), "show", "package.autopsy"],
                cwd=ROOT, env=env, text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            shown = json.loads(result.stdout)
            self.assertEqual(shown["handler"], "snap-store-package")
            self.assertEqual(shown["artifactFormat"], "snap")


if __name__ == "__main__":
    unittest.main()
