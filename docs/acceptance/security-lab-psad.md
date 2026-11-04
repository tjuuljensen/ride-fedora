# Security Lab PSAD package acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64,
2026-11-01.

Batch 06AM maps the Fedora Security Lab `psad` member to `package.psad`.
v3.0 manages the signed RPM only. It does not start the daemon, read firewall
logs, send alerts, or add/remove firewall rules. H064 tracks configuration,
firewall, and alert recovery.

## Completion checks

- Confirm only `psad` moved from unmapped and the opt-in profile contains only
  `package.psad`.
- Verify candidate refusal, plan, apply, Fedora signature, `rpm -V`, executable
  and default config presence, inactive/disabled `psad.service`, unchanged
  nftables ruleset, status, repeat, restore, explicit install/remove, and exact
  package inventory recovery.
- Inspect DNF additions/removals, scriptlets, file capabilities, service state,
  and user/state residue.
- Do not run PSAD, read firewall logs, send packets, generate alerts, or change
  firewall rules.

## VM evidence

Passed on the pinned disposable Fedora 44 Workstation x86_64 KVM target, image
SHA-256 `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae8935ffca7c178`.
Candidate refusal created no journal. Apply installed signed `psad`
2.4.6-24.fc44 and 14 dependency/weak-dependency RPMs, including ESMTP and
s-nail; restore removed exactly those 15 packages. No pre-existing RPM was
removed or upgraded. Signature and root-run `rpm -V` passed. The executable,
default configuration, and systemd unit were present. `psad.service` remained
inactive and disabled. The nftables ruleset was byte-for-byte unchanged before
and after apply, restore, and explicit install/remove. No `psad` user or group
was present before or after removal; no file capabilities were set. Status,
unchanged repeat, restore, explicit install/remove, and exact RPM inventory
recovery passed. PSAD did not run; no logs, packets, alerts, or firewall rules
were accessed or changed.

Apply run ID `20261101T124703Z-2733-17419`, repeat
`20261101T124721Z-3785-32355`, restore `20261101T124722Z-4223-23246`, explicit
install `20261101T124730Z-5119-26126`, remove `20261101T124740Z-5524-9326`.
Transcript: `.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06am/fedora-44-workstation-x86_64/20261101T124633Z-test-package-apply-repeat-status-restore-and-remove-4d9717dd/transcript.jsonl`
(SHA-256 `e9172d44c4e2e4d40f94e4be1bfb4a813e11ec6c75f4403ca42d5d58e06a9612`).
The focused result was `1 passed` in 74.61 seconds. H064 tracks later PSAD
configuration, firewall ownership, log and alert behavior, and recovery.
