#!/usr/bin/env python3
"""Purpose:
  Snapshot and compare ClamAV signature data for the RIDE v3 package handler.

Behavior:
  Hash regular files, directories, ownership, modes, timestamps, and xattrs;
  copy and restore a complete tree while refusing symbolic links and special
  files. An absent source tree is represented explicitly.

Compatibility:
  Python 3.9 or later on Linux.

Usage:
  python3 tools/clamav-state.py hash DIRECTORY
  python3 tools/clamav-state.py copy SOURCE DESTINATION
  python3 tools/clamav-state.py restore SNAPSHOT DESTINATION yes|no

Inputs:
  A ClamAV data directory and a private RIDE-owned snapshot directory.

Side effects:
  Reads metadata and file bytes; copy and restore create or replace the named
  destination tree. The caller must run system-data operations as root.

Prerequisites:
  Python 3.9 or later and a local Linux filesystem supporting ordinary file
  metadata. Symbolic links and special files are rejected.

Ownership and provenance:
  RIDE Fedora project code; no external source.

Version:
  3.0.0

Changelog:
  3.0.0: Add exact-tree support for the ClamAV signature recovery handler.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys


def _tree(root: Path) -> list[dict[str, object]]:
    if root.is_symlink():
        raise ValueError(f"symbolic links are not supported: {root}")
    if not root.exists():
        return []
    if not root.is_dir():
        raise ValueError(f"data path is not a directory: {root}")
    records: list[dict[str, object]] = []
    for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
        base = Path(current)
        dirs.sort()
        files.sort()
        for name in list(dirs):
            path = base / name
            if path.is_symlink() or not path.is_dir():
                raise ValueError(f"symbolic link or special file is not supported: {path}")
        for name in [*dirs, *files]:
            path = base / name
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode) or not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
                raise ValueError(f"symbolic link or special file is not supported: {path}")
            relative = "." if path == root else path.relative_to(root).as_posix()
            attrs: list[list[str]] = []
            try:
                for attr in sorted(os.listxattr(path, follow_symlinks=False)):
                    value = os.getxattr(path, attr, follow_symlinks=False)
                    attrs.append([attr, hashlib.sha256(value).hexdigest()])
            except OSError as exc:
                raise ValueError(f"cannot read extended attributes for {path}: {exc}") from exc
            record: dict[str, object] = {
                "path": relative,
                "type": "directory" if stat.S_ISDIR(info.st_mode) else "file",
                "mode": stat.S_IMODE(info.st_mode),
                "uid": info.st_uid,
                "gid": info.st_gid,
                "mtimeNs": info.st_mtime_ns,
                "xattrs": attrs,
            }
            if stat.S_ISREG(info.st_mode):
                digest = hashlib.sha256()
                with path.open("rb") as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(block)
                record["size"] = info.st_size
                record["sha256"] = digest.hexdigest()
            records.append(record)
    info = root.lstat()
    attrs = []
    try:
        for attr in sorted(os.listxattr(root, follow_symlinks=False)):
            attrs.append([attr, hashlib.sha256(os.getxattr(root, attr, follow_symlinks=False)).hexdigest()])
    except OSError as exc:
        raise ValueError(f"cannot read extended attributes for {root}: {exc}") from exc
    records.insert(0, {"path": ".", "type": "directory", "mode": stat.S_IMODE(info.st_mode),
                       "uid": info.st_uid, "gid": info.st_gid, "mtimeNs": info.st_mtime_ns,
                       "xattrs": attrs})
    return records


def tree_hash(root: Path) -> str:
    if not root.exists() and not root.is_symlink():
        return "absent"
    encoded = json.dumps(_tree(root), sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def copy_tree(source: Path, destination: Path) -> None:
    _tree(source)
    if destination.exists() or destination.is_symlink():
        raise ValueError(f"snapshot destination already exists: {destination}")
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    shutil.copytree(source, destination, copy_function=shutil.copy2, symlinks=False)
    for current, dirs, files in os.walk(destination, topdown=False, followlinks=False):
        for name in [*dirs, *files, ""]:
            path = Path(current) / name if name else Path(current)
            source_path = source / path.relative_to(destination)
            info = source_path.stat(follow_symlinks=False)
            os.chown(path, info.st_uid, info.st_gid, follow_symlinks=False)
    if tree_hash(source) != tree_hash(destination):
        shutil.rmtree(destination)
        raise ValueError("signature snapshot did not preserve the complete file tree")


def restore_tree(snapshot: Path, destination: Path, existed: bool) -> None:
    if destination.is_symlink():
        raise ValueError(f"refusing to replace symbolic link: {destination}")
    if destination.exists():
        _tree(destination)
        shutil.rmtree(destination)
    if not existed:
        return
    if snapshot.is_symlink() or not snapshot.is_dir():
        raise ValueError("saved ClamAV snapshot is missing or unsafe")
    copy_tree(snapshot, destination)


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage exact ClamAV data snapshots.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    hash_parser = subparsers.add_parser("hash")
    hash_parser.add_argument("directory", type=Path)
    copy_parser = subparsers.add_parser("copy")
    copy_parser.add_argument("source", type=Path)
    copy_parser.add_argument("destination", type=Path)
    restore_parser = subparsers.add_parser("restore")
    restore_parser.add_argument("snapshot", type=Path)
    restore_parser.add_argument("destination", type=Path)
    restore_parser.add_argument("existed", choices=("yes", "no"))
    args = parser.parse_args()
    try:
        if args.command == "hash":
            print(tree_hash(args.directory))
        elif args.command == "copy":
            copy_tree(args.source, args.destination)
        else:
            restore_tree(args.snapshot, args.destination, args.existed == "yes")
        return 0
    except (OSError, ValueError) as exc:
        print(f"RIDE ClamAV state: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
