#!/usr/bin/env python3
"""Save names and preset selectors from the separate server repo, never values."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "migration" / "server-inventory.json"
FUNCTION = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)\(\)\s*\{", re.MULTILINE)
SELECTOR = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)\b")
COMMENTED = re.compile(r"^\s*#\s*([A-Za-z][A-Za-z0-9_]*)\b")


def selectors(path: Path, library_names: set[str]) -> dict:
    active, commented = [], []
    for line in path.read_text(encoding="utf-8").splitlines():
        if match := SELECTOR.match(line):
            active.append(match.group(1))
        elif match := COMMENTED.match(line):
            if match.group(1) in library_names or match.group(1) == "GenerateSSHkeys":
                commented.append(match.group(1))
    return {"active": active, "commented": commented,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("server_ride_directory", type=Path)
    args = parser.parse_args()
    directory = args.server_ride_directory.resolve()
    library = directory / "lib-fedora-server.sh"
    functions = FUNCTION.findall(library.read_text(encoding="utf-8"))
    commit = subprocess.check_output(
        ["git", "-C", str(directory), "rev-parse", "HEAD"], text=True,
    ).strip()
    data = {
        "schemaVersion": 1, "sourceCommit": commit,
        "libraryPath": "operations/provisioning/ride/lib-fedora-server.sh",
        "librarySha256": hashlib.sha256(library.read_bytes()).hexdigest(),
        "functions": functions,
        "presets": {path.name: selectors(path, set(functions))
                    for path in sorted((directory / "presets").glob("*.preset"))},
    }
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(functions)} server function names and {len(data['presets'])} preset inventories")


if __name__ == "__main__":
    main()
