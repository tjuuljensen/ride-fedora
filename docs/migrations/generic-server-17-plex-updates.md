# Generic Server 17: Plex updates

Status: **replaced**, 2026-11-02. The v2 `InstallPlexAutoUpdate` function
downloads and executes the mutable `mrworf/plexupdate` installer. Plex now
publishes public server releases through its signed RPM repository, so Fedora
DNF updates the installed `plexmediaserver` package directly.

The update capability remains available through the Plex repository and the
shared Fedora update operations. `system.update-all-packages` performs an
explicit DNF5 update. The separate opt-in `fedora-server-auto-update` profile
enables Fedora-wide DNF5 automatic updates; it is not a Plex-specific timer.
This keeps the server owner in control of whether automatic updates are
enabled and avoids running a mutable remote installer or storing Plex account
credentials.

Plex package and service install/removal passed Fedora 44 Server acceptance in
[`batch 16`](generic-server-16-plex-server.md). The existing DNF5 automatic
package and timer lifecycle passed in
[`generic-server-03`](generic-server-03-autoupdate.md). A Plex-specific update
channel, package pin, or schedule can be reopened if the owner requests one.

Windows alignment: this replacement maps the Fedora v2 updater to Fedora's
existing DNF5 update lifecycle. It does not define or alter Windows Plex
updates.
