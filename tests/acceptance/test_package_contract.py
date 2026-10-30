"""Real package lifecycle contract, initially exercised on Fedora Cloud Base."""

import copy
import json
from pathlib import Path
import re

import pytest


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


def table_row(output, identifier):
    rows = [line.split("\t") for line in output.splitlines()]
    assert rows, output
    header, *data = rows
    matches = [dict(zip(header, row, strict=True)) for row in data if row[0] == identifier]
    assert len(matches) == 1, output
    return matches[0]


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


def assert_ssh_server_available(vm):
    if vm.target["pilotPackage"] == "openssh-clients":
        vm.run("rpm -q --quiet openssh-server")
        vm.run("systemctl is-active --quiet sshd")


def prepare_absent_package(vm):
    """Create an absent-state pilot in this scenario's disposable overlay."""
    assert_ssh_server_available(vm)
    if not package_installed(vm):
        return False
    if vm.target["packageDatabase"] != "rpm":
        raise AssertionError("preinstalled package preparation needs a target-specific remover")
    vm.run(f"sudo dnf -y remove {vm.target['pilotPackage']}", timeout=900)
    assert not package_installed(vm)
    assert_ssh_server_available(vm)
    return True


def verify_installed_package(vm):
    package = vm.target["pilotPackage"]
    if vm.target["packageVerification"] == "rpm-signature-and-files":
        signatures = vm.run(
            f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        vm.run(f"rpm -V {package}")
        if package == "openssh-clients":
            version = vm.run("ssh -V")
            assert "OpenSSH_" in version.stderr
            vm.run("test -f /etc/ssh/ssh_config")
            assert_ssh_server_available(vm)
        return
    raise AssertionError(f"package verifier is not implemented: {vm.target['packageVerification']}")


def test_guest_variant_scope_matches_catalog(vm):
    pilot_id = vm.target["pilotOperation"]
    row = next(item for item in CATALOG["operations"] if item["id"] == pilot_id)
    assert vm.target["variantId"] in row["targets"][vm.target["distro"]]["variantIds"]
    guest_profile = vm.put_json("variant-profile", profile(pilot_id))
    planned = vm.ride("plan", "--profile", guest_profile)
    assert table_row(planned.stdout, pilot_id)["STATUS"] == "candidate"

    unsupported = copy.deepcopy(CATALOG)
    selected = next(item for item in unsupported["operations"] if item["id"] == pilot_id)
    selected["targets"][vm.target["distro"]]["variantIds"] = ["other-edition"]
    unsupported["operations"] = [selected]
    guest_catalog = vm.put_json("unsupported-variant-catalog", unsupported)
    refused = vm.ride("plan", "--profile", guest_profile, catalog=guest_catalog, check=False)
    assert refused.returncode != 0 and "operation is not declared" in refused.stderr
    shown = json.loads(vm.ride("show", pilot_id, catalog=guest_catalog).stdout)
    assert shown["observedState"] == "unsupported"
    assert table_row(vm.ride("status", catalog=guest_catalog).stdout, pilot_id)["OBSERVED"] == "unsupported"
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0


@pytest.mark.recovery("remove-new-install")
def test_package_apply_repeat_status_restore_and_remove(vm):
    pilot_id = vm.target["pilotOperation"]
    guest_profile = vm.put_json("pilot-profile", profile(pilot_id))
    if package_installed(vm):
        original_plan = vm.ride("plan", "--profile", guest_profile)
        original_row = table_row(original_plan.stdout, pilot_id)
        assert (original_row["CURRENT"], original_row["DESIRED"], original_row["STATUS"]) == (
            "installed", "installed", "candidate")
    prepare_absent_package(vm)
    baseline_packages = package_inventory(vm)

    plan = vm.ride("plan", "--profile", guest_profile)
    plan_row = table_row(plan.stdout, pilot_id)
    assert (plan_row["CURRENT"], plan_row["DESIRED"], plan_row["STATUS"]) == (
        "absent", "installed", "candidate")
    assert not package_installed(vm)
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0

    first = vm.ride("apply", "--profile", guest_profile, "--allow-candidate", timeout=900)
    first_id = run_id(first.stdout)
    first_journal = journal(vm, first_id)
    assert first_journal["status"] == "complete"
    assert [(step["id"], step["observedBefore"], step["observedAfter"], step["result"])
            for step in first_journal["steps"]] == [(pilot_id, "absent", "installed", "changed")]
    assert package_installed(vm)
    installed_row = table_row(vm.ride("status", pilot_id).stdout, pilot_id)
    assert (installed_row["OBSERVED"], installed_row["STATUS"]) == ("installed", "candidate")

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
    assert_ssh_server_available(vm)
    absent_row = table_row(vm.ride("status", pilot_id).stdout, pilot_id)
    assert (absent_row["OBSERVED"], absent_row["STATUS"]) == ("absent", "candidate")
    duplicate = vm.ride("restore", "--run-id", first_id, "--allow-candidate", check=False)
    assert duplicate.returncode != 0 and "already been restored" in duplicate.stderr

    installed = vm.ride("install", pilot_id, "--allow-candidate", timeout=900)
    assert journal(vm, run_id(installed.stdout))["status"] == "complete"
    removed = vm.ride("remove", pilot_id, "--allow-candidate", timeout=900)
    assert journal(vm, run_id(removed.stdout))["status"] == "complete"
    assert not package_installed(vm)
    assert package_inventory(vm) == baseline_packages
    assert_ssh_server_available(vm)


@pytest.mark.recovery("remove-new-install")
def test_partial_failure_records_completed_step_and_can_restore(vm):
    pilot_id = vm.target["pilotOperation"]
    prepare_absent_package(vm)
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
    assert_ssh_server_available(vm)


@pytest.mark.recovery("none")
def test_installed_only_package_keeps_existing_client_and_server(vm):
    pilot_id = vm.target["pilotOperation"]
    assert pilot_id == "package.openssh-clients"
    assert package_installed(vm)
    assert_ssh_server_available(vm)
    baseline_packages = package_inventory(vm)
    baseline_config = vm.run("sha256sum /etc/ssh/ssh_config").stdout
    guest_profile = vm.put_json("installed-only-profile", profile(pilot_id))

    plan = vm.ride("plan", "--profile", guest_profile)
    row = table_row(plan.stdout, pilot_id)
    assert (row["CURRENT"], row["DESIRED"], row["STATUS"]) == (
        "installed", "installed", "candidate")
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0

    for _ in range(2):
        result = vm.ride("apply", "--profile", guest_profile, "--allow-candidate")
        record = journal(vm, run_id(result.stdout))
        assert record["status"] == "complete"
        assert [(step["id"], step["observedBefore"], step["observedAfter"],
                 step["recovery"], step["result"]) for step in record["steps"]] == [
                     (pilot_id, "installed", "installed", "none", "unchanged")]

    status = table_row(vm.ride("status", pilot_id).stdout, pilot_id)
    assert (status["OBSERVED"], status["STATUS"]) == ("installed", "candidate")
    verify_installed_package(vm)
    refused = vm.ride("remove", pilot_id, "--allow-candidate", check=False)
    assert refused.returncode != 0 and "invalid state absent" in refused.stderr
    assert package_inventory(vm) == baseline_packages
    assert vm.run("sha256sum /etc/ssh/ssh_config").stdout == baseline_config
    assert_ssh_server_available(vm)


@pytest.mark.recovery("none")
def test_installed_only_package_repairs_absence_and_refuses_inverse(vm):
    pilot_id = vm.target["pilotOperation"]
    assert pilot_id == "package.openssh-clients"
    assert package_installed(vm)
    assert_ssh_server_available(vm)
    vm.run("sudo rpm -e --nodeps openssh-clients")
    assert not package_installed(vm)
    if vm.target["variantId"] == "workstation":
        vm.run("rpm -q --quiet gcr gnome-shell openssh-server")
    else:
        vm.run("rpm -q --quiet openssh-server")
    assert_ssh_server_available(vm)

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
    guest_catalog = vm.put_json("installed-only-failure-catalog", catalog)
    guest_profile = vm.put_json("installed-only-failure-profile", profile(pilot_id, missing_id))

    failed = vm.ride("apply", "--profile", guest_profile, "--allow-candidate",
                     catalog=guest_catalog, timeout=900, check=False)
    assert failed.returncode != 0, failed.stdout
    record = journal(vm, run_id(failed.stdout))
    assert record["status"] == "failed"
    assert [(step["id"], step["observedBefore"], step["result"], step["recovery"])
            for step in record["steps"]] == [
                (pilot_id, "absent", "changed", "none"),
                (missing_id, "absent", "failed", "none")]
    assert package_installed(vm)
    vm.run("sudo dnf check", timeout=900)
    verify_installed_package(vm)

    single_profile = vm.put_json("installed-only-single-profile", profile(pilot_id))
    repeat = vm.ride("apply", "--profile", single_profile, "--allow-candidate")
    assert journal(vm, run_id(repeat.stdout))["steps"][0]["result"] == "unchanged"
    status = table_row(vm.ride("status", pilot_id).stdout, pilot_id)
    assert (status["OBSERVED"], status["STATUS"]) == ("installed", "candidate")
    baseline_packages = package_inventory(vm)
    baseline_config = vm.run("sha256sum /etc/ssh/ssh_config").stdout

    refused = vm.ride("restore", "--run-id", record["runId"], "--allow-candidate",
                      catalog=guest_catalog, check=False)
    assert refused.returncode != 0 and "exact recovery is unavailable" in refused.stderr
    refused = vm.ride("remove", pilot_id, "--allow-candidate", check=False)
    assert refused.returncode != 0 and "invalid state absent" in refused.stderr
    assert package_inventory(vm) == baseline_packages
    assert vm.run("sha256sum /etc/ssh/ssh_config").stdout == baseline_config
    assert_ssh_server_available(vm)


def profile_smoke(vm, profile_name, selected):
    baseline_packages = package_inventory(vm)
    baseline_ssh_config = vm.run("sha256sum /etc/ssh/ssh_config").stdout
    planned = vm.ride("plan", "--profile", profile_name)
    assert [line.split("\t", 1)[0] for line in planned.stdout.splitlines()[1:]] == list(selected)
    for identifier in selected:
        row = table_row(planned.stdout, identifier)
        assert (row["CURRENT"], row["DESIRED"], row["STATUS"]) == (
            "installed", "installed", "candidate")
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0

    applied = vm.ride("apply", "--profile", profile_name, "--allow-candidate")
    record = journal(vm, run_id(applied.stdout))
    assert record["status"] == "complete"
    assert [(step["id"], step["result"]) for step in record["steps"]] == [
        (identifier, "unchanged") for identifier in selected]
    for identifier in selected:
        status = table_row(vm.ride("status", identifier).stdout, identifier)
        assert (status["OBSERVED"], status["STATUS"]) == ("installed", "candidate")
    assert package_inventory(vm) == baseline_packages
    assert vm.run("sha256sum /etc/ssh/ssh_config").stdout == baseline_ssh_config
    vm.run("rpm -q --quiet openssh-server && systemctl is-active --quiet sshd")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_workstation_default_profile_smoke(vm):
    profile_smoke(vm, "default", ("package.less", "package.openssh-clients", "package.exfatprogs"))


@pytest.mark.vm_target("fedora-44-server-x86_64")
def test_server_base_profile_smoke(vm):
    profile_smoke(vm, "server-base", ("package.less", "package.openssh-clients"))
