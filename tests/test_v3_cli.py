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
            "rpmkeys": """#!/bin/sh
printf '%s\\n' "$*" >> "$RIDE_TEST_RPMKEYS_LOG"
[ "${RIDE_TEST_RPMKEYS_FAIL:-0}" != 1 ]
""",
            "dnf": """#!/bin/sh
printf '%s\\n' "$*" >> "$RIDE_TEST_DNF_LOG"
for arg do last=$arg; done
case " $* " in
  *' download '*)
    destination=
    previous=
    for arg do
      if [ "$previous" = --destdir ]; then destination=$arg; fi
      previous=$arg
    done
    mkdir -p "$destination"
    : > "$destination/$last-1.0-1.fc44.x86_64.rpm" ;;
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
            "RIDE_TEST_DNF_LOG": str(self.root / "dnf.log"),
            "RIDE_TEST_RPMKEYS_LOG": str(self.root / "rpmkeys.log"),
            "RIDE_STATE_DIR": str(self.root / "runs"),
            "RIDE_CACHE_DIR": str(self.root / "cache"),
        })

    def run_ride(self, *args, success=True, input_text=None):
        completed = subprocess.run([str(CLI), *args], env=self.env, input=input_text, text=True,
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

    def test_blocked_operation_cannot_be_enabled_with_candidate_override(self):
        catalog = json.loads((ROOT / "catalog" / "operations.json").read_text())
        catalog["operations"] = [entry for entry in catalog["operations"]
                                 if entry["id"] == "setting.firefox-addons"]
        catalog["operations"][0]["status"] = "blocked"
        path = self.root / "blocked-catalog.json"
        path.write_text(json.dumps(catalog))
        self.env["RIDE_CATALOG_PATH"] = str(path)
        (self.root / "os-release").write_text(
            "ID=fedora\nVERSION_ID=44\nVARIANT_ID=workstation\n", encoding="utf-8")
        blocked = self.run_ride("set", "setting.firefox-addons", "--state", "configured",
                                "--allow-candidate", success=False)
        self.assertIn("operation is blocked pending required safety and recovery evidence",
                      blocked.stderr)
        self.assertEqual(self.journals(), [])

    def test_update_command_plans_system_operation_without_mutation(self):
        catalog = json.loads((ROOT / "catalog" / "operations.json").read_text())
        path = self.root / "system-update-catalog.json"
        path.write_text(json.dumps(catalog))
        self.env["RIDE_CATALOG_PATH"] = str(path)
        (self.root / "os-release").write_text(
            "ID=fedora\nVERSION_ID=44\nVARIANT_ID=workstation\n", encoding="utf-8")
        dnf5 = Path(self.env["PATH"].split(":", 1)[0]) / "dnf5"
        dnf5.write_text("#!/bin/sh\nprintf '%s\\n' '{}'\n")
        dnf5.chmod(0o755)
        planned = self.run_ride("update", "system.update-all-packages", "--dry-run")
        self.assertIn("system.update-all-packages", planned.stdout)
        self.assertIn("current", planned.stdout)
        self.assertEqual(self.journals(), [])
        invalid = self.run_ride("set", "system.update-all-packages", "--state", "current", success=False)
        self.assertIn("set requires a setting ID", invalid.stderr)

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

    def test_rpmfusion_codec_uses_only_declared_repository(self):
        catalog = json.loads((ROOT / "catalog" / "operations.json").read_text())
        entry = next(item for item in catalog["operations"]
                     if item["id"] == "package.gstreamer1-plugins-bad-freeworld")
        entry["scope"] = "user"  # Mocked provider test runs without elevation.
        entry["status"] = "candidate"
        entry.pop("acceptanceEvidence", None)
        path = self.root / "rpmfusion-catalog.json"
        path.write_text(json.dumps(catalog))
        self.env["RIDE_CATALOG_PATH"] = str(path)
        (self.root / "os-release").write_text("ID=fedora\nVERSION_ID=44\nVARIANT_ID=workstation\n")
        profile = self.root / "rpmfusion-profile.json"
        profile.write_text(json.dumps({"schemaVersion": 1, "id": "rpmfusion-codec-test",
                                       "description": "Test-only source-pinned package",
                                       "operations": [{"id": entry["id"], "state": "installed"}]}))

        self.run_ride("plan", "--profile", str(profile), "--allow-candidate")
        self.run_ride("apply", "--profile", str(profile), "--allow-candidate")
        call = (self.root / "dnf.log").read_text().strip()
        self.assertIn("--from-repo=rpmfusion-free-updates", call)
        self.assertIn("gstreamer1-plugins-bad-freeworld", call)

        entry["sourceId"] = "unknown-repository"
        path.write_text(json.dumps(catalog))
        (self.root / "packages" / entry["packageName"]).unlink()
        (self.root / "dnf.log").unlink()
        self.run_ride("apply", "--profile", str(profile), "--allow-candidate", success=False)
        self.assertFalse((self.root / "dnf.log").exists())

    def test_handbrake_cli_uses_only_verified_rpmfusion_repository(self):
        catalog = json.loads((ROOT / "catalog" / "operations.json").read_text())
        entry = next(item for item in catalog["operations"]
                     if item["id"] == "package.handbrake-cli")
        entry["scope"] = "user"  # Mocked provider test runs without elevation.
        entry.pop("acceptanceEvidence", None)
        path = self.root / "handbrake-catalog.json"
        path.write_text(json.dumps(catalog))
        self.env["RIDE_CATALOG_PATH"] = str(path)
        (self.root / "os-release").write_text(
            "ID=fedora\nVERSION_ID=44\nVARIANT_ID=workstation\n")
        profile = self.root / "handbrake-profile.json"
        profile.write_text(json.dumps({
            "schemaVersion": 1,
            "id": "handbrake-cli-test",
            "description": "Test-only RPM Fusion CLI source selection",
            "operations": [{"id": entry["id"], "state": "installed"}],
        }))

        self.run_ride("plan", "--profile", str(profile), "--allow-candidate")
        self.run_ride("apply", "--profile", str(profile), "--allow-candidate")
        call = (self.root / "dnf.log").read_text().strip()
        self.assertIn("--from-repo=rpmfusion-free-updates", call)
        self.assertIn("HandBrake", call)

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

    def test_candidate_download_does_not_require_vm_acceptance_or_install(self):
        destination = self.root / "downloaded"
        preview = self.run_ride("download", "package.alpha", "--destination",
                                str(destination), "--dry-run")
        self.assertIn("would download package.alpha", preview.stdout)
        self.assertFalse(destination.exists())
        self.assertEqual(self.journals(), [])

        downloaded = self.run_ride("download", "package.alpha", "--destination",
                                   str(destination))
        artifact = destination / "alpha-1.0-1.fc44.x86_64.rpm"
        self.assertEqual(downloaded.stdout.strip(), str(artifact))
        self.assertTrue(artifact.is_file())
        self.assertTrue((destination / f"{artifact.name}.sha256").is_file())
        self.assertIn("--checksig", (self.root / "rpmkeys.log").read_text())
        self.assertFalse((self.root / "packages" / "alpha").exists())
        self.assertEqual(self.journals(), [])

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

    def test_show_stdin_emits_versioned_compact_records_in_input_order(self):
        shown = self.run_ride(
            "show", "--stdin", input_text="package.beta\r\npackage.alpha\npackage.beta")
        records = [json.loads(line) for line in shown.stdout.splitlines()]
        self.assertEqual([record["id"] for record in records],
                         ["package.beta", "package.alpha", "package.beta"])
        for record in records:
            self.assertEqual(record["schemaVersion"], 1)
            self.assertIsInstance(record["name"], str)
            self.assertIsInstance(record["kind"], str)
            self.assertIsInstance(record["observedState"], str)
            self.assertIsInstance(record["availableSources"], list)
        positional = json.loads(self.run_ride("show", "package.alpha").stdout)
        self.assertEqual(positional["schemaVersion"], 1)
        self.assertEqual(positional["observedState"], "absent")
        self.assertEqual(self.journals(), [])
        self.assertFalse((self.root / "dnf.log").exists())

    def test_show_stdin_empty_and_final_unterminated_line(self):
        self.assertEqual(self.run_ride("show", "--stdin", input_text="").stdout, "")
        shown = self.run_ride("show", "--stdin", input_text="package.alpha")
        self.assertEqual(json.loads(shown.stdout)["id"], "package.alpha")

    def test_show_stdin_rejects_blank_unknown_and_conflicting_selection(self):
        blank = self.run_ride(
            "show", "--stdin", input_text="package.alpha\n\npackage.beta", success=False)
        self.assertIn("blank operation ID", blank.stderr)
        self.assertEqual([json.loads(line)["id"] for line in blank.stdout.splitlines()],
                         ["package.alpha"])
        unknown = self.run_ride(
            "show", "--stdin", input_text="package.alpha\npackage.unknown\npackage.beta",
            success=False)
        self.assertIn("unknown", unknown.stderr)
        self.assertEqual([json.loads(line)["id"] for line in unknown.stdout.splitlines()],
                         ["package.alpha"])
        self.run_ride("show", "--stdin", "package.alpha", success=False)
        self.run_ride("show", "package.alpha", "--stdin", success=False)
        self.run_ride("list", "--stdin", success=False)

    def test_show_stdin_source_selector_is_applied_to_each_id(self):
        catalog = self.root / "catalog.json"
        data = json.loads(catalog.read_text())
        data["operations"][0]["sourceProviders"] = [{
            "sourceId": "alternate-rpm", "handler": "dnf-package", "packageName": "alpha-alt",
            "artifactFormat": "rpm", "status": "candidate", "recovery": "remove-new-install",
            "targets": {"fedora": {"releases": ["44"], "architectures": ["x86_64"]}},
            "sourceUri": "https://example.org/alternate", "verification": "fedora-repository-gpg",
        }]
        catalog.write_text(json.dumps(data))
        selected = self.run_ride("show", "--stdin", "--source", "alternate-rpm",
                                 input_text="package.alpha")
        self.assertEqual(json.loads(selected.stdout)["sourceId"], "alternate-rpm")
        invalid = self.run_ride("show", "--stdin", "--source", "alternate-rpm",
                                input_text="package.beta", success=False)
        self.assertIn("source", invalid.stderr)
        self.assertEqual(invalid.stdout, "")

    def test_status_has_explicit_id_and_view_selectors(self):
        positional = self.run_ride("status", "package.alpha")
        named = self.run_ride("status", "--id", "package.alpha")
        self.assertEqual(named.stdout, positional.stdout)

        packages = self.run_ride("status", "--view", "packages")
        self.assertIn("package.alpha\tfedora-rpm", packages.stdout)
        self.assertIn("package.beta\tfedora-rpm", packages.stdout)
        settings = self.run_ride("status", "--view", "settings")
        self.assertEqual(len(settings.stdout.splitlines()), 1)
        self.assertIn("package.alpha\tfedora-rpm", self.run_ride("status", "--view", "test").stdout)

        profiled_id = self.run_ride("status", "--profile", str(self.profile),
                                    "--id", "package.alpha")
        self.assertIn("package.alpha\tfedora-rpm", profiled_id.stdout)
        self.assertNotIn("package.beta\tfedora-rpm", profiled_id.stdout)
        profiled_packages = self.run_ride("status", "--profile", str(self.profile),
                                          "--view", "packages")
        self.assertIn("package.alpha\tfedora-rpm", profiled_packages.stdout)

        invalid = self.run_ride("status", "--view", "missing-group", success=False)
        self.assertIn("unknown status view", invalid.stderr)
        self.run_ride("status", "package.alpha", "--id", "package.beta", success=False)
        self.run_ride("status", "--id", "package.alpha", "--view", "packages", success=False)
        self.assertEqual(self.journals(), [])
        self.assertFalse((self.root / "dnf.log").exists())

    def test_installed_package_noop_outside_target_is_allowed_without_mutation(self):
        (self.root / "packages" / "alpha").write_text("already installed\n")
        (self.root / "os-release").write_text(
            "ID=fedora\nVERSION_ID=45\nVARIANT_ID=workstation\n")
        self.profile.write_text(json.dumps({
            "schemaVersion": 1, "id": "test", "description": "Installed package no-op",
            "operations": [{"id": "package.alpha", "state": "installed"}],
        }))
        status = json.loads(self.run_ride("show", "package.alpha").stdout)
        self.assertEqual(status["observedState"], "unsupported")
        planned = self.run_ride("plan", "--profile", str(self.profile))
        self.assertIn("package.alpha\tfedora-rpm\tinstalled\tinstalled\tunsupported", planned.stdout)
        installed = self.run_ride("install", "package.alpha")
        self.assertIn("target remains unsupported and no action was taken", installed.stdout)
        profile_apply = self.run_ride("apply", "--profile", str(self.profile))
        self.assertIn("target remains unsupported and no action was taken", profile_apply.stdout)
        self.assertTrue((self.root / "packages" / "alpha").is_file())
        self.assertEqual(self.journals(), [])
        self.assertFalse((self.root / "dnf.log").exists())
        catalog = json.loads((self.root / "catalog.json").read_text())
        self.assertEqual(catalog["operations"][0]["targets"]["fedora"]["releases"], ["44"])

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
        self.env["RIDE_TEST_IBUS_GET_FAIL"] = "1"
        unavailable_preview = self.run_ride(
            "plan", "--profile", str(self.profile), success=False)
        self.assertIn("cannot observe iBus emoji hotkey", unavailable_preview.stderr)
        self.assertEqual(self.journals(), [])
        self.assertEqual(override.read_text(), "['<Alt>F8']\n")
        del self.env["RIDE_TEST_IBUS_GET_FAIL"]
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
        run_count = len(self.journals())
        (self.root / "os-release").write_text(
            "ID=fedora\nVERSION_ID=45\nVARIANT_ID=workstation\n")
        unsupported_preview = self.run_ride(
            "restore", "--run-id", changed["runId"], "--dry-run", success=False)
        self.assertIn("operation is not declared", unsupported_preview.stderr)
        self.assertEqual(len(self.journals()), run_count)
        self.assertEqual(override.read_text(), "['<Control><Alt><Shift>e']\n")
        (self.root / "os-release").write_text(
            "ID=fedora\nVERSION_ID=44\nVARIANT_ID=workstation\n")
        self.run_ride("restore", "--run-id", changed["runId"], "--dry-run")
        candidate_restore = self.run_ride(
            "restore", "--run-id", changed["runId"], success=False)
        self.assertIn("candidate without VM acceptance", candidate_restore.stderr)
        self.assertEqual(override.read_text(), "['<Control><Alt><Shift>e']\n")
        self.assertEqual(len(self.journals()), run_count)
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

    def test_gnome_string_profile_value_and_exact_recovery(self):
        catalog = json.loads((ROOT / "catalog" / "operations.json").read_text())
        entries = [row for row in catalog["operations"] if row["id"] in
                   ("setting.gnome-region", "setting.gnome-window-buttons")]
        (self.root / "catalog.json").write_text(json.dumps({
            "schemaVersion": 3, "clientVersion": "3.0.0", "operations": entries,
        }))
        (self.root / "os-release").write_text("ID=fedora\nVERSION_ID=44\nVARIANT_ID=workstation\n")
        settings = self.root / "gnome-strings"
        settings.mkdir()
        region = settings / "region"
        buttons = settings / "button-layout"
        region.write_text("'en_US.UTF-8'\n")
        (self.root / "bin" / "dconf").write_text("""#!/bin/sh
[ "$1" = read ] || exit 2
case "$2" in
  /system/locale/region) file="$RIDE_TEST_STRINGS/region" ;;
  /org/gnome/desktop/wm/preferences/button-layout) file="$RIDE_TEST_STRINGS/button-layout" ;;
  *) exit 2 ;;
esac
[ ! -f "$file" ] || cat "$file"
""")
        (self.root / "bin" / "gsettings").write_text("""#!/bin/sh
file="$RIDE_TEST_STRINGS/$3"
case "$1" in
  get) if [ -f "$file" ]; then cat "$file"; else printf "'default'\\n"; fi ;;
  range) echo 'type s' ;;
  writable) if [ "${RIDE_TEST_STRING_LOCK:-0}" = 1 ]; then echo false; else echo true; fi ;;
  set)
    printf '%s\\n' "$4" > "$file"
    if [ "${RIDE_TEST_STRING_FAIL_ONCE:-0}" = 1 ] && [ ! -f "$RIDE_TEST_STRING_FAILURE_MARKER" ]; then
      touch "$RIDE_TEST_STRING_FAILURE_MARKER"
      exit 13
    fi ;;
  reset) rm -f "$file" ;;
  *) exit 2 ;;
esac
""")
        (self.root / "bin" / "locale").write_text("""#!/bin/sh
[ "$1" = -a ] || exit 2
printf 'en_US.utf8\\nda_DK.utf8\\n'
""")
        for name in ("dconf", "gsettings", "locale"):
            (self.root / "bin" / name).chmod(0o755)
        self.env["RIDE_TEST_STRINGS"] = str(settings)
        self.env["RIDE_TEST_STRING_FAILURE_MARKER"] = str(self.root / "string-failure-marker")
        self.env["DBUS_SESSION_BUS_ADDRESS"] = "unix:path=/tmp/ride-test-bus"
        self.profile.write_text(json.dumps({
            "schemaVersion": 1, "id": "region-test", "description": "Test region",
            "operations": [{"id": "setting.gnome-region", "state": "configured",
                            "value": "da_DK.UTF-8"}],
        }))

        self.assertIn("configured:da_DK.UTF-8", self.run_ride("plan", "--profile", str(self.profile)).stdout)
        self.run_ride("apply", "--profile", str(self.profile), success=False)
        changed = self.run_ride("apply", "--profile", str(self.profile), "--allow-candidate")
        journal = next(row for row in self.journals() if row["runId"] in changed.stdout)
        self.assertEqual(journal["steps"][0]["selectedValue"], "da_DK.UTF-8")
        self.assertTrue(journal["steps"][0]["observedBefore"].startswith("user:"))
        self.assertEqual(region.read_text(), "'da_DK.UTF-8'\n")
        region.write_text("'fr_FR.UTF-8'\n")
        conflict = self.run_ride("restore", "--run-id", journal["runId"],
                                 "--allow-candidate", success=False)
        self.assertIn("restore conflict", conflict.stderr)
        self.assertEqual(region.read_text(), "'fr_FR.UTF-8'\n")
        region.write_text("'da_DK.UTF-8'\n")
        bad_profile = json.loads(self.profile.read_text())
        bad_profile["operations"][0]["value"] = "fr_FR.UTF-8"
        self.profile.write_text(json.dumps(bad_profile))
        self.run_ride("restore", "--run-id", journal["runId"], "--allow-candidate")
        self.assertEqual(region.read_text(), "'en_US.UTF-8'\n")
        unavailable = self.run_ride("apply", "--profile", str(self.profile),
                                    "--allow-candidate", success=False)
        self.assertIn("locale is unavailable", unavailable.stderr)
        self.assertEqual(region.read_text(), "'en_US.UTF-8'\n")
        bad_profile["operations"][0]["value"] = "not a locale"
        self.profile.write_text(json.dumps(bad_profile))
        self.run_ride("plan", "--profile", str(self.profile), success=False)

        self.profile.write_text(json.dumps({
            "schemaVersion": 1, "id": "region-reset-test", "description": "Reset region",
            "operations": [{"id": "setting.gnome-region", "state": "configured", "value": ""}],
        }))
        self.assertIn("configured:<empty>", self.run_ride("plan", "--profile", str(self.profile)).stdout)
        reset = self.run_ride("apply", "--profile", str(self.profile), "--allow-candidate")
        reset_journal = next(row for row in self.journals() if row["runId"] in reset.stdout)
        self.assertEqual(reset_journal["steps"][0]["selectedValue"], "")
        self.assertEqual(region.read_text(), "''\n")
        self.run_ride("restore", "--run-id", reset_journal["runId"], "--allow-candidate")
        self.assertEqual(region.read_text(), "'en_US.UTF-8'\n")

        self.profile.write_text(json.dumps({
            "schemaVersion": 1, "id": "buttons-test", "description": "Test layout",
            "operations": [{"id": "setting.gnome-window-buttons", "state": "configured",
                            "value": ":minimize,maximize,close"}],
        }))
        missing = json.loads(self.profile.read_text())
        del missing["operations"][0]["value"]
        self.profile.write_text(json.dumps(missing))
        self.run_ride("plan", "--profile", str(self.profile), success=False)
        self.run_ride("set", "setting.gnome-window-buttons", "--state", "configured",
                      "--allow-candidate", success=False)
        missing["operations"][0]["value"] = ":minimize,maximize,close"
        missing["operations"].append(dict(missing["operations"][0], value=":appmenu:close"))
        self.profile.write_text(json.dumps(missing))
        self.run_ride("plan", "--profile", str(self.profile), success=False)
        missing["operations"] = missing["operations"][:1]
        missing["operations"][0]["value"] = "invalid-layout"
        self.profile.write_text(json.dumps(missing))
        self.run_ride("plan", "--profile", str(self.profile), success=False)
        for value in (":minimize,maximize,close", ":appmenu:close", "close,minimize,maximize:"):
            missing["operations"][0]["value"] = value
            self.profile.write_text(json.dumps(missing))
            changed = self.run_ride("apply", "--profile", str(self.profile), "--allow-candidate")
            journal = next(row for row in self.journals() if row["runId"] in changed.stdout)
            self.assertEqual(buttons.read_text(), f"'{value}'\n")
            self.run_ride("restore", "--run-id", journal["runId"], "--dry-run")
            self.run_ride("restore", "--run-id", journal["runId"], "--allow-candidate")
            self.assertFalse(buttons.exists())

        self.env["RIDE_TEST_STRING_FAIL_ONCE"] = "1"
        self.run_ride("set", "setting.gnome-window-buttons", "--state", "configured",
                      "--value", ":appmenu:close", "--allow-candidate", success=False)
        self.assertFalse(buttons.exists())
        del self.env["RIDE_TEST_STRING_FAIL_ONCE"]
        self.env["RIDE_TEST_STRING_LOCK"] = "1"
        locked = self.run_ride("set", "setting.gnome-window-buttons", "--state", "configured",
                               "--value", ":appmenu:close", "--allow-candidate", success=False)
        self.assertIn("locked", locked.stderr)

        del self.env["RIDE_TEST_STRING_LOCK"]
        self.profile.write_text(json.dumps({
            "schemaVersion": 1, "id": "region-profile-removal", "description": "Keep settings",
            "operations": [{"id": "setting.gnome-region", "state": "configured",
                            "value": "da_DK.UTF-8"}],
        }))
        applied = self.run_ride("apply", "--profile", str(self.profile), "--allow-candidate")
        applied_journal = next(row for row in self.journals() if row["runId"] in applied.stdout)
        self.assertEqual(region.read_text(), "'da_DK.UTF-8'\n")
        count_before_remove = len(self.journals())
        removed = self.run_ride("remove", "--profile", str(self.profile), "--allow-candidate")
        self.assertIn("kept non-package profile operation setting.gnome-region", removed.stdout)
        self.assertEqual(region.read_text(), "'da_DK.UTF-8'\n")
        self.assertEqual(len(self.journals()), count_before_remove)

        unset = self.run_ride("unset", "setting.gnome-region", "--allow-candidate")
        unset_journal = next(row for row in self.journals() if row["runId"] in unset.stdout)
        self.assertNotIn("selectedValue", unset_journal["steps"][0])
        self.assertFalse(region.exists())
        self.run_ride("restore", "--run-id", unset_journal["runId"], "--allow-candidate")
        self.assertEqual(region.read_text(), "'da_DK.UTF-8'\n")
        self.assertEqual(applied_journal["steps"][0]["selectedValue"], "da_DK.UTF-8")

        explicit_empty = self.run_ride("set", "setting.gnome-region", "--state", "configured",
                                       "--value", "", "--allow-candidate")
        empty_journal = next(row for row in self.journals() if row["runId"] in explicit_empty.stdout)
        self.assertEqual(empty_journal["steps"][0]["selectedValue"], "")
        self.assertEqual(region.read_text(), "''\n")
        self.run_ride("restore", "--run-id", empty_journal["runId"], "--allow-candidate")
        self.assertEqual(region.read_text(), "'da_DK.UTF-8'\n")

    def test_system_package_change_requires_root_before_state_or_mutation(self):
        catalog_path = Path(self.env["RIDE_CATALOG_PATH"])
        catalog = json.loads(catalog_path.read_text())
        for entry in catalog["operations"]:
            entry["scope"] = "system"
        catalog_path.write_text(json.dumps(catalog))

        refused = self.run_ride("install", "package.alpha", "--allow-candidate", success=False)

        self.assertIn("this operation needs root", refused.stderr)
        self.assertFalse((self.root / "runs").exists())
        self.assertFalse((self.root / "dnf.log").exists())
        self.assertFalse(any((self.root / "packages").iterdir()))

    def test_profile_removal_orders_selected_dependent_before_prerequisite(self):
        catalog_path = Path(self.env["RIDE_CATALOG_PATH"])
        catalog = json.loads(catalog_path.read_text())
        beta = next(entry for entry in catalog["operations"] if entry["id"] == "package.beta")
        beta["dependencies"] = ["package.alpha"]
        catalog_path.write_text(json.dumps(catalog))
        self.profile.write_text(json.dumps({
            "schemaVersion": 1,
            "id": "dependency-removal-order",
            "description": "Remove a dependent before its prerequisite",
            "operations": [
                {"id": "package.alpha", "state": "installed"},
                {"id": "package.beta", "state": "installed"},
            ],
        }))

        applied = self.run_ride("apply", "--profile", str(self.profile), "--allow-candidate")
        applied_run = next(row for row in self.journals() if row["runId"] in applied.stdout)
        self.assertEqual([step["id"] for step in applied_run["steps"]],
                         ["package.alpha", "package.beta"])

        removed = self.run_ride("remove", "--profile", str(self.profile), "--allow-candidate")
        removed_run = next(row for row in self.journals() if row["runId"] in removed.stdout)
        self.assertEqual([step["id"] for step in removed_run["steps"]],
                         ["package.beta", "package.alpha"])
        self.assertFalse(any((self.root / "packages").iterdir()))

    def test_remove_and_command_options_refuse_ambiguity_before_mutation(self):
        missing_selector = self.run_ride("remove", success=False)
        self.assertIn("remove requires a package ID or an explicit --profile", missing_selector.stderr)
        self.assertFalse((self.root / "runs").exists())

        conflicting_selector = self.run_ride("remove", "package.alpha", "--profile",
                                             str(self.profile), success=False)
        self.assertIn("cannot be combined", conflicting_selector.stderr)
        irrelevant = self.run_ride("list", "--state", "installed", success=False)
        self.assertIn("list does not accept options", irrelevant.stderr)
        irrelevant_set = self.run_ride("install", "package.alpha", "--destination",
                                       str(self.root / "elsewhere"), success=False)
        self.assertIn("install requires an ID and accepts only", irrelevant_set.stderr)
        irrelevant_status = self.run_ride("status", "--value", "locale", success=False)
        self.assertIn("status --value requires an ID", irrelevant_status.stderr)
        self.assertFalse((self.root / "runs").exists())
        self.assertFalse((self.root / "dnf.log").exists())

    def test_unset_refuses_when_operation_has_no_declared_unset_state(self):
        catalog = json.loads((ROOT / "catalog" / "operations.json").read_text())
        entry = next(row for row in catalog["operations"]
                     if row["id"] == "setting.gnome-calendar-week-numbers")
        (self.root / "catalog.json").write_text(json.dumps({
            "schemaVersion": 3, "clientVersion": "3.0.0", "operations": [entry],
        }))
        refused = self.run_ride("unset", entry["id"], "--allow-candidate", success=False)
        self.assertIn("no declared unset state", refused.stderr)
        self.assertFalse((self.root / "runs").exists())

    def test_profile_removal_keeps_one_way_prerequisite(self):
        catalog = json.loads((self.root / "catalog.json").read_text())
        prerequisite = operation("trust-keys")
        prerequisite.update({"states": ["installed"], "recovery": "none"})
        catalog["operations"].append(prerequisite)
        (self.root / "catalog.json").write_text(json.dumps(catalog))
        self.profile.write_text(json.dumps({
            "schemaVersion": 1, "id": "test", "description": "Fixture",
            "operations": [{"id": "package.trust-keys", "state": "installed"}],
        }))

        self.run_ride("apply", "--profile", str(self.profile), "--allow-candidate")
        self.assertTrue((self.root / "packages" / "trust-keys").exists())
        removed = self.run_ride("remove", "--profile", str(self.profile), "--allow-candidate")
        self.assertIn("kept one-way prerequisite package.trust-keys", removed.stdout)
        self.assertTrue((self.root / "packages" / "trust-keys").exists())

    def test_profile_source_and_unknown_source(self):
        profile = json.loads(self.profile.read_text())
        profile["operations"][0]["source"] = "not-declared"
        self.profile.write_text(json.dumps(profile))
        refused = self.run_ride("plan", "--profile", str(self.profile), success=False)
        self.assertIn("unknown source", refused.stderr)

    def test_required_tools_maps_exact_rpms_and_stays_one_way(self):
        expected = {
            "package.coreutils": "coreutils",
            "package.git": "git",
            "package.gnupg2": "gnupg2",
            "package.python-command": "python-unversioned-command",
            "package.tar": "tar",
            "package.wget": "wget2-wget",
            "package.gcc": "gcc",
        }
        catalog = json.loads((ROOT / "catalog/operations.json").read_text())
        entries = [row for row in catalog["operations"] if row["id"] in expected]
        self.assertEqual({row["id"]: row["packageName"] for row in entries}, expected)
        for row in entries:
            self.assertEqual(row["states"], ["installed"])
            self.assertEqual(row["recovery"], "none")
            self.assertEqual(row["status"], "candidate")
            row["scope"] = "user"  # Test-only catalog permits mocked, unelevated DNF.
        test_catalog = self.root / "required-tools-catalog.json"
        test_catalog.write_text(json.dumps({"schemaVersion": 3, "clientVersion": "3.0.0",
                                            "operations": entries}))
        self.env["RIDE_CATALOG_PATH"] = str(test_catalog)
        self.env["RIDE_TEST_MODE"] = "1"
        (self.root / "os-release").write_text("ID=fedora\nVERSION_ID=44\nVARIANT_ID=workstation\n")
        profile = str(ROOT / "profiles/required-tools.json")
        profile_ids = [item["id"] for item in json.loads(Path(profile).read_text())["operations"]]
        self.assertEqual(profile_ids, list(expected))

        plan = self.run_ride("plan", "--profile", profile).stdout
        for identifier in expected:
            self.assertIn(f"{identifier}\tfedora-rpm\tabsent\tinstalled\tcandidate", plan)
        self.run_ride("apply", "--profile", profile, success=False)
        self.assertFalse(any((self.root / "packages" / name).exists() for name in expected.values()))
        self.run_ride("apply", "--profile", profile, "--allow-candidate")
        self.assertTrue(all((self.root / "packages" / name).exists() for name in expected.values()))
        repeat = self.run_ride("apply", "--profile", profile, "--allow-candidate").stdout
        self.assertTrue(all(f"unchanged {identifier}" in repeat for identifier in expected))
        status = self.run_ride("status").stdout
        self.assertTrue(all(f"{identifier}\tfedora-rpm\tinstalled\tcandidate" in status
                            for identifier in expected))
        removed = self.run_ride("remove", "--profile", profile, "--allow-candidate").stdout
        self.assertTrue(all(f"kept one-way prerequisite {identifier}" in removed
                            for identifier in expected))
        self.assertTrue(all((self.root / "packages" / name).exists() for name in expected.values()))

    def test_server_required_tools_maps_exact_rpms_and_isolates_firewalld(self):
        expected = {
            "package.open-vm-tools": "open-vm-tools",
            "package.server-nano": "nano",
            "package.wget": "wget2-wget",
            "package.unzip": "unzip",
            "package.git": "git",
            "package.cifs-utils": "cifs-utils",
            "package.samba-client": "samba-client",
            "package.samba-common": "samba-common",
            "package.cronie": "cronie",
            "package.screen": "screen",
        }
        catalog = json.loads((ROOT / "catalog/operations.json").read_text())
        entries = [row for row in catalog["operations"]
                   if row["id"] in expected or row["id"] == "package.firewalld"]
        by_id = {row["id"]: row for row in entries}
        self.assertEqual({identifier: by_id[identifier]["packageName"]
                          for identifier in expected}, expected)
        for identifier, row in by_id.items():
            self.assertIn("server", row["targets"]["fedora"]["variantIds"])
            self.assertEqual(row["scope"], "system")
            row["scope"] = "user"  # Test-only catalog permits mocked, unelevated DNF.
            if row["states"] == ["installed"]:
                self.assertEqual(row["states"], ["installed"])
                self.assertEqual(row["recovery"], "none")
            else:
                self.assertEqual(row["states"], ["installed", "absent"])
                self.assertEqual(row["recovery"], "remove-new-install")
        self.assertEqual(by_id["package.firewalld"]["packageName"], "firewalld")
        self.assertEqual(by_id["package.firewalld"]["states"], ["installed"])
        self.assertEqual(by_id["package.firewalld"]["recovery"], "none")

        test_catalog = self.root / "server-required-catalog.json"
        test_catalog.write_text(json.dumps({"schemaVersion": 3, "clientVersion": "3.0.0",
                                            "operations": entries}))
        self.env["RIDE_CATALOG_PATH"] = str(test_catalog)
        self.env["RIDE_TEST_MODE"] = "1"
        (self.root / "os-release").write_text("ID=fedora\nVERSION_ID=44\nVARIANT_ID=server\n")
        profile = str(ROOT / "profiles/server-required-tools.json")
        profile_ids = [item["id"] for item in json.loads(Path(profile).read_text())["operations"]]
        self.assertEqual(profile_ids, list(expected))
        firewall_profile = str(ROOT / "profiles/server-firewall-package.json")
        firewall_ids = [item["id"] for item in
                        json.loads(Path(firewall_profile).read_text())["operations"]]
        self.assertEqual(firewall_ids, ["package.firewalld"])

        plan = self.run_ride("plan", "--profile", profile).stdout
        self.assertIn("candidate", plan)
        self.assertNotIn("package.firewalld", plan)
        self.run_ride("apply", "--profile", profile, success=False)
        self.run_ride("apply", "--profile", profile, "--allow-candidate")
        repeat = self.run_ride("apply", "--profile", profile, "--allow-candidate").stdout
        self.assertTrue(all(f"unchanged {identifier}" in repeat for identifier in expected), repeat)
        removed = self.run_ride("remove", "--profile", profile, "--allow-candidate").stdout
        one_way = [identifier for identifier in expected
                   if by_id[identifier]["recovery"] == "none"]
        reversible = [identifier for identifier in expected
                      if by_id[identifier]["recovery"] == "remove-new-install"]
        self.assertTrue(all(f"kept one-way prerequisite {identifier}" in removed
                            for identifier in one_way), removed)
        self.assertTrue(all(f"changed {identifier}: installed -> absent" in removed
                            for identifier in reversible), removed)


if __name__ == "__main__":
    unittest.main()
