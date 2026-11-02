"""Owned DNF5 tuning drop-in lifecycle tests."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
PROVIDER = ROOT / "lib/v3/providers.sh"
ENTRY = '{"id":"setting.dnf5-fast-tuning","handler":"dnf5-fast-tuning"}'


class Dnf5FastTuningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ride-dnf5-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.etc = self.root / "etc-dnf"
        self.etc.mkdir()
        self.dist = self.root / "dist-dnf"
        self.dist.mkdir()
        self.main = self.root / "dnf.conf"
        self.main.write_text("[main]\n", encoding="utf-8")
        self.path = self.etc / "99-ride-fastdnf.conf"

    def shell(self, body):
        script = f'''set -euo pipefail
source {PROVIDER}
ride_dnf5_tuning_dir() {{ printf '%s\\n' "$TEST_ETC"; }}
ride_dnf5_tuning_path() {{ printf '%s/99-ride-fastdnf.conf\\n' "$TEST_ETC"; }}
ride_dnf5_tuning_main() {{ printf '%s\\n' "$TEST_MAIN"; }}
ride_dnf5_tuning_distribution_dir() {{ printf '%s\\n' "$TEST_DIST"; }}
ride_require_command() {{ command -v "$1" >/dev/null; }}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 1; }}
ride_error() {{ printf '%s\\n' "$*" >&2; }}
stat() {{ printf '0\\n'; }}
dnf5() {{
  if [[ -f "$TEST_MAIN" ]] && grep -Eiq '^[[:space:]]*fastestmirror[[:space:]]*=' "$TEST_MAIN"; then
    sed -n -E '/^[[:space:]]*fastestmirror[[:space:]]*=/p;/^[[:space:]]*max_parallel_downloads[[:space:]]*=/p' "$TEST_MAIN"
  elif [[ -f "$TEST_ETC/99-ride-fastdnf.conf" ]]; then
    sed -n -E '/^[[:space:]]*fastestmirror[[:space:]]*=/p;/^[[:space:]]*max_parallel_downloads[[:space:]]*=/p' "$TEST_ETC/99-ride-fastdnf.conf"
  else
    printf 'fastestmirror=False\\nmax_parallel_downloads=3\\n'
  fi
}}
entry='{ENTRY}'
{body}
'''
        env = os.environ.copy()
        env.update(TEST_ETC=str(self.etc), TEST_DIST=str(self.dist), TEST_MAIN=str(self.main))
        return subprocess.run(["bash", "-c", script], env=env, text=True,
                              capture_output=True, check=False)

    def test_apply_repeat_and_exact_absent_restore(self):
        result = self.shell('ride_dnf5_fast_tuning_change configured\nride_dnf5_fast_tuning_observe\nride_dnf5_fast_tuning_change configured\nride_dnf5_fast_tuning_change absent\nride_dnf5_fast_tuning_observe')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["configured", "absent"])
        self.assertFalse(self.path.exists())

    def test_unowned_file_and_admin_setting_conflicts_are_refused(self):
        self.path.write_text("[main]\nfastestmirror=True\n", encoding="utf-8")
        result = self.shell('ride_dnf5_tuning_guard')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not owned", result.stderr)
        self.path.unlink()
        self.main.write_text("[main]\nmax_parallel_downloads=8\n", encoding="utf-8")
        result = self.shell('ride_dnf5_tuning_guard')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("main configuration sets", result.stderr)

    def test_other_dnf_dropin_conflict_is_refused(self):
        (self.dist / "95-site.conf").write_text("[main]\nfastestmirror=False\n", encoding="utf-8")
        result = self.shell('ride_dnf5_tuning_guard')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("conflicts with another", result.stderr)

    def test_exact_owned_file_can_be_removed(self):
        self.path.write_text("# RIDE v3 managed: setting.dnf5-fast-tuning\n[main]\nfastestmirror=True\nmax_parallel_downloads=15\n", encoding="utf-8")
        result = self.shell('ride_dnf5_fast_tuning_change absent')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.path.exists())


if __name__ == "__main__":
    unittest.main()
