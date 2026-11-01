"""Offline cache and completion behavior tests."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parent.parent


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        binary = self.root / "bin"
        binary.mkdir()
        fake = binary / "curl"
        fake.write_text("""#!/bin/sh
headers= body=
while [ "$#" -gt 0 ]; do
  case "$1" in
    --config) cat >/dev/null; shift 2 ;;
    --dump-header) headers=$2; shift 2 ;;
    --output) body=$2; shift 2 ;;
    *) shift ;;
  esac
done
if [ -n "$headers" ]; then
  printf 'x-ratelimit-remaining: %s\\r\\nx-ratelimit-reset: %s\\r\\n' \\
    "${RIDE_TEST_REMAINING:-10}" "${RIDE_TEST_RESET:-0}" > "$headers"
  cp "$RIDE_TEST_RESPONSE" "$body"
else
  cp "$RIDE_TEST_ASSET" "$body"
fi
printf '%s\\n' x >> "$RIDE_TEST_CALLS"
printf '%s' "${RIDE_TEST_HTTP_CODE:-200}"
""")
        fake.chmod(0o755)
        response = self.root / "release.json"
        response.write_text(json.dumps({"tag_name": "v1.0.0", "assets": []}))
        asset = self.root / "asset.zip"
        asset.write_bytes(b"verified asset")
        self.env = os.environ.copy()
        self.env.update({
            "PATH": f"{binary}:{self.env['PATH']}", "RIDE_ROOT": str(ROOT),
            "RIDE_TEST_RESPONSE": str(response),
            "RIDE_TEST_ASSET": str(asset),
            "RIDE_TEST_CALLS": str(self.root / "calls"),
            "RIDE_CACHE_DIR": str(self.root / "cache"),
        })

    def call(self, repository="example/tool", success=True):
        script = ('source "$RIDE_ROOT/lib/v3/common.sh"; '
                  'source "$RIDE_ROOT/lib/v3/github.sh"; '
                  'ride_cache_dir() { printf "%s\\n" "$RIDE_CACHE_DIR"; }; '
                  'ride_github_latest "$RIDE_TEST_REPOSITORY"')
        env = self.env | {"RIDE_TEST_REPOSITORY": repository}
        process = subprocess.run(["bash", "-c", script], env=env, text=True, capture_output=True)
        if success:
            self.assertEqual(process.returncode, 0, process.stderr)
        else:
            self.assertNotEqual(process.returncode, 0)
        return process

    def count(self):
        file = self.root / "calls"
        return len(file.read_text().splitlines()) if file.exists() else 0

    def test_disk_cache_and_auth_contexts(self):
        first = json.loads(self.call().stdout)
        self.assertEqual(first["provenance"]["acquisitionKind"], "Network")
        self.assertEqual(json.loads(self.call().stdout)["provenance"]["acquisitionKind"], "DiskCache")
        self.assertEqual(self.count(), 1)
        self.env["RIDE_GITHUB_TOKEN"] = "testTokenOne"
        self.call()
        self.env["RIDE_GITHUB_TOKEN"] = "testTokenTwo"
        self.call()
        self.assertEqual(self.count(), 3)
        cache_text = "".join(p.read_text() for p in (self.root / "cache" / "github").glob("release-*.json"))
        self.assertNotIn("testToken", cache_text)

    def test_backoff_keeps_fresh_cache_but_blocks_other_endpoint(self):
        self.call()
        deadline = int(time.time()) + 120
        backoff = next((self.root / "cache" / "github").glob("backoff-*"), None)
        if backoff is None:
            import hashlib
            context = hashlib.sha256(b"Anonymous|").hexdigest()
            backoff = self.root / "cache" / "github" / f"backoff-{context}"
        backoff.write_text(f"{deadline}\n")
        self.call()
        blocked = self.call("example/other", success=False)
        self.assertIn("rate limit", blocked.stderr)
        self.assertEqual(self.count(), 1)
        self.env["RIDE_GITHUB_TOKEN"] = "testTokenOne"
        self.call("example/other")
        self.assertEqual(self.count(), 2)

    def test_invalid_payload_is_not_cached(self):
        (self.root / "release.json").write_text('{"tag_name":12,"assets":[]}')
        failed = self.call(success=False)
        self.assertIn("invalid or oversized", failed.stderr)
        self.assertEqual(list((self.root / "cache" / "github").glob("release-*.json")), [])

    def test_artifact_digest_verification(self):
        import hashlib

        digest = hashlib.sha256((self.root / "asset.zip").read_bytes()).hexdigest()
        release = {"tag_name": "v1.0.0", "assets": [{
            "name": "tool-linux.zip", "size": 14,
            "digest": f"sha256:{digest}",
            "browser_download_url": "https://github.com/example/tool/releases/download/v1.0.0/tool-linux.zip",
        }]}
        (self.root / "release.json").write_text(json.dumps(release))
        entry = json.dumps({"githubRepository": "example/tool", "assetSuffix": "-linux.zip",
                            "maxBytes": 1000, "productId": "tool"})
        script = ('source "$RIDE_ROOT/lib/v3/common.sh"; '
                  'source "$RIDE_ROOT/lib/v3/github.sh"; '
                  'ride_cache_dir() { printf "%s\\n" "$RIDE_CACHE_DIR"; }; '
                  'ride_github_download_asset "$RIDE_TEST_ENTRY" "$RIDE_TEST_DESTINATION"')
        env = self.env | {"RIDE_TEST_ENTRY": entry,
                          "RIDE_TEST_DESTINATION": str(self.root / "downloads")}
        result = subprocess.run(["bash", "-c", script], env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / "downloads" / "v1.0.0" / "tool-linux.zip").read_bytes(), b"verified asset")
        sidecar = self.root / "downloads" / "v1.0.0" / "tool-linux.zip.ride.json"
        self.assertEqual(json.loads(sidecar.read_text())["sha256"], digest)
        (self.root / "asset.zip").write_bytes(b"tampered asset")
        failed = subprocess.run(["bash", "-c", script], env=env, text=True, capture_output=True)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("SHA-256 differs", failed.stderr)
        self.assertEqual((self.root / "downloads" / "v1.0.0" / "tool-linux.zip").read_bytes(), b"verified asset")


class CompletionTests(unittest.TestCase):
    def test_profile_ids_and_catalog_ids(self):
        script = ('source "$RIDE_ROOT/completion/ride.bash"; '
                  'COMP_WORDS=(./ride.sh apply --profile ""); COMP_CWORD=3; _ride_complete; '
                  'printf "PROFILE:%s\\n" "${COMPREPLY[@]}"; '
                  'COMP_WORDS=(./ride.sh install package.ex); COMP_CWORD=2; _ride_complete; '
                  'printf "ID:%s\\n" "${COMPREPLY[@]}"')
        env = os.environ | {"RIDE_ROOT": str(ROOT)}
        result = subprocess.run(["bash", "-c", script], env=env, text=True,
                                capture_output=True, check=True)
        self.assertIn("PROFILE:default", result.stdout)
        self.assertIn("ID:package.exfatprogs", result.stdout)

    def test_package_source_ids(self):
        script = ('source "$RIDE_ROOT/completion/ride.bash"; '
                  'COMP_WORDS=(./ride.sh install package.exfatprogs --source ""); '
                  'COMP_CWORD=4; _ride_complete; printf "%s\\n" "${COMPREPLY[@]}"')
        env = os.environ | {"RIDE_ROOT": str(ROOT)}
        result = subprocess.run(["bash", "-c", script], env=env, text=True,
                                capture_output=True, check=True)
        self.assertIn("fedora-rpm", result.stdout.splitlines())

    def test_gnome_layout_values_from_catalog(self):
        script = ('source "$RIDE_ROOT/completion/ride.bash"; '
                  'COMP_WORDS=(./ride.sh set setting.gnome-window-buttons --value ""); '
                  'COMP_CWORD=4; _ride_complete; printf "%s\\n" "${COMPREPLY[@]}"')
        env = os.environ | {"RIDE_ROOT": str(ROOT)}
        result = subprocess.run(["bash", "-c", script], env=env, text=True,
                                capture_output=True, check=True)
        self.assertEqual(set(result.stdout.splitlines()),
                         {":minimize,maximize,close", ":appmenu:close", "close,minimize,maximize:"})

    def test_run_ids_from_client_state_store(self):
        with tempfile.TemporaryDirectory() as temp:
            run_id = "20261014T000000Z-12-34"
            (Path(temp) / f"{run_id}.json").write_text("{}")
            script = ('source "$RIDE_ROOT/completion/ride.bash"; '
                      'COMP_WORDS=(./ride.sh restore --run-id ""); COMP_CWORD=3; '
                      '_ride_complete; printf "%s\\n" "${COMPREPLY[@]}"')
            env = os.environ | {"RIDE_ROOT": str(ROOT), "RIDE_STATE_DIR": temp}
            result = subprocess.run(["bash", "-c", script], env=env, text=True,
                                    capture_output=True, check=True)
            self.assertIn(run_id, result.stdout.splitlines())


if __name__ == "__main__":
    unittest.main()
