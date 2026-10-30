"""Pinned UnfURL user environment lifecycle on Fedora Workstation."""

import json
import re
import shlex

import pytest


OPERATION = "package.dfir-unfurl"
RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")
ENVIRONMENT = "/home/ride-test/.local/share/ride-fedora/tools/dfir-unfurl"
JOURNALS = "/home/ride-test/.local/state/ride-fedora/runs"


def run_id(output):
    match = RUN_ID.search(output)
    assert match, output
    return match.group(1)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_unfurl_user_environment(vm):
    def ride(*args, timeout=120):
        return vm.run(shlex.join((f"{vm.repo}/ride.sh", *args)), timeout=timeout)

    def journal(identifier):
        return json.loads(vm.run(f"cat {JOURNALS}/{identifier}.json").stdout)

    vm.run("python3 --version")
    vm.run(f"test ! -e {ENVIRONMENT} && test ! -e {JOURNALS}")
    sibling = "/home/ride-test/.local/share/ride-fedora/tools/keep.txt"
    vm.run(f"mkdir -p {ENVIRONMENT.rsplit('/', 1)[0]} && printf keep > {sibling}")
    profile = vm.put_json("unfurl", {
        "schemaVersion": 1, "id": "unfurl-acceptance",
        "description": "Disposable UnfURL acceptance",
        "operations": [{"id": OPERATION, "state": "installed"}],
    })
    plan = ride("plan", "--profile", profile)
    assert f"{OPERATION}\tpypi-venv\tabsent\tinstalled\tcandidate" in plan.stdout
    applied = ride("apply", "--profile", profile, "--allow-candidate", timeout=1200)
    first = run_id(applied.stdout)
    record = journal(first)
    assert record["status"] == "complete" and record["steps"][0]["result"] == "changed"
    vm.run(f"test -x {ENVIRONMENT}/bin/unfurl && test -x {ENVIRONMENT}/bin/unfurl_app")
    vm.run(f"{ENVIRONMENT}/bin/python -c 'import importlib.metadata as m; "
           "assert m.version(\"dfir-unfurl\") == \"20261007\"'")
    parsed = vm.run(f"{ENVIRONMENT}/bin/unfurl 'https://example.invalid/path?a=b'", timeout=120)
    assert "example.invalid" in parsed.stdout
    status = ride("status", OPERATION)
    assert f"{OPERATION}\tpypi-venv\tinstalled" in status.stdout
    repeated = ride("apply", "--profile", profile, "--allow-candidate")
    assert journal(run_id(repeated.stdout))["steps"][0]["result"] == "unchanged"
    ride("restore", "--run-id", first, "--allow-candidate", timeout=120)
    vm.run(f"test ! -e {ENVIRONMENT} && test \"$(cat {sibling})\" = keep")
    ride("install", OPERATION, "--allow-candidate", timeout=1200)
    ride("remove", OPERATION, "--allow-candidate", timeout=120)
    vm.run(f"test ! -e {ENVIRONMENT} && test \"$(cat {sibling})\" = keep")
