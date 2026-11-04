# Security Lab packet observation acceptance

**Result: PASS**

Tested target: Fedora 44 Workstation x86_64.

The candidate and supported lifecycle tests passed on fresh disposable Fedora
44 Workstation x86_64 VMs on 2026-10-31. Operations: `package.iptraf-ng`,
`package.netsniff-ng`, `package.ngrep`, and `package.tcptrack`; selected by the
opt-in `fedora-security-lab-packet-observation` profile.

The automated test checked plan, candidate refusal without a journal,
explicit candidate apply, supported apply without bypass, RPM signatures,
`rpm -V`, installed status, repeat apply, and restore. All four RPMs were
absent in the baseline. DNF installed each as a separate single-package
transaction with no additional dependencies or existing RPM replacements.
Restore removed all four and returned the exact original RPM inventory. No
packet sniffer, packet generator, replay command, network interface, capture
file, or pcap was used.

The first supported-path run stopped before any package transaction because
the Fedora repository returned a zchunk checksum error. Its failed journal
contains one pending `package.iptraf-ng` step. A fresh-overlay retry passed.
Candidate acceptance passed on its first run.

Automated by
[`test_fedora_security_lab_packet_observation_batch_and_profile`](../../tests/acceptance/test_package_contract.py).
Candidate transcript:
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06l/fedora-44-workstation-x86_64/20261031T134937Z-test-fedora-security-lab-packet-observation-batch-and-profile-c25e9195/`.
Failed supported attempt: `.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06l-supported/fedora-44-workstation-x86_64/20261031T135153Z-test-fedora-security-lab-packet-observation-batch-and-profile-21c3fd62/`.
Passing supported transcript:
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06l-supported-retry/fedora-44-workstation-x86_64/20261031T135316Z-test-fedora-security-lab-packet-observation-batch-and-profile-20c366db/`.

Catalog operation IDs in this accepted profile: `package.iptraf-ng`,
`package.netsniff-ng`, `package.ngrep`, and `package.tcptrack`.
