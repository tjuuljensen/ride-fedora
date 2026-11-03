"""Fedora 44 lifecycle and loopback smoke test for the pinned local SPA."""

import json

import pytest


PROFILE = "fedora-email-header-analyzer"
APP = "/home/ride-test/.local/share/ride-fedora/apps/email-header-analyzer"
LAUNCHER = "/home/ride-test/.local/bin/ride-email-header-analyzer"
MANIFEST = "/home/ride-test/.local/share/ride-fedora/owned-tools/package.email-header-analyzer.json"


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_email_header_analyzer_local_spa_lifecycle(vm):
    # Build tools are explicit prerequisites; RIDE manages only the user-local
    # app and does not silently change system packages.
    vm.run(
        "sudo dnf -y install git nodejs24 nodejs24-bin nodejs24-npm "
        "nodejs24-npm-bin",
        timeout=1200,
    )
    versions = vm.run("node --version && npm --version").stdout
    assert versions.splitlines()[0].startswith("v24.")
    vm.run(f"test ! -e {APP} && test ! -e {LAUNCHER} && test ! -e {MANIFEST}")
    vm.run(
        "mkdir -p /home/ride-test/.mozilla/firefox && "
        "printf 'preserve-profile\\n' > /home/ride-test/.mozilla/firefox/ride-marker"
    )

    client = "/home/ride-test/ride/ride.sh"
    planned = vm.run(f"{client} plan --profile {PROFILE}")
    assert "package.email-header-analyzer" in planned.stdout
    refused = vm.run(f"{client} apply --profile {PROFILE}", check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr

    applied = vm.run(f"{client} apply --profile {PROFILE} --allow-candidate", timeout=2400)
    assert "package.email-header-analyzer" in applied.stdout
    vm.run(f"test -s {APP}/dist/spa/index.html && test -x {LAUNCHER} && test -f {MANIFEST}")
    manifest = json.loads(vm.run(f"cat {MANIFEST}").stdout)
    assert manifest["sourceCommit"] == "ccaf044dfe964215656966013feaaea705726048"
    assert manifest["sourceTree"] == "69ec6b8a3c078a0f952e04ddea47f0a0ebf3ce49"
    assert vm.run(f"python3 {LAUNCHER} --tree-sha256 {APP}").stdout.strip() == manifest["contentSha256"]
    status = vm.run(f"{client} status package.email-header-analyzer").stdout
    assert "package.email-header-analyzer\tgithub-source-pinned\tinstalled\tcandidate" in status

    # Exercise the actual loopback listener and browser-facing privacy headers.
    probe = r'''python3 - <<'PY'
import os, signal, subprocess, time, urllib.request
launcher = "/home/ride-test/.local/bin/ride-email-header-analyzer"
env = os.environ | {"RIDE_DISABLE_BROWSER": "1"}
server = subprocess.Popen([launcher], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, env=env)
try:
    line = server.stdout.readline().strip()
    assert line.startswith("Local analyzer: http://127.0.0.1:"), line
    url = line.removeprefix("Local analyzer: ")
    with urllib.request.urlopen(url, timeout=10) as response:
        body = response.read()
        headers = response.headers
        assert response.status == 200
        assert b"<html" in body.lower()
        assert headers.get("Content-Security-Policy")
        assert "connect-src 'self'" in headers["Content-Security-Policy"]
        assert headers.get("X-Content-Type-Options") == "nosniff"
    route = url.rstrip("/") + "/header-analyzer"
    with urllib.request.urlopen(route, timeout=10) as response:
        assert response.status == 200 and b"<html" in response.read().lower()
    time.sleep(1)
finally:
    server.send_signal(signal.SIGINT)
    stdout, stderr = server.communicate(timeout=15)
    assert server.returncode == 0, (stdout, stderr)
    assert stderr == "", stderr
    assert "header-analyzer" not in stdout
    print("loopback root and SPA route passed; CSP blocks non-local connections; server stopped")
PY'''
    vm.run(probe, timeout=60)
    assert vm.run("cat /home/ride-test/.mozilla/firefox/ride-marker").stdout.strip() == "preserve-profile"

    repeated = vm.run(f"{client} apply --profile {PROFILE} --allow-candidate", timeout=300)
    assert "unchanged package.email-header-analyzer" in repeated.stdout
    vm.run(f"{client} remove --profile {PROFILE} --allow-candidate", timeout=300)
    vm.run(f"test ! -e {APP} && test ! -e {LAUNCHER} && test ! -e {MANIFEST}")
    assert vm.run(f"{client} status package.email-header-analyzer").stdout.splitlines()[-1].split("\t")[2] == "absent"
    assert vm.run("cat /home/ride-test/.mozilla/firefox/ride-marker").stdout.strip() == "preserve-profile"
