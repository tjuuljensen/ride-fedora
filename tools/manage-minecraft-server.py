#!/usr/bin/env python3
"""Manage RIDE's pinned Minecraft Java server artifact.

Purpose: install or remove the official versioned server JAR for the current user.
Behavior: verify Mojang's content-addressed SHA-1 URL, Java 25+, and owned files.
Compatibility: Python 3.11+ on Fedora 44 x86_64.
Usage: manage-minecraft-server.py {observe|install|remove}
Inputs: no untrusted catalog or shell input; release metadata is pinned below.
Side effects: writes only ~/.local/opt/ride-fedora/minecraft-server/26.3.
Prerequisites: Python standard library; Java 25 is required for install.
Ownership: the user owns this helper; RIDE owns only the versioned JAR directory.
Provenance: official Mojang Java Edition 26.3 server JAR; see docs/migrations/generic-server-20.md.
Version: 0.1.0
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import pwd
import shutil
import stat
import sys
import tempfile
from urllib.request import Request, urlopen
import zipfile


OPERATION_ID = "package.minecraft-server"
VERSION = "26.3"
SOURCE_URI = "https://piston-data.mojang.com/v1/objects/33680f5f2ac32864d6d7cf5e56a705fdb3e05f4c/server.jar"
SOURCE_SHA1 = "33680f5f2ac32864d6d7cf5e56a705fdb3e05f4c"
MAX_BYTES = 100 * 1024 * 1024


def install_root(home: Path | None = None) -> Path:
    return (home or current_home()) / ".local/opt/ride-fedora/minecraft-server" / VERSION


def current_home() -> Path:
    sudo_user = os.environ.get("SUDO_USER", "")
    if os.geteuid() == 0 and sudo_user and sudo_user != "root":
        try:
            return Path(pwd.getpwnam(sudo_user).pw_dir)
        except KeyError as exc:
            raise RuntimeError("cannot resolve the invoking user's home for the Minecraft artifact") from exc
    return Path.home()


def regular_file(path: Path) -> bool:
    return path.is_file() and not path.is_symlink() and stat.S_ISREG(path.lstat().st_mode)


def observe(root: Path) -> str:
    if not root.exists() and not root.is_symlink():
        return "absent"
    if root.is_symlink() or not root.is_dir():
        raise RuntimeError(f"refusing unowned Minecraft server path: {root}")
    if set(p.name for p in root.iterdir()) != {"server.jar", ".ride-owned"}:
        raise RuntimeError(f"Minecraft server directory contains unowned files: {root}")
    jar = root / "server.jar"
    manifest_path = root / ".ride-owned"
    if not regular_file(jar) or not regular_file(manifest_path):
        raise RuntimeError(f"Minecraft server files are not regular owned files: {root}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("invalid Minecraft server ownership manifest") from exc
    if manifest != {
        "id": OPERATION_ID,
        "version": VERSION,
        "sourceUri": SOURCE_URI,
        "sourceSha1": SOURCE_SHA1,
        "sha256": sha256_file(jar),
    }:
        raise RuntimeError("Minecraft server ownership record or JAR digest does not match")
    if sha1_file(jar) != SOURCE_SHA1:
        raise RuntimeError("Minecraft server JAR no longer matches Mojang's pinned object")
    return "installed"


def sha256_file(path: Path) -> str:
    return digest_file(path, "sha256")


def sha1_file(path: Path) -> str:
    return digest_file(path, "sha1")


def digest_file(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_java_25() -> None:
    import subprocess

    result = subprocess.run(["java", "-version"], text=True, capture_output=True,
                            timeout=15, check=False)
    output = result.stderr + result.stdout
    if result.returncode != 0 or not any(
        token in output for token in ('version "25', 'openjdk 25', 'openjdk version "25')
    ):
        raise RuntimeError("Minecraft 26.3 requires Java 25; install Fedora's java-25-openjdk-headless first")


def ensure_real_directories(path: Path) -> None:
    home = current_home().resolve()
    path = path.resolve(strict=False)
    if not path.is_relative_to(home):
        raise RuntimeError("Minecraft server destination must remain within the current HOME")
    current = home
    for part in path.relative_to(home).parts:
        current = current / part
        if current.exists() or current.is_symlink():
            if current.is_symlink() or not current.is_dir():
                raise RuntimeError(f"refusing non-directory or symlink path component: {current}")
        else:
            current.mkdir(mode=0o700)


def install(root: Path) -> None:
    require_java_25()
    if observe(root) == "installed":
        return
    ensure_real_directories(root.parent)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".minecraft-server-", dir=root.parent,
                                         delete=False) as stream:
            temporary = Path(stream.name)
            request = Request(SOURCE_URI, headers={"User-Agent": "RIDE/3 Mojang server setup"})
            with urlopen(request, timeout=60) as response:
                if response.geturl() != SOURCE_URI:
                    raise RuntimeError("Mojang server URL redirected unexpectedly")
                total = 0
                digest_sha1 = hashlib.sha1()
                digest_sha256 = hashlib.sha256()
                while block := response.read(1024 * 1024):
                    total += len(block)
                    if total > MAX_BYTES:
                        raise RuntimeError("Minecraft server JAR exceeds the 100 MiB size limit")
                    stream.write(block)
                    digest_sha1.update(block)
                    digest_sha256.update(block)
            stream.flush()
            os.fsync(stream.fileno())
        if digest_sha1.hexdigest() != SOURCE_SHA1:
            raise RuntimeError("Minecraft server JAR SHA-1 does not match Mojang's pinned object URL")
        if not zipfile.is_zipfile(temporary):
            raise RuntimeError("Mojang server artifact is not a valid JAR/ZIP archive")
        root.mkdir(mode=0o700)
        os.replace(temporary, root / "server.jar")
        temporary = None
        manifest = {
            "id": OPERATION_ID,
            "version": VERSION,
            "sourceUri": SOURCE_URI,
            "sourceSha1": SOURCE_SHA1,
            "sha256": digest_sha256.hexdigest(),
        }
        manifest_path = root / ".ride-owned"
        manifest_path.write_text(json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8")
        manifest_path.chmod(0o600)
        if observe(root) != "installed":
            raise RuntimeError("Minecraft server installation did not verify")
    except BaseException:
        if root.exists() and not root.is_symlink():
            shutil.rmtree(root)
        raise
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def remove(root: Path) -> None:
    if observe(root) == "absent":
        return
    shutil.rmtree(root)


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in {"observe", "install", "remove"}:
        print("usage: manage-minecraft-server.py {observe|install|remove}", file=sys.stderr)
        return 2
    try:
        root = install_root()
        if argv[1] == "install":
            install(root)
        elif argv[1] == "remove":
            remove(root)
        print(observe(root))
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"manage-minecraft-server: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
