"""Mocked ownership and lifecycle checks for the Fedora Glances Web unit."""

from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROVIDER = ROOT / "lib/v3/providers.sh"


class GlancesWebServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ride-glances-web-")
        self.addCleanup(self.tmp.cleanup)
        self.state = Path(self.tmp.name) / "unit-state"
        self.state.write_text("disabled inactive\n", encoding="utf-8")
        self.dropin = Path(self.tmp.name) / "systemd/glances.service.d/60-ride-loopback.conf"

    def shell(self, body, *, fragment="/usr/lib/systemd/system/glances.service"):
        script = f'''set -euo pipefail
source {PROVIDER}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 1; }}
ride_error() {{ ride_die "$@"; }}
ride_require_command() {{ :; }}
ride_glances_web_service_dropin() {{ printf '%s\\n' {str(self.dropin)!r}; }}
systemctl() {{
  case "$*" in
    'show --property=FragmentPath --value glances.service') printf '%s\\n' {fragment!r};;
    'is-enabled glances.service') awk '{{print $1}}' {str(self.state)!r};;
    'is-active glances.service') awk '{{print $2}}' {str(self.state)!r};;
    'enable --now glances.service') printf 'enabled active\\n' > {str(self.state)!r};;
    'disable --now glances.service') printf 'disabled inactive\\n' > {str(self.state)!r};;
    'daemon-reload') :;;
    *) return 8;;
  esac
}}
rpm() {{
  [[ "$1" == -qf && "$2" == --qf && "$3" == '%{{NAME}}' && "$4" == /usr/lib/systemd/system/glances.service ]] || return 8
  printf 'glances\\n'
}}
{body}
'''
        return subprocess.run(["bash", "-c", script], text=True, capture_output=True)

    def test_enable_disable_and_reapply_are_idempotent(self):
        result = self.shell(f'''
ride_glances_web_service_observe | grep -Fx disabled
ride_glances_web_service_change enabled
ride_glances_web_service_observe | grep -Fx enabled
grep -F -- '-B 127.0.0.1' {str(self.dropin)!r}
ride_glances_web_service_change enabled
ride_glances_web_service_change disabled
ride_glances_web_service_observe | grep -Fx disabled
test ! -e {str(self.dropin)!r}
''')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_refuses_unowned_unit_override(self):
        result = self.shell('ride_glances_web_service_observe', fragment="/etc/systemd/system/glances.service")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unowned Glances unit", result.stderr)

    def test_refuses_mixed_enabled_and_active_state(self):
        self.state.write_text("enabled inactive\n", encoding="utf-8")
        self.dropin.parent.mkdir(parents=True)
        self.dropin.write_text("[Service]\nExecStart=\nExecStart=/usr/bin/glances -w -B 127.0.0.1\n", encoding="utf-8")
        result = self.shell('ride_glances_web_service_observe')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("mixed enabled/active state", result.stderr)


if __name__ == "__main__":
    unittest.main()
