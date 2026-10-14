"""Real package lifecycle contract, initially exercised on Fedora Cloud Base."""

import copy
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
CATALOG = json.loads((ROOT / "catalog" / "operations.json").read_text(encoding="utf-8"))
RUN_ID = re.compile(r"^Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)$", re.MULTILINE)


def run_id(output):
    match = RUN_ID.search(output)
    assert match, output
    return match.group(1)


def journal(vm, identifier):
    assert RUN_ID.fullmatch(f"Run ID: {identifier}")
    return json.loads(vm.run(f"sudo cat /var/lib/ride-fedora/runs/{identifier}.json").stdout)


def profile(*ids):
    return {"schemaVersion": 1, "id": "acceptance",
            "description": "Disposable VM acceptance fixture",
            "operations": [{"id": identifier, "state": "installed"} for identifier in ids]}


def package_installed(vm):
    package = vm.target["pilotPackage"]
    if vm.target["packageDatabase"] == "rpm":
        return vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
    if vm.target["packageDatabase"] == "dpkg":
        state = vm.run(f"dpkg-query -W -f='${{Status}}' {package}", check=False)
        return state.returncode == 0 and state.stdout.strip() == "install ok installed"
    raise AssertionError("unknown package database")


def package_inventory(vm):
    if vm.target["packageDatabase"] == "rpm":
        return vm.run(
            "rpm -qa --qf '%{NAME}\\t%{EPOCH}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' | sort"
        ).stdout
    if vm.target["packageDatabase"] == "dpkg":
        return vm.run("dpkg-query -W -f='${Package}\\t${Version}\\n' | sort").stdout
    raise AssertionError("unknown package database")


def verify_installed_package(vm):
    package = vm.target["pilotPackage"]
    if vm.target["packageVerification"] == "rpm-signature-and-files":
        signatures = vm.run(
            f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        vm.run(f"rpm -V {package}")
        return
    raise AssertionError(f"package verifier is not implemented: {vm.target['packageVerification']}")


def test_package_apply_repeat_status_restore_and_remove(vm):
    pilot_id = vm.target["pilotOperation"]
    assert not package_installed(vm), "pilot package must be absent in the verified base image"
    baseline_packages = package_inventory(vm)
    guest_profile = vm.put_json("pilot-profile", profile(pilot_id))

    plan = vm.ride("plan", "--profile", guest_profile)
    assert f"{pilot_id}\tabsent\tinstalled\tcandidate" in plan.stdout
    assert not package_installed(vm)
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0

    first = vm.ride("apply", "--profile", guest_profile, "--allow-candidate", timeout=900)
    first_id = run_id(first.stdout)
    first_journal = journal(vm, first_id)
    assert first_journal["status"] == "complete"
    assert [(step["id"], step["observedBefore"], step["observedAfter"], step["result"])
            for step in first_journal["steps"]] == [(pilot_id, "absent", "installed", "changed")]
    assert package_installed(vm)
    assert f"{pilot_id}\tinstalled\tcandidate" in vm.ride("status", pilot_id).stdout

    verify_installed_package(vm)

    repeat = vm.ride("apply", "--profile", guest_profile, "--allow-candidate", timeout=900)
    repeat_journal = journal(vm, run_id(repeat.stdout))
    assert repeat_journal["status"] == "complete"
    assert repeat_journal["steps"][0]["result"] == "unchanged"

    vm.ride("restore", "--run-id", first_id, "--dry-run")
    restore = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=900)
    assert journal(vm, run_id(restore.stdout))["status"] == "complete"
    assert not package_installed(vm)
    assert package_inventory(vm) == baseline_packages
    assert f"{pilot_id}\tabsent\tcandidate" in vm.ride("status", pilot_id).stdout
    duplicate = vm.ride("restore", "--run-id", first_id, "--allow-candidate", check=False)
    assert duplicate.returncode != 0 and "already been restored" in duplicate.stderr

    installed = vm.ride("install", pilot_id, "--allow-candidate", timeout=900)
    assert journal(vm, run_id(installed.stdout))["status"] == "complete"
    removed = vm.ride("remove", pilot_id, "--allow-candidate", timeout=900)
    assert journal(vm, run_id(removed.stdout))["status"] == "complete"
    assert not package_installed(vm)
    assert package_inventory(vm) == baseline_packages


def test_partial_failure_records_completed_step_and_can_restore(vm):
    pilot_id = vm.target["pilotOperation"]
    assert not package_installed(vm), "pilot package must be absent in the verified base image"
    baseline_packages = package_inventory(vm)
    missing_id = "package.ride-acceptance-missing"
    catalog = copy.deepcopy(CATALOG)
    missing = copy.deepcopy(next(item for item in catalog["operations"] if item["id"] == pilot_id))
    missing.update({
        "id": missing_id, "name": "Deliberately missing acceptance package",
        "description": "Test-only missing package, never published as an operation.",
        "packageName": "ride-acceptance-package-that-does-not-exist",
        "productId": "ride-acceptance-missing",
        "productUri": "https://example.org/ride-acceptance-missing",
        "sourceUri": "https://example.org/ride-acceptance-missing",
        "licenseUri": "https://example.org/ride-acceptance-missing",
    })
    catalog["operations"].append(missing)
    guest_catalog = vm.put_json("failure-catalog", catalog)
    guest_profile = vm.put_json("failure-profile", profile(pilot_id, missing_id))

    failed = vm.ride("apply", "--profile", guest_profile, "--allow-candidate",
                     catalog=guest_catalog, timeout=900, check=False)
    assert failed.returncode != 0, failed.stdout
    record = journal(vm, run_id(failed.stdout))
    assert record["status"] == "failed"
    assert [(step["id"], step["result"]) for step in record["steps"]] == [
        (pilot_id, "changed"), (missing_id, "failed")]
    assert package_installed(vm)

    restored = vm.ride("restore", "--run-id", record["runId"], "--allow-candidate",
                       catalog=guest_catalog, timeout=900)
    assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    assert not package_installed(vm)
    assert package_inventory(vm) == baseline_packages
