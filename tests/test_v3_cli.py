"""Mock provider tests for the public v3 command and journal lifecycle."""

import json
import hashlib
import errno
import os
from pathlib import Path
import pty
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "ride.sh"


def operation(name):
    return {
        "id": f"package.{name}", "kind": "package", "name": name,
        "group": "test", "description": f"Fixture {name}",
        "handler": "dnf-package", "packageName": name, "sourceId": "fedora-rpm",
        "distribution": "installed", "deploymentId": "local-installed", "artifactFormat": "rpm",
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
        catalog.write_text(json.dumps({"schemaVersion": 3, "clientVersion": "3.0.0",
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

    def run_ride_pty(self, *args):
        master, slave = pty.openpty()
        try:
            completed = subprocess.run([str(CLI), *args], env=self.env, stdout=slave,
                                       stderr=subprocess.PIPE, timeout=15, check=False)
        finally:
            os.close(slave)
        chunks = []
        try:
            while True:
                try:
                    chunk = os.read(master, 65536)
                except OSError as error:
                    if error.errno == errno.EIO:
                        break
                    raise
                if not chunk:
                    break
                chunks.append(chunk)
        finally:
            os.close(master)
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        return b"".join(chunks).decode().replace("\r", "")

    def journals(self):
        return [json.loads(path.read_text()) for path in (self.root / "runs").glob("*.json")]

    def test_plan_is_read_only_and_candidate_is_gated(self):
        self.assertIn("package.alpha\tfedora-rpm\tabsent\tinstalled", self.run_ride("plan", "--profile", str(self.profile)).stdout)
        self.assertEqual(self.journals(), [])
        self.run_ride("install", "package.alpha", success=False)
        self.assertEqual(self.journals(), [])
        self.assertFalse((self.root / "packages" / "alpha").exists())

    def test_native_cli_tools_profile_uses_candidate_gate_and_dnf_lifecycle(self):
        identifiers = ("pwgen", "htop", "bat", "ncdu", "ripgrep", "fd-find")
        catalog = json.loads((ROOT / "catalog" / "operations.json").read_text())
        for entry in catalog["operations"]:
            if entry["id"] in {f"package.{name}" for name in identifiers}:
                entry["scope"] = "user"  # Test-only catalog permits mocked, unelevated DNF.
                entry["status"] = "candidate"
                entry.pop("acceptanceEvidence", None)
        guest_catalog = self.root / "native-cli-catalog.json"
        guest_catalog.write_text(json.dumps(catalog))
        self.env["RIDE_CATALOG_PATH"] = str(guest_catalog)
        (self.root / "os-release").write_text("ID=fedora\nVERSION_ID=44\nVARIANT_ID=workstation\n")
        profile = str(ROOT / "profiles" / "cli-tools.json")
        planned = self.run_ride("plan", "--profile", profile).stdout
        for name in identifiers:
            self.assertIn(f"package.{name}\tfedora-rpm\tabsent\tinstalled\tcandidate", planned)
        self.assertEqual(self.journals(), [])
        self.run_ride("apply", "--profile", profile, success=False)
        self.assertFalse(any((self.root / "packages" / name).exists() for name in identifiers))

        self.run_ride("apply", "--profile", profile, "--allow-candidate")
        first = self.journals()[0]
        self.assertEqual([(step["id"], step["result"]) for step in first["steps"]],
                         [(f"package.{name}", "changed") for name in identifiers])
        self.assertTrue(all((self.root / "packages" / name).exists() for name in identifiers))
        self.run_ride("apply", "--profile", profile, "--allow-candidate")
        repeat = next(run for run in self.journals() if run["runId"] != first["runId"])
        self.assertEqual([step["result"] for step in repeat["steps"]],
                         ["unchanged"] * len(identifiers))
        self.run_ride("restore", "--run-id", first["runId"], "--allow-candidate")
        self.assertFalse(any((self.root / "packages" / name).exists() for name in identifiers))

        (self.root / "os-release").write_text("ID=fedora\nVERSION_ID=44\nVARIANT_ID=server\n")
        self.run_ride("plan", "--profile", profile, success=False)

    def test_second_native_rpm_batch_maps_exact_v2_package_names(self):
        names = ("libewf", "exif", "md5deep", "alien")
        catalog = json.loads((ROOT / "catalog" / "operations.json").read_text())
        selected = {f"package.{name}": name for name in names}
        for entry in catalog["operations"]:
            if entry["id"] in selected:
                self.assertEqual(entry["packageName"], selected[entry["id"]])
                entry["scope"] = "user"  # Test-only, unelevated mocked provider.
        path = self.root / "native-rpm-02-catalog.json"
        path.write_text(json.dumps(catalog))
        self.env["RIDE_CATALOG_PATH"] = str(path)
        (self.root / "os-release").write_text("ID=fedora\nVERSION_ID=44\nVARIANT_ID=workstation\n")
        profile = self.root / "native-rpm-02-profile.json"
        profile.write_text(json.dumps({"schemaVersion": 1, "id": "native-rpm-02",
                                       "description": "Test-only package selection",
                                       "operations": [{"id": identifier, "state": "installed"}
                                                      for identifier in selected]}))
        self.run_ride("plan", "--profile", str(profile))
        self.run_ride("apply", "--profile", str(profile))
        first = self.journals()[0]
        self.assertEqual([step["result"] for step in first["steps"]], ["changed"] * len(names))
        self.run_ride("apply", "--profile", str(profile))
        repeat = next(run for run in self.journals() if run["runId"] != first["runId"])
        self.assertEqual([step["result"] for step in repeat["steps"]], ["unchanged"] * len(names))
        self.run_ride("restore", "--run-id", first["runId"])
        self.assertFalse(any((self.root / "packages" / name).exists() for name in names))

    def test_interactive_tables_align_and_pipes_remain_tsv(self):
        if shutil.which("column") is None:
            self.skipTest("column is optional for interactive tables")
        plan_lines = self.run_ride_pty("plan", "--profile", str(self.profile)).splitlines()
        self.assertEqual(plan_lines[0].index("CURRENT"), plan_lines[1].index("absent"))
        self.assertEqual(plan_lines[0].index("DESIRED"), plan_lines[1].index("installed"))
        catalog = self.root / "catalog.json"
        data = json.loads(catalog.read_text())
        data["operations"][1]["id"] = "package.beta-with-long-id"
        catalog.write_text(json.dumps(data))

        lines = self.run_ride_pty("list").splitlines()
        self.assertEqual(lines[0].index("STATUS"), lines[1].index("candidate"))
        self.assertEqual(lines[0].index("STATUS"), lines[2].index("candidate"))
        self.assertEqual(lines[0].index("NAME"), lines[1].rindex("alpha"))
        self.assertEqual(lines[0].index("NAME"), lines[2].rindex("beta"))

        status_lines = self.run_ride_pty("status").splitlines()
        self.assertEqual(status_lines[0].index("OBSERVED"), status_lines[1].index("absent"))
        self.assertEqual(status_lines[0].index("OBSERVED"), status_lines[2].index("absent"))
        search_lines = self.run_ride_pty("search", "fixture").splitlines()
        self.assertEqual(search_lines[0].index("DESCRIPTION"), search_lines[1].index("Fixture alpha"))
        self.assertEqual(search_lines[0].index("DESCRIPTION"), search_lines[2].index("Fixture beta"))

        piped = self.run_ride("list").stdout
        self.assertTrue(piped.startswith("package.alpha\tcandidate\talpha\n"))
        self.assertNotIn("ID\tSTATUS\tNAME", piped)

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

    def test_installed_only_package_refuses_remove_and_restore(self):
        catalog = self.root / "catalog.json"
        data = json.loads(catalog.read_text())
        data["operations"][0]["states"] = ["installed"]
        data["operations"][0]["recovery"] = "none"
        catalog.write_text(json.dumps(data))
        self.run_ride("install", "package.alpha", "--allow-candidate")
        run_id = self.journals()[0]["runId"]
        refused = self.run_ride("remove", "package.alpha", "--allow-candidate", success=False)
        self.assertIn("invalid state absent", refused.stderr)
        refused = self.run_ride("restore", "--run-id", run_id, "--allow-candidate", success=False)
        self.assertIn("exact recovery is unavailable", refused.stderr)
        self.assertTrue((self.root / "packages" / "alpha").exists())

        data["operations"][0]["recovery"] = "remove-new-install"
        catalog.write_text(json.dumps(data))
        refused = self.run_ride("show", "package.alpha", success=False)
        self.assertIn("invalid v3 operation catalog", refused.stderr)

    def test_unknown_and_unsupported_targets_fail_closed(self):
        self.run_ride("show", "package.unknown", success=False)
        self.run_ride("status", "package.unknown", success=False)
        (self.root / "os-release").write_text("ID=debian\nVERSION_ID=13\n")
        self.run_ride("plan", "--profile", str(self.profile), success=False)

    def test_variant_scoped_target_fails_closed_on_other_or_missing_edition(self):
        catalog = self.root / "catalog.json"
        data = json.loads(catalog.read_text())
        for item in data["operations"]:
            item["targets"]["fedora"]["variantIds"] = ["workstation"]
        catalog.write_text(json.dumps(data))
        os_release = self.root / "os-release"
        os_release.write_text('ID=fedora\nVERSION_ID=44\nVARIANT_ID="workstation"\n')
        self.run_ride("plan", "--profile", str(self.profile))

        for variant_line in ("VARIANT_ID=cloud\n", ""):
            os_release.write_text(f"ID=fedora\nVERSION_ID=44\n{variant_line}")
            result = self.run_ride("plan", "--profile", str(self.profile), success=False)
            self.assertIn("operation is not declared", result.stderr)
            shown = json.loads(self.run_ride("show", "package.alpha").stdout)
            self.assertEqual(shown["observedState"], "unsupported")
            self.assertIn("package.alpha\tfedora-rpm\tunsupported", self.run_ride("status").stdout)
            self.run_ride("install", "package.alpha", "--allow-candidate", success=False)
            self.assertFalse((self.root / "packages" / "alpha").exists())

    def test_conflict_detection_ignores_provider_for_other_edition(self):
        catalog = self.root / "catalog.json"
        data = json.loads(catalog.read_text())
        data["operations"][0]["sourceProviders"] = [{
            "sourceId": "alternate-rpm", "handler": "dnf-package", "packageName": "alpha-alt",
            "artifactFormat": "rpm", "status": "candidate", "recovery": "remove-new-install",
            "targets": {"fedora": {"releases": ["44"], "architectures": ["x86_64"],
                                   "variantIds": ["server"]}},
            "sourceUri": "https://example.org/alternate", "verification": "fedora-repository-gpg",
        }]
        catalog.write_text(json.dumps(data))
        (self.root / "packages" / "alpha-alt").write_text("")
        os_release = self.root / "os-release"
        os_release.write_text("ID=fedora\nVERSION_ID=44\nVARIANT_ID=workstation\n")
        self.assertNotIn("conflict:alternate-rpm", self.run_ride("status", "package.alpha").stdout)
        os_release.write_text("ID=fedora\nVERSION_ID=44\nVARIANT_ID=server\n")
        self.assertIn("conflict:alternate-rpm", self.run_ride("status", "package.alpha").stdout)

    def test_target_scope_change_requires_original_catalog_for_restore(self):
        (self.root / "os-release").write_text("ID=fedora\nVERSION_ID=44\nVARIANT_ID=workstation\n")
        catalog = self.root / "catalog.json"
        original = json.loads(catalog.read_text())
        self.run_ride("install", "package.alpha", "--allow-candidate")
        run_id = self.journals()[0]["runId"]

        narrower = json.loads(catalog.read_text())
        narrower["operations"][0]["targets"]["fedora"]["variantIds"] = ["workstation"]
        catalog.write_text(json.dumps(narrower))
        refused = self.run_ride("restore", "--run-id", run_id, "--allow-candidate", success=False)
        self.assertIn("source definition changed", refused.stderr)
        self.assertTrue((self.root / "packages" / "alpha").exists())

        catalog.write_text(json.dumps(original))
        self.run_ride("restore", "--run-id", run_id, "--allow-candidate")
        self.assertFalse((self.root / "packages" / "alpha").exists())

    def test_catalog_cannot_supply_shell_expression(self):
        catalog = self.root / "catalog.json"
        data = json.loads(catalog.read_text())
        marker = self.root / "injected"
        data["operations"][0]["packageName"] = f"$(touch {marker})"
        catalog.write_text(json.dumps(data))
        failed = self.run_ride("show", "package.alpha", success=False)
        self.assertIn("invalid v3 operation catalog", failed.stderr)
        self.assertFalse(marker.exists())

    def test_source_selection_conflict_and_journal(self):
        catalog = self.root / "catalog.json"
        data = json.loads(catalog.read_text())
        data["operations"][0]["sourceProviders"] = [{
            "sourceId": "alternate-rpm", "handler": "dnf-package", "packageName": "alpha-alt",
            "artifactFormat": "rpm",
            "status": "candidate", "recovery": "remove-new-install",
            "targets": {"fedora": {"releases": ["44"], "architectures": ["x86_64"]}},
            "sourceUri": "https://example.org/alternate", "verification": "fedora-repository-gpg",
        }]
        catalog.write_text(json.dumps(data))
        shown = json.loads(self.run_ride("show", "package.alpha", "--source", "alternate-rpm").stdout)
        self.assertEqual(shown["sourceId"], "alternate-rpm")
        self.assertEqual(shown["availableSources"], ["fedora-rpm", "alternate-rpm"])
        alternate_profile = json.loads(self.profile.read_text())
        alternate_profile["operations"] = [{"id": "package.alpha", "state": "installed", "source": "alternate-rpm"}]
        self.profile.write_text(json.dumps(alternate_profile))
        self.assertIn("package.alpha\talternate-rpm\tabsent\tinstalled", self.run_ride("plan", "--profile", str(self.profile)).stdout)
        self.run_ride("install", "package.alpha", "--source", "alternate-rpm", "--allow-candidate")
        self.assertTrue((self.root / "packages" / "alpha-alt").exists())
        journal = self.journals()[0]
        self.assertEqual(journal["schemaVersion"], 2)
        self.assertEqual(journal["steps"][0]["sourceId"], "alternate-rpm")
        self.assertEqual(journal["steps"][0]["distribution"], "installed")
        self.assertEqual(journal["steps"][0]["deploymentId"], "local-installed")
        self.assertEqual(journal["steps"][0]["sourceSignatureVersion"], 2)
        self.assertIn("conflict:alternate-rpm", self.run_ride("status", "package.alpha").stdout)
        refused = self.run_ride("install", "package.alpha", "--allow-candidate", success=False)
        self.assertIn("another source is installed", refused.stderr)
        self.assertFalse((self.root / "packages" / "alpha").exists())
        data["operations"][0]["sourceProviders"][0]["packageName"] = "different-package"
        catalog.write_text(json.dumps(data))
        refused = self.run_ride("restore", "--run-id", journal["runId"], "--allow-candidate", success=False)
        self.assertIn("source definition changed", refused.stderr)
        data["operations"][0]["sourceProviders"][0]["packageName"] = "alpha-alt"
        catalog.write_text(json.dumps(data))
        self.run_ride("restore", "--run-id", journal["runId"], "--allow-candidate")
        self.assertFalse((self.root / "packages" / "alpha-alt").exists())
        self.run_ride("apply", "--profile", str(self.profile), "--allow-candidate")
        self.assertTrue((self.root / "packages" / "alpha-alt").exists())
        self.run_ride("remove", "--profile", str(self.profile), "--allow-candidate")
        self.assertFalse((self.root / "packages" / "alpha-alt").exists())

        data["operations"][0]["sourceProviders"][0]["packageName"] = "alpha"
        catalog.write_text(json.dumps(data))
        refused = self.run_ride("show", "package.alpha", success=False)
        self.assertIn("invalid v3 operation catalog", refused.stderr)

    def test_schema_one_run_restores_with_earlier_source_signature(self):
        self.run_ride("install", "package.alpha", "--allow-candidate")
        journal_path = next((self.root / "runs").glob("*.json"))
        journal = json.loads(journal_path.read_text())
        entry = operation("alpha")
        old_fields = {key: entry.get(key) for key in (
            "id", "sourceId", "handler", "packageName", "serviceName", "scope",
            "sourceUri", "verification", "targets", "recovery",
        )}
        encoded = (json.dumps(old_fields, sort_keys=True, separators=(",", ":")) + "\n").encode()
        journal["schemaVersion"] = 1
        step = journal["steps"][0]
        step["sourceSignature"] = hashlib.sha256(encoded).hexdigest()
        step.pop("sourceSignatureVersion")
        step.pop("distribution")
        step.pop("deploymentId")
        step.pop("scope")
        journal_path.write_text(json.dumps(journal))
        self.run_ride("restore", "--run-id", journal["runId"], "--allow-candidate")
        self.assertFalse((self.root / "packages" / "alpha").exists())

    def test_gnome_boolean_setting_journals_and_restores_prior_state(self):
        catalog = json.loads((ROOT / "catalog" / "operations.json").read_text())
        entry = next(row for row in catalog["operations"] if row["id"] == "setting.gnome-clock-date")
        (self.root / "catalog.json").write_text(json.dumps({
            "schemaVersion": 3, "clientVersion": "3.0.0", "operations": [entry],
        }))
        (self.root / "os-release").write_text("ID=fedora\nVERSION_ID=44\nVARIANT_ID=workstation\n")
        settings = self.root / "settings"
        settings.mkdir()
        value = settings / "clock-show-date"
        value.write_text("false\n")
        command = self.root / "bin" / "gsettings"
        command.write_text("""#!/bin/sh
case "$1" in
  get) cat "$RIDE_TEST_SETTINGS/$3" ;;
  writable) if [ "${RIDE_TEST_LOCK:-0}" = 1 ]; then printf 'false\\n'; else printf 'true\\n'; fi ;;
  set) printf '%s\\n' "$4" > "$RIDE_TEST_SETTINGS/$3" ;;
  *) exit 2 ;;
esac
""")
        command.chmod(0o755)
        self.env["RIDE_TEST_SETTINGS"] = str(settings)
        self.env["DBUS_SESSION_BUS_ADDRESS"] = "unix:path=/tmp/ride-test-bus"
        self.profile.write_text(json.dumps({
            "schemaVersion": 1, "id": "gnome-test", "description": "Test setting",
            "operations": [{"id": "setting.gnome-clock-date", "state": "enabled"}],
        }))
        planned = self.run_ride("plan", "--profile", str(self.profile)).stdout
        self.assertIn("disabled\t", planned)
        self.run_ride("set", "setting.gnome-clock-date", "--state", "enabled", success=False)
        self.assertEqual(value.read_text(), "false\n")
        changed = self.run_ride("set", "setting.gnome-clock-date", "--state", "enabled",
                                "--allow-candidate")
        self.assertEqual(value.read_text(), "true\n")
        journal = next(row for row in self.journals() if row["runId"] in changed.stdout)
        self.assertEqual(journal["steps"][0]["observedBefore"], "disabled")
        self.assertEqual(journal["steps"][0]["observedAfter"], "enabled")
        self.run_ride("restore", "--run-id", journal["runId"], "--allow-candidate")
        self.assertEqual(value.read_text(), "false\n")
        self.env["RIDE_TEST_LOCK"] = "1"
        locked = self.run_ride("set", "setting.gnome-clock-date", "--state", "enabled",
                               "--allow-candidate", success=False)
        self.assertIn("GNOME setting is locked", locked.stderr)
        self.assertEqual(value.read_text(), "false\n")

    def test_ibus_hotkey_restores_custom_and_unset_values(self):
        catalog = json.loads((ROOT / "catalog" / "operations.json").read_text())
        entry = next(row for row in catalog["operations"] if row["id"] == "setting.ibus-emoji-hotkey")
        (self.root / "catalog.json").write_text(json.dumps({
            "schemaVersion": 3, "clientVersion": "3.0.0", "operations": [entry],
        }))
        (self.root / "os-release").write_text("ID=fedora\nVERSION_ID=44\nVARIANT_ID=workstation\n")
        override = self.root / "ibus-override"
        override.write_text("['<Alt>F8']\n")
        (self.root / "bin" / "dconf").write_text("""#!/bin/sh
if [ "$1" = read ] && [ "$2" = /desktop/ibus/panel/emoji/hotkey ]; then
  [ ! -f "$RIDE_TEST_IBUS_OVERRIDE" ] || cat "$RIDE_TEST_IBUS_OVERRIDE"
else
  exit 2
fi
""")
        (self.root / "bin" / "gsettings").write_text("""#!/bin/sh
case "$1" in
  get)
    [ "${RIDE_TEST_IBUS_GET_FAIL:-0}" != 1 ] || exit 17
    if [ -f "$RIDE_TEST_IBUS_OVERRIDE" ]; then cat "$RIDE_TEST_IBUS_OVERRIDE"; else printf "['<Super>period']\\n"; fi ;;
  writable) if [ "${RIDE_TEST_IBUS_LOCK:-0}" = 1 ]; then echo false; else echo true; fi ;;
  set)
    printf '%s\\n' "$4" > "$RIDE_TEST_IBUS_OVERRIDE"
    if [ "${RIDE_TEST_IBUS_FAIL_ONCE:-0}" = 1 ] && [ ! -f "$RIDE_TEST_IBUS_FAILURE_MARKER" ]; then
      touch "$RIDE_TEST_IBUS_FAILURE_MARKER"
      exit 13
    fi ;;
  reset) rm -f "$RIDE_TEST_IBUS_OVERRIDE" ;;
  *) exit 2 ;;
esac
""")
        for name in ("dconf", "gsettings"):
            (self.root / "bin" / name).chmod(0o755)
        self.env["RIDE_TEST_IBUS_OVERRIDE"] = str(override)
        self.env["RIDE_TEST_IBUS_FAILURE_MARKER"] = str(self.root / "failure-marker")
        self.env["DBUS_SESSION_BUS_ADDRESS"] = "unix:path=/tmp/ride-test-bus"
        self.profile.write_text(json.dumps({
            "schemaVersion": 1, "id": "ibus-test", "description": "Test setting",
            "operations": [{"id": "setting.ibus-emoji-hotkey", "state": "enabled"}],
        }))

        planned = self.run_ride("plan", "--profile", str(self.profile)).stdout
        self.assertIn("setting.ibus-emoji-hotkey", planned)
        self.run_ride("apply", "--profile", str(self.profile), success=False)
        first = self.run_ride("apply", "--profile", str(self.profile), "--allow-candidate")
        changed = next(row for row in self.journals() if row["runId"] in first.stdout)
        self.assertTrue(changed["steps"][0]["observedBefore"].startswith("user:"))
        self.assertEqual(override.read_text(), "['<Control><Alt><Shift>e']\n")
        repeat = self.run_ride("apply", "--profile", str(self.profile), "--allow-candidate")
        self.assertEqual(next(row for row in self.journals() if row["runId"] in repeat.stdout)
                         ["steps"][0]["result"], "unchanged")
        override.write_text("['<Alt>F9']\n")
        conflict = self.run_ride("restore", "--run-id", changed["runId"],
                                 "--allow-candidate", success=False)
        self.assertIn("restore conflict", conflict.stderr)
        self.assertEqual(override.read_text(), "['<Alt>F9']\n")
        override.write_text("['<Control><Alt><Shift>e']\n")
        self.run_ride("restore", "--run-id", changed["runId"], "--dry-run")
        self.run_ride("restore", "--run-id", changed["runId"], "--allow-candidate")
        self.assertEqual(override.read_text(), "['<Alt>F8']\n")

        override.unlink()
        second = self.run_ride("set", "setting.ibus-emoji-hotkey", "--state", "enabled",
                               "--allow-candidate")
        second_run = next(row for row in self.journals() if row["runId"] in second.stdout)
        self.assertEqual(second_run["steps"][0]["observedBefore"], "unset")
        self.run_ride("restore", "--run-id", second_run["runId"], "--allow-candidate")
        self.assertFalse(override.exists())

        override.write_text("['<Alt>F8']\n")
        self.env["RIDE_TEST_IBUS_FAIL_ONCE"] = "1"
        self.run_ride("set", "setting.ibus-emoji-hotkey", "--state", "enabled",
                      "--allow-candidate", success=False)
        self.assertEqual(override.read_text(), "['<Alt>F8']\n")
        del self.env["RIDE_TEST_IBUS_FAIL_ONCE"]
        self.env["RIDE_TEST_IBUS_LOCK"] = "1"
        locked = self.run_ride("set", "setting.ibus-emoji-hotkey", "--state", "enabled",
                               "--allow-candidate", success=False)
        self.assertIn("iBus hotkey is locked", locked.stderr)
        self.assertEqual(override.read_text(), "['<Alt>F8']\n")
        del self.env["RIDE_TEST_IBUS_LOCK"]
        self.env["RIDE_TEST_IBUS_GET_FAIL"] = "1"
        unreadable = self.run_ride("set", "setting.ibus-emoji-hotkey", "--state", "enabled",
                                   "--allow-candidate", success=False)
        self.assertIn("cannot observe current state", unreadable.stderr)
        self.assertEqual(override.read_text(), "['<Alt>F8']\n")

    def test_profile_source_and_unknown_source(self):
        profile = json.loads(self.profile.read_text())
        profile["operations"][0]["source"] = "not-declared"
        self.profile.write_text(json.dumps(profile))
        refused = self.run_ride("plan", "--profile", str(self.profile), success=False)
        self.assertIn("unknown source", refused.stderr)


if __name__ == "__main__":
    unittest.main()
