#!/usr/bin/env python3
"""Remove and exactly restore one explicitly selected keyfile mount mapping.

Behavior: edit one crypttab mapper row and its matching fstab source only.
Compatibility: Python 3.9+ on Fedora 44; production execution is root-only.
Inputs: action (observe/remove/restore) and one mapper name.
Side effects: remove/restore two system config rows and retain a private recovery record.
Prerequisites: regular root-owned /etc/crypttab, /etc/fstab, and selected keyfile.
Ownership: RIDE owns its private recovery record; selected rows require explicit operator selection.
Provenance: migration of lib-fedora.sh RemoveKeyfileMounts; no upstream code copied.
Version: RIDE client v3.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from pathlib import Path

MAPPER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.+-]{0,63}$")
KEY_PREFIX = "/root/keyfile_"


class Refusal(Exception):
    """Raised when the selected state cannot be changed safely."""


def test_mode() -> bool:
    return os.environ.get("RIDE_TEST_MODE") == "1"


def uid() -> int:
    return os.getuid() if test_mode() else 0


def env_path(name: str, default: str) -> Path:
    if test_mode() and os.environ.get(name):
        return Path(os.environ[name])
    return Path(default)


def files() -> tuple[Path, Path]:
    return env_path("RIDE_KEYFILE_MOUNTS_TEST_CRYPTTAB", "/etc/crypttab"), env_path(
        "RIDE_KEYFILE_MOUNTS_TEST_FSTAB", "/etc/fstab"
    )


def recovery_root() -> Path:
    return env_path(
        "RIDE_KEYFILE_MOUNTS_TEST_STATE_ROOT",
        "/var/lib/ride-fedora/owned-tools/setting.keyfile-mounts",
    )


def validate_mapper(mapper: str) -> str:
    if not MAPPER_RE.fullmatch(mapper):
        raise Refusal("mapper value must be one simple Linux mapper name")
    return mapper


def check_regular(path: Path, label: str, mode: int | None = None) -> os.stat_result:
    try:
        info = path.lstat()
    except OSError as exc:
        raise Refusal(f"cannot inspect {label}: {path}") from exc
    if not stat.S_ISREG(info.st_mode) or info.st_uid != uid():
        raise Refusal(f"{label} must be a regular file with the expected owner: {path}")
    actual_mode = stat.S_IMODE(info.st_mode)
    if (mode is not None and actual_mode != mode) or (mode is None and actual_mode & 0o022):
        raise Refusal(f"{label} has unsafe permissions: {path}")
    return info


def read_file(path: Path, label: str) -> tuple[bytes, os.stat_result]:
    before = check_regular(path, label)
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            if (info.st_dev, info.st_ino) != (before.st_dev, before.st_ino):
                raise Refusal(f"{label} changed during inspection: {path}")
            return stream.read(), info
    except OSError as exc:
        raise Refusal(f"cannot read {label}: {path}") from exc


def logical_keyfile(path: str) -> Path:
    if not path.startswith(KEY_PREFIX) or path == KEY_PREFIX:
        raise Refusal("selected crypttab row must use a /root/keyfile_* keyfile")
    if test_mode() and os.environ.get("RIDE_KEYFILE_MOUNTS_TEST_ROOT"):
        return Path(os.environ["RIDE_KEYFILE_MOUNTS_TEST_ROOT"]) / path.lstrip("/")
    return Path(path)


def tokens(line: bytes) -> list[str]:
    text = line.decode("utf-8").strip()
    return [] if not text or text.startswith("#") else text.split()


def mount_field(value: str) -> str:
    return re.sub(r"\\([0-7]{3})", lambda m: chr(int(m.group(1), 8)), value)


def device_mapper(mapper: str) -> Path:
    if test_mode() and os.environ.get("RIDE_KEYFILE_MOUNTS_TEST_ROOT"):
        return Path(os.environ["RIDE_KEYFILE_MOUNTS_TEST_ROOT"]) / "dev/mapper" / mapper
    return Path("/dev/mapper") / mapper


def ensure_inactive(mapper: str, mountpoint: str) -> None:
    if device_mapper(mapper).exists() or device_mapper(mapper).is_symlink():
        raise Refusal(f"refusing to change active encrypted mapping: {mapper}")
    if mountpoint == "/" or not mountpoint.startswith("/"):
        raise Refusal("refusing an unsafe encrypted mountpoint")
    mountinfo = env_path("RIDE_KEYFILE_MOUNTS_TEST_MOUNTINFO", "/proc/self/mountinfo")
    try:
        for line in mountinfo.read_text(encoding="utf-8").splitlines():
            fields = line.split()
            if len(fields) > 4 and mount_field(fields[4]) == mountpoint:
                raise Refusal(f"refusing to change mounted encrypted target: {mountpoint}")
    except OSError as exc:
        raise Refusal("cannot inspect mounted filesystems") from exc


def selected(mapper: str, crypttab: bytes, fstab: bytes) -> dict[str, object] | None:
    crows, frows = [], []
    for index, line in enumerate(crypttab.splitlines(keepends=True)):
        fields = tokens(line)
        if fields and fields[0] == mapper:
            crows.append((index, line, fields))
    expected_source = f"/dev/mapper/{mapper}"
    for index, line in enumerate(fstab.splitlines(keepends=True)):
        fields = tokens(line)
        if fields and fields[0] == expected_source:
            frows.append((index, line, fields))
    if not crows and not frows:
        return None
    if len(crows) != 1 or len(frows) != 1:
        raise Refusal(f"expected exactly one matching crypttab and fstab row: {mapper}")
    ci, cline, cf = crows[0]
    fi, fline, ff = frows[0]
    if len(cf) < 3 or len(ff) < 4:
        raise Refusal(f"selected mount records are incomplete: {mapper}")
    key_path = cf[2]
    keyfile = logical_keyfile(key_path)
    key = check_regular(keyfile, "selected LUKS keyfile", 0o400)
    point = mount_field(ff[1])
    ensure_inactive(mapper, point)
    return {
        "cryptIndex": ci,
        "cryptLine": cline,
        "fstabIndex": fi,
        "fstabLine": fline,
        "keyPath": key_path,
        "keyStat": {
            "dev": key.st_dev,
            "ino": key.st_ino,
            "size": key.st_size,
            "mtimeNs": key.st_mtime_ns,
            "uid": key.st_uid,
            "gid": key.st_gid,
            "mode": stat.S_IMODE(key.st_mode),
        },
    }


def file_meta(info: os.stat_result) -> dict[str, int]:
    return {
        "dev": info.st_dev,
        "ino": info.st_ino,
        "uid": info.st_uid,
        "gid": info.st_gid,
        "mode": stat.S_IMODE(info.st_mode),
    }


def atomic_replace(path: Path, expected: bytes, replacement: bytes, meta: dict[str, int]) -> None:
    current, info = read_file(path, str(path))
    if current != expected or info.st_ino != meta["ino"]:
        raise Refusal(f"configuration changed since inspection: {path}")
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.ride-", dir=path.parent)
    try:
        os.fchown(fd, meta["uid"], meta["gid"])
        os.fchmod(fd, meta["mode"])
        with os.fdopen(fd, "wb") as stream:
            stream.write(replacement)
            stream.flush()
            os.fsync(stream.fileno())
        latest, latest_info = read_file(path, str(path))
        if latest != expected or latest_info.st_ino != meta["ino"]:
            raise Refusal(f"configuration changed before update: {path}")
        os.replace(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def state_dir(mapper: str) -> Path:
    return recovery_root() / hashlib.sha256(mapper.encode()).hexdigest()


def inspect(mapper: str):
    cpath, fpath = files()
    crypt, cstat = read_file(cpath, "/etc/crypttab")
    fstab, fstat = read_file(fpath, "/etc/fstab")
    record = selected(mapper, crypt, fstab)
    return ("absent" if record is None else "configured"), record, (cpath, fpath), crypt, fstab, cstat, fstat


def ensure_state_parent(directory: Path) -> None:
    parent = directory.parent
    parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = parent.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != uid() or stat.S_IMODE(info.st_mode) & 0o022:
        raise Refusal(f"recovery directory is unsafe: {parent}")
    if directory.exists() or directory.is_symlink():
        raise Refusal("private recovery state already exists for this mapper")
    directory.mkdir(mode=0o700)
    os.chmod(directory, 0o700)


def discard_recovery(directory: Path) -> None:
    (directory / "recovery.json").unlink(missing_ok=True)
    directory.rmdir()


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def unb64(value: str) -> bytes:
    return base64.b64decode(value, validate=True)


def remove(mapper: str) -> str:
    current, record, paths, crypt, fstab, cstat, fstat = inspect(mapper)
    if current == "absent":
        return "absent"
    assert record is not None
    directory = state_dir(mapper)
    ensure_state_parent(directory)
    clines, flines = crypt.splitlines(keepends=True), fstab.splitlines(keepends=True)
    crypt_after = b"".join(line for i, line in enumerate(clines) if i != record["cryptIndex"])
    fstab_after = b"".join(line for i, line in enumerate(flines) if i != record["fstabIndex"])
    manifest = {
        "schemaVersion": 1,
        "mapper": mapper,
        "keyPath": record["keyPath"],
        "keyStat": record["keyStat"],
        "crypttab": {"before": b64(crypt), "after": b64(crypt_after), "meta": file_meta(cstat)},
        "fstab": {"before": b64(fstab), "after": b64(fstab_after), "meta": file_meta(fstat)},
    }
    recovery_file = directory / "recovery.json"
    fd = os.open(recovery_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(manifest, stream, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.chmod(recovery_file, 0o600)
    try:
        atomic_replace(paths[0], crypt, crypt_after, file_meta(cstat))
    except Exception:
        discard_recovery(directory)
        raise
    try:
        atomic_replace(paths[1], fstab, fstab_after, file_meta(fstat))
    except Exception:
        new_info = paths[0].stat()
        atomic_replace(paths[0], crypt_after, crypt, {**file_meta(cstat), "ino": new_info.st_ino})
        discard_recovery(directory)
        raise
    return "absent"


def restore(mapper: str) -> str:
    directory = state_dir(mapper)
    recovery_file = directory / "recovery.json"
    check_regular(recovery_file, "private recovery record", 0o600)
    try:
        manifest = json.loads(recovery_file.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise Refusal("private recovery record is unreadable") from exc
    if manifest.get("schemaVersion") != 1 or manifest.get("mapper") != mapper:
        raise Refusal("private recovery record does not match the mapper")
    keyfile = logical_keyfile(manifest.get("keyPath", ""))
    key = check_regular(keyfile, "selected LUKS keyfile", 0o400)
    expected_key = manifest["keyStat"]
    attrs = (("st_dev", "dev"), ("st_ino", "ino"), ("st_size", "size"), ("st_mtime_ns", "mtimeNs"), ("st_uid", "uid"), ("st_gid", "gid"))
    if any(getattr(key, attr) != expected_key[name] for attr, name in attrs):
        raise Refusal("selected LUKS keyfile changed; recovery retained")
    paths = files()
    records = (manifest["crypttab"], manifest["fstab"])
    current = []
    for path, rec in zip(paths, records):
        data, info = read_file(path, str(path))
        if data != unb64(rec["after"]):
            raise Refusal(f"configuration changed since removal; recovery retained: {path}")
        if info.st_uid != rec["meta"]["uid"] or stat.S_IMODE(info.st_mode) != rec["meta"]["mode"]:
            raise Refusal(f"configuration owner or mode changed; recovery retained: {path}")
        current.append(data)
    atomic_replace(paths[0], current[0], unb64(records[0]["before"]), {**records[0]["meta"], "ino": paths[0].stat().st_ino})
    try:
        atomic_replace(paths[1], current[1], unb64(records[1]["before"]), {**records[1]["meta"], "ino": paths[1].stat().st_ino})
    except Exception:
        restored, info = read_file(paths[0], str(paths[0]))
        atomic_replace(paths[0], restored, current[0], {**records[0]["meta"], "ino": info.st_ino})
        raise
    recovery_file.unlink()
    directory.rmdir()
    return "configured"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("observe", "remove", "restore"))
    parser.add_argument("--mapper", required=True)
    args = parser.parse_args()
    try:
        mapper = validate_mapper(args.mapper)
        if not test_mode() and os.geteuid() != 0:
            raise Refusal("setting.keyfile-mounts requires root")
        if args.action == "observe":
            print(inspect(mapper)[0])
        elif args.action == "remove":
            print(remove(mapper))
        else:
            print(restore(mapper))
        return 0
    except (Refusal, OSError, ValueError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
