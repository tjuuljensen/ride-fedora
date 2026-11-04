# Security Lab host integrity and compliance acceptance

**Result: PASS (candidate)**

The opt-in `fedora-security-lab-host-integrity` profile passed on the pinned
Fedora 44 Workstation x86_64 image (SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`) on
2026-10-31. The automated lifecycle checked candidate refusal without a run
journal, plan, explicit candidate apply, RPM signatures, root-run `rpm -V`,
status, repeat apply, restore, and exact RPM inventory recovery. All five
requested RPMs were absent in the baseline. The final package inventory
returned to baseline with no pre-existing RPM identity or version changes.

DNF installed seven dependencies in addition to the five requested packages:
`apt-libs`, `opendbx`, `openscap`, `cronie`, `cronie-anacron`, `crontabs`, and
`s-nail`. The
transaction used about 733 MiB of additional installed space, mostly SCAP
Security Guide content. Installing the rkhunter dependency `cronie` enabled
`crond.service` (it remained inactive during the recorded run); restore removed
the dependency and returned the unit to its baseline `not-found` / `inactive`
state. This package scriptlet side effect is captured by the test.

The test did not run AIDE, chkrootkit, rkhunter, or OpenSCAP, initialize an
AIDE database, evaluate or remediate SCAP content, refresh scanner definitions,
or inspect host files. All five operations remain opt-in and candidate-gated
pending H039 review of scan behavior, generated data, network activity, and
recovery.

Automated by
[`test_fedora_security_lab_host_integrity_batch_and_profile`](../../tests/acceptance/test_package_contract.py).
Transcript and target metadata:
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06n-final/fedora-44-workstation-x86_64/20261031T141243Z-test-fedora-security-lab-host-integrity-batch-and-profile-57d36e57/`.
Catalog operation IDs in this accepted profile: `package.aide`, `package.chkrootkit`, `package.openscap-scanner`, `package.rkhunter`, `package.scap-security-guide`.
