# OpenConnect client and GNOME integration

Status: **package-only acceptance passed**, 2026-10-30 UTC.
The owner kept the v2 `OpenconnectVPN` capability for v3.0. Its only source
function, `InstallOpenconnectVPN`, installs build tools, clones a moving
`git://` repository, compiles OpenConnect into `/usr`, and has no inverse.
The user-visible replacement is the Fedora-packaged OpenConnect CLI,
`/etc/vpnc/vpnc-script` routing helper, and GNOME NetworkManager editor.
The build-only automake, libtool, and development libraries are unnecessary
when using signed Fedora RPMs.

[Fedora OpenConnect](https://packages.fedoraproject.org/pkgs/openconnect/openconnect/)
is LGPL-2.1-or-later and supports Juniper and other SSL VPN protocols.
[vpnc-script](https://packages.fedoraproject.org/pkgs/vpnc-script/vpnc-script/)
is GPL-2.0-or-later and supplies the v2 helper path.
[NetworkManager-openconnect-gnome](https://packages.fedoraproject.org/pkgs/NetworkManager-openconnect/NetworkManager-openconnect-gnome/)
is GPL-2.0-or-later AND LGPL-2.1-only and depends on the core plugin and
OpenConnect client. Fedora 44 x86_64 Workstation is the only declared target.
Acquisition uses the signed Fedora repository, not the v2 source clone.

## Completion criteria defined before implementation

- Add stable, separate `package.openconnect`, `package.vpnc-script`, and
  `package.networkmanager-openconnect-gnome` operations with the existing
  fixed DNF handler, signed-RPM verification, installed/absent detection,
  and remove-new-install recovery. Install the helper first in the opt-in
  profile so its operation records ownership before OpenConnect can pull it
  as a dependency. Put all three in one opt-in profile and
  keep them out of `default`. Do not add a VPN connection, activation,
  private credential, or configuration handler in this batch.
- In one disposable Fedora 44 x86_64 Workstation overlay, capture the
  pre-existing package inventory and NetworkManager connection state. If
  the target preinstalls the three requested RPMs, review the exact DNF
  removal transaction before using it for absent-state preparation, then
  reinstall and verify every displaced pre-existing package name at the end.
  Seed
  an unrelated VPN profile under a private path, with mode 0600, and verify
  its bytes and metadata remain unchanged. Check each absent plan, apply,
  repeat, status, Fedora RPM signature/files, CLI/editor/helper presence,
  restore, and explicit remove. Account for dependency RPMs introduced or
  updated by DNF without removing a pre-existing package.
- Reuse the unchanged DNF handler's focused failure evidence; add a targeted
  partial-profile failure/recovery check only if package ordering reveals a
  new risk. Investigate any VM failure before retrying. Count this source
  outcome operable only when the three required components and seeded-state
  recovery pass on the declared target.
- Record the package-only result separately from a working VPN connection.
  Keep Juniper protocol login, GNOME dialog, routing, DNS, secret, and
  connection recovery behavior in a named v3.1 hardening item. Update the
  catalog, generated docs, ledger, progress, and Windows alignment.

The accepted scope installs client capability; it never connects to a VPN
or reads private connection credentials. An owner-provided server or profile
is needed before end-to-end protocol behavior can be tested.

## Result

The [disposable Workstation lifecycle](../acceptance/system-security-openconnect-packages.md)
passed the predefined package, inverse, and unrelated NetworkManager-state
checks. The three operations are supported only as package deployments on
Fedora 44 x86_64 Workstation. The profile remains opt-in. Promotion changes
catalog status and evidence metadata; the unchanged DNF handler's focused
failure evidence is reused. H031 owns the broader VPN behavior review.
