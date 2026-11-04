# AFF tools package acceptance

`package.afftools` is an isolated Fedora 44 Workstation x86_64 candidate RPM
operation from Security Lab batch 06AE. RIDE manages package presence only; it
never opens or transforms forensic images.

## Completion checks

- Confirm exact source group membership and isolated profile mapping.
- Confirm candidate refusal creates no run journal.
- Plan, apply, verify the Fedora RPM signature and root-run `rpm -V`, query
  status, repeat, restore, and compare package inventory and mount table.
- Inspect RPM scripts, file capabilities, service units, dependencies, and
  existing RPM changes. Do not open, convert, mount, hash, or process images.

## VM evidence

Passed on 2026-10-31 using the disposable `fedora-44-workstation-x86_64` VM.
Candidate refusal created no journal; apply installed `afftools` 3.7.22-4.fc44
and its `afflib` dependency; repeat reported unchanged; restore removed both.
No pre-existing RPM changed. The RPM had an RSA/SHA256 header signature, passed
root-run `rpm -V`, and had no file capabilities, scriptlets, or service units.
Package inventory and mount table were unchanged after restore. No AFF tool was
run and no evidence image was accessed. Pytest reported `1 passed`.

Run IDs: apply `20261031T152052Z-2480-29204`, repeat
`20261031T152104Z-3261-26303`, restore `20261031T152105Z-3528-22584`. Transcript:
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06ae/fedora-44-workstation-x86_64/20261031T152023Z-test-fedora-security-lab-forensic-images-batch-and-profile-47311ff1/transcript.jsonl` (SHA-256 `14eac5aa43580daf4f34a4921127a8e08442a9ed122a7aac29bb2976ea3a6c8d`). H056 tracks image provenance,
read-only handling, cryptographic material, and recovery before AFF behavior
is managed.
