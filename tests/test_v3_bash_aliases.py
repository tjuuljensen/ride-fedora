"""Owned Bash alias fragments preserve existing user shell configuration."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/v3/bash_aliases.sh"
CATALOG = ROOT / "lib/v3/catalog.sh"


class BashAliasesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ride-bash-aliases-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.xdg = self.root / "state"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        eza = self.bin / "eza"
        eza.write_text("#!/bin/sh\nexit 0\n")
        eza.chmod(0o755)
        self.value = json.dumps(["ls-eza", "wanip", "wanip4", "wanip6"], separators=(",", ":"))
        self.entry = json.dumps({"id": "setting.bash-aliases", "selectedValue": self.value})

    def shell(self, body, extra=""):
        script = f"""set -euo pipefail
source {CATALOG}
source {MODULE}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
{extra}
{body}
"""
        env = os.environ.copy()
        env["HOME"] = str(self.home)
        env["XDG_STATE_HOME"] = str(self.xdg)
        env["PATH"] = f"{self.bin}:{env['PATH']}"
        return subprocess.run(["bash", "-c", script], env=env, text=True,
                              capture_output=True, check=False)

    def test_apply_repeat_status_and_remove_preserve_user_changes(self):
        rc = self.home / ".bashrc"
        aliases = self.home / ".bash_aliases"
        rc.write_text("# user bashrc\nexport USER_RC=1\n")
        aliases.write_text("# user aliases\nalias ll='ls -la'\n")
        result = self.shell(
            'ride_bash_aliases_observe "$TEST_ENTRY"\n'
            'ride_bash_aliases_change "$TEST_ENTRY" configured\n'
            'ride_bash_aliases_observe "$TEST_ENTRY"\n'
            'ride_bash_aliases_change "$TEST_ENTRY" configured\n'
            'printf "alias_file=%s\\n" "$(cat "$HOME/.bash_aliases")"\n'
            'printf "rc=%s\\n" "$(cat "$HOME/.bashrc")"\n'
            'printf "owner_mode=%s\\n" "$(stat -c %a "$(ride_bash_aliases_owner)")"\n'
            'printf "# later user rc edit\\n" >> "$HOME/.bashrc"\n'
            'printf "# later user alias edit\\n" >> "$HOME/.bash_aliases"\n'
            'ride_bash_aliases_change "$TEST_ENTRY" absent\n'
            'printf "after_aliases=%s\\n" "$(cat "$HOME/.bash_aliases")"\n'
            'printf "after_rc=%s\\n" "$(cat "$HOME/.bashrc")"',
            extra="TEST_ENTRY=" + json.dumps(self.entry),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("absent\nconfigured\n", result.stdout)
        self.assertIn("alias ls='eza'", result.stdout)
        self.assertIn("https://api64.ipify.org", result.stdout)
        self.assertIn("https://api.ipify.org", result.stdout)
        self.assertIn("https://api6.ipify.org", result.stdout)
        self.assertIn("owner_mode=600", result.stdout)
        after_aliases = result.stdout.split("after_aliases=", 1)[1].split("\nafter_rc=", 1)[0]
        after_rc = result.stdout.split("after_rc=", 1)[1]
        self.assertIn("alias ll='ls -la'", after_aliases)
        self.assertIn("later user alias edit", after_aliases)
        self.assertNotIn("RIDE managed Bash aliases", after_aliases)
        self.assertIn("export USER_RC=1", after_rc)
        self.assertIn("later user rc edit", after_rc)
        self.assertNotIn("RIDE managed Bash aliases", after_rc)
        self.assertFalse((self.xdg / "ride-fedora/owned/setting.bash-aliases.json").exists())

    def test_modified_owned_alias_block_refuses_removal(self):
        aliases = self.home / ".bash_aliases"
        aliases.write_text("# user's existing alias\n")
        result = self.shell(
            'ride_bash_aliases_change "$TEST_ENTRY" configured\n'
            'sed -i "s/alias ls=.eza./alias ls=ls/" "$HOME/.bash_aliases"\n'
            'ride_bash_aliases_change "$TEST_ENTRY" absent',
            extra="TEST_ENTRY=" + json.dumps(self.entry),
        )
        self.assertEqual(result.returncode, 42)
        self.assertIn("changed outside RIDE", result.stderr)
        self.assertTrue((self.xdg / "ride-fedora/owned/setting.bash-aliases.json").exists())

    def test_failure_adding_loader_rolls_back_alias_file_block(self):
        aliases = self.home / ".bash_aliases"
        rc = self.home / ".bashrc"
        aliases.write_text("# existing alias content\n")
        rc.write_text("# existing rc content\n")
        result = self.shell(
            'ride_bash_aliases_change "$TEST_ENTRY" configured',
            extra=("TEST_ENTRY=" + json.dumps(self.entry) + "\n" +
                   'ride_bash_aliases_insert_block() {\n'
                   '  if [[ "$1" == "$HOME/.bashrc" ]]; then return 1; fi\n'
                   '  ride_bash_aliases_insert_block_impl "$@"\n'
                   '}'),
        )
        self.assertEqual(result.returncode, 42)
        self.assertIn("cannot add owned Bash alias loader", result.stderr)
        self.assertEqual(aliases.read_text(), "# existing alias content\n")
        self.assertEqual(rc.read_text(), "# existing rc content\n")
        self.assertFalse((self.xdg / "ride-fedora/owned/setting.bash-aliases.json").exists())

    def test_unowned_alias_conflict_and_shell_syntax_values_are_rejected(self):
        (self.home / ".bash_aliases").write_text("alias ls='ls --color=auto'\n")
        conflict = self.shell(
            'ride_bash_aliases_change "$TEST_ENTRY" configured',
            extra="TEST_ENTRY=" + json.dumps(self.entry),
        )
        self.assertEqual(conflict.returncode, 42)
        self.assertIn("unowned definition: ls", conflict.stderr)
        invalid = json.dumps({"id": "setting.bash-aliases"})
        injection = json.dumps(["wanip'; touch /tmp/pwned; #"])
        rejected = self.shell(
            'ride_setting_value_valid "$TEST_ENTRY" "$TEST_VALUE"',
            extra="TEST_ENTRY=" + json.dumps(invalid) + "\nTEST_VALUE=" + json.dumps(injection),
        )
        self.assertNotEqual(rejected.returncode, 0)


if __name__ == "__main__":
    unittest.main()
