"""Read-only inventory of local RIDE v3 journals for migration review.

Prints run IDs, status, changed operation IDs, and whether a completed restore
exists. It never prints saved state values or changes a journal.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys


RUN_ID = re.compile(r"^[0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+$")
OPERATION_ID = re.compile(r"^(package|setting|artifact|system)\.[a-z0-9.-]+$")
MAX_JOURNAL_BYTES = 16 * 1024 * 1024


def inventory(directory: Path) -> tuple[list[tuple[str, str, str, str]], int]:
    """Return public-only summary rows and an invalid-journal count."""
    try:
        mode = os.lstat(directory).st_mode
    except FileNotFoundError:
        return [], 0
    if not stat.S_ISDIR(mode):
        raise ValueError("state path must be a real directory")

    journals: dict[str, dict] = {}
    invalid: list[str] = []
    with os.scandir(directory) as entries:
        paths = sorted(Path(entry.path) for entry in entries if entry.name.endswith(".json"))
    for path in paths:
        if not RUN_ID.fullmatch(path.stem):
            invalid.append(json.dumps(path.name))
            continue
        try:
            descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(descriptor, "rb") as stream:
                size = os.fstat(stream.fileno())
                if not stat.S_ISREG(size.st_mode) or size.st_size > MAX_JOURNAL_BYTES:
                    raise ValueError("journal is not a regular bounded file")
                data = json.loads(stream.read(MAX_JOURNAL_BYTES + 1).decode("utf-8"))
            if (not isinstance(data, dict) or
                    type(data.get("schemaVersion")) is not int or
                    data["schemaVersion"] not in (1, 2) or
                    data.get("runId") != path.stem or
                    data.get("status") not in ("running", "complete", "failed") or
                    not isinstance(data.get("action"), str) or
                    (data["action"].startswith("restore:") and
                     not RUN_ID.fullmatch(data["action"].removeprefix("restore:"))) or
                    not isinstance(data.get("steps"), list) or
                    any(not isinstance(step, dict) or
                        not isinstance(step.get("id"), str) or
                        not OPERATION_ID.fullmatch(step["id"]) or
                        step.get("result") not in ("pending", "changed", "unchanged", "failed")
                        for step in data["steps"])):
                raise ValueError("invalid journal shape")
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
            invalid.append(json.dumps(path.name))
            continue
        journals[path.stem] = data

    restored = {
        data["action"].removeprefix("restore:")
        for data in journals.values()
        if data["status"] == "complete" and data["action"].startswith("restore:")
    }
    rows: list[tuple[str, str, str, str]] = []
    for identifier, data in sorted(journals.items()):
        changed = sorted({step["id"] for step in data["steps"]
                          if step["result"] == "changed"})
        uncertain = any(step["result"] in ("pending", "failed") for step in data["steps"])
        orphan_restore = (data["action"].startswith("restore:") and
                          data["action"].removeprefix("restore:") not in journals)
        state = ("restored" if identifier in restored else
                 "restore-record" if data["status"] == "complete" and
                 data["action"].startswith("restore:") and not uncertain and
                 not orphan_restore else
                 "review" if changed or uncertain or orphan_restore or
                 data["status"] != "complete" else
                 "no-changes")
        rows.append((identifier, data["status"], state, ",".join(changed) or "-"))
    rows.extend((name, "invalid", "review", "-") for name in invalid)
    return rows, len(invalid)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=Path("/var/lib/ride-fedora/runs"),
                        help="local RIDE run directory (default: /var/lib/ride-fedora/runs)")
    args = parser.parse_args(argv)
    try:
        rows, invalid = inventory(args.state_dir)
    except (OSError, ValueError) as error:
        print(f"audit error: {error}", file=sys.stderr)
        return 2
    print("RUN_ID\tSTATUS\tREVIEW\tCHANGED_OPERATIONS")
    for row in rows:
        print("\t".join(row))
    print(f"journals={len(rows)} review={sum(row[2] == 'review' for row in rows)}")
    return 2 if invalid else 0


if __name__ == "__main__":
    raise SystemExit(main())
