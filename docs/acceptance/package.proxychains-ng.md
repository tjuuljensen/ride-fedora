# ProxyChains-NG package acceptance

`package.proxychains-ng` is a Fedora 44 Workstation x86_64 candidate operation
from Security Lab batch 06AF. The Fedora package is 4.17-9.fc44, GPL-2.0-or-later,
from the active ProxyChains-NG upstream. RIDE manages RPM presence only; it
does not load proxy configuration, connect to endpoints, or redirect traffic.

Package lifecycle, signature, `rpm -V`, status, repeat apply, restore, and
absence of package-owned systemd units passed in the shared [06AF acceptance
report](security-lab-network-path-tools.md). No capabilities or RPM scriptlets
were present. The shared test also verifies that no pre-existing RPM changed.
