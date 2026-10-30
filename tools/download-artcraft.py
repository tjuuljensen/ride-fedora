#!/usr/bin/env python3
"""Discover and archive full Linux installers published by storytold on GitHub.

Uses Python's standard library on Windows or Linux. Public release HTML avoids
requiring credentials or consuming GitHub's shared unauthenticated API quota.
No downloaded executable is run. Each archive records URLs, versions, sizes,
upstream SHA256 digests and local hashes. Dependencies are handled on Fedora by
lib/artcraft/download-dependencies.sh, not guessed from Windows.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import sys
import time
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen

OWNER = "storytold"
BASE = "https://github.com"
FORMATS = {"appimage", "flatpak", "rpm"}


def fetch(url: str):
    if urlparse(url).scheme != "https":
        raise ValueError(f"Only HTTPS downloads are allowed: {url}")
    for attempt in range(4):
        try:
            return urlopen(Request(url, headers={"User-Agent": "ride-fedora-artcraft/1.0"}), timeout=120)
        except OSError:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)


def page(url: str) -> str:
    with fetch(url) as response:
        data = response.read(16 * 1024 * 1024 + 1)
    if len(data) > 16 * 1024 * 1024:
        raise ValueError(f"Oversized release page: {url}")
    return data.decode("utf-8")


def safe_name(name: str) -> str:
    # Also reject Windows reserved path syntax, even when running on Linux.
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.+-]*", name) or name.endswith("."):
        raise ValueError(f"Unsafe upstream filename: {name!r}")
    if name.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL", *{f"COM{i}" for i in range(1, 10)}, *{f"LPT{i}" for i in range(1, 10)}}:
        raise ValueError(f"Reserved filename: {name!r}")
    return name


def repositories() -> list[str]:
    found: set[str] = set()
    for number in range(1, 100):
        body = page(f"{BASE}/orgs/{OWNER}/repositories?type=all&page={number}")
        names = set(re.findall(r'href="/storytold/([A-Za-z0-9_.-]+)"', body))
        total = re.search(r'"repositoryCount":(\d+)', body)
        if not names or (number > 1 and not names - found):
            raise ValueError("Repository pagination stopped before completion")
        found.update(names)
        if total and len(found) >= int(total.group(1)):
            return sorted(found, key=str.lower)
        if 'rel="next"' not in body:
            if total and len(found) != int(total.group(1)):
                raise ValueError("Repository count does not match discovered repositories")
            return sorted(found, key=str.lower)
    raise ValueError("Too many repository pages")


def asset_format(name: str) -> str | None:
    suffix = name.rsplit(".", 1)[-1].lower()
    if suffix not in FORMATS:
        return None
    if re.search(r"(^|[-_.])(demo|trial|lite)([-_.]|$)", name, re.I):
        return None
    return suffix


def asset_arch(name: str) -> str:
    if re.search(r"aarch64|arm64", name, re.I):
        return "aarch64"
    if re.search(r"x86_64|amd64|x64", name, re.I):
        return "x86_64"
    if re.search(r"riscv64", name, re.I):
        return "riscv64"
    if re.search(r"i[3-6]86", name, re.I):
        return "i686"
    return "unspecified"


def parse_assets(body: str, repo: str, tag: str) -> list[dict]:
    assets = []
    seen = set()
    prefix = f"/{OWNER}/{repo}/releases/download/"
    for row in re.split(r"<li\b", body):
        match = re.search(r'href="([^\"]+/releases/download/[^\"]+)"', row)
        if not match:
            continue
        href = html.unescape(match.group(1))
        if not href.startswith(prefix):
            raise ValueError(f"Unexpected asset URL: {href}")
        name = safe_name(unquote(href.rsplit("/", 1)[-1]))
        if name in seen:
            continue
        seen.add(name)
        fmt = asset_format(name)
        if not fmt and name.lower() not in {"sha256sums", "sha256sums.txt", "checksums.txt"}:
            continue
        digest = re.search(r"sha256:([a-fA-F0-9]{64})", row)
        assets.append({"repo": repo, "tag": tag, "name": name,
                       "format": fmt or "checksums", "architecture": asset_arch(name),
                       "url": urljoin(BASE, href),
                       "upstream_sha256": digest.group(1).lower() if digest else None})
    return assets


def discover_repo(repo: str, arch: str) -> dict:
    result = {"name": repo, "url": f"{BASE}/{OWNER}/{repo}", "assets": [], "status": "no-linux-installers"}
    for number in range(1, 100):
        body = page(f"{result['url']}/releases?page={number}")
        fragments = list(dict.fromkeys(html.unescape(x) for x in re.findall(
            r'(?:src|data-deferred-src)="([^\"]+/releases/expanded_assets/[^\"]+)"', body)))
        if not fragments:
            if re.search(r"There aren.t any releases here", html.unescape(body)):
                return result
            raise ValueError(f"Cannot identify releases or an empty release list for {repo}")
        for fragment in fragments:
            if not fragment.startswith(f"{result['url']}/releases/expanded_assets/"):
                raise ValueError(f"Unexpected release fragment: {fragment}")
            tag = unquote(fragment.split("/expanded_assets/", 1)[1])
            assets = parse_assets(page(fragment), repo, tag)
            installers = [a for a in assets if a["format"] in FORMATS]
            if not installers:
                continue
            selected = [a for a in assets if a["format"] == "checksums" or arch == "all" or a["architecture"] in {arch, "unspecified"}]
            result.update(tag=tag, assets=selected, status="available" if any(a["format"] in FORMATS for a in selected) else "architecture-unavailable",
                          available_formats=sorted({a["format"] for a in installers}),
                          missing_formats=sorted(FORMATS - {a["format"] for a in installers}))
            return result
        # GitHub renders both Next and Previous buttons; check for an enabled
        # next link rather than a disabled pagination control.
        if not re.search(r'<a\b[^>]+rel="next"', body):
            return result
    raise ValueError(f"Too many release pages for {repo}")


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".tmp")
    partial.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
    partial.replace(path)


def discover(output: Path, arch: str, workers: int) -> dict:
    repos = repositories()
    print(f"Checking {len(repos)} repositories", flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pending = {pool.submit(discover_repo, r, arch): r for r in repos}
        for future in as_completed(pending):
            repo = pending[future]
            try:
                result = future.result()
            except Exception as exc:
                result = {"name": repo, "assets": [], "status": "error", "error": str(exc)}
            results.append(result)
            if result["assets"] or result["status"] == "error":
                print(f"{repo}: {result['status']} ({len(result['assets'])} files)", flush=True)
    catalog = {"schema_version": 1, "owner": OWNER,
               "generated_at": datetime.now(timezone.utc).isoformat(),
               "architecture": arch, "selection": "newest published release with full Linux installers, including prereleases",
               "repositories": sorted(results, key=lambda r: r["name"].lower())}
    write_json(output, catalog)
    if any(r["status"] == "error" for r in results):
        raise ValueError(f"Incomplete discovery; errors recorded in {output}")
    return catalog


def sha256(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def download_asset(asset: dict, destination: Path) -> dict:
    repo = safe_name(asset["repo"])
    name = safe_name(asset["name"])
    expected_prefix = f"{BASE}/{OWNER}/{repo}/releases/download/"
    if not asset["url"].startswith(expected_prefix):
        raise ValueError(f"Unexpected installer URL: {asset['url']}")
    target = destination / repo / safe_name(asset["tag"]) / name
    target.parent.mkdir(parents=True, exist_ok=True)
    expected = asset.get("upstream_sha256")
    if target.is_file() and expected and sha256(target) == expected:
        return {**asset, "path": target.relative_to(destination).as_posix(), "size": target.stat().st_size,
                "sha256": expected, "status": "verified-existing"}
    partial = target.with_name(target.name + ".part")
    for attempt in range(3):
        try:
            with fetch(asset["url"]) as source, partial.open("wb") as output:
                length = source.headers.get("Content-Length")
                while chunk := source.read(1024 * 1024):
                    output.write(chunk)
            if length and partial.stat().st_size != int(length):
                raise ValueError(f"Truncated installer: {name}")
            digest = sha256(partial)
            if expected and digest != expected:
                raise ValueError(f"SHA256 mismatch: {name}")
            with partial.open("rb") as source:
                magic = source.read(4)
            if asset["format"] == "appimage" and magic != b"\x7fELF":
                raise ValueError(f"Not an ELF AppImage: {name}")
            if asset["format"] == "rpm" and magic != b"\xed\xab\xee\xdb":
                raise ValueError(f"Not an RPM: {name}")
            if partial.stat().st_size == 0:
                raise ValueError(f"Empty download: {name}")
            partial.replace(target)
            return {**asset, "path": target.relative_to(destination).as_posix(), "size": target.stat().st_size,
                    "sha256": digest, "status": "downloaded"}
        except (OSError, ValueError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


def download(catalog: dict, destination: Path, workers: int, formats: set[str]):
    if catalog.get("schema_version") != 1 or catalog.get("owner") != OWNER:
        raise ValueError("Unsupported catalog")
    if any(r["status"] == "error" for r in catalog["repositories"]):
        raise ValueError("Refusing an incomplete catalog; repeat discovery")
    destination.mkdir(parents=True, exist_ok=True)
    write_json(destination / "catalog.json", catalog)
    notes = """ArtCraft Linux installer archive

Choose ONE installer format per application. Files are grouped by repository
and release. catalog.json lists included versions and repositories without
Linux installers; download-report.json records upstream and local hashes.

Verify installers on Linux from this directory:
  sha256sum --check SHA256SUMS.local

Fedora dependencies (when prepared) are in dependencies/fedora-RELEASE-ARCH.
Verify them from that directory: sha256sum --check SHA256SUMS

Offline RPM example from this archive directory (adjust app/version/release):
  sudo dnf --disablerepo='*' install ./APP/VERSION/APP.rpm ./dependencies/fedora-44-x86_64/rpm/*.rpm

Offline Flatpak: install saved runtime bundles first, then one app bundle.
  for bundle in dependencies/fedora-44-x86_64/flatpak/*.flatpak; do
    flatpak install --user --no-deps --no-related "$bundle"
  done
  flatpak install --user --no-deps --no-related APP/VERSION/APP.flatpak

AppImage: chmod +x APP/VERSION/APP.AppImage, then run that file on Linux.
Host GPU drivers are hardware-dependent; this archive includes Mesa/Vulkan
and FUSE support when Fedora dependencies have been prepared.
ArtCraft applications were not executed while preparing this archive.
"""
    (destination / "INSTALL.txt").write_text(notes, encoding="utf-8", newline="\n")
    assets = [a for r in catalog["repositories"] for a in r["assets"] if a["format"] in formats | {"checksums"}]
    report = {"schema_version": 1, "files": [], "dependencies": {"status": "pending-linux-resolution"}}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pending = {pool.submit(download_asset, a, destination): a for a in assets}
        for future in as_completed(pending):
            asset = pending[future]
            try:
                entry = future.result()
                print(f"{entry['status']}: {entry['name']} ({entry['size']:,} bytes)", flush=True)
            except Exception as exc:
                entry = {**asset, "status": "error", "error": str(exc)}
                print(f"ERROR {asset['name']}: {exc}", file=sys.stderr, flush=True)
            report["files"].append(entry)
            write_json(destination / "download-report.json", report)
    if not assets:
        write_json(destination / "download-report.json", report)
    successful = [e for e in report["files"] if e["status"] != "error"]
    sums = "".join(f"{e['sha256']}  {e['path']}\n" for e in sorted(successful, key=lambda e: e["path"]))
    (destination / "SHA256SUMS.local").write_text(sums, encoding="utf-8", newline="\n")
    if any(e["status"] == "error" for e in report["files"]):
        raise ValueError("Some downloads failed; see download-report.json")
    print(f"Saved {len(successful)} files ({sum(e['size'] for e in successful):,} bytes) to {destination}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["discover", "download", "all"])
    parser.add_argument("--catalog", type=Path, default=Path("artcraft-catalog.json"))
    parser.add_argument("--destination", type=Path, default=Path("artcraft-linux"))
    parser.add_argument("--arch", choices=["all", "x86_64", "aarch64"], default="all")
    parser.add_argument("--formats", nargs="+", choices=sorted(FORMATS), default=sorted(FORMATS))
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        parser.error("--workers must be between 1 and 8")
    try:
        if args.action in {"discover", "all"}:
            catalog = discover(args.catalog, args.arch, args.workers)
        else:
            catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        if args.action in {"download", "all"}:
            download(catalog, args.destination.resolve(), args.workers, set(args.formats))
    except (OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
