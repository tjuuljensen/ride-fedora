"""Validate and unpack the pinned CyberChef release; verify owned payload files.

Used only by the Bash v3 provider. The ZIP is data, never executable input.
Usage: cyberchef_archive.py extract ZIP DEST | manifest PAYLOAD FILE | verify PAYLOAD FILE
Inputs: a fixed release ZIP or an owned payload directory and manifest path.
Side effects: extract writes DEST; manifest writes FILE; verify is read-only.
Requires: Python 3 standard library. Owned by ride-fedora v3.0.0.
"""

import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import zipfile


MAX_ENTRIES = 1000
MAX_UNPACKED = 250_000_000
MAX_FILE = 100_000_000
REQUIRED = {"CyberChef_v11.5.0.html", "images/cyberchef-128x128.png",
            "assets/main.js", "assets/main.css"}
SAFE_NAME = re.compile(r"[A-Za-z0-9._/-]+\Z")


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def snapshot(root: Path) -> list[dict]:
    if not root.is_dir() or root.is_symlink():
        raise ValueError("payload is not an owned directory")
    entries = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlink in payload: {path}")
        item = {"path": path.relative_to(root).as_posix()}
        if path.is_dir():
            item["kind"] = "dir"
        elif path.is_file():
            item.update(kind="file", size=path.stat().st_size, sha256=digest(path))
        else:
            raise ValueError(f"unsupported payload entry: {path}")
        entries.append(item)
    return entries


def extract(archive: Path, destination: Path) -> None:
    if destination.exists() or destination.is_symlink():
        raise ValueError("extraction destination already exists")
    with zipfile.ZipFile(archive) as bundle:
        members = bundle.infolist()
        if len(members) > MAX_ENTRIES or sum(item.file_size for item in members) > MAX_UNPACKED:
            raise ValueError("archive expansion exceeds limit")
        names = set()
        for item in members:
            name = item.filename.rstrip("/")
            if (not name or not SAFE_NAME.fullmatch(name) or
                    any(part in {"", ".", ".."} for part in name.split("/")) or
                    name in names or item.file_size > MAX_FILE or item.flag_bits & 1):
                raise ValueError(f"unsafe or duplicate archive entry: {item.filename}")
            mode = (item.external_attr >> 16) & 0o170000
            if mode not in (0, 0o040000 if item.is_dir() else 0o100000):
                raise ValueError(f"unsupported archive entry type: {item.filename}")
            names.add(name)
        if not REQUIRED <= names or sum(name.endswith(".LICENSE.txt") for name in names) < 30:
            raise ValueError("archive lacks CyberChef entry or bundled notices")
        destination.mkdir(parents=True, mode=0o755)
        for item in members:
            target = destination / item.filename
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True, mode=0o755)
            else:
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
                with bundle.open(item) as source, target.open("xb") as output:
                    shutil.copyfileobj(source, output, 1024 * 1024)
                target.chmod(0o644)
        for path in destination.rglob("*"):
            if path.is_dir():
                path.chmod(0o755)


def main() -> None:
    if len(sys.argv) != 4 or sys.argv[1] not in {"extract", "manifest", "verify"}:
        raise ValueError("usage: cyberchef_archive.py extract ZIP DEST | manifest PAYLOAD FILE | verify PAYLOAD FILE")
    command, first, second = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    if command == "extract":
        extract(first, second)
    elif command == "manifest":
        if second.exists() or second.is_symlink():
            raise ValueError("manifest destination already exists")
        second.write_text(json.dumps(snapshot(first), sort_keys=True, separators=(",", ":")) + "\n")
        second.chmod(0o644)
    else:
        if not second.is_file() or second.is_symlink():
            raise ValueError("missing owned manifest")
        if snapshot(first) != json.loads(second.read_text()):
            raise ValueError("CyberChef payload differs from owned manifest")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(f"CyberChef archive error: {error}", file=sys.stderr)
        raise SystemExit(1) from None
