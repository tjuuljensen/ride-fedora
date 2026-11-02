"""Owned external DNF repository and RPM application lifecycle tests."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/v3/providers.sh"
FINGERPRINT = "BC528686B50D79E339D3721CEB3E94ADBE1229CF"
TAILSCALE_FINGERPRINT = "2596A99EAAB33821893C0A79458CA832957F5868"
PLEX_FINGERPRINT = "6EFFEB478A6559D75C7C4FE706C521790B9CFFDE"


class PublisherRepoRpmTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ride-publisher-repo-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repos = self.root / "repos"
        self.owners = self.root / "owners"
        self.repos.mkdir()
        self.calls = self.root / "calls.txt"
        self.entry = json.dumps({
            "id": "package.visual-studio-code",
            "packageName": "code",
            "repositoryId": "ride-vscode",
            "repositoryFile": "ride-vscode.repo",
            "repositoryBaseUrl": "https://packages.microsoft.com/yumrepos/vscode/",
            "repositoryKeyUri": "https://packages.microsoft.com/keys/microsoft.asc",
            "repositoryKeyFingerprint": FINGERPRINT,
        })
        self.plaso_entry = json.dumps({
            "id": "package.plaso",
            "packageName": "plaso-tools",
            "repositoryId": "ride-gift-stable",
            "repositoryFile": "ride-gift-stable.repo",
            "repositoryBaseUrl": "https://download.copr.fedorainfracloud.org/results/@gift/stable/fedora-$releasever-$basearch/",
            "repositoryKeyUri": "https://download.copr.fedorainfracloud.org/results/@gift/stable/pubkey.gpg",
        })
        self.tailscale_entry = json.dumps({
            "id": "package.tailscale",
            "packageName": "tailscale",
            "repositoryId": "ride-tailscale",
            "repositoryFile": "ride-tailscale.repo",
            "repositoryBaseUrl": "https://pkgs.tailscale.com/stable/fedora/$basearch",
            "repositoryKeyUri": "https://pkgs.tailscale.com/stable/fedora/repo.gpg",
            "repositoryKeyFingerprint": TAILSCALE_FINGERPRINT,
        })
        self.plex_entry = json.dumps({
            "id": "package.plex-server",
            "packageName": "plexmediaserver",
            "repositoryId": "ride-plex-server",
            "repositoryFile": "ride-plex-server.repo",
            "repositoryBaseUrl": "https://repo.plex.tv/rpm/",
            "repositoryKeyUri": "https://downloads.plex.tv/plex-keys/PlexSign.v2.key",
            "repositoryKeyFingerprint": PLEX_FINGERPRINT,
        })

    def shell(self, body, *, installed=False):
        script = f"""set -euo pipefail
source {MODULE}
RIDE_OS_ID=fedora
ride_require_command() {{ :; }}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 42; }}
ride_publisher_repo_file() {{ printf '%s/%s\\n' "$TEST_REPOS" "$TEST_REPO_FILE"; }}
ride_publisher_repo_owner_file() {{ printf '%s/%s.sha256\\n' "$TEST_OWNERS" "$TEST_REPO_ID"; }}
rpm() {{
  printf 'rpm %s\\n' "$*" >> "$TEST_CALLS"
  [[ "$TEST_INSTALLED" == 1 ]]
}}
curl() {{
  printf 'curl %s\\n' "$*" >> "$TEST_CALLS"
  printf 'mock key\\n' > "${{!#}}"
}}
gpg() {{
  printf 'gpg %s\\n' "$*" >> "$TEST_CALLS"
  case "$*" in
    *'--with-colons --fingerprint'*) printf 'fpr:::::::::{FINGERPRINT}:\\n'; printf 'fpr:::::::::{TAILSCALE_FINGERPRINT}:\\n'; printf 'fpr:::::::::{PLEX_FINGERPRINT}:\\n' ;;
    *) return 0 ;;
  esac
}}
dnf() {{
  printf 'dnf %s\\n' "$*" >> "$TEST_CALLS"
  case "$*" in
    *' install '*) TEST_INSTALLED=1 ;;
    *' remove '*) TEST_INSTALLED=0 ;;
  esac
}}
{body}
"""
        env = os.environ.copy()
        selected = json.loads(os.environ.get("TEST_ENTRY_OVERRIDE", self.entry))
        env.update(TEST_REPOS=str(self.repos), TEST_OWNERS=str(self.owners),
                   TEST_CALLS=str(self.calls), TEST_ENTRY=os.environ.get("TEST_ENTRY_OVERRIDE", self.entry),
                   TEST_REPO_FILE=selected["repositoryFile"],
                   TEST_REPO_ID=selected["repositoryId"],
                   TEST_INSTALLED="1" if installed else "0")
        return subprocess.run(["bash", "-c", script], env=env, text=True,
                              capture_output=True, check=False)

    def test_create_install_repeat_remove_owns_only_repository_file(self):
        result = self.shell(
            'ride_change_publisher_repo_rpm "$TEST_ENTRY" installed\n'
            'ride_publisher_repo_content "$TEST_ENTRY" > "$TEST_REPOS/expected"\n'
            'test "$(cat "$(ride_publisher_repo_file "$TEST_ENTRY")")" = "$(cat "$TEST_REPOS/expected")"\n'
            'test -f "$(ride_publisher_repo_owner_file "$TEST_ENTRY")"\n'
            'ride_change_publisher_repo_rpm "$TEST_ENTRY" installed\n'
            'ride_change_publisher_repo_rpm "$TEST_ENTRY" absent\n'
            'test ! -e "$(ride_publisher_repo_file "$TEST_ENTRY")"\n'
            'test ! -e "$(ride_publisher_repo_owner_file "$TEST_ENTRY")"'
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.calls.read_text(encoding="utf-8").splitlines()
        self.assertTrue(any(line.startswith("dnf --setopt=ride-vscode.gpgcheck=1") for line in calls))
        self.assertTrue(any("--from-repo=ride-vscode code" in line for line in calls))
        self.assertFalse(any("rpm --import" in line for line in calls))

    def test_repository_conflict_is_refused_without_overwrite(self):
        path = self.repos / "ride-vscode.repo"
        path.write_text("[unrelated]\n", encoding="utf-8")
        result = self.shell('ride_change_publisher_repo_rpm "$TEST_ENTRY" installed')
        self.assertEqual(result.returncode, 42)
        self.assertIn("conflicts with existing content", result.stderr)
        self.assertEqual(path.read_text(encoding="utf-8"), "[unrelated]\n")
        self.assertNotIn("dnf ", self.calls.read_text(encoding="utf-8"))

    def test_preexisting_matching_repository_is_preserved_on_remove(self):
        expected = self.shell('ride_publisher_repo_content "$TEST_ENTRY"')
        self.assertEqual(expected.returncode, 0, expected.stderr)
        path = self.repos / "ride-vscode.repo"
        path.write_text(expected.stdout, encoding="utf-8")
        result = self.shell('ride_change_publisher_repo_rpm "$TEST_ENTRY" absent', installed=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(path.read_text(encoding="utf-8"), expected.stdout)

    def test_changed_owned_repository_is_preserved_on_remove(self):
        result = self.shell(
            'ride_publisher_repo_install_file "$TEST_ENTRY" >/dev/null\n'
            'printf "# operator change\\n" >> "$(ride_publisher_repo_file "$TEST_ENTRY")"\n'
            'ride_change_publisher_repo_rpm "$TEST_ENTRY" absent', installed=True)
        self.assertEqual(result.returncode, 42)
        self.assertIn("file changed; preserving it", result.stderr)
        self.assertTrue((self.repos / "ride-vscode.repo").exists())
        self.assertTrue(any("dnf remove -y code" in line for line in self.calls.read_text().splitlines()))

    def test_plaso_uses_the_documented_gift_stable_repository(self):
        os.environ["TEST_ENTRY_OVERRIDE"] = self.plaso_entry
        self.addCleanup(os.environ.pop, "TEST_ENTRY_OVERRIDE", None)
        result = self.shell(
            'ride_change_publisher_repo_rpm "$TEST_ENTRY" installed\n'
            'test "$(cat "$(ride_publisher_repo_file "$TEST_ENTRY")")" = "$(ride_publisher_repo_content "$TEST_ENTRY")"\n'
            'grep -Fxq "gpgcheck=1" "$(ride_publisher_repo_file "$TEST_ENTRY")"\n'
            'grep -Fxq "repo_gpgcheck=0" "$(ride_publisher_repo_file "$TEST_ENTRY")"\n'
            'ride_change_publisher_repo_rpm "$TEST_ENTRY" absent\n'
            'test ! -e "$(ride_publisher_repo_file "$TEST_ENTRY")"')
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.calls.read_text(encoding="utf-8").splitlines()
        self.assertTrue(any("--from-repo=ride-gift-stable plaso-tools" in line for line in calls))
        content = self.shell('ride_publisher_repo_content "$TEST_ENTRY"', )
        self.assertIn("@gift/stable/fedora-$releasever-$basearch/", content.stdout)
        self.assertIn("@gift/stable/pubkey.gpg", content.stdout)

    def test_tailscale_uses_pinned_publisher_key_and_signed_metadata(self):
        os.environ["TEST_ENTRY_OVERRIDE"] = self.tailscale_entry
        self.addCleanup(os.environ.pop, "TEST_ENTRY_OVERRIDE", None)
        result = self.shell(
            'ride_change_publisher_repo_rpm "$TEST_ENTRY" installed\n'
            'grep -Fxq "repo_gpgcheck=1" "$(ride_publisher_repo_file "$TEST_ENTRY")"\n'
            'grep -Fxq "gpgcheck=1" "$(ride_publisher_repo_file "$TEST_ENTRY")"\n'
            'grep -Fxq "gpgkey=https://pkgs.tailscale.com/stable/fedora/repo.gpg" "$(ride_publisher_repo_file "$TEST_ENTRY")"\n'
            'ride_change_publisher_repo_rpm "$TEST_ENTRY" absent\n'
            'test ! -e "$(ride_publisher_repo_file "$TEST_ENTRY")"')
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.calls.read_text(encoding="utf-8").splitlines()
        self.assertTrue(any("--with-colons --fingerprint" in line for line in calls))
        self.assertTrue(any("--from-repo=ride-tailscale tailscale" in line for line in calls))
        self.assertTrue(any(line == "dnf remove -y tailscale" for line in calls))
        self.assertNotIn("rpm --import", "\n".join(calls))

    def test_plex_uses_current_v2_key_and_signed_rpm_metadata(self):
        os.environ["TEST_ENTRY_OVERRIDE"] = self.plex_entry
        self.addCleanup(os.environ.pop, "TEST_ENTRY_OVERRIDE", None)
        result = self.shell(
            'ride_change_publisher_repo_rpm "$TEST_ENTRY" installed\n'
            'grep -Fxq "baseurl=https://repo.plex.tv/rpm/" "$(ride_publisher_repo_file "$TEST_ENTRY")"\n'
            'grep -Fxq "repo_gpgcheck=1" "$(ride_publisher_repo_file "$TEST_ENTRY")"\n'
            'grep -Fxq "gpgcheck=1" "$(ride_publisher_repo_file "$TEST_ENTRY")"\n'
            'grep -Fxq "gpgkey=https://downloads.plex.tv/plex-keys/PlexSign.v2.key" "$(ride_publisher_repo_file "$TEST_ENTRY")"\n'
            'ride_change_publisher_repo_rpm "$TEST_ENTRY" absent\n'
            'test ! -e "$(ride_publisher_repo_file "$TEST_ENTRY")"')
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.calls.read_text(encoding="utf-8").splitlines()
        self.assertTrue(any("--with-colons --fingerprint" in line for line in calls))
        self.assertTrue(any("--from-repo=ride-plex-server plexmediaserver" in line for line in calls))
        self.assertTrue(any(line == "dnf remove -y plexmediaserver" for line in calls))



if __name__ == "__main__":
    unittest.main()
