#!/usr/bin/env python3
"""Add a locally built and inspected Fedora image to the VM target matrix.

Purpose: Register a verified Fedora 44/45 Workstation or Server image.
Behavior: Confirms the build manifest hashes against the ISO, Kickstart,
          checksum file, and qcow2, then clones the matching Fedora 44 target
          metadata with the new target identity and evidence digests.
Compatibility: Python 3.12+.
Usage: python3 tools/register-acceptance-target.py IMAGE RELEASE EDITION BUILD_DIR
Inputs: Locally built image, its manifest, installer ISO, signed CHECKSUM file,
        and tests/acceptance/fedora-RELEASE-EDITION.ks.
Side effects: Updates tests/acceptance/targets.json after all checks pass.
Prerequisites: Python standard library and a completed build-acceptance-images.sh build.
Owner: RIDE Fedora maintainers.
Provenance: Target metadata model in tests/acceptance/targets.json.
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "tests" / "acceptance" / "targets.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_manifest(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        key, sep, value = line.partition("=")
        if not sep or key in values:
            raise ValueError(f"invalid/duplicate manifest field: {line}")
        values[key] = value
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("release", choices=("44", "45"))
    parser.add_argument("edition", choices=("workstation", "server"))
    parser.add_argument("build_dir", type=Path)
    args = parser.parse_args()

    build_dir = args.build_dir.resolve()
    manifest = read_manifest(build_dir / "manifest.txt")
    iso_name = Path(manifest["iso_source"]).name
    checksum_name = manifest["installer_checksum_file"]
    iso = build_dir.parent / iso_name
    checksum_file = build_dir.parent / checksum_name
    kickstart = ROOT / "tests" / "acceptance" / f"fedora-{args.release}-{args.edition}.ks"
    checks = {
        "image_sha256": (digest(args.image),),
        "iso_sha256": (digest(iso),),
        "kickstart_sha256": (digest(kickstart),),
        "installer_checksum_sha256": (digest(checksum_file),),
    }
    for key, (actual,) in checks.items():
        if manifest.get(key) != actual:
            raise SystemExit(f"{key} mismatch: manifest {manifest.get(key)!r}, actual {actual!r}")
    if (manifest.get("release"), manifest.get("edition"), manifest.get("architecture")) != (
            args.release, args.edition, "x86_64"):
        raise SystemExit("build manifest target does not match requested release/edition")

    data = json.loads(TARGETS.read_text(encoding="utf-8"))
    target_id = f"fedora-{args.release}-{args.edition}-x86_64"
    if any(item["id"] == target_id for item in data["targets"]):
        raise SystemExit(f"target already exists; refusing to overwrite: {target_id}")
    baseline_id = f"fedora-44-{args.edition}-x86_64"
    baseline = next((item for item in data["targets"] if item["id"] == baseline_id), None)
    if baseline is None:
        raise SystemExit(f"missing baseline target metadata: {baseline_id}")
    target = json.loads(json.dumps(baseline))
    target.update({
        "id": target_id,
        "release": args.release,
        "imageSha256": manifest["image_sha256"],
        "imageSource": manifest["iso_source"],
        "imageRelease": args.release,
        "imageInstallerSha256": manifest["iso_sha256"],
        "imageBuildRecipeSha256": manifest["kickstart_sha256"],
        "imageBuildRecipe": f"tests/acceptance/fedora-{args.release}-{args.edition}.ks",
    })
    data["targets"].append(target)
    temporary = TARGETS.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(TARGETS)
    print(f"Registered {target_id} with image SHA-256 {manifest['image_sha256']}")
    print("Fedora checksum signature was verified during fetch; retain the CHECKSUM and fedora.gpg files with image evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
