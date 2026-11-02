# Plex Media Server service acceptance

VM acceptance result: **PASS** on Fedora 44 Server x86_64 under QEMU TCG.
`setting.plex-server-service` was applied through the opt-in Plex profile after
the signed `package.plex-server` install. Fedora's package scriptlet had
already enabled and started the unit; RIDE observed the exact active/enabled
state and recorded it. Repeat and status reported the intended state. Restore
stopped and disabled the service before the package was removed. The seeded
Plex library markers, service account UID/GID, and firewall state were
preserved. See the full [Plex package and data acceptance](package.plex-server.md)
and its transcript evidence.
