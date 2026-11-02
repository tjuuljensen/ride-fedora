# `package.nebula` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64,
2026-11-01.

Fedora 44 provides Nebula 1.11.2-1.fc44 under Fedora repository signatures.
The Fedora license expression is Apache-2.0 AND BSD-2-Clause-Views AND
BSD-3-Clause AND GPL-2.0-only AND ISC AND MIT AND Zlib. The maintained
[upstream project](https://github.com/slackhq/nebula) provides an overlay
network daemon and certificate utility. The operation manages package presence
only.

The package lifecycle checks candidate refusal, plan, apply, signature and
`rpm -V`, executable and sample configuration presence, inactive/disabled
service state, status, unchanged repeat, restore, explicit removal, and exact
RPM inventory recovery. Package scriptlets, capabilities, dependencies, and
unit ownership are inspected. No configuration or certificates were created;
no service, certificate utility, interface, route, or overlay connection was
used.

The Fedora 44 Workstation x86_64 VM pilot is recorded in the
[06AJ batch report](security-lab-nebula.md). H062 retains service/network
configuration and recovery work for v3.1.
