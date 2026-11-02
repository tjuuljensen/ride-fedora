# Security Lab Dislocker package acceptance

Batch 06X covers the signed Fedora 44 Workstation x86_64 Dislocker RPM as an
opt-in candidate. RIDE manages package presence only. Acceptance does not
attach or decrypt a volume, request or expose a recovery key, create decrypted
output, or mount data.

## Completion checks

- Verify exact source group membership and profile mapping.
- Verify candidate refusal creates no run journal.
- On the disposable Fedora 44 Workstation target, plan, apply, verify the RPM
  signature and files, query status, repeat apply, and restore.
- Inspect RPM scripts, file capabilities, dependencies, and changes to
  pre-existing RPMs.
- Confirm package inventory returns to its expected post-DNF state.

## VM evidence

Passed on 2026-10-31 with the pinned disposable target
`fedora-44-workstation-x86_64` (Fedora 44 Workstation, x86_64). Candidate
refusal, plan, apply, signed RPM and file checks, status, repeat, restore,
package-state recovery, and alternatives cleanup passed. Run IDs were
`20261031T145552Z-2480-9757` (apply), `20261031T145605Z-3266-21350`
(repeat), and `20261031T145606Z-3532-7366` (restore). DNF installed Dislocker
and 16 dependencies, including weak dependencies; restore removed all 17
packages. No pre-existing RPM changed. The Fedora scriptlet added and then
removed the `/usr/bin/dislocker` alternatives entry. No key or volume was
provided, and no encrypted data was accessed.

The retained transcript is
`.tmp-vm-acceptance-security-06x-verified/fedora-44-workstation-x86_64/20261031T145523Z-test-fedora-security-lab-dislocker-package-only-91313e50/transcript.jsonl`
(SHA-256 `f901669891415e38b847cf762e7553039a93dc0783bfe1b82ab6dad5e0842aed`);
pytest reported `1 passed`. H049 tracks key handling, source-volume access,
decrypted-output ownership and sizing, mount isolation, and cleanup before any
volume behavior is managed.
Catalog operation IDs in this accepted profile: `package.dislocker`.
