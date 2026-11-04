# Security Lab data sanitizer package acceptance

Batch 06AA covers `nwipe`, `scrub`, and `wipe` as Fedora 44 Workstation
x86_64 opt-in candidate RPM operations. This is an isolated package-only
batch. RIDE does not enumerate devices, open files for erasure, or run any
sanitization tool.

## Completion checks

- Verify exact source group membership and isolated profile mapping.
- Verify candidate refusal creates no run journal.
- On the disposable Fedora 44 Workstation target, plan, apply, verify RPM
  signatures and files, query status, repeat apply, and restore.
- Inspect RPM scripts, file capabilities, dependencies, and existing RPM
  changes.
- Confirm requested package state and mount table return to the expected
  post-DNF state after restore.

## VM evidence

Passed on 2026-10-31 with the pinned disposable target
`fedora-44-workstation-x86_64` (Fedora 44 Workstation, x86_64). Candidate
refusal, plan, apply, RPM signatures, root-run file checks, status, repeat,
restore, package-state recovery, and mount-table stability passed. `nwipe` and
`wipe` were installed then removed; `scrub` was already installed and remained
unchanged. Nwipe added `libconfig`, `smartmontools`, and
`smartmontools-selinux`; restore removed all three. No pre-existing RPM
changed. None of the requested packages declared file capabilities or RPM
scriptlets. The mount table was identical before, during, and after. No device
was enumerated and no sanitizer was run.

The retained transcript is
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06aa/fedora-44-workstation-x86_64/20261031T150517Z-test-fedora-security-lab-data-sanitizers-batch-and-profile-207300c9/transcript.jsonl`
(SHA-256 `56651aa78f098e3e5e75cfd8607e83dad193b5299ccc8070a69ac33beb024309`);
pytest reported `1 passed`. H052 tracks explicit-target confirmation, media
limitations, authorization, and recovery before these tools are operated.
Catalog operation IDs in this accepted profile: `package.nwipe`, `package.scrub`, `package.wipe`.
