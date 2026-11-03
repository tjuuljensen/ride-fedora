"""Pinned VMFS6 reader source-build ownership and rollback tests."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent


class Vmfs6ReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.source = self.root / "source"
        (self.source / "debugvmfs6").mkdir(parents=True)
        (self.source / "LICENSE").write_text("GPL-2.0-only fixture\n")
        (self.source / "configure").write_text("#!/usr/bin/env bash\nexit 0\n")
        (self.source / "configure").chmod(0o755)
        self.archive = self.root / "source.tar.gz"
        with tarfile.open(self.archive, "w:gz") as bundle:
            bundle.add(self.source / "LICENSE", arcname="vmfs6-tools-pin/LICENSE")
            bundle.add(self.source / "configure", arcname="vmfs6-tools-pin/configure")
            bundle.add(self.source / "debugvmfs6", arcname="vmfs6-tools-pin/debugvmfs6")

        for command in ("gcc", "pkg-config"):
            executable = self.bin / command
            executable.write_text("#!/usr/bin/env bash\nexit 0\n")
            executable.chmod(0o755)
        curl = self.bin / "curl"
        curl.write_text(
            "#!/usr/bin/env bash\n"
            "while (($#)); do if [[ $1 == -o ]]; then output=$2; shift 2; else shift; fi; done\n"
            "[[ ${VMFS6_CURL_FAIL:-0} == 0 ]] || exit 22\n"
            "cp \"$VMFS6_SOURCE_ARCHIVE\" \"$output\"\n"
        )
        curl.chmod(0o755)
        make = self.bin / "make"
        make.write_text(
            "#!/usr/bin/env bash\n"
            "[[ ${VMFS6_BUILD_FAIL:-0} == 0 ]] || exit 23\n"
            "[[ \" $* \" == *' debugvmfs6/debugvmfs6 '* ]] || exit 24\n"
            "mkdir -p debugvmfs6\n"
            "cat > debugvmfs6/debugvmfs6 <<'EOF'\n"
            "#!/usr/bin/env bash\n"
            "echo 'VMFS6 debug reader fixture'\n"
            "EOF\n"
            "chmod +x debugvmfs6/debugvmfs6\n"
        )
        make.chmod(0o755)

        entry = next(row for row in json.loads((ROOT / "catalog/operations.json").read_text())[
            "operations"] if row["id"] == "package.vmfs6-reader")
        entry["sourceSha256"] = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.entry = self.root / "entry.json"
        self.entry.write_text(json.dumps(entry))
        self.directory = self.home / ".local/share/ride-fedora/tools/vmfs6-reader"
        self.link = self.home / ".local/bin/debugvmfs6"
        self.sibling = self.directory.parent / "keep.txt"
        self.sibling.parent.mkdir(parents=True)
        self.sibling.write_text("keep")
        self.env = os.environ | {
            "HOME": str(self.home),
            "RIDE_ROOT": str(ROOT),
            "PATH": f"{self.bin}:{os.environ['PATH']}",
            "VMFS6_SOURCE_ARCHIVE": str(self.archive),
        }

    def change(self, state, env=None):
        command = (
            'source "$RIDE_ROOT/lib/v3/common.sh"; '
            'source "$RIDE_ROOT/lib/v3/providers.sh"; '
            f'ride_change_vmfs6_reader "$(cat {self.entry})" {state}'
        )
        return subprocess.run(["bash", "-c", command], env=env or self.env,
                              capture_output=True, text=True)

    def observe(self):
        command = (
            'source "$RIDE_ROOT/lib/v3/common.sh"; '
            'source "$RIDE_ROOT/lib/v3/providers.sh"; '
            f'ride_observe_vmfs6_reader "$(cat {self.entry})"'
        )
        return subprocess.run(["bash", "-c", command], env=self.env,
                              capture_output=True, text=True)

    def test_install_observe_remove_preserves_sibling(self):
        installed = self.change("installed")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertTrue(self.link.is_symlink())
        self.assertEqual(self.link.resolve(), self.directory / "debugvmfs6")
        observed = self.observe()
        self.assertEqual(observed.returncode, 0, observed.stderr)
        self.assertEqual(observed.stdout.strip(), "installed")
        removed = self.change("absent")
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertFalse(self.directory.exists())
        self.assertFalse(self.link.is_symlink())
        self.assertEqual(self.sibling.read_text(), "keep")

    def test_digest_and_build_failures_clean_staging(self):
        entry = json.loads(self.entry.read_text()) | {"sourceSha256": "0" * 64}
        self.entry.write_text(json.dumps(entry))
        mismatch = self.change("installed")
        self.assertNotEqual(mismatch.returncode, 0)
        self.assertFalse(self.directory.exists())
        self.assertEqual(list(self.directory.parent.glob(".vmfs6-reader.*")), [])

        entry["sourceSha256"] = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.entry.write_text(json.dumps(entry))
        failed = self.change("installed", self.env | {"VMFS6_BUILD_FAIL": "1"})
        self.assertNotEqual(failed.returncode, 0)
        self.assertFalse(self.directory.exists())
        self.assertEqual(list(self.directory.parent.glob(".vmfs6-reader.*")), [])

    def test_remove_refuses_modified_binary(self):
        self.assertEqual(self.change("installed").returncode, 0)
        with (self.directory / "debugvmfs6").open("a") as binary:
            binary.write("# modified\n")
        refused = self.change("absent")
        self.assertNotEqual(refused.returncode, 0)
        self.assertTrue(self.directory.exists())
        self.assertTrue(self.link.is_symlink())


if __name__ == "__main__":
    unittest.main()
