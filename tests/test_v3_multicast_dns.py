"""Owned authselect-feature lifecycle checks for MulticastDNS."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROVIDER = ROOT / "lib/v3/providers.sh"


class MulticastDnsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ride-mdns-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.current = self.root / "current"
        self.current.write_text("local with-silent-lastlog with-mdns4\n", encoding="utf-8")
        self.marker = self.root / "state" / "multicast-dns.json"
        self.valid = self.root / "valid"
        self.valid.touch()
        self.authselect = self.bin / "authselect"
        self.authselect.write_text("""#!/usr/bin/env bash
set -euo pipefail
case "$*" in
  'check') test -e "$RIDE_TEST_AUTHSELECT_VALID" ;;
  'current --raw') cat "$RIDE_TEST_AUTHSELECT_CURRENT" ;;
  'list-features local') printf '%s\\n' with-mdns4 with-mdns6 with-silent-lastlog ;;
  'enable-feature with-mdns4')
    sed -i 's/$/ with-mdns4/' "$RIDE_TEST_AUTHSELECT_CURRENT" ;;
  'disable-feature with-mdns4')
    sed -i 's/ with-mdns4$//' "$RIDE_TEST_AUTHSELECT_CURRENT" ;;
  *) printf 'unexpected authselect command: %s\\n' "$*" >&2; exit 2 ;;
esac
""", encoding="utf-8")
        self.authselect.chmod(0o755)

    def shell(self, body):
        script = f'''set -euo pipefail
source {PROVIDER}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 1; }}
RIDE_TEST_MODE=1
RIDE_TEST_NSSWITCH_MARKER={str(self.marker)!r}
{body}
'''
        env = os.environ.copy()
        env["PATH"] = f"{self.bin}:{env['PATH']}"
        env["RIDE_TEST_AUTHSELECT_CURRENT"] = str(self.current)
        env["RIDE_TEST_AUTHSELECT_VALID"] = str(self.valid)
        return subprocess.run(["bash", "-c", script], env=env, text=True,
                              capture_output=True, check=False)

    def test_disable_repeat_and_exact_restore(self):
        result = self.shell('''
ride_nsswitch_mdns_change disabled
ride_nsswitch_mdns_observe
ride_nsswitch_mdns_change disabled
ride_nsswitch_mdns_change enabled
ride_nsswitch_mdns_observe
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["disabled", "enabled"])
        self.assertEqual(self.current.read_text(encoding="utf-8"),
                         "local with-silent-lastlog with-mdns4\n")
        self.assertFalse(self.marker.exists())

    def test_external_authselect_change_blocks_recovery(self):
        result = self.shell('''
ride_nsswitch_mdns_change disabled
printf '%s\\n' 'local with-silent-lastlog with-mdns6' > "$RIDE_TEST_AUTHSELECT_CURRENT"
ride_nsswitch_mdns_change enabled
''')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("changed outside RIDE", result.stderr)
        self.assertEqual(self.current.read_text(encoding="utf-8"),
                         "local with-silent-lastlog with-mdns6\n")
        self.assertTrue(self.marker.exists())

    def test_unmanaged_authselect_configuration_refuses_mutation(self):
        self.valid.unlink()
        before = self.current.read_text(encoding="utf-8")
        result = self.shell("ride_nsswitch_mdns_change disabled")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid or unmanaged", result.stderr)
        self.assertEqual(self.current.read_text(encoding="utf-8"), before)
        self.assertFalse(self.marker.exists())

    def test_marker_records_exact_profile_selection(self):
        result = self.shell("ride_nsswitch_mdns_change disabled")
        self.assertEqual(result.returncode, 0, result.stderr)
        marker = json.loads(self.marker.read_text(encoding="utf-8"))
        self.assertEqual(marker["priorCurrent"], "local with-silent-lastlog with-mdns4")
        self.assertEqual(marker["managedCurrent"], "local with-silent-lastlog")
        self.assertEqual(marker["desired"], "disabled")
