"""Publisher ArtCraft OCI Flatpak candidate lifecycle on Fedora Workstation."""

import json
import shlex
import subprocess

import pytest


APP_IDS = [
    "artcraft-launcher", "photocraft", "vectorcraft", "filmcraft",
    "lightcraft", "pdfcraft", "effectcraft", "designcraft", "figcraft",
    "wordcraft", "soundcraft", "deckcraft", "cadcraft", "gridcraft",
]


def verify_suite(vm, app_ids=APP_IDS):
    cli = shlex.quote(f"{vm.repo}/ride.sh")
    user = "ride-test"
    original = vm.run("id -u").stdout.strip()
    assert original != "0" and user in vm.run("id -un").stdout
    assert not vm.run("flatpak remotes --user --columns=name --json").stdout.strip() or \
        "artcraft-oci" not in vm.run("flatpak remotes --user --columns=name --json").stdout
    vm.run("flatpak remote-add --user flathub https://dl.flathub.org/repo/flathub.flatpakrepo",
           timeout=900)
    runtime_remote = json.loads(vm.run(
        "flatpak remotes --user --columns=name,url,options --json").stdout)
    flathub = next(row for row in runtime_remote if row["name"] == "flathub")
    assert flathub["url"] == "https://dl.flathub.org/repo/"
    assert "no-gpg-verify" not in flathub["options"]

    refused = vm.run(f"{cli} set setting.artcraft-oci-user-remote --state configured", check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    vm.run(f"{cli} set setting.artcraft-oci-user-remote --state configured --allow-candidate",
           timeout=900)
    remotes = json.loads(vm.run("flatpak remotes --user --columns=name,url,options --json").stdout)
    remote = [row for row in remotes if row["name"] == "artcraft-oci"]
    assert len(remote) == 1 and remote[0]["url"].rstrip("/") == "oci+https://getartcraft.com"
    vm.run("command -v xvfb-run >/dev/null && command -v dbus-run-session >/dev/null || "
           "sudo dnf install -y xorg-x11-server-Xvfb xorg-x11-xauth dbus-daemon",
           timeout=1200)

    failures = []
    for slug in app_ids:
        operation = f"package.{slug}"
        app_id = f"ai.storyteller.{slug}"
        try:
            absent = vm.run(f"{cli} status {operation}")
            assert "absent" in absent.stdout
            vm.run(f"{cli} install {operation} --allow-candidate", timeout=1800)
            present = vm.run("flatpak list --user --columns=application,origin --json")
            installed = [row for row in json.loads(present.stdout) if
                         row.get("application_id", row.get("application")) == app_id]
            assert len(installed) == 1 and installed[0]["origin"] == "artcraft-oci"
            repeated = vm.run(f"{cli} install {operation} --allow-candidate")
            assert "unchanged" in repeated.stdout
            # A clean exit or a GUI still running after 20 seconds passes the
            # startup smoke check under a disposable virtual display.
            run_command = f"flatpak run --user {shlex.quote(app_id)}"
            if slug == "designcraft":
                run_command = f"flatpak run --user --env=WGPU_BACKEND=gl {shlex.quote(app_id)}"
            launch_script = f"timeout 20s {run_command}; result=$?; sleep 2; exit $result"
            launched = vm.run(
                "NO_AT_BRIDGE=1 xvfb-run -a dbus-run-session -- bash -c "
                f"{shlex.quote(launch_script)}",
                timeout=90, check=False)
            assert launched.returncode in (0, 124), launched.stderr
            diagnostics = (launched.stdout + launched.stderr).lower()
            assert not any(word in diagnostics for word in ("panic", "traceback", "fatal error")), \
                diagnostics
            app_errors = [line for line in launched.stdout.splitlines()
                          if " ERROR " in line and
                          "The X11 server closed the connection" not in line and
                          "Broken pipe (os error 32)" not in line]
            assert not app_errors, "\n".join(app_errors)
        except (AssertionError, subprocess.TimeoutExpired) as exc:
            failures.append(f"{operation}: {exc}")
        finally:
            removal = vm.run(f"{cli} remove {operation} --allow-candidate",
                             timeout=900, check=False)
            if removal.returncode != 0:
                failures.append(f"{operation}: remove failed: {removal.stderr}")

    vm.run(f"{cli} unset setting.artcraft-oci-user-remote --allow-candidate", timeout=900)
    remaining = vm.run("flatpak remotes --user --columns=name --json").stdout
    assert "artcraft-oci" not in remaining and "flathub" in remaining
    assert not failures, "\n".join(failures)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_artcraft_launcher_fedora_44(vm):
    verify_suite(vm, APP_IDS[:1])


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_artcraft_suite_fedora_44(vm):
    verify_suite(vm)


@pytest.mark.vm_target("fedora-45-workstation-x86_64")
def test_artcraft_suite_fedora_45(vm):
    verify_suite(vm)


@pytest.mark.vm_target("fedora-45-workstation-x86_64")
def test_artcraft_designcraft_fedora_45(vm):
    verify_suite(vm, ["designcraft"])
