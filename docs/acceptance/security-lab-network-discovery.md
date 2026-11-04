# Security Lab network discovery acceptance

**Result: PASS**

Disposable VM run: PASS on Fedora 44 Workstation x86_64, 2026-10-31.
Pinned image SHA-256: `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.

Operations: `package.arp-scan`, `package.argus-clients`, `package.dnsmap`, and
`package.nmbscan`, selected by the opt-in
`fedora-security-lab-network-discovery` profile. No base profile selects these
tools.

## Checks and result

- The planned profile listed the four candidates. Apply without
  `--allow-candidate` was refused without creating a run journal. Explicit
  opt-in apply completed and changed all four packages from absent to
  installed.
- All four Fedora RPMs had repository signature metadata and passed `rpm -V`.
  Status reported installed for each operation, and repeat apply reported all
  four unchanged. `arp-scan --help` and `ra -h` printed local usage. DNSmap's
  no-argument invocation printed usage and performed no lookup. `nmbscan` was
  checked through its command and packaged manual page; no scan was run.
- No ARP, DNS, SMB, or Argus traffic was sent. No capture interface was opened.
- The DNF transaction introduced 39 RPMs. It upgraded three pre-existing
  Fedora Perl packages: `perl-Errno` `1.38-523.fc44` to `1.38-525.fc44`, and
  `perl-interpreter` plus `perl-libs` `5.42.1-523.fc44` to `5.42.3-525.fc44`.
  DNF reported the exact replacements. Restore removed all 39 introduced
  RPMs, retained only those three recorded updates, removed none of the 1,913
  baseline package identities, and returned to 1,913 package records.

The automated lifecycle is
[`test_fedora_security_lab_network_discovery_batch_and_profile`](../../tests/acceptance/test_package_contract.py).
The passing supported-operation transcript and disposable overlay are retained
under
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06h-supported/fedora-44-workstation-x86_64/20261031T122547Z-test-fedora-security-lab-network-discovery-batch-and-profile-09cc226b/`.
