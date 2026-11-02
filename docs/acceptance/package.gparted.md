# GParted package acceptance

`package.gparted` is an isolated Fedora 44 Workstation x86_64 candidate RPM
operation from Security Lab batch 06AD. RIDE manages package presence only; it
never launches GParted or modifies storage.

## Completion checks

- Confirm exact source group membership and isolated profile mapping.
- Confirm candidate refusal creates no run journal.
- Plan, apply, verify the Fedora RPM signature and root-run `rpm -V`, query
  status, repeat, restore, and compare package inventory and mount table.
- Inspect RPM scripts, file capabilities, service units, dependencies, and
  existing RPM changes. Do not enumerate devices or invoke partition tools.

## VM evidence

Passed on 2026-10-31 using the disposable `fedora-44-workstation-x86_64` VM.
Candidate refusal created no journal; apply installed Fedora `gparted`
1.7.0-3.fc44, repeat reported unchanged, and restore removed it. There were no
new dependencies or changes to existing RPMs. The RPM had an RSA/SHA256 header
signature, passed root-run `rpm -V`, had no file capabilities or scriptlets,
and shipped no system service units. The mount table was unchanged. GParted
was not launched; no block devices were enumerated and no partition tool was
invoked. Pytest reported `1 passed`.

Run IDs: apply `20261031T151852Z-2490-3335`, repeat
`20261031T151904Z-3275-18567`, restore `20261031T151904Z-3542-17949`. Transcript:
`.tmp-vm-acceptance-security-06ad/fedora-44-workstation-x86_64/20261031T151823Z-test-fedora-security-lab-storage-tools-batch-and-profile-5dbc7580/transcript.jsonl` (SHA-256 `42a3b49f4f862e4c2132ed7f496047b9531f2a3cb074d0301fa0d4b3865f1956`). H055 retains the storage behavior
safety and recovery gate and reviews Fedora's 1.7.0 package against upstream
1.8.1.
