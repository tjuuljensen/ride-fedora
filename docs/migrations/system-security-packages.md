# Isolated storage, VPN plugin, and encrypted-vault package outcomes

Status: **package-only VM acceptance passed**, 2026-10-30. The v2 functions for
`NetMgrLibreswan`, `NetMgrL2TP`, and `KeepassXC` only install
or remove named Fedora packages. The v3 outcome is limited to those signed
RPMs. It does not configure SMART devices, connect a VPN, manage secrets, or
open a KeePass database.

## Completion criteria defined before implementation

- Use Fedora 44 x86_64 Workstation package records for each current package,
  source, and license. Give each RPM a stable operation ID and an opt-in
  profile. Do not add these packages to `default`.
- On a disposable pinned Workstation VM, exercise plan, signed apply,
  repeat, status, package verification, restore, and explicit remove. For
  each source outcome, preserve pre-existing RPMs and seeded user or system
  state, including NetworkManager connections, a vault file, and smartd
  service state. The package handler's mocked failure evidence is reused;
  any transaction or recovery failure must be investigated before retrying.
- For VPN plugins, do not create or activate connections, nor
  inspect or store credentials. For KeePassXC, do not open a database; a
  seeded vault file must remain byte-identical. A package-only operation
  may be supported only if these narrower safety checks pass.
- Keep broader hardware, VPN protocol and GUI, and encrypted-vault workflow
  tests in named v3.1 hardening items. Those tests are needed before any
  future setting or credential operation claims support.

## Reviewed Fedora sources

Fedora packages and license records: [NetworkManager-libreswan](https://packages.fedoraproject.org/pkgs/NetworkManager-libreswan/NetworkManager-libreswan/),
[NetworkManager-libreswan-gnome](https://packages.fedoraproject.org/pkgs/NetworkManager-libreswan/NetworkManager-libreswan-gnome/),
[NetworkManager-l2tp](https://packages.fedoraproject.org/pkgs/NetworkManager-l2tp/NetworkManager-l2tp/),
[NetworkManager-l2tp-gnome](https://packages.fedoraproject.org/pkgs/NetworkManager-l2tp/NetworkManager-l2tp-gnome/),
and [KeePassXC](https://packages.fedoraproject.org/pkgs/keepassxc/keepassxc/).
The Fedora repository's signature verification is the acquisition check.

## Fedora 44 Workstation VM result

The [pinned Workstation acceptance](../acceptance/system-security-packages.md)
passed all three package-only lifecycles and a separate partial-failure
restore for the Libreswan pair. The five RPM operations can be supported for
installation and removal on this exact target. VPN connections, credentials,
protocol behavior, and vault use remain outside their declared behavior.
