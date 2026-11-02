"""Unit tests for the user-local Ferium lifecycle helper."""

from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock
import zipfile


ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "manage_ferium", ROOT / "tools" / "manage-ferium.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import Ferium lifecycle helper")
ferium = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ferium)


class FeriumLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="ride-ferium-")
        self.home = Path(self.temporary.name)
        self.config = self.home / ".config/ferium/config.json"
        self.output = self.home / "minecraft/mods/keep.jar"
        self.config.parent.mkdir(parents=True)
        self.output.parent.mkdir(parents=True)
        self.config.write_text('{"profiles": ["keep"]}\n', encoding="utf-8")
        self.output.write_bytes(b"user-owned mod\n")
        self.archive = self.make_archive()

    def tearDown(self):
        self.temporary.cleanup()

    @staticmethod
    def make_archive(filename="ferium"):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            info = zipfile.ZipInfo(filename)
            info.external_attr = (0o100755 << 16)
            archive.writestr(info, b"mock ferium binary")
        return stream.getvalue()

    def patch_download(self, contents=None, version=None):
        response = io.BytesIO(self.archive if contents is None else contents)
        response.geturl = lambda: ferium.ASSET_URL
        return (mock.patch.object(ferium.urllib.request, "urlopen", return_value=response),
                mock.patch.object(ferium.subprocess, "run", return_value=subprocess.CompletedProcess(
                    ["ferium", "--version"], 0, version or f"ferium {ferium.VERSION}\n", "")))

    def test_install_repeat_remove_preserves_configuration_and_modpack_output(self):
        download, version = self.patch_download()
        with download, version:
            ferium.install(self.home)
            ferium.install(self.home)
        root, link, manifest = ferium.paths(self.home)
        self.assertEqual(ferium.observe(self.home), "installed")
        record = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual(record["assetUrl"], ferium.ASSET_URL)
        self.assertEqual(record["archiveSha256"], ferium.hashlib.sha256(self.archive).hexdigest())
        self.assertEqual(link.resolve(), root / "ferium")
        self.assertEqual(self.config.read_text(encoding="utf-8"), '{"profiles": ["keep"]}\n')
        self.assertEqual(self.output.read_bytes(), b"user-owned mod\n")
        ferium.remove(self.home)
        self.assertEqual(ferium.observe(self.home), "absent")
        self.assertTrue(self.config.exists())
        self.assertTrue(self.output.exists())

    def test_existing_unowned_link_is_preserved(self):
        _, link, _ = ferium.paths(self.home)
        link.parent.mkdir(parents=True)
        owned_elsewhere = self.home / "custom-ferium"
        owned_elsewhere.write_text("user binary", encoding="utf-8")
        link.symlink_to(owned_elsewhere)
        download, version = self.patch_download()
        with download, version:
            with self.assertRaisesRegex(ferium.FeriumError, "unowned or modified"):
                ferium.install(self.home)
        self.assertTrue(link.is_symlink())
        self.assertEqual(owned_elsewhere.read_text(encoding="utf-8"), "user binary")

    def test_modified_owned_binary_refuses_removal(self):
        download, version = self.patch_download()
        with download, version:
            ferium.install(self.home)
        root, _, _ = ferium.paths(self.home)
        (root / "ferium").write_bytes(b"modified")
        with self.assertRaisesRegex(ferium.FeriumError, "modified or not RIDE-owned"):
            ferium.remove(self.home)
        self.assertTrue((root / "ferium").exists())

    def test_user_file_added_to_owned_directory_blocks_removal(self):
        download, version = self.patch_download()
        with download, version:
            ferium.install(self.home)
        root, _, _ = ferium.paths(self.home)
        extra = root / "user-notes.txt"
        extra.write_text("preserve me", encoding="utf-8")
        with self.assertRaisesRegex(ferium.FeriumError, "modified or not RIDE-owned"):
            ferium.remove(self.home)
        self.assertEqual(extra.read_text(encoding="utf-8"), "preserve me")

    def test_unsafe_archive_member_is_refused(self):
        download, version = self.patch_download(self.make_archive("../ferium"))
        with download, version:
            with self.assertRaisesRegex(ferium.FeriumError, "unsafe entry"):
                ferium.install(self.home)
        root, link, manifest = ferium.paths(self.home)
        self.assertFalse(root.exists())
        self.assertFalse(link.exists())
        self.assertFalse(manifest.exists())

    def test_wrong_binary_version_is_not_installed(self):
        download, version = self.patch_download(version="ferium 4.6.0\n")
        with download, version:
            with self.assertRaisesRegex(ferium.FeriumError, "declared Ferium version"):
                ferium.install(self.home)
        self.assertEqual(ferium.observe(self.home), "absent")


if __name__ == "__main__":
    unittest.main()
