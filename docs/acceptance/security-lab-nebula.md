# Security Lab Nebula package acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64,
2026-11-01.

Batch 06AJ maps the Fedora Security Lab `nebula` member to
`package.nebula`. v3.0 manages the Fedora signed RPM only. It does not create
configuration or certificates, start or enable the service, add interfaces or
routes, or join an overlay network.

## Completion checks

- Confirm only `nebula` moved from unmapped and the opt-in profile contains only
  `package.nebula`.
- Verify candidate refusal without a journal, plan, apply, Fedora RPM
  signature, `rpm -V`, executable and sample configuration presence, inactive
  and disabled `nebula.service`, status, unchanged repeat, restore, explicit
  install/remove, and exact RPM inventory recovery.
- Inspect dependencies, scriptlets, file capabilities, and unit ownership.
- Do not run Nebula, its certificate or service tools, or any network behavior.

## VM evidence

Passed on the pinned Fedora 44 Workstation x86_64 KVM target, image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
Candidate refusal created no journal. Apply installed only signed `nebula`
1.11.2-1.fc44; DNF made no dependency changes or pre-existing RPM updates.
Signature and root-run `rpm -V` passed. The executable, sample config, and
systemd unit were present. Fedora's RPM scriptlets register the unit through
the systemd update helper; it remained inactive and disabled. No file
capabilities were set. Status, unchanged repeat, restore, explicit
install/remove, and exact RPM inventory recovery passed. No Nebula or
certificate tools were run and no network behavior was exercised.

Apply run ID `20261101T123725Z-2567-29780`, repeat
`20261101T123739Z-3612-28031`, restore `20261101T123740Z-4048-17177`.
Transcript: `.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06aj/fedora-44-workstation-x86_64/20261101T123655Z-test-package-apply-repeat-status-restore-and-remove-a7614119/transcript.jsonl`
(SHA-256 `4cba687cb5906636290a15bd8b6b2b544b981937776bec7ee2f81130eb5cf219`).
The focused result was `1 passed` in 55.70 seconds. H062 tracks later
configuration, certificate, overlay, and service recovery work.
