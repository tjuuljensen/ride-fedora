# Security Lab wireless package acceptance

**Result: PASS (candidate)**

Tested target: Fedora 44 Workstation x86_64.

The opt-in `fedora-security-lab-wireless` profile passed on the pinned Fedora
44 Workstation x86_64 image (SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`) on
2026-10-31. The automated lifecycle checked candidate refusal without a run
journal, plan, explicit candidate apply, Fedora RPM signatures, root-run
`rpm -V`, status, repeat apply, restore, and exact RPM inventory recovery. All
four requested RPMs were absent at baseline. DNF added nine dependency package
identities; restore removed all nine. No existing RPM identity or version
changed.

The test refreshed systemd's view before querying Kismet. `kismet.service`
remained `not-found / inactive` before, during, and after apply; no `kismet`
system account appeared. RPM scriptlets and file-capability metadata were
recorded. No wireless adapter was attached and no capture, injection, key
cracking, or package executable ran.

The four operations remain opt-in and candidate-gated pending H042 review of
authorized radio scope, privileges, service ownership, and recovery.

Automated by
[`test_fedora_security_lab_wireless_batch_and_profile`](../../tests/acceptance/test_package_contract.py).
Transcript and target metadata:
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06q/fedora-44-workstation-x86_64/20261031T142543Z-test-fedora-security-lab-wireless-batch-and-profile-2c701672/`.

Catalog operation IDs in this accepted profile: `package.aircrack-ng`,
`package.cowpatty`, `package.kismet`, and `package.reaver`.
