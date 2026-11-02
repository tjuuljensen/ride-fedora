"""Focused tests for non-reversible, fixed-name DNF5 package updates."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent


class DnfPackageSetUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ride-dnf5-update-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        binary = self.root / "bin"
        binary.mkdir()
        (binary / "rpm").write_text("""#!/bin/sh
printf '%s\\n' "$*" >> "$RIDE_TEST_RPM_LOG"
case ":${RIDE_TEST_INSTALLED:-}:" in *":$3:"*) exit 0 ;; esac
exit 1
""")
        (binary / "dnf5").write_text("""#!/bin/sh
printf '%s\\n' "$*" >> "$RIDE_TEST_DNF5_LOG"
case " $* " in
  *' check-upgrade '*)
    printf '%s\\n' "$RIDE_TEST_UPDATE_JSON"
    exit "${RIDE_TEST_UPDATE_STATUS:-0}" ;;
  *' upgrade '*)
    case " $* " in *' --assumeno '*)
      printf '%s\\n' "${RIDE_TEST_PREVIEW:-Operation aborted.}"
      exit "${RIDE_TEST_PREVIEW_STATUS:-1}" ;;
    esac
    printf '%s\\n' "${RIDE_TEST_APPLY_OUTPUT:-Transaction complete.}"
    exit "${RIDE_TEST_APPLY_STATUS:-0}" ;;
  *) exit 2 ;;
esac
""")
        for executable in binary.iterdir():
            executable.chmod(0o755)
        self.env = os.environ.copy()
        self.env.update({
            "PATH": f"{binary}:{os.environ['PATH']}",
            "RIDE_TEST_INSTALLED": "alpha:beta",
            "RIDE_TEST_RPM_LOG": str(self.root / "rpm.log"),
            "RIDE_TEST_DNF5_LOG": str(self.root / "dnf5.log"),
        })
        self.entry = json.dumps({
            "id": "system.update-multimedia-codecs",
            "packageNames": ["alpha", "beta", "absent"],
        })

    def run_shell(self, body, *, success=True):
        script = f"""
source {ROOT / 'lib/v3/common.sh'}
source {ROOT / 'lib/v3/providers.sh'}
entry=$(cat <<'RIDE_ENTRY'
{self.entry}
RIDE_ENTRY
)
{body}
"""
        result = subprocess.run(["bash", "-c", script], env=self.env, text=True,
                                capture_output=True, check=False)
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def test_observe_updates_uses_only_installed_names(self):
        self.env["RIDE_TEST_UPDATE_STATUS"] = "0"
        self.env["RIDE_TEST_UPDATE_JSON"] = '{"Upgrading":[{"name":"alpha"}]}'
        result = self.run_shell('ride_dnf5_package_set_update_observe "$entry"')
        self.assertEqual(result.stdout.strip(), "outdated")
        invocation = (self.root / "dnf5.log").read_text()
        self.assertIn("check-upgrade --json alpha beta", invocation)
        self.assertNotIn("--refresh", invocation)
        self.assertNotIn("absent", invocation)

    def test_observe_current_update_set(self):
        self.env["RIDE_TEST_UPDATE_STATUS"] = "0"
        self.env["RIDE_TEST_UPDATE_JSON"] = '{"Upgrading":[]}'
        result = self.run_shell('ride_dnf5_package_set_update_observe "$entry"')
        self.assertEqual(result.stdout.strip(), "current")

    def test_observe_rejects_dnf_failure_and_empty_json_with_update_exit(self):
        self.env["RIDE_TEST_UPDATE_STATUS"] = "1"
        self.env["RIDE_TEST_UPDATE_JSON"] = "metadata error"
        failed = self.run_shell('ride_dnf5_package_set_update_observe "$entry"', success=False)
        self.assertIn("DNF5 update check failed", failed.stderr)

        self.env["RIDE_TEST_UPDATE_STATUS"] = "100"
        self.env["RIDE_TEST_UPDATE_JSON"] = '{"Upgrading":[]}'
        mismatch = self.run_shell('ride_dnf5_package_set_update_observe "$entry"', success=False)
        self.assertIn("exit status disagrees", mismatch.stderr)

    def test_observe_reports_empty_fixed_set(self):
        self.env["RIDE_TEST_INSTALLED"] = ""
        result = self.run_shell('ride_dnf5_package_set_update_observe "$entry"')
        self.assertEqual(result.stdout.strip(), "no-packages")
        self.assertFalse((self.root / "dnf5.log").exists())

    def test_change_updates_only_installed_names_without_downgrade_flag(self):
        self.run_shell('ride_dnf5_package_set_update_change "$entry" current')
        invocation = (self.root / "dnf5.log").read_text().strip()
        self.assertEqual(invocation, "upgrade --no-allow-downgrade --assumeyes alpha beta")

    def test_preview_accepts_expected_assumeno_and_rejects_removal(self):
        self.env["RIDE_TEST_PREVIEW"] = "Upgrading:\\n alpha 1 -> 2\\nOperation aborted."
        preview = self.run_shell('ride_dnf5_package_set_update_preview "$entry"')
        self.assertIn("transaction preview", preview.stdout)

        self.env["RIDE_TEST_PREVIEW"] = "Removing:\\n alpha\\nOperation aborted."
        refused = self.run_shell('ride_dnf5_package_set_update_preview "$entry"', success=False)
        self.assertIn("would remove or downgrade", refused.stderr)


if __name__ == "__main__":
    unittest.main()
