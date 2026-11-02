"""Pinned VeraCrypt publisher signature and RPM lifecycle checks."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/v3/providers.sh"
FINGERPRINT = "5069A233D55A0EEB174A5FC3821ACD02680D16DE"


class VeraCryptProviderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ride-veracrypt-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.calls = self.root / "calls.txt"
        self.entry = json.dumps({
            "id": "package.veracrypt",
            "packageName": "veracrypt",
            "signingFingerprint": FINGERPRINT,
            "sourceUri": "https://example.invalid/veracrypt.rpm",
            "signatureUri": "https://example.invalid/veracrypt.rpm.sig",
            "signingKeyUri": "https://example.invalid/key.asc",
        })

    def run_change(self, gpg_mode="valid", installed=False, dnf_mode="valid"):
        script = f"""set -euo pipefail
source {MODULE}
RIDE_OS_ID=fedora
ride_require_command() {{ :; }}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
rpm() {{
  printf 'rpm %s\\n' "$*" >> "$VC_CALLS"
  case "$*" in
    '-q --quiet veracrypt') [[ "$VC_INSTALLED" == 1 ]] ;;
    '-qp --qf %{{NAME}}\\n '*) printf 'veracrypt\\n' ;;
    *) return 2 ;;
  esac
}}
curl() {{
  printf 'curl %s\\n' "$*" >> "$VC_CALLS"
  output=${{!#}}
  printf 'mock artifact\\n' > "$output"
}}
gpg() {{
  printf 'gpg %s\\n' "$*" >> "$VC_CALLS"
  case "$*" in
    *'--with-colons --fingerprint'*) printf 'fpr:::::::::{FINGERPRINT}:\\n' ;;
    *'--verify'*) [[ "$VC_GPG_MODE" == valid ]] ;;
    *) return 0 ;;
  esac
}}
dnf() {{ printf 'dnf %s\\n' "$*" >> "$VC_CALLS"; [[ "$VC_DNF_MODE" == valid ]]; }}
ride_change_veracrypt "$VC_ENTRY" installed
"""
        env = os.environ.copy()
        env.update(VC_CALLS=str(self.calls), VC_ENTRY=self.entry,
                   VC_GPG_MODE=gpg_mode, VC_INSTALLED="1" if installed else "0",
                   VC_DNF_MODE=dnf_mode,
                   TMPDIR=str(self.root))
        return subprocess.run(["bash", "-c", script], env=env, text=True,
                              capture_output=True, check=False)

    def test_verified_rpm_is_installed_without_global_key_import(self):
        result = self.run_change()
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.calls.read_text(encoding="utf-8").splitlines()
        self.assertTrue(any(line.startswith("gpg --batch --homedir ") and "--import" in line for line in calls))
        self.assertTrue(any(line.startswith("gpg --batch --homedir ") and "--verify" in line for line in calls))
        self.assertTrue(any(line.startswith("dnf --setopt=localpkg_gpgcheck=0 install -y ") for line in calls))
        self.assertFalse(any("rpm --import" in line or "rpmkeys --import" in line for line in calls))
        self.assertFalse(list(self.root.glob("ride-veracrypt.*")))

    def test_bad_detached_signature_blocks_install(self):
        result = self.run_change(gpg_mode="invalid")
        self.assertEqual(result.returncode, 42)
        self.assertIn("detached signature verification failed", result.stderr)
        self.assertNotIn("dnf ", self.calls.read_text(encoding="utf-8"))

    def test_existing_install_is_unchanged(self):
        result = self.run_change(installed=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls.read_text(encoding="utf-8").splitlines(), ["rpm -q --quiet veracrypt"])

    def test_failed_dnf_transaction_cleans_verified_artifacts(self):
        result = self.run_change(dnf_mode="fail")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(list(self.root.glob("ride-veracrypt.*")))
        self.assertTrue(any(line.startswith("dnf ") for line in
                            self.calls.read_text(encoding="utf-8").splitlines()))

    def test_mounted_volume_blocks_package_removal_before_dnf(self):
        script = f"""set -euo pipefail
source {MODULE}
RIDE_OS_ID=fedora
ride_require_command() {{ :; }}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
rpm() {{ return 0; }}
veracrypt() {{ printf '1: /tmp/test.hc /dev/mapper/veracrypt1 /mnt/test\\n'; }}
dnf() {{ printf 'dnf %s\\n' "$*" >> "$VC_CALLS"; }}
ride_change_veracrypt "$VC_ENTRY" absent
"""
        env = os.environ.copy()
        env.update(VC_CALLS=str(self.calls), VC_ENTRY=self.entry)
        result = subprocess.run(["bash", "-c", script], env=env, text=True,
                                capture_output=True, check=False)
        self.assertEqual(result.returncode, 42)
        self.assertIn("unmount them before removing", result.stderr)
        self.assertFalse(self.calls.exists())

    def test_empty_mount_list_allows_package_removal(self):
        script = f"""set -euo pipefail
source {MODULE}
RIDE_OS_ID=fedora
ride_require_command() {{ :; }}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
rpm() {{ return 0; }}
veracrypt() {{ printf 'Error: No volumes mounted.\\n'; return 1; }}
dnf() {{ printf 'dnf %s\\n' "$*" >> "$VC_CALLS"; }}
ride_change_veracrypt "$VC_ENTRY" absent
"""
        env = os.environ.copy()
        env.update(VC_CALLS=str(self.calls), VC_ENTRY=self.entry)
        result = subprocess.run(["bash", "-c", script], env=env, text=True,
                                capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls.read_text(encoding="utf-8").splitlines(),
                         ["dnf remove -y veracrypt"])


if __name__ == "__main__":
    unittest.main()
