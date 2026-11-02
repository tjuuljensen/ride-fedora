# `package.psad` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64,
2026-11-01.

Fedora 44 publishes PSAD 2.4.6-24.fc44 under Fedora repository signatures,
licensed GPL-2.0-or-later. PSAD is a privileged port-scan detection daemon
that can add blocking rules; upstream project:
[Cipherdyne PSAD](https://www.cipherdyne.org/psad/).

The candidate operation manages RPM presence only. It must leave
`psad.service` inactive and disabled and preserve the nftables ruleset. No
firewall logs, network traffic, alerts, or block behavior are exercised. The
pinned Fedora 44 Workstation lifecycle pilot is pending in the
[06AM batch report](security-lab-psad.md). H064 tracks later firewall,
configuration, and alert recovery work for v3.1.
