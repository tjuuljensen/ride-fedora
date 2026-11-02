"""Ownership and recovery checks for the Minecraft server JAR helper."""

from __future__ import annotations

from io import BytesIO
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SPEC = importlib.util.spec_from_file_location(
    "manage_minecraft_server", Path(__file__).resolve().parents[1] / "tools" / "manage-minecraft-server.py"
)
manager = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(manager)


class Response(BytesIO):
    def geturl(self):
        return manager.SOURCE_URI


class MinecraftServerManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "home"
        self.home.mkdir()
        self.root = self.home / ".local/opt/ride-fedora/minecraft-server" / manager.VERSION
        archive = BytesIO()
        with zipfile.ZipFile(archive, "w") as jar:
            jar.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\n")
            jar.writestr("version.json", '{"id":"26.3"}')
        self.payload = archive.getvalue()
        self.sha1 = hashlib.sha1(self.payload).hexdigest()
        self.sha256 = hashlib.sha256(self.payload).hexdigest()
        self.constants = patch.multiple(
            manager, SOURCE_SHA1=self.sha1,
            SOURCE_URI="https://example.invalid/server.jar",
        )
        self.constants.start()
        self.addCleanup(self.constants.stop)

    def install_with_fixture(self):
        with patch.object(manager.Path, "home", return_value=self.home), \
             patch.object(manager, "require_java_25"), \
             patch.object(manager, "urlopen", return_value=Response(self.payload)):
            manager.install(self.root)

    def test_install_repeat_and_remove_preserves_world_state(self):
        world = self.home / "minecraft/world"
        world.mkdir(parents=True)
        (world / "level.dat").write_bytes(b"world sentinel")
        config = self.home / "minecraft/server.properties"
        config.write_text("level-name=world\n", encoding="utf-8")
        eula = self.home / "minecraft/eula.txt"
        eula.write_text("eula=false\n", encoding="utf-8")
        before = {p: p.read_bytes() for p in (world / "level.dat", config, eula)}

        self.install_with_fixture()
        self.assertEqual(manager.observe(self.root), "installed")
        manifest = json.loads((self.root / ".ride-owned").read_text())
        self.assertEqual(manifest["sha256"], self.sha256)
        self.assertEqual((self.root / "server.jar").read_bytes(), self.payload)
        self.install_with_fixture()
        manager.remove(self.root)
        self.assertEqual(manager.observe(self.root), "absent")
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_refuses_unowned_or_modified_install(self):
        self.root.mkdir(parents=True)
        (self.root / "world").mkdir()
        with self.assertRaisesRegex(RuntimeError, "unowned files"):
            manager.remove(self.root)
        (self.root / "world").rmdir()
        (self.root / "server.jar").write_bytes(self.payload)
        (self.root / ".ride-owned").write_text("{}\n")
        with self.assertRaisesRegex(RuntimeError, "ownership record"):
            manager.remove(self.root)

    def test_refuses_symlinked_install_path(self):
        outside = self.home / "outside"
        outside.mkdir()
        self.root.parent.mkdir(parents=True)
        self.root.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(RuntimeError, "unowned Minecraft server path"):
            manager.observe(self.root)

    def test_rejects_wrong_content_address(self):
        with self.assertRaisesRegex(RuntimeError, "does not match Mojang"):
            with patch.object(manager.Path, "home", return_value=self.home), \
                 patch.object(manager, "SOURCE_SHA1", "0" * 40), \
                 patch.object(manager, "require_java_25"), \
                 patch.object(manager, "urlopen", return_value=Response(self.payload)):
                manager.install(self.root)


if __name__ == "__main__":
    unittest.main()
