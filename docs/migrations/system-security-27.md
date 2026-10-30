# System and security batch 27: Pidgin with OTR

Status: **unsupported for v3.0**, 2026-10-30. The v2 pair installs and removes both
`pidgin` and `pidgin-otr`. Both have [Fedora 44 package
records](https://packages.fedoraproject.org/pkgs/pidgin/pidgin/) and the
[OTR plugin](https://packages.fedoraproject.org/pkgs/pidgin-otr/pidgin-otr/)
is a separate security-sensitive product. Before a runnable v3 profile,
review plugin compatibility, installation and activation, security claims,
user data and key ownership, removal, and recovery in an isolated VM batch.
An RPM transaction alone does not establish correct encrypted messaging.
The v2 function gives no account, key, plugin activation, protocol test, or
user-data inverse. A runnable operation needs a separately requested Pidgin
and OTR deployment, current upstream and license review, isolated key store,
two-party encrypted-message test, and seeded-profile recovery on a disposable
Workstation. Reopen on that evidence; do not put a security claim behind a
package-only success result. No state-changing VM test was run for this
non-runnable decision.
