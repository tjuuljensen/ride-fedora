# Security Lab offline password recovery acceptance

**Result: PASS (candidate)**

The opt-in `fedora-security-lab-password-recovery` profile passed on the
pinned Fedora 44 Workstation x86_64 image (SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`) on
2026-10-31. The automated lifecycle checked candidate refusal without a run
journal, plan, explicit candidate apply, Fedora RPM signatures, root-run
`rpm -V`, status, repeat apply, restore, and exact RPM inventory recovery. All
five requested RPMs were absent at baseline. No existing RPM identity or
version changed; restore returned the package inventory to baseline.

DNF installed 13 dependencies for Ophcrack's Qt desktop package: ten required
and three weak dependencies (`gstreamer1-plugins-good-qt`,
`qadwaitadecorations-qt5`, and `qt5-qttranslations`). Restore removed all 13.
John the Ripper is published in Fedora 44 as RPM version `1.9.0-12.fc43`; its
Fedora 44 repository signature and file verification passed on the declared
target. No evidence files, hashes, Windows hives, PDFs, or BIOS/CMOS state were
read. No recovery command or GUI was launched.

All five operations remain opt-in and candidate-gated pending H041 review of
authorized evidence scope and private input/output handling.

Automated by
[`test_fedora_security_lab_password_recovery_batch_and_profile`](../../tests/acceptance/test_package_contract.py).
Transcript and target metadata:
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06p/fedora-44-workstation-x86_64/20261031T142320Z-test-fedora-security-lab-password-recovery-batch-and-profile-8402bebe/`.
Catalog operation IDs in this accepted profile: `package.bkhive`, `package.cmospwd`, `package.john`, `package.ophcrack`, `package.pdfcrack`.
