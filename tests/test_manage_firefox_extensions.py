#!/usr/bin/env python3
"""Unit tests for the repository-local Firefox policy manager.

Purpose: Verify merge ownership, conflict handling, idempotency, and the
install/block/finalize lifecycle without changing a real Firefox installation.
Usage: python3 -m unittest discover -s tests -p 'test_*.py'
Inputs: Repository files and temporary test directories.
Outputs/side effects: Test output and temporary files removed by unittest.
Prerequisites: Python 3 standard library.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "tools" / "manage-firefox-extensions.py"
SPEC = importlib.util.spec_from_file_location("firefox_policy", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load policy manager: {MODULE_PATH}")
policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(policy)


class FirefoxPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(
            prefix=".test-firefox-policy-", dir=REPO_ROOT
        )
        self.root = Path(self.temporary.name)
        self.target = self.root / "etc" / "firefox" / "policies" / "policies.json"
        self.state = self.root / "var" / "lib" / "ride-fedora" / "state.json"
        self.manifest = {
            "schema_version": 1,
            "default_installation_mode": "normal_installed",
            "extensions": [
                {
                    "name": "Example",
                    "id": "example@example.invalid",
                    "slug": "example",
                }
            ],
        }

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_target(self, value: dict) -> None:
        self.target.parent.mkdir(parents=True, exist_ok=True)
        self.target.write_text(json.dumps(value), encoding="utf-8")

    def read_target(self) -> dict:
        return json.loads(self.target.read_text(encoding="utf-8"))

    def test_install_remove_finalize_preserves_unrelated_policy(self) -> None:
        unrelated = {"installation_mode": "allowed"}
        self.write_target(
            {
                "policies": {
                    "Homepage": {"URL": "https://example.invalid"},
                    "Extensions": {
                        "Uninstall": ["admin-uninstall@example.invalid"],
                        "Locked": ["admin-locked@example.invalid"],
                    },
                    "ExtensionSettings": {"other@example.invalid": unrelated},
                }
            }
        )

        policy.install(self.manifest, self.target, self.state)
        installed = self.read_target()
        settings = installed["policies"]["ExtensionSettings"]
        self.assertEqual(settings["other@example.invalid"], unrelated)
        self.assertEqual(
            settings["example@example.invalid"]["installation_mode"],
            "normal_installed",
        )

        target_before = self.target.read_bytes()
        state_before = self.state.read_bytes()
        policy.install(self.manifest, self.target, self.state)
        self.assertEqual(self.target.read_bytes(), target_before)
        self.assertEqual(self.state.read_bytes(), state_before)

        policy.remove(self.manifest, self.target, self.state)
        blocked = self.read_target()["policies"]["ExtensionSettings"]
        self.assertEqual(
            blocked["example@example.invalid"], {"installation_mode": "blocked"}
        )
        self.assertEqual(blocked["other@example.invalid"], unrelated)
        removal_policy = self.read_target()["policies"]["Extensions"]
        self.assertEqual(
            removal_policy["Uninstall"],
            ["admin-uninstall@example.invalid", "example@example.invalid"],
        )
        self.assertEqual(removal_policy["Locked"], ["admin-locked@example.invalid"])

        policy.install(self.manifest, self.target, self.state)
        restored = self.read_target()["policies"]
        self.assertEqual(
            restored["Extensions"]["Uninstall"], ["admin-uninstall@example.invalid"]
        )
        self.assertEqual(
            restored["ExtensionSettings"]["example@example.invalid"]["installation_mode"],
            "normal_installed",
        )
        policy.remove(self.manifest, self.target, self.state)

        with mock.patch.object(policy, "verify_extensions_removed"):
            policy.finalize_remove(self.target, self.state)
        finalized = self.read_target()
        self.assertNotIn(
            "example@example.invalid",
            finalized["policies"]["ExtensionSettings"],
        )
        self.assertEqual(
            finalized["policies"]["ExtensionSettings"]["other@example.invalid"],
            unrelated,
        )
        self.assertEqual(
            finalized["policies"]["Extensions"],
            {"Uninstall": ["admin-uninstall@example.invalid"],
             "Locked": ["admin-locked@example.invalid"]},
        )
        self.assertFalse(self.state.exists())

    def test_observe_tracks_configured_pending_and_absent(self) -> None:
        self.assertEqual(policy.observe(self.manifest, self.target, self.state), "absent")
        policy.install(self.manifest, self.target, self.state)
        self.assertEqual(policy.observe(self.manifest, self.target, self.state), "configured")
        policy.remove(self.manifest, self.target, self.state)
        self.assertEqual(
            policy.observe(self.manifest, self.target, self.state), "removal-pending"
        )
        with mock.patch.object(policy, "verify_extensions_removed"):
            policy.finalize_remove(self.target, self.state)
        self.assertEqual(policy.observe(self.manifest, self.target, self.state), "absent")

    def test_finalize_refuses_live_firefox_process(self) -> None:
        policy.install(self.manifest, self.target, self.state)
        policy.remove(self.manifest, self.target, self.state)
        with mock.patch.object(policy, "firefox_running", return_value=True):
            with self.assertRaisesRegex(policy.PolicyError, "Firefox is still running"):
                policy.finalize_remove(self.target, self.state)
        self.assertTrue(self.state.exists())
        self.assertEqual(policy.observe(self.manifest, self.target, self.state), "removal-pending")

    def test_finalize_refuses_managed_extension_still_in_profile(self) -> None:
        profile = self.root / "profile"
        profile.mkdir()
        (profile / "extensions.json").write_text(
            json.dumps({"addons": [{"id": "example@example.invalid"}]}),
            encoding="utf-8",
        )
        policy.install(self.manifest, self.target, self.state)
        policy.remove(self.manifest, self.target, self.state)
        with (mock.patch.object(policy, "firefox_running", return_value=False),
              mock.patch.object(policy, "firefox_profiles", return_value={profile})):
            with self.assertRaisesRegex(policy.PolicyError, "extensions remain"):
                policy.finalize_remove(self.target, self.state)
        self.assertTrue(self.state.exists())
        self.assertEqual(policy.observe(self.manifest, self.target, self.state), "removal-pending")

    def test_profile_discovery_resolves_registered_relative_and_absolute_paths(self) -> None:
        home = self.root / "home" / "operator"
        firefox = home / ".mozilla" / "firefox"
        relative = firefox / "default-release"
        absolute = self.root / "custom-profile"
        relative.mkdir(parents=True)
        absolute.mkdir()
        (firefox / "profiles.ini").parent.mkdir(parents=True, exist_ok=True)
        (firefox / "profiles.ini").write_text(
            "[Profile0]\nName=Default\nIsRelative=1\nPath=default-release\n\n"
            f"[Profile1]\nName=Custom\nIsRelative=0\nPath={absolute}\n",
            encoding="utf-8",
        )
        account = SimpleNamespace(pw_dir=str(home))
        with mock.patch.object(policy.pwd, "getpwall", return_value=[account]):
            profiles = policy.firefox_profiles()
        self.assertEqual(profiles, {relative, absolute})

    def test_profile_discovery_fails_closed_on_malformed_ini(self) -> None:
        home = self.root / "home" / "operator"
        profile_ini = home / ".mozilla" / "firefox" / "profiles.ini"
        profile_ini.parent.mkdir(parents=True)
        profile_ini.write_text("[Profile0\nPath=broken\n", encoding="utf-8")
        account = SimpleNamespace(pw_dir=str(home))
        with mock.patch.object(policy.pwd, "getpwall", return_value=[account]):
            with self.assertRaisesRegex(policy.PolicyError, "cannot inspect Firefox profiles"):
                policy.firefox_profiles()

    def test_install_refuses_unmanaged_conflict(self) -> None:
        original = {
            "policies": {
                "ExtensionSettings": {
                    "example@example.invalid": {"installation_mode": "blocked"}
                }
            }
        }
        self.write_target(original)

        with self.assertRaises(policy.PolicyError):
            policy.install(self.manifest, self.target, self.state)

        self.assertEqual(self.read_target(), original)
        self.assertFalse(self.state.exists())

    def test_manifest_rejects_duplicate_slugs(self) -> None:
        manifest_path = self.root / "manifest.json"
        duplicate = dict(self.manifest)
        duplicate["extensions"] = self.manifest["extensions"] * 2
        manifest_path.write_text(json.dumps(duplicate), encoding="utf-8")

        with self.assertRaises(policy.PolicyError):
            policy.load_manifest(manifest_path)


if __name__ == "__main__":
    unittest.main()
