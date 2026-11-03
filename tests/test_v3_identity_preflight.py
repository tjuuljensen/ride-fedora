"""Focused identity tests for read-only restore-preview preflight."""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "ride.sh"
COMMON = ROOT / "lib/v3/common.sh"


class PreviewIdentityTests(unittest.TestCase):
    def run_identity_check(self, scope, uid):
        script = (
            'source "$1"; '
            'TEST_EFFECTIVE_UID=$2; '
            'ride_effective_uid() { printf "%s\\n" "$TEST_EFFECTIVE_UID"; }; '
            'ride_require_preview_identity "$3"'
        )
        return subprocess.run(
            ["bash", "-c", script, "preview-identity-test", str(COMMON), str(uid),
             f'{{"scope":"{scope}"}}'],
            check=False, capture_output=True, text=True)

    def test_root_cannot_preview_user_scope(self):
        result = self.run_identity_check("user", 0)
        self.assertEqual(result.returncode, 2)
        self.assertIn("intended non-root account", result.stderr)

    def test_root_can_preview_system_scope_without_mutation_privilege_check(self):
        result = self.run_identity_check("system", 0)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_restore_preview_refuses_root_identity_before_observation_or_journaling(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "runs"
            state.mkdir()
            run_id = "20261103T120000Z-123-1"
            journal = state / f"{run_id}.json"
            original = {
                "schemaVersion": 2,
                "runId": run_id,
                "action": "single",
                "startedAt": "2026-11-03T12:00:00Z",
                "status": "complete",
                "steps": [{
                    "id": "setting.gnome-calendar-week-numbers",
                    "observedBefore": "disabled",
                    "observedAfter": "enabled",
                    "result": "changed",
                    "sourceId": None,
                    "sourceSignature": None,
                    "sourceSignatureVersion": 1,
                }],
            }
            journal.write_text(json.dumps(original) + "\n", encoding="utf-8")
            journal_before = journal.read_bytes()
            os_release = root / "os-release"
            os_release.write_text(
                "ID=fedora\nVERSION_ID=44\nVARIANT_ID=workstation\n",
                encoding="utf-8")
            observe_log = root / "observe.log"
            script = (
                'source "$1"; '
                'ride_effective_uid() { printf "0\\n"; }; '
                'ride_observe() { printf "called\\n" >> "$RIDE_TEST_OBSERVE_LOG"; return 1; }; '
                'ride_main restore --run-id "$2" --dry-run'
            )
            env = os.environ.copy()
            env.update({
                "RIDE_TEST_MODE": "1",
                "RIDE_OS_RELEASE_FILE": str(os_release),
                "RIDE_STATE_DIR": str(state),
                "RIDE_TEST_OBSERVE_LOG": str(observe_log),
            })
            result = subprocess.run(
                ["bash", "-c", script, "restore-preview-test", str(CLI), run_id],
                env=env, capture_output=True, text=True, check=False)

            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("per-user; preview it from the intended non-root account",
                          result.stderr)
            self.assertEqual(journal.read_bytes(), journal_before)
            self.assertEqual(sorted(path.name for path in state.iterdir()),
                             [journal.name])
            self.assertFalse(observe_log.exists())

    def test_uid_zero_namespace_restore_preview_refuses_before_observation_or_journaling(self):
        unshare = shutil.which("unshare")
        if not unshare:
            self.skipTest("unshare is unavailable")

        with tempfile.TemporaryDirectory(prefix="ride-root-preview-") as directory:
            root = Path(directory)
            mount_probe = root / "mount-probe"
            mount_probe.mkdir()
            probe = subprocess.run(
                [unshare, "--user", "--map-root-user", "--mount", "bash", "-c",
                 'mount --make-rprivate / && mount -t tmpfs ride-probe "$1" && umount "$1"',
                 "ride-root-preview-probe", str(mount_probe)],
                capture_output=True, text=True, check=False)
            if probe.returncode:
                self.skipTest(f"isolated user/mount namespaces unavailable: {probe.stderr.strip()}")

            os_release = root / "os-release"
            os_release.write_text(
                "ID=fedora\nVERSION_ID=44\nVARIANT_ID=workstation\n",
                encoding="utf-8")
            run_id = "20261103T120000Z-123-1"
            state = root / "runs"
            state.mkdir()
            journal = state / f"{run_id}.json"
            journal.write_text(json.dumps({
                "schemaVersion": 2,
                "runId": run_id,
                "action": "single",
                "startedAt": "2026-11-03T12:00:00Z",
                "status": "complete",
                "steps": [{
                    "id": "setting.gnome-calendar-week-numbers",
                    "observedBefore": "disabled",
                    "observedAfter": "enabled",
                    "result": "changed",
                    "sourceId": None,
                    "sourceSignature": None,
                    "sourceSignatureVersion": 1,
                }],
            }) + "\n", encoding="utf-8")
            journal_before = journal.read_bytes()
            fake_bin = root / "bin"
            fake_bin.mkdir()
            gsettings = fake_bin / "gsettings"
            gsettings.write_text(
                '#!/bin/sh\nprintf "called\\n" >> "$RIDE_TEST_GSETTINGS_LOG"\nexit 0\n',
                encoding="utf-8")
            gsettings.chmod(0o755)
            gsettings_log = root / "gsettings.log"
            script = (
                'set -euo pipefail; '
                'mount --make-rprivate /; '
                'mount -t tmpfs ride-root-preview /var/lib; '
                'mkdir -p /var/lib/ride-fedora/runs; '
                'cp "$1" /var/lib/ride-fedora/runs/20261103T120000Z-123-1.json; '
                'mount --bind "$2" /etc/os-release; '
                'test "$EUID" -eq 0; '
                'RIDE_CATALOG_PATH="$3/catalog/operations.json" '
                '"$3/ride.sh" restore --run-id 20261103T120000Z-123-1 --dry-run '
                '>"$4/stdout" 2>"$4/stderr" && exit 90 || rc=$?; '
                'test "$rc" -eq 2; '
                'grep -F "per-user; preview it from the intended non-root account" '
                '"$4/stderr" >/dev/null; '
                'test "$(find /var/lib/ride-fedora/runs -maxdepth 1 -type f | wc -l)" -eq 1; '
                'test ! -s "$4/stdout"'
            )
            env = os.environ.copy()
            env.update({
                "PATH": f"{fake_bin}:{env['PATH']}",
                "RIDE_TEST_GSETTINGS_LOG": str(gsettings_log),
            })
            result = subprocess.run(
                [unshare, "--user", "--map-root-user", "--mount", "bash", "-c",
                 script, "ride-root-preview-test", str(journal), str(os_release),
                 str(ROOT), str(root)],
                env=env, capture_output=True, text=True, check=False)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(journal.read_bytes(), journal_before)
            self.assertFalse(gsettings_log.exists())


if __name__ == "__main__":
    unittest.main()
