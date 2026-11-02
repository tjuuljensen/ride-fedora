"""Private static hostname selection and exact prior-name restoration tests."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
PROVIDER = ROOT / "lib/v3/providers.sh"
ENTRY = '{"id":"setting.hostname","selectedValue":"ride-test-host.example","handler":"system-hostname"}'


class SystemHostnameTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ride-hostname-test-")
        self.addCleanup(self.tmp.cleanup)
        self.state = Path(self.tmp.name) / "static-hostname"
        self.state.write_text("previous-host.example\n", encoding="utf-8")

    def shell(self, body):
        script = f'''set -euo pipefail
source {PROVIDER}
ride_require_command() {{ command -v "$1" >/dev/null; }}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 1; }}
hostnamectl() {{
  if [[ "$1" == --static ]]; then cat "$TEST_STATE"; return; fi
  if [[ "$1" == set-hostname && "$2" == --static ]]; then printf '%s\\n' "$3" > "$TEST_STATE"; return; fi
  return 2
}}
entry='{ENTRY}'
{body}
'''
        env = os.environ.copy()
        env["TEST_STATE"] = str(self.state)
        return subprocess.run(["bash", "-c", script], env=env, text=True,
                              capture_output=True, check=False)

    def test_apply_repeat_and_exact_prior_hostname_restore(self):
        result = self.shell('''ride_system_hostname_observe "$entry"
ride_system_hostname_change "$entry" configured
ride_system_hostname_observe "$entry"
ride_system_hostname_change "$entry" hostname:previous-host.example
ride_system_hostname_observe "$entry"''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [
            "hostname:previous-host.example", "configured", "hostname:previous-host.example"])
        self.assertEqual(self.state.read_text().strip(), "previous-host.example")

    def test_hostname_validation_rejects_invalid_or_oversized_values(self):
        for value in ("", "-starts-wrong", "ends-wrong-", "has space", "has_underscore", ".leading", "double..dot", "x" * 65):
            with self.subTest(value=value):
                result = self.shell(f"ride_system_hostname_value {value!r}")
                self.assertNotEqual(result.returncode, 0, value)
        self.assertEqual(self.shell("ride_system_hostname_value host.example").returncode, 0)

    def test_cli_value_validation_is_private_and_explicit(self):
        os_release = Path(self.tmp.name) / "os-release"
        os_release.write_text("ID=fedora\nVERSION_ID=44\nVARIANT_ID=workstation\n", encoding="utf-8")
        env = os.environ.copy()
        env.update(RIDE_TEST_MODE="1", RIDE_OS_RELEASE_FILE=str(os_release))
        good = subprocess.run([str(ROOT / "ride.sh"), "set", "setting.hostname", "--state", "configured", "--value", "pilot-node.example", "--dry-run"], env=env, text=True, capture_output=True, check=False)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertIn("configured:pilot-node.example", good.stdout)
        bad = subprocess.run([str(ROOT / "ride.sh"), "set", "setting.hostname", "--state", "configured", "--value", "invalid host", "--dry-run"], env=env, text=True, capture_output=True, check=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("invalid value", bad.stderr)


if __name__ == "__main__":
    unittest.main()
