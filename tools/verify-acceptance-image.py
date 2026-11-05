#!/usr/bin/env python3
"""Boot one freshly built acceptance image, verify its target, and retain evidence.

Purpose: Verify a locally built Fedora qcow2 boots to cloud-init and SSH.
Behavior: Uses the VM harness with a fresh overlay, checks target identity,
          runs only read-only guest commands, then shuts the VM down.
Compatibility: Python 3.12+; x86_64 Linux host.
Usage: python3 tools/verify-acceptance-image.py IMAGE RELEASE EDITION OUTPUT_DIR [--accel kvm|tcg]
Inputs: Fedora qcow2, release 44/45, edition workstation/server, output directory.
Side effects: Creates disposable overlay, cloud-init seed, SSH key, logs, and transcript under OUTPUT_DIR.
Prerequisites: QEMU, qemu-img, genisoimage, SSH tools; KVM or slower TCG.
Owner: RIDE Fedora maintainers.
Provenance: Uses tools/vm_acceptance.py VM lifecycle and target checks.
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.vm_acceptance import VM  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("release", choices=("44", "45"))
    parser.add_argument("edition", choices=("workstation", "server"))
    parser.add_argument("output", type=Path)
    parser.add_argument("--accel", choices=("kvm", "tcg"), default=None)
    args = parser.parse_args()

    hasher = hashlib.sha256()
    with args.image.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    digest = hasher.hexdigest()
    target = {
        "id": f"fedora-{args.release}-{args.edition}-x86_64",
        "distro": "fedora",
        "release": args.release,
        "edition": "Workstation" if args.edition == "workstation" else "Server",
        "variantId": args.edition,
        "architecture": "x86_64",
        "imageFormat": "qcow2",
        "imageSha256": digest,
        "imageSource": "locally built from Fedora Everything ISO",
        "imageRelease": args.release,
        "acceptanceScope": "image-boot-verification",
        "pilotOperation": "package.less",
        "pilotPackage": "less",
        "seedPackages": [],
        "packageDatabase": "rpm",
        "packageVerification": "rpm-signature-and-files",
        "vmSmp": 4,
        "vmMemoryMiB": 6144,
    }
    output = args.output.resolve()
    kvm_available = Path("/dev/kvm").exists() and os.access("/dev/kvm", os.R_OK | os.W_OK)
    vm = VM(target, args.image, output, accel=args.accel or ("kvm" if kvm_available else "tcg"))
    try:
        vm.start()
        result = vm.run("printf 'boot=PASS\\n'; cat /etc/os-release; uname -m; cloud-init status --long")
        (output / "identity.txt").write_text(result.stdout, encoding="utf-8")
        (output / "target.json").write_text(json.dumps(target, indent=2) + "\n", encoding="utf-8")
        print(result.stdout)
        print(f"Boot acceptance evidence: {output}")
    finally:
        vm.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
