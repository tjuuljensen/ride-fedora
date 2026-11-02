# Security Lab packet generation acceptance

Batch 06U covers hping3, packETH, sing, tcpreplay, and THC-IPv6 as Fedora RPM
presence operations in the opt-in `fedora-security-lab-packet-generation`
profile. Fedora package links and hping3 upstream status are in the [batch
record](../migrations/provider-foundation-06.md).

The pinned Fedora 44 Workstation x86_64 candidate lifecycle passed on
2026-10-31. Candidate refusal, plan, apply, signatures, root-run `rpm -V`,
status, repeat apply, restore, and package identity recovery passed. DNF added
`tcl8`, `gtk2`, `ibus-gtk2`, weak `libcanberra-gtk2`, `libnet10`, `libdnet`,
and `libnetfilter_queue`; it changed no existing RPM. Restore removed all five
requested packages and all new dependencies except `gtk2`, `ibus-gtk2`, and
`libcanberra-gtk2`, the weak-dependency closure retained by DNF for packETH.
The test allows exactly these three residual packages. No packet was sent or
replayed, and no interface or installed tool was used. hping3's upstream is no
longer active; Fedora still ships `0.0.20051105-47.fc42`, so Scapy or Nping
remain v3.1 alternatives to review. Transcript and overlay:
`.tmp-vm-acceptance-security-06u-investigated/fedora-44-workstation-x86_64/`.

All operations remain opt-in and candidate-gated pending H046 review of
authorized links, packet bounds, and replay recovery.
Catalog operation IDs in this accepted profile: `package.hping3`, `package.packeth`, `package.sing`, `package.tcpreplay`, `package.thc-ipv6`.
