# Security Lab proxy routing and packet tools acceptance

Batch 06AF covers two isolated Fedora 44 Workstation x86_64 candidate RPMs:
ProxyChains-NG 4.17-9.fc44 (GPL-2.0-or-later) and Scapy 2.7.0-3.fc44
(GPL-2.0-only). Fedora's signed repository is the acquisition source.
ProxyChains-NG continues the legacy ProxyChains utility; Scapy is a current
packet manipulation tool and library, also recorded as an alternative for
the inactive hping3 upstream. Catalog candidates and sources are documented
in [ProxyChains-NG](package.proxychains-ng.md) and [Scapy](package.python3-scapy.md).

## Completion checks

- Verify the two source inventory entries map only to this profile.
- Candidate refusal creates no journal.
- On the pinned Fedora 44 Workstation x86_64 VM, plan, apply, verify RPM
  signatures and root-run `rpm -V`, query status, repeat, restore, and compare
  package inventory.
- Inspect dependency changes, existing RPM changes, capabilities, scriptlets,
  and service-unit ownership.
- Never load proxy settings, contact a proxy, launch either tool, open a
  network interface, or craft, capture, or transmit packets.

## VM evidence

Passed on 2026-11-01 on `fedora-44-workstation-x86_64`, Fedora 44 Workstation,
x86_64, KVM. The base image was rebuilt from the signature-verified Fedora
Everything 44-1.7 installer using the unchanged checked-in Kickstart; the
target matrix pins image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
Candidate refusal created no journal. Plan showed both operations absent and
candidate. Apply installed signed RPMs; both passed root-run `rpm -V` and status
reported installed. Repeat reported both unchanged. Restore completed and
returned both requested package states to absent. No pre-existing RPM changed.

Scapy's transaction installed 357 packages including Scapy. The combined
profile added 358 RPMs including ProxyChains-NG. Restore removed 355 packages
in the Scapy transaction and removed ProxyChains-NG separately. The exact
remaining dependency packages were `python3-tkinter` 3.14.3-2.fc44 and `tk`
1:9.0.2-2.fc44; H058 queues dependency ownership and cleanup review. The
acceptance assertion records only these two additions. Neither requested RPM
had file capabilities, scriptlets, or a systemd unit. No proxy configuration
was loaded, no endpoint contacted, and neither tool was launched; no packet
was crafted, captured, or sent.

The first lifecycle run exposed the two dependency remnants because its
inventory assertion expected a perfect dependency cleanup. We inspected the
apply and restore DNF transactions, constrained the test to the exact
observed residue, and reran it with a fresh overlay. The final pytest result
was `1 passed, 72 deselected`.

Run IDs: apply `20261101T121203Z-2547-14388`, repeat
`20261101T121412Z-4813-970`, restore `20261101T121413Z-5193-2504`. Transcript:
`.tmp-vm-acceptance-security-06af-final/fedora-44-workstation-x86_64/20261101T121133Z-test-fedora-security-lab-network-path-tools-batch-and-profile-b6af65da/transcript.jsonl`
(SHA-256 `522f2ff908d411b6e74ba171d2ea776d0b36217513449d8957b35409fcd0271d`).
H046 gates Scapy packet behavior; H057 gates ProxyChains endpoint and routing
behavior; H058 records the DNF dependency residue.
