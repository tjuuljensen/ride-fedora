# Security Lab network clients acceptance

**Result: PASS**

Disposable VM run: PASS on Fedora 44 Workstation x86_64.
Pinned image SHA-256: `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
Date: 2026-10-31.

Operations: `package.httpie`, `package.iperf`, `package.irssi`, and
`package.socat`, selected by the opt-in
`fedora-security-lab-network-clients` profile. The profile is not in a base
profile.

## Checks and result

- Plan listed all four candidates. Apply without `--allow-candidate` was
  refused before creating a journal. Explicit candidate apply completed and
  installed all four packages.
- Each package had Fedora RPM signature metadata and passed `rpm -V`. Local
  help probes succeeded for `http`, `iperf`, `irssi`, and `socat`; no HTTP,
  iperf, IRC, or relay traffic was sent. Status reported installed.
- Repeat apply completed with all four unchanged. Restore completed and
  removed the four selected packages and their newly introduced dependencies.
- DNF's HTTPie dependency transaction explicitly upgraded the pre-existing
  `python3-requests` package from `2.32.5-5.fc44` to
  `2.33.1-1.fc44`. The transaction output identified this replacement. RIDE
  restore does not downgrade that shared package, so the Fedora update remains.
- RPM inventory contained 1,913 package records before apply and 1,929 after
  apply. After restore, 1,913 records remained; the only difference from the
  baseline was the documented `python3-requests` version upgrade. No other
  existing RPM changed and no introduced dependency remained.

The complete automated test is
[`test_fedora_security_lab_network_clients_batch_and_profile`](../../tests/acceptance/test_package_contract.py). Its VM transcript and overlay are retained under `.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06f/`.
