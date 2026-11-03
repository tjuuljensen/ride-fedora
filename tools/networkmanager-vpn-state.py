#!/usr/bin/env python3
"""Manage exact recovery snapshots for selected NetworkManager VPN keyfiles.

Purpose: Preserve exact VPN profile keyfiles during a user-selected removal.
Behavior: Verify UUIDs, snapshot private keyfiles, detect races, restore metadata,
          and remove private snapshots only after verified recovery.
Compatibility: Python 3.11 or newer on Fedora; no third-party modules.
Usage: networkmanager-vpn-state.py {snapshot,verify,check-live,restore,discard}.
Inputs: Private NetworkManager keyfiles, selected UUIDs, and a private state path.
Side effects: Writes/removes mode-0600 recovery copies; restore recreates keyfiles.
Prerequisites: Root for system keyfiles and RIDE's system-owned state directory.
Owner: RIDE Fedora. Provenance: Fedora NetworkManager keyfile recovery.
Version: 0.1.0.
"""

from __future__ import annotations

import argparse
import base64
import configparser
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
from pathlib import Path

UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
MANIFEST = "manifest.json"


class StateError(Exception):
    pass


def fail(message: str) -> None:
    raise StateError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_uuid(value: str) -> str:
    if not UUID_RE.fullmatch(value):
        fail(f"invalid NetworkManager UUID: {value!r}")
    return value.lower()


def safe_directory(path: Path, *, create: bool = False, private: bool = True) -> None:
    if create:
        missing = []
        current = path
        while not current.exists() and current != current.parent:
            missing.append(current)
            current = current.parent
        for directory in reversed(missing):
            directory.mkdir(mode=0o700)
    st = path.lstat()
    if not stat.S_ISDIR(st.st_mode) or stat.S_ISLNK(st.st_mode):
        fail(f"unsafe state directory: {path}")
    if st.st_uid != os.geteuid() or (private and stat.S_IMODE(st.st_mode) & 0o077):
        fail(f"directory has unsafe owner or permissions: {path}")


def keyfile_uuid_and_type(path: Path) -> tuple[str, str]:
    try:
        st = path.lstat()
    except FileNotFoundError:
        fail(f"NetworkManager keyfile is missing: {path}")
    if not stat.S_ISREG(st.st_mode) or stat.S_ISLNK(st.st_mode):
        fail(f"unsupported NetworkManager keyfile type: {path}")
    if st.st_uid != os.geteuid() or stat.S_IMODE(st.st_mode) & 0o077:
        fail(f"NetworkManager keyfile must be caller-owned and private: {path}")
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    try:
        with path.open("r", encoding="utf-8") as stream:
            parser.read_file(stream)
        uuid = check_uuid(parser.get("connection", "uuid"))
        kind = parser.get("connection", "type")
    except (OSError, UnicodeError, configparser.Error, ValueError) as exc:
        fail(f"cannot validate NetworkManager keyfile {path}: {exc}")
    return uuid, kind


def xattrs(path: Path) -> list[dict[str, str]]:
    result = []
    try:
        names = os.listxattr(path, follow_symlinks=False)
    except OSError as exc:
        fail(f"cannot read extended attributes from {path}: {exc}")
    for name in sorted(names):
        try:
            value = os.getxattr(path, name, follow_symlinks=False)
        except OSError as exc:
            fail(f"cannot read extended attribute {name} from {path}: {exc}")
        result.append({"name": name, "value": base64.b64encode(value).decode("ascii")})
    return result


def atomic_write(path: Path, data: bytes, mode: int) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=".ride-vpn-", dir=path.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp, mode)
        os.replace(temp, path)
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def read_manifest(state_dir: Path) -> dict:
    safe_directory(state_dir)
    path = state_dir / MANIFEST
    st = path.lstat()
    if not stat.S_ISREG(st.st_mode) or stat.S_ISLNK(st.st_mode):
        fail("VPN profile recovery manifest is not a regular file")
    if st.st_uid != os.geteuid() or stat.S_IMODE(st.st_mode) != 0o600:
        fail("VPN profile recovery manifest must be caller-owned and mode 0600")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail(f"cannot read VPN profile recovery manifest: {exc}")
    if data.get("schemaVersion") != 1 or not isinstance(data.get("entries"), list):
        fail("invalid VPN profile recovery manifest")
    seen: set[str] = set()
    for entry in data["entries"]:
        uuid = check_uuid(entry.get("uuid", ""))
        if uuid in seen:
            fail("duplicate UUID in VPN profile recovery manifest")
        seen.add(uuid)
        if entry.get("snapshot") != f"{uuid}.nmconnection":
            fail("invalid snapshot filename in VPN profile recovery manifest")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+\.nmconnection", entry.get("filename", "")):
            fail("invalid original filename in VPN profile recovery manifest")
        if not re.fullmatch(r"[0-9a-f]{64}", entry.get("sha256", "")):
            fail("invalid keyfile digest in VPN profile recovery manifest")
        if not isinstance(entry.get("xattrs"), list):
            fail("invalid extended attributes in VPN profile recovery manifest")
    return data


def snapshot(args: argparse.Namespace) -> None:
    uuids = [check_uuid(value) for value in args.uuid]
    if not uuids or len(set(uuids)) != len(uuids):
        fail("select one or more unique VPN UUIDs")
    if not args.connection_dir.is_dir() or args.connection_dir.is_symlink():
        fail(f"unsupported NetworkManager keyfile directory: {args.connection_dir}")
    safe_directory(args.state_dir, create=True)
    if any(args.state_dir.iterdir()):
        fail("VPN profile recovery state already exists for this selection")

    by_uuid: dict[str, Path] = {}
    for path in args.connection_dir.iterdir():
        if path.suffix != ".nmconnection":
            continue
        if path.is_symlink() or not path.is_file():
            fail(f"unsupported entry in NetworkManager keyfile directory: {path}")
        uuid, kind = keyfile_uuid_and_type(path)
        if uuid in by_uuid:
            fail(f"duplicate NetworkManager keyfile for UUID {uuid}")
        if kind == "vpn":
            by_uuid[uuid] = path

    missing = [uuid for uuid in uuids if uuid not in by_uuid]
    if missing:
        fail("selected VPN UUID has no supported keyfile: " + ", ".join(missing))

    entries = []
    copied: list[Path] = []
    try:
        for uuid in sorted(uuids):
            source = by_uuid[uuid]
            source_stat = source.stat(follow_symlinks=False)
            content = source.read_bytes()
            if keyfile_uuid_and_type(source) != (uuid, "vpn"):
                fail(f"selected keyfile changed during snapshot: {source}")
            snapshot_name = f"{uuid}.nmconnection"
            snapshot_path = args.state_dir / snapshot_name
            atomic_write(snapshot_path, content, 0o600)
            copied.append(snapshot_path)
            entries.append({
                "uuid": uuid,
                "filename": source.name,
                "snapshot": snapshot_name,
                "sha256": digest(content),
                "mode": stat.S_IMODE(source_stat.st_mode),
                "uid": source_stat.st_uid,
                "gid": source_stat.st_gid,
                "mtime_ns": source_stat.st_mtime_ns,
                "xattrs": xattrs(source),
            })
        manifest = json.dumps({"schemaVersion": 1, "entries": entries}, sort_keys=True).encode()
        atomic_write(args.state_dir / MANIFEST, manifest, 0o600)
    except Exception:
        for path in copied:
            path.unlink(missing_ok=True)
        raise


def verify(args: argparse.Namespace) -> dict:
    data = read_manifest(args.state_dir)
    requested = sorted(check_uuid(value) for value in args.uuid)
    recorded = sorted(entry["uuid"] for entry in data["entries"])
    if requested != recorded:
        fail("requested VPN UUIDs do not match the saved selection")
    for entry in data["entries"]:
        path = args.state_dir / entry["snapshot"]
        st = path.lstat()
        if not stat.S_ISREG(st.st_mode) or stat.S_ISLNK(st.st_mode):
            fail(f"unsafe VPN profile snapshot: {path}")
        if st.st_uid != os.geteuid() or stat.S_IMODE(st.st_mode) != 0o600:
            fail(f"VPN profile snapshot must be caller-owned and mode 0600: {path}")
        if digest(path.read_bytes()) != entry["sha256"]:
            fail(f"VPN profile snapshot changed: {path}")
    return data


def check_live(args: argparse.Namespace) -> None:
    data = read_manifest(args.state_dir)
    entries = {entry["uuid"]: entry for entry in data["entries"]}
    for entry in data["entries"]:
        path = args.state_dir / entry["snapshot"]
        st = path.lstat()
        if not stat.S_ISREG(st.st_mode) or stat.S_ISLNK(st.st_mode):
            fail(f"unsafe VPN profile snapshot: {path}")
        if st.st_uid != os.geteuid() or stat.S_IMODE(st.st_mode) != 0o600:
            fail(f"VPN profile snapshot must be caller-owned and mode 0600: {path}")
        if digest(path.read_bytes()) != entry["sha256"]:
            fail(f"VPN profile snapshot changed: {path}")
    requested = sorted(check_uuid(value) for value in args.uuid) if args.uuid else sorted(entries)
    if not requested or any(uuid not in entries for uuid in requested):
        fail("live-check UUIDs do not match the saved selection")
    safe_directory(args.connection_dir, private=False)
    by_uuid: dict[str, Path] = {}
    for path in args.connection_dir.iterdir():
        if path.suffix != ".nmconnection":
            continue
        if path.is_symlink() or not path.is_file():
            fail(f"unsupported entry in NetworkManager keyfile directory: {path}")
        uuid, kind = keyfile_uuid_and_type(path)
        if uuid in by_uuid:
            fail(f"duplicate NetworkManager keyfile for UUID {uuid}")
        if kind == "vpn":
            by_uuid[uuid] = path
    for uuid in requested:
        entry = entries[uuid]
        source = by_uuid.get(entry["uuid"])
        if source is None or source.name != entry["filename"]:
            fail(f"selected NetworkManager profile changed since snapshot: {entry['uuid']}")
        st = source.stat(follow_symlinks=False)
        if (digest(source.read_bytes()) != entry["sha256"] or
                st.st_uid != entry["uid"] or st.st_gid != entry["gid"] or
                stat.S_IMODE(st.st_mode) != entry["mode"] or
                st.st_mtime_ns != entry["mtime_ns"] or xattrs(source) != entry["xattrs"]):
            fail(f"selected NetworkManager profile changed since snapshot: {entry['uuid']}")


def restore(args: argparse.Namespace) -> None:
    data = verify(args)
    safe_directory(args.connection_dir, private=False)
    restored: list[Path] = []
    try:
        for entry in data["entries"]:
            destination = args.connection_dir / entry["filename"]
            snapshot_path = args.state_dir / entry["snapshot"]
            matches = []
            for path in args.connection_dir.iterdir():
                if path.suffix == ".nmconnection" and path.is_file() and not path.is_symlink():
                    uuid, kind = keyfile_uuid_and_type(path)
                    if uuid == entry["uuid"] and kind == "vpn":
                        matches.append(path)
            if len(matches) > 1:
                fail(f"multiple NetworkManager keyfiles use UUID {entry['uuid']}")
            if matches:
                if matches[0] == destination and digest(destination.read_bytes()) == entry["sha256"]:
                    continue
                fail(f"refusing NetworkManager keyfile collision at {matches[0]}")
            if destination.exists() or destination.is_symlink():
                fail(f"refusing NetworkManager keyfile collision at {destination}")
            content = snapshot_path.read_bytes()
            if digest(content) != entry["sha256"]:
                fail(f"VPN profile snapshot changed: {snapshot_path}")
            atomic_write(destination, content, entry["mode"])
            restored.append(destination)
            os.chown(destination, entry["uid"], entry["gid"], follow_symlinks=False)
            os.chmod(destination, entry["mode"], follow_symlinks=False)
            for item in entry["xattrs"]:
                os.setxattr(destination, item["name"], base64.b64decode(item["value"], validate=True), follow_symlinks=False)
            os.utime(destination, ns=(entry["mtime_ns"], entry["mtime_ns"]), follow_symlinks=False)
    except Exception:
        for path in restored:
            path.unlink(missing_ok=True)
        raise


def discard(args: argparse.Namespace) -> None:
    verify(args)
    shutil.rmtree(args.state_dir)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("snapshot", "verify", "check-live", "restore", "discard"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--connection-dir", type=Path, required=True)
        cmd.add_argument("--state-dir", type=Path, required=True)
        cmd.add_argument("--uuid", action="append", default=[])
        cmd.set_defaults(func={"snapshot": snapshot, "verify": verify, "check-live": check_live,
                               "restore": restore, "discard": discard}[name])
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = args.func(args)
        if args.command == "verify":
            print(json.dumps({"uuids": sorted(entry["uuid"] for entry in result["entries"])}))
        return 0
    except (StateError, OSError, ValueError, configparser.Error) as exc:
        print(f"networkmanager-vpn-state: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
