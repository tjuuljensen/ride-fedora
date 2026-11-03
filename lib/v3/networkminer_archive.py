#!/usr/bin/env python3
"""Validate and manage the pinned NetworkMiner ZIP payload."""

import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path, PurePosixPath

MAX_MEMBER = 256 * 1024 * 1024
MAX_TOTAL = 2 * 1024 * 1024 * 1024
ROOT = "NetworkMiner_3-2"
REQUIRED = {
    f"{ROOT}/NetworkMiner.exe",
    f"{ROOT}/PacketParser.dll",
    f"{ROOT}/Fingerprints/mac-ages_LICENSE",
}


def members(bundle: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    result = []
    seen = set()
    total = 0
    for item in bundle.infolist():
        name = item.filename
        path = PurePosixPath(name)
        mode = item.external_attr >> 16
        file_type = mode & 0o170000
        if (path.is_absolute() or not name or "\\" in name or
                any(part in {"", ".", ".."} for part in name.rstrip("/").split("/")) or
                not path.parts or path.parts[0] != ROOT or name in seen or
                item.flag_bits & 1 or item.file_size > MAX_MEMBER or
                file_type not in (0, 0o040000 if item.is_dir() else 0o100000)):
            raise ValueError(f"unsafe or duplicate archive entry: {name}")
        seen.add(name)
        total += item.file_size
        if total > MAX_TOTAL:
            raise ValueError("archive expands beyond the allowed size")
        result.append(item)
    if not REQUIRED <= seen:
        raise ValueError("archive lacks NetworkMiner executable, parser, or license notice")
    return result


def extract(archive: Path, destination: Path) -> None:
    with zipfile.ZipFile(archive) as bundle:
        entries = members(bundle)
        destination.mkdir(parents=True, mode=0o700)
        for item in entries:
            relative = PurePosixPath(item.filename).relative_to(ROOT)
            if not relative.parts:
                continue
            target = destination.joinpath(*relative.parts)
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True, mode=0o700)
                continue
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            with bundle.open(item) as source, target.open("xb") as output:
                shutil.copyfileobj(source, output, 1024 * 1024)
            target.chmod(0o600 if relative.name.endswith("LICENSE") else 0o644)
        for path in sorted(destination.rglob("*"), key=lambda value: len(value.parts), reverse=True):
            if path.is_dir():
                path.chmod(0o700)


def snapshot(payload: Path) -> list[dict[str, str]]:
    result = []
    for path in sorted(payload.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"payload contains a symlink: {path}")
        relative = path.relative_to(payload).as_posix()
        if path.is_dir():
            result.append({"path": relative, "type": "directory"})
        elif path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            result.append({"path": relative, "type": "file", "sha256": digest})
        else:
            raise ValueError(f"payload contains a special file: {path}")
    return result


def main() -> None:
    if len(sys.argv) != 4 or sys.argv[1] not in {"extract", "manifest", "verify"}:
        raise ValueError("usage: networkminer_archive.py extract ZIP DEST | manifest PAYLOAD FILE | verify PAYLOAD FILE")
    command, first, second = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    if command == "extract":
        extract(first, second)
    elif command == "manifest":
        if second.exists() or second.is_symlink():
            raise ValueError("manifest destination already exists")
        second.write_text(json.dumps(snapshot(first), sort_keys=True, separators=(",", ":")) + "\n")
        second.chmod(0o600)
    else:
        if not second.is_file() or second.is_symlink():
            raise ValueError("missing owned payload manifest")
        if snapshot(first) != json.loads(second.read_text()):
            raise ValueError("NetworkMiner payload differs from owned manifest")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as error:
        print(f"NetworkMiner archive error: {error}", file=sys.stderr)
        raise SystemExit(1) from None
