# Security Lab OpenSSH core package mapping

Status: **PASS; mapped to supported operation** on Fedora 44 Workstation and
Server x86_64, 2026-11-01.

The legacy Security Lab member is the Fedora `openssh` core RPM. Fedora says
this package supplies common files for both client and server subpackages; it
is useful when a client or server subpackage is installed. The migrated path
maps it to the existing `package.openssh-clients` operation. That operation
includes SSH client tools and its existing profile/recovery contract does not
configure or enable an SSH server.

No new catalog operation or handler was added. The supported operation and
both Fedora 44 target implementations are unchanged, so existing VM evidence is
reused. See [`package.openssh-clients` acceptance](package.openssh-clients.md)
for Workstation and Server lifecycle transcripts, package inventory, signature
and file verification, executable checks, and active-SSH-server checks.
