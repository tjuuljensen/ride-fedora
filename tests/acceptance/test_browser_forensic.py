"""Pinned browser-forensic install and seeded Firefox read-only smoke test."""

import shlex

import pytest


PROFILE = "fedora-browser-forensics"
BUILD_TOOLS_PROFILE = "fedora-rust-build-tools"
FIXTURE = "/home/ride-test/.mozilla/firefox/ride-forensic-fixture"
TOOL_DIR = "/home/ride-test/.local/share/ride-fedora/tools/browser-forensic"


def ride(vm, *args, check=True, timeout=240):
    return vm.run(shlex.join([f"{vm.repo}/ride.sh", *args]), check=check, timeout=timeout)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
@pytest.mark.recovery("remove-new-install")
def test_browser_forensic_pinned_build_and_read_only_firefox_analysis(vm):
    planned_tools = vm.run(f"sudo {vm.repo}/ride.sh plan --profile {BUILD_TOOLS_PROFILE}")
    assert "package.cargo" in planned_tools.stdout
    tools_gated = vm.run(f"sudo {vm.repo}/ride.sh apply --profile {BUILD_TOOLS_PROFILE}", check=False)
    assert tools_gated.returncode != 0 and "--allow-candidate" in tools_gated.stderr
    vm.run(f"sudo {vm.repo}/ride.sh apply --profile {BUILD_TOOLS_PROFILE} --allow-candidate", timeout=1200)

    vm.run(f"mkdir -p {shlex.quote(FIXTURE)}")
    vm.run(f"python3 - <<'PY'\n"
           "import sqlite3\n"
           f"root = {FIXTURE!r}\n"
           "db = sqlite3.connect(root + '/places.sqlite')\n"
           "db.executescript('''CREATE TABLE moz_places (id INTEGER PRIMARY KEY, url TEXT NOT NULL, title TEXT, visit_count INTEGER DEFAULT 0, last_visit_date INTEGER);"
           "CREATE TABLE moz_bookmarks (id INTEGER PRIMARY KEY, type INTEGER NOT NULL, fk INTEGER, title TEXT, dateAdded INTEGER NOT NULL DEFAULT 0);"
           "INSERT INTO moz_places VALUES (1, 'https://migration-fixture.invalid/visited', 'Seeded history', 2, 1648000000000000);"
           "INSERT INTO moz_places VALUES (2, 'https://migration-fixture.invalid/bookmark', 'Seeded bookmark', 0, NULL);"
           "INSERT INTO moz_bookmarks VALUES (1, 1, 2, 'Seeded bookmark', 1648000000000000);''')\n"
           "db.commit(); db.close()\n"
           "db = sqlite3.connect(root + '/cookies.sqlite')\n"
           "db.executescript('''CREATE TABLE moz_cookies (id INTEGER PRIMARY KEY, host TEXT NOT NULL, name TEXT NOT NULL, value TEXT DEFAULT '', path TEXT NOT NULL, expiry INTEGER DEFAULT 0, creationTime INTEGER NOT NULL, lastAccessed INTEGER DEFAULT 0, isSecure INTEGER DEFAULT 0, isHttpOnly INTEGER DEFAULT 0, sameSite INTEGER DEFAULT 0);"
           "INSERT INTO moz_cookies (host, name, path, creationTime, expiry, isSecure, isHttpOnly, sameSite) VALUES ('.migration-fixture.invalid', 'synthetic', '/', 1648000000000000, 0, 1, 1, 1);''')\n"
           "db.commit(); db.close()\n"
           "PY")
    before = vm.run(f"sha256sum {FIXTURE}/places.sqlite {FIXTURE}/cookies.sqlite").stdout

    planned = ride(vm, "plan", "--profile", PROFILE)
    assert "package.browser-forensic" in planned.stdout
    assert "package.cargo" not in planned.stdout
    vm.run("rpm -q cargo rust && cargo --version && rustc --version")
    gated = ride(vm, "apply", "--profile", PROFILE, check=False)
    assert gated.returncode != 0 and "--allow-candidate" in gated.stderr

    applied = ride(vm, "apply", "--profile", PROFILE, "--allow-candidate", timeout=3600)
    assert "package.browser-forensic" in applied.stdout
    vm.run("rpm -V cargo rust")
    vm.run("test -x /home/ride-test/.local/bin/br4n6 && "
           f"test -f {TOOL_DIR}/.ride-owned && test -f {TOOL_DIR}/browser-forensic-10e2f70.tar.gz")
    status = ride(vm, "status", "package.browser-forensic")
    assert "package.browser-forensic\tgithub-source-pinned\tinstalled\tcandidate" in status.stdout

    history = vm.run(f"/home/ride-test/.local/bin/br4n6 artifact history {FIXTURE}/places.sqlite --format jsonl")
    assert "migration-fixture.invalid/visited" in history.stdout
    bookmarks = vm.run(f"/home/ride-test/.local/bin/br4n6 artifact bookmarks {FIXTURE}/places.sqlite --format jsonl")
    assert "Seeded bookmark" in bookmarks.stdout
    cookies = vm.run(f"/home/ride-test/.local/bin/br4n6 artifact cookies {FIXTURE}/cookies.sqlite --format jsonl")
    assert "synthetic" in cookies.stdout
    assert vm.run(f"sha256sum {FIXTURE}/places.sqlite {FIXTURE}/cookies.sqlite").stdout == before

    # The source archive carries upstream's synthetic NSS fixture. Exercise
    # double-gated decryption without placing the known test secret in logs.
    vm.run(f"mkdir -p /tmp/ride-browser-forensic-fixture && "
           f"tar -xzf {TOOL_DIR}/browser-forensic-10e2f70.tar.gz --strip-components=5 "
           f"-C /tmp/ride-browser-forensic-fixture "
           "browser-forensic-10e2f70bd53d50144edcff849749efd0095c9a03/crates/browser-forensic-decrypt/tests/data/ffpbes2/key4.db "
           "browser-forensic-10e2f70bd53d50144edcff849749efd0095c9a03/crates/browser-forensic-decrypt/tests/data/ffpbes2/logins.json")
    vm.run("umask 077 && python3 - <<'PY'\n"
           "import os, pathlib, subprocess\n"
           "cli='/home/ride-test/.local/bin/br4n6'; root='/tmp/ride-browser-forensic-fixture/ffpbes2'\n"
           "base=[cli,'artifact','logins',root,'--keys',root,'--password-stdin']\n"
           "plain=subprocess.run(base,input='',text=True,capture_output=True,check=True)\n"
           "assert 'alice@example.com' in plain.stdout and 'S3cr3t-Passw0rd!' not in plain.stdout\n"
           "secret=pathlib.Path('/tmp/ride-browser-forensic-fixture/secrets.jsonl')\n"
           "revealed=subprocess.run(base+['--reveal-secrets',str(secret)],input='',text=True,capture_output=True,check=True)\n"
           "assert 'S3cr3t-Passw0rd!' not in revealed.stdout\n"
           "assert 'S3cr3t-Passw0rd!' in secret.read_text() and (secret.stat().st_mode & 0o777)==0o600\n"
           "PY\n"
           "rm -rf /tmp/ride-browser-forensic-fixture")

    repeated = ride(vm, "apply", "--profile", PROFILE, "--allow-candidate")
    assert "unchanged" in repeated.stdout
    run_id = applied.stdout.split("Run ID: ", 1)[1].splitlines()[0]
    ride(vm, "restore", "--run-id", run_id, "--allow-candidate")
    vm.run(f"test ! -e {TOOL_DIR} && test ! -e /home/ride-test/.local/bin/br4n6")
    assert vm.run(f"sha256sum {FIXTURE}/places.sqlite {FIXTURE}/cookies.sqlite").stdout == before
    ride(vm, "apply", "--profile", PROFILE, "--allow-candidate", timeout=3600)
    ride(vm, "remove", "--profile", PROFILE, "--allow-candidate")
    vm.run(f"test ! -e {TOOL_DIR} && test ! -e /home/ride-test/.local/bin/br4n6")
    assert vm.run(f"sha256sum {FIXTURE}/places.sqlite {FIXTURE}/cookies.sqlite").stdout == before
    vm.run(f"sudo {vm.repo}/ride.sh remove --profile {BUILD_TOOLS_PROFILE} --allow-candidate", timeout=1200)
