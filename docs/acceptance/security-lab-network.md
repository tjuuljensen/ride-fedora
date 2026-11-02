# Fedora Security Lab network profile acceptance

Status: **PASS; opt-in candidate** on Fedora 44 Workstation, x86_64,
2026-10-31.

Target: Fedora 44 Workstation, x86_64. Profile: `fedora-security-lab-network`.

The focused disposable-VM check covers the five Security Lab members
`nmap-ncat`, `nmap`, `tcpdump`, `wireshark-cli`, and `wireshark`. It checks
candidate refusal without `--allow-candidate`, plan, first apply, repeat,
status, RPM signature metadata, `rpm -V`, read-only version probes, and exact
restoration of the apply run. It checks preservation of pre-existing package
identities and removal of newly introduced packages and unused dependencies.
`remove --profile` explicitly sets every profile member absent; acceptance
uses `restore --run-id` for the exact inverse. It does not
change capture permissions or capture traffic. Existing package lifecycle
evidence for Ncat, Nmap, tcpdump, and Wireshark is reused; this run covers the
new CLI operation and the combined profile.

The group query confirmed all five exact members. Before apply,
`nmap-ncat` and `tcpdump` were installed; `nmap`, `wireshark-cli`, and
`wireshark` were absent. Candidate apply was refused without
`--allow-candidate`; plan showed all five desired installed. Apply run
`20261031T074652Z-2856-28275` completed with the expected two unchanged
pre-existing packages and three changed installations. Fedora RPM signatures,
root-run `rpm -V`, and the five read-only command version probes passed.
Repeat run `20261031T075017Z-4421-22384` reported all five unchanged. Exact
restore run `20261031T075050Z-5689-25164` removed only the three packages RIDE
had installed; `nmap-ncat` and `tcpdump` remained. The complete pre-run and
post-restore RPM name/architecture sets matched.

DNF upgraded `nmap-ncat` and ten pre-existing Qt/GStreamer RPMs during the
install transactions. Each changed version appeared in an `Upgrading:` table;
restore did not downgrade them. The acceptance check verifies changed RPM
versions are limited to packages named in those transactions.

An earlier run invoked `rpm -V` as the unprivileged SSH user and returned `?`
for `/usr/bin/dumpcap`, which that user cannot inspect. Investigation showed
this was a test privilege issue; the root-run verification above passed.

Transcript: `/tmp/ride-fedora-security-lab-06b-restore/fedora-44-workstation-x86_64/20261031T074245Z-test-security-lab-network-analysis-profile-0d2ee452/transcript.jsonl`.
Catalog operation IDs in this accepted profile: `package.ncat`, `package.nmap`, `package.tcpdump`, `package.wireshark`, `package.wireshark-cli`.
