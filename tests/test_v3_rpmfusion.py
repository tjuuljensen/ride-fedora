"""Focused tests for the RPM Fusion inverse dependency gate."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
import os
import tempfile


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib" / "v3" / "rpmfusion.sh"


class RpmFusionInverseGateTests(unittest.TestCase):
    def run_gate(self, records: str, rpm_status: int = 0) -> subprocess.CompletedProcess[str]:
        script = f'''\nsource {MODULE!s}\nrpm() {{\n  if [[ "$1" == "-qa" ]]; then\n    printf %s "$TEST_RPM_RECORDS"\n    return {rpm_status}\n  fi\n  return 0\n}}\nride_rpmfusion_has_foreign_packages\n'''
        env = os.environ | {"TEST_RPM_RECORDS": records}
        return subprocess.run(["bash", "-c", script], text=True, capture_output=True, check=False, env=env)

    def test_no_packages_signed_by_rpmfusion_allows_inverse(self) -> None:
        result = self.run_gate("ordinary\t(none)\nrpmfusion-free-release\tkey ID e06f8ecdd651ff2e\n")
        self.assertEqual(result.returncode, 1, result.stderr)

    def test_package_signed_by_free_or_nonfree_key_blocks_inverse(self) -> None:
        for key_id in ("e06f8ecdd651ff2e", "6a2af96194843c65"):
            with self.subTest(key_id=key_id):
                result = self.run_gate(f"codec\tkey ID {key_id}\n")
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_rpm_query_failure_is_distinct_from_no_matching_packages(self) -> None:
        result = self.run_gate("", rpm_status=2)
        self.assertEqual(result.returncode, 2, result.stderr)


class RpmFusionBootstrapTests(unittest.TestCase):
    def run_bootstrap(self, *, bad_fingerprint: bool = False, bad_signature: bool = False,
                      bad_digest: bool = False, collision: str = "") -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory(prefix="ride-rpmfusion-test-") as tempdir:
            key_dir = Path(tempdir) / "keys"
            key_dir.mkdir()
            for family in ("free", "nonfree"):
                (key_dir / f"RPM-GPG-KEY-rpmfusion-{family}-fedora-44").write_text("test key\n")
            env = os.environ | {
                "TEST_KEY_DIR": str(key_dir),
                "TEST_BAD_FINGERPRINT": "1" if bad_fingerprint else "0",
                "TEST_BAD_SIGNATURE": "1" if bad_signature else "0",
                "TEST_BAD_DIGEST": "1" if bad_digest else "0",
                "TEST_COLLISION": collision,
                "TEST_TEMP": tempdir,
            }
            script = f'''
source {MODULE!s}
ride_require_command() {{ :; }}
ride_rpmfusion_key_dir() {{ printf '%s\\n' "$TEST_KEY_DIR"; }}
ride_die() {{ printf 'DIE:%s\\n' "$*" >&2; exit 70; }}
ride_error() {{ printf 'ERROR:%s\\n' "$*" >&2; }}
gpg() {{
  if [[ "$TEST_BAD_FINGERPRINT" == 1 ]]; then printf 'fpr:::::::::BADFINGERPRINT:\\n';
  elif [[ "$*" == *nonfree* ]]; then printf 'fpr:::::::::79BDB88F9BBF73910FD4095B6A2AF96194843C65:\\n';
  else printf 'fpr:::::::::E9A491A3DE247814E7E067EAE06F8ECDD651FF2E:\\n'; fi
}}
curl() {{
  while (($#)); do if [[ "$1" == --output ]]; then : > "$2"; return; fi; shift; done
  return 1
}}
rpm() {{
  local args="$*" last="${{!#}}" family name
  case "$args" in
    "-q --quiet distribution-gpg-keys"|"-V distribution-gpg-keys"|*"--import "*) return 0 ;;
    *"--checksig --verbose "*)
      if [[ "$TEST_BAD_SIGNATURE" == 1 ]]; then printf 'NOKEY\\n'; return 1; fi
      if [[ "$last" == */free.rpm ]]; then printf 'key fingerprint: e9a491a3de247814e7e067eae06f8ecdd651ff2e: OK\\n';
      else printf 'key fingerprint: 79bdb88f9bbf73910fd4095b6a2af96194843c65: OK\\n'; fi
      if [[ "$TEST_BAD_DIGEST" == 1 ]]; then printf 'Payload SHA256 digest: BAD\\n';
      else printf 'Payload SHA256 digest: OK\\n'; fi ;;
    *"%{{NAME}} %{{VERSION}}-%{{RELEASE}} %{{LICENSE}} %{{ARCH}}"*)
      if [[ "$last" == */free.rpm ]]; then printf 'rpmfusion-free-release 44-3 BSD noarch';
      else printf 'rpmfusion-nonfree-release 44-3 BSD noarch'; fi ;;
    *"%{{FILENAMES}}"*)
      if [[ "$last" == */free.rpm ]]; then name=rpmfusion-free-release; else name=rpmfusion-nonfree-release; fi
      if [[ -n "$TEST_COLLISION" ]]; then printf '%s\\n' "$TEST_COLLISION"; else printf '%s\\n' "$TEST_TEMP/$name.repo"; fi ;;
    *) printf 'unexpected rpm call: %s\\n' "$args" >&2; return 99 ;;
  esac
}}
ride_rpmfusion_download_verify "$TEST_TEMP/downloads"
'''
            (Path(tempdir) / "downloads").mkdir()
            return subprocess.run(["bash", "-c", script], text=True, capture_output=True, check=False, env=env)

    def test_pinned_fingerprints_signatures_and_payloads_allow_bootstrap(self) -> None:
        result = self.run_bootstrap()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_unexpected_key_fingerprint_stops_before_download(self) -> None:
        result = self.run_bootstrap(bad_fingerprint=True)
        self.assertEqual(result.returncode, 70)
        self.assertIn("fingerprint mismatch", result.stderr)

    def test_bad_release_signature_stops_bootstrap(self) -> None:
        result = self.run_bootstrap(bad_signature=True)
        self.assertEqual(result.returncode, 70)
        self.assertIn("signature verification failed", result.stderr)

    def test_bad_payload_digest_stops_bootstrap(self) -> None:
        result = self.run_bootstrap(bad_digest=True)
        self.assertEqual(result.returncode, 70)
        self.assertIn("signature or payload verification failed", result.stderr)

    def test_preexisting_owned_package_path_is_refused(self) -> None:
        with tempfile.NamedTemporaryFile(prefix="ride-rpmfusion-collision-") as occupied:
            result = self.run_bootstrap(collision=occupied.name)
        self.assertEqual(result.returncode, 70)
        self.assertIn("path already exists outside RIDE ownership", result.stderr)

    def test_partial_release_pair_install_runs_package_rollback(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ride-rpmfusion-rollback-") as tempdir:
            log = Path(tempdir) / "dnf.log"
            script = f'''
source {MODULE!s}
mktemp() {{ /usr/bin/mktemp -d "$TEST_TMPDIR/rpmfusion.XXXXXXXX"; }}
ride_rpmfusion_guard() {{ :; }}
ride_rpmfusion_state() {{ printf 'absent\\n'; }}
ride_rpmfusion_download_verify() {{ :; }}
ride_rpmfusion_remove_installed_release_packages() {{
  dnf5 remove -y rpmfusion-free-release rpmfusion-nonfree-release
}}
rpm() {{ [[ "$1 $2 $3" == "-q --quiet rpmfusion-free-release" || "$1 $2 $3" == "-q --quiet rpmfusion-nonfree-release" ]]; }}
dnf5() {{ printf '%s\\n' "$*" >> "$TEST_DNF_LOG"; [[ " $* " != *" install "* ]]; }}
ride_rpmfusion_change configured
'''
            result = subprocess.run(
                ["bash", "-c", script], text=True, capture_output=True, check=False,
                env=os.environ | {"TEST_DNF_LOG": str(log), "TEST_TMPDIR": tempdir},
            )
            self.assertEqual(result.returncode, 1, result.stderr)
            calls = log.read_text().splitlines()
            self.assertEqual(len(calls), 2)
            self.assertIn(" install -y ", f" {calls[0]} ")
            self.assertEqual(calls[1], "remove -y rpmfusion-free-release rpmfusion-nonfree-release")

    def test_ownership_marker_failure_rolls_back_both_release_packages(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ride-rpmfusion-marker-rollback-") as tempdir:
            log = Path(tempdir) / "dnf.log"
            (Path(tempdir) / "free.repo").write_text("[rpmfusion-free]\ngpgcheck=1\n")
            (Path(tempdir) / "nonfree.repo").write_text("[rpmfusion-nonfree]\ngpgcheck=1\n")
            script = f'''
source {MODULE!s}
mktemp() {{ /usr/bin/mktemp -d "$TEST_TMPDIR/rpmfusion.XXXXXXXX"; }}
ride_rpmfusion_guard() {{ :; }}
ride_rpmfusion_state() {{ printf 'absent\\n'; }}
ride_rpmfusion_download_verify() {{ :; }}
ride_rpmfusion_owned_files_ok() {{ :; }}
ride_rpmfusion_write_marker() {{ return 1; }}
ride_rpmfusion_remove_installed_release_packages() {{ dnf5 remove -y rpmfusion-free-release rpmfusion-nonfree-release; }}
rpm() {{ printf '%s\\n' "$TEST_TMPDIR/free.repo" "$TEST_TMPDIR/nonfree.repo"; }}
dnf5() {{ printf '%s\\n' "$*" >> "$TEST_DNF_LOG"; return 0; }}
ride_rpmfusion_change configured
'''
            result = subprocess.run(
                ["bash", "-c", script], text=True, capture_output=True, check=False,
                env=os.environ | {"TEST_DNF_LOG": str(log), "TEST_TMPDIR": tempdir},
            )
            self.assertEqual(result.returncode, 1, result.stderr)
            calls = log.read_text().splitlines()
            self.assertIn("install -y", f" {calls[0]} ")
            self.assertEqual(
                calls[1],
                "remove -y rpmfusion-free-release rpmfusion-nonfree-release",
            )


if __name__ == "__main__":
    unittest.main()
