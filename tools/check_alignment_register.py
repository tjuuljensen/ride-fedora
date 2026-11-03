#!/usr/bin/env python3
"""Validate the pinned Fedora/Windows capability-difference register."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parent.parent
REGISTER = Path("docs/models/capability-differences.json")
CONTRACT_REF = Path("docs/models/ride-behavior-contract-ref.json")
ALLOWED_DISPOSITIONS = {"aligned", "temporary-gap", "permanent-platform-difference"}
ALLOWED_DECISIONS = {"source-reviewed", "open", "proposed-owner-review"}


def validate_register(register, contract_reference):
    errors = []
    if register.get("schemaVersion") != 1:
        errors.append("unsupported capability-difference register schema version")
    if register.get("contractVersion") != contract_reference.get("contractVersion"):
        errors.append("register contract version differs from the consumer pin")
    if not isinstance(register.get("reviewedOn"), str) or not register["reviewedOn"]:
        errors.append("register lacks its review date")

    sources = register.get("reviewedSources", {})
    for source_name in ("rideWindows", "rideFedora"):
        source = sources.get(source_name, {})
        if not re.fullmatch(r"[0-9a-f]{7,40}", str(source.get("commit", ""))):
            errors.append(f"{source_name} lacks a reviewed commit")
        if not source.get("branch") or not isinstance(source.get("paths"), list) or not source["paths"]:
            errors.append(f"{source_name} lacks a branch or reviewed paths")
    fedora_hashes = sources.get("rideFedora", {}).get("sha256", {})
    if not isinstance(fedora_hashes, dict) or not fedora_hashes:
        errors.append("Fedora source snapshot lacks working-tree hashes")

    entries = register.get("entries")
    if not isinstance(entries, list) or not entries:
        return errors + ["register has no entries"]
    ids = []
    required = ("capability", "disposition", "decisionStatus", "owner", "reason",
                "ruleIds", "evidence", "linkedWork", "reviewRemovalTrigger")
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("register entry must be an object")
            continue
        ident = entry.get("id", "")
        ids.append(ident)
        for key in required:
            missing = key not in entry or entry[key] is None or entry[key] == ""
            if key != "linkedWork" and entry.get(key) == []:
                missing = True
            if missing:
                errors.append(f"entry {ident or '<missing-id>'} lacks {key}")
        if entry.get("disposition") not in ALLOWED_DISPOSITIONS:
            errors.append(f"entry {ident} has an invalid disposition")
        if entry.get("decisionStatus") not in ALLOWED_DECISIONS:
            errors.append(f"entry {ident} has an invalid decision status")
        if not all(re.fullmatch(r"RB-[0-9]{2}", str(rule)) for rule in entry.get("ruleIds", [])):
            errors.append(f"entry {ident} has an invalid behavior rule ID")
        if not isinstance(entry.get("evidence"), list) or not all(
                isinstance(item, dict) and item.get("windows") and item.get("fedora")
                for item in entry.get("evidence", [])):
            errors.append(f"entry {ident} needs Windows and Fedora evidence")
        if entry.get("disposition") == "temporary-gap" and not entry.get("linkedWork"):
            errors.append(f"temporary gap {ident} needs linked work")
    if len(ids) != len(set(ids)):
        errors.append("register entry IDs must be unique")
    return errors


def validate_repository(root=ROOT):
    register = json.loads((root / REGISTER).read_text(encoding="utf-8"))
    contract_reference = json.loads((root / CONTRACT_REF).read_text(encoding="utf-8"))
    errors = validate_register(register, contract_reference)
    for relative, expected in register.get("reviewedSources", {}).get("rideFedora", {}).get("sha256", {}).items():
        path = (root / relative).resolve()
        if root.resolve() not in path.parents or not path.is_file():
            errors.append(f"reviewed Fedora source path is missing or outside repository: {relative}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected.lower():
            errors.append(f"reviewed Fedora source changed since register snapshot: {relative}")
    return errors, len(register.get("entries", []))


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    errors, count = validate_repository()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Validated Fedora/Windows capability-difference register: {count} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
