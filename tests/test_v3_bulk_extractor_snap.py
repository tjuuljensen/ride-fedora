"""Pinned BulkExtractor Snap lifecycle without processing forensic data."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/v3/providers.sh"
PAYLOAD = b"fixture snap archive bytes\n"


class BulkExtractorSnapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ride-bulk-extractor-snap-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.calls = self.root / "calls.txt"
        self.payload = self.root / "source.snap"
        self.state = self.root / "snap-state"
        self.payload.write_bytes(PAYLOAD)
        self.entry = {
            "id": "package.bulk-extractor",
            "packageName": "bulk-extractor",
            "releaseVersion": "2.2.0",
            "snapArchiveUri": "https://example.invalid/bulk-extractor.snap",
            "sha256": hashlib.sha256(PAYLOAD).hexdigest(),
        }
        self.state.write_text("0 ", encoding="utf-8")

    def shell(self, body, installed="0", version=""):
        self.state.write_text(f"{installed} {version}", encoding="utf-8")
        script = f'''set -euo pipefail
source {MODULE}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
ride_require_command() {{ :; }}
snap() {{
  printf '%s\\n' "$*" >> "$TEST_CALLS"
  case "$1" in
    list)
      printf 'Name Version Rev Tracking Publisher Notes\\n'
      read -r installed version < "$TEST_STATE"
      if [[ "$installed" == 1 ]]; then
        printf 'bulk-extractor %s 1 - unknown dangerous\\n' "$version"
      fi
      ;;
    install)
      printf '1 2.2.0' > "$TEST_STATE"
      [[ "$(cat "${{!#}}")" == "$(cat "$TEST_PAYLOAD")" ]]
      ;;
    remove) printf '0 ' > "$TEST_STATE" ;;
    *) return 2 ;;
  esac
}}
curl() {{
  printf '%s\\n' "$*" >> "$TEST_CALLS"
  [[ "$TEST_DOWNLOAD_FAIL" == 0 ]] || return 22
  while (($#)); do
    if [[ "$1" == --output ]]; then cp "$TEST_PAYLOAD" "$2"; fi
    shift
  done
}}
{body}
'''
        env = os.environ.copy()
        env.update({
            "TEST_CALLS": str(self.calls),
            "TEST_PAYLOAD": str(self.payload),
            "TEST_STATE": str(self.state),
            "TEST_ENTRY": json.dumps(self.entry),
            "TEST_DOWNLOAD_FAIL": "0",
            "RIDE_OS_ID": "fedora",
            "TMPDIR": str(self.root),
        })
        return subprocess.run(["bash", "-c", script], env=env, text=True,
                              capture_output=True, check=False)

    def test_install_repeat_status_and_remove_use_verified_local_snap(self):
        result = self.shell(
            'test "$(ride_bulk_extractor_observe "$TEST_ENTRY")" = absent\n'
            'ride_bulk_extractor_change "$TEST_ENTRY" installed\n'
            'test "$(ride_bulk_extractor_observe "$TEST_ENTRY")" = installed\n'
            'ride_bulk_extractor_change "$TEST_ENTRY" installed\n'
            'ride_bulk_extractor_change "$TEST_ENTRY" absent\n'
            'test "$(ride_bulk_extractor_observe "$TEST_ENTRY")" = absent')
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.calls.read_text(encoding="utf-8").splitlines()
        self.assertTrue(any("--proto =https --tlsv1.2" in line for line in calls))
        self.assertTrue(any(line.startswith("install --dangerous ") for line in calls))
        self.assertIn("remove bulk-extractor", calls)
        self.assertNotIn("remove bulk-extractor --purge", calls)
        self.assertEqual(sum(line.startswith("install --dangerous ") for line in calls), 1)

    def test_existing_wrong_version_is_refused_without_mutation(self):
        result = self.shell(
            'ride_bulk_extractor_change "$TEST_ENTRY" installed',
            installed="1", version="2.1.1")
        self.assertEqual(result.returncode, 42)
        self.assertIn("expected pinned version 2.2.0", result.stderr)
        self.assertFalse(any(line.startswith("install ") for line in self.calls.read_text().splitlines()))

    def test_digest_mismatch_does_not_install(self):
        self.entry["sha256"] = "0" * 64
        result = self.shell(
            'ride_bulk_extractor_change "$TEST_ENTRY" installed')
        self.assertEqual(result.returncode, 42)
        self.assertIn("SHA-256 mismatch", result.stderr)
        calls = self.calls.read_text(encoding="utf-8").splitlines()
        self.assertFalse(any(line.startswith("install ") for line in calls))

    def test_download_failure_does_not_install(self):
        result = subprocess.run(
            ["bash", "-c", f'''set -euo pipefail
source {MODULE}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
ride_require_command() {{ :; }}
snap() {{ printf '%s\\n' "$*" >> "$TEST_CALLS"; printf 'Name Version Rev Tracking Publisher Notes\\n'; }}
curl() {{ return 22; }}
ride_bulk_extractor_change "$TEST_ENTRY" installed
'''],
            env={**os.environ, "TEST_CALLS": str(self.calls),
                 "TEST_ENTRY": json.dumps(self.entry), "RIDE_OS_ID": "fedora",
                 "TMPDIR": str(self.root)}, text=True, capture_output=True,
            check=False)
        self.assertEqual(result.returncode, 42)
        self.assertIn("download failed", result.stderr)
        self.assertFalse(self.calls.exists() and any(
            line.startswith("install ") for line in self.calls.read_text().splitlines()))

    def test_public_catalog_guard_accepts_pinned_snap_operation(self):
        with tempfile.TemporaryDirectory(prefix="ride-bulk-extractor-catalog-") as directory:
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
                [str(ROOT / "ride.sh"), "show", "package.bulk-extractor"],
                cwd=ROOT, env=env, text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            shown = json.loads(result.stdout)
            self.assertEqual(shown["handler"], "pinned-snap-package")
            self.assertEqual(
                shown["sha256"],
                "dbc0749a7a84e2710c104a09fd921b93c1db9e2147bb11da978dea7af0e16c67")


if __name__ == "__main__":
    unittest.main()
