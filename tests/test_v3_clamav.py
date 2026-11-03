"""Mocked ClamAV package, signature snapshot, and exact inverse lifecycle."""

import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ClamAVLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.data = self.root / "clamav"
        self.data.mkdir()
        (self.data / "seeded.dat").write_bytes(b"existing signature state\n")
        (self.data / "seeded.dat").chmod(0o640)
        self.owner = self.root / "state/package.clamav"
        self.packages = self.root / "packages.json"
        self.packages.write_text('{"clamav":false,"clamav-freshclam":false}\n')
        self.systemctl = self._command("systemctl", r'''#!/usr/bin/env bash
set -eu
unit=${@: -1}
installed=$(jq -r 'any(.[]; . == true)' "$CLAMAV_PACKAGES")
case "$1" in
  show) if [[ "$installed" == true ]]; then printf 'loaded\n'; else printf 'not-found\n'; fi ;;
  is-enabled) if [[ "$installed" == true ]]; then printf 'disabled\n'; else printf 'not-found\n'; fi ;;
  is-active) if [[ "$installed" == true ]]; then printf 'inactive\n'; else printf 'inactive\n'; fi ;;
  *) exit 2 ;;
esac
''')
        self.rpm = self._command("rpm", r'''#!/usr/bin/env bash
set -eu
if [[ $1 == -q && $2 == --quiet ]]; then
  jq -e --arg package "$3" '.[$package] == true' "$CLAMAV_PACKAGES" >/dev/null
elif [[ $1 == -qa && $2 == --qf ]]; then
  jq -r 'to_entries[] | select(.value == true) | .key' "$CLAMAV_PACKAGES"
else exit 2; fi
''')
        self.dnf = self._command("dnf", r'''#!/usr/bin/env bash
set -eu
case " $* " in
  *" install "*)
    for package in "$@"; do
      case "$package" in
        clamav|clamav-freshclam)
          jq --arg package "$package" '.[$package]=true' "$CLAMAV_PACKAGES" > "$CLAMAV_PACKAGES.tmp"
          mv "$CLAMAV_PACKAGES.tmp" "$CLAMAV_PACKAGES"
          if [[ "$package" == clamav-freshclam ]]; then
            cp "$CLAMAV_FRESHCLAM_TEMPLATE" "$CLAMAV_FRESHCLAM_BIN"
            chmod 0755 "$CLAMAV_FRESHCLAM_BIN"
          fi
          ;;
      esac
    done
    ;;
  *" remove "*)
    for package in "${@: -2}"; do
      case "$package" in
        clamav|clamav-freshclam)
          jq --arg package "$package" '.[$package]=false' "$CLAMAV_PACKAGES" > "$CLAMAV_PACKAGES.tmp"
          mv "$CLAMAV_PACKAGES.tmp" "$CLAMAV_PACKAGES"
          [[ "$package" != clamav-freshclam ]] || rm -f "$CLAMAV_FRESHCLAM_BIN"
          ;;
      esac
    done
    ;;
  *) exit 2 ;;
esac
''')
        self.freshclam = self._command("freshclam", r'''#!/usr/bin/env bash
set -eu
[[ ${CLAMAV_UPDATE_FAIL:-0} == 0 ]] || exit 7
mkdir -p "$CLAMAV_DATA"
printf 'fresh signatures\n' > "$CLAMAV_DATA/daily.cvd"
printf 'fresh metadata\n' > "$CLAMAV_DATA/freshclam.dat"
printf 'Database test passed.\ndaily.cvd updated (version: 1)\n'
''')
        self.freshclam_template = self.root / "freshclam-template"
        self.freshclam_template.write_text(self.freshclam.read_text())
        self.freshclam.unlink()
        self.entry = next(
            item for item in json.loads((ROOT / "catalog/operations.json").read_text())['operations']
            if item['id'] == 'package.clamav'
        )
        self.entry_file = self.root / "entry.json"
        self.entry_file.write_text(json.dumps(self.entry))
        self.env = os.environ | {
            "PATH": f"{self.bin}:{os.environ['PATH']}",
            "CLAMAV_PACKAGES": str(self.packages),
            "CLAMAV_DATA": str(self.data),
            "CLAMAV_FRESHCLAM_TEMPLATE": str(self.freshclam_template),
            "CLAMAV_FRESHCLAM_BIN": str(self.bin / "freshclam"),
            "CLAMAV_UPDATE_FAIL": "0",
        }

    def _command(self, name, content):
        path = self.bin / name
        path.write_text(content)
        path.chmod(0o755)
        return path

    def _ride(self, command, env=None):
        script = (
            'source "$RIDE_ROOT/lib/v3/common.sh"; '
            'source "$RIDE_ROOT/lib/v3/providers.sh"; '
            'source "$RIDE_ROOT/lib/v3/clamav.sh"; '
            'RIDE_OS_ID=fedora; RIDE_OS_VERSION=44; RIDE_ARCH=x86_64; '
            f'RIDE_CLAMAV_DATA_DIR={shlex.quote(str(self.data))}; '
            f'RIDE_CLAMAV_OWNER_DIR={shlex.quote(str(self.owner))}; '
            f'ENTRY=$(cat {shlex.quote(str(self.entry_file))}); {command}'
        )
        return subprocess.run(
            ["bash", "-c", script], env=(env or self.env) | {"RIDE_ROOT": str(ROOT)},
            text=True, capture_output=True, check=False,
        )

    def _package_state(self):
        return json.loads(self.packages.read_text())

    def test_apply_repeat_remove_restores_seeded_data_and_package_state(self):
        before = (self.data / "seeded.dat").read_bytes()
        mode = (self.data / "seeded.dat").stat().st_mode & 0o777
        applied = self._ride('ride_change "$ENTRY" installed')
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertEqual(self._package_state(), {"clamav": True, "clamav-freshclam": True})
        self.assertTrue((self.data / "daily.cvd").exists())
        self.assertEqual(self._ride('ride_observe "$ENTRY"').stdout.strip(), "installed")
        repeated = self._ride('ride_change "$ENTRY" installed')
        self.assertEqual(repeated.returncode, 0, repeated.stderr)

        removed = self._ride('ride_change "$ENTRY" absent')
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual(self._package_state(), {"clamav": False, "clamav-freshclam": False})
        self.assertEqual(sorted(path.name for path in self.data.iterdir()), ["seeded.dat"])
        self.assertEqual((self.data / "seeded.dat").read_bytes(), before)
        self.assertEqual((self.data / "seeded.dat").stat().st_mode & 0o777, mode)
        self.assertEqual(self._ride('ride_observe "$ENTRY"').stdout.strip(), "absent")

    def test_update_failure_rolls_back_packages_database_and_ownership_record(self):
        before = (self.data / "seeded.dat").read_bytes()
        failed = self._ride('ride_change "$ENTRY" installed', self.env | {"CLAMAV_UPDATE_FAIL": "1"})
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("initial FreshClam update failed", failed.stderr)
        self.assertEqual(self._package_state(), {"clamav": False, "clamav-freshclam": False})
        self.assertEqual(sorted(path.name for path in self.data.iterdir()), ["seeded.dat"])
        self.assertEqual((self.data / "seeded.dat").read_bytes(), before)
        self.assertFalse((self.owner / "state.json").exists())
        self.assertFalse((self.owner / "snapshots").exists())

    def test_remove_preserves_a_preexisting_clamav_rpm(self):
        self.packages.write_text('{"clamav":true,"clamav-freshclam":false}\n')
        before = (self.data / "seeded.dat").read_bytes()
        applied = self._ride('ride_change "$ENTRY" installed')
        self.assertEqual(applied.returncode, 0, applied.stderr)
        removed = self._ride('ride_change "$ENTRY" absent')
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual(self._package_state(), {"clamav": True, "clamav-freshclam": False})
        self.assertEqual((self.data / "seeded.dat").read_bytes(), before)

    def test_removal_restores_data_directory_absence(self):
        (self.data / "seeded.dat").unlink()
        self.data.rmdir()
        applied = self._ride('ride_change "$ENTRY" installed')
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertTrue((self.data / "daily.cvd").is_file())
        removed = self._ride('ride_change "$ENTRY" absent')
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertFalse(self.data.exists())
        self.assertEqual(self._package_state(), {"clamav": False, "clamav-freshclam": False})


if __name__ == "__main__":
    unittest.main()
