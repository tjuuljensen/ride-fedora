# OpenConnect package-only acceptance

Status: **PASS for package installation and removal** on Fedora 44 x86_64
Workstation, 2026-10-30 UTC. The accepted operations are
`package.vpnc-script`, `package.openconnect`, and
`package.networkmanager-openconnect-gnome`. They supply the CLI, routing
helper, and GNOME editor. They do not create a connection or establish that
a VPN login, route, DNS change, or credential workflow works.

The pinned Workstation image SHA-256 was
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
The disposable overlay
`20261030T230818Z-test-openconnect-signed-packages-and-seeded-vpn-state-124a0dd1`
used candidate catalog SHA-256
`c03453a79e3736f934934dc0ec19b790ae1b325569b349675ce4b54ffcdca6b9`.
It passed in 771.38 seconds. The image initially contained all three RPMs.
Preparation removed an exact reviewed set of 11 target and dependent RPMs, and final
recovery reinstalled all 11. No pre-existing RPM name was lost.

The profile planned all three candidate operations and refused apply without
`--allow-candidate`. With that opt-in it installed the routing helper first,
then the CLI and GNOME editor, recording all three as changed. Fedora RPM
signatures and `rpm -V` passed for every package. The client reported
OpenConnect 9.12-11.fc44; the helper file and GNOME authentication dialog were
present. Repeat apply reported all three unchanged; status reported installed.
Restore preview and execution returned the three target RPMs to absent with
no dependency residue. A separate fresh apply followed by explicit reverse
order removal did the same.

A seeded unrelated NetworkManager VPN file retained its SHA-256, owner, and
mode 0600. NetworkManager connection UUIDs, active connection UUIDs, and
service enabled/active state remained unchanged through apply and recovery.
The first pilot stopped during preparation when DNF removed more dependencies
than the initial test expected; the reviewed 11-package bound was added before
retry. The next pilot exposed an ordering issue because OpenConnect pulled in
`vpnc-script` before its own operation; the profile now installs the helper
first. Neither pilot reached an uninvestigated retry.

The existing DNF handler's focused mocked failure and recovery checks are
reused. Promotion to `supported` changes only catalog status and evidence
metadata; the package handler, source, order, target, and recovery contract
are unchanged. A focused supported-profile smoke passed in overlay
`20261030T232150Z-test-openconnect-supported-profile-gate-65986d03`,
using catalog SHA-256
`9a43cd3eb544763f556b39900e86b127d4fea15f91df2396c2236f58614621b6`.
The profile planned all three operations as supported, applied without
`--allow-candidate`, reported all three unchanged because the image already
contained the RPMs, and preserved the RPM inventory. It passed in 154.40
seconds. The full absent-state lifecycle above remains the installation and
recovery evidence.
See the [batch criteria](../migrations/system-security-openconnect-01.md).
