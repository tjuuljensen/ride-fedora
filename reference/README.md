# Standalone script references

## MAC vendor lookup

`mac-vendor.py` and `mac-vendor.sh` are standalone copies from the owner's
`linux-scripts` repository at commit `08e58ba3a546f6d2cbd6c250e5012e3ede8a6e54`.
They are the v3.0 functional replacement for the old mutable `InstallMacvendor`
download. Run either from the repository root as a regular user. `--offline`
reads only the shared user cache; `--update` downloads IEEE registry data and
writes that cache. Neither script installs itself or changes system files.
If a cache update is unwanted, restore a prior cache backup; both scripts
can also rebuild the cache on a later update.

```bash
python3 reference/mac-vendor.py --help
bash reference/mac-vendor.sh --help
```

RIDE-managed installation, updates, and removal of these scripts are queued
for v3.1 as H024. The `linux-scripts` repository remains the authoritative
source for script changes; this copied revision was verified with its 15
offline parity tests. No separate public license is asserted here.

## Waydroid Fedora installer

Status: **REFERENCE ONLY - NOT TESTED END TO END**

`install-waydroid-fedora.sh` is a standalone reference implementation for
installing Waydroid on a mutable Fedora workstation. It is not integrated into
`ride.sh`, `lib-fedora.sh`, or a RIDE preset.

The script has passed Bash syntax checks and dry-run exercises on an already
configured Fedora 44 workstation. It has not been validated on a clean Fedora
installation, so review its package, OTA channel, systemd, and firewalld actions
before using it.

Preview the proposed commands without making changes:

```bash
./reference/install-waydroid-fedora.sh --dry-run
```

Real execution requires an explicit acknowledgement:

```bash
./reference/install-waydroid-fedora.sh --acknowledge-untested
```

The reference deliberately does not:

- modify `/etc/docker/daemon.json` or restart Docker, because the intended
  Docker configuration was not captured
- include the attempted camera workaround, because camera frame capture was
  not successfully verified
- delete or recreate firewalld's `trusted` zone

Before promoting this into the normal RIDE workflow, test it on a disposable
clean Fedora workstation and decide whether the optional `waydroid-to-host`
policy belongs in the default setup.
