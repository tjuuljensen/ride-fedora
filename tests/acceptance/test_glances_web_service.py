"""Fedora 44 Server Glances RPM and loopback Web service lifecycle."""

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "package.glances"
SERVICE = "setting.glances-web-service"
UNIT = "/usr/lib/systemd/system/glances.service"


def fixtures(vm):
    catalog = json.loads((ROOT / "catalog/operations.json").read_text(encoding="utf-8"))
    package = next(item for item in catalog["operations"] if item["id"] == PACKAGE)
    if "server" not in package["targets"]["fedora"]["variantIds"]:
        package["targets"]["fedora"]["variantIds"].append("server")
    profile = {
        "schemaVersion": 1,
        "id": "glances-web-acceptance",
        "description": "Disposable Glances Web service lifecycle fixture.",
        "operations": [{"id": PACKAGE, "state": "installed"}, {"id": SERVICE, "state": "enabled"}],
    }
    return (vm.put_json("glances-web-acceptance-catalog", catalog),
            vm.put_json("glances-web-acceptance-profile", profile))


@pytest.mark.vm_target("fedora-44-server-x86_64")
def test_glances_server_web_service_is_loopback_owned_and_restorable(vm):
    catalog, profile = fixtures(vm)
    vm.run("! rpm -q glances")
    vm.run("! systemctl is-active --quiet glances.service")
    vm.run("! systemctl is-enabled --quiet glances.service")
    vm.run("sudo test ! -e /etc/systemd/system/glances.service")
    vm.run("sudo test ! -e /etc/systemd/system/glances.service.d/60-ride-loopback.conf")
    vm.run("sudo mkdir -p /etc/glances && mkdir -p /home/ride-test/.config/glances")
    vm.run("printf '[global]\\n# RIDE acceptance seed\\n' | sudo tee /etc/glances/glances.conf >/dev/null")
    vm.run("printf 'user-glances-seed\\n' > /home/ride-test/.config/glances/glances.conf")
    vm.run("sha256sum /etc/glances/glances.conf /home/ride-test/.config/glances/glances.conf > /home/ride-test/glances-config-before")
    firewall_before = vm.run("sudo firewall-cmd --list-all-zones").stdout

    plan = vm.ride("plan", "--profile", profile, catalog=catalog)
    assert PACKAGE in plan.stdout and SERVICE in plan.stdout
    applied = vm.ride("apply", "--profile", profile, "--allow-candidate", catalog=catalog, timeout=900)
    run_id = applied.stdout.split("Run ID: ", 1)[1].splitlines()[0]
    vm.run("rpm -q glances")
    rpm_verify = vm.run("rpm -V glances", check=False)
    changed_files = [line for line in rpm_verify.stdout.splitlines()
                     if "/etc/glances/glances.conf" not in line]
    assert not changed_files, rpm_verify.stdout
    assert "/etc/glances/glances.conf" in rpm_verify.stdout
    vm.run("sha256sum -c /home/ride-test/glances-config-before")
    vm.run("sudo test -f /etc/glances/glances.conf.rpmnew")
    vm.run(f"test \"$(systemctl show --property=FragmentPath --value glances.service)\" = {UNIT}")
    vm.run("sudo grep -Fx '[Service]' /etc/systemd/system/glances.service.d/60-ride-loopback.conf")
    vm.run("sudo grep -Fx 'ExecStart=/usr/bin/glances -w -B 127.0.0.1' /etc/systemd/system/glances.service.d/60-ride-loopback.conf")
    vm.run("systemctl is-enabled glances.service | grep -Fx enabled")
    vm.run("systemctl is-active glances.service | grep -Fx active")
    listeners = vm.run("sudo ss -ltnH 'sport = :61208' | awk '{print $4}'").stdout.splitlines()
    assert listeners == ["127.0.0.1:61208"], listeners
    vm.run("python3 -c 'import urllib.request; r=urllib.request.urlopen(\"http://127.0.0.1:61208/\", timeout=10); assert r.status == 200 and r.headers.get_content_type() == \"text/html\"; print(r.status, r.headers.get_content_type())'", timeout=30)
    vm.run("sha256sum -c /home/ride-test/glances-config-before")
    assert vm.run("sudo firewall-cmd --list-all-zones").stdout == firewall_before

    repeated = vm.ride("apply", "--profile", profile, "--allow-candidate", catalog=catalog)
    assert "unchanged" in repeated.stdout
    assert SERVICE in vm.ride("status", SERVICE, catalog=catalog).stdout
    vm.ride("restore", "--run-id", run_id, "--allow-candidate", catalog=catalog)
    vm.run("! rpm -q glances")
    vm.run("! systemctl is-active --quiet glances.service")
    vm.run("! systemctl is-enabled --quiet glances.service")
    vm.run("sudo test ! -e /etc/systemd/system/glances.service")
    vm.run("sudo test ! -e /etc/systemd/system/glances.service.d/60-ride-loopback.conf")
    vm.run("sudo test ! -e /etc/glances/glances.conf && sudo test -f /etc/glances/glances.conf.rpmsave")
    vm.run("test \"$(sudo sha256sum /etc/glances/glances.conf.rpmsave | cut -d' ' -f1)\" = \"$(awk 'NR == 1 {print $1}' /home/ride-test/glances-config-before)\"")
    vm.run("test \"$(sha256sum /home/ride-test/.config/glances/glances.conf | cut -d' ' -f1)\" = \"$(awk 'NR == 2 {print $1}' /home/ride-test/glances-config-before)\"")
    assert vm.run("sudo firewall-cmd --list-all-zones").stdout == firewall_before
