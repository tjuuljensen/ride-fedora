# Network package bundle acceptance

Status: **PASS; operable opt-in candidates** on Fedora 44 x86_64 Workstation,
2026-10-30. The ten catalog IDs are `package.tcpdump`, `package.wireshark`,
`package.tftp-server`, `package.nmap`, `package.macchanger`,
`package.flow-tools`, `package.nethogs`, `package.minicom`, `package.putty`,
and `package.remmina`.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T135032Z-test-network-package-bundles-9e3f0430`;
candidate catalog SHA-256
`d6eb68cabd2c8e347128cd779e65ee2ea076dad898e9aaff094328504481232c`;
source bundle SHA-256
`7d8097afe8d48cdc1e4beb216d5e5242f12114255da5686d5351a8dc02d1965e`.
The retained transcript records one passing shared test in 186.72 seconds.
The first attempt stopped at a preinstalled `tcpdump`; preparation removed
only that RPM in the next disposable overlay. A later run hit `/tmp` quota
during its first DNF transaction; completed disposable overlays were removed
while retaining transcripts and metadata. The final run passed from a new
overlay after that infrastructure failure was investigated.

Each package passed absent plan, candidate-gate refusal, signed RPM apply,
`rpm -V`, unchanged repeat, installed status, restore preview, and restore.
The `network-analysis-tools` and `remote-comms-tools` profiles then passed
plan, apply, unchanged repeat, and restore. The RPM inventory after both
profile restores exactly matched the prepared absent baseline: no
pre-existing package was lost and no new dependency remained. `tftp.socket`
was disabled and inactive before and after its install and the combined
profile. The unchanged DNF provider's mocked failure checks are reused from
[base package acceptance](package.exfatprogs.md).

No packet capture, target scan, TFTP service activation, serial-device
operation, remote connection, or desktop visual behavior was exercised. H019
tracks those optional application reviews and broader recovery. See the
[batch review](../migrations/system-security-network-tools.md).
