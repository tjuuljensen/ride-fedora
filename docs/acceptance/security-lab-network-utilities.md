# Security Lab network utilities acceptance

**Result: PASS**

Disposable VM run: PASS on Fedora 44 Workstation x86_64.
Pinned image SHA-256: `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
Date: 2026-10-31.

Operations: `package.bmon`, `package.fping`, `package.iftop`, `package.lnav`,
and `package.nload`, selected by the opt-in
`fedora-security-lab-network-utilities` profile. The profile is not part of a
base profile.

## Checks and result

- Plan listed all five operations as candidates. Applying without
  `--allow-candidate` failed with the expected explicit opt-in message and
  created no run journal.
- Applying with `--allow-candidate` completed successfully. The VM was clean
  for all five package names before apply; the run changed each to installed.
- Each installed RPM exposed repository signature metadata and passed
  `rpm -V`. Local usage/version probes succeeded for every binary. `bmon
  --help` returns exit code 1 while emitting the expected help text; the probe
  checks the help content as well as the accepted 0/1 exit status.
- Status reported installed for each operation. A repeated apply completed
  with all five operations unchanged.
- Restore completed and removed the five packages. DNF also removed
  `libconfuse`, the dependency introduced only for bmon.
- RPM inventory contained 1,913 package identities before the run, 1,919
  after apply (the five selected packages plus `libconfuse`), and 1,913 after
  restore. The restored inventory exactly matched the baseline; no package
  upgrades or other residue remained.

The exact command transcript and VM overlay for this session are retained
under `.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06e/` in the working tree. The profile
acceptance is implemented by
[`test_fedora_security_lab_network_utilities_batch_and_profile`](../../tests/acceptance/test_package_contract.py).
