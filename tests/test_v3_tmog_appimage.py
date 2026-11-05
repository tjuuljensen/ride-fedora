"""Check the pinned TMOG AppImage lifecycle without touching user data."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
FIXTURE = b"\x7fELF TMOG fixture\n"


class TmogAppimageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.home = self.root / "home"
        self.home.mkdir()
        mock_bin = self.root / "bin"
        mock_bin.mkdir()
        artifact = self.root / "tmog.AppImage"
        artifact.write_bytes(FIXTURE)
        curl = mock_bin / "curl"
        curl.write_text(
            "#!/usr/bin/env bash\n"
            "while (($#)); do case $1 in -o) out=$2; shift 2;; *) uri=$1; shift;; esac; done\n"
            "[[ $uri == https://tmog.org/downloads/TaskManagerOG-1.1.1-x86_64.AppImage ]] || exit 23\n"
            "[[ ${TMOG_CURL_FAIL:-0} == 0 ]] || exit 22\n"
            "cp \"$TMOG_FIXTURE\" \"$out\"\n"
        )
        curl.chmod(0o755)
        unsquashfs = mock_bin / "unsquashfs"
        unsquashfs.write_text(
            "#!/usr/bin/env bash\n"
            "while (($#)); do case $1 in -d) destination=$2; shift 2;; -o) "
            "[[ $2 == 944632 ]] || exit 24; shift 2;; *) shift;; esac; done\n"
            "[[ ${TMOG_EXTRACT_FAIL:-0} == 0 ]] || exit 25\n"
            "mkdir -p \"$destination/usr/bin\"\n"
            "printf '#!/bin/sh\\nexit 0\\n' > \"$destination/AppRun\"\n"
            "chmod 755 \"$destination/AppRun\"\n"
            "printf 'payload\\n' > \"$destination/usr/bin/tmog-task-manager\"\n"
            "mkdir -p \"$destination/usr/share/icons/hicolor/256x256/apps\"\n"
            "printf 'icon fixture\\n' > \"$destination/usr/share/icons/hicolor/256x256/apps/tmog-task-manager.png\"\n"
        )
        unsquashfs.chmod(0o755)
        operation = next(
            entry for entry in json.loads((ROOT / "catalog/operations.json").read_text())["operations"]
            if entry["id"] == "package.tmog"
        )
        operation["sourceSha256"] = hashlib.sha256(FIXTURE).hexdigest()
        self.operation = self.root / "operation.json"
        self.operation.write_text(json.dumps(operation))
        self.appimage = self.home / ".local/opt/ride-fedora/tmog/1.1.1" / operation["assetName"]
        self.appdir = self.appimage.parent / "appdir"
        self.desktop = self.home / ".local/share/applications/com.tmog.taskmanager.desktop"
        self.manifest = self.home / ".local/share/ride-fedora/owned-tools/package.tmog.json"
        self.license = self.home / ".config/TMOG/Task Manager TMOG/license.json"
        self.license.parent.mkdir(parents=True)
        self.license.write_text("synthetic license sentinel")
        self.environment = os.environ | {
            "HOME": str(self.home),
            "RIDE_ROOT": str(ROOT),
            "PATH": f"{mock_bin}:{os.environ['PATH']}",
            "TMOG_FIXTURE": str(artifact),
        }

    def call(self, function, state=None, environment=None):
        args = f' "{state}"' if state else ""
        command = (
            'source "$RIDE_ROOT/lib/v3/common.sh"; '
            'source "$RIDE_ROOT/lib/v3/providers.sh"; '
            f'{function} "$(cat {self.operation})"{args}'
        )
        return subprocess.run(
            ["bash", "-c", command], env=environment or self.environment,
            capture_output=True, text=True,
        )

    def test_install_repeat_observe_and_remove_preserve_license(self):
        for _ in range(2):
            self.assertEqual(self.call("ride_change_tmog_appimage", "installed").returncode, 0)
        self.assertEqual(self.call("ride_observe_tmog_appimage").stdout.strip(), "installed")
        self.assertEqual(self.appimage.read_bytes(), FIXTURE)
        self.assertTrue((self.appdir / "AppRun").is_file())
        self.assertEqual(json.loads(self.manifest.read_text())["id"], "package.tmog")
        self.assertIn(str(self.appdir / "AppRun"), self.desktop.read_text())
        self.assertIn(
            "Icon=" + str(self.appdir / "usr/share/icons/hicolor/256x256/apps/tmog-task-manager.png"),
            self.desktop.read_text(),
        )
        self.assertEqual(self.call("ride_change_tmog_appimage", "absent").returncode, 0)
        self.assertFalse(self.appimage.exists())
        self.assertFalse(self.appdir.exists())
        self.assertFalse(self.desktop.exists())
        self.assertFalse(self.manifest.exists())
        self.assertEqual(self.license.read_text(), "synthetic license sentinel")

    def test_download_and_digest_failure_leave_no_install(self):
        failed = self.call(
            "ride_change_tmog_appimage", "installed",
            self.environment | {"TMOG_CURL_FAIL": "1"},
        )
        self.assertNotEqual(failed.returncode, 0)
        self.assertFalse(self.appimage.exists())
        self.assertFalse(self.appdir.exists())
        operation = json.loads(self.operation.read_text())
        operation["sourceSha256"] = "0" * 64
        self.operation.write_text(json.dumps(operation))
        mismatch = self.call("ride_change_tmog_appimage", "installed")
        self.assertNotEqual(mismatch.returncode, 0)
        self.assertFalse(self.appimage.exists())
        self.assertFalse(self.appdir.exists())
        self.assertEqual(self.license.read_text(), "synthetic license sentinel")

    def test_extract_failure_and_modified_payload_are_safe(self):
        failed = self.call(
            "ride_change_tmog_appimage", "installed",
            self.environment | {"TMOG_EXTRACT_FAIL": "1"},
        )
        self.assertNotEqual(failed.returncode, 0)
        self.assertFalse(self.appimage.exists())
        self.assertFalse(self.appdir.exists())
        self.assertEqual(self.call("ride_change_tmog_appimage", "installed").returncode, 0)
        (self.appdir / "usr/bin/tmog-task-manager").write_text("modified payload")
        self.assertEqual(self.call("ride_observe_tmog_appimage").stdout.strip(), "unowned")
        self.assertNotEqual(self.call("ride_change_tmog_appimage", "absent").returncode, 0)
        self.assertTrue(self.appimage.exists())
        self.assertEqual(self.license.read_text(), "synthetic license sentinel")

    def test_unowned_file_refuses_install_and_removal(self):
        self.appimage.parent.mkdir(parents=True)
        self.appimage.write_text("different AppImage")
        self.assertNotEqual(self.call("ride_change_tmog_appimage", "installed").returncode, 0)
        self.assertNotEqual(self.call("ride_change_tmog_appimage", "absent").returncode, 0)
        self.assertEqual(self.appimage.read_text(), "different AppImage")
        self.assertEqual(self.license.read_text(), "synthetic license sentinel")

    def test_modified_desktop_entry_refuses_removal(self):
        self.assertEqual(self.call("ride_change_tmog_appimage", "installed").returncode, 0)
        self.desktop.write_text("unowned desktop entry")
        self.assertEqual(self.call("ride_observe_tmog_appimage").stdout.strip(), "unowned")
        self.assertNotEqual(self.call("ride_change_tmog_appimage", "absent").returncode, 0)
        self.assertEqual(self.appimage.read_bytes(), FIXTURE)
        self.assertEqual(self.desktop.read_text(), "unowned desktop entry")

    def test_catalog_guard_rejects_changed_publisher_digest(self):
        catalog = json.loads((ROOT / "catalog/operations.json").read_text())
        operation = next(entry for entry in catalog["operations"] if entry["id"] == "package.tmog")
        operation["sourceSha256"] = "0" * 64
        altered = self.root / "catalog.json"
        altered.write_text(json.dumps(catalog))
        result = subprocess.run(
            ["bash", str(ROOT / "ride.sh"), "show", "package.tmog"],
            env=self.environment | {"RIDE_CATALOG_PATH": str(altered)},
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid v3 operation catalog", result.stderr)

    def test_previous_deployment_run_keeps_read_only_restore_path(self):
        old_signature = "8ca372bf3ad0402e022ade54114679a22ba195c8d8353c571aae73dab93266c3"
        journal = self.root / "old-run.json"
        journal.write_text(json.dumps({"schemaVersion": 2, "steps": [{
            "id": "package.tmog",
            "sourceId": "tmog-publisher-appimage-pinned",
            "sourceSignature": old_signature,
            "sourceSignatureVersion": 2,
            "deploymentId": "user-applications-appimage",
            "observedBefore": "absent",
            "observedAfter": "installed",
            "result": "changed",
        }]}))
        command = (
            'source "$RIDE_ROOT/ride.sh"; '
            'entry=$(jq -c ".operations[] | select(.id == \\"package.tmog\\")" "$RIDE_CATALOG"); '
            'ride_restore_signature_matches package.tmog tmog-publisher-appimage-pinned '
            f'"$1" 2 "$entry" "{journal}"'
        )
        accepted = subprocess.run(["bash", "-c", command, "bash", old_signature],
                                  env=self.environment, capture_output=True, text=True)
        rejected = subprocess.run(["bash", "-c", command, "bash", "0" * 64],
                                  env=self.environment, capture_output=True, text=True)
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertNotEqual(rejected.returncode, 0)


if __name__ == "__main__":
    unittest.main()
