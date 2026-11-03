#!/usr/bin/env python3
"""Validate the pinned shared behavior scenarios and Fedora test adapter."""

import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
SCENARIO_PATH = Path("docs/models/behavior-scenarios.json")
REFERENCE_PATH = Path("docs/models/ride-behavior-contract-ref.json")
ADAPTER_PATH = Path("tests/fixtures/behavior-scenario-fedora-adapter.json")


def _read_json(root, relative):
    with (root / relative).open(encoding="utf-8") as stream:
        return json.load(stream)


def validate_envelope(scenario_set, adapter, contract_reference):
    errors = []
    revision = scenario_set.get("scenarioRevision")
    if scenario_set.get("schemaVersion") != 1:
        errors.append("unsupported behavior-scenario schema version")
    if not revision or adapter.get("scenarioRevision") != revision:
        errors.append("scenario revision differs from the Fedora adapter pin")
    if scenario_set.get("contractVersion") != contract_reference.get("contractVersion"):
        errors.append("scenario contract version differs from the Fedora contract pin")
    if scenario_set.get("contractSha256", "").upper() != contract_reference.get("sha256", "").upper():
        errors.append("scenario contract digest differs from the Fedora contract pin")

    scenarios = scenario_set.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        errors.append("behavior-scenario set is empty or invalid")
        scenarios = []
    ids = [item.get("id") for item in scenarios if isinstance(item, dict)]
    if len(ids) != len(scenarios) or any(not item for item in ids):
        errors.append("every behavior scenario must have an ID")
    if len(ids) != len(set(ids)):
        errors.append("behavior-scenario IDs must be unique")
    for item in scenarios:
        if not isinstance(item, dict):
            continue
        if not item.get("rules") or not item.get("expected"):
            errors.append(f"scenario {item.get('id', '<unknown>')} lacks rules or expected behavior")
        if {"windowsAdapter", "fedoraAdapter"}.intersection(item):
            errors.append(f"scenario {item.get('id', '<unknown>')} embeds platform-specific adapter data")

    mappings = adapter.get("mappings")
    if not isinstance(mappings, list):
        errors.append("Fedora adapter mappings are invalid")
        mappings = []
    mapping_ids = [item.get("scenarioId") for item in mappings if isinstance(item, dict)]
    if len(mapping_ids) != len(mappings) or len(mapping_ids) != len(set(mapping_ids)):
        errors.append("each Fedora adapter mapping must have one unique scenario ID")
    if set(mapping_ids) != set(ids):
        errors.append("Fedora adapter must map every shared scenario exactly once")
    for mapping in mappings:
        if mapping.get("localDisposition") == "temporary-difference" and not mapping.get("differenceId"):
            errors.append(f"temporary difference {mapping.get('scenarioId')} lacks a difference ID")
    return errors


def _declared_tests(source):
    tree = ast.parse(source)
    tests = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    tests.add((node.name, member.name))
    return tests


def validate_repository(root=ROOT):
    scenario_set = _read_json(root, SCENARIO_PATH)
    reference = _read_json(root, REFERENCE_PATH)
    adapter = _read_json(root, ADAPTER_PATH)
    errors = validate_envelope(scenario_set, adapter, reference)

    actual_digest = hashlib.sha256((root / SCENARIO_PATH).read_bytes()).hexdigest().upper()
    if adapter.get("scenarioSha256", "").upper() != actual_digest:
        errors.append("shared scenario bytes differ from the Fedora adapter digest pin")

    for mapping in adapter.get("mappings", []) + adapter.get("supportingTests", []):
        relative = Path(mapping.get("testFile", ""))
        path = (root / relative).resolve()
        if not relative.parts or path != root.resolve() and root.resolve() not in path.parents:
            errors.append(f"test mapping escapes the repository: {relative}")
            continue
        if not path.is_file():
            errors.append(f"mapped test file is missing: {relative}")
            continue
        try:
            declared = _declared_tests(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError) as error:
            errors.append(f"cannot inspect mapped test file {relative}: {error}")
            continue
        case = (mapping.get("testClass"), mapping.get("testMethod"))
        if case not in declared:
            errors.append(f"mapped test does not exist: {relative}:{case[0]}.{case[1]}")

    return errors, len(scenario_set.get("scenarios", [])), scenario_set.get("scenarioRevision", "unknown")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate pins and test mappings")
    args = parser.parse_args()
    errors, count, revision = validate_repository()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Validated shared behavior scenarios {revision}: {count} cases mapped to Fedora tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
