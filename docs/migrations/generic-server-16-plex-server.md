# Generic Server 16: Plex Media Server

Status: **supported on Fedora 44 Server x86_64**, 2026-11-02.
The owner-kept `InstallPlexServer` outcome maps to the opt-in
`package.plex-server` and `setting.plex-server-service` operations.

## Completion checks

- Use Plex's current RPM repository and pin the official PlexSign v2 primary
  key fingerprint; enable repository metadata and RPM signature checks.
- Keep the package and service distinct, verify the unit belongs to the Plex
  RPM, and do not change firewall or account state.
- Before implementation, define disposable Server checks for service startup,
  repeat, status, exact seeded library-data preservation, package/repository
  removal, and service/account/firewall recovery.

The Fedora 44 Server acceptance passed. Plex's RPM enables and starts its
service from its install scriptlet. The service operation observes the
RPM-owned unit and only accepts matching active/enabled or inactive/disabled
states. Recovery stops and disables the service before package removal. The
acceptance seeded Plex-owned marker files in the documented library tree and
verified exact hashes across install and removal. See
[`Plex acceptance`](../acceptance/package.plex-server.md).

The profile remains opt-in and is not included in `server-base`. RIDE does not
claim account activation, firewall exposure, real library migration, or
database-schema recovery. H105 tracks those expansions for v3.1.

Windows alignment: Plex's Fedora repository and systemd service operations
are Linux-provider behavior. No Windows Plex operation or shared installer
contract was added.
