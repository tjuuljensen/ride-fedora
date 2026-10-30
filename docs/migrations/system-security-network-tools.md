# Network analysis and communication package bundles

Status: **operable opt-in candidate**, 2026-10-30. The active v2
`InstallNetworkTools`/`RemoveNetworkTools` pair installs and removes seven
Fedora RPMs; `InstallNetCommsTools`/`RemoveNetCommsTools` does the same for
three RPMs. Neither v2 function configures a connection or capture target.
The v3 split uses one stable package ID per RPM and two opt-in profiles.

## Completion criteria defined before implementation

- Preserve all ten v2 RPM names. On the pinned Fedora 44 x86_64 Workstation
  VM, check each package's plan, signed RPM acquisition, apply, repeated
  apply, status, declared remove/restore, and package files. Reuse the
  unchanged DNF handler's mocked failure evidence.
- Check that the `tftp-server` package install leaves `tftp.socket` disabled
  and inactive; no listener, packet capture, remote connection, interface
  change, or user profile is run by RIDE. Keep both profiles opt-in and
  candidate-gated. Record dependency residue if DNF retains unowned RPMs.
- Compare Linux catalog, profile, and run-state behavior with Windows;
  document visual, device, capture, and protocol use as H019 for v3.1.

## Source and scope

The [Fedora package index](https://packages.fedoraproject.org/) lists the
Fedora 44 builds and license metadata for `tcpdump`, `wireshark`,
`tftp-server`, `nmap`, `macchanger`, `flow-tools`, `nethogs`, `minicom`,
`putty`, and `remmina`. The catalog points to each package's own source
page. The [Fedora TFTP package](https://packages.fedoraproject.org/pkgs/tftp/tftp-server/)
documents socket activation and an off-by-default service. Package-only
operations make no claim about remote access, capture permissions, or
network service configuration.

## Fedora 44 VM result

The [pinned Workstation run](../acceptance/network-package-bundles.md)
passed the ten individual package lifecycles and both curated profile
smokes. The first preparation failure revealed preinstalled `tcpdump`;
the revised test removed only that RPM in the disposable overlay. A later
`/tmp` quota failure was investigated, completed overlay disks were freed
while transcripts remained, and a new overlay passed. The final RPM set
returned exactly to the prepared baseline after restore. `tftp.socket`
stayed disabled and inactive. Wireshark and Remmina desktop operation,
capture privileges, connections, and broader recovery remain H019.
