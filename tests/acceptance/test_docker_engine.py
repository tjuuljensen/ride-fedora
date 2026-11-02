"""Deep Docker CE package, daemon, image, and named-volume recovery checks."""

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
OPERATION = "system.docker-engine"
FINGERPRINT = "060A61C51B558A7F742B77AAC52FEB6B621E9F35"
REPOSITORY = "/etc/yum.repos.d/docker-ce.repo"
KEY = "/etc/pki/rpm-gpg/RPM-GPG-KEY-docker-ce-ride"
MARKER = "/var/lib/ride-fedora/operations/docker-engine.json"
VOLUME = "ride-v3-recovery-fixture"
IMAGE = "ride-v3-recovery-fixture:seed"


def temporary_catalog(vm):
    """Expose the unregistered handler only inside the disposable VM test."""
    catalog = json.loads((ROOT / "catalog/operations.json").read_text(encoding="utf-8"))
    catalog["operations"].append({
        "id": OPERATION,
        "kind": "system",
        "name": "Docker Engine acceptance fixture",
        "group": "system-security",
        "description": "Test-only Docker CE Engine lifecycle fixture.",
        "handler": "docker-engine",
        "states": ["configured", "absent"],
        "scope": "system",
        # This supported status exists only in a temporary catalog uploaded to
        # the disposable guest. Production registration waits for both pilots.
        "status": "supported",
        "acceptanceEvidence": "docs/acceptance/system.docker-engine.md",
        "targets": {"fedora": {
            "releases": ["44"],
            "architectures": ["x86_64"],
            "variantIds": [vm.target["variantId"]],
        }},
        "productId": "docker-ce-engine",
        "productUri": "https://docs.docker.com/engine/",
        "license": "Apache-2.0",
        "licenseUri": "https://docs.docker.com/engine/install/fedora/",
        "sourceUri": "https://docs.docker.com/engine/install/fedora/",
        "verification": "docker-ce-local-key-and-data-preservation",
        "recovery": "none",
        "signingFingerprint": FINGERPRINT,
    })
    return vm.put_json("docker-acceptance-catalog", catalog)


def verify_docker_engine_lifecycle(vm):
    catalog = temporary_catalog(vm)
    run = lambda *args, **kwargs: vm.ride(*args, catalog=catalog, **kwargs)
    vm.run("rpm -qa --qf '%{NAME}.%{ARCH}\\n' | sort > /home/ride-test/docker-rpm-before")
    vm.run("! id -Gn ride-test | tr ' ' '\\n' | grep -Fxq docker")
    vm.run(f"test ! -e {REPOSITORY} && test ! -e {KEY} && test ! -e {MARKER}")
    vm.run("! rpm -q docker-ce docker-ce-cli containerd.io")

    plan = run("deploy", OPERATION, "--state", "configured", "--dry-run")
    assert OPERATION in plan.stdout and "supported" in plan.stdout
    applied = run("deploy", OPERATION, "--state", "configured", timeout=900)
    run_id = applied.stdout.split("Run ID: ", 1)[1].splitlines()[0]
    vm.run("rpm -q docker-ce docker-ce-cli containerd.io")
    vm.run("! rpm -q docker-ce-rootless-extras docker-buildx-plugin docker-compose-plugin")
    vm.run("rpm -V docker-ce docker-ce-cli containerd.io")
    vm.run("test \"$(systemctl is-active docker.service)\" = active")
    vm.run("test -z \"$(find /etc/yum.repos.d -maxdepth 1 -type f -name '.ride-docker-ce.*' -print)\"")
    vm.run("test -z \"$(sudo find /var/lib/ride-fedora/operations -maxdepth 1 -type f -name '.docker-engine.*' -print)\"")
    vm.run("sudo docker version --format '{{.Server.Version}}'")
    vm.run("! id -Gn ride-test | tr ' ' '\\n' | grep -Fxq docker")

    # Create data without running a container or contacting a registry.
    vm.run("mkdir -p /var/tmp/ride-docker-rootfs && printf 'seed-image\\n' > /var/tmp/ride-docker-rootfs/seed.txt && tar -C /var/tmp/ride-docker-rootfs -cf /var/tmp/ride-docker-image.tar .")
    vm.run(f"sudo docker import /var/tmp/ride-docker-image.tar {IMAGE}")
    image_id = vm.run(f"sudo docker image inspect --format '{{{{.Id}}}}' {IMAGE}").stdout.strip()
    assert image_id.startswith("sha256:")
    vm.run(f"sudo docker volume create {VOLUME}")
    mount = vm.run(f"sudo docker volume inspect --format '{{{{.Mountpoint}}}}' {VOLUME}").stdout.strip()
    assert mount.startswith("/var/lib/docker/volumes/")
    vm.run(f"printf 'seed-volume\\n' | sudo tee {mount}/ride-seed.txt >/dev/null")
    vm.run(f"sudo sha256sum {mount}/ride-seed.txt | cut -d' ' -f1 > /home/ride-test/docker-volume-before")
    vm.run("test -z \"$(sudo docker ps --quiet)\"")

    assert "configured" in run("status", OPERATION).stdout
    repeat = run("deploy", OPERATION, "--state", "configured")
    assert "unchanged" in repeat.stdout
    assert "configured" in run("status", OPERATION).stdout
    refused_restore = run("restore", "--run-id", run_id, check=False)
    assert refused_restore.returncode != 0 and "exact recovery is unavailable" in refused_restore.stderr

    run("deploy", OPERATION, "--state", "absent", timeout=900)
    vm.run("! rpm -q docker-ce docker-ce-cli containerd.io")
    vm.run(f"test ! -e {REPOSITORY} && test ! -e {KEY} && test ! -e {MARKER}")
    vm.run("test -d /var/lib/docker && test -d /var/lib/containerd")
    vm.run(f"test \"$(sudo sha256sum /var/lib/docker/volumes/{VOLUME}/_data/ride-seed.txt | cut -d' ' -f1)\" = \"$(cat /home/ride-test/docker-volume-before)\"")
    vm.run("! rpm -q gpg-pubkey-621e9f35")

    run("deploy", OPERATION, "--state", "configured", timeout=900)
    vm.run(f"test \"$(sudo docker image inspect --format '{{{{.Id}}}}' {IMAGE})\" = {image_id}")
    vm.run(f"test \"$(sudo docker volume inspect --format '{{{{.Mountpoint}}}}' {VOLUME})\" = {mount}")
    vm.run(f"test \"$(sudo sha256sum {mount}/ride-seed.txt | cut -d' ' -f1)\" = \"$(cat /home/ride-test/docker-volume-before)\"")
    vm.run("rpm -qa --qf '%{NAME}.%{ARCH}\\n' | sort > /home/ride-test/docker-rpm-after")
    vm.run("! comm -23 /home/ride-test/docker-rpm-before /home/ride-test/docker-rpm-after | grep -q .")
    vm.run(f"test -e {REPOSITORY} && test -e {KEY} && test -e {MARKER}")
    vm.run("test -d /var/lib/docker && test -d /var/lib/containerd")


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_docker_engine_workstation_image_and_volume_recovery(vm):
    verify_docker_engine_lifecycle(vm)


@pytest.mark.vm_target("fedora-44-server-x86_64")
def test_docker_engine_server_image_and_volume_recovery(vm):
    verify_docker_engine_lifecycle(vm)
