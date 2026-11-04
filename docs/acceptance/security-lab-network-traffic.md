# Security Lab HTTP and TCP traffic tools acceptance

**Result: PASS**

Both candidate and supported-path lifecycles passed on disposable Fedora 44
Workstation x86_64 VMs on 2026-10-31. The supported-path apply used no
candidate bypass.
Pinned image SHA-256:
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.

Operations: `package.httping`, `package.httpry`, `package.tcpflow`, and
`package.tcpick`, selected by the opt-in
`fedora-security-lab-network-traffic` profile. No base profile selects them.

## Checks and result

- Candidate apply without `--allow-candidate` was refused without creating a
  journal. Candidate apply and the later supported-path apply both completed;
  the supported run used no candidate flag. All four Fedora RPMs had
  signature metadata and passed `rpm -V`.
- The first exploratory probe used `httping -h`, which requires an argument
  and directed the test to `httping --help`; it sent no request. After
  correcting the probe, local help passed for `httping`, `httpry`, `tcpflow`,
  and `tcpick`.
- Status reported installed; repeat apply reported all four unchanged.
  Restore removed the selected RPMs and returned to the exact 1,913-package
  baseline. The transaction added exactly four RPMs and changed no
  pre-existing RPM or dependency.
- No URL was supplied, no network request was sent, no interface was opened,
  and no capture file was read or written.

The lifecycle is automated by
[`test_fedora_security_lab_network_traffic_batch_and_profile`](../../tests/acceptance/test_package_contract.py).
The corrected candidate transcript is retained under
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06i-retry/fedora-44-workstation-x86_64/20261031T124555Z-test-fedora-security-lab-network-traffic-batch-and-profile-ecb4fc3a/`.
The passing supported-path transcript is retained under
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06i-supported/fedora-44-workstation-x86_64/20261031T125541Z-test-fedora-security-lab-network-traffic-batch-and-profile-581e8769/`.
