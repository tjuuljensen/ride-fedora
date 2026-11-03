"""Mock the ExpressVPN signed local installer and RIDE-owned recovery wrapper."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
FINGERPRINT = "1D0B09AD6C93FEE93FDDBD9DAFF2A1415F6A3A38"
SHA256 = "f784af6628564f4fcb0a82064d4dc1f22520c3c917bb1c882bd61eb621b31efb"


class ExpressVPNWrapperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.app = self.root / "opt/expressvpn"
        self.state = self.root / "var/lib/ride-fedora/expressvpn"
        self.artifacts = self.root / "artifacts"
        self.artifacts.mkdir()
        self.unit = self.root / "systemd/expressvpn-service.service"
        self.link = self.root / "systemd/wants/expressvpn-service.service"
        self.desktop = self.root / "applications/expressvpn.desktop"
        self.cli = self.root / "bin-links/expressvpn"
        self.ctl = self.root / "bin-links/expressvpnctl"
        self.nm = self.root / "NetworkManager/conf.d/wgexpressvpn.conf"
        self.nm.parent.mkdir(parents=True)
        self.nm.write_text("owner NM configuration\n")
        self.routes = self.root / "iproute2/rt_tables"
        self.routes.parent.mkdir(parents=True)
        self.routes.write_text("255 local\nowner table\n")
        self.root_config = self.root / "root/.config/expressvpn"
        self.root_config.mkdir(parents=True)
        (self.root_config / "preferences").write_text("owner preference\n")
        self.rules = self.root / "ip-rules"
        self.rules.write_text("100: from all lookup main\n")

        self.entry = next(
            item for item in json.loads((ROOT / "catalog/operations.json").read_text())["operations"]
            if item["id"] == "package.expressvpn"
        )
        self.entry_path = self.root / "entry.json"
        self.entry_path.write_text(json.dumps(self.entry))
        installer = self.artifacts / self.entry["assetName"]
        installer.write_text("mock verified installer\n")
        installer.chmod(0o755)
        (self.artifacts / self.entry["signatureAssetName"]).write_text("mock signature\n")
        (self.artifacts / self.entry["signingKeyAssetName"]).write_text("mock key\n")

        self._command("sha256sum", f'''#!/usr/bin/env bash
set -eu
for arg in "$@"; do
  if [[ "$arg" == *{self.entry["assetName"]} ]]; then
    printf '{SHA256}  %s\\n' "$arg"
    exit 0
  fi
done
exec /usr/bin/sha256sum "$@"
''')
        self._command("gpg", f'''#!/usr/bin/env bash
set -eu
case " $* " in
  *" --import "*) exit 0 ;;
  *" --with-colons "*) printf 'pub:::::::::\\nfpr:::::::::{FINGERPRINT}:\\n' ;;
  *" --status-fd 1 --verify "*) printf '[GNUPG:] VALIDSIG {FINGERPRINT} 20260922 0 4 0 1 10 00\\n' ;;
  *) exit 2 ;;
esac
''')
        self._command("ip", f'''#!/usr/bin/env bash
set -eu
rules={self.rules}
if [[ $1 == -o && $2 == rule && $3 == show ]]; then cat "$rules"; exit 0; fi
if [[ $1 == rule && $2 == add && $3 == priority ]]; then
  shift 3
  priority=$1
  shift
  printf '%s: %s\\n' "$priority" "$*" >> "$rules"
  exit 0
fi
if [[ $1 == rule && $2 == del ]]; then
  case "$*" in
    *"priority 50 lookup main suppress_prefixlength 1"*) sed -i '/^50: from all lookup main suppress_prefixlength 1$/d' "$rules" ;;
    *"priority 70 fwmark 0x3214 lookup evpnFwdrt"*) sed -i '/^70: from all fwmark 0x3214 lookup evpnFwdrt$/d' "$rules" ;;
    *) exit 2 ;;
  esac
  exit 0
fi
exit 2
''')
        self._command("systemctl", '''#!/usr/bin/env bash
set -eu
case "$1" in
  is-enabled) printf 'disabled\\n' ;;
  is-active) printf 'inactive\\n' ;;
  disable|daemon-reload|reset-failed) exit 0 ;;
  *) exit 2 ;;
esac
''')
        self._command("dnf", "#!/usr/bin/env bash\nexit 0\n")
        self._command("rpm", "#!/usr/bin/env bash\nexit 0\n")
        self._command("stat", "#!/usr/bin/env bash\nexec /usr/bin/stat \"$@\"\n")
        self._command("tar", "#!/usr/bin/env bash\nexec /usr/bin/tar \"$@\"\n")
        self._command("expressvpn-installer", self._installer_script())
        # Use the wrapper script as the staged .run so the test can produce a
        # deterministic mock app while sha256sum supplies the pinned digest.
        installer.write_text(self._installer_script())
        installer.chmod(0o755)

        self.env = os.environ.copy()
        self.env.update({
            "PATH": f"{self.bin}:{os.environ['PATH']}",
            "RIDE_ROOT": str(ROOT),
            "RIDE_TEST_MODE": "1",
            "RIDE_OS_ID": "fedora",
            "RIDE_OS_VERSION": "44",
            "RIDE_ARCH": "x86_64",
            "RIDE_EXPRESSVPN_STATE_DIR": str(self.state),
            "RIDE_EXPRESSVPN_ARTIFACT_DIR": str(self.artifacts),
            "RIDE_EXPRESSVPN_APP_ROOT": str(self.app),
            "RIDE_EXPRESSVPN_SERVICE_UNIT": str(self.unit),
            "RIDE_EXPRESSVPN_SERVICE_LINK": str(self.link),
            "RIDE_EXPRESSVPN_DESKTOP_ENTRY": str(self.desktop),
            "RIDE_EXPRESSVPN_CLI_LINK": str(self.cli),
            "RIDE_EXPRESSVPN_CTL_LINK": str(self.ctl),
            "RIDE_EXPRESSVPN_NM_CONFIG": str(self.nm),
            "RIDE_EXPRESSVPN_RT_TABLES": str(self.routes),
            "RIDE_EXPRESSVPN_ROOT_CONFIG": str(self.root_config),
            "RIDE_TEST_VPN_CONNECTED": "0",
        })

    def _command(self, name, content):
        path = self.bin / name
        path.write_text(content)
        path.chmod(0o755)
        return path

    def _installer_script(self):
        return f'''#!/usr/bin/env bash
set -eu
mkdir -p "{self.app}/bin" "{self.app}/lib" "{self.root_config}"
mkdir -p "$(dirname "{self.unit}")"
cat > "{self.app}/bin/expressvpnctl" <<'CTL'
#!/usr/bin/env bash
[[ ${{RIDE_TEST_VPN_CONNECTED:-0}} == 1 ]] && echo "Connected" || echo "Not connected"
CTL
cat > "{self.app}/bin/expressvpn-uninstall.sh" <<'UNINSTALL'
#!/usr/bin/env bash
read -r answer
[[ $answer == y ]] || exit 3
rm -rf "{self.app}" "{self.root_config}"
rm -f "{self.nm}" "{self.desktop}" "{self.cli}" "{self.ctl}"
UNINSTALL
chmod 0755 "{self.app}/bin/expressvpnctl" "{self.app}/bin/expressvpn-uninstall.sh"
printf 'Description=ExpressVPN daemon\\nExecStart={self.app}/bin/expressvpn-daemon\\nEnvironment="LD_LIBRARY_PATH={self.app}/lib"\\n' > "{self.unit}"
mkdir -p "$(dirname "{self.link}")" "$(dirname "{self.desktop}")" "$(dirname "{self.cli}")"
ln -s "{self.unit}" "{self.link}"
ln -s "{self.app}/expressvpn.desktop" "{self.desktop}"
ln -s "{self.app}/bin/expressvpn" "{self.cli}"
ln -s "{self.app}/bin/expressvpnctl" "{self.ctl}"
printf 'installer-written NM\\n' > "{self.nm}"
printf '255 local\\n202 evpnFwdrt\\n' > "{self.routes}"
printf '50: from all lookup main suppress_prefixlength 1\\n70: from all fwmark 0x3214 lookup evpnFwdrt\\n' > "{self.rules}"
printf 'installer-written root config\\n' > "{self.root_config}/preferences"
'''

    def _ride(self, code, env=None):
        script = (
            'source "$RIDE_ROOT/lib/v3/common.sh"; '
            'source "$RIDE_ROOT/lib/v3/expressvpn.sh"; '
            f'ENTRY=$(cat {self.entry_path}); {code}'
        )
        return subprocess.run(["bash", "-c", script], env=env or self.env,
                              text=True, capture_output=True, check=False)

    def test_install_repeat_observe_remove_restores_existing_state(self):
        nm_before = self.nm.read_bytes()
        routes_before = self.routes.read_bytes()
        root_before = (self.root_config / "preferences").read_bytes()
        installed = self._ride('ride_expressvpn_change "$ENTRY" installed')
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual(self._ride('ride_expressvpn_observe').stdout.strip(), "installed")
        self.assertEqual(self._ride('ride_expressvpn_change "$ENTRY" installed').returncode, 0)
        removed = self._ride('ride_expressvpn_change "$ENTRY" absent')
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual(self.nm.read_bytes(), nm_before)
        self.assertEqual(self.routes.read_bytes(), routes_before)
        self.assertEqual((self.root_config / "preferences").read_bytes(), root_before)
        self.assertEqual(self.rules.read_text(), "100: from all lookup main\n")
        self.assertFalse(self.app.exists())
        self.assertFalse(self.unit.exists())
        self.assertFalse(self.link.exists())
        self.assertFalse(self.state.exists())
        self.assertEqual(self._ride('ride_expressvpn_observe').stdout.strip(), "absent")

    def test_remove_refuses_connected_client_and_preserves_owned_record(self):
        installed = self._ride('ride_expressvpn_change "$ENTRY" installed')
        self.assertEqual(installed.returncode, 0, installed.stderr)
        connected = self._ride('ride_expressvpn_change "$ENTRY" absent',
                               self.env | {"RIDE_TEST_VPN_CONNECTED": "1"})
        self.assertNotEqual(connected.returncode, 0)
        self.assertIn("connected", connected.stderr)
        self.assertTrue(self.state.joinpath("manifest.json").exists())
        self.assertTrue(self.app.exists())

    def test_modified_owned_configuration_blocks_removal(self):
        installed = self._ride('ride_expressvpn_change "$ENTRY" installed')
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.nm.write_text("changed by owner after install\n")
        removed = self._ride('ride_expressvpn_change "$ENTRY" absent')
        self.assertNotEqual(removed.returncode, 0)
        self.assertIn("preserving it", removed.stderr)
        self.assertEqual(self.nm.read_text(), "changed by owner after install\n")
        self.assertTrue(self.state.joinpath("manifest.json").exists())

    def test_missing_preexisting_path_blocks_vendor_uninstall(self):
        installed = self._ride('ride_expressvpn_change "$ENTRY" installed')
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.nm.unlink()
        removed = self._ride('ride_expressvpn_change "$ENTRY" absent')
        self.assertNotEqual(removed.returncode, 0)
        self.assertIn("recovery path disappeared", removed.stderr)
        self.assertTrue(self.app.exists())
        self.assertTrue(self.state.joinpath("manifest.json").exists())

    def test_repeat_install_refuses_incomplete_owned_app_files(self):
        installed = self._ride('ride_expressvpn_change "$ENTRY" installed')
        self.assertEqual(installed.returncode, 0, installed.stderr)
        (self.app / "bin/expressvpnctl").unlink()
        repeated = self._ride('ride_expressvpn_change "$ENTRY" installed')
        self.assertNotEqual(repeated.returncode, 0)
        self.assertIn("installed files are incomplete", repeated.stderr)

    def test_bad_catalog_identity_is_rejected_before_artifact_access(self):
        bad = dict(self.entry, sourceSha256="0" * 64)
        bad_path = self.root / "bad-entry.json"
        bad_path.write_text(json.dumps(bad))
        result = subprocess.run(
            ["bash", "-c",
             'source "$RIDE_ROOT/lib/v3/common.sh"; source "$RIDE_ROOT/lib/v3/expressvpn.sh"; '
             'ENTRY=$(cat "$1"); ride_expressvpn_change "$ENTRY" installed',
             "expressvpn-bad-identity", str(bad_path)],
            env=self.env, text=True, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("catalog identity is invalid", result.stderr)
        self.assertFalse(self.state.exists())

    def test_preexisting_expressvpn_priority_rule_blocks_install_without_changing_it(self):
        rule = "50: from all lookup main suppress_prefixlength 1\n"
        self.rules.write_text(rule)
        result = self._ride('ride_expressvpn_change "$ENTRY" installed')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("policy-routing entries conflict", result.stderr)
        self.assertEqual(self.rules.read_text(), rule)
        self.assertFalse(self.state.exists())


if __name__ == "__main__":
    unittest.main()
