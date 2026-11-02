#!/usr/bin/env python3
"""Install or remove the pinned Debian-built Galleta CLI for the current user.

Purpose: Preserve the legacy Internet Explorer cookie parser capability.
Behavior: Verify a pinned Debian package, extract only its Galleta binary and
          license text, and remove only unchanged RIDE-owned files.
Compatibility: Python 3.11+ on Linux x86_64.
Usage: python3 tools/manage-galleta.py observe|install|remove
Inputs: Fixed Debian package URL and SHA-256 below.
Side effects: Owns ~/.local/bin/galleta and a private ownership manifest.
Prerequisites: Python standard library and network access for install.
Ownership: User-local install; RIDE owns only its unchanged binary and manifest.
Provenance: Debian galleta 1.0+20040505-12, upstream BSD-3-Clause source.
Version: 3.0.0.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import pwd
import stat
import struct
import sys
import tarfile
import tempfile
from urllib.request import Request, urlopen


OPERATION_ID = "package.galleta"
VERSION = "1.0+20040505-12"
SOURCE_URI = "https://deb.debian.org/debian/pool/main/g/galleta/galleta_1.0+20040505-12_amd64.deb"
SOURCE_SHA256 = "1bb1867237e07c403c9f79abad71b6838645f4494a5ea1a4077821f610b401ff"
MAX_PACKAGE_BYTES = 100_000
ERROR = "RIDE Galleta: "


class GalletaError(Exception):
    """A safe lifecycle error."""


def invoking_home() -> Path:
    sudo_user = os.environ.get("SUDO_USER", "")
    if os.geteuid() == 0 and sudo_user and sudo_user != "root":
        try:
            return Path(pwd.getpwnam(sudo_user).pw_dir)
        except KeyError as exc:
            raise GalletaError("cannot resolve the invoking user's home") from exc
    return Path.home()


def paths(home: Path) -> tuple[Path, Path]:
    return (home / ".local/bin/galleta",
            home / ".local/share/ride-fedora/owned-tools/package.galleta.json")


def regular_file(path: Path) -> bool:
    return path.is_file() and not path.is_symlink() and stat.S_ISREG(path.lstat().st_mode)


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def load_manifest(path: Path) -> dict | None:
    if not path.exists() and not path.is_symlink():
        return None
    if not regular_file(path):
        raise GalletaError("ownership manifest is not a regular file")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GalletaError("cannot read the ownership manifest") from exc
    expected = {"id", "version", "sourceUri", "sourceSha256", "binarySha256", "licenseSha256", "destination"}
    if (not isinstance(value, dict) or set(value) != expected or
            value.get("id") != OPERATION_ID or value.get("version") != VERSION or
            value.get("sourceUri") != SOURCE_URI or value.get("sourceSha256") != SOURCE_SHA256 or
            value.get("destination") != str(path.parents[4] / ".local/bin/galleta") or
            not all(isinstance(value.get(name), str) for name in ("binarySha256", "licenseSha256"))):
        raise GalletaError("ownership manifest does not match the pinned operation")
    return value


def observe(home: Path) -> str:
    binary, manifest_path = paths(home)
    license_path = manifest_path.with_name("package.galleta-copyright")
    manifest = load_manifest(manifest_path)
    if (manifest is None and not binary.exists() and not binary.is_symlink() and
            not license_path.exists() and not license_path.is_symlink()):
        return "absent"
    if manifest is None or binary.is_symlink() or not regular_file(binary):
        raise GalletaError("Galleta path is unowned or changed; refusing to overwrite it")
    license_path = manifest_path.with_name("package.galleta-copyright")
    if (manifest_path.stat().st_uid != os.getuid() or
            stat.S_IMODE(manifest_path.stat().st_mode) != 0o600 or
            binary.stat().st_uid != os.getuid() or
            stat.S_IMODE(binary.stat().st_mode) != 0o755 or
            digest_file(binary) != manifest["binarySha256"] or
            not regular_file(license_path) or
            digest_file(license_path) != manifest["licenseSha256"]):
        raise GalletaError("owned Galleta files changed; refusing to manage them")
    return "installed"


def safe_parents(home: Path) -> None:
    for path in (home / ".local", home / ".local/bin", home / ".local/share",
                 home / ".local/share/ride-fedora",
                 home / ".local/share/ride-fedora/owned-tools"):
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            raise GalletaError(f"unsafe user-local path component: {path}")


def fetch_package() -> bytes:
    request = Request(SOURCE_URI, headers={"User-Agent": "RIDE-Fedora/3.0"})
    try:
        with urlopen(request, timeout=30) as response:
            if not response.geturl().startswith("https://"):
                raise GalletaError("Debian package download redirected away from HTTPS")
            package = response.read(MAX_PACKAGE_BYTES + 1)
    except Exception as exc:
        raise GalletaError(f"could not download the pinned Debian package: {exc}") from exc
    if len(package) > MAX_PACKAGE_BYTES or digest_bytes(package) != SOURCE_SHA256:
        raise GalletaError("Debian package size or SHA-256 does not match the pinned artifact")
    return package


def data_members(package: bytes) -> tuple[bytes, bytes]:
    if not package.startswith(b"!<arch>\n"):
        raise GalletaError("download is not a Debian ar package")
    offset = 8
    data_archive = None
    while offset < len(package):
        header = package[offset:offset + 60]
        if len(header) != 60 or header[58:60] != b"`\n":
            raise GalletaError("Debian package has an invalid ar member")
        name = header[:16].decode("ascii", errors="strict").strip().rstrip("/")
        try:
            size = int(header[48:58].decode("ascii").strip())
        except ValueError as exc:
            raise GalletaError("Debian package has an invalid member size") from exc
        start = offset + 60
        end = start + size
        if end > len(package):
            raise GalletaError("Debian package member exceeds the downloaded file")
        if name.startswith("data.tar"):
            if data_archive is not None:
                raise GalletaError("Debian package contains multiple data archives")
            data_archive = package[start:end]
        offset = end + (size % 2)
    if data_archive is None:
        raise GalletaError("Debian package has no data archive")
    try:
        with tarfile.open(fileobj=io.BytesIO(data_archive), mode="r:xz") as archive:
            binary_member = next((item for item in archive.getmembers()
                                  if item.name.lstrip("./") == "usr/bin/galleta"), None)
            license_member = next((item for item in archive.getmembers()
                                   if item.name.lstrip("./") == "usr/share/doc/galleta/copyright"), None)
            if (binary_member is None or not binary_member.isfile() or
                    license_member is None or not license_member.isfile()):
                raise GalletaError("Debian package is missing its expected binary or license file")
            binary_stream = archive.extractfile(binary_member)
            license_stream = archive.extractfile(license_member)
            if binary_stream is None or license_stream is None:
                raise GalletaError("could not read Galleta package members")
            binary, license_text = binary_stream.read(20_000_001), license_stream.read(500_001)
    except (tarfile.TarError, OSError) as exc:
        raise GalletaError("Debian data archive is invalid") from exc
    if len(binary) > 20_000_000 or len(license_text) > 500_000 or not binary.startswith(b"\x7fELF"):
        raise GalletaError("Galleta binary or license member is invalid")
    if len(binary) < 20 or struct.unpack_from("<H", binary, 18)[0] != 62:
        raise GalletaError("Galleta binary is not an x86_64 ELF executable")
    if b"BSD" not in license_text or b"Copyright" not in license_text:
        raise GalletaError("Galleta license text is missing or unexpected")
    return binary, license_text


def install(home: Path) -> None:
    if observe(home) == "installed":
        return
    binary_path, manifest_path = paths(home)
    safe_parents(home)
    package = fetch_package()
    binary, license_text = data_members(package)
    binary_path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    manifest_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    license_path = manifest_path.with_name("package.galleta-copyright")
    if (binary_path.exists() or binary_path.is_symlink() or manifest_path.exists() or
            manifest_path.is_symlink() or license_path.exists() or license_path.is_symlink()):
        raise GalletaError("an unowned Galleta binary or manifest already exists")
    manifest = {
        "id": OPERATION_ID,
        "version": VERSION,
        "sourceUri": SOURCE_URI,
        "sourceSha256": SOURCE_SHA256,
        "binarySha256": digest_bytes(binary),
        "licenseSha256": digest_bytes(license_text),
        "destination": str(binary_path),
    }
    marker = manifest_path.with_name(manifest_path.name + ".tmp")
    binary_tmp = None
    try:
        with tempfile.NamedTemporaryFile(dir=binary_path.parent, prefix=".galleta-", delete=False) as stream:
            binary_tmp = Path(stream.name)
            stream.write(binary)
        os.chmod(binary_tmp, 0o755)
        os.replace(binary_tmp, binary_path)
        marker.write_text(json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8")
        os.chmod(marker, 0o600)
        os.replace(marker, manifest_path)
        with tempfile.NamedTemporaryFile(dir=license_path.parent, prefix=".galleta-copyright-", delete=False) as stream:
            license_tmp = Path(stream.name)
            stream.write(license_text)
        os.chmod(license_tmp, 0o600)
        os.replace(license_tmp, license_path)
    except OSError as exc:
        if binary_tmp is not None:
            binary_tmp.unlink(missing_ok=True)
        if binary_path.exists() and digest_file(binary_path) == digest_bytes(binary):
            binary_path.unlink()
        marker.unlink(missing_ok=True)
        manifest_path.unlink(missing_ok=True)
        for leftover in license_path.parent.glob(".galleta-copyright-*"):
            if leftover.is_file() and not leftover.is_symlink():
                leftover.unlink(missing_ok=True)
        if license_path.exists() and license_path.is_file() and not license_path.is_symlink() and digest_file(license_path) == digest_bytes(license_text):
            license_path.unlink()
        raise GalletaError(f"could not install Galleta safely: {exc}") from exc


def remove(home: Path) -> None:
    if observe(home) == "absent":
        return
    binary_path, manifest_path = paths(home)
    license_path = manifest_path.with_name("package.galleta-copyright")
    manifest = load_manifest(manifest_path)
    assert manifest is not None
    if (license_path.is_symlink() or not regular_file(license_path) or
            digest_file(license_path) != manifest["licenseSha256"]):
        raise GalletaError("owned Galleta copyright file is changed or not regular")
    binary_path.unlink()
    manifest_path.unlink()
    license_path.unlink(missing_ok=True)


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"observe", "install", "remove"}:
        print(f"usage: {Path(sys.argv[0]).name} observe|install|remove", file=sys.stderr)
        return 2
    try:
        home = invoking_home()
        action = sys.argv[1]
        if action == "observe":
            print(observe(home))
        elif action == "install":
            install(home)
            print("installed")
        else:
            remove(home)
            print("absent")
        return 0
    except (GalletaError, OSError) as exc:
        print(f"{ERROR}{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
