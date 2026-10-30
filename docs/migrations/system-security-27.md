# System and security batch 27: Pidgin with OTR

Status: **unresolved**, 2026-10-30. The v2 pair installs and removes both
`pidgin` and `pidgin-otr`. Both have [Fedora 44 package
records](https://packages.fedoraproject.org/pkgs/pidgin/pidgin/) and the
[OTR plugin](https://packages.fedoraproject.org/pkgs/pidgin-otr/pidgin-otr/)
is a separate security-sensitive product. Before a runnable v3 profile,
review plugin compatibility, installation and activation, security claims,
user data and key ownership, removal, and recovery in an isolated VM batch.
An RPM transaction alone does not establish correct encrypted messaging.
