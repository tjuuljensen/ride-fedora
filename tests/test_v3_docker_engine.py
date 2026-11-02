"""Mocked ownership and data-preserving lifecycle checks for Docker Engine."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROVIDER = ROOT / "lib/v3/providers.sh"
FINGERPRINT = "060A61C51B558A7F742B77AAC52FEB6B621E9F35"
ENTRY = '{"id":"system.docker-engine","handler":"docker-engine","signingFingerprint":"' + FINGERPRINT + '"}'


class DockerEngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ride-docker-engine-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.state = self.root / "state"
        self.repo_dir = self.root / "repos"
        self.repo_dir.mkdir()
        self.repo = self.repo_dir / "docker-ce.repo"
        self.key_dir = self.root / "rpm-gpg"
        self.key_dir.mkdir()
        self.key = self.key_dir / "docker-ce.gpg"
        self.packages = self.root / "packages"
        self.packages.mkdir()
        self.service = self.root / "service"
        self.service.write_text("not-found", encoding="utf-8")
        self.volume = self.root / "docker-data" / "volumes" / "ride-seeded" / "_data"
        self.volume.mkdir(parents=True)
        (self.volume / "payload.txt").write_text("keep this volume\n", encoding="utf-8")

    def shell(self, body, *, running=""):
        script = f'''set -euo pipefail
source {PROVIDER}
ride_die() {{ printf '%s\\n' "$*" >&2; exit 1; }}
ride_error() {{ printf '%s\\n' "$*" >&2; exit 1; }}
ride_require_command() {{ :; }}
ride_docker_engine_repo_path() {{ printf '%s\\n' {str(self.repo)!r}; }}
ride_docker_engine_key_path() {{ printf '%s\\n' {str(self.key)!r}; }}
rpm() {{
  [[ "$1" == -q && "$2" == --quiet ]] || return 8
  [[ -f {str(self.packages)!r}/"$3" ]]
}}
systemctl() {{
  case "$1 $2" in
    'show --property=LoadState') cat {str(self.service)!r};;
    'is-active docker.service') [[ "$(cat {str(self.service)!r})" == active ]] && printf 'active\\n' || {{ printf 'inactive\\n'; return 3; }};;
    'start docker.service') printf 'active\\n' > {str(self.service)!r};;
    'stop docker.service') printf 'inactive\\n' > {str(self.service)!r};;
    *) return 7;;
  esac
}}
dnf5() {{
  if [[ "$1" == --setopt=install_weak_deps=False ]]; then shift; fi
  case "$1 $2" in
    'install --assumeyes') touch {str(self.packages)!r}/docker-ce {str(self.packages)!r}/docker-ce-cli {str(self.packages)!r}/containerd.io;;
    'remove --assumeyes') rm -f {str(self.packages)!r}/docker-ce {str(self.packages)!r}/docker-ce-cli {str(self.packages)!r}/containerd.io;;
    *) return 9;;
  esac
}}
curl() {{ local last; for last do :; done; printf key > "$last"; }}
gpg() {{ printf 'pub:::::::::\nfpr:::::::::{FINGERPRINT}:\\n'; }}
docker() {{ [[ "$1" == ps && "$2" == --quiet ]] || return 9; printf '%s\\n' {running!r}; }}
RIDE_OS_ID=fedora
entry='{ENTRY}'
{body}
'''
        env = os.environ.copy()
        env.update(RIDE_TEST_MODE="1", RIDE_TEST_DOCKER_STATE_DIR=str(self.state))
        return subprocess.run(["bash", "-c", script], env=env, text=True,
                              capture_output=True, check=False)

    def test_apply_repeat_and_remove_preserves_container_data(self):
        result = self.shell('''
ride_docker_engine_change "$entry" configured
ride_docker_engine_observe "$entry"
ride_docker_engine_change "$entry" configured
ride_docker_engine_change "$entry" absent
ride_docker_engine_observe "$entry"
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["configured", "absent"])
        self.assertEqual((self.volume / "payload.txt").read_text(), "keep this volume\n")
        self.assertFalse(self.repo.exists())
        self.assertFalse(self.key.exists())
        self.assertFalse((self.state / "docker-engine.json").exists())
        self.assertEqual(list(self.repo_dir.iterdir()), [])
        self.assertEqual(list(self.state.iterdir()), [])

    def test_stopped_owned_engine_is_observable_and_restarted_on_configure(self):
        result = self.shell('''
ride_docker_engine_change "$entry" configured
''')
        # The mock systemctl reads the fixture service file, so set it stopped
        # between calls using a second shell invocation with the same owned state.
        self.assertEqual(result.returncode, 0, result.stderr)
        self.service.write_text("inactive", encoding="utf-8")
        result = self.shell('''
ride_docker_engine_observe "$entry"
ride_docker_engine_change "$entry" configured
ride_docker_engine_observe "$entry"
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["stopped", "configured"])

    def test_stopped_engine_refuses_removal_until_running_containers_can_be_checked(self):
        result = self.shell('''
ride_docker_engine_change "$entry" configured
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.service.write_text("inactive", encoding="utf-8")
        result = self.shell('ride_docker_engine_change "$entry" absent')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("start it so RIDE can verify", result.stderr)
        self.assertTrue(self.repo.exists())
        self.assertTrue((self.state / "docker-engine.json").exists())

    def test_running_containers_block_removal_without_touching_owned_state(self):
        result = self.shell('''
ride_docker_engine_change "$entry" configured
ride_docker_engine_change "$entry" absent
''', running="container-id")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("running Docker containers prevent removal", result.stderr)
        self.assertTrue(self.repo.exists())
        self.assertTrue((self.state / "docker-engine.json").exists())
        self.assertTrue((self.volume / "payload.txt").exists())

    def test_unowned_repository_conflict_refuses_apply(self):
        self.repo.write_text("administrator repository\n", encoding="utf-8")
        result = self.shell('ride_docker_engine_change "$entry" configured')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("partial or unowned state", result.stderr)
        self.assertEqual(self.repo.read_text(), "administrator repository\n")

    def test_wrong_signing_key_is_refused_before_mutation(self):
        body = ("gpg() { printf 'pub:::::::::\\nfpr:::::::::0000000000000000000000000000000000000000:\\n'; }; "
                'ride_docker_engine_change "$entry" configured')
        result = self.shell(body)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fingerprint does not match", result.stderr)
        self.assertFalse(self.repo.exists())
        self.assertFalse(self.key.exists())
        self.assertFalse((self.state / "docker-engine.json").exists())

    def test_failed_package_install_cleans_only_new_owned_files(self):
        result = self.shell('dnf5() { return 12; }; ride_docker_engine_change "$entry" configured')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.repo.exists())
        self.assertFalse(self.key.exists())
        self.assertFalse((self.state / "docker-engine.json").exists())
        self.assertEqual((self.volume / "payload.txt").read_text(), "keep this volume\n")

    def test_failed_remove_restarts_service_and_keeps_owned_state(self):
        body = ("ride_docker_engine_change \"$entry\" configured; "
                "dnf5() { case \"$1 $2\" in 'remove --assumeyes') return 12;; *) return 9;; esac; }; "
                'ride_docker_engine_change "$entry" absent')
        result = self.shell(body)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(self.repo.exists())
        self.assertTrue(self.key.exists())
        self.assertTrue((self.state / "docker-engine.json").exists())
        self.assertEqual(self.service.read_text().strip(), "active")


if __name__ == "__main__":
    unittest.main()
