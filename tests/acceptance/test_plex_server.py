"""Plex signed RPM install, explicit service, and library-data recovery."""

import pytest


PROFILE = "fedora-server-plex"
REPO = "/etc/yum.repos.d/ride-plex-server.repo"
UNIT = "/usr/lib/systemd/system/plexmediaserver.service"
DATA = "/var/lib/plexmediaserver/Library/Application Support/Plex Media Server"


@pytest.mark.vm_target("fedora-44-server-x86_64")
@pytest.mark.recovery("remove-new-install")
def test_plex_server_preserves_seeded_library_and_service_state(vm):
    vm.run("! rpm -q --quiet plexmediaserver")
    vm.run(f"sudo test ! -e {REPO}")
    vm.run("! systemctl is-active --quiet plexmediaserver.service")
    vm.run("! systemctl is-enabled --quiet plexmediaserver.service")
    vm.run("getent group plex >/dev/null || sudo groupadd --system plex")
    vm.run("getent passwd plex >/dev/null || sudo useradd --system --gid plex --home-dir /var/lib/plexmediaserver --shell /sbin/nologin plex")
    account = vm.run("id -u plex; id -g plex").stdout.splitlines()
    seed_dir = f"{DATA}/Metadata"
    db_seed_dir = f"{DATA}/Plug-in Support/Databases"
    vm.run(f"sudo install -d -o plex -g plex -m 0750 '{seed_dir}' '{db_seed_dir}'")
    vm.run(f"sudo chown -R plex:plex /var/lib/plexmediaserver && sudo chmod 0750 '{DATA}'")
    vm.run(f"printf 'existing plex metadata seed\\n' | sudo tee '{seed_dir}/ride-v3-seed.marker' >/dev/null")
    vm.run(f"printf 'existing library database-sidecar seed\\n' | sudo tee '{db_seed_dir}/ride-v3-seed.marker' >/dev/null")
    vm.run(f"sudo chown plex:plex '{seed_dir}/ride-v3-seed.marker' '{db_seed_dir}/ride-v3-seed.marker'")
    vm.run(f"sudo sha256sum '{seed_dir}/ride-v3-seed.marker' '{db_seed_dir}/ride-v3-seed.marker' > /home/ride-test/plex-seeds.before")
    firewall_before = vm.run("sudo firewall-cmd --list-all-zones").stdout

    plan = vm.ride("plan", "--profile", PROFILE)
    assert "package.plex-server" in plan.stdout and "setting.plex-server-service" in plan.stdout
    applied = vm.ride("apply", "--profile", PROFILE, timeout=1800)
    run_id = applied.stdout.split("Run ID: ", 1)[1].splitlines()[0]

    vm.run("rpm -q plexmediaserver")
    vm.run("sudo grep -Fx 'gpgcheck=1' " + REPO)
    vm.run("sudo grep -Fx 'repo_gpgcheck=1' " + REPO)
    vm.run(f"test \"$(systemctl show --property=FragmentPath --value plexmediaserver.service)\" = {UNIT}")
    vm.run("systemctl is-enabled plexmediaserver.service | grep -Fx enabled")
    vm.run("systemctl is-active plexmediaserver.service | grep -Fx active")
    vm.run("test \"$(id -u plex)\" = " + account[0])
    vm.run("test \"$(id -g plex)\" = " + account[1])
    vm.run("sudo sha256sum -c /home/ride-test/plex-seeds.before")
    assert vm.run("sudo firewall-cmd --list-all-zones").stdout == firewall_before

    repeated = vm.ride("apply", "--profile", PROFILE)
    assert "unchanged" in repeated.stdout
    assert "setting.plex-server-service" in vm.ride("status", "setting.plex-server-service").stdout
    vm.ride("restore", "--run-id", run_id, timeout=1800)

    vm.run("! rpm -q --quiet plexmediaserver")
    vm.run(f"sudo test ! -e {REPO}")
    vm.run("! systemctl is-active --quiet plexmediaserver.service")
    vm.run("! systemctl is-enabled --quiet plexmediaserver.service")
    vm.run("sudo sha256sum -c /home/ride-test/plex-seeds.before")
    vm.run("test \"$(id -u plex)\" = " + account[0])
    vm.run("test \"$(id -g plex)\" = " + account[1])
    assert vm.run("sudo firewall-cmd --list-all-zones").stdout == firewall_before
