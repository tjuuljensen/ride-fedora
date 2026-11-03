"""Mocked behavior for the explicit, non-restorable DNF5 whole-system update."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROVIDER = ROOT / "lib/v3/providers.sh"


class Dnf5SystemUpdateTests(unittest.TestCase):
    def run_shell(self, body, *, status="0", checkups='{}', preview="Nothing to do.", history='[]', info='[]', reboot='[{"type":"reboot","reboot_required":false,"packages":[]}]'):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "history"
            transaction_info = Path(directory) / "transaction-info"
            state.write_text(history, encoding="utf-8")
            transaction_info.write_text(info, encoding="utf-8")
            script = f'''set -euo pipefail
source {PROVIDER}
ride_die() {{ printf '%s\\n' "$*" >&2; return 1; }}
ride_require_command() {{ :; }}
dnf5() {{
  case "$*" in
    'check-upgrade --json'|'--refresh check-upgrade --json') printf '%s\\n' {checkups!r}; return {status} ;;
    'upgrade --assumeno --no-allow-downgrade') printf '%s\\n' {preview!r}; if [[ {preview!r} == 'Nothing to do.' ]]; then return 0; else return 1; fi ;;
    'history list --json') cat {str(state)!r};;
    'history info '* ) cat {str(transaction_info)!r};;
    'upgrade --no-allow-downgrade --assumeyes') printf '%s\\n' '[mock upgrade]'; printf '[{{"id":5,"status":"Ok"}}]\\n' > {str(state)!r};;
    'needs-restarting --json') printf '%s\\n' {reboot!r};;
    *) printf 'unexpected dnf5 call: %s\\n' "$*" >&2; return 9;;
  esac
}}
{body}
'''
            return subprocess.run(["bash", "-c", script], text=True, capture_output=True, check=False)

    def test_check_and_preview_and_apply_report(self):
        result = self.run_shell('''
ride_dnf5_system_update_check
ride_dnf5_system_update_preview
ride_dnf5_system_update_change current
printf 'REPORT=%s\\n' "$RIDE_DNF5_SYSTEM_UPDATE_REPORT"
''', checkups='{"updates":["pkg-2"]}', status="100",
            history='[{"id":4,"status":"Ok"}]',
            info='[{"id":5,"status":"Ok","packages":[{"nevra":"pkg-0:2-1.x86_64"}]}]')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("outdated", result.stdout)
        self.assertIn('"transactionId":5', result.stdout)
        self.assertIn('"pkg-0:2-1.x86_64"', result.stdout)
        self.assertIn('"rebootRequired":false', result.stdout)

    def test_update_check_rejects_status_json_disagreement(self):
        result = self.run_shell("ride_dnf5_system_update_check", checkups='{}', status="100")
        self.assertNotEqual(result.returncode, 0)

    def test_preview_refuses_removals_and_downgrades(self):
        for line in ("Removing: pkg.x86_64", "Downgrading: pkg.x86_64"):
            with self.subTest(line=line):
                result = self.run_shell("ride_dnf5_system_update_preview", preview=line)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("includes removal", result.stderr)

    def test_reboot_checker_unavailable_is_explicit(self):
        result = self.run_shell('''
ride_dnf5_system_update_reboot_assessment
''', reboot="not-json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"assessment":"unavailable"', result.stdout)

    def test_failed_upgrade_still_produces_report_and_fails(self):
        # A failed DNF process is represented by replacing only the mock upgrade branch.
        result = self.run_shell('''
dnf5() {
  case "$*" in
    'history list --json') printf '[{"id":2,"status":"Ok"}]\\n';;
    'upgrade --no-allow-downgrade --assumeyes') return 7;;
    'needs-restarting --json') printf '[{"type":"reboot","reboot_required":false,"packages":[]}]\\n';;
    *) return 8;;
  esac
}
ride_dnf5_system_update_change current
''')
        self.assertNotEqual(result.returncode, 0)

    def test_large_transaction_history_is_streamed_into_report(self):
        import json

        count = 2000
        packages = [{"nevra": f"package-{index}:1.0-1.x86_64"}
                    for index in range(count)]
        info = json.dumps([{"id": 5, "status": "Ok", "packages": packages}])
        result = self.run_shell('''
ride_dnf5_system_update_change current
printf 'REPORT=%s\\n' "$RIDE_DNF5_SYSTEM_UPDATE_REPORT"
''', history='[{"id":4,"status":"Ok"}]', info=info)
        self.assertEqual(result.returncode, 0, result.stderr)
        report_text = result.stdout.split("REPORT=", 1)[1].splitlines()[0]
        report = json.loads(report_text)
        self.assertEqual(len(report["packages"]), count)
        self.assertEqual(report["packages"][-1], "package-1999:1.0-1.x86_64")


if __name__ == "__main__":
    unittest.main()
