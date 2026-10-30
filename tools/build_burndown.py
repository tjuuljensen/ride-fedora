#!/usr/bin/env python3
"""Render the scoped workstation and server outcome queue."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "docs" / "workstation-server-burndown.md"
PROGRESS_LEDGER = ROOT / "migration" / "outcomes.json"
WAYDROID_REFERENCE = ROOT / "reference" / "install-waydroid-fedora.sh"
FUNCTION = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)\(\)\s*\{", re.MULTILINE)
SELECTOR = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)\b")
COMMENTED = re.compile(r"^\s*#\s*([A-Za-z][A-Za-z0-9_]*)\b")

# User-scoped exclusions: obsolete or host-specific functions stay in legacy
# source and the server name inventory, but are not v3 migration outcomes.
WORKSTATION_OUT_OF_SCOPE = {"InstallCitrixClient", "RemoveCitrixClient"}
SERVER_OUT_OF_SCOPE_TAIL = (
    "CreateqBittorrentUser",
    "InstallqBittorrentServer",
    "CreateQbtFirewallRules",
    "CreateQbtServiceFile",
    "CreateQbtSSHkeys",
    "CreatePlexUser",
    "InstallPlexServer",
    "CreatePlexFirewallRules",
    "InstallPlexAutoUpdate",
    "InstallAMP",
    "InstallFerium",
    "InstallMinecraftServer",
)
SERVER_OUT_OF_SCOPE = {"MountNASSMBfolders", *SERVER_OUT_OF_SCOPE_TAIL}


def function_names(path: Path) -> list[str]:
    return FUNCTION.findall(path.read_text(encoding="utf-8"))


def workstation_selectors(names: set[str]) -> tuple[list[str], list[str]]:
    active, commented = [], []
    for line in (ROOT / "default.preset").read_text(encoding="utf-8").splitlines():
        if match := SELECTOR.match(line):
            active.append(match.group(1))
        elif match := COMMENTED.match(line):
            if match.group(1) in names or match.group(1) == "RequireAdmin":
                commented.append(match.group(1))
    return active, commented


def group_key(name: str) -> tuple[str, str]:
    for first, second, kind in (
        ("Install", "Remove", "package"),
        ("Install", "Uninstall", "package"),
        ("Set", "Unset", "setting"),
        ("Enable", "Disable", "setting"),
        ("Show", "Hide", "setting"),
    ):
        if name.startswith(first) and len(name) > len(first) and name[len(first)].isupper():
            return kind, name[len(first):]
        if name.startswith(second) and len(name) > len(second) and name[len(second)].isupper():
            return kind, name[len(second):]
    return "action", name


def groups(names: list[str]) -> list[tuple[str, list[str]]]:
    result: dict[tuple[str, str], list[str]] = {}
    for name in names:
        result.setdefault(group_key(name), []).append(name)
    return [(f"{kind}.{outcome}", members) for (kind, outcome), members in result.items()]


def active_ledger() -> dict[str, tuple[str, str]]:
    result = {}
    for line in (ROOT / "docs" / "MIGRATION-PLAN.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            break
        if line.startswith("| `"):
            parts = line.split("|")
            result[parts[1].strip().strip("`")] = (parts[2].strip(), parts[3].strip())
    return result


def workstation_disposition(members: list[str], active: set[str], ledger: dict) -> str:
    for name in members:
        if name in active:
            disposition, reason = ledger[name]
            return f"{disposition}: {reason}"
    names = set(members)
    special = {
        "InstallVolatility3": "implemented candidate `package.volatility3`; isolated pinned core, VM acceptance pending",
        "InstallPlaso": "deferred candidate; opt-in COPR and removal need VM evidence",
        "InstallAutopsy": "deferred candidate; upstream Linux setup and removal need VM evidence",
        "InstallGalleta": "deferred incomplete legacy stub; source and current package need review",
        "InstallXplico": "deferred incomplete legacy stub; source and current package need review",
        "InstallFirefoxAddons": "deferred v3 integration; existing policy helper remains tested separately",
        "CheckFirefoxAddons": "deferred v3 integration; existing policy helper remains tested separately",
        "FinalizeFirefoxAddonRemoval": "deferred v3 integration; restart-dependent policy lifecycle needs journal ownership",
    }
    for name, decision in special.items():
        if name in names:
            return decision
    if members[0].startswith(("Install", "Remove", "Uninstall")):
        return "deferred; inspect current package or publisher, detection, verification, removal and recovery"
    if members[0].startswith(("Set", "Unset", "Enable", "Disable", "Show", "Hide")):
        return "deferred; inspect exact prior value, ownership, applicability and restore"
    return "deferred; classify as explicit operation, private value, CLI utility or retired behavior"


def server_disposition(members: list[str]) -> str:
    name = members[0]
    if name == "ViewIPaddress":
        return "retire as install outcome; expose inspection through `status` if useful"
    if name in {"SetHostname", "GenerateSSHkeysRSA"}:
        return "private overlay for host values or key material; extract generic behavior only after ownership review"
    if name in {"InstallPythonPip", "InstallSelenium"}:
        return "replace global Python installation with isolated, pinned per-tool environment"
    if name in {"UpdateFedora", "InstallRequired", "InstallAutoUpdate"}:
        return "deferred generic server baseline; split package/update/timer behavior and record recovery limits"
    if name == "SetNoRootLogin":
        return "deferred SSH policy setting; preserve existing file content and test exact restore"
    if name.startswith(("InstallExpressVPN", "CreateVPN", "SetVPN")):
        return "deferred opt-in VPN profile; keep provider account and host routing private"
    return "deferred optional server operation; verify current package/source, state and recovery"


def render() -> str:
    if not WAYDROID_REFERENCE.is_file():
        raise ValueError("Waydroid reference candidate is missing")
    workstation_source_names = function_names(ROOT / "lib-fedora.sh")
    if len(set(workstation_source_names)) != len(workstation_source_names):
        raise ValueError("duplicate workstation function names")
    if not WORKSTATION_OUT_OF_SCOPE <= set(workstation_source_names):
        raise ValueError("a workstation exclusion is missing from the source library")
    workstation_names = [name for name in workstation_source_names if name not in WORKSTATION_OUT_OF_SCOPE]
    active_list, commented_list = workstation_selectors(set(workstation_source_names))
    active, commented = set(active_list), set(commented_list)
    ledger = active_ledger()
    if active != set(ledger):
        raise ValueError("active workstation preset and migration ledger differ")
    inventory = json.loads((ROOT / "migration" / "server-inventory.json").read_text(encoding="utf-8"))
    server_source_names = inventory["functions"]
    if len(set(server_source_names)) != len(server_source_names):
        raise ValueError("duplicate server function names")
    if not SERVER_OUT_OF_SCOPE <= set(server_source_names):
        raise ValueError("a server exclusion is missing from the source inventory")
    if server_source_names[server_source_names.index(SERVER_OUT_OF_SCOPE_TAIL[0]):] != list(SERVER_OUT_OF_SCOPE_TAIL):
        raise ValueError("server inventory changed after the excluded outcome boundary; review scope")
    server_names = [name for name in server_source_names if name not in SERVER_OUT_OF_SCOPE]
    workstation_groups = groups(workstation_names)
    server_groups = groups(server_names)
    progress_rows = json.loads(PROGRESS_LEDGER.read_text(encoding="utf-8"))["outcomes"]
    progress = {row["key"]: row for row in progress_rows}
    expected_progress = ({f"workstation:{key}" for key, _ in workstation_groups}
                         | {f"server:{key}" for key, _ in server_groups})
    if len(progress) != len(progress_rows) or set(progress) != expected_progress:
        raise ValueError("migration progress ledger does not cover the source outcome queue")
    inactive_workstation = sum(not any(name in active for name in members) for _, members in workstation_groups)
    server_active = {name for preset in inventory["presets"].values() for name in preset["active"]}
    server_commented = {name for preset in inventory["presets"].values() for name in preset["commented"]}
    inactive_server = sum(not any(name in server_active for name in members)
                          for _, members in server_groups)
    lines = [
        "# Workstation and server outcome burndown",
        "",
        "This queue covers workstation and generic server migration candidates, including",
        "functions absent from active presets. Obsolete and host-specific functions excluded",
        "by the owner remain in the legacy source and server name inventory, outside this queue.",
        "Install/remove and analogous state pairs share an outcome row. A `deferred` row is",
        "inventory, not an executable operation or acceptance claim.",
        "Current progress and batch assignment come from `migration/outcomes.json`; the",
        "older disposition text records the initial migration assessment.",
        "Selector coverage records v2 preset references, not actual installations or",
        "a priority rule. Active, commented, and library-only packages receive the same",
        "source and product review; risk and dependencies determine batch order.",
        "",
        f"Workstation source: `lib-fedora.sh` at Fedora commit `43ba467`; {len(workstation_source_names)} source functions,",
        f"{len(workstation_names)} queued functions,",
        f"{len(workstation_groups)} grouped outcomes, {inactive_workstation} outcomes with no active default selector.",
        f"Function coverage: {len(active & set(workstation_names))} active, "
        f"{len((commented - active) & set(workstation_names))} commented-only, "
        f"{len(set(workstation_names) - active - commented)} library-only.",
        f"Default preset: {len(active_list)} active selectors and {len(commented_list)} commented selectors",
        "that name a defined function or controller action. The [active migration ledger](MIGRATION-PLAN.md)",
        "provides the decisions for all active selectors.",
        "",
        f"Server source: `{inventory['libraryPath']}` at `network-devices` commit",
        f"`{inventory['sourceCommit']}`; {len(server_source_names)} source functions,",
        f"{len(server_names)} queued functions, {len(server_groups)} outcomes,",
        f"{inactive_server} outcomes absent from all active server presets. Its three preset inventories",
        "are stored as names only in `migration/server-inventory.json`; no host values were copied.",
        f"Function coverage: {len(server_active & set(server_names))} active in a server preset, "
        f"{len((server_commented - server_active) & set(server_names))} commented-only, "
        f"{len(set(server_names) - server_active - server_commented)} library-only.",
        "",
        "## Workstation library",
        "",
        "| Outcome key | Exact source functions | Selector coverage | Initial disposition / review rationale | Batch / current progress |",
        "| --- | --- | --- | --- | --- |",
    ]
    for key, members in workstation_groups:
        selection = ", ".join(
            f"`{name}`: " + ("active" if name in active else "commented" if name in commented else "library only")
            for name in members
        )
        decision = workstation_disposition(members, active, ledger)
        current = progress[f"workstation:{key}"]
        lines.append(f"| `{key}` | {', '.join(f'`{name}`' for name in members)} | {selection} | {decision} | "
                     f"`{current['batch']}` / {current['progress']} |")
    lines += [
        "",
        "`PressAnyKeyToContinue` and `Restart` are active default selectors but live outside",
        "`lib-fedora.sh`; both are retired as install outcomes in the active ledger.",
        "`RequireAdmin` is a commented controller selector, also outside the library.",
        "",
        "## Reference-script candidates",
        "",
        "These are review inputs outside the v2 function libraries. They have no executable",
        "v3 catalog ID and are not selected by a profile.",
        "",
        "| Outcome | Reference | Status | Migration review |",
        "| --- | --- | --- | --- |",
        "| Waydroid on a mutable Fedora workstation | "
        "[install-waydroid-fedora.sh](../reference/install-waydroid-fedora.sh) | "
        "deferred; reference-only and not clean-VM tested | "
        "Split Fedora package installation, OTA image initialization, container service, "
        "and optional firewalld policy into owned changes. Verify image provenance, "
        "repeat apply, partial failure, removal and restore on a disposable Fedora "
        "Wayland workstation. Keep forced reinitialization explicit. |",
        "",
        "## Server library and presets",
        "",
        "| Outcome key | Exact source functions | Active presets | Commented presets | Initial disposition / review rationale | Batch / current progress |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for key, members in server_groups:
        active_presets = [name.removesuffix(".preset") for name, preset in inventory["presets"].items()
                          if any(member in preset["active"] for member in members)]
        commented_presets = [name.removesuffix(".preset") for name, preset in inventory["presets"].items()
                             if any(member in preset["commented"] for member in members)]
        current = progress[f"server:{key}"]
        lines.append(
            f"| `{key}` | {', '.join(f'`{name}`' for name in members)} | "
            f"{', '.join(active_presets) or '—'} | {', '.join(commented_presets) or '—'} | "
            f"{server_disposition(members)} | `{current['batch']}` / {current['progress']} |"
        )
    lines += [
        "",
        "`RequireAdmin`, `PressAnyKeyToContinue` and `Restart` appear as active server preset",
        "selectors but are controller flow, not server-library outcomes. The commented",
        "`GenerateSSHkeys` selector is not defined in the server library; it must not silently",
        "resolve to `GenerateSSHkeysRSA` without a migration decision.",
        "",
        "## Current retirement and replacement decisions",
        "",
        "These dispositions come from `migration/outcomes.json` and supersede the",
        "initial assessment above. The ledger records each reason and review trigger.",
        "",
        "| Source outcome | Current disposition | Batch |",
        "| --- | --- | --- |",
    ]
    for row in progress_rows:
        if row["disposition"] in {"retire", "replace"}:
            lines.append(f"| `{row['key']}` | `{row['disposition']}` | `{row['batch']}` |")
    lines += [
        "",
        "## Closeout rules",
        "",
        "1. Count an outcome as operable only with a mapped v3 operation and focused",
        "   automated evidence. Only a target-specific VM pass permits supported status.",
        "   Keep candidate, supported, and non-operable resolutions distinct.",
        "2. Mark a retired outcome only with a concrete reason. Do not turn an old no-op",
        "   function into a successful v3 operation.",
        "3. Reconcile server consumers in `complete`, `plexserver`, and `streambox` before",
        "   moving generic behavior. Keep hostname, NAS, accounts, secrets and media paths",
        "   in a private overlay.",
        "4. Regenerate this table after any source inventory or disposition change with",
        "   `python3 tools/build_burndown.py --write`.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render()
    if args.write:
        OUTPUT.write_text(content, encoding="utf-8")
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content):
        raise SystemExit("workstation/server burndown is stale; run --write")
    outcomes = json.loads(PROGRESS_LEDGER.read_text(encoding="utf-8"))["outcomes"]
    decisions = sum(row["disposition"] in {"retire", "replace"} for row in outcomes)
    print(f"Verified {len(outcomes)} library outcome rows, {decisions} current "
          "retirement/replacement decisions, and 1 reference candidate")


if __name__ == "__main__":
    main()
