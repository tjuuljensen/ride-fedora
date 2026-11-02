# Glances Web service acceptance

Status: **PASS — supported as an opt-in Fedora 44 Server x86_64 operation**.

`setting.glances-web-service` manages Fedora's packaged `glances.service` and
depends on supported package operation `package.glances`. It owns only
`/etc/systemd/system/glances.service.d/60-ride-loopback.conf`; the drop-in
replaces the packaged `ExecStart` with `/usr/bin/glances -w -B 127.0.0.1`.
This keeps the unauthenticated API and Web UI on loopback. Do not open port
61208 in firewalld. Remote users can connect through an SSH tunnel, for
example `ssh -L 61208:127.0.0.1:61208 user@server`.

## Completion checks

- Fedora 44 Server x86_64 only; use a disposable VM and the signed Fedora RPM.
- Preserve a valid seeded `/etc/glances/glances.conf` and a seeded user config.
  On install, RPM must preserve the original system bytes and place its default
  config in `.rpmnew`. On removal, confirm RPM retains those original bytes in
  `.rpmsave`; H102 tracks exact path restoration.
- Verify the systemd fragment is owned by the Fedora `glances` RPM. Refuse an
  administrator unit or any unrelated service drop-in. Repeated apply must
  report unchanged; removal must stop and disable only this service and remove
  only the exact RIDE drop-in.
- Verify the Web UI responds with `200 text/html` on loopback port 61208, the
  socket binds exactly to `127.0.0.1`, and the firewalld state is unchanged.
- Apply the profile, repeat, check status, and restore the original journal.
  Confirm the package and service return to absent/disabled, the loopback
  override is removed, user config is byte-identical, and system config bytes
  survive as `.rpmsave`.

## Fedora 44 Server evidence

The disposable Server run passed the profile plan, Fedora RPM signature and
file checks (allowing only the intentionally seeded config difference),
`.rpmnew` preservation, loopback binding, Web UI response, repeat, status,
restore, config-byte retention, and unchanged firewalld checks. The full
acceptance transcript and restore continuation are local under
`.acceptance-runs/generic-server-07-glances-complete/` and
`.acceptance-runs/glances-final-restore-continuation-2/`. The checked-in
scenario is `tests/acceptance/test_glances_web_service.py`; mocked handler
coverage is in `tests/test_v3_glances_web_service.py`.

The official Fedora 44 package includes `glances.service` and Web dependencies
such as FastAPI and Uvicorn. The package version observed in the VM was
`4.5.7-1.fc44`. Upstream documents the `-B` bind option and warns that Web/API
mode has no authentication by default; therefore this operation uses loopback
and SSH forwarding. H102 tracks authenticated direct remote access and exact
restoration of an administrator config's original pathname. See the [Fedora
Glances package](https://packages.fedoraproject.org/pkgs/glances/glances/fedora-44.html)
and [Glances Web server documentation](https://github.com/nicolargo/glances).
