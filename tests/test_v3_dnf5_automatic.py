"""Owned DNF5 automatic-update timer and systemd drop-in lifecycle tests."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROVIDER = ROOT / "lib/v3/providers.sh"


class Dnf5AutomaticTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ride-dnf5-auto-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.dropin = self.root / "systemd/dnf5-automatic.service.d/50-ride-fedora.conf"
        self.marker = self.root / "state/dnf5-automatic.json"
        self.enabled = self.root / "enabled"
        self.active = self.root / "active"
        self.enabled.write_text("disabled\n", encoding="utf-8")
        self.active.write_text("inactive\n", encoding="utf-8")
        self.systemctl = self.bin / "systemctl"
        self.systemctl.write_text("""#!/usr/bin/env bash
set -euo pipefail
case "$*" in
  'is-enabled dnf5-automatic.timer')
    value=$(cat "$RIDE_TEST_DNF5_AUTO_ENABLED"); printf '%s\\n' "$value"
    [[ "$value" == enabled ]] ;;
  'is-active dnf5-automatic.timer')
    value=$(cat "$RIDE_TEST_DNF5_AUTO_ACTIVE"); printf '%s\\n' "$value"
    [[ "$value" == active ]] ;;
  'cat dnf5-automatic.service') cat "$RIDE_TEST_DNF5_AUTO_SERVICE" ;;
  'cat dnf5-automatic.timer')
    if [[ "$(cat "$RIDE_TEST_DNF5_AUTO_ENABLED")" == not-found ]]; then exit 1; fi
    printf '[Timer]\\nUnit=dnf5-automatic.service\\n' ;;
  'show --property=DropInPaths --value dnf5-automatic.service') : ;;
  'daemon-reload') : ;;
  'enable --now dnf5-automatic.timer') printf 'enabled\\n' > "$RIDE_TEST_DNF5_AUTO_ENABLED"; printf 'active\\n' > "$RIDE_TEST_DNF5_AUTO_ACTIVE" ;;
  'disable --now dnf5-automatic.timer') printf 'disabled\\n' > "$RIDE_TEST_DNF5_AUTO_ENABLED"; printf 'inactive\\n' > "$RIDE_TEST_DNF5_AUTO_ACTIVE" ;;
  *) printf 'unexpected systemctl command: %s\\n' "$*" >&2; exit 2 ;;
esac
""", encoding="utf-8")
        self.systemctl.chmod(0o755)
        self.dnf5 = self.bin / "dnf5"
        self.dnf5.write_text("#!/usr/bin/env bash\nprintf '%s\\n' '--installupdates'\n", encoding="utf-8")
        self.dnf5.chmod(0o755)
        self.service = self.root / "vendor.service"
        self.service.write_text("[Service]\nExecStart=/usr/bin/dnf5 automatic --timer\n", encoding="utf-8")
        self.timer = self.root / "vendor.timer"
        self.timer.write_text("[Timer]\nUnit=dnf5-automatic.service\n", encoding="utf-8")

    def shell(self, body):
        script = f'''set -euo pipefail
source {PROVIDER}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 1; }}
RIDE_TEST_MODE=1
RIDE_TEST_DNF5_AUTOMATIC_DROPIN={str(self.dropin)!r}
RIDE_TEST_DNF5_AUTOMATIC_MARKER={str(self.marker)!r}
{body}
'''
        env = os.environ.copy()
        env["PATH"] = f"{self.bin}:{env['PATH']}"
        env["RIDE_TEST_DNF5_AUTO_ENABLED"] = str(self.enabled)
        env["RIDE_TEST_DNF5_AUTO_ACTIVE"] = str(self.active)
        env["RIDE_TEST_DNF5_AUTO_SERVICE"] = str(self.service)
        env["RIDE_TEST_DNF5_AUTOMATIC_SERVICE_UNIT"] = str(self.service)
        env["RIDE_TEST_DNF5_AUTOMATIC_TIMER_UNIT"] = str(self.timer)
        return subprocess.run(["bash", "-c", script], env=env, text=True,
                              capture_output=True, check=False)

    def test_enable_repeat_status_and_exact_disable(self):
        result = self.shell('''
ride_dnf5_automatic_change enabled
ride_dnf5_automatic_observe
ride_dnf5_automatic_change enabled
ride_dnf5_automatic_change disabled
ride_dnf5_automatic_observe
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["enabled", "disabled"])
        self.assertFalse(self.dropin.exists())
        self.assertFalse(self.marker.exists())
        self.assertEqual(self.enabled.read_text(encoding="utf-8"), "disabled\n")
        self.assertEqual(self.active.read_text(encoding="utf-8"), "inactive\n")

    def test_missing_service_or_timer_unit_files_refuses_enablement(self):
        self.timer.unlink()
        result = self.shell("ride_dnf5_automatic_change enabled")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unit files are unavailable", result.stderr)
        self.assertFalse(self.marker.exists())
        self.assertFalse(self.dropin.exists())

    def test_marker_pins_command_and_timer_state(self):
        result = self.shell("ride_dnf5_automatic_change enabled")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--installupdates", self.dropin.read_text(encoding="utf-8"))
        marker = json.loads(self.marker.read_text(encoding="utf-8"))
        self.assertEqual(marker["priorEnabled"], "disabled")
        self.assertEqual(marker["priorActive"], "inactive")
        self.assertEqual(marker["managedEnabled"], "enabled")
        self.assertEqual(marker["managedActive"], "active")

    def test_existing_timer_or_override_is_not_claimed(self):
        self.enabled.write_text("enabled\n", encoding="utf-8")
        self.active.write_text("active\n", encoding="utf-8")
        result = self.shell("ride_dnf5_automatic_change enabled")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unowned DNF5 automatic timer", result.stderr)
        self.assertFalse(self.marker.exists())

        self.enabled.write_text("disabled\n", encoding="utf-8")
        self.active.write_text("inactive\n", encoding="utf-8")
        self.dropin.parent.mkdir(parents=True)
        self.dropin.write_text("unowned\n", encoding="utf-8")
        result = self.shell("ride_dnf5_automatic_change enabled")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unowned DNF5 automatic service override", result.stderr)
        self.assertEqual(self.dropin.read_text(encoding="utf-8"), "unowned\n")

        self.dropin.unlink()
        (self.dropin.parent / "20-other.conf").write_text("[Service]\\n", encoding="utf-8")
        result = self.shell("ride_dnf5_automatic_change enabled")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unowned DNF5 automatic service drop-ins", result.stderr)
        self.assertFalse(self.marker.exists())

    def test_modified_dropin_or_timer_blocks_restore(self):
        self.shell("ride_dnf5_automatic_change enabled")
        self.dropin.write_text(self.dropin.read_text(encoding="utf-8") + "# later edit\n",
                               encoding="utf-8")
        result = self.shell("ride_dnf5_automatic_change disabled")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("changed outside RIDE", result.stderr)
        self.assertTrue(self.marker.exists())
        self.assertTrue(self.dropin.exists())

    def test_external_timer_state_blocks_restore(self):
        self.shell("ride_dnf5_automatic_change enabled")
        self.enabled.write_text("enabled\n", encoding="utf-8")
        self.active.write_text("inactive\n", encoding="utf-8")
        result = self.shell("ride_dnf5_automatic_change disabled")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("changed outside RIDE", result.stderr)
        self.assertTrue(self.marker.exists())
        self.assertTrue(self.dropin.exists())

    def test_missing_dependency_timer_is_observed_as_disabled(self):
        self.enabled.write_text("not-found\n", encoding="utf-8")
        result = self.shell('''
ride_dnf5_automatic_timer_state
ride_dnf5_automatic_observe
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["disabled\tinactive", "disabled"])

    def test_systemd_disabled_and_inactive_nonzero_exit_codes_are_normal(self):
        result = self.shell('''
ride_dnf5_automatic_timer_state
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "disabled\tinactive")
