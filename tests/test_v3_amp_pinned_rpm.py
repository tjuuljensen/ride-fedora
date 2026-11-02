"""AMP RPM digest pin and disabled scriptlet lifecycle."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/v3/providers.sh"
SHA256 = "c766e78308df4ff29d703081b4e2477d70822deb5344c985a3502a2306d0396e"


class AmpPinnedRpmTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ride-amp-rpm-")
        self.addCleanup(self.temp.cleanup)
        self.calls = Path(self.temp.name) / "calls.txt"
        self.entry = json.dumps({
            "id": "package.amp-installer",
            "packageName": "ampinstmgr",
            "version": "2.8.0.10-2",
            "sourceUri": "https://cdn-repo.c7rs.com/ampinstmgr-2.8.0.10-2.x86_64.rpm",
            "sourceSha256": SHA256,
            "targets": {"fedora": {"architectures": ["x86_64"]}},
        })

    def run_shell(self, body):
        script = f"""set -euo pipefail
source {MODULE}
RIDE_OS_ID=fedora
TEST_CALLS={self.calls}
TEST_ENTRY={json.dumps(self.entry)}
TEST_INSTALLED=0
ride_require_command() {{ :; }}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
rpm() {{
  printf 'rpm %s\\n' "$*" >> "$TEST_CALLS"
  case "$*" in
    '-q --quiet ampinstmgr') [[ "$TEST_INSTALLED" == 1 ]] ;;
    '-qp --queryformat %{{NAME}} %{{VERSION}}-%{{RELEASE}} %{{ARCH}}'*) printf 'ampinstmgr 2.8.0.10-2 x86_64\\n' ;;
  esac
}}
curl() {{
  printf 'curl %s\\n' "$*" >> "$TEST_CALLS"
  while (($#)); do
    if [[ "$1" == --output ]]; then shift; printf 'rpm bytes\\n' > "$1"; fi
    shift
  done
}}
sha256sum() {{
  printf 'sha256sum %s\\n' "$*" >> "$TEST_CALLS"
  [[ "$1" == --check ]]
}}
dnf() {{
  printf 'dnf %s\\n' "$*" >> "$TEST_CALLS"
  case "$*" in *' install '*) TEST_INSTALLED=1 ;; *' remove '*) TEST_INSTALLED=0 ;; esac
}}
systemctl() {{
  printf 'systemctl %s\\n' "$*" >> "$TEST_CALLS"
  case "$1" in daemon-reload) return 0 ;; *) return 1 ;; esac
}}
{body}
"""
        return subprocess.run(["bash", "-c", script], text=True,
                              capture_output=True, check=False)

    def test_install_repeat_and_restore_suppress_amp_scriptlets(self):
        result = self.run_shell(
            'ride_change_amp_pinned_rpm "$TEST_ENTRY" installed\n'
            'ride_change_amp_pinned_rpm "$TEST_ENTRY" installed\n'
            'ride_change_amp_pinned_rpm "$TEST_ENTRY" absent\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.calls.read_text(encoding="utf-8")
        self.assertIn("--setopt=localpkg_gpgcheck=0 --setopt=tsflags=noscripts install -y", calls)
        self.assertIn("--setopt=tsflags=noscripts remove -y ampinstmgr", calls)
        self.assertIn("sha256sum --check", calls)
        self.assertEqual(calls.count("curl "), 1)
        self.assertEqual(calls.count("systemctl daemon-reload"), 2)


if __name__ == "__main__":
    unittest.main()
