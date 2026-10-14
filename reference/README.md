# Waydroid Fedora Installer Reference

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
