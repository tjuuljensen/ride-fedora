"""Focused ownership and recovery tests for Firefox global XPI deployment."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "manage-firefox-global-xpis.py"
SPEC = importlib.util.spec_from_file_location("firefox_global_xpis", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load Firefox XPI manager: {MODULE_PATH}")
manager = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(manager)


@pytest.fixture(autouse=True)
def temporary_paths_do_not_require_system_root(monkeypatch):
    def check_paths(*paths):
        for path in paths:
            manager.ensure_no_symlink(path)

    monkeypatch.setattr(manager, "require_root", check_paths)


@pytest.fixture
def paths(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    manifest = {
        "extensions": [
            {"id": "addon@example.invalid", "slug": "addon", "name": "Addon"},
            {"id": "second@example.invalid", "slug": "second", "name": "Second"},
        ]
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    target = tmp_path / "usr/lib64/mozilla/extensions" / manager.FIREFOX_APP_ID
    policy = tmp_path / "etc/firefox/policies/policies.json"
    state = tmp_path / "var/lib/ride/firefox.json"
    backup = tmp_path / "var/lib/ride/firefox-backup"
    return manifest, target, policy, state, backup


def install_fixture(monkeypatch, manifest, target, policy, state, backup):
    payloads = {
        extension["id"]: ("xpi-" + extension["id"]).encode()
        for extension in manifest["extensions"]
    }
    info = {
        extension_id: {
            "sha256": hashlib.sha256(payload).hexdigest(),
            "version": "1.0",
        }
        for extension_id, payload in payloads.items()
    }
    monkeypatch.setattr(manager, "fetch_current_xpis", lambda _: (info, payloads))
    manager.install(manifest, target, policy, state, backup)
    return payloads


def test_install_is_idempotent_and_records_exact_owned_files(monkeypatch, paths):
    manifest, target, policy, state, backup = paths
    payloads = install_fixture(monkeypatch, manifest, target, policy, state, backup)

    before = {path.name: path.read_bytes() for path in target.iterdir()}
    manager.install(manifest, target, policy, state, backup)

    assert before == {path.name: path.read_bytes() for path in target.iterdir()}
    record = json.loads(state.read_text(encoding="utf-8"))
    assert record["phase"] == "configured"
    assert set(record["managed_extensions"]) == set(payloads)
    assert all(Path(item["path"]).parent == target
               for item in record["managed_extensions"].values())
    assert state.stat().st_mode & 0o777 == 0o600
    assert all(path.stat().st_mode & 0o777 == 0o644 for path in target.iterdir())


def test_refuses_unowned_addon_and_policy_conflicts(paths):
    manifest, target, policy, state, backup = paths
    target.mkdir(parents=True)
    (target / manager.extension_filename(manifest["extensions"][0]["id"])).write_bytes(b"owner")
    with pytest.raises(manager.XpiError, match="unowned Firefox extension"):
        manager.current_state(manifest, target, policy, state, backup)

    (target / manager.extension_filename(manifest["extensions"][0]["id"])).unlink()
    policy.parent.mkdir(parents=True)
    policy.write_text(json.dumps({"policies": {"ExtensionSettings": {
        manifest["extensions"][0]["id"]: {"installation_mode": "allowed"},
    }}}), encoding="utf-8")
    with pytest.raises(manager.XpiError, match="ExtensionSettings conflicts"):
        manager.current_state(manifest, target, policy, state, backup)


def test_tampered_owned_xpi_is_preserved_and_refused(monkeypatch, paths):
    manifest, target, policy, state, backup = paths
    install_fixture(monkeypatch, manifest, target, policy, state, backup)
    owned = target / manager.extension_filename(manifest["extensions"][0]["id"])
    owned.write_bytes(b"changed by somebody else")

    with pytest.raises(manager.XpiError, match="changed or is missing"):
        manager.current_state(manifest, target, policy, state, backup)
    assert owned.read_bytes() == b"changed by somebody else"


def test_removal_keeps_verified_recovery_and_restore_is_exact(monkeypatch, paths):
    manifest, target, policy, state, backup = paths
    payloads = install_fixture(monkeypatch, manifest, target, policy, state, backup)

    manager.begin_removal(manifest, target, policy, state, backup)
    assert manager.current_state(manifest, target, policy, state, backup) == "removal-pending"
    assert not list(target.glob("*.xpi"))
    assert {path.name: path.read_bytes() for path in backup.iterdir()} == {
        manager.extension_filename(extension_id): content
        for extension_id, content in payloads.items()
    }
    assert backup.stat().st_mode & 0o777 == 0o700
    assert all(path.stat().st_mode & 0o777 == 0o600 for path in backup.iterdir())

    manager.restore(manifest, target, policy, state, backup)
    assert manager.current_state(manifest, target, policy, state, backup) == "configured"
    assert {path.name: path.read_bytes() for path in target.glob("*.xpi")} == {
        manager.extension_filename(extension_id): content
        for extension_id, content in payloads.items()
    }
    assert not backup.exists()


def test_finalize_requires_stopped_firefox_and_absent_profile_addons(monkeypatch, paths):
    manifest, target, policy, state, backup = paths
    install_fixture(monkeypatch, manifest, target, policy, state, backup)
    manager.begin_removal(manifest, target, policy, state, backup)

    monkeypatch.setattr(manager._AMO, "firefox_running", lambda: True)
    with pytest.raises(manager.XpiError, match="Firefox is still running"):
        manager.finalize_removal(manifest, target, policy, state, backup)
    assert state.exists() and backup.exists()

    monkeypatch.setattr(manager._AMO, "firefox_running", lambda: False)
    monkeypatch.setattr(manager._AMO, "verify_extensions_removed", lambda _: None)
    manager.finalize_removal(manifest, target, policy, state, backup)
    assert not state.exists() and not backup.exists()
    assert not target.exists()
