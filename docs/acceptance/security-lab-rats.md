# Security Lab RATS package acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64,
2026-11-01.

Batch 06AN maps Fedora Security Lab `rats` to the Fedora 44 signed RATS
2.4-31.fc44 package. Its upstream is an old Google Code export. v3.0 preserves
it as an opt-in candidate and manages package presence only; it does not run
RATS or scan source code. Fedora's existing Flawfinder is a maintained
C/C++-only alternative, not a full replacement for RATS' advertised language
coverage. H065 tracks an upstream and analyzer comparison.

## Completion checks

- Confirm only `rats` moved from unmapped and the profile contains only
  `package.rats`.
- Verify refusal, plan, apply, signature, `rpm -V`, executable and bundled XML
  vulnerability database, status, repeat, restore, explicit remove, and exact
  package inventory recovery.
- Inspect dependencies, scriptlets, file capabilities, and package ownership.
- Do not execute RATS or its bundled vulnerability database against any source.

## VM evidence

Passed on the pinned disposable Fedora 44 Workstation x86_64 KVM target, image
SHA-256 `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae8935ffca7c178`.
Candidate refusal created no journal. Apply installed only signed Fedora RPM
`rats` 2.4-31.fc44; it had no dependencies, scriptlets, systemd units, or file
capabilities. `/usr/bin/rats` and the bundled XML databases for C, OpenSSL,
Perl, PHP, Python, and Ruby were present. Signature and `rpm -V` passed. Status,
unchanged repeat, restore, explicit install/remove, and exact RPM inventory
recovery passed. RATS was not executed and no source code was scanned.

Apply run ID `20261101T124940Z-2567-3472`, repeat
`20261101T124951Z-3456-21382`, restore `20261101T124953Z-3892-18065`, explicit
install `20261101T124956Z-4504-32009`, remove `20261101T124958Z-4806-2250`.
Transcript: `.tmp-vm-acceptance-security-06an/fedora-44-workstation-x86_64/20261101T124910Z-test-package-apply-repeat-status-restore-and-remove-1ec61e3b/transcript.jsonl`
(SHA-256 `2cb52f348573b9e0d1042fab2bc90793a3a2e09929cffd8a82d79dcbac85dc0a`).
The focused result was `1 passed` in 50.51 seconds. H065 tracks the old
upstream and the maintained alternative review.
