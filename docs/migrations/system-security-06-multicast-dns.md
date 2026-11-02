# System Security 06: MulticastDNS

Status: **operable opt-in candidate on Fedora 44 Workstation x86_64**.
The owner kept both v2 functions for v3.0. The legacy pair changes the hosts
resolver line to enable or disable mDNS; Fedora 44 generates that file through
authselect.

## Completion checks

- Read the active authselect profile and require `authselect check` to pass.
- Use the profile's supported `with-mdns4` feature. Do not directly rewrite
  `/etc/nsswitch.conf` or claim an unmanaged configuration.
- Journal the complete profile selection before changing the feature. Require
  the exact managed selection before restore, preserving external profile
  changes.
- In the disposable Fedora 44 Workstation x86_64 VM, verify plan, candidate
  gate, apply, repeat, status, `getent hosts localhost`, profile validity,
  conflict refusal after an unrelated feature change, and byte-for-byte
  profile/resolver recovery.
- Keep the operation opt-in. This isolated VM has no mDNS peer, so it cannot
  prove discovery of another `.local` host.

Fedora's current `nss-mdns` package documentation confirms the plugin resolves
`.local` names and that a separate responder such as Avahi is required to
advertise a host. Fedora's authselect profile templates expose `with-mdns4`,
and the `authselect` command provides explicit feature enable/disable actions.
The pinned Fedora 44 Workstation profile is valid, reports
`local with-silent-lastlog with-mdns4`, and supports the feature. See [Fedora's
package record](https://packages.fedoraproject.org/pkgs/nss-mdns/nss-mdns/),
[authselect profile notes](https://fedoraproject.org/wiki/User:Pbrezina/Authselect_and_packages_that_modifies_nsswitch),
and [authselect command documentation](https://github.com/authselect/authselect/blob/master/src/man/authselect.8.adoc).

The provider and mocked tests use authselect state with exact selection
recovery. The [Fedora 44 Workstation acceptance](../acceptance/setting.multicast-dns.md)
passed, including the external feature conflict and exact restore. H100 tracks
alternate profile and future target compatibility after v3.0.
