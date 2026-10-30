"""Real package lifecycle contract, initially exercised on Fedora Cloud Base."""

import copy
import json
from pathlib import Path
import re

import pytest


ROOT = Path(__file__).resolve().parents[2]
CATALOG = json.loads((ROOT / "catalog" / "operations.json").read_text(encoding="utf-8"))
RUN_ID = re.compile(r"^Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)$", re.MULTILINE)


def catalog_status(identifier):
    return next(item["status"] for item in CATALOG["operations"] if item["id"] == identifier)


def candidate_args(identifier):
    return ("--allow-candidate",) if catalog_status(identifier) == "candidate" else ()


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
    assert table_row(planned.stdout, pilot_id)["STATUS"] == catalog_status(pilot_id)

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
            "installed", "installed", catalog_status(pilot_id))
    prepare_absent_package(vm)
    baseline_packages = package_inventory(vm)

    plan = vm.ride("plan", "--profile", guest_profile)
    plan_row = table_row(plan.stdout, pilot_id)
    assert (plan_row["CURRENT"], plan_row["DESIRED"], plan_row["STATUS"]) == (
        "absent", "installed", catalog_status(pilot_id))
    assert not package_installed(vm)
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0

    first = vm.ride("apply", "--profile", guest_profile, *candidate_args(pilot_id), timeout=900)
    first_id = run_id(first.stdout)
    first_journal = journal(vm, first_id)
    assert first_journal["status"] == "complete"
    assert [(step["id"], step["observedBefore"], step["observedAfter"], step["result"])
            for step in first_journal["steps"]] == [(pilot_id, "absent", "installed", "changed")]
    assert package_installed(vm)
    installed_row = table_row(vm.ride("status", pilot_id).stdout, pilot_id)
    assert (installed_row["OBSERVED"], installed_row["STATUS"]) == (
        "installed", catalog_status(pilot_id))

    verify_installed_package(vm)

    repeat = vm.ride("apply", "--profile", guest_profile, *candidate_args(pilot_id), timeout=900)
    repeat_journal = journal(vm, run_id(repeat.stdout))
    assert repeat_journal["status"] == "complete"
    assert repeat_journal["steps"][0]["result"] == "unchanged"

    vm.ride("restore", "--run-id", first_id, "--dry-run")
    restore = vm.ride("restore", "--run-id", first_id, *candidate_args(pilot_id), timeout=900)
    assert journal(vm, run_id(restore.stdout))["status"] == "complete"
    assert not package_installed(vm)
    assert package_inventory(vm) == baseline_packages
    assert_ssh_server_available(vm)
    absent_row = table_row(vm.ride("status", pilot_id).stdout, pilot_id)
    assert (absent_row["OBSERVED"], absent_row["STATUS"]) == (
        "absent", catalog_status(pilot_id))
    duplicate = vm.ride("restore", "--run-id", first_id, *candidate_args(pilot_id), check=False)
    assert duplicate.returncode != 0 and "already been restored" in duplicate.stderr

    installed = vm.ride("install", pilot_id, *candidate_args(pilot_id), timeout=900)
    assert journal(vm, run_id(installed.stdout))["status"] == "complete"
    removed = vm.ride("remove", pilot_id, *candidate_args(pilot_id), timeout=900)
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
        "status": "candidate",
        "packageName": "ride-acceptance-package-that-does-not-exist",
        "productId": "ride-acceptance-missing",
        "productUri": "https://example.org/ride-acceptance-missing",
        "sourceUri": "https://example.org/ride-acceptance-missing",
        "licenseUri": "https://example.org/ride-acceptance-missing",
    })
    missing.pop("acceptanceEvidence", None)
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
        "installed", "installed", catalog_status(pilot_id))
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0

    for _ in range(2):
        result = vm.ride("apply", "--profile", guest_profile, *candidate_args(pilot_id))
        record = journal(vm, run_id(result.stdout))
        assert record["status"] == "complete"
        assert [(step["id"], step["observedBefore"], step["observedAfter"],
                 step["recovery"], step["result"]) for step in record["steps"]] == [
                     (pilot_id, "installed", "installed", "none", "unchanged")]

    status = table_row(vm.ride("status", pilot_id).stdout, pilot_id)
    assert (status["OBSERVED"], status["STATUS"]) == (
        "installed", catalog_status(pilot_id))
    verify_installed_package(vm)
    refused = vm.ride("remove", pilot_id, *candidate_args(pilot_id), check=False)
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
        "status": "candidate",
        "packageName": "ride-acceptance-package-that-does-not-exist",
        "productId": "ride-acceptance-missing",
        "productUri": "https://example.org/ride-acceptance-missing",
        "sourceUri": "https://example.org/ride-acceptance-missing",
        "licenseUri": "https://example.org/ride-acceptance-missing",
    })
    missing.pop("acceptanceEvidence", None)
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
    repeat = vm.ride("apply", "--profile", single_profile, *candidate_args(pilot_id))
    assert journal(vm, run_id(repeat.stdout))["steps"][0]["result"] == "unchanged"
    status = table_row(vm.ride("status", pilot_id).stdout, pilot_id)
    assert (status["OBSERVED"], status["STATUS"]) == (
        "installed", catalog_status(pilot_id))
    baseline_packages = package_inventory(vm)
    baseline_config = vm.run("sha256sum /etc/ssh/ssh_config").stdout

    refused = vm.ride("restore", "--run-id", record["runId"], "--allow-candidate",
                      catalog=guest_catalog, check=False)
    assert refused.returncode != 0 and "exact recovery is unavailable" in refused.stderr
    refused = vm.ride("remove", pilot_id, *candidate_args(pilot_id), check=False)
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
            "installed", "installed", catalog_status(identifier))
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0

    applied = vm.ride("apply", "--profile", profile_name)
    record = journal(vm, run_id(applied.stdout))
    assert record["status"] == "complete"
    assert [(step["id"], step["result"]) for step in record["steps"]] == [
        (identifier, "unchanged") for identifier in selected]
    for identifier in selected:
        status = table_row(vm.ride("status", identifier).stdout, identifier)
        assert (status["OBSERVED"], status["STATUS"]) == (
            "installed", catalog_status(identifier))
    assert package_inventory(vm) == baseline_packages
    assert vm.run("sha256sum /etc/ssh/ssh_config").stdout == baseline_ssh_config
    vm.run("rpm -q --quiet openssh-server && systemctl is-active --quiet sshd")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_workstation_default_profile_smoke(vm):
    profile_smoke(vm, "default", ("package.less", "package.openssh-clients", "package.exfatprogs"))


@pytest.mark.vm_target("fedora-44-server-x86_64")
def test_server_base_profile_smoke(vm):
    profile_smoke(vm, "server-base", ("package.less", "package.openssh-clients"))


def native_rpm_batch(vm, packages, allowed_residuals=None, installed_probes=None,
                     residue_candidates=(), inventory_policy="strict"):
    """Check each package in one disposable Workstation overlay."""
    assert inventory_policy in ("strict", "name-arch")
    allowed_residuals = allowed_residuals or {}
    installed_probes = installed_probes or {}
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    for package in packages:
        before = set(package_inventory(vm).splitlines())
        identifier = f"package.{package}"
        expected_status = catalog_status(identifier)
        assert vm.run(f"rpm -q --quiet {package}", check=False).returncode != 0, (
            f"{package} is preinstalled; review the removal transaction before retrying")
        guest_profile = vm.put_json(f"cli-{package}", profile(identifier))
        planned = table_row(vm.ride("plan", "--profile", guest_profile).stdout, identifier)
        assert (planned["CURRENT"], planned["DESIRED"], planned["STATUS"]) == (
            "absent", "installed", expected_status)
        assert set(package_inventory(vm).splitlines()) == before

        applied = vm.ride("apply", "--profile", guest_profile, *candidate_args(identifier), timeout=900)
        first_id = run_id(applied.stdout)
        record = journal(vm, first_id)
        assert record["status"] == "complete"
        assert [(step["id"], step["result"]) for step in record["steps"]] == [(identifier, "changed")]
        assert vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
        introduced = set(package_inventory(vm).splitlines()) - before

        def recovered():
            after = set(package_inventory(vm).splitlines())
            if inventory_policy == "name-arch":
                def identity(line):
                    fields = line.split("\t")
                    return (fields[0], fields[4])

                before_names = {identity(line) for line in before}
                after_names = {identity(line) for line in after}
                assert before_names <= after_names, (
                    f"pre-existing RPM identities lost: {sorted(before_names - after_names)}")
                residue_names = after_names - before_names
                introduced_names = {identity(line) for line in introduced}
                if package in residue_candidates:
                    assert residue_names <= introduced_names, (
                        f"unrelated RPM residue: {sorted(residue_names - introduced_names)}")
                else:
                    assert {name for name, _ in residue_names} == set(allowed_residuals.get(package, ()))
                changed = {identity(line) for line in before - after} & after_names
                print(f"{package} retained dependencies: {sorted(residue_names)}; "
                      f"updated RPMs: {sorted(changed)}")
                return
            assert not (before - after), f"pre-existing RPMs lost or changed: {sorted(before - after)}"
            residue = after - before
            if package in residue_candidates:
                assert residue <= introduced, f"unrelated RPM residue: {sorted(residue - introduced)}"
                print(f"{package} retained dependencies: {sorted(residue)}")
            else:
                added = {line.split("\t", 1)[0] for line in residue}
                assert added == set(allowed_residuals.get(package, ())), (
                    f"unexpected RPM residue after {package}: {sorted(added)}")

        signatures = vm.run(
            f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        vm.run(f"rpm -V {package}")
        if package in installed_probes:
            vm.run(installed_probes[package])
        status = table_row(vm.ride("status", identifier).stdout, identifier)
        assert (status["OBSERVED"], status["STATUS"]) == ("installed", expected_status)

        repeated = vm.ride("apply", "--profile", guest_profile, *candidate_args(identifier))
        assert journal(vm, run_id(repeated.stdout))["steps"][0]["result"] == "unchanged"
        restored = vm.ride("restore", "--run-id", first_id, *candidate_args(identifier), timeout=900)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
        assert vm.run(f"rpm -q --quiet {package}", check=False).returncode != 0
        recovered()

        installed = vm.ride("install", identifier, *candidate_args(identifier), timeout=900)
        assert journal(vm, run_id(installed.stdout))["status"] == "complete"
        removed = vm.ride("remove", identifier, *candidate_args(identifier), timeout=900)
        assert journal(vm, run_id(removed.stdout))["status"] == "complete"
        assert vm.run(f"rpm -q --quiet {package}", check=False).returncode != 0
        recovered()


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_native_cli_tools_batch(vm):
    native_rpm_batch(vm, ("pwgen", "htop", "bat", "ncdu", "ripgrep", "fd-find"))


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_native_forensic_and_package_tools_batch(vm):
    # The pinned image predates Fedora 44 RPM updates required by alien. Refresh
    # only this disposable overlay before taking the recovery inventory baseline.
    vm.run("sudo dnf -y upgrade --refresh", timeout=1800)
    native_rpm_batch(vm, ("libewf", "exif", "md5deep", "alien"),
                     {"alien": ("systemd-rpm-macros",)})


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_native_active_workstation_applications_batch(vm):
    # Compare recovery against the same refreshed package baseline used for
    # the dependency-heavy publisher RPM in the preceding native batch.
    vm.run("sudo dnf -y upgrade --refresh", timeout=1800)
    native_rpm_batch(vm, ("hexchat", "speedtest-cli", "chromium"),
                     installed_probes={"hexchat": "hexchat --version",
                                       "speedtest-cli": "speedtest-cli --version",
                                       "chromium": "chromium-browser --version"},
                     residue_candidates=("hexchat", "chromium"))


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_native_chromium_probe_and_lifecycle(vm):
    # Reuse the preceding HexChat and Speedtest CLI lifecycle transcript after
    # their passing checks; only Chromium's Fedora launcher name needed repair.
    vm.run("sudo dnf -y upgrade --refresh", timeout=1800)
    native_rpm_batch(vm, ("chromium",),
                     installed_probes={"chromium": "chromium-browser --version"},
                     residue_candidates=("chromium",))


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_native_forensic_and_desktop_applications_batch(vm):
    vm.run("sudo dnf -y upgrade --refresh", timeout=1800)
    native_rpm_batch(vm, ("dc3dd", "qbittorrent", "thunderbird", "flameshot", "gimp"),
                     installed_probes={"dc3dd": "dc3dd --version",
                                       **desktop_launcher_probes()},
                     residue_candidates=("qbittorrent", "thunderbird", "flameshot", "gimp"))


def desktop_launcher_probes():
    return {package: f"rpm -ql {package} | grep -qE '/usr/share/applications/.*\\.desktop$'"
            for package in ("qbittorrent", "thunderbird", "flameshot", "gimp")}


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_native_desktop_applications_lifecycle(vm):
    # The preceding dc3dd checks passed; graphical apps use Fedora launcher
    # files as their package happy-path probe without requiring a GUI session.
    vm.run("sudo dnf -y upgrade --refresh", timeout=1800)
    native_rpm_batch(vm, ("qbittorrent", "thunderbird", "flameshot", "gimp"),
                     installed_probes=desktop_launcher_probes(),
                     residue_candidates=("qbittorrent", "thunderbird", "flameshot", "gimp"))


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_remaining_native_repository_batch(vm):
    # DNF may update signed system RPMs while installing a new package. This
    # batch records those updates and gates the declared named-package inverse.
    packages = ("libpst", "lynis", "dia", "wine", "vlc")
    launcher = "rpm -ql {package} | grep -qE '/usr/share/applications/.*\\.desktop$'"
    native_rpm_batch(vm, packages, inventory_policy="name-arch", residue_candidates=packages,
                     installed_probes={"libpst": "command -v readpst",
                                       "lynis": "command -v lynis",
                                       "dia": launcher.format(package="dia"),
                                       "wine": "command -v wine",
                                       "vlc": launcher.format(package="vlc")})


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_provider_shell_tools_batch_and_profile(vm):
    packages = ("pv", "strace")
    native_rpm_batch(vm, packages, inventory_policy="name-arch",
                     residue_candidates=packages,
                     installed_probes={package: f"command -v {package}" for package in packages})

    identifiers = tuple(f"package.{package}" for package in packages)
    planned = vm.ride("plan", "--profile", "shell-tools")
    assert [line.split("\t", 1)[0] for line in planned.stdout.splitlines()[1:]] == list(identifiers)
    for identifier in identifiers:
        row = table_row(planned.stdout, identifier)
        assert (row["CURRENT"], row["DESIRED"], row["STATUS"]) == (
            "absent", "installed", catalog_status(identifier))
    before = set(package_inventory(vm).splitlines())
    applied = vm.ride("apply", "--profile", "shell-tools", *candidate_args(identifiers[0]))
    first_id = run_id(applied.stdout)
    assert [(step["id"], step["result"]) for step in journal(vm, first_id)["steps"]] == [
        (identifier, "changed") for identifier in identifiers]
    for package in packages:
        assert vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
    installed = set(package_inventory(vm).splitlines())
    repeated = vm.ride("apply", "--profile", "shell-tools", *candidate_args(identifiers[0]))
    assert [step["result"] for step in journal(vm, run_id(repeated.stdout))["steps"]] == [
        "unchanged", "unchanged"]
    restored = vm.ride("restore", "--run-id", first_id, *candidate_args(identifiers[0]))
    assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    for package in packages:
        assert vm.run(f"rpm -q --quiet {package}", check=False).returncode != 0
    after = set(package_inventory(vm).splitlines())
    def identities(lines):
        return {(fields[0], fields[4]) for line in lines if (fields := line.split("\t"))}
    assert identities(before) <= identities(after), "profile restore lost a pre-existing RPM identity"
    assert identities(after) - identities(before) <= identities(installed) - identities(before), (
        "profile restore left unrelated RPMs")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_provider_kernel_and_python_packages_batch(vm):
    # DNF5 and its plugins replace the old dnf-utils bundle. Verify actual
    # commands on the declared VM without changing repository configuration.
    vm.run("rpm -q --quiet dnf5 dnf5-plugins")
    vm.run("dnf5 config-manager --help")
    vm.run("dnf5 download --help")
    packages = ("kernel-devel", "kernel-headers", "python3-pip")
    native_rpm_batch(vm, packages, inventory_policy="name-arch",
                     residue_candidates=packages,
                     installed_probes={"kernel-devel": "uname -r && rpm -q kernel-devel",
                                       "kernel-headers": "rpm -q kernel-headers",
                                       "python3-pip": "python3 -m pip --version"})


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_provider_archive_replacement_batch(vm):
    # The pinned Workstation image includes 7zip. Create an absent baseline
    # only after proving the preparation removes no other pre-existing RPM.
    before = set(package_inventory(vm).splitlines())
    assert vm.run("rpm -q --quiet 7zip", check=False).returncode == 0
    vm.run("sudo dnf remove -y 7zip", timeout=900)
    after = set(package_inventory(vm).splitlines())
    assert {line.split("\t", 1)[0] for line in before - after} == {"7zip"}
    assert not (after - before), "preparation changed unrelated RPMs"
    native_rpm_batch(vm, ("7zip", "unar"), inventory_policy="name-arch",
                     residue_candidates=("7zip", "unar"),
                     installed_probes={"7zip": "command -v 7z",
                                       "unar": "command -v unar"})


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_provider_editors_and_gnome_utilities_batch(vm):
    vm.run("rpm -q --quiet dnf5")
    vm.run("dnf5 versionlock --help")
    before = set(package_inventory(vm).splitlines())
    assert vm.run("rpm -q --quiet nano", check=False).returncode == 0
    vm.run("sudo dnf remove -y nano", timeout=900)
    after = set(package_inventory(vm).splitlines())
    assert {line.split("\t", 1)[0] for line in before - after} == {
        "nano", "nano-default-editor", "default-editor"}
    assert not (after - before), "editor preparation changed unrelated RPMs"

    packages = ("nano", "vim-enhanced", "system-config-printer", "gnome-tweaks")
    launcher = "rpm -ql {package} | grep -qE '/usr/share/applications/.*\\.desktop$'"
    native_rpm_batch(vm, packages, inventory_policy="name-arch",
                     residue_candidates=packages,
                     installed_probes={"nano": "command -v nano",
                                       "vim-enhanced": "command -v vim",
                                       "system-config-printer": launcher.format(package="system-config-printer"),
                                       "gnome-tweaks": launcher.format(package="gnome-tweaks")})


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_provider_eza_fedora_package(vm):
    # The v2 GitHub ZIP uses /usr/local/bin; the Fedora RPM must leave that
    # destination outside its install and inverse contract.
    vm.run("test ! -e /usr/local/bin/eza")
    native_rpm_batch(vm, ("eza",), inventory_policy="name-arch",
                     residue_candidates=("eza",),
                     installed_probes={"eza": "test -x /usr/bin/eza && /usr/bin/eza --version"})
    vm.run("test ! -e /usr/local/bin/eza")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_native_cli_tools_supported_profile_smoke(vm):
    identifiers = tuple(f"package.{name}" for name in
                        ("pwgen", "htop", "bat", "ncdu", "ripgrep", "fd-find"))
    assert all(catalog_status(identifier) == "supported" for identifier in identifiers)
    baseline = package_inventory(vm)
    plan = vm.ride("plan", "--profile", "cli-tools")
    assert [line.split("\t", 1)[0] for line in plan.stdout.splitlines()[1:]] == list(identifiers)
    for identifier in identifiers:
        row = table_row(plan.stdout, identifier)
        assert (row["CURRENT"], row["DESIRED"], row["STATUS"]) == (
            "absent", "installed", "supported")
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0

    applied = vm.ride("apply", "--profile", "cli-tools", timeout=900)
    first_id = run_id(applied.stdout)
    record = journal(vm, first_id)
    assert record["status"] == "complete"
    assert [(step["id"], step["result"]) for step in record["steps"]] == [
        (identifier, "changed") for identifier in identifiers]
    repeat = vm.ride("apply", "--profile", "cli-tools", timeout=900)
    assert [step["result"] for step in journal(vm, run_id(repeat.stdout))["steps"]] == [
        "unchanged"] * len(identifiers)
    for identifier in identifiers:
        row = table_row(vm.ride("status", identifier).stdout, identifier)
        assert (row["OBSERVED"], row["STATUS"]) == ("installed", "supported")
    restored = vm.ride("restore", "--run-id", first_id, timeout=900)
    assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    assert package_inventory(vm) == baseline
