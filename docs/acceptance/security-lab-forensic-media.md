# Security Lab forensic media package acceptance

**Result: PASS**

Candidate and supported-path lifecycles passed on disposable Fedora 44
Workstation x86_64 VMs on 2026-10-31. The supported-path run applied without
candidate bypass.

Operations: `package.dcfldd`, `package.ddrescue`, `package.foremost`, and
`package.hexedit`, selected by the opt-in
`fedora-security-lab-forensic-media` profile. No base profile selects them.

## Candidate lifecycle result

- Applying without `--allow-candidate` was refused without creating a run
  journal. Explicit candidate apply and later supported apply completed for
  all four packages. Each Fedora RPM had signature metadata and passed
  `rpm -V`.
- Local probes passed for `dcfldd --help`, `ddrescue --version`, `foremost
  -h`, and `hexedit --help`. Hexedit returned 1 while printing its usage;
  the test accepted the observed exit and checked the output. No file or
  device was supplied to any tool.
- Status reported installed and repeat apply reported all packages unchanged.
  Restore removed all four RPMs and returned the exact 1,913-package
  inventory from 1,917 after installation. The transaction added exactly four
  packages and changed no pre-existing RPM or dependency.
- No disk, block device, image, recovered output, or user file was read,
  written, wiped, carved, or edited.

The lifecycle is automated by
[`test_fedora_security_lab_forensic_media_batch_and_profile`](../../tests/acceptance/test_package_contract.py).
The passing candidate transcript and disposable overlay are under
`.tmp-vm-acceptance-security-06j/fedora-44-workstation-x86_64/20261031T130644Z-test-fedora-security-lab-forensic-media-batch-and-profile-e513f638/`.
The passing supported-path transcript and overlay are under
`.tmp-vm-acceptance-security-06j-supported-retry/fedora-44-workstation-x86_64/20261031T131809Z-test-fedora-security-lab-forensic-media-batch-and-profile-45e4f2a2/`.
