"""Focused lifecycle checks for the pinned Galleta Debian binary helper."""

from __future__ import annotations

import hashlib
import importlib.util
import io
import struct
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools/manage-galleta.py"
SPEC = importlib.util.spec_from_file_location("manage_galleta", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
manage_galleta = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(manage_galleta)


def ar_member(name: str, content: bytes) -> bytes:
    name_bytes = (name + "/").encode("ascii").ljust(16, b" ")
    header = (name_bytes + b"0".ljust(12) + b"0".ljust(6) + b"0".ljust(6) +
              b"100644".ljust(8) + str(len(content)).encode().ljust(10) + b"`\n")
    assert len(header) == 60
    return header + content + (b"\n" if len(content) % 2 else b"")


def build_test_package() -> bytes:
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w:xz") as archive:
        binary = bytearray(64)
        binary[:4] = b"\x7fELF"
        binary[18:20] = struct.pack("<H", 62)
        for name, payload in (
            ("./usr/bin/galleta", bytes(binary)),
            ("./usr/share/doc/galleta/copyright", b"Copyright Keith J. Jones. BSD-3-Clause\n"),
        ):
            item = tarfile.TarInfo(name)
            item.size = len(payload)
            item.mode = 0o755 if name.endswith("/galleta") else 0o644
            archive.addfile(item, io.BytesIO(payload))
    return b"!<arch>\n" + ar_member("debian-binary", b"2.0\n") + ar_member("data.tar.xz", tar_buffer.getvalue())


class FakeResponse(io.BytesIO):
    def geturl(self):
        return "https://deb.debian.org/test.deb"


class GalletaHelperTests(unittest.TestCase):
    def test_pinned_deb_installs_and_removes_only_owned_user_files(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            package = build_test_package()
            with patch.object(manage_galleta, "SOURCE_SHA256", hashlib.sha256(package).hexdigest()), \
                 patch.object(manage_galleta, "urlopen", return_value=FakeResponse(package)) as fetch:
                manage_galleta.install(home)
                self.assertEqual(manage_galleta.observe(home), "installed")
                self.assertEqual(manage_galleta.paths(home)[0].read_bytes()[:4], b"\x7fELF")
                self.assertEqual(manage_galleta.paths(home)[0].stat().st_mode & 0o777, 0o755)
                manage_galleta.install(home)
                fetch.assert_called_once()
                manage_galleta.remove(home)
                self.assertEqual(manage_galleta.observe(home), "absent")

    def test_modified_binary_is_never_removed(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            package = build_test_package()
            with patch.object(manage_galleta, "SOURCE_SHA256", hashlib.sha256(package).hexdigest()), \
                 patch.object(manage_galleta, "urlopen", return_value=FakeResponse(package)):
                manage_galleta.install(home)
                binary, _ = manage_galleta.paths(home)
                binary.write_bytes(b"user modification")
                with self.assertRaisesRegex(manage_galleta.GalletaError, "changed"):
                    manage_galleta.remove(home)
                self.assertEqual(binary.read_bytes(), b"user modification")


if __name__ == "__main__":
    unittest.main()
