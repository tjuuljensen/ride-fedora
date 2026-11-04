# Security Lab SNMP package acceptance

**Result: PASS (candidate)**

The opt-in `fedora-security-lab-snmp` profile passed on the pinned Fedora 44
Workstation x86_64 image (SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`) on
2026-10-31. The automated lifecycle checked candidate refusal without a run
journal, plan, explicit candidate apply, Fedora RPM signatures, root-run
`rpm -V`, status, repeat apply, restore, and exact RPM inventory recovery. All
four requested RPMs were absent at baseline. No pre-existing package identity
or version changed; restore returned the exact RPM inventory to baseline.

DNF added 18 dependency package identities: three for `net-snmp` and fifteen
for Ruby-based `snmpcheck`, including five weak Ruby dependencies. Restore
removed all 18. `onesixtyone` and `snmpcheck` were not invoked. `snmpd` and
`snmptrapd` remained inactive through the lifecycle; `systemctl` reported both
as `not-found / inactive` before, during, and after, even after reloading its
unit cache. The net-snmp RPM metadata lists the two service-unit files and its
post-install unit helper; the package-only operation did not start either
daemon. This result is recorded as observed for the pinned image, and H040
keeps service ownership and broader query behavior for later review.

No SNMP query, scanner, trap listener, or network workload ran. The four
operations remain opt-in and candidate-gated pending H040 review of authorized
query scope, daemon ownership/configuration, and recovery.

Automated by
[`test_fedora_security_lab_snmp_batch_and_profile`](../../tests/acceptance/test_package_contract.py).
Transcript and target metadata:
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06o-final2/fedora-44-workstation-x86_64/20261031T142033Z-test-fedora-security-lab-snmp-batch-and-profile-7f1a7302/`.
Catalog operation IDs in this accepted profile: `package.net-snmp`, `package.net-snmp-utils`, `package.onesixtyone`, `package.snmpcheck`.
