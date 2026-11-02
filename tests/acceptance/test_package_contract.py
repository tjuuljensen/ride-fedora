"""Real package lifecycle contract, initially exercised on Fedora Cloud Base."""

import copy
import json
from pathlib import Path
import re
import shlex

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


def run_journal_snapshot(vm):
    return vm.run(
        "sudo sh -c '[ ! -d /var/lib/ride-fedora/runs ] || "
        "find /var/lib/ride-fedora/runs -maxdepth 1 -type f -name \"*.json\" "
        "-printf \"%f\\n\" | sort'"
    ).stdout


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
    if vm.target["pilotPackage"] == "nano-default-editor":
        before = {(line.split("\t")[0], line.split("\t")[4])
                  for line in package_inventory(vm).splitlines()}
        vm.run("sudo dnf -y remove nano", timeout=900)
        after = {(line.split("\t")[0], line.split("\t")[4])
                 for line in package_inventory(vm).splitlines()}
        removed = before - after
        assert {name for name, _arch in removed} == {
            "nano", "nano-default-editor", "default-editor"
        }, f"editor preparation changed the expected three RPMs: {sorted(removed)}"
    else:
        vm.run(f"sudo dnf -y remove {vm.target['pilotPackage']}", timeout=900)
    assert not package_installed(vm)
    assert_ssh_server_available(vm)
    return True


def service_snapshot(vm, unit):
    active = vm.run(f"systemctl is-active {unit}", check=False)
    enabled = vm.run(f"systemctl is-enabled {unit}", check=False)
    return (active.returncode, active.stdout.strip(), enabled.returncode, enabled.stdout.strip())


def account_snapshot(vm, name):
    user = vm.run(f"getent passwd {name}", check=False)
    group = vm.run(f"getent group {name}", check=False)
    return {"user": user.stdout.strip() if user.returncode == 0 else None,
            "group": group.stdout.strip() if group.returncode == 0 else None}


def sysuser_snapshot(vm):
    return account_snapshot(vm, "ntp")


def assert_tripwire_removal_state(vm):
    generated = vm.run(
        "sudo sh -c 'for path in /etc/tripwire /var/lib/tripwire; do "
        "if [ -d \"$path\" ]; then find \"$path\" -type f "
        "\\( -name \"*.key\" -o -name \"*.twd\" \\); fi; done'"
    )
    assert not generated.stdout.strip(), generated.stdout
    hostname = vm.run("hostname").stdout.strip()
    saved_policy = vm.run("sudo grep '^HOSTNAME=' /etc/tripwire/twpol.txt.rpmsave").stdout.strip()
    assert saved_policy == f"HOSTNAME={hostname};", saved_policy
    owned = vm.run("rpm -qf --quiet /etc/tripwire/twpol.txt.rpmsave", check=False)
    assert owned.returncode != 0, "the RPM backup policy should remain unowned"


def firewall_snapshot(vm):
    return vm.run("sudo nft -j list ruleset").stdout


def verify_installed_package(vm):
    package = vm.target["pilotPackage"]
    if vm.target["packageVerification"] == "rpm-signature-and-files":
        signatures = vm.run(
            f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        if package == "HandBrake":
            assert any("e06f8ecdd651ff2e" in value.lower() for value in signatures), signatures
        if package == "tripwire":
            verify = vm.run(f"sudo rpm -V {package}", check=False)
            assert verify.returncode == 1 and verify.stdout.splitlines() == [
                "S.5....T.  c /etc/tripwire/twpol.txt"
            ], verify.stdout
            hostname = vm.run("hostname").stdout.strip()
            policy = vm.run("sudo grep '^HOSTNAME=' /etc/tripwire/twpol.txt").stdout.strip()
            assert policy == f"HOSTNAME={hostname};", policy
        else:
            vm.run(f"sudo rpm -V {package}")
        if package == "openssh-clients":
            version = vm.run("ssh -V")
            assert "OpenSSH_" in version.stderr
            vm.run("test -f /etc/ssh/ssh_config")
            assert_ssh_server_available(vm)
        if package == "scanmem":
            vm.run("test -x /usr/bin/scanmem")
        if package == "unhide":
            vm.run("test -x /usr/bin/unhide")
        if package == "gnome-browser-connector":
            vm.run("test -x /usr/bin/gnome-browser-connector-host")
            vm.run("test -f /usr/lib64/mozilla/native-messaging-hosts/org.gnome.browser_connector.json")
            vm.run("test -f /etc/chromium/native-messaging-hosts/org.gnome.browser_connector.json")
        if package == "gnome-browser-connector":
            vm.run("test -x /usr/bin/gnome-browser-connector-host")
            vm.run("test -f /usr/lib64/mozilla/native-messaging-hosts/org.gnome.browser_connector.json")
            vm.run("test -f /etc/chromium/native-messaging-hosts/org.gnome.browser_connector.json")
        if package == "tripwire":
            vm.run("test -x /usr/bin/tripwire")
            vm.run("sudo test -f /etc/tripwire/twcfg.txt")
            vm.run("sudo test -f /etc/tripwire/twpol.txt")
            generated = vm.run(
                r"sudo find /etc/tripwire /var/lib/tripwire -type f \( -name '*.key' -o -name '*.twd' \)",
                check=False,
            )
            assert generated.returncode in (0, 1) and not generated.stdout.strip(), generated.stdout
            daily = vm.run("test -f /etc/cron.daily/tripwire-check")
            assert daily.returncode == 0
        if package == "rats":
            vm.run("test -x /usr/bin/rats")
            files = vm.run("rpm -ql rats").stdout.splitlines()
            assert any(path.endswith(".xml") and "rats" in path for path in files), files
        if package == "usbsniff":
            for command in ("usb_capture", "usb_replay", "usb_detach", "usb_reset"):
                vm.run(f"test -x /usr/bin/{command}")
            files = vm.run("rpm -ql usbsniff").stdout.splitlines()
            assert {f"/usr/bin/{name}" for name in
                    ("usb_capture", "usb_replay", "usb_detach", "usb_reset")} <= set(files), files
        if package == "HandBrake":
            vm.run("test -x /usr/bin/HandBrakeCLI")
            version = vm.run("/usr/bin/HandBrakeCLI --version")
            assert "HandBrake" in version.stdout or "HandBrake" in version.stderr, version
        if package == "psad":
            vm.run("test -x /usr/bin/psad")
            vm.run("test -f /etc/psad/psad.conf")
            active = vm.run("systemctl is-active psad.service", check=False)
            assert active.returncode != 0 and active.stdout.strip() in ("inactive", "unknown"), active.stdout
            enabled = vm.run("systemctl is-enabled psad.service", check=False)
            assert enabled.returncode != 0 and enabled.stdout.strip() in ("disabled", "not-found"), enabled.stdout
        if package == "ntpsec":
            vm.run("test -x /usr/bin/ntpd")
            vm.run("test -x /usr/bin/ntpq")
            vm.run("test -f /etc/ntp.conf")
            active = vm.run("systemctl is-active ntpd.service", check=False)
            assert active.returncode != 0 and active.stdout.strip() in ("inactive", "unknown"), active.stdout
            enabled = vm.run("systemctl is-enabled ntpd.service", check=False)
            assert enabled.returncode != 0 and enabled.stdout.strip() in ("disabled", "not-found"), enabled.stdout
        if package == "nebula":
            vm.run("test -x /usr/bin/nebula")
            vm.run("test -f /etc/nebula/config.yml")
            active = vm.run("systemctl show -p ActiveState --value nebula.service")
            assert active.stdout.strip() == "inactive", active.stdout
            enabled = vm.run("systemctl is-enabled nebula.service", check=False)
            assert enabled.returncode in (0, 1) and enabled.stdout.strip() == "disabled", enabled.stdout
        if package == "nano-default-editor":
            vm.run("test -f /etc/profile.d/nano-default-editor.sh")
            vm.run("test -f /etc/profile.d/nano-default-editor.csh")
            vm.run("test -f /usr/share/fish/vendor_conf.d/nano-default-editor.fish")
            default_editor = vm.run(
                "env -u EDITOR bash -lc 'printf %s \"${EDITOR:-}\"'"
            )
            assert default_editor.stdout.strip() == "/usr/bin/nano", default_editor.stdout
            selected_editor = vm.run(
                "env EDITOR=vi bash -lc 'printf %s \"${EDITOR:-}\"'"
            )
            assert selected_editor.stdout.strip() == "vi", selected_editor.stdout
        if package in {"scanmem", "unhide", "nano-default-editor", "nebula", "ntpsec", "psad", "rats", "tripwire", "usbsniff", "HandBrake"}:
            vm.run(f"rpm -q --scripts {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            units = vm.run(
                f"rpm -ql {package} | grep -E '/systemd/system/'", check=False
            )
            assert units.returncode in (0, 1)
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
    if vm.target["pilotPackage"] == "HandBrake":
        # RPM Fusion trust and repository recovery are already accepted separately.
        vm.ride("apply", "--profile", "rpmfusion", "--allow-candidate", timeout=1200)
        repos = vm.run("dnf repolist --enabled").stdout
        assert "rpmfusion-free" in repos, repos
    extension_state_before = None
    if pilot_id == "package.gnome-browser-connector":
        extension_dir = "/home/ride-test/.local/share/gnome-shell/extensions/rideacceptance@example.test"
        vm.run(f"mkdir -p {shlex.quote(extension_dir)}")
        vm.run(f"printf 'pre-existing extension data\\n' > {shlex.quote(extension_dir + '/metadata.json')}")
        extension_state_before = vm.run(
            f"find {shlex.quote(extension_dir)} -type f -exec sha256sum {{}} + | sort"
        ).stdout
    prepare_absent_package(vm)
    baseline_packages = package_inventory(vm)
    expected_packages_after_cleanup = set(baseline_packages.splitlines())
    glances_user_config = None
    glances_firewall_ports = None
    if pilot_id == "package.glances":
        config_path = "/home/ride-test/.config/glances/glances.conf"
        vm.run("mkdir -p /home/ride-test/.config/glances")
        vm.run(f"printf '[global]\\n# RIDE acceptance seed\\n' > {shlex.quote(config_path)}")
        glances_user_config = vm.run(f"sha256sum {shlex.quote(config_path)}").stdout
        glances_firewall_ports = vm.run("sudo firewall-cmd --list-ports").stdout
    chronyd_before = service_snapshot(vm, "chronyd.service") if vm.target["pilotPackage"] == "ntpsec" else None
    ntp_user_before = sysuser_snapshot(vm) if vm.target["pilotPackage"] == "ntpsec" else None
    psad_firewall_before = firewall_snapshot(vm) if vm.target["pilotPackage"] == "psad" else None
    psad_user_before = account_snapshot(vm, "psad") if vm.target["pilotPackage"] == "psad" else None
    journals_before_plan = run_journal_snapshot(vm)

    plan = vm.ride("plan", "--profile", guest_profile)
    plan_row = table_row(plan.stdout, pilot_id)
    assert (plan_row["CURRENT"], plan_row["DESIRED"], plan_row["STATUS"]) == (
        "absent", "installed", catalog_status(pilot_id))
    assert not package_installed(vm)
    assert run_journal_snapshot(vm) == journals_before_plan

    if catalog_status(pilot_id) == "candidate":
        refused = vm.ride("apply", "--profile", guest_profile, check=False)
        assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
        assert run_journal_snapshot(vm) == journals_before_plan

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
    if pilot_id == "package.glances":
        vm.run("glances --version")
        stdout_smoke = vm.run(
            "PYTHONUNBUFFERED=1 timeout 20 glances --disable-process "
            "--stdout cpu.user,mem.used,load",
            check=False,
        )
        assert stdout_smoke.returncode == 124
        assert all(stat in stdout_smoke.stdout for stat in ("cpu.user:", "mem.used:", "load:"))
        assert vm.run("systemctl is-active glances.service", check=False).stdout.strip() != "active"
        assert vm.run("systemctl is-enabled glances.service", check=False).stdout.strip() != "enabled"
        assert vm.run("sudo firewall-cmd --list-ports").stdout == glances_firewall_ports
    if vm.target["pilotPackage"] == "HandBrake":
        installed_inventory = set(package_inventory(vm).splitlines())
        added = installed_inventory - set(baseline_packages.splitlines())
        expected_key = next((line for line in installed_inventory
                             if line.split("\t")[0] == "gpg-pubkey" and
                             line.split("\t")[2] ==
                             "e9a491a3de247814e7e067eae06f8ecdd651ff2e"), None)
        assert expected_key is not None, sorted(added)
        assert any(line.split("\t")[0] == "HandBrake" for line in added), sorted(added)
        expected_packages_after_cleanup.add(expected_key)
    if vm.target["pilotPackage"] == "ntpsec":
        assert service_snapshot(vm, "chronyd.service") == chronyd_before
        installed_packages = package_inventory(vm).splitlines()
        baseline_set = set(baseline_packages.splitlines())
        assert baseline_set.issubset(set(installed_packages)), "NTPsec transaction removed a pre-existing RPM"
    if vm.target["pilotPackage"] == "psad":
        assert firewall_snapshot(vm) == psad_firewall_before
        installed_packages = package_inventory(vm).splitlines()
        assert set(baseline_packages.splitlines()).issubset(set(installed_packages)), "PSAD transaction removed a pre-existing RPM"

    repeat = vm.ride("apply", "--profile", guest_profile, *candidate_args(pilot_id), timeout=900)
    repeat_journal = journal(vm, run_id(repeat.stdout))
    assert repeat_journal["status"] == "complete"
    assert repeat_journal["steps"][0]["result"] == "unchanged"

    vm.ride("restore", "--run-id", first_id, "--dry-run")
    restore = vm.ride("restore", "--run-id", first_id, *candidate_args(pilot_id), timeout=900)
    assert journal(vm, run_id(restore.stdout))["status"] == "complete"
    assert not package_installed(vm)
    assert set(package_inventory(vm).splitlines()) == expected_packages_after_cleanup
    if glances_user_config is not None:
        assert vm.run("sha256sum /home/ride-test/.config/glances/glances.conf").stdout == glances_user_config
    if vm.target["pilotPackage"] == "tripwire":
        assert_tripwire_removal_state(vm)
    if vm.target["pilotPackage"] == "ntpsec":
        assert service_snapshot(vm, "chronyd.service") == chronyd_before
        ntp_user_after_restore = sysuser_snapshot(vm)
        if ntp_user_before["user"] is None and ntp_user_after_restore["user"]:
            fields = ntp_user_after_restore["user"].split(":")
            assert len(fields) >= 7 and fields[6] in ("/usr/sbin/nologin", "/sbin/nologin"), ntp_user_after_restore
    if vm.target["pilotPackage"] == "psad":
        assert firewall_snapshot(vm) == psad_firewall_before
        psad_user_after_restore = account_snapshot(vm, "psad")
        if psad_user_before["user"] is None and psad_user_after_restore["user"]:
            fields = psad_user_after_restore["user"].split(":")
            assert len(fields) >= 7 and fields[6] in ("/usr/sbin/nologin", "/sbin/nologin"), psad_user_after_restore
    assert_ssh_server_available(vm)
    if extension_state_before is not None:
        extension_dir = "/home/ride-test/.local/share/gnome-shell/extensions/rideacceptance@example.test"
        assert vm.run(
            f"find {shlex.quote(extension_dir)} -type f -exec sha256sum {{}} + | sort"
        ).stdout == extension_state_before
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
    assert set(package_inventory(vm).splitlines()) == expected_packages_after_cleanup
    if vm.target["pilotPackage"] == "tripwire":
        assert_tripwire_removal_state(vm)
    if vm.target["pilotPackage"] == "ntpsec":
        assert service_snapshot(vm, "chronyd.service") == chronyd_before
        ntp_user_after_restore = sysuser_snapshot(vm)
        if ntp_user_before["user"] is None and ntp_user_after_restore["user"]:
            fields = ntp_user_after_restore["user"].split(":")
            assert len(fields) >= 7 and fields[6] in ("/usr/sbin/nologin", "/sbin/nologin"), ntp_user_after_restore
    if vm.target["pilotPackage"] == "psad":
        assert firewall_snapshot(vm) == psad_firewall_before
        psad_user_after_restore = account_snapshot(vm, "psad")
        if psad_user_before["user"] is None and psad_user_after_restore["user"]:
            fields = psad_user_after_restore["user"].split(":")
            assert len(fields) >= 7 and fields[6] in ("/usr/sbin/nologin", "/sbin/nologin"), psad_user_after_restore
    assert_ssh_server_available(vm)
    if extension_state_before is not None:
        extension_dir = "/home/ride-test/.local/share/gnome-shell/extensions/rideacceptance@example.test"
        assert vm.run(
            f"find {shlex.quote(extension_dir)} -type f -exec sha256sum {{}} + | sort"
        ).stdout == extension_state_before


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
    if vm.target["pilotPackage"] == "ntpsec":
        assert service_snapshot(vm, "chronyd.service") == chronyd_before
        ntp_user_after_restore = sysuser_snapshot(vm)
        if ntp_user_before["user"] is None and ntp_user_after_restore["user"]:
            fields = ntp_user_after_restore["user"].split(":")
            assert len(fields) >= 7 and fields[6] in ("/usr/sbin/nologin", "/sbin/nologin"), ntp_user_after_restore
    if vm.target["pilotPackage"] == "psad":
        assert firewall_snapshot(vm) == psad_firewall_before
        psad_user_after_restore = account_snapshot(vm, "psad")
        if psad_user_before["user"] is None and psad_user_after_restore["user"]:
            fields = psad_user_after_restore["user"].split(":")
            assert len(fields) >= 7 and fields[6] in ("/usr/sbin/nologin", "/sbin/nologin"), psad_user_after_restore
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
                     residue_candidates=(), inventory_policy="strict", identifiers=None):
    """Check each package in one disposable Workstation overlay."""
    assert inventory_policy in ("strict", "name-arch")
    allowed_residuals = allowed_residuals or {}
    installed_probes = installed_probes or {}
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    for package in packages:
        before = set(package_inventory(vm).splitlines())
        identifier = (identifiers or {}).get(package, f"package.{package}")
        expected_status = catalog_status(identifier)
        assert vm.run(f"rpm -q --quiet {package}", check=False).returncode != 0, (
            f"{package} is preinstalled; review the removal transaction before retrying")
        guest_profile = vm.put_json(f"cli-{package.lower()}", profile(identifier))
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
        vm.run(f"sudo rpm -V {package}")
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
def test_fedora_optional_codec_plugins_batch_and_profile(vm):
    packages = (
        "gstreamer1-plugins-bad-free-extras",
        "gstreamer1-plugins-bad-free-fluidsynth",
        "gstreamer1-plugins-bad-free-lv2",
        "gstreamer1-plugins-bad-free-wildmidi",
        "gstreamer1-plugins-bad-free-zbar",
        "lame",
    )
    identifiers = tuple(f"package.{package}" for package in packages)
    candidate = candidate_args(identifiers[0])
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    before = set(package_inventory(vm).splitlines())
    for package in packages:
        assert vm.run(f"rpm -q --quiet {package}", check=False).returncode != 0, (
            f"{package} is preinstalled; review the package inverse before retrying")
    planned = vm.ride("plan", "--profile", "fedora-codecs-optional", *candidate)
    assert [line.split("\t", 1)[0] for line in planned.stdout.splitlines()[1:]] == list(identifiers)
    applied = vm.ride("apply", "--profile", "fedora-codecs-optional", *candidate, timeout=1200)
    first_id = run_id(applied.stdout)
    record = journal(vm, first_id)
    assert record["status"] == "complete"
    assert [(step["id"], step["result"]) for step in record["steps"]] == [
        (identifier, "changed") for identifier in identifiers]
    installed_inventory = set(package_inventory(vm).splitlines())
    introduced = installed_inventory - before
    for package, identifier in zip(packages, identifiers, strict=True):
        assert vm.run(f"rpm -q --quiet {package}").returncode == 0
        signatures = vm.run(
            f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        vm.run(f"sudo rpm -V {package}")
        assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
    repeated = vm.ride("apply", "--profile", "fedora-codecs-optional", *candidate)
    assert all(step["result"] == "unchanged" for step in journal(vm, run_id(repeated.stdout))["steps"])
    removed = vm.ride("remove", "--profile", "fedora-codecs-optional", *candidate, timeout=1200)
    assert journal(vm, run_id(removed.stdout))["status"] == "complete"
    for package in packages:
        assert vm.run(f"rpm -q --quiet {package}", check=False).returncode != 0
    recovered = set(package_inventory(vm).splitlines())
    before_names = {(line.split("\t")[0], line.split("\t")[4]) for line in before}
    recovered_names = {(line.split("\t")[0], line.split("\t")[4]) for line in recovered}
    introduced_names = {(line.split("\t")[0], line.split("\t")[4]) for line in introduced}
    assert before_names <= recovered_names
    residual_names = recovered_names - before_names
    assert residual_names <= introduced_names, f"unrelated RPM residue: {sorted(residual_names - introduced_names)}"


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_good_codec_plugins_batch_and_profile(vm):
    packages = (
        "gstreamer1-plugins-good-extras",
        "gstreamer1-plugins-good-gtk",
        "gstreamer1-plugins-good-qt",
        "gstreamer1-plugins-good-qt6",
    )
    identifiers = tuple(f"package.{package}" for package in packages)
    candidate = candidate_args(identifiers[0])
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    before = set(package_inventory(vm).splitlines())
    baseline_installed = {
        package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
        for package in packages
    }
    planned = vm.ride("plan", "--profile", "fedora-codecs-good-plugins", *candidate)
    plan_rows = [line.split("\t") for line in planned.stdout.splitlines()[1:]]
    assert [row[0] for row in plan_rows] == list(identifiers)
    for package, row in zip(packages, plan_rows, strict=True):
        expected = "installed" if baseline_installed[package] else "absent"
        assert row[2:5] == [expected, "installed", catalog_status(f"package.{package}")]
    applied = vm.ride("apply", "--profile", "fedora-codecs-good-plugins", *candidate, timeout=1200)
    first_id = run_id(applied.stdout)
    record = journal(vm, first_id)
    assert record["status"] == "complete"
    assert [(step["id"], step["result"]) for step in record["steps"]] == [
        (identifier, "unchanged" if baseline_installed[package] else "changed")
        for package, identifier in zip(packages, identifiers, strict=True)]
    installed_inventory = set(package_inventory(vm).splitlines())
    introduced = installed_inventory - before
    for package, identifier in zip(packages, identifiers, strict=True):
        assert vm.run(f"rpm -q --quiet {package}").returncode == 0
        signatures = vm.run(
            f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        vm.run(f"sudo rpm -V {package}")
        assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
    repeated = vm.ride("apply", "--profile", "fedora-codecs-good-plugins", *candidate)
    assert all(step["result"] == "unchanged" for step in journal(vm, run_id(repeated.stdout))["steps"])
    removed = vm.ride("remove", "--profile", "fedora-codecs-good-plugins", *candidate, timeout=1200)
    assert journal(vm, run_id(removed.stdout))["status"] == "complete"
    for package, identifier in zip(packages, identifiers, strict=True):
        installed = vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
        if package in {"gstreamer1-plugins-good-gtk", "gstreamer1-plugins-good-qt6"}:
            assert installed, f"profile removal deleted one-way Workstation package {package}"
            assert f"kept one-way prerequisite {identifier}" in removed.stdout
        else:
            assert not installed, f"profile inverse left removable package {package} installed"
    recovered = set(package_inventory(vm).splitlines())
    before_names = {(line.split("\t")[0], line.split("\t")[4]) for line in before}
    recovered_names = {(line.split("\t")[0], line.split("\t")[4]) for line in recovered}
    introduced_names = {(line.split("\t")[0], line.split("\t")[4]) for line in introduced}
    assert before_names <= recovered_names
    residual_names = recovered_names - before_names
    assert residual_names <= introduced_names, f"unrelated RPM residue: {sorted(residual_names - introduced_names)}"


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_multimedia_group_gstreamer_batch_and_profile(vm):
    packages = (
        "gstreamer1-plugins-bad-free",
        "gstreamer1-plugins-good",
        "gstreamer1-plugin-dav1d",
        "gstreamer1-plugin-libav",
        "gstreamer1-plugin-openh264",
        "gstreamer1-plugins-ugly-free",
    )
    identifiers = tuple(f"package.{package}" for package in packages)
    candidate = candidate_args(identifiers[0])
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    before = set(package_inventory(vm).splitlines())
    baseline_installed = {
        package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
        for package in packages
    }
    assert all(baseline_installed.values()), (
        "Pinned Workstation Multimedia packages differ from the reviewed baseline; "
        "inspect the transcript before any apply."
    )
    planned = vm.ride("plan", "--profile", "fedora-codecs-multimedia-group", *candidate)
    plan_rows = [line.split("\t") for line in planned.stdout.splitlines()[1:]]
    assert [row[0] for row in plan_rows] == list(identifiers)
    assert all(row[2:5] == ["installed", "installed", catalog_status(row[0])]
               for row in plan_rows)
    applied = vm.ride("apply", "--profile", "fedora-codecs-multimedia-group", *candidate)
    record = journal(vm, run_id(applied.stdout))
    assert record["status"] == "complete"
    assert [(step["id"], step["result"]) for step in record["steps"]] == [
        (identifier, "unchanged") for identifier in identifiers]
    for package, identifier in zip(packages, identifiers, strict=True):
        assert vm.run(f"rpm -q --quiet {package}").returncode == 0
        signatures = vm.run(
            f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        vm.run(f"sudo rpm -V {package}")
        assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
    repeated = vm.ride("apply", "--profile", "fedora-codecs-multimedia-group", *candidate)
    assert all(step["result"] == "unchanged"
               for step in journal(vm, run_id(repeated.stdout))["steps"])
    removed = vm.ride("remove", "--profile", "fedora-codecs-multimedia-group", *candidate)
    assert journal(vm, run_id(removed.stdout))["status"] == "complete"
    for identifier in identifiers:
        assert f"kept one-way prerequisite {identifier}" in removed.stdout
    after = set(package_inventory(vm).splitlines())
    before_names = {(line.split("\t")[0], line.split("\t")[4]) for line in before}
    after_names = {(line.split("\t")[0], line.split("\t")[4]) for line in after}
    assert before_names <= after_names, "profile removal lost a pre-existing RPM identity"
    assert all(vm.run(f"rpm -q --quiet {package}").returncode == 0 for package in packages)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_multimedia_update_is_fixed_set_and_non_reversible(vm):
    package_names = (
        "PackageKit-gstreamer-plugin",
        "alsa-ucm",
        "alsa-utils",
        "gstreamer1-plugin-dav1d",
        "gstreamer1-plugin-libav",
        "gstreamer1-plugin-openh264",
        "gstreamer1-plugins-bad-free",
        "gstreamer1-plugins-good",
        "gstreamer1-plugins-ugly-free",
        "libva-intel-media-driver",
        "pipewire-alsa",
        "pipewire-gstreamer",
        "pipewire-pulseaudio",
        "pipewire-utils",
        "wireplumber",
        "gstreamer-plugins-espeak",
    )
    operation_id = "system.update-multimedia-codecs"
    candidate = candidate_args(operation_id)
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    before_inventory = package_inventory(vm).splitlines()
    before_names = {(line.split("\t")[0], line.split("\t")[4]) for line in before_inventory}
    baseline_names = {line.split("\t")[0] for line in before_inventory}
    installed = [package for package in package_names if package in baseline_names]
    assert installed, "the pinned Workstation image has no installed Multimedia group members"

    before_versions = {
        fields[0]: (fields[1], fields[2], fields[3])
        for line in before_inventory if (fields := line.split("\t"))
    }
    plan = vm.ride("plan", "--profile", "fedora-codecs-updates", *candidate,
                   timeout=300)
    assert f"{operation_id}\t-\t" in plan.stdout and "\tcurrent\t" in plan.stdout, plan.stdout
    applied = vm.ride("apply", "--profile", "fedora-codecs-updates", *candidate, timeout=1800)
    assert f"DNF5 transaction preview for {operation_id}:" in applied.stdout, applied.stdout
    assert "Upgrading:" in applied.stdout, applied.stdout
    first_id = run_id(applied.stdout)
    first_journal = journal(vm, first_id)
    assert first_journal["status"] == "complete"
    assert first_journal["steps"][0]["observedBefore"] == "outdated"
    assert first_journal["steps"][0]["observedAfter"] == "current"
    assert first_journal["steps"][0]["recovery"] == "none"

    after_inventory = package_inventory(vm).splitlines()
    after_names = {(line.split("\t")[0], line.split("\t")[4]) for line in after_inventory}
    assert before_names <= after_names, "DNF update removed a pre-existing RPM identity"
    after_versions = {
        fields[0]: (fields[1], fields[2], fields[3])
        for line in after_inventory if (fields := line.split("\t"))
    }
    changed_names = {
        name for name in before_versions.keys() & after_versions.keys()
        if before_versions[name] != after_versions[name]
    }
    assert changed_names & set(installed), (changed_names, installed)
    vm.run("sudo dnf5 history info last", timeout=300)
    for package in installed:
        if package in changed_names:
            vm.run(f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {shlex.quote(package)}")
            vm.run(f"rpm -V {shlex.quote(package)}")

    assert table_row(vm.ride("status", operation_id, *candidate, timeout=300).stdout,
                     operation_id)["OBSERVED"] == "current"
    repeated = vm.ride("apply", "--profile", "fedora-codecs-updates", *candidate,
                       timeout=1800)
    assert journal(vm, run_id(repeated.stdout))["steps"][0]["result"] == "unchanged"
    removed = vm.ride("remove", "--profile", "fedora-codecs-updates", *candidate)
    assert "kept non-reversible operation system.update-multimedia-codecs" in removed.stdout
    assert vm.ride("restore", "--run-id", first_id, *candidate, check=False).returncode != 0
    final_inventory = package_inventory(vm).splitlines()
    final_versions = {
        fields[0]: (fields[1], fields[2], fields[3])
        for line in final_inventory if (fields := line.split("\t"))
    }
    assert final_versions == after_versions, "profile removal or restore changed accepted package versions"


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_network_utilities_batch_and_profile(vm):
    packages = ("bmon", "fping", "iftop", "lnav", "nload")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-network-utilities"
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    before = package_inventory(vm).splitlines()
    before_names = {(line.split("\t")[0], line.split("\t")[4]) for line in before}
    initial = {
        package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
        for package in packages
    }
    planned = vm.ride("plan", "--profile", profile_id, timeout=300)
    assert "\tcandidate\t" in planned.stdout
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    rows = [line.split("\t") for line in planned.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        expected = "installed" if initial[package] else "absent"
        assert row[2:5] == [expected, "installed", "candidate"]

    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    record = journal(vm, first_id)
    assert record["status"] == "complete"
    assert [(step["id"], step["result"]) for step in record["steps"]] == [
        (identifier, "unchanged" if initial[package] else "changed")
        for package, identifier in zip(packages, identifiers, strict=True)]
    after = package_inventory(vm).splitlines()
    after_names = {(line.split("\t")[0], line.split("\t")[4]) for line in after}
    assert before_names <= after_names, "install transaction lost a pre-existing RPM identity"
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    assert changed_existing == {("python3-requests", "noarch")}, (
        f"unexpected existing RPM changes: {sorted(changed_existing)}")
    transaction_output = applied.stdout + applied.stderr
    assert "upgrading python3-requests" in transaction_output.lower()
    assert "2.32.5-5.fc44" in transaction_output and "2.33.1-1.fc44" in transaction_output
    introduced = set(after) - set(before)
    vm.run("sudo dnf5 history info last", timeout=300)
    probes = {"bmon": "bmon --help", "fping": "fping --help", "iftop": "iftop -h",
              "lnav": "lnav --help", "nload": "nload --help"}
    probe_markers = {"bmon": "Module configuration", "fping": "usage", "iftop": "usage",
                     "lnav": "lnav", "nload": "nload"}
    for package, identifier in zip(packages, identifiers, strict=True):
        vm.run(f"rpm -q --quiet {package}")
        signatures = vm.run(
            f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        vm.run(f"sudo rpm -V {package}")
        probe = vm.run(probes[package], check=False)
        probe_output = probe.stdout + probe.stderr
        assert probe.returncode in (0, 1) and probe_markers[package].lower() in probe_output.lower(), (
            f"{package} local help probe failed: {probe.returncode} {probe_output[:500]}")
        assert table_row(vm.ride("status", identifier, "--allow-candidate").stdout,
                         identifier)["OBSERVED"] == "installed"

    repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
    assert all(step["result"] == "unchanged"
               for step in journal(vm, run_id(repeated.stdout))["steps"])
    restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
    assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final_names = {(line.split("\t")[0], line.split("\t")[4])
                   for line in package_inventory(vm).splitlines()}
    assert before_names <= final_names, "restore lost a pre-existing RPM identity"
    final_inventory = package_inventory(vm).splitlines()
    final_by_key = {(line.split("\t")[0], line.split("\t")[4]): line
                    for line in final_inventory}
    assert {key for key, line in before_by_key.items()
            if key != ("python3-requests", "noarch") and final_by_key.get(key) != line} == set(), (
        "restore changed an existing RPM outside the recorded HTTPie dependency upgrade")
    assert final_by_key[("python3-requests", "noarch")] == after_by_key[("python3-requests", "noarch")]
    residual = set(final_inventory) - set(before)
    assert residual <= introduced, (
        f"restore left unrelated RPM identities: {sorted(residual - introduced)}")
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_network_clients_batch_and_profile(vm):
    packages = ("httpie", "iperf", "irssi", "socat")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-network-clients"
    before = package_inventory(vm).splitlines()
    before_names = {(line.split("\t")[0], line.split("\t")[4]) for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    planned = vm.ride("plan", "--profile", profile_id, timeout=300)
    assert "\tcandidate\t" in planned.stdout
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    rows = [line.split("\t") for line in planned.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        expected = "installed" if initial[package] else "absent"
        assert row[2:5] == [expected, "installed", "candidate"]
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    record = journal(vm, first_id)
    assert record["status"] == "complete"
    assert [(step["id"], step["result"]) for step in record["steps"]] == [
        (identifier, "unchanged" if initial[package] else "changed")
        for package, identifier in zip(packages, identifiers, strict=True)]
    after = package_inventory(vm).splitlines()
    after_names = {(line.split("\t")[0], line.split("\t")[4]) for line in after}
    assert before_names <= after_names, "install transaction lost a pre-existing RPM identity"
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    transaction_output = applied.stdout + applied.stderr
    for key in changed_existing:
        old_fields = before_by_key[key].split("\t")
        new_fields = after_by_key[key].split("\t")
        old_version = f"{old_fields[2]}-{old_fields[3]}"
        new_version = f"{new_fields[2]}-{new_fields[3]}"
        assert (key[0] in transaction_output and old_version in transaction_output and
                new_version in transaction_output and "replacing" in transaction_output.lower()), (
            f"DNF did not document exact dependency update for {key[0]}")
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    assert changed_existing == {("python3-requests", "noarch")}, (
        f"unexpected existing RPM changes: {sorted(changed_existing)}")
    transaction_output = applied.stdout + applied.stderr
    assert "upgrading python3-requests" in transaction_output.lower()
    assert "2.32.5-5.fc44" in transaction_output and "2.33.1-1.fc44" in transaction_output
    introduced = set(after) - set(before)
    probes = {"httpie": "http --help", "iperf": "iperf --help",
              "irssi": "irssi --help", "socat": "socat -h"}
    markers = {"httpie": "usage", "iperf": "usage", "irssi": "irssi",
               "socat": "usage"}
    for package, identifier in zip(packages, identifiers, strict=True):
        vm.run(f"rpm -q --quiet {package}")
        signatures = vm.run(
            f"rpm -q --qf '%{{SIGPGP:pgpsig}}\n%{{RSAHEADER:pgpsig}}\n' {package}"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        vm.run(f"sudo rpm -V {package}")
        probe = vm.run(probes[package], check=False)
        output = probe.stdout + probe.stderr
        valid_codes = {255} if package == "fpdns" else {0, 1}
        assert probe.returncode in valid_codes and markers[package].lower() in output.lower(), (
            f"{package} local help/version probe failed: {probe.returncode} {output[:500]}")
        assert table_row(vm.ride("status", identifier, "--allow-candidate").stdout,
                         identifier)["OBSERVED"] == "installed"
    vm.run("sudo dnf5 history info last", timeout=300)
    repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
    assert all(step["result"] == "unchanged"
               for step in journal(vm, run_id(repeated.stdout))["steps"])
    restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
    assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final_names = {(line.split("\t")[0], line.split("\t")[4])
                   for line in package_inventory(vm).splitlines()}
    assert before_names <= final_names, "restore lost a pre-existing RPM identity"
    final_inventory = package_inventory(vm).splitlines()
    final_by_key = {(line.split("\t")[0], line.split("\t")[4]): line
                    for line in final_inventory}
    assert {key for key, line in before_by_key.items()
            if key != ("python3-requests", "noarch") and final_by_key.get(key) != line} == set(), (
        "restore changed an existing RPM outside the recorded HTTPie dependency upgrade")
    assert final_by_key[("python3-requests", "noarch")] == after_by_key[("python3-requests", "noarch")]
    residual = set(final_inventory) - set(before)
    assert residual <= introduced, (
        f"restore left unrelated RPM identities: {sorted(residual - introduced)}")
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_dns_tools_batch_and_profile(vm):
    packages = ("dnsenum", "dnstracer", "dnstop", "fpdns")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-dns-tools"
    before = package_inventory(vm).splitlines()
    before_names = {(line.split("\t")[0], line.split("\t")[4]) for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    planned = vm.ride("plan", "--profile", profile_id, timeout=300)
    assert "\tcandidate\t" in planned.stdout
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    rows = [line.split("\t") for line in planned.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        expected = "installed" if initial[package] else "absent"
        assert row[2:5] == [expected, "installed", "candidate"]
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    record = journal(vm, first_id)
    assert record["status"] == "complete"
    assert [(step["id"], step["result"]) for step in record["steps"]] == [
        (identifier, "unchanged" if initial[package] else "changed")
        for package, identifier in zip(packages, identifiers, strict=True)]
    after = package_inventory(vm).splitlines()
    after_names = {(line.split("\t")[0], line.split("\t")[4]) for line in after}
    assert before_names <= after_names, "install transaction lost a pre-existing RPM identity"
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    expected_dependency_updates = {
        ("perl-Errno", "x86_64"), ("perl-interpreter", "x86_64"), ("perl-libs", "x86_64")}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    assert changed_existing == expected_dependency_updates, (
        f"unexpected existing RPM changes: {sorted(changed_existing)}")
    transaction_output = applied.stdout + applied.stderr
    for name, old_version, new_version in (
            ("perl-Errno", "1.38-523.fc44", "1.38-525.fc44"),
            ("perl-interpreter", "5.42.1-523.fc44", "5.42.3-525.fc44"),
            ("perl-libs", "5.42.1-523.fc44", "5.42.3-525.fc44")):
        assert name in transaction_output and old_version in transaction_output and new_version in transaction_output, (
            f"DNF transaction did not document {name} upgrade")
    introduced = set(after) - set(before)
    probes = {"dnsenum": "dnsenum --help", "dnstracer": "dnstracer -h",
              "dnstop": "dnstop -h", "fpdns": "fpdns -v"}
    markers = {"dnsenum": "usage", "dnstracer": "usage", "dnstop": "usage",
               "fpdns": "version"}
    for package, identifier in zip(packages, identifiers, strict=True):
        vm.run(f"rpm -q --quiet {package}")
        signatures = vm.run(
            f"rpm -q --qf '%{{SIGPGP:pgpsig}}\n%{{RSAHEADER:pgpsig}}\n' {package}"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        vm.run(f"sudo rpm -V {package}")
        probe = vm.run(probes[package], check=False)
        output = probe.stdout + probe.stderr
        valid_codes = {255} if package == "fpdns" else {0, 1}
        assert probe.returncode in valid_codes and markers[package].lower() in output.lower(), (
            f"{package} local help/version probe failed: {probe.returncode} {output[:500]}")
        assert table_row(vm.ride("status", identifier, "--allow-candidate").stdout,
                         identifier)["OBSERVED"] == "installed"
    vm.run("sudo dnf5 history info last", timeout=300)
    repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
    assert all(step["result"] == "unchanged"
               for step in journal(vm, run_id(repeated.stdout))["steps"])
    restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
    assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = set(package_inventory(vm).splitlines())
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in expected_dependency_updates}
    expected_final.update(after_by_key[key] for key in expected_dependency_updates)
    assert final == expected_final, (
        f"restore left unexpected package changes: {sorted(final ^ expected_final)}")
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_network_discovery_batch_and_profile(vm):
    packages = ("arp-scan", "argus-clients", "dnsmap", "nmbscan")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-network-discovery"
    before = package_inventory(vm).splitlines()
    before_names = {(line.split("\t")[0], line.split("\t")[4]) for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    planned = vm.ride("plan", "--profile", profile_id, timeout=300)
    rows = [line.split("\t") for line in planned.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        expected = "installed" if initial[package] else "absent"
        assert row[2:5] == [expected, "installed", "supported"]
    applied = vm.ride("apply", "--profile", profile_id, timeout=1800)
    first_id = run_id(applied.stdout)
    record = journal(vm, first_id)
    assert record["status"] == "complete"
    assert [(step["id"], step["result"]) for step in record["steps"]] == [
        (identifier, "unchanged" if initial[package] else "changed")
        for package, identifier in zip(packages, identifiers, strict=True)]
    after = package_inventory(vm).splitlines()
    after_names = {(line.split("\t")[0], line.split("\t")[4]) for line in after}
    assert before_names <= after_names, "install transaction lost a pre-existing RPM identity"
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    expected_dependency_updates = {
        ("perl-Errno", "x86_64"), ("perl-interpreter", "x86_64"), ("perl-libs", "x86_64")}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    assert changed_existing <= expected_dependency_updates, (
        f"unexpected existing RPM changes: {sorted(changed_existing)}")
    transaction_output = applied.stdout + applied.stderr
    for key in changed_existing:
        old_fields = before_by_key[key].split("\t")
        new_fields = after_by_key[key].split("\t")
        old_version = f"{old_fields[2]}-{old_fields[3]}"
        new_version = f"{new_fields[2]}-{new_fields[3]}"
        assert (key[0] in transaction_output and old_version in transaction_output and
                new_version in transaction_output and "replacing" in transaction_output.lower()), (
            f"DNF did not document exact dependency update for {key[0]}")
    introduced = set(after) - set(before)
    probes = {"arp-scan": "arp-scan --help", "argus-clients": "ra -h",
              "dnsmap": "dnsmap"}
    markers = {"arp-scan": "usage", "argus-clients": "usage", "dnsmap": "usage"}
    for package, identifier in zip(packages, identifiers, strict=True):
        vm.run(f"rpm -q --quiet {package}")
        signatures = vm.run(
            f"rpm -q --qf '%{{SIGPGP:pgpsig}}\n%{{RSAHEADER:pgpsig}}\n' {package}"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        vm.run(f"sudo rpm -V {package}")
        vm.run(f"command -v {package if package != 'argus-clients' else 'ra'}")
        if package in probes:
            probe = vm.run(probes[package], check=False)
            output = probe.stdout + probe.stderr
            assert probe.returncode in (0, 1) and markers[package].lower() in output.lower(), (
                f"{package} local help probe failed: {probe.returncode} {output[:500]}")
        if package == "nmbscan":
            vm.run("rpm -ql nmbscan | grep -Fx /usr/share/man/man1/nmbscan.1.gz")
        assert table_row(vm.ride("status", identifier).stdout,
                         identifier)["OBSERVED"] == "installed"
    vm.run("sudo dnf5 history info last", timeout=300)
    repeated = vm.ride("apply", "--profile", profile_id, timeout=600)
    assert all(step["result"] == "unchanged"
               for step in journal(vm, run_id(repeated.stdout))["steps"])
    restored = vm.ride("restore", "--run-id", first_id, timeout=1200)
    assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = set(package_inventory(vm).splitlines())
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert final == expected_final, (
        f"restore left unexpected package changes: {sorted(final ^ expected_final)}")
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_network_traffic_batch_and_profile(vm):
    packages = ("httping", "httpry", "tcpflow", "tcpick")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-network-traffic"
    before = package_inventory(vm).splitlines()
    before_names = {(line.split("\t")[0], line.split("\t")[4]) for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    planned = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in planned.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        expected = "installed" if initial[package] else "absent"
        assert row[2:5] == [expected, "installed", "supported"]
    applied = vm.ride("apply", "--profile", profile_id, timeout=1800)
    first_id = run_id(applied.stdout)
    record = journal(vm, first_id)
    assert record["status"] == "complete"
    assert [(step["id"], step["result"]) for step in record["steps"]] == [
        (identifier, "unchanged" if initial[package] else "changed")
        for package, identifier in zip(packages, identifiers, strict=True)]
    after = package_inventory(vm).splitlines()
    after_names = {(line.split("\t")[0], line.split("\t")[4]) for line in after}
    assert before_names <= after_names, "install transaction lost a pre-existing RPM identity"
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    transaction_output = applied.stdout + applied.stderr
    for key in changed_existing:
        old_fields = before_by_key[key].split("\t")
        new_fields = after_by_key[key].split("\t")
        old_version = f"{old_fields[2]}-{old_fields[3]}"
        new_version = f"{new_fields[2]}-{new_fields[3]}"
        assert (key[0] in transaction_output and old_version in transaction_output and
                new_version in transaction_output and "replacing" in transaction_output.lower()), (
            f"DNF did not document exact dependency update for {key[0]}")
    probes = {"httping": "httping --help", "httpry": "httpry -h",
              "tcpflow": "tcpflow --help", "tcpick": "tcpick --help"}
    for package, identifier in zip(packages, identifiers, strict=True):
        vm.run(f"rpm -q --quiet {package}")
        signatures = vm.run(
            f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        vm.run(f"sudo rpm -V {package}")
        vm.run(f"command -v {package}")
        probe = vm.run(probes[package], check=False)
        output = probe.stdout + probe.stderr
        assert probe.returncode in (0, 1) and package in output.lower(), (
            f"{package} local help probe failed: {probe.returncode} {output[:500]}")
        assert table_row(vm.ride("status", identifier).stdout,
                         identifier)["OBSERVED"] == "installed"
    vm.run("sudo dnf5 history info last", timeout=300)
    repeated = vm.ride("apply", "--profile", profile_id, timeout=600)
    assert all(step["result"] == "unchanged"
               for step in journal(vm, run_id(repeated.stdout))["steps"])
    restored = vm.ride("restore", "--run-id", first_id, timeout=1200)
    assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = set(package_inventory(vm).splitlines())
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert final == expected_final, (
        f"restore left unexpected package changes: {sorted(final ^ expected_final)}")
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_forensic_media_batch_and_profile(vm):
    packages = ("dcfldd", "ddrescue", "foremost", "hexedit")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-forensic-media"
    before = package_inventory(vm).splitlines()
    before_names = {(line.split("\t")[0], line.split("\t")[4]) for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    planned = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in planned.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        expected = "installed" if initial[package] else "absent"
        assert row[2:5] == [expected, "installed", "supported"]
    applied = vm.ride("apply", "--profile", profile_id, timeout=1800)
    first_id = run_id(applied.stdout)
    record = journal(vm, first_id)
    assert record["status"] == "complete"
    assert [(step["id"], step["result"]) for step in record["steps"]] == [
        (identifier, "unchanged" if initial[package] else "changed")
        for package, identifier in zip(packages, identifiers, strict=True)]
    after = package_inventory(vm).splitlines()
    after_names = {(line.split("\t")[0], line.split("\t")[4]) for line in after}
    assert before_names <= after_names, "install transaction lost a pre-existing RPM identity"
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    transaction_output = applied.stdout + applied.stderr
    for key in changed_existing:
        old_fields = before_by_key[key].split("\t")
        new_fields = after_by_key[key].split("\t")
        old_version = f"{old_fields[2]}-{old_fields[3]}"
        new_version = f"{new_fields[2]}-{new_fields[3]}"
        assert (key[0] in transaction_output and old_version in transaction_output and
                new_version in transaction_output and "replacing" in transaction_output.lower()), (
            f"DNF did not document exact dependency update for {key[0]}")
    probes = {"dcfldd": "dcfldd --help", "ddrescue": "ddrescue --version",
              "foremost": "foremost -h", "hexedit": "hexedit --help"}
    for package, identifier in zip(packages, identifiers, strict=True):
        vm.run(f"rpm -q --quiet {package}")
        signatures = vm.run(
            f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        vm.run(f"sudo rpm -V {package}")
        vm.run(f"command -v {package}")
        probe = vm.run(probes[package], check=False)
        output = probe.stdout + probe.stderr
        assert probe.returncode in (0, 1) and package in output.lower(), (
            f"{package} local help/version probe failed: {probe.returncode} {output[:500]}")
        assert table_row(vm.ride("status", identifier).stdout,
                         identifier)["OBSERVED"] == "installed"
    vm.run("sudo dnf5 history info last", timeout=300)
    repeated = vm.ride("apply", "--profile", profile_id, timeout=600)
    assert all(step["result"] == "unchanged"
               for step in journal(vm, run_id(repeated.stdout))["steps"])
    restored = vm.ride("restore", "--run-id", first_id, timeout=1200)
    assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = set(package_inventory(vm).splitlines())
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert final == expected_final, (
        f"restore left unexpected package changes: {sorted(final ^ expected_final)}")
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_system_monitoring_batch_and_profile(vm):
    packages = ("inxi", "pcp-system-tools", "powertop", "sysstat")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-system-monitoring"
    before = package_inventory(vm).splitlines()
    before_names = {(line.split("\t")[0], line.split("\t")[4]) for line in before}
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    timer_before = vm.run("systemctl is-enabled sysstat-summary.timer", check=False)
    collector_before = {unit: vm.run(f"systemctl is-active {unit}", check=False).stdout.strip()
                        for unit in ("pmcd", "pmlogger")}
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "supported"]
    applied = vm.ride("apply", "--profile", profile_id, timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_names = {(line.split("\t")[0], line.split("\t")[4]) for line in after}
    assert before_names <= after_names, "install transaction lost a pre-existing RPM identity"
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    transaction_output = applied.stdout + applied.stderr
    for key in changed_existing:
        old_fields = before_by_key[key].split("\t")
        new_fields = after_by_key[key].split("\t")
        old_version = f"{old_fields[2]}-{old_fields[3]}"
        new_version = f"{new_fields[2]}-{new_fields[3]}"
        assert (key[0] in transaction_output and old_version in transaction_output and
                new_version in transaction_output and "replacing" in transaction_output.lower()), (
            f"DNF did not document exact dependency update for {key[0]}")
    assert all(table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
               for identifier in identifiers)
    probes = {"inxi": "inxi --version", "pcp-system-tools": None,
              "powertop": "powertop --version", "sysstat": "sar -V"}
    for package, probe in probes.items():
        signatures = vm.run(
            f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        vm.run(f"sudo rpm -V {package}")
        if probe:
            result = vm.run(probe, check=False)
            assert result.returncode in (0, 1), f"{probe}: {result.stderr[:500]}"
    collector_after = {unit: vm.run(f"systemctl is-active {unit}", check=False).stdout.strip()
                       for unit in ("pmcd", "pmlogger")}
    assert collector_after == collector_before
    timer_after = vm.run("systemctl is-enabled sysstat-summary.timer", check=False)
    if initial["sysstat"]:
        assert (timer_after.returncode, timer_after.stdout.strip()) == (
            timer_before.returncode, timer_before.stdout.strip())
    else:
        assert timer_after.stdout.strip() == "enabled"
    repeated = vm.ride("apply", "--profile", profile_id, timeout=600)
    assert all(step["result"] == "unchanged"
               for step in journal(vm, run_id(repeated.stdout))["steps"])
    vm.run("sudo dnf5 history info last", timeout=300)
    restored = vm.ride("restore", "--run-id", first_id, timeout=1200)
    assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    final_names = {(line.split("\t")[0], line.split("\t")[4]) for line in final}
    assert final_names == before_names
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final, (
        f"restore left unexpected package changes: {sorted(set(final) ^ expected_final)}")
    timer_restored = vm.run("systemctl is-enabled sysstat-summary.timer", check=False)
    assert (timer_restored.returncode, timer_restored.stdout.strip()) == (
        timer_before.returncode, timer_before.stdout.strip())
    collector_restored = {unit: vm.run(f"systemctl is-active {unit}", check=False).stdout.strip()
                          for unit in ("pmcd", "pmlogger")}
    assert collector_restored == collector_before
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_packet_observation_batch_and_profile(vm):
    packages = ("iptraf-ng", "netsniff-ng", "ngrep", "tcptrack")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-packet-observation"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "supported"]
    applied = vm.ride("apply", "--profile", profile_id, timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    transaction_output = applied.stdout + applied.stderr
    for key in changed_existing:
        old_fields = before_by_key[key].split("\t")
        new_fields = after_by_key[key].split("\t")
        old_version = f"{old_fields[2]}-{old_fields[3]}"
        new_version = f"{new_fields[2]}-{new_fields[3]}"
        assert (key[0] in transaction_output and old_version in transaction_output and
                new_version in transaction_output and "replacing" in transaction_output.lower()), (
            f"DNF did not document exact dependency update for {key[0]}")
    for package, identifier in zip(packages, identifiers, strict=True):
        signatures = vm.run(
            f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        vm.run(f"sudo rpm -V {package}")
        assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
    repeated = vm.ride("apply", "--profile", profile_id, timeout=600)
    assert all(step["result"] == "unchanged"
               for step in journal(vm, run_id(repeated.stdout))["steps"])
    restored = vm.ride("restore", "--run-id", first_id, timeout=1200)
    assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final, (
        f"restore left unexpected package changes: {sorted(set(final) ^ expected_final)}")
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_network_probing_batch_and_profile(vm):
    packages = ("firewalk", "lbd", "masscan", "zmap")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-network-probing"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    transaction_output = applied.stdout + applied.stderr
    for key in changed_existing:
        old_fields = before_by_key[key].split("\t")
        new_fields = after_by_key[key].split("\t")
        old_version = f"{old_fields[2]}-{old_fields[3]}"
        new_version = f"{new_fields[2]}-{new_fields[3]}"
        assert (key[0] in transaction_output and old_version in transaction_output and
                new_version in transaction_output and "replacing" in transaction_output.lower()), (
            f"DNF did not document exact dependency update for {key[0]}")
    for package, identifier in zip(packages, identifiers, strict=True):
        signatures = vm.run(
            f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        vm.run(f"sudo rpm -V {package}")
        vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
        vm.run(f"rpm -q --scripts {package}")
        assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
    repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
    assert all(step["result"] == "unchanged"
               for step in journal(vm, run_id(repeated.stdout))["steps"])
    restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
    assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final, (
        f"restore left unexpected package changes: {sorted(set(final) ^ expected_final)}")
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_host_integrity_batch_and_profile(vm):
    packages = ("aide", "chkrootkit", "openscap-scanner", "rkhunter", "scap-security-guide")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-host-integrity"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    cron_before = vm.run(
        "systemctl is-enabled crond.service 2>/dev/null || true; "
        "systemctl is-active crond.service 2>/dev/null || true"
    ).stdout.splitlines()
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    transaction_output = applied.stdout + applied.stderr
    try:
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            assert (key[0] in transaction_output and old_version in transaction_output and
                    new_version in transaction_output and "replacing" in transaction_output.lower()), (
                f"DNF did not document exact dependency update for {key[0]}")
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\n%{{RSAHEADER:pgpsig}}\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\t%{{FILECAPS}}\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        crond_after = vm.run(
            "systemctl is-enabled crond.service 2>/dev/null || true; "
            "systemctl is-active crond.service 2>/dev/null || true"
        ).stdout.splitlines()
        assert crond_after != cron_before, "rkhunter's cronie dependency should expose its service effect"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final, (
        f"restore left unexpected package changes: {sorted(set(final) ^ expected_final)}")
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    cron_after_restore = vm.run(
        "systemctl is-enabled crond.service 2>/dev/null || true; "
        "systemctl is-active crond.service 2>/dev/null || true"
    ).stdout.splitlines()
    assert cron_after_restore == cron_before, (
        f"crond state was not restored: {cron_before!r} -> {cron_after_restore!r}")
    # These operations only manage signed RPM presence. Never invoke a scan,
    # evaluate SCAP content, initialize an AIDE database, or remediate settings.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_snmp_batch_and_profile(vm):
    packages = ("net-snmp", "net-snmp-utils", "onesixtyone", "snmpcheck")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-snmp"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}

    def service_state():
        # Refresh PID 1's view of package-installed units without starting them.
        vm.run("sudo systemctl daemon-reload")
        return vm.run(
            "for unit in snmpd.service snmptrapd.service; do "
            "enabled=$(sudo systemctl is-enabled \"$unit\" 2>/dev/null) || enabled=not-found; "
            "active=$(sudo systemctl is-active \"$unit\" 2>/dev/null) || active=inactive; "
            "printf '%s enabled=%s active=%s\n' \"$unit\" \"$enabled\" \"$active\"; done"
        ).stdout.splitlines()

    services_before = service_state()
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    transaction_output = applied.stdout + applied.stderr
    try:
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            assert (key[0] in transaction_output and old_version in transaction_output and
                    new_version in transaction_output and "replacing" in transaction_output.lower()), (
                f"DNF did not document exact dependency update for {key[0]}")
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\n%{{RSAHEADER:pgpsig}}\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\t%{{FILECAPS}}\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        services_after = service_state()
        assert all("active=active" not in line for line in services_after), services_after
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final, (
        f"restore left unexpected package changes: {sorted(set(final) ^ set(expected_final))}")
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    assert service_state() == services_before, (
        f"SNMP service state was not restored: {services_before!r} -> {service_state()!r}")
    # Never run SNMP clients, scanners, daemons, or trap listeners in acceptance.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_password_recovery_batch_and_profile(vm):
    packages = ("bkhive", "cmospwd", "john", "ophcrack", "pdfcrack")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-password-recovery"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    transaction_output = applied.stdout + applied.stderr
    try:
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            assert (key[0] in transaction_output and old_version in transaction_output and
                    new_version in transaction_output and "replacing" in transaction_output.lower()), (
                f"DNF did not document exact dependency update for {key[0]}")
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\n%{{RSAHEADER:pgpsig}}\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\t%{{FILECAPS}}\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final, (
        f"restore left unexpected package changes: {sorted(set(final) ^ set(expected_final))}")
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    # Never execute password recovery, open evidence, or access CMOS state.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_wireless_batch_and_profile(vm):
    packages = ("aircrack-ng", "cowpatty", "kismet", "reaver")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-wireless"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}

    def kismet_state():
        vm.run("sudo systemctl daemon-reload")
        return vm.run(
            "enabled=$(sudo systemctl is-enabled kismet.service 2>/dev/null) || enabled=not-found; "
            "active=$(sudo systemctl is-active kismet.service 2>/dev/null) || active=inactive; "
            "printf 'kismet.service enabled=%s active=%s\n' \"$enabled\" \"$active\""
        ).stdout.strip()

    service_before = kismet_state()
    user_before = vm.run("getent passwd kismet || true").stdout.strip()
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    transaction_output = applied.stdout + applied.stderr
    try:
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            assert (key[0] in transaction_output and old_version in transaction_output and
                    new_version in transaction_output and "replacing" in transaction_output.lower()), (
                f"DNF did not document exact dependency update for {key[0]}")
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\n%{{RSAHEADER:pgpsig}}\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\t%{{FILECAPS}}\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        service_after = kismet_state()
        assert "active=active" not in service_after, service_after
        user_after = vm.run("getent passwd kismet || true").stdout.strip()
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final, (
        f"restore left unexpected package changes: {sorted(set(final) ^ set(expected_final))}")
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    service_restored = kismet_state()
    user_restored = vm.run("getent passwd kismet || true").stdout.strip()
    assert service_restored == service_before, (service_before, service_after, service_restored)
    assert user_restored == user_before, (user_before, user_after, user_restored)
    # Never attach a radio, start Kismet, capture frames, or run wireless tools.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_network_load_batch_and_profile(vm):
    packages = ("siege", "sipp", "sipsak", "sockperf", "uperf")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-network-load-tools"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    try:
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            assert (key[0] in applied.stdout + applied.stderr and old_version in applied.stdout + applied.stderr and
                    new_version in applied.stdout + applied.stderr and "replacing" in (applied.stdout + applied.stderr).lower()), (
                f"DNF did not document exact dependency update for {key[0]}")
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\n%{{RSAHEADER:pgpsig}}\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final, (
        f"restore left unexpected package changes: {sorted(set(final) ^ set(expected_final))}")
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    # Never run a load test, send HTTP/SIP traffic, benchmark a socket, or execute these tools.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_network_credential_batch_and_profile(vm):
    packages = ("hydra", "medusa", "ncrack", "dsniff", "ettercap")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-network-credential-tools"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    try:
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            transcript = applied.stdout + applied.stderr
            assert (key[0] in transcript and old_version in transcript and new_version in transcript and
                    "replacing" in transcript.lower()), f"DNF did not document exact update for {key[0]}"
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\n%{{RSAHEADER:pgpsig}}\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final, (
        f"restore left unexpected package changes: {sorted(set(final) ^ set(expected_final))}")
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    # Never attempt logins, sniff or intercept traffic, or execute these tools.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_network_monitoring_batch_and_profile(vm):
    packages = ("argus", "nfswatch", "nicstat", "vnstat")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-network-monitoring"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}

    def vnstat_state():
        vm.run("sudo systemctl daemon-reload")
        unit = vm.run(
            "enabled=$(sudo systemctl is-enabled vnstat.service 2>/dev/null) || enabled=not-found; "
            "active=$(sudo systemctl is-active vnstat.service 2>/dev/null) || active=inactive; "
            "printf 'vnstat.service enabled=%s active=%s\\n' \"$enabled\" \"$active\""
        ).stdout.strip()
        account = vm.run("getent passwd vnstat || true").stdout.strip()
        database = vm.run(
            "if sudo test -d /var/lib/vnstat; then sudo find /var/lib/vnstat -type f "
            "-exec sha256sum {} \\; | sort; else printf 'absent\\n'; fi"
        ).stdout.strip()
        return unit, account, database

    service_before, account_before, database_before = vnstat_state()
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    service_after, account_after, database_after = vnstat_state()
    try:
        assert "active=active" not in service_after, service_after
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            transcript = applied.stdout + applied.stderr
            assert key[0] in transcript and old_version in transcript and new_version in transcript
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\n%{{RSAHEADER:pgpsig}}\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final, (
        f"restore left unexpected package changes: {sorted(set(final) ^ set(expected_final))}")
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    service_restored, account_restored, database_restored = vnstat_state()
    assert service_restored == service_before, (service_before, service_after, service_restored)
    assert database_restored == database_before, (database_before, database_after, database_restored)
    # Account creation is reported as observed; no service or monitor is started.
    assert account_restored in (account_before, account_after)
    # Never capture traffic, start vnstat, or run the monitoring tools.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_packet_generation_batch_and_profile(vm):
    packages = ("hping3", "packETH", "sing", "tcpreplay", "thc-ipv6")
    identifiers = ("package.hping3", "package.packeth", "package.sing", "package.tcpreplay", "package.thc-ipv6")
    profile_id = "fedora-security-lab-packet-generation"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    try:
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            transcript = applied.stdout + applied.stderr
            assert (key[0] in transcript and old_version in transcript and new_version in transcript and
                    "replacing" in transcript.lower()), f"DNF did not document exact update for {key[0]}"
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\n%{{RSAHEADER:pgpsig}}\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    # Fedora DNF retains packETH's weak-dependency closure after removing the
    # requested RPM; record and constrain the exact observed residue.
    weak_dependency_residue = {"gtk2", "ibus-gtk2", "libcanberra-gtk2"}
    expected_final.update(line for line in after
                          if line.split("\t")[0] in weak_dependency_residue)
    before_names = {line.split("\t")[0] for line in before}
    assert {line.split("\t")[0] for line in final
            if line.split("\t")[0] not in before_names} == weak_dependency_residue
    assert set(final) == expected_final, (
        f"restore left unexpected package changes: {sorted(set(final) ^ set(expected_final))}")
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    # Never craft/replay packets, open interfaces, or run the installed tools.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_codec_runtime_and_opencv_batch_and_profile(vm):
    packages = (
        "gstreamer1-plugins-bad-free-libs",
        "gstreamer1-plugins-bad-free-opencv",
        "gstreamer1-plugins-base",
        "lame-libs",
    )
    identifiers = tuple(f"package.{package}" for package in packages)
    candidate = candidate_args(identifiers[0])
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    before = set(package_inventory(vm).splitlines())
    baseline_installed = {
        package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
        for package in packages
    }
    expected_baseline = {
        "gstreamer1-plugins-bad-free-libs": True,
        "gstreamer1-plugins-bad-free-opencv": False,
        "gstreamer1-plugins-base": True,
        "lame-libs": True,
    }
    assert baseline_installed == expected_baseline, (
        "Pinned Workstation codec runtime baseline differs from the reviewed image; "
        "inspect the transcript before any apply."
    )
    planned = vm.ride("plan", "--profile", "fedora-codecs-runtime-and-opencv", *candidate)
    plan_rows = [line.split("\t") for line in planned.stdout.splitlines()[1:]]
    assert [row[0] for row in plan_rows] == list(identifiers)
    for package, row in zip(packages, plan_rows, strict=True):
        expected = "installed" if expected_baseline[package] else "absent"
        assert row[2:5] == [expected, "installed", catalog_status(row[0])]
    applied = vm.ride("apply", "--profile", "fedora-codecs-runtime-and-opencv", *candidate, timeout=1800)
    first = journal(vm, run_id(applied.stdout))
    assert first["status"] == "complete"
    assert [(step["id"], step["result"]) for step in first["steps"]] == [
        (identifier, "unchanged" if expected_baseline[package] else "changed")
        for package, identifier in zip(packages, identifiers, strict=True)]
    installed = set(package_inventory(vm).splitlines())
    introduced = installed - before
    for package, identifier in zip(packages, identifiers, strict=True):
        assert vm.run(f"rpm -q --quiet {package}").returncode == 0
        signatures = vm.run(
            f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        vm.run(f"sudo rpm -V {package}")
        assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
    repeated = vm.ride("apply", "--profile", "fedora-codecs-runtime-and-opencv", *candidate)
    assert all(step["result"] == "unchanged"
               for step in journal(vm, run_id(repeated.stdout))["steps"])
    removed = vm.ride("remove", "--profile", "fedora-codecs-runtime-and-opencv", *candidate, timeout=1800)
    assert journal(vm, run_id(removed.stdout))["status"] == "complete"
    for package, identifier in zip(packages, identifiers, strict=True):
        installed_now = vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
        if expected_baseline[package]:
            assert installed_now, f"profile removal deleted pre-existing package {package}"
            assert f"kept one-way prerequisite {identifier}" in removed.stdout
        else:
            assert not installed_now, f"profile inverse left package {package} installed"
    recovered = set(package_inventory(vm).splitlines())
    before_names = {(line.split("\t")[0], line.split("\t")[4]) for line in before}
    recovered_names = {(line.split("\t")[0], line.split("\t")[4]) for line in recovered}
    introduced_names = {(line.split("\t")[0], line.split("\t")[4]) for line in introduced}
    assert before_names <= recovered_names
    residual_names = recovered_names - before_names
    assert residual_names <= introduced_names, f"unrelated RPM residue: {sorted(residual_names - introduced_names)}"


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_multimedia_audio_video_integration_batch_and_profile(vm):
    packages = (
        "PackageKit-gstreamer-plugin",
        "alsa-ucm",
        "alsa-utils",
        "libva-intel-media-driver",
        "pipewire-alsa",
        "pipewire-gstreamer",
    )
    identifiers = tuple(f"package.{package.lower()}" for package in packages)
    candidate = candidate_args(identifiers[0])
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    before = set(package_inventory(vm).splitlines())
    baseline_installed = {
        package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
        for package in packages
    }
    assert all(baseline_installed.values()), (
        "Pinned Workstation Multimedia integration baseline differs from review; "
        "inspect the transcript before any apply."
    )
    planned = vm.ride("plan", "--profile", "fedora-codecs-audio-video-integration", *candidate)
    plan_rows = [line.split("\t") for line in planned.stdout.splitlines()[1:]]
    assert [row[0] for row in plan_rows] == list(identifiers)
    assert all(row[2:5] == ["installed", "installed", catalog_status(row[0])]
               for row in plan_rows)
    applied = vm.ride("apply", "--profile", "fedora-codecs-audio-video-integration", *candidate)
    first = journal(vm, run_id(applied.stdout))
    assert first["status"] == "complete"
    assert [(step["id"], step["result"]) for step in first["steps"]] == [
        (identifier, "unchanged") for identifier in identifiers]
    for package, identifier in zip(packages, identifiers, strict=True):
        assert vm.run(f"rpm -q --quiet {package}").returncode == 0
        signatures = vm.run(
            f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        vm.run(f"sudo rpm -V {package}")
        assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
    repeated = vm.ride("apply", "--profile", "fedora-codecs-audio-video-integration", *candidate)
    assert all(step["result"] == "unchanged"
               for step in journal(vm, run_id(repeated.stdout))["steps"])
    removed = vm.ride("remove", "--profile", "fedora-codecs-audio-video-integration", *candidate)
    assert journal(vm, run_id(removed.stdout))["status"] == "complete"
    for identifier in identifiers:
        assert f"kept one-way prerequisite {identifier}" in removed.stdout
    after = set(package_inventory(vm).splitlines())
    before_names = {(line.split("\t")[0], line.split("\t")[4]) for line in before}
    after_names = {(line.split("\t")[0], line.split("\t")[4]) for line in after}
    assert before_names <= after_names, "profile removal lost a pre-existing RPM identity"


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_pipewire_espeak_batch_and_profile(vm):
    packages = ("pipewire-pulseaudio", "pipewire-utils", "wireplumber",
                "gstreamer-plugins-espeak")
    identifiers = tuple(f"package.{package}" for package in packages)
    candidate = candidate_args(identifiers[0])
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    before = set(package_inventory(vm).splitlines())
    baseline_installed = {
        package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
        for package in packages
    }
    expected_baseline = {
        "pipewire-pulseaudio": True,
        "pipewire-utils": True,
        "wireplumber": True,
        "gstreamer-plugins-espeak": False,
    }
    assert baseline_installed == expected_baseline, (
        "Pinned Workstation Multimedia package baseline differs from review; "
        "inspect the transcript before any apply."
    )
    planned = vm.ride("plan", "--profile", "fedora-codecs-pipewire-and-espeak", *candidate)
    plan_rows = [line.split("\t") for line in planned.stdout.splitlines()[1:]]
    assert [row[0] for row in plan_rows] == list(identifiers)
    for package, row in zip(packages, plan_rows, strict=True):
        expected = "installed" if expected_baseline[package] else "absent"
        assert row[2:5] == [expected, "installed", catalog_status(row[0])]
    applied = vm.ride("apply", "--profile", "fedora-codecs-pipewire-and-espeak",
                      *candidate, timeout=1200)
    first = journal(vm, run_id(applied.stdout))
    assert first["status"] == "complete"
    assert [(step["id"], step["result"]) for step in first["steps"]] == [
        (identifier, "unchanged" if expected_baseline[package] else "changed")
        for package, identifier in zip(packages, identifiers, strict=True)]
    installed = set(package_inventory(vm).splitlines())
    introduced = installed - before
    for package, identifier in zip(packages, identifiers, strict=True):
        assert vm.run(f"rpm -q --quiet {package}").returncode == 0
        signatures = vm.run(
            f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        vm.run(f"sudo rpm -V {package}")
        assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
    repeated = vm.ride("apply", "--profile", "fedora-codecs-pipewire-and-espeak", *candidate)
    assert all(step["result"] == "unchanged"
               for step in journal(vm, run_id(repeated.stdout))["steps"])
    removed = vm.ride("remove", "--profile", "fedora-codecs-pipewire-and-espeak",
                      *candidate, timeout=1200)
    assert journal(vm, run_id(removed.stdout))["status"] == "complete"
    for package, identifier in zip(packages, identifiers, strict=True):
        installed_now = vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
        if expected_baseline[package]:
            assert installed_now, f"profile removal deleted pre-existing package {package}"
            assert f"kept one-way prerequisite {identifier}" in removed.stdout
        else:
            assert not installed_now, f"profile inverse left package {package} installed"
    recovered = set(package_inventory(vm).splitlines())
    before_names = {(line.split("\t")[0], line.split("\t")[4]) for line in before}
    recovered_names = {(line.split("\t")[0], line.split("\t")[4]) for line in recovered}
    introduced_names = {(line.split("\t")[0], line.split("\t")[4]) for line in introduced}
    assert before_names <= recovered_names
    residual_names = recovered_names - before_names
    assert residual_names <= introduced_names, f"unrelated RPM residue: {sorted(residual_names - introduced_names)}"


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
def test_provider_unrar_wrapper_lifecycle(vm):
    # The accepted 7zip package is already in the pinned image. Preserve it
    # while adding and removing the Fedora unrar command wrapper.
    seven_zip = vm.run("rpm -q 7zip").stdout
    native_rpm_batch(vm, ("unrar",),
                     installed_probes={"unrar":
                                       "test -x /usr/bin/unrar && unrar --version"})
    assert vm.run("rpm -q 7zip").stdout == seven_zip


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_archive_tools_opt_in_profile(vm):
    baseline = package_inventory(vm)
    seven_zip = vm.run("rpm -q 7zip").stdout
    plan = vm.ride("plan", "--profile", "archive-tools").stdout
    assert table_row(plan, "package.7zip")["CURRENT"] == "installed"
    assert table_row(plan, "package.unrar")["CURRENT"] == "absent"
    first = run_id(vm.ride("apply", "--profile", "archive-tools", timeout=900).stdout)
    assert [step["result"] for step in journal(vm, first)["steps"]] == ["unchanged", "changed"]
    repeat = run_id(vm.ride("apply", "--profile", "archive-tools").stdout)
    assert [step["result"] for step in journal(vm, repeat)["steps"]] == ["unchanged", "unchanged"]
    vm.ride("restore", "--run-id", first, timeout=900)
    assert vm.run("rpm -q --quiet unrar", check=False).returncode != 0
    assert vm.run("rpm -q 7zip").stdout == seven_zip
    assert package_inventory(vm) == baseline


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
def test_terminator_package_without_ibus_setting(vm):
    # The package path is independent of the v2 per-user iBus mutation.
    native_rpm_batch(vm, ("terminator",), inventory_policy="name-arch",
                     residue_candidates=("terminator",),
                     installed_probes={"terminator":
                                       "rpm -ql terminator | grep -q '/usr/share/applications/.*\\.desktop$'"})


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_security_lab_core_reuses_accepted_package_operations(vm):
    identifiers = (
        "package.binwalk", "package.dc3dd", "package.htop", "package.lynis",
        "package.pwgen", "package.vim-enhanced",
    )
    packages = ("binwalk", "dc3dd", "htop", "lynis", "pwgen", "vim-enhanced")
    profile_path = ROOT / "profiles" / "fedora-security-lab-core.json"
    profile_value = json.loads(profile_path.read_text(encoding="utf-8"))
    assert [item["id"] for item in profile_value["operations"]] == list(identifiers)
    group = vm.run("sudo dnf5 group info security-lab", timeout=600).stdout
    for package in packages:
        assert re.search(rf"(?m)^\s*:\s*{re.escape(package)}\s*$", group), package

    baseline_rows = package_inventory(vm).splitlines()
    baseline = {
        f"{fields[0]}.{fields[4]}": tuple(fields[1:4])
        for fields in (line.split("\t") for line in baseline_rows)
    }
    was_installed = {
        package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
        for package in packages
    }
    planned = vm.ride("plan", "--profile", "fedora-security-lab-core").stdout
    for identifier in identifiers:
        assert table_row(planned, identifier)["DESIRED"] == "installed"

    first = run_id(vm.ride("apply", "--profile", "fedora-security-lab-core", timeout=1200).stdout)
    assert [(step["id"], step["result"]) for step in journal(vm, first)["steps"]] == [
        (identifier, "unchanged" if was_installed[package] else "changed")
        for identifier, package in zip(identifiers, packages, strict=True)
    ]
    assert all(vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages)
    signatures = vm.run(
        "rpm -q --qf '%{NAME}\\t%{RSAHEADER:pgpsig}\\n' " + " ".join(packages)
    ).stdout
    assert all(package in signatures and "(none)" not in signatures
               for package in packages)
    vm.run("rpm -V " + " ".join(packages))
    repeat = run_id(vm.ride("apply", "--profile", "fedora-security-lab-core").stdout)
    assert [step["result"] for step in journal(vm, repeat)["steps"]] == ["unchanged"] * len(packages)
    for identifier in identifiers:
        assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"

    vm.ride("remove", "--profile", "fedora-security-lab-core", timeout=1200)
    for package, previous in was_installed.items():
        current = vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
        assert current == previous, package
    final_rows = package_inventory(vm).splitlines()
    final = {
        f"{fields[0]}.{fields[4]}": tuple(fields[1:4])
        for fields in (line.split("\t") for line in final_rows)
    }
    assert set(final) == set(baseline)
    changed_versions = {identity for identity in baseline if baseline[identity] != final[identity]}
    assert changed_versions <= {"vim-data.noarch", "vim-minimal.x86_64"}


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_security_lab_network_analysis_profile(vm):
    identifiers = (
        "package.ncat", "package.nmap", "package.tcpdump",
        "package.wireshark-cli", "package.wireshark",
    )
    packages = ("nmap-ncat", "nmap", "tcpdump", "wireshark-cli", "wireshark")
    profile = "fedora-security-lab-network"
    profile_value = json.loads((ROOT / "profiles" / f"{profile}.json").read_text(encoding="utf-8"))
    catalog = json.loads((ROOT / "catalog" / "operations.json").read_text(encoding="utf-8"))
    entries = {item["id"]: item for item in catalog["operations"]}
    assert [item["id"] for item in profile_value["operations"]] == list(identifiers)
    assert all(entries[identifier]["status"] == "candidate" for identifier in identifiers)

    group = vm.run("sudo dnf5 group info security-lab", timeout=600).stdout
    for package in packages:
        assert re.search(rf"(?m)^\s*:\s*{re.escape(package)}\s*$", group), package

    baseline_rows = package_inventory(vm).splitlines()
    baseline = {
        f"{fields[0]}.{fields[4]}": tuple(fields[1:4])
        for fields in (line.split("\t") for line in baseline_rows)
    }
    was_installed = {
        package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
        for package in packages
    }
    refused = vm.ride("apply", "--profile", profile, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    planned = vm.ride("plan", "--profile", profile).stdout
    for identifier in identifiers:
        assert table_row(planned, identifier)["DESIRED"] == "installed"

    first_output = vm.ride("apply", "--profile", profile, "--allow-candidate", timeout=1200).stdout
    first = run_id(first_output)
    assert [(step["id"], step["result"]) for step in journal(vm, first)["steps"]] == [
        (identifier, "unchanged" if was_installed[package] else "changed")
        for identifier, package in zip(identifiers, packages, strict=True)
    ]
    assert all(vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages)
    signatures = vm.run(
        "rpm -q --qf '%{NAME}\\t%{RSAHEADER:pgpsig}\\n' " + " ".join(packages)
    ).stdout
    assert all(package in signatures and "(none)" not in signatures for package in packages)
    # dumpcap is intentionally not world-readable; verify as root so RPM can
    # inspect every packaged attribute instead of reporting '?' for that file.
    vm.run("sudo rpm -V " + " ".join(packages))
    for probe in ("ncat --version", "nmap --version", "tcpdump --version",
                  "tshark --version", "wireshark --version"):
        vm.run(probe)

    repeated = run_id(vm.ride("apply", "--profile", profile, "--allow-candidate").stdout)
    assert [step["result"] for step in journal(vm, repeated)["steps"]] == [
        "unchanged"
    ] * len(packages)
    for identifier in identifiers:
        assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"

    # Exact recovery reverses only changes made by this apply. `remove
    # --profile` instead sets every profile member absent, including packages
    # that were already installed before the run.
    vm.ride("restore", "--run-id", first, "--allow-candidate", timeout=1200)
    for package, previous in was_installed.items():
        current = vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
        assert current == previous, package
    final_rows = package_inventory(vm).splitlines()
    final = {
        f"{fields[0]}.{fields[4]}": tuple(fields[1:4])
        for fields in (line.split("\t") for line in final_rows)
    }
    assert set(final) == set(baseline)
    upgraded_names = set()
    in_upgrade_table = False
    for line in first_output.splitlines():
        if line.strip() == "Upgrading:":
            in_upgrade_table = True
        elif in_upgrade_table and line.strip() in {
            "Installing:", "Downgrading:", "Removing:", "Transaction Summary:",
        }:
            in_upgrade_table = False
        elif in_upgrade_table and line.startswith(" "):
            fields = line.split()
            if fields and fields[0] != "replacing":
                upgraded_names.add(fields[0])
    changed_names = {
        identity.rsplit(".", 1)[0]
        for identity in baseline.keys() & final.keys()
        if baseline[identity] != final[identity]
    }
    assert changed_names <= upgraded_names, (changed_names, upgraded_names)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_security_lab_forensic_recovery_profile(vm):
    identifiers = ("package.ewftools", "package.sleuthkit", "package.testdisk")
    packages = ("ewftools", "sleuthkit", "testdisk")
    profile = "fedora-security-lab-forensics"
    profile_value = json.loads((ROOT / "profiles" / f"{profile}.json").read_text(encoding="utf-8"))
    catalog = json.loads((ROOT / "catalog" / "operations.json").read_text(encoding="utf-8"))
    entries = {item["id"]: item for item in catalog["operations"]}
    assert [item["id"] for item in profile_value["operations"]] == list(identifiers)
    assert all(entries[identifier]["status"] == "candidate" for identifier in identifiers)

    group = vm.run("sudo dnf5 group info security-lab", timeout=600).stdout
    for package in packages:
        assert re.search(rf"(?m)^\s*:\s*{re.escape(package)}\s*$", group), package

    baseline_rows = package_inventory(vm).splitlines()
    baseline = {
        f"{fields[0]}.{fields[4]}": tuple(fields[1:4])
        for fields in (line.split("\t") for line in baseline_rows)
    }
    was_installed = {
        package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
        for package in packages
    }
    refused = vm.ride("apply", "--profile", profile, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    planned = vm.ride("plan", "--profile", profile).stdout
    for identifier in identifiers:
        assert table_row(planned, identifier)["DESIRED"] == "installed"

    first_output = vm.ride("apply", "--profile", profile, "--allow-candidate", timeout=1200).stdout
    first = run_id(first_output)
    assert [(step["id"], step["result"]) for step in journal(vm, first)["steps"]] == [
        (identifier, "unchanged" if was_installed[package] else "changed")
        for identifier, package in zip(identifiers, packages, strict=True)
    ]
    assert all(vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages)
    signatures = vm.run(
        "rpm -q --qf '%{NAME}\\t%{RSAHEADER:pgpsig}\\n' " + " ".join(packages)
    ).stdout
    assert all(package in signatures and "(none)" not in signatures for package in packages)
    vm.run("sudo rpm -V " + " ".join(packages))
    for probe in ("ewfinfo -V", "mmls -V", "testdisk /version"):
        vm.run(probe)

    repeated = run_id(vm.ride("apply", "--profile", profile, "--allow-candidate").stdout)
    assert [step["result"] for step in journal(vm, repeated)["steps"]] == [
        "unchanged"
    ] * len(packages)
    for identifier in identifiers:
        assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"

    vm.ride("restore", "--run-id", first, "--allow-candidate", timeout=1200)
    for package, previous in was_installed.items():
        current = vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
        assert current == previous, package
    final_rows = package_inventory(vm).splitlines()
    final = {
        f"{fields[0]}.{fields[4]}": tuple(fields[1:4])
        for fields in (line.split("\t") for line in final_rows)
    }
    assert set(final) == set(baseline)
    upgraded_names = set()
    in_upgrade_table = False
    for line in first_output.splitlines():
        if line.strip() == "Upgrading:":
            in_upgrade_table = True
        elif in_upgrade_table and line.strip() in {
            "Installing:", "Downgrading:", "Removing:", "Transaction Summary:",
        }:
            in_upgrade_table = False
        elif in_upgrade_table and line.startswith(" "):
            fields = line.split()
            if fields and fields[0] != "replacing":
                upgraded_names.add(fields[0])
    changed_names = {
        identity.rsplit(".", 1)[0]
        for identity in baseline.keys() & final.keys()
        if baseline[identity] != final[identity]
    }
    assert changed_names <= upgraded_names, (changed_names, upgraded_names)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_security_lab_network_diagnostics_profile(vm):
    identifiers = (
        "package.macchanger", "package.mtr", "package.nethogs", "package.whois",
    )
    packages = ("macchanger", "mtr", "nethogs", "whois")
    profile = "fedora-security-lab-network-diagnostics"
    profile_value = json.loads((ROOT / "profiles" / f"{profile}.json").read_text(encoding="utf-8"))
    catalog = json.loads((ROOT / "catalog" / "operations.json").read_text(encoding="utf-8"))
    entries = {item["id"]: item for item in catalog["operations"]}
    assert [item["id"] for item in profile_value["operations"]] == list(identifiers)
    assert all(entries[identifier]["status"] == "candidate" for identifier in identifiers)

    group = vm.run("sudo dnf5 group info security-lab", timeout=600).stdout
    for package in packages:
        assert re.search(rf"(?m)^\s*:\s*{re.escape(package)}\s*$", group), package

    baseline_rows = package_inventory(vm).splitlines()
    baseline = {
        f"{fields[0]}.{fields[4]}": tuple(fields[1:4])
        for fields in (line.split("\t") for line in baseline_rows)
    }
    was_installed = {
        package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
        for package in packages
    }
    refused = vm.ride("apply", "--profile", profile, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    planned = vm.ride("plan", "--profile", profile).stdout
    for identifier in identifiers:
        assert table_row(planned, identifier)["DESIRED"] == "installed"

    first_output = vm.ride("apply", "--profile", profile, "--allow-candidate", timeout=1200).stdout
    first = run_id(first_output)
    assert [(step["id"], step["result"]) for step in journal(vm, first)["steps"]] == [
        (identifier, "unchanged" if was_installed[package] else "changed")
        for identifier, package in zip(identifiers, packages, strict=True)
    ]
    assert all(vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages)
    signatures = vm.run(
        "rpm -q --qf '%{NAME}\\t%{RSAHEADER:pgpsig}\\n' " + " ".join(packages)
    ).stdout
    assert all(package in signatures and "(none)" not in signatures for package in packages)
    vm.run("sudo rpm -V " + " ".join(packages))
    for package in packages:
        vm.run(f"command -v {package}")

    repeated = run_id(vm.ride("apply", "--profile", profile, "--allow-candidate").stdout)
    assert [step["result"] for step in journal(vm, repeated)["steps"]] == [
        "unchanged"
    ] * len(packages)
    for identifier in identifiers:
        assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"

    vm.ride("restore", "--run-id", first, "--allow-candidate", timeout=1200)
    for package, previous in was_installed.items():
        current = vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
        assert current == previous, package
    final_rows = package_inventory(vm).splitlines()
    final = {
        f"{fields[0]}.{fields[4]}": tuple(fields[1:4])
        for fields in (line.split("\t") for line in final_rows)
    }
    assert set(final) == set(baseline)
    upgraded_names = set()
    in_upgrade_table = False
    for line in first_output.splitlines():
        if line.strip() == "Upgrading:":
            in_upgrade_table = True
        elif in_upgrade_table and line.strip() in {
            "Installing:", "Downgrading:", "Removing:", "Transaction Summary:",
        }:
            in_upgrade_table = False
        elif in_upgrade_table and line.startswith(" "):
            fields = line.split()
            if fields and fields[0] != "replacing":
                upgraded_names.add(fields[0])
    changed_names = {
        identity.rsplit(".", 1)[0]
        for identity in baseline.keys() & final.keys()
        if baseline[identity] != final[identity]
    }
    assert changed_names <= upgraded_names, (changed_names, upgraded_names)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_forensic_exiftool_fedora_package(vm):
    # The RPM deployment must not adopt the source-build path from v2.
    vm.run("test ! -e /usr/lib/exiftool")
    native_rpm_batch(vm, ("perl-Image-ExifTool",), inventory_policy="name-arch",
                     residue_candidates=("perl-Image-ExifTool",),
                     identifiers={"perl-Image-ExifTool": "package.exiftool"},
                     installed_probes={"perl-Image-ExifTool":
                                       "command -v exiftool && exiftool -ver"})
    vm.run("test ! -e /usr/lib/exiftool")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_forensic_binwalk_and_autopep8_fedora_packages(vm):
    # Installing the RPMs must leave the legacy mutable-script and global
    # pip destinations outside RIDE's package lifecycle.
    vm.run("test ! -e /usr/local/bin/binwalk && test ! -e /usr/local/bin/autopep8")
    native_rpm_batch(vm, ("binwalk", "python3-autopep8"),
                     inventory_policy="name-arch",
                     residue_candidates=("binwalk", "python3-autopep8"),
                     identifiers={"python3-autopep8": "package.autopep8"},
                     installed_probes={"binwalk": "test -x /usr/bin/binwalk && binwalk --version",
                                       "python3-autopep8":
                                       "test -x /usr/bin/autopep8 && autopep8 --version"})
    vm.run("test ! -e /usr/local/bin/binwalk && test ! -e /usr/local/bin/autopep8")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_publisher_native_video_and_monitor_packages(vm):
    native_rpm_batch(vm, ("youtube-dl", "gnome-shell-extension-system-monitor-applet",
                          "lm_sensors"), inventory_policy="name-arch",
                     residue_candidates=("youtube-dl",
                                         "gnome-shell-extension-system-monitor-applet",
                                         "lm_sensors"),
                     identifiers={"gnome-shell-extension-system-monitor-applet":
                                  "package.gnome-shell-extension-system-monitor-applet",
                                  "lm_sensors": "package.lm-sensors"},
                     installed_probes={
                         "youtube-dl": "test -x /usr/bin/youtube-dl && youtube-dl --version",
                         "gnome-shell-extension-system-monitor-applet":
                             "rpm -ql gnome-shell-extension-system-monitor-applet | "
                             "grep -q '/gnome-shell/extensions/.*/metadata.json$'",
                         "lm_sensors": "test -x /usr/bin/sensors && sensors --version",
                     })


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_yt_dlp_native_package_and_youtube_dl_coexistence(vm):
    native_rpm_batch(vm, ("yt-dlp",), inventory_policy="name-arch",
                     residue_candidates=("yt-dlp",),
                     installed_probes={"yt-dlp":
                                       "test -x /usr/bin/yt-dlp && yt-dlp --version"})
    # The v2 package may still be in use; the new CLI must not replace it.
    if vm.run("rpm -q --quiet youtube-dl", check=False).returncode != 0:
        vm.ride("install", "package.youtube-dl", timeout=900)
    assert vm.run("rpm -q --quiet youtube-dl", check=False).returncode == 0
    vm.ride("install", "package.yt-dlp", "--allow-candidate", timeout=900)
    vm.run("test -x /usr/bin/youtube-dl && test -x /usr/bin/yt-dlp")
    vm.ride("remove", "package.yt-dlp", "--allow-candidate", timeout=900)
    assert vm.run("rpm -q --quiet youtube-dl", check=False).returncode == 0
    vm.run("test -x /usr/bin/youtube-dl")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_workstation_monitoring_opt_in_profile(vm):
    identifiers = ("package.gnome-shell-extension-system-monitor-applet",
                   "package.lm-sensors")
    planned = vm.ride("plan", "--profile", "workstation-monitoring").stdout
    assert all(table_row(planned, identifier)["STATUS"] == "candidate"
               for identifier in identifiers)
    applied = vm.ride("apply", "--profile", "workstation-monitoring",
                      "--allow-candidate", timeout=900)
    first_id = run_id(applied.stdout)
    assert [(step["id"], step["result"]) for step in journal(vm, first_id)["steps"]] == [
        (identifier, "changed") for identifier in identifiers]
    vm.run("rpm -q --quiet gnome-shell-extension-system-monitor-applet lm_sensors")
    repeated = vm.ride("apply", "--profile", "workstation-monitoring",
                       "--allow-candidate")
    assert [step["result"] for step in journal(vm, run_id(repeated.stdout))["steps"]] == [
        "unchanged", "unchanged"]
    restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate",
                       timeout=900)
    assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    vm.run("! rpm -q --quiet gnome-shell-extension-system-monitor-applet")
    vm.run("! rpm -q --quiet lm_sensors")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_logitech_unifying_opt_in_packages_and_profile(vm):
    vm.run("systemd-detect-virt")
    vm.run("rpm -q spice-vdagent spice-webdavd open-vm-tools", check=False)
    native_rpm_batch(vm, ("solaar", "acpi"), inventory_policy="name-arch",
                     residue_candidates=("solaar", "acpi"),
                     installed_probes={"solaar": "test -x /usr/bin/solaar && solaar --version",
                                       "acpi": "test -x /usr/bin/acpi && acpi --version | grep -q '^acpi 1\\.8'"})
    planned = vm.ride("plan", "--profile", "logitech-unifying").stdout
    assert all(table_row(planned, identifier)["STATUS"] == "candidate"
               for identifier in ("package.solaar", "package.acpi"))
    applied = vm.ride("apply", "--profile", "logitech-unifying",
                      "--allow-candidate", timeout=900)
    first_id = run_id(applied.stdout)
    assert [step["result"] for step in journal(vm, first_id)["steps"]] == [
        "changed", "changed"]
    repeated = vm.ride("apply", "--profile", "logitech-unifying",
                       "--allow-candidate")
    assert [step["result"] for step in journal(vm, run_id(repeated.stdout))["steps"]] == [
        "unchanged", "unchanged"]
    restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate",
                       timeout=900)
    assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    vm.run("! rpm -q --quiet solaar")
    vm.run("! rpm -q --quiet acpi")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_commander_file_managers_opt_in_packages_and_profile(vm):
    native_rpm_batch(vm, ("gnome-commander", "mc"), inventory_policy="name-arch",
                     residue_candidates=("gnome-commander", "mc"),
                     installed_probes={
                         "gnome-commander": "test -x /usr/bin/gnome-commander",
                         "mc": "test -x /usr/bin/mc && TERM=xterm mc --version | grep -q 'GNU Midnight Commander'",
                     })
    identifiers = ("package.gnome-commander", "package.mc")
    planned = vm.ride("plan", "--profile", "commander-file-managers").stdout
    assert all(table_row(planned, identifier)["STATUS"] == "candidate"
               for identifier in identifiers)
    applied = vm.ride("apply", "--profile", "commander-file-managers",
                      "--allow-candidate", timeout=900)
    first_id = run_id(applied.stdout)
    assert [step["result"] for step in journal(vm, first_id)["steps"]] == [
        "changed", "changed"]
    vm.run("rpm -q --quiet gnome-commander mc")
    repeated = vm.ride("apply", "--profile", "commander-file-managers",
                       "--allow-candidate")
    assert [step["result"] for step in journal(vm, run_id(repeated.stdout))["steps"]] == [
        "unchanged", "unchanged"]
    restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate",
                       timeout=900)
    assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    vm.run("! rpm -q --quiet gnome-commander")
    vm.run("! rpm -q --quiet mc")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_clementine_opt_in_package_and_profile(vm):
    vm.run("rpm -q pipewire-pulseaudio pulseaudio pulseaudio-qpaeq", check=False)
    native_rpm_batch(vm, ("clementine",), inventory_policy="name-arch",
                     residue_candidates=("clementine",),
                     installed_probes={"clementine": "test -x /usr/bin/clementine"})
    planned = vm.ride("plan", "--profile", "music-player").stdout
    assert table_row(planned, "package.clementine")["STATUS"] == "candidate"
    applied = vm.ride("apply", "--profile", "music-player", "--allow-candidate",
                      timeout=900)
    first_id = run_id(applied.stdout)
    assert [step["result"] for step in journal(vm, first_id)["steps"]] == ["changed"]
    vm.run("rpm -q --quiet clementine")
    repeated = vm.ride("apply", "--profile", "music-player", "--allow-candidate")
    assert [step["result"] for step in journal(vm, run_id(repeated.stdout))["steps"]] == ["unchanged"]
    restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate",
                       timeout=900)
    assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    vm.run("! rpm -q --quiet clementine")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_easyeffects_opt_in_package_and_profile(vm):
    vm.run("rpm -q --quiet pipewire-pulseaudio")
    vm.run("! rpm -q --quiet pulseaudio")
    native_rpm_batch(vm, ("easyeffects",), inventory_policy="name-arch",
                     residue_candidates=("easyeffects",),
                     installed_probes={"easyeffects": "test -x /usr/bin/easyeffects"})
    planned = vm.ride("plan", "--profile", "audio-effects").stdout
    assert table_row(planned, "package.easyeffects")["STATUS"] == "candidate"
    applied = vm.ride("apply", "--profile", "audio-effects", "--allow-candidate",
                      timeout=900)
    first_id = run_id(applied.stdout)
    assert [step["result"] for step in journal(vm, first_id)["steps"]] == ["changed"]
    vm.run("rpm -q --quiet easyeffects pipewire-pulseaudio")
    vm.run("! rpm -q --quiet pulseaudio")
    repeated = vm.ride("apply", "--profile", "audio-effects", "--allow-candidate")
    assert [step["result"] for step in journal(vm, run_id(repeated.stdout))["steps"]] == ["unchanged"]
    restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate",
                       timeout=900)
    assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    vm.run("! rpm -q --quiet easyeffects")
    vm.run("rpm -q --quiet pipewire-pulseaudio")
    vm.run("! rpm -q --quiet pulseaudio")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_projecteur_and_cheat_native_packages(vm):
    vm.run("rpm -qf /bin/cheat", check=False)
    native_rpm_batch(vm, ("projecteur", "cheat"), inventory_policy="name-arch",
                     residue_candidates=("projecteur", "cheat"),
                     installed_probes={
                         "projecteur": "test -x /usr/bin/projecteur && test -f /usr/lib/udev/rules.d/55-projecteur.rules",
                         "cheat": "test -x /usr/bin/cheat && cheat --version",
                     })
    planned = vm.ride("plan", "--profile", "spotlight-pointer").stdout
    assert table_row(planned, "package.projecteur")["STATUS"] == "candidate"
    applied = vm.ride("apply", "--profile", "spotlight-pointer",
                      "--allow-candidate", timeout=900)
    first_id = run_id(applied.stdout)
    assert [step["result"] for step in journal(vm, first_id)["steps"]] == ["changed"]
    vm.run("rpm -q --quiet projecteur")
    repeated = vm.ride("apply", "--profile", "spotlight-pointer",
                       "--allow-candidate")
    assert [step["result"] for step in journal(vm, run_id(repeated.stdout))["steps"]] == ["unchanged"]
    restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate",
                       timeout=900)
    assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    vm.run("! rpm -q --quiet projecteur")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_forensic_volatility3_user_environment(vm):
    identifier = "package.volatility3"
    environment = "/home/ride-test/.local/share/ride-fedora/tools/volatility3"
    journal_dir = "/home/ride-test/.local/state/ride-fedora/runs"
    sibling = "/home/ride-test/.local/share/ride-fedora/tools/keep.txt"

    def user_ride(*args, timeout=120):
        return vm.run(shlex.join((f"{vm.repo}/ride.sh", *args)), timeout=timeout)

    def user_journal(run):
        return json.loads(vm.run(f"cat {journal_dir}/{run}.json").stdout)

    vm.run(f"test ! -e {environment} && test ! -e {journal_dir}")
    vm.run(f"mkdir -p {environment.rsplit('/', 1)[0]} && printf keep > {sibling}")
    guest_profile = vm.put_json("forensic-volatility3", profile(identifier))
    planned = table_row(user_ride("plan", "--profile", guest_profile).stdout, identifier)
    assert (planned["CURRENT"], planned["DESIRED"], planned["STATUS"], planned["SCOPE"]) == (
        "absent", "installed", "candidate", "user")

    applied = user_ride("apply", "--profile", guest_profile, "--allow-candidate", timeout=900)
    first_id = run_id(applied.stdout)
    assert user_journal(first_id)["steps"][0]["result"] == "changed"
    vm.run(f"test -f {environment}/.ride-owned")
    vm.run(f"{environment}/bin/python -c 'import importlib.metadata as m; "
           "assert m.version(\"volatility3\") == \"2.28.2\"; "
           "assert m.version(\"pefile\") == \"2024.8.26\"'")
    vm.run(f"{environment}/bin/vol --help", timeout=120)
    observed = table_row(user_ride("status", identifier).stdout, identifier)
    assert (observed["OBSERVED"], observed["STATUS"]) == ("installed", "candidate")
    repeated = user_ride("apply", "--profile", guest_profile, "--allow-candidate")
    assert user_journal(run_id(repeated.stdout))["steps"][0]["result"] == "unchanged"

    restored = user_ride("restore", "--run-id", first_id, "--allow-candidate")
    assert user_journal(run_id(restored.stdout))["status"] == "complete"
    vm.run(f"test ! -e {environment} && test \"$(cat {sibling})\" = keep")

    installed = user_ride("install", identifier, "--allow-candidate", timeout=900)
    assert user_journal(run_id(installed.stdout))["status"] == "complete"
    removed = user_ride("remove", identifier, "--allow-candidate")
    assert user_journal(run_id(removed.stdout))["status"] == "complete"
    vm.run(f"test ! -e {environment} && test \"$(cat {sibling})\" = keep")


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


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_network_observation_batch_and_profile(vm):
    packages = ("etherape", "p0f", "pads", "pcapdiff", "ssldump")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-network-observation"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}

    def pads_state():
        vm.run("sudo systemctl daemon-reload")
        return vm.run(
            "enabled=$(sudo systemctl is-enabled pads.service 2>/dev/null) || enabled=not-found; "
            "active=$(sudo systemctl is-active pads.service 2>/dev/null) || active=inactive; "
            "printf 'pads.service enabled=%s active=%s\\n' \"$enabled\" \"$active\""
        ).stdout.strip()

    service_before = pads_state()
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    service_after = pads_state()
    try:
        assert "active=active" not in service_after, service_after
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            transcript = applied.stdout + applied.stderr
            assert key[0] in transcript and old_version in transcript and new_version in transcript
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\n%{{RSAHEADER:pgpsig}}\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final, (
        f"restore left unexpected package changes: {sorted(set(final) ^ expected_final)}")
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    service_restored = pads_state()
    assert service_restored == service_before, (service_before, service_after, service_restored)
    # Never open a PCAP, capture traffic, start PADS, or execute these tools.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_filesystem_tools_batch_and_profile(vm):
    packages = ("extundelete", "hfsutils", "ntfs-3g", "ntfsprogs")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-filesystem-tools"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    mounts_before = vm.run("findmnt -rn -o SOURCE,TARGET,FSTYPE,OPTIONS").stdout

    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0

    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    try:
        assert vm.run("findmnt -rn -o SOURCE,TARGET,FSTYPE,OPTIONS").stdout == mounts_before
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            transcript = applied.stdout + applied.stderr
            assert key[0] in transcript and old_version in transcript and new_version in transcript
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"

    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final, (
        f"restore left unexpected package changes: {sorted(set(final) ^ expected_final)}")
    assert vm.run("findmnt -rn -o SOURCE,TARGET,FSTYPE,OPTIONS").stdout == mounts_before
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    # Never attach a disk, mount a filesystem, access user data, or run these utilities.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_dislocker_package_only(vm):
    identifier = "package.dislocker"
    profile_id = "fedora-security-lab-dislocker"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initially_installed = vm.run("rpm -q --quiet dislocker", check=False).returncode == 0
    alternative_before = vm.run("readlink /usr/bin/dislocker", check=False)
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    row = table_row(plan.stdout, identifier)
    assert (row["CURRENT"], row["DESIRED"], row["STATUS"]) == (
        "installed" if initially_installed else "absent", "installed", "candidate")
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=900)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    try:
        if not initially_installed:
            alternative_after = vm.run("readlink -f /usr/bin/dislocker")
            assert alternative_after.stdout.strip() == "/usr/bin/dislocker-file"
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            transcript = applied.stdout + applied.stderr
            assert key[0] in transcript and old_version in transcript and new_version in transcript
        signatures = vm.run(
            "rpm -q --qf '%{SIGPGP:pgpsig}\\n%{RSAHEADER:pgpsig}\\n' dislocker"
        ).stdout.splitlines()
        assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
        vm.run("sudo rpm -V dislocker")
        vm.run("rpm -q --qf '[%{FILENAMES}\\t%{FILECAPS}\\n]' dislocker")
        vm.run("rpm -q --scripts dislocker")
        assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate")
        assert journal(vm, run_id(repeated.stdout))["steps"][0]["result"] == "unchanged"
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=900)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final
    alternative_restored = vm.run("readlink /usr/bin/dislocker", check=False)
    assert (alternative_restored.returncode, alternative_restored.stdout) == (
        alternative_before.returncode, alternative_before.stdout)
    assert (vm.run("rpm -q --quiet dislocker", check=False).returncode == 0) == initially_installed
    # Never provide keys, attach/decrypt/mount volumes, or inspect user data.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_console_clients_batch_and_profile(vm):
    packages = ("mcabber", "mutt", "screen", "telnet")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-console-clients"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    try:
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            transcript = applied.stdout + applied.stderr
            assert key[0] in transcript and old_version in transcript and new_version in transcript
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    assert catalog_status("package.screen") == "candidate"
    # Do not launch clients, connect, or access mail, chat, or terminal session data.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_web_tools_batch_and_profile(vm):
    packages = ("goaccess", "httpd-tools", "httrack", "wget2-wget")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-web-tools"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}

    def httpd_state():
        return vm.run(
            "enabled=$(sudo systemctl is-enabled httpd.service 2>/dev/null) || enabled=not-found; "
            "active=$(sudo systemctl is-active httpd.service 2>/dev/null) || active=inactive; "
            "printf 'httpd.service enabled=%s active=%s\\n' \"$enabled\" \"$active\""
        ).stdout.strip()

    service_before = httpd_state()
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    service_after = httpd_state()
    try:
        assert "active=active" not in service_after, service_after
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            transcript = applied.stdout + applied.stderr
            assert key[0] in transcript and old_version in transcript and new_version in transcript
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    service_restored = httpd_state()
    assert service_restored == service_before, (service_before, service_after, service_restored)
    # Never read logs, retrieve sites, start a server, or issue network requests.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_data_sanitizers_batch_and_profile(vm):
    packages = ("nwipe", "scrub", "wipe")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-data-sanitizers"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    mounts_before = vm.run("findmnt -rn -o SOURCE,TARGET,FSTYPE,OPTIONS").stdout
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    try:
        assert vm.run("findmnt -rn -o SOURCE,TARGET,FSTYPE,OPTIONS").stdout == mounts_before
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            transcript = applied.stdout + applied.stderr
            assert key[0] in transcript and old_version in transcript and new_version in transcript
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final
    assert vm.run("findmnt -rn -o SOURCE,TARGET,FSTYPE,OPTIONS").stdout == mounts_before
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    # Never enumerate devices, access data, or run any sanitizer.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_network_interception_batch_and_profile(vm):
    packages = ("ArpON", "hunt", "netsed", "sslsplit")
    identifiers = tuple(f"package.{package.lower()}" for package in packages)
    profile_id = "fedora-security-lab-network-interception"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    service_before = vm.run("systemctl is-active arpon.service", check=False).stdout.strip()
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    try:
        assert vm.run("systemctl is-active arpon.service", check=False).stdout.strip() == service_before
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            transcript = applied.stdout + applied.stderr
            assert key[0] in transcript and old_version in transcript and new_version in transcript
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final
    assert vm.run("systemctl is-active arpon.service", check=False).stdout.strip() == service_before
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    # Never scan source, contact network endpoints, send mail, or run these tools.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_network_diagnostics_batch_and_profile(vm):
    packages = ("flawfinder", "sslscan", "subnetcalc", "swaks")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-network-diagnostics-2"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    try:
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            transcript = applied.stdout + applied.stderr
            assert key[0] in transcript and old_version in transcript and new_version in transcript
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            service_units = vm.run(
                f"rpm -ql {package} | grep -E '/systemd/system/[^/]+[.]service$'", check=False
            ).stdout.splitlines()
            assert not service_units, (package, service_units)
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    # Never scan source, contact network endpoints, send mail, or run these tools.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_storage_tools_batch_and_profile(vm):
    packages = ("gparted",)
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-storage-tools"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    mounts_before = vm.run("findmnt -rn -o SOURCE,TARGET,FSTYPE,OPTIONS").stdout
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    try:
        assert vm.run("findmnt -rn -o SOURCE,TARGET,FSTYPE,OPTIONS").stdout == mounts_before
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            transcript = applied.stdout + applied.stderr
            assert key[0] in transcript and old_version in transcript and new_version in transcript
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final
    assert vm.run("findmnt -rn -o SOURCE,TARGET,FSTYPE,OPTIONS").stdout == mounts_before
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    # Never launch GParted, enumerate devices, invoke partition tools, or change storage.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_network_interception_batch_and_profile(vm):
    packages = ("ArpON", "hunt", "netsed", "sslsplit")
    identifiers = tuple(f"package.{package.lower()}" for package in packages)
    profile_id = "fedora-security-lab-network-interception"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    service_before = vm.run("systemctl is-active arpon.service", check=False).stdout.strip()
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    try:
        assert vm.run("systemctl is-active arpon.service", check=False).stdout.strip() == service_before
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            transcript = applied.stdout + applied.stderr
            assert key[0] in transcript and old_version in transcript and new_version in transcript
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final
    assert vm.run("systemctl is-active arpon.service", check=False).stdout.strip() == service_before
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    # Never scan source, contact network endpoints, send mail, or run these tools.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_network_diagnostics_batch_and_profile(vm):
    packages = ("flawfinder", "sslscan", "subnetcalc", "swaks")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-network-diagnostics-2"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    try:
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            transcript = applied.stdout + applied.stderr
            assert key[0] in transcript and old_version in transcript and new_version in transcript
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            service_units = vm.run(
                f"rpm -ql {package} | grep -E '/systemd/system/[^/]+[.]service$'", check=False
            ).stdout.splitlines()
            assert not service_units, (package, service_units)
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    # Never scan source, contact network endpoints, send mail, or run these tools.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_forensic_images_batch_and_profile(vm):
    packages = ("afftools",)
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-forensic-images"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    mounts_before = vm.run("findmnt -rn -o SOURCE,TARGET,FSTYPE,OPTIONS").stdout
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    try:
        assert vm.run("findmnt -rn -o SOURCE,TARGET,FSTYPE,OPTIONS").stdout == mounts_before
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            transcript = applied.stdout + applied.stderr
            assert key[0] in transcript and old_version in transcript and new_version in transcript
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final
    assert vm.run("findmnt -rn -o SOURCE,TARGET,FSTYPE,OPTIONS").stdout == mounts_before
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    # Never open, convert, mount, hash, or process evidence images; do not enumerate devices.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_network_path_tools_batch_and_profile(vm):
    packages = ("proxychains-ng", "python3-scapy")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-network-path-tools"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    try:
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            owned_paths = vm.run(f"rpm -ql {package}").stdout.splitlines()
            assert not any("/systemd/system/" in path for path in owned_paths)
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    final_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in final}
    initial_names = {key[0] for key in before_by_key}
    final_names = {key[0] for key in final_by_key}
    requested_names = set(packages)
    dependency_residue = final_names - initial_names - requested_names
    assert dependency_residue == {"python3-tkinter", "tk"}
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    expected_final.update(final_by_key[key] for key in final_by_key if key[0] in dependency_residue)
    assert set(final) == expected_final
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    # Never configure a proxy, connect to an endpoint, open an interface, or send/capture packets.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_security_desktop_tools_batch_and_profile(vm):
    packages = ("security-menus", "setools-gui")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-security-desktop-tools"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    try:
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            owned_paths = vm.run(f"rpm -ql {package}").stdout.splitlines()
            assert owned_paths
            assert not any("/systemd/system/" in path for path in owned_paths)
            if package == "security-menus":
                assert any(path.endswith((".menu", ".directory")) for path in owned_paths)
            if package == "setools-gui":
                assert "/usr/bin/apol" in owned_paths
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    # Do not launch the desktop menu or Apol, or inspect or alter host policy data.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_network_interception_batch_and_profile(vm):
    packages = ("ArpON", "hunt", "netsed", "sslsplit")
    identifiers = tuple(f"package.{package.lower()}" for package in packages)
    profile_id = "fedora-security-lab-network-interception"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    service_before = vm.run("systemctl is-active arpon.service", check=False).stdout.strip()
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    try:
        assert vm.run("systemctl is-active arpon.service", check=False).stdout.strip() == service_before
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            transcript = applied.stdout + applied.stderr
            assert key[0] in transcript and old_version in transcript and new_version in transcript
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final
    assert vm.run("systemctl is-active arpon.service", check=False).stdout.strip() == service_before
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    # Never scan source, contact network endpoints, send mail, or run these tools.


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_fedora_security_lab_network_diagnostics_batch_and_profile(vm):
    packages = ("flawfinder", "sslscan", "subnetcalc", "swaks")
    identifiers = tuple(f"package.{package}" for package in packages)
    profile_id = "fedora-security-lab-network-diagnostics-2"
    before = package_inventory(vm).splitlines()
    before_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in before}
    initial = {package: vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0
               for package in packages}
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    plan = vm.ride("plan", "--profile", profile_id)
    rows = [line.split("\t") for line in plan.stdout.splitlines()[1:]]
    assert [row[0] for row in rows] == list(identifiers)
    for package, row in zip(packages, rows, strict=True):
        assert row[2:5] == ["installed" if initial[package] else "absent", "installed", "candidate"]
    refused = vm.ride("apply", "--profile", profile_id, check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    assert vm.run("sudo test ! -e /var/lib/ride-fedora/runs", check=False).returncode == 0
    applied = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=1800)
    first_id = run_id(applied.stdout)
    assert journal(vm, first_id)["status"] == "complete"
    after = package_inventory(vm).splitlines()
    after_by_key = {(line.split("\t")[0], line.split("\t")[4]): line for line in after}
    changed_existing = {key for key, line in before_by_key.items()
                        if after_by_key.get(key) != line}
    try:
        for key in changed_existing:
            old_fields = before_by_key[key].split("\t")
            new_fields = after_by_key[key].split("\t")
            old_version = f"{old_fields[2]}-{old_fields[3]}"
            new_version = f"{new_fields[2]}-{new_fields[3]}"
            transcript = applied.stdout + applied.stderr
            assert key[0] in transcript and old_version in transcript and new_version in transcript
        for package, identifier in zip(packages, identifiers, strict=True):
            signatures = vm.run(
                f"rpm -q --qf '%{{SIGPGP:pgpsig}}\\n%{{RSAHEADER:pgpsig}}\\n' {package}"
            ).stdout.splitlines()
            assert any(value.strip() not in ("", "(none)") for value in signatures), signatures
            vm.run(f"sudo rpm -V {package}")
            vm.run(f"rpm -q --qf '[%{{FILENAMES}}\\t%{{FILECAPS}}\\n]' {package}")
            vm.run(f"rpm -q --scripts {package}")
            service_units = vm.run(
                f"rpm -ql {package} | grep -E '/systemd/system/[^/]+[.]service$'", check=False
            ).stdout.splitlines()
            assert not service_units, (package, service_units)
            assert table_row(vm.ride("status", identifier).stdout, identifier)["OBSERVED"] == "installed"
        repeated = vm.ride("apply", "--profile", profile_id, "--allow-candidate", timeout=600)
        assert all(step["result"] == "unchanged"
                   for step in journal(vm, run_id(repeated.stdout))["steps"])
    finally:
        restored = vm.ride("restore", "--run-id", first_id, "--allow-candidate", timeout=1200)
        assert journal(vm, run_id(restored.stdout))["status"] == "complete"
    final = package_inventory(vm).splitlines()
    expected_final = {line for line in before
                      if (line.split("\t")[0], line.split("\t")[4]) not in changed_existing}
    expected_final.update(after_by_key[key] for key in changed_existing)
    assert set(final) == expected_final
    for package, was_installed in initial.items():
        assert (vm.run(f"rpm -q --quiet {package}", check=False).returncode == 0) == was_installed
    # Never scan source, contact network endpoints, send mail, or run these tools.
