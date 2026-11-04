# Security Lab default editor acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64,
2026-11-01.

Batch 06AI maps the Fedora Security Lab member `default-editor` to the
concrete Fedora 44 Workstation RPM operation `package.nano-default-editor`.
The RPM sets `EDITOR` to nano for common shells when the user has not selected
an editor; RIDE manages the Fedora package and does not edit shell startup
files directly. This is an opt-in candidate.

## Completion checks

- Confirm the source member maps to this single operation and profile.
- In the pinned disposable Fedora 44 Workstation VM, remove only the known
  `nano`, `nano-default-editor`, and `default-editor` packages to create an
  absent baseline; reject any other package removal.
- Verify candidate refusal without a journal, plan, apply, signed RPM and
  `rpm -V`, `EDITOR=/usr/bin/nano` in a clean login shell, preservation of an explicit
  `EDITOR=vi`, status, unchanged repeat, restore, explicit remove, and exact
  package inventory recovery.
- Inspect dependencies, scriptlets, file capabilities, owned shell files, and
  service-unit ownership. Do not launch an editor or write user files.

## VM evidence

Passed on the pinned Fedora 44 Workstation x86_64 KVM target, image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
Candidate refusal created no journal. Preparation removed exactly
`default-editor`, `nano-default-editor`, and `nano`; apply installed signed
`nano` 8.7.1-2.fc44 plus `nano-default-editor` 8.7.1-2.fc44. Signature and
root-run `rpm -V` checks passed. A clean Bash login set `EDITOR=/usr/bin/nano`,
while an explicit `EDITOR=vi` remained `vi`. The status and repeat checks
passed; restore and explicit remove returned the complete RPM inventory to the
prepared baseline. The package had no scriptlets, file capabilities, or
systemd units. Its owned Bash, CSH, and fish files were present; CSH/fish
runtime behavior remains queued under H061. No editor was opened and no user
files were written.

Apply run ID `20261101T123337Z-2987-2640`, repeat
`20261101T123350Z-4078-136`, restore `20261101T123351Z-4515-30886`.
Transcript: `.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06ai/fedora-44-workstation-x86_64/20261101T123303Z-test-package-apply-repeat-status-restore-and-remove-fd462103/transcript.jsonl`
(SHA-256 `fd47f316a2f396cdc9e4c293b70af12add59b411bd0e85f2c154d8e5aa0bef6b`).
The final focused result was `1 passed`. The first run used the shorthand
expected value `nano` and stopped after observing Fedora's actual `/usr/bin/nano`
value; that assertion was corrected and the check passed on a fresh overlay.
