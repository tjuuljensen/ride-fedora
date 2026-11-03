import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/v3/networkmanager-vpn-profiles.sh"
UUIDS = (
    "c5f9fa90-29d8-4a88-801e-a56a5a3d8201",
    "de96ea18-94f8-4e5a-86a8-0a5e3aa60002",
    "038b9389-2399-4fd3-9f4a-51c3d7650003",
)


NMCLI = r'''#!/usr/bin/env python3
import configparser
import os
import sys
from pathlib import Path

root = Path(os.environ["NM_TEST_DIR"])
args = sys.argv[1:]
files = list(root.glob("*.nmconnection"))

def profile(path):
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(path)
    return parser.get("connection", "uuid"), parser.get("connection", "type")

if args[:3] == ["-g", "connection.type", "connection"] and args[3:4] == ["show"]:
    wanted = args[4]
    for path in files:
        uuid, kind = profile(path)
        if uuid == wanted:
            print(kind)
            sys.exit(0)
    sys.exit(10)
if args == ["-g", "RUNNING", "general"]:
    print("running")
    sys.exit(0)
if args[:4] == ["-g", "UUID", "connection", "show"] and args[4:] == ["--active"]:
    counter = root / ".active-query-count"
    count = int(counter.read_text()) if counter.exists() else 0
    count += 1
    counter.write_text(str(count))
    active = os.environ.get("NM_ACTIVE_UUIDS", "")
    if count >= int(os.environ.get("NM_ACTIVATE_ON_QUERY", "999")):
        active = os.environ.get("NM_ACTIVATE_UUID", active)
    print(active)
    sys.exit(0)
if args[:3] == ["connection", "delete", "uuid"]:
    wanted = args[3]
    if wanted == os.environ.get("NM_FAIL_DELETE_UUID"):
        sys.exit(1)
    for path in files:
        uuid, _ = profile(path)
        if uuid == wanted:
            path.unlink()
            sys.exit(0)
    sys.exit(10)
if args == ["connection", "reload"]:
    if os.environ.get("NM_FAIL_RELOAD_ONCE") and not (root / ".reload-failed").exists():
        (root / ".reload-failed").touch()
        sys.exit(1)
    sys.exit(0)
sys.exit(3)
'''


class NetworkManagerVPNProfilesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ride-vpn-profiles-")
        self.base = Path(self.temp.name)
        self.connection_dir = self.base / "connections"
        self.connection_dir.mkdir(mode=0o700)
        self.state_root = self.base / "state"
        self.bin_dir = self.base / "bin"
        self.bin_dir.mkdir()
        nmcli = self.bin_dir / "nmcli"
        nmcli.write_text(NMCLI)
        nmcli.chmod(0o755)
        self.env = os.environ.copy()
        self.env.update({
            "PATH": f"{self.bin_dir}:{self.env['PATH']}",
            "RIDE_ROOT": str(ROOT),
            "RIDE_TEST_MODE": "1",
            "RIDE_VPN_PROFILES_TEST_CONNECTION_DIR": str(self.connection_dir),
            "RIDE_VPN_PROFILES_TEST_STATE_ROOT": str(self.state_root),
            "NM_TEST_DIR": str(self.connection_dir),
        })
        self.add_profile(UUIDS[0], "selected-one", secret="auth-pass=private-one")
        self.add_profile(UUIDS[1], "selected-two", secret="auth-pass=private-two")
        self.add_profile(UUIDS[2], "unrelated", secret="auth-pass=keep-me")
        self.entry = json.dumps({"selectedValue": f"{UUIDS[0]},{UUIDS[1]}"})

    def tearDown(self):
        self.temp.cleanup()

    def add_profile(self, uuid, name, secret):
        path = self.connection_dir / f"{name}.nmconnection"
        path.write_text(
            f"[connection]\nid={name}\nuuid={uuid}\ntype=vpn\n"
            f"[vpn]\nservice-type=org.freedesktop.NetworkManager.openvpn\n"
            f"secrets={secret}\n"
        )
        path.chmod(0o600)
        try:
            os.setxattr(path, "user.ride-test", b"metadata-fixture")
        except OSError:
            pass
        return path

    def file_state(self):
        result = {}
        for path in self.connection_dir.glob("*.nmconnection"):
            info = path.stat()
            try:
                attr = os.getxattr(path, "user.ride-test")
            except OSError:
                attr = None
            result[path.name] = (
                path.read_bytes(), info.st_uid, info.st_gid, info.st_mode & 0o777,
                info.st_mtime_ns, attr,
            )
        return result

    def run_shell(self, body, *, env=None):
        script = f'''source "{MODULE}"
ride_require_command() {{ command -v "$1" >/dev/null 2>&1 || ride_die "missing command $1"; }}
ride_die() {{ printf 'RIDE: %s\\n' "$*" >&2; exit 2; }}
entry={json.dumps(self.entry)}
{body}
'''
        return subprocess.run(
            ["bash", "-c", script], env=env or self.env,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )

    def test_remove_restore_repeat_observe_preserves_unrelated_profile(self):
        before = self.file_state()
        removed = self.run_shell('ride_vpn_profiles_change "$entry" absent; ride_vpn_profiles_observe "$entry"')
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual(removed.stdout.strip(), "absent")
        self.assertEqual({p.name for p in self.connection_dir.glob("*.nmconnection")}, {"unrelated.nmconnection"})

        restored = self.run_shell('ride_vpn_profiles_change "$entry" configured; ride_vpn_profiles_observe "$entry"')
        self.assertEqual(restored.returncode, 0, restored.stderr)
        self.assertEqual(restored.stdout.strip(), "configured")
        after = self.file_state()
        self.assertEqual(after, before)
        self.assertEqual((self.connection_dir / "selected-one.nmconnection").stat().st_mode & 0o777, 0o600)

    def test_active_selected_profile_refuses_before_snapshot_or_deletion(self):
        env = self.env.copy()
        env["NM_ACTIVE_UUIDS"] = UUIDS[0]
        result = self.run_shell('ride_vpn_profiles_change "$entry" absent', env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("active VPN profile", result.stderr)
        self.assertEqual(len(list(self.connection_dir.glob("*.nmconnection"))), 3)
        self.assertFalse(any(self.state_root.rglob("manifest.json")))

    def test_profile_activated_after_snapshot_refuses_and_cleans_snapshot(self):
        env = self.env.copy()
        env["NM_ACTIVATE_ON_QUERY"] = "2"
        env["NM_ACTIVATE_UUID"] = UUIDS[0]
        result = self.run_shell('ride_vpn_profiles_change "$entry" absent', env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing to remove active VPN profile", result.stderr)
        self.assertEqual(len(list(self.connection_dir.glob("*.nmconnection"))), 3)
        self.assertFalse(any(self.state_root.rglob("manifest.json")))

    def test_failed_second_delete_restores_first_and_cleans_snapshot(self):
        env = self.env.copy()
        env["NM_FAIL_DELETE_UUID"] = UUIDS[1]
        before = {p.name: p.read_bytes() for p in self.connection_dir.glob("*.nmconnection")}
        result = self.run_shell('ride_vpn_profiles_change "$entry" absent', env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("partial change was rolled back", result.stderr)
        after = {p.name: p.read_bytes() for p in self.connection_dir.glob("*.nmconnection")}
        self.assertEqual(after, before)
        self.assertFalse(any(self.state_root.rglob("manifest.json")))

    def test_failed_networkmanager_reload_rolls_back_removed_profiles(self):
        env = self.env.copy()
        env["NM_FAIL_RELOAD_ONCE"] = "1"
        before = self.file_state()
        result = self.run_shell('ride_vpn_profiles_change "$entry" absent', env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("the change was rolled back", result.stderr)
        self.assertEqual(self.file_state(), before)
        self.assertFalse(any(self.state_root.rglob("manifest.json")))

    def test_modified_snapshot_blocks_restore(self):
        removed = self.run_shell('ride_vpn_profiles_change "$entry" absent')
        self.assertEqual(removed.returncode, 0, removed.stderr)
        snapshot = next(self.state_root.rglob(f"{UUIDS[0]}.nmconnection"))
        snapshot.write_text(snapshot.read_text() + "# changed\n")
        result = self.run_shell('ride_vpn_profiles_change "$entry" configured')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exact VPN profile recovery state is unavailable", result.stderr)
        self.assertEqual({p.name for p in self.connection_dir.glob("*.nmconnection")}, {"unrelated.nmconnection"})

    def test_live_profile_change_after_snapshot_is_detected(self):
        helper = ROOT / "tools/networkmanager-vpn-state.py"
        state_dir = self.state_root / "direct-helper-test"
        snapshot = subprocess.run(
            ["python3", str(helper), "snapshot", "--connection-dir", str(self.connection_dir),
             "--state-dir", str(state_dir), "--uuid", UUIDS[0]],
            env=self.env, text=True, capture_output=True,
        )
        self.assertEqual(snapshot.returncode, 0, snapshot.stderr)
        args = ["python3", str(helper), "check-live", "--connection-dir", str(self.connection_dir),
                "--state-dir", str(state_dir), "--uuid", UUIDS[0]]
        unchanged = subprocess.run(args, env=self.env, text=True, capture_output=True)
        self.assertEqual(unchanged.returncode, 0, unchanged.stderr)
        path = self.connection_dir / "selected-one.nmconnection"
        path.write_text(path.read_text() + "# external change\n")
        changed = subprocess.run(args, env=self.env, text=True, capture_output=True)
        self.assertNotEqual(changed.returncode, 0)
        self.assertIn("changed since snapshot", changed.stderr)

    def test_duplicate_or_invalid_uuid_selection_refuses(self):
        for value in (f"{UUIDS[0]},{UUIDS[0]}", "not-a-uuid"):
            env = self.env.copy()
            self.entry = json.dumps({"selectedValue": value})
            result = self.run_shell('ride_vpn_profiles_change "$entry" absent', env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(len(list(self.connection_dir.glob("*.nmconnection"))), 3)

    def test_cli_accepts_uuid_list_for_plan_and_reports_supported_state(self):
        os_release = self.base / "os-release"
        os_release.write_text("ID=fedora\nVERSION_ID=44\nVARIANT_ID=workstation\n")
        env = self.env.copy()
        env["RIDE_OS_RELEASE_FILE"] = str(os_release)
        command = [
            str(ROOT / "ride.sh"), "set", "setting.networkmanager-vpn-profiles",
            "--state", "absent", "--value", f"{UUIDS[0]},{UUIDS[1]}", "--dry-run",
        ]
        planned = subprocess.run(command, env=env, text=True, capture_output=True)
        self.assertEqual(planned.returncode, 0, planned.stderr)
        self.assertIn("configured\tabsent:", planned.stdout)
        self.assertIn("\tsupported\t", planned.stdout)
        self.assertEqual(len(list(self.connection_dir.glob("*.nmconnection"))), 3)


if __name__ == "__main__":
    unittest.main()
