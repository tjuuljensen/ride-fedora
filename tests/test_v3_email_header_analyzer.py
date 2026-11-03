"""Pinned local email analyzer acquisition and loopback lifecycle."""

import json
import importlib.util
import io
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch


ROOT = Path(__file__).resolve().parent.parent
COMMIT = "ccaf044dfe964215656966013feaaea705726048"
TREE = "69ec6b8a3c078a0f952e04ddea47f0a0ebf3ce49"
LOCK_BLOB = "7e8a00e275c2253e6ffe29f42a9aac8dc00aee41"


class EmailHeaderAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.tmp = self.root / "tmp"
        self.tmp.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.fixture = self.root / "fixture-source"
        frontend = self.fixture / "src/Frontend"
        frontend.mkdir(parents=True)
        (frontend / "package-lock.json").write_text("pinned-lock", encoding="utf-8")
        package = frontend / "package.json"
        package.write_text('{"scripts":{"build":"quasar build"}}\n', encoding="utf-8")
        self.git = self.bin / "git"
        self.git.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "if [[ $1 == clone ]]; then\n"
            "  target=${!#}\n"
            "  [[ ${EMAIL_GIT_FAIL:-0} == 0 ]] || exit 9\n"
            "  mkdir -p \"$target/.git\"\n"
            "  cp -a \"$EMAIL_FIXTURE_SOURCE/.\" \"$target/\"\n"
            "  printf '%s\\n' '" + COMMIT + "' > \"$target/.git/head\"\n"
            "  exit 0\n"
            "fi\n"
            "if [[ $1 == -C ]]; then\n"
            "  repo=$2; shift 2\n"
            "  case $1 in\n"
            "    checkout) [[ ${EMAIL_GIT_FAIL_CHECKOUT:-0} == 0 ]] ;;\n"
            "    rev-parse)\n"
            "      case $2 in\n"
            "        HEAD) cat \"$repo/.git/head\" ;;\n"
            "        'HEAD^{tree}') printf '%s\\n' \"${EMAIL_GIT_TREE_OVERRIDE:-" + TREE + "}\" ;;\n"
            "        *:src/Frontend/package-lock.json) printf '%s\\n' '" + LOCK_BLOB + "' ;;\n"
            "        *) exit 10 ;;\n"
            "      esac\n"
            "      ;;\n"
            "    *) exit 11 ;;\n"
            "  esac\n"
            "fi\n"
        )
        self.git.chmod(0o755)
        self.npm = self.bin / "npm"
        self.npm.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "if [[ $1 == ci ]]; then\n"
            "  [[ ${EMAIL_NPM_FAIL:-0} == 0 ]] || exit 17\n"
            "  mkdir -p node_modules/.bin\n"
            "  printf '#!/usr/bin/env bash\\nexit 0\\n' > node_modules/.bin/quasar\n"
            "  chmod +x node_modules/.bin/quasar\n"
            "elif [[ $1 == run && $2 == build ]]; then\n"
            "  [[ ${EMAIL_NPM_FAIL_BUILD:-0} == 0 ]] || exit 18\n"
            "  mkdir -p dist/spa/assets\n"
            "  printf '<html><body>fixture analyzer</body></html>\\n' > dist/spa/index.html\n"
            "  printf 'local fixture\\n' > dist/spa/assets/app.js\n"
            "else exit 19; fi\n"
        )
        self.npm.chmod(0o755)
        self.entry = json.loads((ROOT / "catalog/operations.json").read_text())
        self.entry = next(
            row for row in self.entry["operations"]
            if row["id"] == "package.email-header-analyzer"
        )
        self.entry_path = self.root / "entry.json"
        self.entry_path.write_text(json.dumps(self.entry), encoding="utf-8")
        self.app = self.home / ".local/share/ride-fedora/apps/email-header-analyzer"
        self.launcher = self.home / ".local/bin/ride-email-header-analyzer"
        self.manifest = self.home / ".local/share/ride-fedora/owned-tools/package.email-header-analyzer.json"
        self.unrelated = self.home / "Documents/keep.txt"
        self.unrelated.parent.mkdir(parents=True)
        self.unrelated.write_text("keep this data", encoding="utf-8")
        self.env = os.environ | {
            "HOME": str(self.home),
            "TMPDIR": str(self.tmp),
            "RIDE_ROOT": str(ROOT),
            "EMAIL_FIXTURE_SOURCE": str(self.fixture),
            "PATH": f"{self.bin}:{os.environ['PATH']}",
            "RIDE_DISABLE_BROWSER": "1",
        }

    def shell(self, body, env=None):
        command = (
            'source "$RIDE_ROOT/lib/v3/common.sh"; '
            'source "$RIDE_ROOT/lib/v3/providers.sh"; '
            'source "$RIDE_ROOT/lib/v3/email_header_analyzer.sh"; '
            f'ENTRY=$(cat {shlex.quote(str(self.entry_path))}); {body}'
        )
        return subprocess.run(
            ["bash", "-c", command], env=env or self.env,
            text=True, capture_output=True, check=False,
        )

    def install(self, env=None):
        return self.shell('ride_change "$ENTRY" installed', env)

    def remove(self, env=None):
        return self.shell('ride_change "$ENTRY" absent', env)

    def observe(self):
        return self.shell('ride_observe "$ENTRY"').stdout.strip()

    def test_install_repeat_serve_spa_and_remove_preserves_unrelated_data(self):
        installed = self.install()
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual(self.observe(), "installed")
        repeat = self.install()
        self.assertEqual(repeat.returncode, 0, repeat.stderr)

        spec = importlib.util.spec_from_file_location(
            "ride_email_header_analyzer", ROOT / "tools/ride-email-header-analyzer.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        state = {}
        self_outer = self

        class FakeServer:
            def __init__(self, address, handler):
                state["address"] = address
                state["handler"] = handler
                self.server_address = (address[0], 45823)

            def serve_forever(self):
                state["removal"] = self_outer.remove()

            def server_close(self):
                state["closed"] = True

        output = io.StringIO()
        with patch.dict(os.environ, self.env), \
             patch.object(module.http.server, "ThreadingHTTPServer", FakeServer), \
             redirect_stdout(output):
            self.assertEqual(module.serve(), 0)
        self.assertEqual(state["address"], ("127.0.0.1", 0))
        self.assertEqual(state["removal"].returncode, 2)
        self.assertIn("is running", state["removal"].stderr)
        self.assertTrue(state["closed"])
        self.assertIn("http://127.0.0.1:45823/", output.getvalue())

        handler = module.LocalSpaHandler.__new__(module.LocalSpaHandler)
        handler.path = "/header-analyzer"
        handler.translate_path = lambda _path: str(self.app / "missing-route")
        with patch.object(module.http.server.SimpleHTTPRequestHandler, "send_head",
                          lambda instance: instance.path):
            self.assertEqual(handler.send_head(), "/index.html")
        handler = module.LocalSpaHandler.__new__(module.LocalSpaHandler)
        handler._headers_buffer = []
        handler.request_version = "HTTP/1.1"
        handler.wfile = io.BytesIO()
        module.LocalSpaHandler.end_headers(handler)
        headers = handler.wfile.getvalue().decode()
        self.assertIn("connect-src 'self'", headers)
        self.assertIn("Referrer-Policy: no-referrer", headers)
        self.assertIn("Cache-Control: no-store", headers)

        removed = self.remove()
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual(self.observe(), "absent")
        self.assertEqual(self.unrelated.read_text(encoding="utf-8"), "keep this data")

    def test_acquisition_build_and_source_pin_failures_leave_no_partial_install(self):
        for env in (
            self.env | {"EMAIL_GIT_FAIL": "1"},
            self.env | {"EMAIL_GIT_TREE_OVERRIDE": "0" * 40},
            self.env | {"EMAIL_NPM_FAIL": "1"},
            self.env | {"EMAIL_NPM_FAIL_BUILD": "1"},
        ):
            result = self.install(env)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(self.app.exists())
            self.assertFalse(self.launcher.exists())
            self.assertFalse(self.manifest.exists())
        self.assertEqual(self.unrelated.read_text(encoding="utf-8"), "keep this data")

    def test_modified_or_unowned_files_are_never_removed(self):
        self.assertEqual(self.install().returncode, 0)
        changed = self.app / "dist/spa/assets/app.js"
        changed.write_text("user change", encoding="utf-8")
        self.assertEqual(self.observe(), "unowned")
        refused = self.remove()
        self.assertNotEqual(refused.returncode, 0)
        self.assertTrue(self.app.exists())
        self.assertEqual(changed.read_text(encoding="utf-8"), "user change")


if __name__ == "__main__":
    unittest.main()
