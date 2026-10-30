#!/usr/bin/env python3
"""Validate and report the scoped RIDE v2-to-v3 migration ledger.

Purpose: Keep every pinned workstation and generic-server v2 outcome visible.
Behavior: Compare the ledger with the legacy source inventory and v3 catalog,
          then print progress or check/generate the Markdown report.
Compatibility: Python 3.11 or newer; no third-party modules.
Usage: python3 tools/migration_progress.py [--summary | --json | --check | --write-docs]
Inputs: migration/outcomes.json, legacy source names, catalog, and evidence files.
Side effects: --write-docs replaces only docs/migrations/progress.md; other modes read only.
Prerequisites: Run from any directory with this repository available.
Owner: RIDE Linux repository. Provenance: local v2 migration inventory.
Version: 0.1.0.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

if __package__:
    from . import build_burndown as inventory
else:
    import build_burndown as inventory


ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "migration" / "outcomes.json"
REPORT = ROOT / "docs" / "migrations" / "progress.md"
VERSION = "0.1.0"
PROGRESS = {"unresolved", "assessed", "implemented", "operable", "supported", "resolved"}
DISPOSITIONS = {"review", "migrate", "replace", "retire", "private", "unsupported"}
RISK = {"low", "medium", "high"}
KEY = re.compile(r"^(workstation|server):(action|package|setting)\.[A-Za-z0-9_]+$")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def source_groups() -> dict[str, list[str]]:
    workstation = inventory.function_names(ROOT / "lib-fedora.sh")
    server = read_json(ROOT / "migration" / "server-inventory.json")["functions"]
    if len(set(workstation)) != len(workstation) or len(set(server)) != len(server):
        raise ValueError("duplicate v2 source function")
    result = {}
    for source, names, excluded in (
        ("workstation", workstation, inventory.WORKSTATION_OUT_OF_SCOPE),
        ("server", server, inventory.SERVER_OUT_OF_SCOPE),
    ):
        if not excluded <= set(names):
            raise ValueError(f"{source} exclusion missing from source inventory")
        for key, functions in inventory.groups([name for name in names if name not in excluded]):
            result[f"{source}:{key}"] = functions
    if len(result) != 180:
        raise ValueError(f"expected 180 scoped outcomes, found {len(result)}")
    return result


def checked_path(value: str, *, required: bool = True) -> Path:
    path = Path(value)
    if not value or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"invalid repository evidence path: {value!r}")
    absolute = ROOT / path
    if required and not absolute.is_file():
        raise ValueError(f"missing evidence file: {value}")
    return absolute


def catalog_matches_target(entry: dict, target_id: str) -> bool:
    variant = "workstation" if target_id == "fedora-44-workstation-x86_64" else "server"
    fedora = entry.get("targets", {}).get("fedora", {})
    return ("44" in fedora.get("releases", [])
            and "x86_64" in fedora.get("architectures", [])
            and variant in fedora.get("variantIds", []))


def validate() -> dict:
    data = read_json(LEDGER)
    if data.get("schemaVersion") != 1:
        raise ValueError("unsupported migration ledger schema")
    expected = source_groups()
    rows = data.get("outcomes")
    if not isinstance(rows, list) or len(rows) != len(expected):
        raise ValueError(f"ledger must contain exactly {len(expected)} outcomes")
    catalog = {row["id"]: row for row in read_json(ROOT / "catalog" / "operations.json")["operations"]}
    workstation_names = set(inventory.function_names(ROOT / "lib-fedora.sh"))
    workstation_active, workstation_commented = inventory.workstation_selectors(workstation_names)
    server_inventory = read_json(ROOT / "migration" / "server-inventory.json")
    server_active = {name for preset in server_inventory["presets"].values() for name in preset["active"]}
    server_commented = {name for preset in server_inventory["presets"].values() for name in preset["commented"]}
    batches = data.get("batches")
    if not isinstance(batches, list) or not batches:
        raise ValueError("migration batches are missing")
    batch_ids = [batch.get("id") for batch in batches]
    if len(batch_ids) != len(set(batch_ids)) or any(not item for item in batch_ids):
        raise ValueError("duplicate or empty migration batch ID")
    batch_map = {batch["id"]: batch for batch in batches}
    for batch in batches:
        if not batch.get("family") or not batch.get("title") or not batch.get("nextAction"):
            raise ValueError(f"incomplete batch {batch['id']}")
        for link in batch.get("evidence", []):
            checked_path(link)
    exclusions = data.get("exclusions", [])
    exclusion_pairs = [(item.get("source"), item.get("sourceFunction")) for item in exclusions]
    expected_exclusions = ({("workstation", name) for name in inventory.WORKSTATION_OUT_OF_SCOPE}
                           | {("server", name) for name in inventory.SERVER_OUT_OF_SCOPE})
    if len(exclusion_pairs) != len(set(exclusion_pairs)) or set(exclusion_pairs) != expected_exclusions:
        raise ValueError("owner exclusions differ from the pinned v2 inventory")
    if any(not item.get("reason") for item in exclusions):
        raise ValueError("an owner exclusion lacks its reason")
    hardening = data.get("v31Hardening", [])
    hardening_ids = [item.get("id") for item in hardening]
    if len(hardening_ids) != len(set(hardening_ids)) or any(
        not item.get("title") or not item.get("trigger") or item.get("status") not in {"queued", "active", "complete"}
        for item in hardening
    ):
        raise ValueError("invalid v3.1 hardening queue")
    seen = set()
    batch_members = Counter()
    for row in rows:
        key = row.get("key")
        if not isinstance(key, str) or not KEY.fullmatch(key) or key in seen:
            raise ValueError(f"duplicate or invalid outcome key: {key!r}")
        seen.add(key)
        if expected.get(key) != row.get("sourceFunctions"):
            raise ValueError(f"source function coverage differs for {key}")
        source = key.split(":", 1)[0]
        active = set(workstation_active) if source == "workstation" else server_active
        commented = set(workstation_commented) if source == "workstation" else server_commented
        expected_coverage = ("active" if any(name in active for name in row["sourceFunctions"])
                             else "commented" if any(name in commented for name in row["sourceFunctions"])
                             else "library-only")
        if row.get("selectorCoverage") != expected_coverage:
            raise ValueError(f"selector coverage differs for {key}")
        batch_id = row.get("batch")
        if batch_id not in batch_map or row.get("family") != batch_map[batch_id]["family"]:
            raise ValueError(f"missing or inconsistent batch for {key}")
        batch_members[batch_id] += 1
        if row.get("risk") not in RISK or row.get("progress") not in PROGRESS:
            raise ValueError(f"invalid risk or progress for {key}")
        if row.get("disposition") not in DISPOSITIONS:
            raise ValueError(f"invalid disposition for {key}")
        if row.get("target") != f"fedora-44-{source}-x86_64":
            raise ValueError(f"incorrect planned target for {key}")
        if not row.get("nextAction"):
            raise ValueError(f"missing next action for {key}")
        if not isinstance(row.get("v3Ids"), list) or not isinstance(row.get("evidence"), list):
            raise ValueError(f"invalid v3 ID or evidence list for {key}")
        if len(row["v3Ids"]) != len(set(row["v3Ids"])):
            raise ValueError(f"duplicate v3 ID for {key}")
        for identifier in row["v3Ids"]:
            if identifier not in catalog:
                raise ValueError(f"unknown v3 operation {identifier} for {key}")
        for link in row["evidence"]:
            checked_path(link)
        if not set(row.get("v31Hardening", [])) <= set(hardening_ids):
            raise ValueError(f"unknown v3.1 hardening item for {key}")
        progress, disposition = row["progress"], row["disposition"]
        if progress in {"unresolved", "assessed", "implemented"} and not row.get("blocker"):
            raise ValueError(f"incomplete outcome needs a blocker for {key}")
        if disposition == "review" and progress != "unresolved":
            raise ValueError(f"unreviewed outcome claims progress: {key}")
        if progress in {"operable", "supported"}:
            if disposition != "migrate" or not row["v3Ids"] or not row["evidence"]:
                raise ValueError(f"{key} claims an operation without mapping and evidence")
            if progress == "operable" and row["risk"] == "high":
                raise ValueError(f"high-risk {key} cannot count as opt-in operable")
            if progress == "operable" and not row["v31Hardening"]:
                raise ValueError(f"opt-in {key} lacks a named v3.1 hardening follow-up")
            for identifier in row["v3Ids"]:
                entry = catalog[identifier]
                expected_status = "supported" if progress == "supported" else "candidate"
                if entry["status"] != expected_status or not catalog_matches_target(entry, row["target"]):
                    raise ValueError(f"{key} catalog status or target disagrees with progress")
                if progress == "supported":
                    checked_path(entry.get("acceptanceEvidence", ""))
            target_edition = "Workstation" if source == "workstation" else "Server"
            if not any(
                link.startswith("docs/acceptance/") and
                (record := checked_path(link).read_text(encoding="utf-8")) and
                "PASS" in record and "Fedora 44" in record and target_edition in record and
                all(identifier in record for identifier in row["v3Ids"])
                for link in row["evidence"]
            ):
                raise ValueError(f"{key} lacks passing VM acceptance evidence")
        if progress == "resolved":
            if (disposition not in {"replace", "retire", "private", "unsupported"} or not row["evidence"]
                    or not row.get("reason") or not row.get("reviewTrigger")):
                raise ValueError(f"{key} lacks a documented non-operable resolution")
        if progress in {"operable", "supported", "resolved"} and row.get("blocker"):
            raise ValueError(f"completed outcome still has a blocker: {key}")
    if seen != set(expected):
        raise ValueError(f"source outcome coverage differs: missing={sorted(set(expected)-seen)}, extra={sorted(seen-set(expected))}")
    if set(batch_members) != set(batch_map):
        raise ValueError("empty migration batch")
    for batch_id, count in batch_members.items():
        if count > 6 or (count > 1 and batch_map[batch_id]["family"] != "desktop-user"
                         and any(row["batch"] == batch_id and row["risk"] == "high" for row in rows)):
            raise ValueError(f"oversized or mixed high-risk batch: {batch_id}")
    return data


def summarize(data: dict) -> dict:
    rows = data["outcomes"]
    progress = Counter(row["progress"] for row in rows)
    disposition = Counter(row["disposition"] for row in rows if row["progress"] == "resolved")
    complete = sum(progress[item] for item in ("operable", "supported", "resolved"))
    batches = []
    for batch in data["batches"]:
        members = [row for row in rows if row["batch"] == batch["id"]]
        done = sum(row["progress"] in {"operable", "supported", "resolved"} for row in members)
        batches.append({"id": batch["id"], "family": batch["family"], "title": batch["title"],
                        "total": len(members), "complete": done, "evidence": batch["evidence"],
                        "risk": dict(Counter(row["risk"] for row in members)),
                        "nextAction": batch["nextAction"]})
    return {"total": len(rows), "complete": complete, "percent": round(100*complete/len(rows), 1),
            "supported": progress["supported"], "operableCandidate": progress["operable"],
            "replaced": disposition["replace"],
            "runnable": progress["supported"] + progress["operable"],
            "requiresAllowCandidate": progress["operable"],
            "retired": disposition["retire"], "private": disposition["private"],
            "unsupported": disposition["unsupported"], "unresolved": len(rows)-complete,
            "risk": dict(Counter(row["risk"] for row in rows)), "batches": batches,
            "v31Hardening": data["v31Hardening"]}


def render(data: dict) -> str:
    report = summarize(data)
    lines = ["# V2 to v3 migration progress", "",
             "Generated from `migration/outcomes.json`; run `python3 tools/migration_progress.py --summary` for a current CLI view.",
             "Source outcomes are counted separately from catalog operations. A disposition is not a working install.", "",
             f"**{report['complete']}/{report['total']} complete ({report['percent']}%)**: "
             f"{report['supported']} supported, {report['operableCandidate']} opt-in candidate, "
             f"{report['replaced']} replaced, {report['retired']} retired, {report['private']} private, "
             f"{report['unsupported']} unsupported; {report['unresolved']} unresolved.", "",
             f"Runnable outcomes: {report['runnable']}; {report['requiresAllowCandidate']} require `--allow-candidate`. "
             "Owner exclusions: 2 Citrix functions and 13 host-specific server functions, outside the 180 outcomes.", "",
             "| Batch | Family | Risk | Complete | Evidence | Next action |",
             "| --- | --- | --- | ---: | --- | --- |"]
    for batch in report["batches"]:
        links = ", ".join(f"[{Path(path).name}](../../{path})" for path in batch["evidence"]) or "—"
        risk = ", ".join(f"{level} {count}" for level, count in sorted(batch["risk"].items()))
        lines.append(f"| `{batch['id']}` | {batch['title']} | {risk} | {batch['complete']}/{batch['total']} | {links} | {batch['nextAction']} |")
    lines += ["", "## v3.1 hardening queue", "",
              "These items do not replace v3.0 safety checks for data, storage, encryption, or security behavior.", "",
              "| ID | Item | Trigger | Status |", "| --- | --- | --- | --- |"]
    for item in data["v31Hardening"]:
        lines.append(f"| `{item['id']}` | {item['title']} | {item['trigger']} | {item['status']} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--summary", action="store_true", help="print a concise progress summary (default)")
    mode.add_argument("--json", action="store_true", help="print machine-readable progress")
    mode.add_argument("--check", action="store_true", help="validate ledger and generated report without writes")
    mode.add_argument("--write-docs", action="store_true", help="write the generated progress report")
    parser.add_argument("--version", action="version", version=f"migration-progress {VERSION}")
    args = parser.parse_args()
    try:
        data = validate()
        expected = render(data)
        if args.check and (not REPORT.is_file() or REPORT.read_text(encoding="utf-8") != expected):
            raise ValueError("progress report is stale; run --write-docs")
        if args.write_docs:
            REPORT.parent.mkdir(parents=True, exist_ok=True)
            REPORT.write_text(expected, encoding="utf-8")
        if args.json:
            print(json.dumps(summarize(data), indent=2))
        elif args.summary or not (args.check or args.write_docs):
            report = summarize(data)
            print(f"v2 outcomes: {report['complete']}/{report['total']} ({report['percent']}%) complete")
            print(f"supported={report['supported']} opt-in-candidate={report['operableCandidate']} "
                  f"replaced={report['replaced']} retired={report['retired']} private={report['private']} "
                  f"unsupported={report['unsupported']} unresolved={report['unresolved']}")
            print(f"runnable={report['runnable']} requires-allow-candidate={report['requiresAllowCandidate']}")
            for batch in report["batches"]:
                print(f"{batch['id']}: {batch['complete']}/{batch['total']} - {batch['nextAction']}")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"Migration progress invalid: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
