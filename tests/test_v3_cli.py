"""Mock provider tests for the public v3 command and journal lifecycle."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "ride.sh"


def operation(name):
    return {
        "id": f"package.{name}", "kind": "package", "name": name,
        "group": "test", "description": f"Fixture {name}",
        "handler": "dnf-package", "packageName": name,
        "states": ["installed", "absent"], "scope": "user",
        "status": "candidate", "recovery": "remove-new-install",
        "targets": {"fedora": {"releases": ["44"], "architectures": ["x86_64"]}},
        "productId": name, "productUri": "https://example.org/product",
        "license": "MIT", "licenseUri": "https://example.org/license",
        "sourceUri": "https://example.org/source", "verification": "fedora-repository-gpg",
    }


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        binary = self.root / "bin"
        binary.mkdir()
        for name, source in {
            "rpm": """#!/bin/sh
test -f "$RIDE_TEST_PACKAGES/$3"
""",
            "dnf": """#!/bin/sh
for arg do last=$arg; done
case " $* " in
  *' install '*)
    [ "$last" != "beta" ] || [ "${RIDE_TEST_FAIL_BETA:-0}" != 1 ] || exit 13
    touch "$RIDE_TEST_PACKAGES/$last" ;;
  *' remove '*) rm -f "$RIDE_TEST_PACKAGES/$last" ;;
  *) exit 3 ;;
esac
""",
        }.items():
            path = binary / name
            path.write_text(source)
            path.chmod(0o755)
        packages = self.root / "packages"
        packages.mkdir()
        os_release = self.root / "os-release"
        os_release.write_text("ID=fedora\nVERSION_ID=44\n")
        catalog = self.root / "catalog.json"
        catalog.write_text(json.dumps({"schemaVersion": 1, "clientVersion": "3.0.0",
                                       "operations": [operation("alpha"), operation("beta")]}))
        self.profile = self.root / "profile.json"
        self.profile.write_text(json.dumps({"schemaVersion": 1, "id": "test",
                                            "description": "Fixture",
                                            "operations": [{"id": "package.alpha", "state": "installed"},
                                                           {"id": "package.beta", "state": "installed"}]}))
        self.env = os.environ.copy()
        self.env.update({
            "PATH": f"{binary}:{self.env['PATH']}",
            "RIDE_TEST_MODE": "1", "RIDE_OS_RELEASE_FILE": str(os_release),
            "RIDE_CATALOG_PATH": str(catalog), "RIDE_TEST_PACKAGES": str(packages),
            "RIDE_STATE_DIR": str(self.root / "runs"),
            "RIDE_CACHE_DIR": str(self.root / "cache"),
        })

    def run_ride(self, *args, success=True):
        completed = subprocess.run([str(CLI), *args], env=self.env, text=True,
                                   capture_output=True, check=False)
        if success:
            self.assertEqual(completed.returncode, 0, completed.stderr)
        else:
            self.assertNotEqual(completed.returncode, 0, completed.stdout)
        return completed

    def journals(self):
        return [json.loads(path.read_text()) for path in (self.root / "runs").glob("*.json")]

    def test_plan_is_read_only_and_candidate_is_gated(self):
        self.assertIn("package.alpha\tabsent\tinstalled", self.run_ride("plan", "--profile", str(self.profile)).stdout)
        self.assertEqual(self.journals(), [])
        self.run_ride("install", "package.alpha", success=False)
        self.assertEqual(self.journals(), [])
        self.assertFalse((self.root / "packages" / "alpha").exists())

    def test_apply_repeat_restore_once(self):
        self.run_ride("apply", "--profile", str(self.profile), "--allow-candidate")
        first = self.journals()[0]
        self.assertEqual(first["status"], "complete")
        self.assertEqual([step["result"] for step in first["steps"]], ["changed", "changed"])
        self.run_ride("apply", "--profile", str(self.profile), "--allow-candidate")
        self.assertEqual(sorted(step["result"] for run in self.journals() for step in run["steps"]),
                         ["changed", "changed", "unchanged", "unchanged"])
        self.run_ride("restore", "--run-id", first["runId"], "--dry-run")
        self.run_ride("restore", "--run-id", first["runId"], "--allow-candidate")
        self.assertFalse((self.root / "packages" / "alpha").exists())
        self.assertFalse((self.root / "packages" / "beta").exists())
        result = self.run_ride("restore", "--run-id", first["runId"], "--allow-candidate", success=False)
        self.assertIn("already been restored", result.stderr)

    def test_partial_failure_is_recorded(self):
        self.env["RIDE_TEST_FAIL_BETA"] = "1"
        result = self.run_ride("apply", "--profile", str(self.profile), "--allow-candidate", success=False)
        self.assertIn("change failed", result.stderr)
        run = self.journals()[0]
        self.assertEqual(run["status"], "failed")
        self.assertEqual([step["result"] for step in run["steps"]], ["changed", "failed"])
        self.assertTrue((self.root / "packages" / "alpha").exists())

    def test_remove_cannot_claim_exact_restore(self):
        (self.root / "packages" / "alpha").write_text("")
        self.run_ride("remove", "package.alpha", "--allow-candidate")
        run = self.journals()[0]
        result = self.run_ride("restore", "--run-id", run["runId"], "--allow-candidate", success=False)
        self.assertIn("exact recovery is unavailable", result.stderr)

    def test_unknown_and_unsupported_targets_fail_closed(self):
        self.run_ride("show", "package.unknown", success=False)
        (self.root / "os-release").write_text("ID=debian\nVERSION_ID=13\n")
        self.run_ride("plan", "--profile", str(self.profile), success=False)

    def test_catalog_cannot_supply_shell_expression(self):
        catalog = self.root / "catalog.json"
        data = json.loads(catalog.read_text())
        marker = self.root / "injected"
        data["operations"][0]["packageName"] = f"$(touch {marker})"
        catalog.write_text(json.dumps(data))
        failed = self.run_ride("show", "package.alpha", success=False)
        self.assertIn("invalid v3 operation catalog", failed.stderr)
        self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
