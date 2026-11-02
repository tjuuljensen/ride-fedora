"""Plex service ownership and active/enabled state tests."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/v3/providers.sh"
UNIT = "/usr/lib/systemd/system/plexmediaserver.service"


class PlexServerServiceTests(unittest.TestCase):
    def run_shell(self, body, *, fragment=UNIT, enabled="disabled", active="inactive", owner="plexmediaserver"):
        with tempfile.TemporaryDirectory(prefix="ride-plex-service-") as directory:
            calls = Path(directory) / "calls"
            script = f"""set -euo pipefail
source {MODULE}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
rpm() {{ [[ "$*" == "-qf --qf %{{NAME}} {UNIT}" ]] && printf '%s\\n' "$TEST_OWNER"; }}
systemctl() {{
  printf '%s\\n' "$*" >> "$TEST_CALLS"
  case "$*" in
    'show --property=FragmentPath --value plexmediaserver.service') printf '%s\\n' "$TEST_FRAGMENT" ;;
    'is-enabled plexmediaserver.service') printf '%s\\n' "$TEST_ENABLED" ;;
    'is-active plexmediaserver.service') printf '%s\\n' "$TEST_ACTIVE" ;;
    'enable --now plexmediaserver.service') TEST_ENABLED=enabled; TEST_ACTIVE=active ;;
    'disable --now plexmediaserver.service') TEST_ENABLED=disabled; TEST_ACTIVE=inactive ;;
    *) return 1 ;;
  esac
}}
{body}
"""
            env = os.environ.copy()
            env.update(TEST_CALLS=str(calls), TEST_FRAGMENT=fragment,
                       TEST_ENABLED=enabled, TEST_ACTIVE=active, TEST_OWNER=owner)
            result = subprocess.run(["bash", "-c", script], env=env, text=True,
                                    capture_output=True, check=False)
            result.calls = calls.read_text().splitlines() if calls.exists() else []
            return result

    def test_enable_start_repeat_and_stop_disable(self):
        result = self.run_shell(
            'ride_plex_server_service_observe | grep -Fx disabled; '
            'ride_plex_server_service_change enabled; '
            'ride_plex_server_service_observe | grep -Fx enabled; '
            'ride_plex_server_service_change enabled; '
            'ride_plex_server_service_change disabled; '
            'ride_plex_server_service_observe | grep -Fx disabled')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.calls.count("enable --now plexmediaserver.service"), 1)
        self.assertEqual(result.calls.count("disable --now plexmediaserver.service"), 1)

    def test_missing_unit_is_disabled_before_package_install(self):
        result = self.run_shell('ride_plex_server_service_observe | grep -Fx disabled', fragment="")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_unowned_unit_is_refused(self):
        result = self.run_shell('ride_plex_server_service_observe', fragment="/etc/systemd/system/plexmediaserver.service")
        self.assertEqual(result.returncode, 42)
        self.assertIn("unowned Plex service unit", result.stderr)

    def test_mixed_active_and_enabled_state_is_refused(self):
        result = self.run_shell('ride_plex_server_service_observe', enabled="enabled", active="inactive")
        self.assertEqual(result.returncode, 42)
        self.assertIn("mixed enabled/active state", result.stderr)

    def test_unit_from_unexpected_rpm_is_refused(self):
        result = self.run_shell('ride_plex_server_service_observe', owner="other-package")
        self.assertEqual(result.returncode, 42)
        self.assertIn("not owned by the plexmediaserver RPM", result.stderr)


if __name__ == "__main__":
    unittest.main()
