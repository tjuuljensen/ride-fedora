# Fedora 44 acceptance: package.ngrep

**Result: PASS**

`package.ngrep` passed the supported Fedora 44 Workstation x86_64 VM lifecycle
without candidate bypass. Its signed Fedora RPM passed `rpm -V`; status,
repeat apply, and restore passed. No interface or pcap was opened. The catalog
records Fedora's `ngrep` license label; upstream license details are recorded
in [batch 06L](../migrations/provider-foundation-06.md). See the combined
[packet observation acceptance](security-lab-packet-observation.md).
