"""Focused UPower drop-in ownership and recovery tests."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
PROVIDER = ROOT / "lib/v3/providers.sh"
ENTRY = '{"id":"setting.upower-percentage-low","selectedValue":"15","handler":"upower-threshold"}'


class UPowerProviderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ride-upower-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.dropins = self.root / "UPower.conf.d"
        self.dropins.mkdir()
        self.main = self.root / "UPower.conf"
        self.main.write_text(
            "[UPower]\nUsePercentageForPolicy=true\n"
            "PercentageLow=20.0\nPercentageCritical=5.0\nPercentageAction=2.0\n",
            encoding="utf-8",
        )
        self.owned = self.dropins / "70-ride-percentage-low.conf"

    def shell(self, body, *, fail_restart=False):
        script = f"""set -euo pipefail
source {PROVIDER}
ride_upower_dir() {{ printf '%s\\n' "$UP_TEST_DIR"; }}
ride_upower_main() {{ printf '%s\\n' "$UP_TEST_MAIN"; }}
ride_upower_path() {{ printf '%s/70-ride-percentage-low.conf\\n' "$UP_TEST_DIR"; }}
ride_require_command() {{ command -v "$1" >/dev/null; }}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 1; }}
ride_error() {{ printf '%s\\n' "$*" >&2; }}
rpm() {{ return 0; }}
stat() {{ printf '0\\n'; }}
systemctl() {{ [[ "${{UP_FAIL_RESTART:-0}}" != 1 ]]; }}
entry='{ENTRY}'
{body}
"""
        env = os.environ.copy()
        env.update(UP_TEST_DIR=str(self.dropins), UP_TEST_MAIN=str(self.main),
                   UP_FAIL_RESTART="1" if fail_restart else "0")
        return subprocess.run(["bash", "-c", script], env=env, text=True,
                              capture_output=True, check=False)

    def test_absent_apply_repeat_and_restore(self):
        result = self.shell('ride_upower_guard 15\nride_upower_change "$entry" configured\nride_upower_observe "$entry"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "configured")
        self.assertEqual(self.owned.read_text(),
                         "# RIDE v3 managed: setting.upower-percentage-low\n"
                         "[UPower]\nPercentageLow=15.0\n")
        result = self.shell('ride_upower_observe "$entry"\nride_upower_change "$entry" absent\nride_upower_observe "$entry"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["configured", "absent"])
        self.assertFalse(self.owned.exists())

    def test_prior_owned_value_restored_exactly(self):
        self.owned.write_text(
            "# RIDE v3 managed: setting.upower-percentage-low\n"
            "[UPower]\nPercentageLow=20.0\n", encoding="utf-8")
        original = self.owned.read_bytes()
        result = self.shell('ride_upower_observe "$entry"\nride_upower_change "$entry" configured\nride_upower_change "$entry" owned:20\nride_upower_observe "$entry"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["owned:20", "owned:20"])
        self.assertEqual(self.owned.read_bytes(), original)

    def test_unowned_and_competing_admin_policy_refused(self):
        self.owned.write_text("[UPower]\nPercentageLow=15.0\n", encoding="utf-8")
        result = self.shell('ride_upower_guard 15')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not owned by RIDE", result.stderr)
        self.owned.unlink()
        self.owned.symlink_to(self.main)
        result = self.shell('ride_upower_guard 15')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not owned by RIDE", result.stderr)
        self.owned.unlink()
        (self.dropins / "80-admin.conf").write_text(
            "[UPower]\nPercentageLow=30.0\n", encoding="utf-8")
        result = self.shell('ride_upower_guard 15')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("another UPower drop-in", result.stderr)

    def test_invalid_policy_and_restart_failure_restore_absence(self):
        self.main.write_text(
            "[UPower]\nUsePercentageForPolicy=true\n"
            "PercentageCritical=18.0\nPercentageAction=2.0\n", encoding="utf-8")
        result = self.shell('ride_upower_guard 15')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must exceed critical", result.stderr)
        self.main.write_text(
            "[UPower]\nUsePercentageForPolicy=true\n"
            "PercentageCritical=5.0\nPercentageAction=2.0\n", encoding="utf-8")
        result = self.shell('ride_upower_change "$entry" configured', fail_restart=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.owned.exists())

    def test_profile_value_and_direct_value_validation(self):
        os_release = self.root / "os-release"
        os_release.write_text("ID=fedora\nVERSION_ID=44\nVARIANT_ID=workstation\n", encoding="utf-8")
        env = os.environ.copy()
        env.update(RIDE_TEST_MODE="1", RIDE_OS_RELEASE_FILE=str(os_release))
        planned = subprocess.run(
            [str(ROOT / "ride.sh"), "plan", "--profile", "upower-low-15"],
            env=env, text=True, capture_output=True, check=False,
        )
        self.assertEqual(planned.returncode, 0, planned.stderr)
        self.assertIn("configured:15", planned.stdout)
        for invalid in ("0", "5", "51", "015", "15.0", "true"):
            result = subprocess.run(
                [str(ROOT / "ride.sh"), "set", "setting.upower-percentage-low",
                 "--state", "configured", "--value", invalid, "--dry-run"],
                env=env, text=True, capture_output=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0, invalid)
            self.assertIn("invalid value", result.stderr)


if __name__ == "__main__":
    unittest.main()
