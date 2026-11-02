"""Mocked ownership and exact recovery checks for the sshd root-login policy."""

from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROVIDER = ROOT / "lib/v3/providers.sh"


class SshdRootLoginTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ride-sshd-root-login-")
        self.addCleanup(self.tmp.cleanup)
        self.dropin = Path(self.tmp.name) / "sshd_config.d/00-ride-root-login.conf"
        self.reloads = Path(self.tmp.name) / "reload-count"
        self.reloads.write_text("0\n", encoding="utf-8")

    def shell(self, body, *, effective_override=False):
        effective = "yes" if effective_override else None
        script = f'''set -euo pipefail
source {PROVIDER}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 1; }}
ride_error() {{ ride_die "$@"; }}
ride_require_command() {{ :; }}
ride_sshd_root_login_dropin() {{ printf '%s\\n' {str(self.dropin)!r}; }}
systemctl() {{
  case "$*" in
    'is-active sshd.service') printf 'active\\n';;
    'reload sshd.service') n=$(cat {str(self.reloads)!r}); printf '%s\\n' "$((n + 1))" > {str(self.reloads)!r};;
    *) return 8;;
  esac
}}
sshd() {{
  case "$1" in
    -t) return 0;;
    -T)
      if [[ -f {str(self.dropin)!r} ]]; then printf 'permitrootlogin {effective or 'no'}\\n';
      else printf 'permitrootlogin prohibit-password\\n'; fi;;
    *) return 8;;
  esac
}}
{body}
'''
        return subprocess.run(["bash", "-c", script], text=True, capture_output=True)

    def test_apply_repeat_remove_and_restore_prior_effective_policy(self):
        result = self.shell(f'''
[[ "$(ride_sshd_root_login_observe)" == absent ]]
ride_sshd_root_login_change configured
[[ "$(ride_sshd_root_login_observe)" == configured ]]
grep -Fx 'PermitRootLogin no' {str(self.dropin)!r}
ride_sshd_root_login_change configured
ride_sshd_root_login_change absent
[[ "$(ride_sshd_root_login_observe)" == absent ]]
test ! -e {str(self.dropin)!r}
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.reloads.read_text(encoding="utf-8").strip(), "2")

    def test_refuses_existing_dropin(self):
        self.dropin.parent.mkdir(parents=True)
        self.dropin.write_text("PermitRootLogin yes\n", encoding="utf-8")
        result = self.shell('ride_sshd_root_login_change configured')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("modified SSH root-login drop-in", result.stderr)

    def test_removes_owned_file_if_effective_policy_check_fails(self):
        result = self.shell('ride_sshd_root_login_change configured', effective_override=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("could not safely apply", result.stderr)
        self.assertFalse(self.dropin.exists())


if __name__ == "__main__":
    unittest.main()
