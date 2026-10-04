#!/usr/bin/env python3
"""Manage RIDE's Firefox ExtensionSettings policy.

Purpose:
    Validate the repository-owned Firefox extension manifest and merge its
    entries into Firefox's system-wide policies.json without replacing other
    administrator policies.
Behavior:
    ``check`` validates the manifest and can verify each extension against
    Mozilla Add-ons. ``install`` performs the online check before an atomic
    policy update. ``remove`` switches RIDE-owned entries to ``blocked`` so
    Firefox uninstalls them. ``finalize-remove`` later removes the tombstones.
Usage:
    manage-firefox-extensions.py check [--online]
    manage-firefox-extensions.py install [--offline]
    manage-firefox-extensions.py remove
    manage-firefox-extensions.py finalize-remove
Inputs/environment:
    The manifest defaults to ``policies/firefox-extensions.json``. Target and
    state paths can be overridden with command-line options for testing.
Outputs/side effects:
    Installation updates ``/etc/firefox/policies/policies.json`` and writes
    ownership state below ``/var/lib/ride-fedora``. Existing policy files are
    backed up before changes. Online checks download XPIs to temporary files.
Prerequisites:
    Python 3 standard library, HTTPS access to addons.mozilla.org for online
    checks, and root privileges when writing the default system paths.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
from typing import Any
import urllib.error
import urllib.request
import zipfile


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO_ROOT / "policies" / "firefox-extensions.json"
DEFAULT_TARGET = Path("/etc/firefox/policies/policies.json")
DEFAULT_STATE = Path("/var/lib/ride-fedora/firefox-extensions.json")
AMO_API = "https://addons.mozilla.org/api/v5/addons/addon/{slug}/"
AMO_XPI = "https://addons.mozilla.org/firefox/downloads/latest/{slug}/latest.xpi"
USER_AGENT = "ride-fedora-firefox-policy/1.0"
MAX_XPI_BYTES = 100 * 1024 * 1024
ALLOWED_MODES = {"normal_installed", "force_installed"}
BLOCKED_SETTING = {"installation_mode": "blocked"}


class PolicyError(RuntimeError):
    """Expected validation or policy-management failure."""


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError as exc:
        raise PolicyError(f"{label} not found: {path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise PolicyError(f"Cannot read {label} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PolicyError(f"{label} must contain a JSON object: {path}")
    return value


def load_manifest(path: Path) -> dict[str, Any]:
    manifest = read_json(path, "manifest")
    if manifest.get("schema_version") != 1:
        raise PolicyError("manifest schema_version must be 1")

    default_mode = manifest.get("default_installation_mode")
    if default_mode not in ALLOWED_MODES:
        raise PolicyError(
            "default_installation_mode must be normal_installed or force_installed"
        )

    extensions = manifest.get("extensions")
    if not isinstance(extensions, list) or not extensions:
        raise PolicyError("manifest extensions must be a non-empty list")

    ids: set[str] = set()
    slugs: set[str] = set()
    for index, extension in enumerate(extensions, start=1):
        if not isinstance(extension, dict):
            raise PolicyError(f"extension #{index} must be an object")
        for field in ("name", "id", "slug"):
            if not isinstance(extension.get(field), str) or not extension[field].strip():
                raise PolicyError(f"extension #{index} has invalid {field}")
        extension_id = extension["id"]
        slug = extension["slug"]
        if extension_id in ids:
            raise PolicyError(f"duplicate extension id: {extension_id}")
        if slug in slugs:
            raise PolicyError(f"duplicate extension slug: {slug}")
        ids.add(extension_id)
        slugs.add(slug)
        mode = extension.get("installation_mode", default_mode)
        if mode not in ALLOWED_MODES:
            raise PolicyError(f"invalid installation mode for {slug}: {mode}")

    return manifest


def desired_settings(manifest: dict[str, Any]) -> dict[str, dict[str, str]]:
    default_mode = manifest["default_installation_mode"]
    settings: dict[str, dict[str, str]] = {}
    for extension in manifest["extensions"]:
        settings[extension["id"]] = {
            "installation_mode": extension.get("installation_mode", default_mode),
            "install_url": AMO_XPI.format(slug=extension["slug"]),
        }
    return settings


def request_bytes(url: str, attempts: int = 3, timeout: int = 30) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            if exc.code < 500 or attempt == attempts:
                raise PolicyError(f"HTTP {exc.code} from {url}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if attempt == attempts:
                raise PolicyError(f"request failed for {url}: {exc}") from exc
        time.sleep(attempt)
    raise AssertionError("unreachable")


def download_xpi(url: str, destination: Path, timeout: int = 60) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    digest = hashlib.sha256()
    size = 0
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            with destination.open("wb") as output:
                while chunk := response.read(1024 * 1024):
                    size += len(chunk)
                    if size > MAX_XPI_BYTES:
                        raise PolicyError(f"XPI exceeds {MAX_XPI_BYTES} bytes: {url}")
                    digest.update(chunk)
                    output.write(chunk)
    except urllib.error.HTTPError as exc:
        raise PolicyError(f"HTTP {exc.code} while downloading {url}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise PolicyError(f"cannot download {url}: {exc}") from exc
    return digest.hexdigest()


def xpi_manifest_id(path: Path) -> str | None:
    try:
        with zipfile.ZipFile(path) as archive:
            bad_member = archive.testzip()
            if bad_member is not None:
                raise PolicyError(f"corrupt XPI member: {bad_member}")
            try:
                raw_manifest = archive.read("manifest.json")
            except KeyError as exc:
                raise PolicyError("XPI has no manifest.json") from exc
    except zipfile.BadZipFile as exc:
        raise PolicyError("download is not a valid XPI/ZIP file") from exc

    try:
        manifest = json.loads(raw_manifest.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PolicyError(f"invalid XPI manifest.json: {exc}") from exc

    for parent in ("browser_specific_settings", "applications"):
        value = manifest.get(parent, {})
        if isinstance(value, dict):
            gecko = value.get("gecko", {})
            if isinstance(gecko, dict) and isinstance(gecko.get("id"), str):
                return gecko["id"]
    return None


def check_online(manifest: dict[str, Any]) -> None:
    with tempfile.TemporaryDirectory(prefix="ride-firefox-check-") as temp_dir:
        temp_root = Path(temp_dir)
        for extension in manifest["extensions"]:
            slug = extension["slug"]
            print(f"Checking {slug}...")
            api_url = AMO_API.format(slug=slug)
            try:
                metadata = json.loads(request_bytes(api_url).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise PolicyError(f"invalid AMO response for {slug}: {exc}") from exc

            if metadata.get("guid") != extension["id"]:
                raise PolicyError(
                    f"AMO id mismatch for {slug}: expected {extension['id']}, "
                    f"got {metadata.get('guid')}"
                )
            if metadata.get("status") != "public" or metadata.get("is_disabled"):
                raise PolicyError(f"AMO extension is not public and enabled: {slug}")

            file_info = metadata.get("current_version", {}).get("file", {})
            expected_hash = file_info.get("hash")
            if not isinstance(expected_hash, str) or not expected_hash.startswith("sha256:"):
                raise PolicyError(f"AMO did not provide a SHA-256 hash for {slug}")

            xpi_path = temp_root / f"{slug}.xpi"
            actual_hash = download_xpi(AMO_XPI.format(slug=slug), xpi_path)
            if actual_hash != expected_hash.removeprefix("sha256:"):
                raise PolicyError(f"XPI SHA-256 mismatch for {slug}")
            declared_id = xpi_manifest_id(xpi_path)
            if declared_id is not None and declared_id != extension["id"]:
                raise PolicyError(
                    f"XPI manifest id mismatch for {slug}: expected {extension['id']}, "
                    f"got {declared_id}"
                )


def load_policy(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"policies": {}}
    policy = read_json(path, "Firefox policy")
    policies = policy.get("policies")
    if not isinstance(policies, dict):
        raise PolicyError("Firefox policy must contain a policies object")
    extension_settings = policies.get("ExtensionSettings", {})
    if not isinstance(extension_settings, dict):
        raise PolicyError("policies.ExtensionSettings must be an object")
    return policy


def load_state(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    state = read_json(path, "RIDE state")
    managed = state.get("managed_extensions")
    if state.get("schema_version") != 1 or not isinstance(managed, dict):
        raise PolicyError(f"invalid RIDE state: {path}")
    if state.get("phase") not in {"installed", "removal_pending"}:
        raise PolicyError(f"invalid RIDE state phase: {path}")
    return state


def canonical_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_atomic(path: Path, value: dict[str, Any], mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(canonical_bytes(value))
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def backup_file(path: Path) -> Path | None:
    if not path.exists():
        return None
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = path.with_name(f"{path.name}.bak-{timestamp}-{os.getpid()}")
    shutil.copy2(path, backup)
    return backup


def ensure_system_write_allowed(path: Path) -> None:
    if os.name == "posix" and str(path).startswith("/etc/"):
        if hasattr(os, "geteuid") and os.geteuid() != 0:
            raise PolicyError(f"root privileges are required to write {path}")


def build_state(
    phase: str,
    managed: dict[str, dict[str, str]],
    current: dict[str, Any] | None,
) -> dict[str, Any]:
    if (
        current is not None
        and current.get("phase") == phase
        and current.get("managed_extensions") == managed
    ):
        return current
    return {
        "schema_version": 1,
        "phase": phase,
        "managed_extensions": managed,
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def apply_transaction(
    target: Path,
    old_policy: dict[str, Any],
    new_policy: dict[str, Any],
    state_path: Path,
    new_state: dict[str, Any],
) -> Path | None:
    target_existed = target.exists()
    target_changed = not target_existed or canonical_bytes(old_policy) != canonical_bytes(
        new_policy
    )
    old_state = state_path.read_bytes() if state_path.exists() else None
    current_state = load_state(state_path) if state_path.exists() else None
    state_changed = canonical_bytes(current_state) != canonical_bytes(new_state) if current_state else True
    if not target_changed and not state_changed:
        return None

    backup = backup_file(target) if target_changed else None
    try:
        if target_changed:
            write_atomic(target, new_policy)
        if state_changed:
            write_atomic(state_path, new_state)
    except Exception:
        if target_changed:
            if target_existed:
                write_atomic(target, old_policy)
            else:
                target.unlink(missing_ok=True)
        if old_state is None:
            state_path.unlink(missing_ok=True)
        else:
            state_path.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
            state_path.write_bytes(old_state)
        raise
    return backup


def install(manifest: dict[str, Any], target: Path, state_path: Path) -> None:
    ensure_system_write_allowed(target)
    policy = load_policy(target)
    state = load_state(state_path)
    wanted = desired_settings(manifest)
    updated = copy.deepcopy(policy)
    settings = updated.setdefault("policies", {}).setdefault("ExtensionSettings", {})

    previous = state.get("managed_extensions", {}) if state else {}
    for extension_id in previous:
        settings.pop(extension_id, None)

    for extension_id, configuration in wanted.items():
        existing = settings.get(extension_id)
        if existing is not None and existing != configuration:
            raise PolicyError(
                f"refusing to replace unmanaged ExtensionSettings entry: {extension_id}"
            )
        settings[extension_id] = configuration

    new_state = build_state("installed", wanted, state)
    backup = apply_transaction(target, policy, updated, state_path, new_state)
    if backup:
        print(f"Previous Firefox policy backed up to: {backup}")
    print(f"Managed {len(wanted)} Firefox extensions in: {target}")


def remove(manifest: dict[str, Any], target: Path, state_path: Path) -> None:
    ensure_system_write_allowed(target)
    if not target.exists():
        raise PolicyError(f"Firefox policy does not exist: {target}")

    policy = load_policy(target)
    state = load_state(state_path)
    expected = state.get("managed_extensions", {}) if state else desired_settings(manifest)
    settings = policy["policies"].get("ExtensionSettings", {})
    conflicts = [
        extension_id
        for extension_id, prior_value in expected.items()
        if extension_id in settings and settings[extension_id] != prior_value
    ]
    if conflicts:
        joined = ", ".join(conflicts)
        raise PolicyError(f"refusing to replace modified managed entries: {joined}")

    blocked = {extension_id: copy.deepcopy(BLOCKED_SETTING) for extension_id in expected}
    updated = copy.deepcopy(policy)
    updated_settings = updated["policies"].setdefault("ExtensionSettings", {})
    updated_settings.update(blocked)
    new_state = build_state("removal_pending", blocked, state)
    backup = apply_transaction(target, policy, updated, state_path, new_state)
    if backup:
        print(f"Previous Firefox policy backed up to: {backup}")
    print(f"Marked {len(blocked)} Firefox extensions blocked for uninstall")
    print("Restart Firefox, verify removal, then run FinalizeFirefoxAddonRemoval")


def finalize_remove(target: Path, state_path: Path) -> None:
    ensure_system_write_allowed(target)
    state = load_state(state_path)
    if state is None or state.get("phase") != "removal_pending":
        raise PolicyError("no pending RIDE Firefox extension removal was found")
    if not target.exists():
        raise PolicyError(f"Firefox policy does not exist: {target}")

    policy = load_policy(target)
    managed = state["managed_extensions"]
    settings = policy["policies"].get("ExtensionSettings", {})
    conflicts = [
        extension_id
        for extension_id, prior_value in managed.items()
        if extension_id in settings and settings[extension_id] != prior_value
    ]
    if conflicts:
        joined = ", ".join(conflicts)
        raise PolicyError(f"refusing to remove modified blocked entries: {joined}")

    updated = copy.deepcopy(policy)
    updated_settings = updated["policies"].get("ExtensionSettings", {})
    for extension_id in managed:
        updated_settings.pop(extension_id, None)
    if not updated_settings:
        updated["policies"].pop("ExtensionSettings", None)

    backup = backup_file(target)
    write_atomic(target, updated)
    state_path.unlink()
    if backup:
        print(f"Previous Firefox policy backed up to: {backup}")
    print(f"Removed {len(managed)} completed RIDE removal tombstones")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="validate desired state")
    check_parser.add_argument("--online", action="store_true")

    install_parser = subparsers.add_parser("install", help="merge and install policy")
    install_parser.add_argument(
        "--offline",
        action="store_true",
        help="skip AMO/XPI verification; use only when the network is unavailable",
    )
    subparsers.add_parser("remove", help="block extensions so Firefox uninstalls them")
    subparsers.add_parser(
        "finalize-remove", help="remove policy tombstones after Firefox uninstalls"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        manifest = load_manifest(args.manifest)
        if args.command == "check":
            if args.online:
                check_online(manifest)
            print(f"Validated {len(manifest['extensions'])} Firefox extensions")
        elif args.command == "install":
            if not args.offline:
                check_online(manifest)
            install(manifest, args.target, args.state)
        elif args.command == "remove":
            remove(manifest, args.target, args.state)
        elif args.command == "finalize-remove":
            finalize_remove(args.target, args.state)
        return 0
    except PolicyError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ERROR: unexpected failure: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
