#!/usr/bin/env python3
"""Install or remove the RIDE-owned Ferium no-GUI binary.

Purpose: Manage the optional Ferium CLI without touching its user data.
Behavior: Fetch the fixed upstream release over HTTPS, verify the reported
          version, record observed hashes, and remove only unchanged RIDE files.
Compatibility: Python 3.11+ on Linux; used only on Fedora 44 Server x86_64.
Usage: python3 tools/manage-ferium.py observe|install|remove
Inputs: The current user's HOME and the fixed Ferium v4.7.1 release URL.
Side effects: Owns ~/.local/opt/ride-fedora/ferium/4.7.1, a ~/.local/bin link,
              and a private ownership manifest. Never changes Ferium config.
Prerequisites: Python 3, curl, and a working network for install.
Owner: RIDE Fedora maintainers. Provenance: Ferium upstream v4.7.1 release.
Version: 3.0.0.

The upstream Linux release does not publish a SHA-256 file. The asset is
downloaded from its immutable version URL over HTTPS, then its archive and
binary digests are recorded locally for integrity checks after installation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.request
import zipfile


VERSION = "4.7.1"
ASSET_URL = (
    "https://github.com/gorilla-devs/ferium/releases/download/v4.7.1/"
    "ferium-linux-nogui.zip"
)
MAX_ARCHIVE_BYTES = 20_000_000
MAX_BINARY_BYTES = 15_000_000
ERROR = "RIDE Ferium: "


class FeriumError(Exception):
    """A safe, user-facing lifecycle failure."""


def paths(home: Path) -> tuple[Path, Path, Path]:
    root = home / ".local/opt/ride-fedora/ferium" / VERSION
    return root, home / ".local/bin/ferium", home / ".local/share/ride-fedora/owned-tools/package.ferium-portable.json"


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_manifest(path: Path) -> dict | None:
    if not path.exists() and not path.is_symlink():
        return None
    if path.is_symlink() or not path.is_file():
        raise FeriumError("ownership manifest is not a regular file")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FeriumError(f"cannot read ownership manifest: {exc}") from exc
    if (not isinstance(value, dict) or value.get("schemaVersion") != 1 or
            value.get("id") != "package.ferium-portable" or
            value.get("version") != VERSION or value.get("assetUrl") != ASSET_URL or
            not all(isinstance(value.get(name), str) for name in
                    ("archiveSha256", "binarySha256", "destination"))):
        raise FeriumError("ownership manifest is invalid or belongs to another operation")
    return value


def observe(home: Path) -> str:
    root, link, manifest_path = paths(home)
    manifest = load_manifest(manifest_path)
    if manifest is None and not root.exists() and not root.is_symlink() and not link.exists() and not link.is_symlink():
        return "absent"
    if (manifest is None or root.is_symlink() or not root.is_dir() or
            link.is_symlink() is False or not link.exists() or
            os.readlink(link) != str(root / "ferium") or
            manifest_path.stat().st_uid != os.getuid() or
            stat.S_IMODE(manifest_path.stat().st_mode) != 0o600):
        return "unowned"
    binary = root / "ferium"
    marker = root / ".ride-owned"
    if (root.stat().st_uid != os.getuid() or
            {item.name for item in root.iterdir()} != {"ferium", ".ride-owned"} or
            not binary.is_file() or binary.is_symlink() or not os.access(binary, os.X_OK) or
            not marker.is_file() or marker.is_symlink() or
            manifest["destination"] != str(link) or
            digest(binary) != manifest["binarySha256"] or
            marker.read_text(encoding="utf-8").strip() !=
            f"ride-fedora package.ferium-portable {VERSION} {manifest['archiveSha256']} {manifest['binarySha256']}"):
        return "unowned"
    return "installed"


def ensure_safe_parents(home: Path) -> None:
    for part in (
        home / ".local", home / ".local/opt", home / ".local/opt/ride-fedora",
        home / ".local/opt/ride-fedora/ferium", home / ".local/bin",
        home / ".local/share", home / ".local/share/ride-fedora",
        home / ".local/share/ride-fedora/owned-tools",
    ):
        if part.is_symlink() or (part.exists() and not part.is_dir()):
            raise FeriumError(f"unsafe user-local path component: {part}")


def download_asset(path: Path) -> None:
    request = urllib.request.Request(ASSET_URL, headers={"User-Agent": "RIDE-Fedora/3.0"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response, path.open("wb") as output:
            if response.geturl().split(":", 1)[0] != "https":
                raise FeriumError("release download did not remain on HTTPS")
            total = 0
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > MAX_ARCHIVE_BYTES:
                    raise FeriumError("Ferium release archive exceeds the size limit")
                output.write(chunk)
    except FeriumError:
        raise
    except Exception as exc:
        raise FeriumError(f"cannot download the fixed Ferium release: {exc}") from exc


def extract_binary(archive_path: Path, destination: Path) -> None:
    try:
        with zipfile.ZipFile(archive_path) as archive:
            selected = []
            for info in archive.infolist():
                path = PurePosixPath(info.filename)
                mode = info.external_attr >> 16
                file_type = stat.S_IFMT(mode)
                if (path.is_absolute() or ".." in path.parts or
                        stat.S_ISLNK(mode) or
                        (info.is_dir() and file_type not in (0, stat.S_IFDIR)) or
                        (not info.is_dir() and file_type not in (0, stat.S_IFREG))):
                    raise FeriumError("release archive contains an unsafe entry")
                if not info.is_dir() and path.name == "ferium":
                    if info.file_size <= 0 or info.file_size > MAX_BINARY_BYTES:
                        raise FeriumError("Ferium binary has an invalid size")
                    selected.append(info)
            if len(selected) != 1:
                raise FeriumError("release archive must contain exactly one Ferium executable")
            with archive.open(selected[0]) as source, destination.open("xb") as output:
                shutil.copyfileobj(source, output)
    except FeriumError:
        raise
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise FeriumError(f"cannot safely extract Ferium release: {exc}") from exc
    destination.chmod(0o755)


def atomic_json(path: Path, value: dict) -> None:
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(0o600)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def install(home: Path) -> None:
    root, link, manifest_path = paths(home)
    current = observe(home)
    if current == "installed":
        return
    if current != "absent":
        raise FeriumError("an unowned or modified Ferium path exists; preserving it")
    ensure_safe_parents(home)
    root.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    link.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
    manifest_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.TemporaryDirectory(prefix="ride-ferium-", dir=root.parent) as temporary_name:
        temporary = Path(temporary_name)
        archive = temporary / "release.zip"
        binary = temporary / "ferium"
        download_asset(archive)
        archive_sha = digest(archive)
        extract_binary(archive, binary)
        try:
            result = subprocess.run([str(binary), "--version"], check=False, text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=20)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise FeriumError(f"cannot run Ferium version probe: {exc}") from exc
        if result.returncode != 0 or VERSION not in result.stdout:
            raise FeriumError("downloaded binary did not report the declared Ferium version")
        binary_sha = digest(binary)
        marker_text = f"ride-fedora package.ferium-portable {VERSION} {archive_sha} {binary_sha}\n"
        (temporary / ".ride-owned").write_text(marker_text, encoding="utf-8")
        (temporary / ".ride-owned").chmod(0o600)
        (temporary / "release.zip").unlink()
        if root.exists() or root.is_symlink() or link.exists() or link.is_symlink() or manifest_path.exists() or manifest_path.is_symlink():
            raise FeriumError("Ferium destination changed during installation")
        os.replace(temporary, root)
    try:
        link.symlink_to(root / "ferium")
        atomic_json(manifest_path, {
            "schemaVersion": 1, "id": "package.ferium-portable", "version": VERSION,
            "assetUrl": ASSET_URL, "archiveSha256": archive_sha,
            "binarySha256": binary_sha, "destination": str(link),
        })
    except Exception:
        if link.is_symlink() and os.readlink(link) == str(root / "ferium"):
            link.unlink()
        shutil.rmtree(root, ignore_errors=True)
        manifest_path.unlink(missing_ok=True)
        raise


def remove(home: Path) -> None:
    root, link, manifest_path = paths(home)
    current = observe(home)
    if current == "absent":
        return
    if current != "installed":
        raise FeriumError("Ferium deployment is modified or not RIDE-owned; preserving it")
    link.unlink()
    manifest_path.unlink()
    shutil.rmtree(root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("observe", "install", "remove"))
    args = parser.parse_args()
    home = Path(os.environ.get("HOME", ""))
    if not home.is_absolute() or not home.is_dir() or home.is_symlink():
        print(ERROR + "HOME must be an existing, real absolute directory", file=sys.stderr)
        return 1
    try:
        if args.action == "install":
            install(home)
        elif args.action == "remove":
            remove(home)
        state = observe(home)
        print(state)
        return 0 if state != "unowned" else 2
    except (FeriumError, OSError) as exc:
        print(ERROR + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
