"""Pytest entry point for disposable Linux guest acceptance."""

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from uuid import uuid4

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.vm_acceptance import VM, load_target, select_pilot  # noqa: E402


def pytest_addoption(parser):
    group = parser.getgroup("RIDE VM acceptance")
    group.addoption("--vm-target", help="Target ID from tests/acceptance/targets.json")
    group.addoption("--vm-pilot", help="Declared pilot operation; defaults to the target's first pilot")
    group.addoption("--vm-image", help="Local, verified qcow2 image for the target")
    group.addoption("--vm-accel", choices=("kvm", "tcg"), default="kvm",
                    help="QEMU acceleration; tcg is a slower software fallback")
    group.addoption("--vm-output", default="/tmp/ride-acceptance-runs",
                    help="Directory for VM overlays, transcripts, and console logs")


def pytest_configure(config):
    config.addinivalue_line("markers", "recovery(mode): package recovery contract required by the scenario")
    config.addinivalue_line("markers", "vm_target(id): VM target required by the scenario")


@pytest.fixture
def vm(request):
    target_id = request.config.getoption("--vm-target")
    image = request.config.getoption("--vm-image")
    if not target_id or not image:
        pytest.fail("both --vm-target and --vm-image are required")
    target = select_pilot(load_target(target_id), request.config.getoption("--vm-pilot"))
    required_target = request.node.get_closest_marker("vm_target")
    if required_target is not None and target_id != required_target.args[0]:
        pytest.skip(f"scenario requires {required_target.args[0]}")
    required_recovery = request.node.get_closest_marker("recovery")
    if required_recovery is not None:
        catalog = json.loads((ROOT / "catalog" / "operations.json").read_text(encoding="utf-8"))
        operation = next(item for item in catalog["operations"]
                         if item["id"] == target["pilotOperation"])
        if operation["recovery"] != required_recovery.args[0]:
            pytest.skip(f"{target['pilotOperation']} has {operation['recovery']} recovery")
    name = re.sub(r"[^a-z0-9-]", "-", request.node.name.lower()).strip("-")[:80]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifacts = Path(request.config.getoption("--vm-output")).expanduser().resolve()
    artifacts = artifacts / target_id / f"{stamp}-{name}-{uuid4().hex[:8]}"
    machine = VM(target, Path(image), artifacts, accel=request.config.getoption("--vm-accel"))
    machine.start()
    try:
        yield machine
    finally:
        machine.stop()
