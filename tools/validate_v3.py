#!/usr/bin/env python3
"""Validate v3 JSON data and generate its operation reference."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog" / "operations.json"
PROFILES = ROOT / "profiles"
DOC = ROOT / "docs" / "OPERATIONS.md"
COMMAND_DOC = ROOT / "docs" / "COMMANDS.md"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def validate() -> dict:
    catalog = load_json(CATALOG)
    schema = load_json(ROOT / "schemas" / "catalog.schema.json")
    Draft202012Validator(schema).validate(catalog)
    entries = catalog["operations"]
    by_id = {entry["id"]: entry for entry in entries}
    if len(by_id) != len(entries):
        raise ValueError("duplicate catalog ID")
    for entry in entries:
        if entry["kind"] == "package":
            sources = [entry["sourceId"], *(source["sourceId"] for source in entry.get("sourceProviders", []))]
            if len(sources) != len(set(sources)):
                raise ValueError(f"{entry['id']} repeats a source ID")
            package_names = [
                name for name in [entry.get("packageName"),
                                  *(source["packageName"] for source in entry.get("sourceProviders", []))]
                if name is not None
            ]
            if len(package_names) != len(set(package_names)):
                raise ValueError(f"{entry['id']} has RPM sources that cannot be distinguished by observation")
            for source in entry.get("sourceProviders", []):
                if source["status"] == "supported":
                    evidence = source.get("acceptanceEvidence")
                    expected = f"docs/acceptance/{entry['id']}.{source['sourceId']}.md"
                    if evidence != expected or not (ROOT / expected).is_file():
                        raise ValueError(f"{entry['id']}/{source['sourceId']} lacks acceptance evidence")
                    record = (ROOT / expected).read_text(encoding="utf-8")
                    if not all(field in record for field in (entry["id"], source["sourceId"], "VM", "PASS")):
                        raise ValueError(f"{entry['id']}/{source['sourceId']} lacks a passed VM run")
        for dependency in entry.get("dependencies", []):
            if dependency not in by_id:
                raise ValueError(f"{entry['id']} has unknown dependency {dependency}")
        if entry["status"] == "supported":
            evidence = entry.get("acceptanceEvidence")
            if evidence != f"docs/acceptance/{entry['id']}.md" or not (ROOT / evidence).is_file():
                raise ValueError(f"{entry['id']} claims support without acceptance evidence")
            record = (ROOT / evidence).read_text(encoding="utf-8")
            if not all(field in record for field in (entry["id"], "VM", "PASS")):
                raise ValueError(f"{entry['id']} acceptance evidence lacks a passed VM run")

    profile_schema = load_json(ROOT / "schemas" / "profile.schema.json")
    for path in sorted(PROFILES.glob("*.json")):
        profile = load_json(path)
        Draft202012Validator(profile_schema).validate(profile)
        seen: set[str] = set()
        for item in profile["operations"]:
            op_id = item["id"]
            if op_id in seen:
                raise ValueError(f"duplicate {op_id} in {path.name}")
            seen.add(op_id)
            if op_id not in by_id:
                raise ValueError(f"unknown {op_id} in {path.name}")
            if item["state"] not in by_id[op_id]["states"]:
                raise ValueError(f"invalid state for {op_id} in {path.name}")
            if by_id[op_id]["kind"] == "artifact":
                raise ValueError(f"download-only artifact {op_id} in {path.name}")
            source = item.get("source")
            if source is not None:
                entry = by_id[op_id]
                if entry["kind"] != "package" or source not in [
                    entry["sourceId"], *(variant["sourceId"] for variant in entry.get("sourceProviders", []))
                ]:
                    raise ValueError(f"unknown source {source} for {op_id} in {path.name}")
    return catalog


def render_docs(catalog: dict) -> str:
    lines = [
        "# RIDE v3 operations",
        "",
        "Generated from `catalog/operations.json` by `tools/validate_v3.py`.",
        "Candidate operations need explicit `--allow-candidate` until disposable VM acceptance.",
        "",
        "| ID | Group | Outcome | Targets | Product / source | License | Verification | Recovery | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in catalog["operations"]:
        targets = ", ".join(
            f"{distro} {','.join(map(str, target['releases']))} ({','.join(target['architectures'])})"
            for distro, target in entry["targets"].items()
        )
        description = entry["description"].replace("|", "\\|")
        source_label = (
            f" (`{entry['sourceId']}`; {entry['distribution']}/"
            f"{entry['deploymentId']}; {entry['artifactFormat']}; {entry['scope']})"
            if entry["kind"] == "package" else ""
        )
        alternative_sources = ", ".join(
            f"[{source['sourceId']}]({source['sourceUri']})"
            for source in entry.get("sourceProviders", [])
        )
        if alternative_sources:
            source_label += f"; alternatives: {alternative_sources}"
        lines.append(
            f"| `{entry['id']}` | {entry['group']} | {description} | {targets} | "
            f"[{entry['productId']}]({entry['productUri']}) / [source]({entry['sourceUri']}){source_label} | "
            f"[{entry['license']}]({entry['licenseUri']}) | {entry['verification']} | "
            f"{entry['recovery']} | {entry['status']} |"
        )
    lines += [
        "",
        "Repository package operations request DNF GPG checking; RPM downloads also force",
        "signature verification at RPM's `all` level. Artifact SHA-256 evidence",
        "from GitHub metadata detects transfer changes but is not an independent publisher signature.",
        "A candidate becomes supported only after its target VM matrix is recorded and reviewed.",
        "",
    ]
    return "\n".join(lines)


def render_commands() -> str:
    help_text = subprocess.run(
        ["bash", str(ROOT / "ride.sh"), "--help"],
        check=True, capture_output=True, text=True,
    ).stdout.rstrip()
    return "# RIDE v3 commands\n\nGenerated from `ride.sh --help`.\n\n```text\n" + help_text + "\n```\n"


def validate_migration_maps() -> None:
    active = [
        match.group(1)
        for line in (ROOT / "default.preset").read_text(encoding="utf-8").splitlines()
        if (match := re.match(r"^([A-Za-z][A-Za-z0-9_]*)\b", line))
    ]
    ledger = [
        match.group(1)
        for line in (ROOT / "docs" / "MIGRATION-PLAN.md").read_text(encoding="utf-8").splitlines()
        if (match := re.match(r"^\| `([^`]+)` \|", line))
    ]
    if active != ledger:
        raise ValueError("Fedora migration ledger does not match active default.preset order")
    sander = (ROOT / "docs" / "sander-feature-map.md").read_text(encoding="utf-8")
    if len(re.findall(r"^\| [^|]+ \| `[^`]+` \|", sander, re.MULTILINE)) != 185:
        raise ValueError("Sander feature map no longer has its pinned 185-function inventory")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-docs", action="store_true")
    parser.add_argument("--check-docs", action="store_true")
    args = parser.parse_args()
    try:
        catalog = validate()
        validate_migration_maps()
        expected = render_docs(catalog)
        commands = render_commands()
        if args.write_docs:
            DOC.write_text(expected, encoding="utf-8")
            COMMAND_DOC.write_text(commands, encoding="utf-8")
        if args.check_docs and (not DOC.exists() or DOC.read_text(encoding="utf-8") != expected):
            raise ValueError("docs/OPERATIONS.md is out of date; run tools/validate_v3.py --write-docs")
        if args.check_docs and (not COMMAND_DOC.exists() or COMMAND_DOC.read_text(encoding="utf-8") != commands):
            raise ValueError("docs/COMMANDS.md is out of date; run tools/validate_v3.py --write-docs")
        print(f"Validated {len(catalog['operations'])} operations and {len(list(PROFILES.glob('*.json')))} profiles")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
