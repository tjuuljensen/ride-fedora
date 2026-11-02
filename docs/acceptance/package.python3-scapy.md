# Scapy package acceptance

`package.python3-scapy` is a Fedora 44 Workstation x86_64 candidate operation
from Security Lab batch 06AF. Fedora packages Scapy 2.7.0-3.fc44 under
GPL-2.0-only. Scapy is active upstream and offers a maintained packet
manipulation program and Python library; H046 retains packet-scope and
recovery review before its behavior is managed. RIDE manages RPM presence only
and never crafts, captures, or sends packets.

Package lifecycle, signature, `rpm -V`, status, repeat apply, restore, and
absence of package-owned systemd units passed in the shared [06AF acceptance
report](security-lab-network-path-tools.md). Fedora DNF installed a 357-package
transaction for Scapy. Restore removed the requested RPM and most dependencies;
`python3-tkinter` and `tk` remained. H058 records dependency ownership and
cleanup review for v3.1. No capabilities or RPM scriptlets were present, and
no pre-existing RPM changed.
