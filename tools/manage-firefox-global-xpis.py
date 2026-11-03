#!/usr/bin/env python3
"""Manage a pinned Firefox add-on list through Fedora's global XPI directory.

Purpose:
    Install, observe, remove, restore, and finalize the repository-owned AMO
    add-on set without altering administrator ExtensionSettings policy.
Behavior:
    Download current public AMO XPIs, verify their publisher-provided SHA-256
    and embedded IDs, and install owned files under Firefox's global extension
    directory. Removal is restart-aware and keeps exact XPI recovery copies.
Compatibility:
    Python 3.11+ on Fedora 44 Workstation x86_64 with Firefox RPM.
Usage:
    manage-firefox-global-xpis.py [--manifest PATH] [--target PATH]
      [--policy PATH] [--state PATH] [--backup-dir PATH]
      check [--online] | observe | set-state configured|removal-pending|absent
Inputs:
    policies/firefox-extensions.json and HTTPS AMO metadata/XPI downloads.
Side effects:
    Writes root-owned XPI files to /usr/lib64/mozilla/extensions/<Firefox ID>,
    plus protected ownership and pending-removal recovery state below
    /var/lib/ride-fedora. It does not modify Firefox policies or profile data.
Prerequisites:
    Root privileges for default system paths and HTTPS access to AMO when
    configuring the add-ons.
Ownership and provenance:
    RIDE Fedora; add-ons and metadata are from the Mozilla Add-ons service.
Version:
    3.0.0.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "policies/firefox-extensions.json"
POLICY = Path("/etc/firefox/policies/policies.json")
FIREFOX_APP_ID = "{ec8030f7-c20a-464f-9b0e-13a3a9e97384}"
TARGET = Path(f"/usr/lib64/mozilla/extensions/{FIREFOX_APP_ID}")
STATE = Path("/var/lib/ride-fedora/firefox-global-xpis.json")
BACKUP_DIR = Path("/var/lib/ride-fedora/firefox-global-xpi-removal")

_SPEC = importlib.util.spec_from_file_location(
    "firefox_addon_sources", REPO_ROOT / "tools/manage-firefox-extensions.py"
)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("cannot load the shared AMO verification helpers")
_AMO = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_AMO)


class XpiError(RuntimeError):
    """Expected Firefox XPI lifecycle error."""


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise XpiError(f"cannot read {label} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise XpiError(f"{label} must be a JSON object")
    return value


def ensure_no_symlink(path: Path) -> None:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        if current.is_symlink():
            raise XpiError(f"refusing symbolic link in managed path: {current}")


def require_root(*paths: Path) -> None:
    if os.name == "posix" and os.geteuid() != 0:
        raise XpiError("root privileges are required for the system Firefox extension directory")
    for path in paths:
        ensure_no_symlink(path)


def extension_filename(extension_id: str) -> str:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@{}._+-")
    if not extension_id or any(char not in allowed for char in extension_id):
        raise XpiError(f"invalid Firefox extension ID for a filename: {extension_id!r}")
    return f"{extension_id}.xpi"


def load_manifest(path: Path) -> dict[str, Any]:
    return _AMO.load_manifest(path)


def state_read(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise XpiError(f"Firefox XPI state is not a regular owned file: {path}")
    state = load_json(path, "Firefox XPI state")
    if state.get("schema_version") != 1 or state.get("phase") not in {"configured", "removal_pending"}:
        raise XpiError("invalid Firefox XPI ownership state")
    if not isinstance(state.get("managed_extensions"), dict):
        raise XpiError("Firefox XPI state has no managed extension map")
    return state


def atomic_json(path: Path, value: dict[str, Any], mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
    ensure_no_symlink(path.parent)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def managed_map(manifest: dict[str, Any], metadata: dict[str, dict[str, str]],
                target: Path) -> dict[str, dict[str, str]]:
    result = {}
    for extension in manifest["extensions"]:
        extension_id = extension["id"]
        result[extension_id] = {
            "name": extension["name"],
            "slug": extension["slug"],
            "path": str(target / extension_filename(extension_id)),
            "sha256": metadata[extension_id]["sha256"],
            "version": metadata[extension_id]["version"],
        }
    return result


def fetch_current_xpis(manifest: dict[str, Any]) -> tuple[dict[str, dict[str, str]], dict[str, bytes]]:
    information: dict[str, dict[str, str]] = {}
    contents: dict[str, bytes] = {}
    with tempfile.TemporaryDirectory(prefix="ride-firefox-xpi-stage-") as temp:
        root = Path(temp)
        for extension in manifest["extensions"]:
            slug = extension["slug"]
            extension_id = extension["id"]
            try:
                metadata = json.loads(_AMO.request_bytes(_AMO.AMO_API.format(slug=slug)).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise XpiError(f"invalid AMO metadata for {slug}: {exc}") from exc
            if metadata.get("guid") != extension_id or metadata.get("status") != "public" or metadata.get("is_disabled"):
                raise XpiError(f"AMO identity/status mismatch for {slug}")
            current = metadata.get("current_version", {})
            file_info = current.get("file", {}) if isinstance(current, dict) else {}
            expected = file_info.get("hash") if isinstance(file_info, dict) else None
            if not isinstance(expected, str) or not expected.startswith("sha256:"):
                raise XpiError(f"AMO has no SHA-256 for {slug}")
            path = root / f"{len(information)}.xpi"
            actual = _AMO.download_xpi(_AMO.AMO_XPI.format(slug=slug), path)
            if actual != expected.removeprefix("sha256:"):
                raise XpiError(f"AMO XPI SHA-256 mismatch for {slug}")
            if _AMO.xpi_manifest_id(path) != extension_id:
                raise XpiError(f"XPI embedded ID mismatch for {slug}")
            information[extension_id] = {"sha256": actual, "version": str(current.get("version", "unknown"))}
            contents[extension_id] = path.read_bytes()
    return information, contents


def policy_conflicts(manifest: dict[str, Any], policy_path: Path) -> None:
    if not policy_path.exists():
        return
    policy = _AMO.load_policy(policy_path)
    settings = policy.get("policies", {}).get("ExtensionSettings", {})
    conflicts = sorted(set(extension["id"] for extension in manifest["extensions"]) & set(settings))
    if conflicts:
        raise XpiError("unrelated or legacy ExtensionSettings conflicts for: " + ", ".join(conflicts))


def current_state(manifest: dict[str, Any], target: Path, policy_path: Path,
                  state_path: Path, backup_dir: Path) -> str:
    require_root(target, policy_path, state_path, backup_dir)
    state = state_read(state_path)
    if state is None:
        policy_conflicts(manifest, policy_path)
        for extension in manifest["extensions"]:
            path = target / extension_filename(extension["id"])
            if path.exists() or path.is_symlink():
                raise XpiError(f"unowned Firefox extension file already exists: {path}")
        if backup_dir.exists():
            raise XpiError(f"orphaned Firefox XPI recovery directory needs review: {backup_dir}")
        return "absent"
    expected_ids = {extension["id"] for extension in manifest["extensions"]}
    managed = state["managed_extensions"]
    if set(managed) != expected_ids:
        raise XpiError("owned Firefox extension list differs from the declared manifest")
    phase = state["phase"]
    if phase == "configured":
        if backup_dir.exists():
            raise XpiError("unexpected Firefox XPI recovery directory while configured")
        for extension_id, record in managed.items():
            path = target / extension_filename(extension_id)
            if not path.is_file() or path.is_symlink() or sha256(path) != record.get("sha256"):
                raise XpiError(f"owned Firefox XPI changed or is missing: {path}")
    else:
        if not backup_dir.is_dir() or backup_dir.is_symlink():
            raise XpiError("Firefox XPI removal backup is missing or unsafe")
        for extension_id, record in managed.items():
            backup = backup_dir / extension_filename(extension_id)
            source = target / extension_filename(extension_id)
            if not backup.is_file() or backup.is_symlink() or sha256(backup) != record.get("sha256"):
                raise XpiError(f"Firefox XPI recovery copy changed or is missing: {backup}")
            if source.exists() and (source.is_symlink() or not source.is_file() or sha256(source) != record.get("sha256")):
                raise XpiError(f"unexpected Firefox XPI conflict during removal: {source}")
    return phase.replace("_", "-")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def install(manifest: dict[str, Any], target: Path, policy_path: Path,
            state_path: Path, backup_dir: Path) -> None:
    observed = current_state(manifest, target, policy_path, state_path, backup_dir)
    if observed == "configured":
        return
    if observed == "removal-pending":
        restore(manifest, target, policy_path, state_path, backup_dir)
        return
    require_root(target.parent, policy_path, state_path, backup_dir)
    policy_conflicts(manifest, policy_path)
    info, payloads = fetch_current_xpis(manifest)
    managed = managed_map(manifest, info, target)
    target_existed = target.exists()
    if target_existed and (target.is_symlink() or not target.is_dir()):
        raise XpiError(f"Firefox global extension destination is not a directory: {target}")
    target.mkdir(parents=True, mode=0o755, exist_ok=True)
    created: list[Path] = []
    try:
        with tempfile.TemporaryDirectory(prefix=".ride-firefox-xpis-", dir=target) as staging:
            stage = Path(staging)
            for extension_id, payload in payloads.items():
                path = target / extension_filename(extension_id)
                if path.exists() or path.is_symlink():
                    raise XpiError(f"unowned Firefox extension file already exists: {path}")
                temporary = stage / extension_filename(extension_id)
                temporary.write_bytes(payload)
                os.chmod(temporary, 0o644)
                with temporary.open("rb") as stream:
                    os.fsync(stream.fileno())
                os.replace(temporary, path)
                created.append(path)
        state = {
            "schema_version": 1,
            "phase": "configured",
            "target_directory_created": not target_existed,
            "managed_extensions": managed,
        }
        atomic_json(state_path, state)
    except Exception:
        for path in created:
            path.unlink(missing_ok=True)
        if not target_existed:
            try:
                target.rmdir()
            except OSError:
                pass
        raise


def begin_removal(manifest: dict[str, Any], target: Path, policy_path: Path,
                  state_path: Path, backup_dir: Path) -> None:
    if current_state(manifest, target, policy_path, state_path, backup_dir) != "configured":
        raise XpiError("Firefox add-ons are not configured")
    state = state_read(state_path)
    assert state is not None
    backup_dir.mkdir(parents=True, mode=0o700, exist_ok=False)
    try:
        os.chmod(backup_dir, 0o700)
        for extension_id, record in state["managed_extensions"].items():
            source = target / extension_filename(extension_id)
            backup = backup_dir / extension_filename(extension_id)
            shutil.copy2(source, backup)
            os.chmod(backup, 0o600)
            if sha256(backup) != record["sha256"]:
                raise XpiError(f"failed to verify Firefox XPI recovery copy: {backup}")
        pending = dict(state)
        pending["phase"] = "removal_pending"
        atomic_json(state_path, pending)
    except Exception:
        shutil.rmtree(backup_dir, ignore_errors=True)
        raise
    for extension_id in state["managed_extensions"]:
        (target / extension_filename(extension_id)).unlink()
    print("Firefox add-on removal is pending a browser restart")


def restore(manifest: dict[str, Any], target: Path, policy_path: Path,
            state_path: Path, backup_dir: Path) -> None:
    if current_state(manifest, target, policy_path, state_path, backup_dir) != "removal-pending":
        raise XpiError("no pending Firefox add-on removal to restore")
    state = state_read(state_path)
    assert state is not None
    target.mkdir(parents=True, mode=0o755, exist_ok=True)
    created: list[Path] = []
    try:
        for extension_id, record in state["managed_extensions"].items():
            source = backup_dir / extension_filename(extension_id)
            destination = target / extension_filename(extension_id)
            if destination.exists() or destination.is_symlink():
                raise XpiError(f"Firefox XPI destination appeared during restore: {destination}")
            with tempfile.NamedTemporaryFile(dir=target, prefix=".ride-firefox-", delete=False) as stream:
                temporary = Path(stream.name)
                shutil.copyfile(source, temporary)
                os.chmod(temporary, 0o644)
                stream.flush()
                os.fsync(stream.fileno())
            if sha256(temporary) != record["sha256"]:
                temporary.unlink(missing_ok=True)
                raise XpiError(f"Firefox XPI recovery copy failed digest check: {source}")
            os.replace(temporary, destination)
            created.append(destination)
        configured = dict(state)
        configured["phase"] = "configured"
        atomic_json(state_path, configured)
        shutil.rmtree(backup_dir)
    except Exception:
        for path in created:
            path.unlink(missing_ok=True)
        raise


def finalize_removal(manifest: dict[str, Any], target: Path, policy_path: Path,
                     state_path: Path, backup_dir: Path) -> None:
    if current_state(manifest, target, policy_path, state_path, backup_dir) != "removal-pending":
        raise XpiError("no pending Firefox add-on removal was found")
    state = state_read(state_path)
    assert state is not None
    ids = set(state["managed_extensions"])
    if _AMO.firefox_running():
        raise XpiError("Firefox is still running; close Firefox before finalizing add-on removal")
    _AMO.verify_extensions_removed(ids)
    for extension_id, record in state["managed_extensions"].items():
        source = target / extension_filename(extension_id)
        if source.exists():
            if source.is_symlink() or not source.is_file() or sha256(source) != record["sha256"]:
                raise XpiError(f"unexpected Firefox XPI conflict during finalization: {source}")
            source.unlink()
    shutil.rmtree(backup_dir)
    state_path.unlink()
    if state.get("target_directory_created"):
        try:
            target.rmdir()
        except OSError:
            pass
    print(f"Removed completed Firefox add-on state for {len(ids)} managed extensions")


def set_state(manifest: dict[str, Any], target: Path, policy_path: Path,
              state_path: Path, backup_dir: Path, desired: str) -> None:
    observed = current_state(manifest, target, policy_path, state_path, backup_dir)
    if desired == "configured":
        if observed == "absent":
            install(manifest, target, policy_path, state_path, backup_dir)
        elif observed == "removal-pending":
            restore(manifest, target, policy_path, state_path, backup_dir)
    elif desired == "removal-pending":
        if observed == "configured":
            begin_removal(manifest, target, policy_path, state_path, backup_dir)
        elif observed == "absent":
            raise XpiError("cannot request Firefox add-on removal when already absent")
    elif desired == "absent":
        if observed == "configured":
            begin_removal(manifest, target, policy_path, state_path, backup_dir)
        elif observed == "removal-pending":
            finalize_removal(manifest, target, policy_path, state_path, backup_dir)
    else:
        raise XpiError(f"invalid Firefox add-on state: {desired}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--target", type=Path, default=TARGET)
    parser.add_argument("--policy", type=Path, default=POLICY)
    parser.add_argument("--state", type=Path, default=STATE)
    parser.add_argument("--backup-dir", type=Path, default=BACKUP_DIR)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check")
    check.add_argument("--online", action="store_true")
    sub.add_parser("observe")
    state = sub.add_parser("set-state")
    state.add_argument("desired_state", choices=("configured", "removal-pending", "absent"))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        require_root(args.target, args.policy, args.state, args.backup_dir)
        manifest = load_manifest(args.manifest)
        if args.command == "check":
            if args.online:
                fetch_current_xpis(manifest)
            else:
                print(f"Validated {len(manifest['extensions'])} Firefox add-ons")
        elif args.command == "observe":
            print(current_state(manifest, args.target, args.policy, args.state, args.backup_dir))
        elif args.command == "set-state":
            set_state(manifest, args.target, args.policy, args.state, args.backup_dir, args.desired_state)
            print(current_state(manifest, args.target, args.policy, args.state, args.backup_dir))
        return 0
    except (XpiError, _AMO.PolicyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ERROR: unexpected failure: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
