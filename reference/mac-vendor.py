#!/usr/bin/env python3
"""
mac-vendor.py

Purpose:
  Look up the IEEE registry assignee/vendor for a MAC address or MAC prefix.

Description:
  Downloads and caches IEEE public MAC assignment registries, then performs
  longest-prefix matching against normalized MAC addresses.

  Supported registries:
    - MA-L / OUI   : 24-bit prefix
    - MA-M         : 28-bit prefix
    - MA-S / OUI36 : 36-bit prefix
    - IAB          : 36-bit prefix

Usage:
  python3 mac-vendor.py 00:1A:2B:33:44:55
  python3 mac-vendor.py --update
  python3 mac-vendor.py --offline --show-address 00:1A:2B:33:44:55
  python3 mac-vendor.py --quiet --json 00-1A-2B

Cache:
  Shares ieee-mac-vendors.tsv and metadata.json with mac-vendor.sh under
  $XDG_CACHE_HOME/mac-vendor, or $HOME/.cache/mac-vendor when XDG_CACHE_HOME
  is unset or empty. --cache-dir overrides this location for either script.
  Both scripts can read and refresh the same cache.

  The default freshness threshold is seven days, configurable with
  --max-age-days. Missing, empty, or stale caches are refreshed automatically
  unless --offline is set. --offline performs no downloads and requires an
  existing nonempty cache; stale caches are accepted in offline mode.

  --update explicitly refreshes all four IEEE registries. On a terminal,
  --update without positional addresses exits after refreshing; otherwise,
  lookup continues using positional addresses or piped input. Empty query
  input exits 2. Combining --update with --offline is a CLI error (exit 2),
  detected before any cache access or download.

Output model:
  Default output includes the vendor, registry, prefix, and MAC flag notes.
  --show-address adds registry addresses to normal text output.
  --quiet prints only vendor names (Unknown for unmatched queries) and
  suppresses download progress messages.
  --json prints an array of complete lookup results, one per query.
  Together, --quiet and --json include only the organization field per query,
  with null for unknown vendors, for example:
    [{"organization": "Example Vendor"}, {"organization": null}]

Security / privacy note:
  This script performs local lookup against a cached IEEE database. It does not
  submit queried MAC addresses to an online lookup API.

Limitations:
  A MAC vendor lookup identifies the registry assignee for a prefix. It does not
  prove the current physical manufacturer, device type, owner, or authenticity
  of the device. Locally administered/randomized MAC addresses often cannot be
  meaningfully resolved.

Author:
  Torsten Juul-Jensen

Version:
  1.0.0

Date:
  2026-10-15
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import ipaddress
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


VERSION = "1.0.0"
DEFAULT_MAX_AGE_DAYS = 7

IEEE_REGISTRIES = [
    {
        "name": "MA-L",
        "bits": 24,
        "url": "https://standards-oui.ieee.org/oui/oui.csv",
    },
    {
        "name": "MA-M",
        "bits": 28,
        "url": "https://standards-oui.ieee.org/oui28/mam.csv",
    },
    {
        "name": "MA-S",
        "bits": 36,
        "url": "https://standards-oui.ieee.org/oui36/oui36.csv",
    },
    {
        "name": "IAB",
        "bits": 36,
        "url": "https://standards-oui.ieee.org/iab/iab.csv",
    },
]


@dataclass(frozen=True)
class VendorRecord:
    prefix: str
    bits: int
    registry: str
    organization: str
    address: str = ""


@dataclass(frozen=True)
class LookupResult:
    query: str
    normalized: str
    prefix: str | None
    bits: int | None
    registry: str | None
    organization: str | None
    address: str | None
    locally_administered: bool
    multicast: bool


class ScriptError(RuntimeError):
    """User-facing error."""


def default_cache_dir() -> Path:
    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    if xdg_cache:
        return Path(xdg_cache) / "mac-vendor"
    return Path.home() / ".cache" / "mac-vendor"


def normalize_mac(value: str) -> str:
    normalized = re.sub(r"[^0-9A-Fa-f]", "", value).upper()

    if len(normalized) < 6:
        raise ScriptError(f"MAC address/prefix is too short: {value!r}")

    if len(normalized) > 12:
        raise ScriptError(f"MAC address/prefix is too long: {value!r}")

    if not re.fullmatch(r"[0-9A-F]+", normalized):
        raise ScriptError(f"Invalid MAC address/prefix: {value!r}")

    return normalized


def mac_flags(normalized: str) -> tuple[bool, bool]:
    first_octet = int(normalized[0:2], 16)

    multicast = bool(first_octet & 0b00000001)
    locally_administered = bool(first_octet & 0b00000010)

    return locally_administered, multicast


def cache_file(cache_dir: Path) -> Path:
    return cache_dir / "ieee-mac-vendors.tsv"


def metadata_file(cache_dir: Path) -> Path:
    return cache_dir / "metadata.json"


def cache_is_fresh(path: Path, max_age_days: int) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return False

    age = dt.datetime.now(dt.timezone.utc) - dt.datetime.fromtimestamp(
        path.stat().st_mtime,
        tz=dt.timezone.utc,
    )

    return age <= dt.timedelta(days=max_age_days)


def download_text(url: str, timeout: int) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": f"mac-vendor.py/{VERSION}",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.URLError as exc:
        raise ScriptError(f"Could not download {url}: {exc}") from exc

    return raw.decode("utf-8-sig")


def row_value(row: dict[str, str], *names: str) -> str:
    for name in names:
        if name in row and row[name] is not None:
            return row[name].strip()
    return ""


def parse_registry_csv(text: str, registry_name: str, bits: int) -> list[VendorRecord]:
    records: list[VendorRecord] = []

    reader = csv.DictReader(text.splitlines())

    if not reader.fieldnames:
        raise ScriptError(f"{registry_name}: CSV has no header row.")

    for row in reader:
        assignment = row_value(row, "Assignment")
        organization = row_value(
            row,
            "Organization Name",
            "Organization",
            "Company Name",
        )
        address = row_value(
            row,
            "Organization Address",
            "Address",
        )

        prefix = re.sub(r"[^0-9A-Fa-f]", "", assignment).upper()

        if not prefix or not organization:
            continue

        expected_hex_len = bits // 4

        if len(prefix) < expected_hex_len:
            continue

        prefix = prefix[:expected_hex_len]

        if not re.fullmatch(r"[0-9A-F]+", prefix):
            continue

        records.append(
            VendorRecord(
                prefix=prefix,
                bits=bits,
                registry=registry_name,
                organization=organization,
                address=address,
            )
        )

    return records


def update_cache(cache_dir: Path, timeout: int, quiet: bool) -> int:
    cache_dir.mkdir(parents=True, exist_ok=True)

    all_records: list[VendorRecord] = []

    for registry in IEEE_REGISTRIES:
        name = registry["name"]
        bits = int(registry["bits"])
        url = str(registry["url"])

        if not quiet:
            print(f"Downloading {name}: {url}", file=sys.stderr)

        text = download_text(url, timeout)
        records = parse_registry_csv(text, name, bits)

        if not quiet:
            print(f"  {len(records)} records", file=sys.stderr)

        all_records.extend(records)

    # Prefer longest prefixes if duplicates occur.
    all_records.sort(key=lambda r: (r.prefix, -r.bits, r.registry, r.organization))

    final_cache = cache_file(cache_dir)

    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        newline="",
        dir=str(cache_dir),
        delete=False,
    ) as tmp:
        tmp_path = Path(tmp.name)
        writer = csv.writer(tmp, delimiter="\t", lineterminator="\n")
        writer.writerow(["prefix", "bits", "registry", "organization", "address"])

        for record in all_records:
            writer.writerow(
                [
                    record.prefix,
                    record.bits,
                    record.registry,
                    record.organization,
                    record.address,
                ]
            )

    tmp_path.replace(final_cache)
    final_cache.chmod(0o644)

    metadata = {
        "tool": "mac-vendor.py",
        "tool_version": VERSION,
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "registries": IEEE_REGISTRIES,
        "record_count": len(all_records),
    }

    metadata_file(cache_dir).write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    if not quiet:
        print(f"Cache updated: {final_cache}", file=sys.stderr)

    return len(all_records)


def load_cache(path: Path) -> dict[int, dict[str, VendorRecord]]:
    if not path.exists() or path.stat().st_size == 0:
        raise ScriptError(f"Vendor cache does not exist or is empty: {path}")

    index: dict[int, dict[str, VendorRecord]] = {
        36: {},
        28: {},
        24: {},
    }

    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")

        for row in reader:
            prefix = row.get("prefix", "").strip().upper()
            bits_text = row.get("bits", "").strip()
            registry = row.get("registry", "").strip()
            organization = row.get("organization", "").strip()
            address = row.get("address", "").strip()

            if not bits_text.isdigit():
                continue

            bits = int(bits_text)

            if bits not in index:
                continue

            if not prefix or not organization:
                continue

            # Keep the first record for exact duplicate prefixes.
            index[bits].setdefault(
                prefix,
                VendorRecord(
                    prefix=prefix,
                    bits=bits,
                    registry=registry,
                    organization=organization,
                    address=address,
                ),
            )

    return index


def lookup_vendor(index: dict[int, dict[str, VendorRecord]], query: str) -> LookupResult:
    normalized = normalize_mac(query)
    locally_administered, multicast = mac_flags(normalized)

    for bits in (36, 28, 24):
        hex_len = bits // 4

        if len(normalized) < hex_len:
            continue

        prefix = normalized[:hex_len]
        record = index.get(bits, {}).get(prefix)

        if record:
            return LookupResult(
                query=query,
                normalized=normalized,
                prefix=record.prefix,
                bits=record.bits,
                registry=record.registry,
                organization=record.organization,
                address=record.address,
                locally_administered=locally_administered,
                multicast=multicast,
            )

    return LookupResult(
        query=query,
        normalized=normalized,
        prefix=None,
        bits=None,
        registry=None,
        organization=None,
        address=None,
        locally_administered=locally_administered,
        multicast=multicast,
    )


def print_result(result: LookupResult, *, quiet: bool, show_address: bool) -> None:
    if quiet:
        print(result.organization or "Unknown")
        return

    if result.organization:
        prefix_text = f"{result.prefix}/{result.bits}"
        print(f"{result.query} -> {result.organization} [{result.registry}, {prefix_text}]")

        if show_address and result.address:
            print(f"  {result.address}")
    else:
        print(f"{result.query} -> Unknown")

    if result.locally_administered:
        print("  Note: locally administered/randomized MAC; vendor lookup may be meaningless.")

    if result.multicast:
        print("  Note: multicast/group MAC; vendor lookup may be meaningless.")


def iter_queries(args: argparse.Namespace) -> Iterable[str]:
    if args.addresses:
        yield from args.addresses
        return

    if not sys.stdin.isatty():
        for line in sys.stdin:
            value = line.strip()
            if value:
                yield value
        return

    value = input("MAC address or prefix: ").strip()
    if value:
        yield value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Look up IEEE MAC/OUI vendor assignments.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  mac-vendor.py 00:1A:2B:33:44:55
  mac-vendor.py --quiet 00-1A-2B
  mac-vendor.py --update
  mac-vendor.py --offline 00:1A:2B:33:44:55
  printf '%s\\n' 00:1A:2B:33:44:55 3C:52:82:AA:BB:CC | mac-vendor.py

Accepted input formats:
  00:1A:2B:33:44:55
  00-1A-2B-33-44-55
  001A.2B33.4455
  001A2B334455
  001A2B
""",
    )

    parser.add_argument("addresses", nargs="*", help="MAC address or prefix to look up")
    parser.add_argument("-s", "--quiet", action="store_true", help="print only the vendor name (with --json: organization only)")
    parser.add_argument("-u", "--update", action="store_true", help="download and refresh the local IEEE cache")
    parser.add_argument("--offline", action="store_true", help="do not download; require an existing cache")
    parser.add_argument("--json", action="store_true", help="print JSON output")
    parser.add_argument("--show-address", action="store_true", help="include registry address in normal output")
    parser.add_argument("--cache-dir", type=Path, default=default_cache_dir(), help="cache directory")
    parser.add_argument("--max-age-days", type=int, default=DEFAULT_MAX_AGE_DAYS, help="cache freshness threshold")
    parser.add_argument("--timeout", type=int, default=30, help="download timeout in seconds")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.update and args.offline:
        parser.error("--update and --offline cannot be combined")

    try:
        cfile = cache_file(args.cache_dir)

        if args.update:
            update_cache(args.cache_dir, args.timeout, args.quiet)
            if not args.addresses and sys.stdin.isatty():
                return 0

        if not args.offline and not cache_is_fresh(cfile, args.max_age_days):
            update_cache(args.cache_dir, args.timeout, args.quiet)

        index = load_cache(cfile)

        results = [lookup_vendor(index, query) for query in iter_queries(args)]

        if not results:
            parser.print_usage(sys.stderr)
            return 2

        if args.json:
            output = [
                {"organization": result.organization} if args.quiet else asdict(result)
                for result in results
            ]
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            for result in results:
                print_result(result, quiet=args.quiet, show_address=args.show_address)

        return 0

    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130

    except ScriptError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
