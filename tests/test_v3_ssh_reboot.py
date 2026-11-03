"""Mocked ownership, command scope, and exact recovery for SSH reboot sudoers."""

from pathlib import Path
import subprocess
import tempfile
import unittest
import os

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/v3/ssh_reboot.sh"


class SshRebootSudoersTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ride-ssh-reboot-")
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name) / "sudoers.d"
        self.directory.mkdir()
        self.file = self.directory / "allowsshreboot_ride-test"

    def test_cli_requires_explicit_valid_principal_for_dry_run(self):
        os_release = Path(self.tmp.name) / "os-release"
        os_release.write_text('ID=fedora\nVERSION_ID="44"\nVARIANT_ID=workstation\n', encoding="utf-8")
        binary = Path(self.tmp.name) / "bin"
        binary.mkdir()
        stat = binary / "stat"
        stat.write_text("#!/bin/sh\nprintf '0 0 755\\n'\n", encoding="utf-8")
        stat.chmod(0o755)
        getent = binary / "getent"
        getent.write_text(
            "#!/bin/sh\n"
            "[ \"$1\" = passwd ] && [ \"$2\" = ride-test ] || exit 2\n"
            "printf 'ride-test:x:1000:1000::/home/ride-test:/bin/bash\\n'\n",
            encoding="utf-8",
        )
        getent.chmod(0o755)
        env = os.environ | {
            "PATH": f"{binary}:{os.environ['PATH']}",
            "RIDE_TEST_MODE": "1",
            "RIDE_OS_RELEASE_FILE": str(os_release),
            "RIDE_TEST_SSH_REBOOT_DIR": str(self.directory),
        }
        command = [str(ROOT / "ride.sh"), "set", "setting.ssh-reboot", "--state", "configured"]
        missing = subprocess.run(command + ["--dry-run"], env=env, text=True, capture_output=True)
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("requires --value", missing.stderr)
        invalid = subprocess.run(command + ["--value", "bad user", "--dry-run"], env=env,
                                 text=True, capture_output=True)
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("invalid value", invalid.stderr)
        valid = subprocess.run(command + ["--value", "ride-test", "--dry-run"], env=env,
                                text=True, capture_output=True)
        self.assertEqual(valid.returncode, 0, valid.stderr)
        self.assertIn("setting.ssh-reboot", valid.stdout)
        self.assertIn("configured:ride-test", valid.stdout)

    def shell(self, body, *, visudo="return 0"):
        script = f'''set -euo pipefail
source {MODULE}
RIDE_TEST_MODE=1
RIDE_TEST_SSH_REBOOT_DIR={self.directory!s}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 2; }}
ride_require_command() {{ :; }}
getent() {{ [[ "$1" == passwd && "$2" == ride-test ]] && printf 'ride-test:x:1000:1000::/home/ride-test:/bin/bash\\n'; }}
stat() {{ printf '0 0 440\\n'; }}
chown() {{ :; }}
visudo() {{ {visudo}
}}
entry='{{"id":"setting.ssh-reboot","handler":"ssh-reboot-sudoers","selectedValue":"ride-test"}}'
{body}
'''
        return subprocess.run(["bash", "-c", script], text=True, capture_output=True)

    def test_apply_repeat_and_exact_remove(self):
        result = self.shell(f'''
[[ "$(ride_ssh_reboot_observe "$entry")" == absent ]]
ride_ssh_reboot_change "$entry" configured
[[ "$(ride_ssh_reboot_observe "$entry")" == configured ]]
grep -Fx 'ride-test ALL=(root) NOPASSWD: /usr/bin/systemctl reboot' {str(self.file)!r}
ride_ssh_reboot_change "$entry" configured
ride_ssh_reboot_change "$entry" absent
[[ "$(ride_ssh_reboot_observe "$entry")" == absent ]]
test ! -e {str(self.file)!r}
''')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_refuses_and_preserves_seeded_file(self):
        self.file.write_text("ride-test ALL=(root) NOPASSWD: ALL\n", encoding="utf-8")
        result = self.shell(f'ride_ssh_reboot_change "$entry" configured\n')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing a pre-existing or modified", result.stderr)
        self.assertEqual(self.file.read_text(encoding="utf-8"), "ride-test ALL=(root) NOPASSWD: ALL\n")

    def test_refuses_external_modification_before_restore(self):
        result = self.shell(f'''
ride_ssh_reboot_change "$entry" configured
chmod 0644 {str(self.file)!r}
printf 'ride-test ALL=(root) NOPASSWD: ALL\\n' > {str(self.file)!r}
ride_ssh_reboot_change "$entry" absent
''')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing a pre-existing or modified", result.stderr)
        self.assertIn("NOPASSWD: ALL", self.file.read_text(encoding="utf-8"))

    def test_rolls_back_if_complete_policy_validation_fails_after_install(self):
        result = self.shell(
            f'ride_ssh_reboot_change "$entry" configured\n',
            visudo='''
  if [[ "$*" == "-c" ]]; then
    count=${VISUDO_COUNT:-0}; count=$((count + 1)); export VISUDO_COUNT=$count
    [[ "$count" -ne 2 ]] || return 1
  fi
  return 0
''',
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rolled back", result.stderr)
        self.assertFalse(self.file.exists())

    def test_refuses_root_and_invalid_principals(self):
        result = self.shell('''
bad=$(jq -nc '{id:"setting.ssh-reboot",handler:"ssh-reboot-sudoers",selectedValue:"root"}')
ride_ssh_reboot_change "$bad" configured
''')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("non-root Linux username", result.stderr)

    @unittest.skipIf(os.geteuid() == 0, "requires an unprivileged test process")
    def test_observation_reports_root_requirement_without_escalating(self):
        script = f'''set -euo pipefail
source {MODULE}
entry='{{"id":"setting.ssh-reboot","handler":"ssh-reboot-sudoers","selectedValue":"ride-test"}}'
ride_ssh_reboot_observe "$entry"
'''
        result = subprocess.run(["bash", "-c", script], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "requires-root")


if __name__ == "__main__":
    unittest.main()
