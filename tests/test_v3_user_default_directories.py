"""Owned lifecycle checks for the optional ~/bin and ~/git defaults."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/v3/providers.sh"


class UserDefaultDirectoriesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ride-user-dirs-")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "home"
        self.home.mkdir()
        self.marker = self.home / ".local/share/ride-fedora/owned-directories/package.user-default-directories.json"

    def shell(self, body):
        script = f"""set -euo pipefail
source {MODULE}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
{body}
"""
        env = os.environ.copy()
        env["HOME"] = str(self.home)
        return subprocess.run(["bash", "-c", script], env=env, text=True,
                              capture_output=True, check=False)

    def test_preserves_existing_directory_and_removes_only_created_empty_one(self):
        git = self.home / "git"
        git.mkdir()
        sentinel = git / "owned-by-user.txt"
        sentinel.write_text("keep\n", encoding="utf-8")
        result = self.shell(
            'ride_user_default_directories_observe\n'
            'ride_user_default_directories_change installed\n'
            'ride_user_default_directories_observe\n'
            'ride_user_default_directories_change installed\n'
            'ride_user_default_directories_change absent\n'
            'ride_user_default_directories_observe\n'
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["absent", "installed", "absent"])
        self.assertTrue(sentinel.exists())
        self.assertFalse((self.home / "bin").exists())
        self.assertFalse(self.marker.exists())

    def test_nonempty_created_directory_is_preserved_until_user_cleans_it(self):
        result = self.shell(
            'ride_user_default_directories_change installed\n'
            'printf data > "$HOME/bin/tool"\n'
            'ride_user_default_directories_change absent'
        )
        self.assertEqual(result.returncode, 42)
        self.assertTrue((self.home / "bin/tool").exists())
        self.assertTrue(self.marker.exists())
        (self.home / "bin/tool").unlink()
        result = self.shell('ride_user_default_directories_change absent')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.home / "bin").exists())
        self.assertFalse(self.marker.exists())

    def test_symlink_conflict_fails_closed_before_creating_other_directory(self):
        target = self.home.parent / "outside"
        target.mkdir()
        (self.home / "git").symlink_to(target, target_is_directory=True)
        result = self.shell('ride_user_default_directories_change installed')
        self.assertEqual(result.returncode, 42)
        self.assertFalse((self.home / "bin").exists())
        self.assertFalse(self.marker.exists())


if __name__ == "__main__":
    unittest.main()
