"""Pytest entry point for disposable Linux guest acceptance."""

from datetime import datetime, timezone
from pathlib import Path
import re
import sys
from uuid import uuid4

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.vm_acceptance import VM, load_target  # noqa: E402


def pytest_addoption(parser):
    group = parser.getgroup("RIDE VM acceptance")
    group.addoption("--vm-target", help="Target ID from tests/acceptance/targets.json")
    group.addoption("--vm-image", help="Local, verified qcow2 image for the target")
    group.addoption("--vm-output", default="/tmp/ride-acceptance-runs",
                    help="Directory for VM overlays, transcripts, and console logs")


@pytest.fixture
def vm(request):
    target_id = request.config.getoption("--vm-target")
    image = request.config.getoption("--vm-image")
    if not target_id or not image:
        pytest.fail("both --vm-target and --vm-image are required")
    target = load_target(target_id)
    name = re.sub(r"[^a-z0-9-]", "-", request.node.name.lower()).strip("-")[:80]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifacts = Path(request.config.getoption("--vm-output")).expanduser().resolve()
    artifacts = artifacts / target_id / f"{stamp}-{name}-{uuid4().hex[:8]}"
    machine = VM(target, Path(image), artifacts)
    machine.start()
    try:
        yield machine
    finally:
        machine.stop()
