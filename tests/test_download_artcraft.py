"""Offline tests for release selection and verified download handling."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "download_artcraft", Path(__file__).resolve().parents[1] / "tools/download-artcraft.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def row(name, digest="a" * 64):
    return (f'<li><a href="/storytold/example/releases/download/v1/{name}">{name}</a>'
            f'<span>sha256:{digest}</span></li>')


class Response(io.BytesIO):
    def __init__(self, data, length=None):
        super().__init__(data)
        self.headers = {"Content-Length": str(len(data) if length is None else length)}


class DiscoveryTests(unittest.TestCase):
    def test_formats_exclude_deltas_refs_and_lite(self):
        for name in ("app.AppImage.zsync", "app.flatpakref", "app-linux.tar.gz", "app-trial.rpm", "app-lite.flatpak"):
            self.assertIsNone(tool.asset_format(name))
        self.assertEqual(tool.asset_format("app.AppImage"), "appimage")

    def test_metadata_and_architecture(self):
        assets = tool.parse_assets(row("app-x86_64.rpm") + row("app-aarch64.flatpak") + row("SHA256SUMS.txt"), "example", "v1")
        self.assertEqual([a["architecture"] for a in assets], ["x86_64", "aarch64", "unspecified"])
        self.assertEqual(assets[0]["upstream_sha256"], "a" * 64)

    def test_unsafe_names_rejected(self):
        for name in ("../escape.rpm", "a\\b.rpm", "CON.rpm", "foo:bar.rpm", "a."):
            with self.subTest(name=name), self.assertRaises(ValueError):
                tool.safe_name(name)

    def test_foreign_asset_rejected(self):
        body = '<li><a href="/attacker/example/releases/download/v1/app.rpm">app</a></li>'
        with self.assertRaises(ValueError):
            tool.parse_assets(body, "example", "v1")

    def test_repository_pagination_and_count(self):
        pages = ['"repositoryCount":2 <a href="/storytold/one">one</a> rel="next"',
                 '"repositoryCount":2 <a href="/storytold/two">two</a>']
        with patch.object(tool, "page", side_effect=pages):
            self.assertEqual(tool.repositories(), ["one", "two"])

    def test_incomplete_repository_pagination_fails(self):
        with patch.object(tool, "page", return_value='"repositoryCount":2 <a href="/storytold/one">one</a>'):
            with self.assertRaises(ValueError):
                tool.repositories()

    def test_source_only_release_falls_back_and_filters_arch(self):
        prefix = "https://github.com/storytold/example/releases/expanded_assets/"
        releases = f'<include-fragment src="{prefix}v2"><include-fragment data-deferred-src="{prefix}v1">'
        with patch.object(tool, "page", side_effect=[releases, "no binary assets", row("app-x86_64.rpm") + row("app-aarch64.rpm")]):
            result = tool.discover_repo("example", "x86_64")
        self.assertEqual(result["tag"], "v1")
        self.assertEqual(len(result["assets"]), 1)
        self.assertEqual(result["missing_formats"], ["appimage", "flatpak"])

    def test_release_pagination(self):
        prefix = "https://github.com/storytold/example/releases/expanded_assets/"
        pages = [f'<include-fragment src="{prefix}v2"><a rel="next" href="?page=2">Next</a>',
                 'source only', f'<include-fragment src="{prefix}v1">', row("app-x86_64.rpm")]
        with patch.object(tool, "page", side_effect=pages):
            self.assertEqual(tool.discover_repo("example", "all")["tag"], "v1")

    def test_block_page_is_not_misreported_as_no_releases(self):
        with patch.object(tool, "page", return_value="Please sign in or try again"):
            with self.assertRaises(ValueError):
                tool.discover_repo("example", "all")

    def test_explicit_empty_release_list(self):
        with patch.object(tool, "page", return_value="There aren’t any releases here"):
            self.assertEqual(tool.discover_repo("example", "all")["status"], "no-linux-installers")

    def test_discovery_error_cannot_be_downloaded(self):
        catalog = {"schema_version": 1, "owner": "storytold", "repositories": [{"status": "error"}]}
        with tempfile.TemporaryDirectory() as temp, self.assertRaises(ValueError):
            tool.download(catalog, Path(temp), 1, tool.FORMATS)


class DownloadTests(unittest.TestCase):
    def setUp(self):
        self.data = b"\xed\xab\xee\xdbvalid-rpm-placeholder"
        self.asset = {"repo": "example", "name": "app-x86_64.rpm", "tag": "v1", "format": "rpm",
                      "architecture": "x86_64", "url": "https://github.com/storytold/example/releases/download/v1/app-x86_64.rpm",
                      "upstream_sha256": hashlib.sha256(self.data).hexdigest()}

    def test_download_and_verified_reuse(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            with patch.object(tool, "fetch", return_value=Response(self.data)):
                entry = tool.download_asset(self.asset, dest)
            self.assertEqual(entry["status"], "downloaded")
            with patch.object(tool, "fetch", side_effect=AssertionError("network should not be used")):
                self.assertEqual(tool.download_asset(self.asset, dest)["status"], "verified-existing")

    def test_hash_mismatch_does_not_replace_existing_file(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            target = dest / "example/v1/app-x86_64.rpm"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"old-file")
            with patch.object(tool, "fetch", side_effect=lambda _: Response(b"corrupt")), patch.object(tool.time, "sleep"):
                with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                    tool.download_asset(self.asset, dest)
            self.assertEqual(target.read_bytes(), b"old-file")

    def test_truncated_file_is_not_promoted(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            with patch.object(tool, "fetch", side_effect=lambda _: Response(self.data, len(self.data) + 5)), patch.object(tool.time, "sleep"):
                with self.assertRaisesRegex(ValueError, "Truncated"):
                    tool.download_asset(self.asset, dest)
            self.assertFalse((dest / "example/v1/app-x86_64.rpm").exists())

    def test_error_report_preserves_partial_success(self):
        catalog = {"schema_version": 1, "owner": "storytold", "repositories": [{"status": "available", "assets": [self.asset]}]}
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            with patch.object(tool, "download_asset", side_effect=OSError("network unavailable")):
                with self.assertRaises(ValueError):
                    tool.download(catalog, dest, 1, tool.FORMATS)
            report = json.loads((dest / "download-report.json").read_text())
            self.assertEqual(report["files"][0]["status"], "error")
            self.assertEqual(report["dependencies"]["status"], "pending-linux-resolution")


if __name__ == "__main__":
    unittest.main()
