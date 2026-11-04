# Security Lab filesystem utilities acceptance

Batch 06W covers `extundelete`, `hfsutils`, `ntfs-3g`, and `ntfsprogs` as
Fedora 44 Workstation x86_64 opt-in candidate RPM operations. RIDE manages
package presence only. Acceptance does not attach disks, mount filesystems,
run recovery or repair utilities, or access user data.

## Completion checks

- Verify exact source group membership and profile mapping.
- Verify candidate refusal creates no run journal.
- On the disposable Fedora 44 Workstation target, plan, apply, verify RPM
  signatures and files, query status, repeat apply, and restore.
- Inspect RPM scripts and file capabilities; record dependencies and changes
  to pre-existing RPMs.
- Confirm mount table and requested package state return to their expected
  post-DNF state after restore.

## VM evidence

Passed on 2026-10-31 with the pinned disposable target
`fedora-44-workstation-x86_64` (Fedora 44 Workstation, x86_64). Candidate
refusal, plan, apply, signed RPM and file checks, status, repeat, restore, and
package-state checks passed. The profile installed `extundelete` and
`hfsutils`; `ntfs-3g` and `ntfsprogs` were already installed and remained
unchanged. No dependencies or pre-existing RPM changes were observed. None of
the four RPMs declares file capabilities or scriptlets. The mount table was
identical before, during, and after the lifecycle. Run IDs were
`20261031T145224Z-2849-28257` (apply), `20261031T145243Z-5002-11571`
(repeat), and `20261031T145244Z-5606-18004` (restore).

The retained command transcript is
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06w/fedora-44-workstation-x86_64/20261031T145154Z-test-fedora-security-lab-filesystem-tools-batch-and-profile-564ebe0e/transcript.jsonl`
(SHA-256 `d51013d1666ee6d875c41f4ac28573de066eb7ca41f45f09eeadd5fc4a49609d`);
pytest reported `1 passed`. No filesystem, recovery workflow, or user data was
accessed. H048 tracks the separate review needed before removing candidate
gates, including image-first procedures, read-only/source-volume boundaries,
and isolated recovery destinations.

Fedora describes upstream extundelete as no longer maintained and limited on
modern ext4. The Fedora RPM path is retained for v3.0; a maintained alternative
review is queued for v3.1.
Catalog operation IDs in this accepted profile: `package.extundelete`, `package.hfsutils`, `package.ntfs-3g`, `package.ntfsprogs`.
