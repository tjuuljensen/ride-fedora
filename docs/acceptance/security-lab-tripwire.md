# Security Lab Tripwire package acceptance

Status: **CANDIDATE LIFECYCLE PASSED** on Fedora 44 Workstation x86_64,
2026-11-01.

Batch 06AO maps the Fedora Security Lab `tripwire` member to
`package.tripwire`. v3.0 manages the Fedora signed RPM only. No keys, policy,
or baseline are initialized; no scheduled check or filesystem scan is run.
H066 tracks the security-sensitive initialization and recovery contract.

## Completion checks

- Confirm only `tripwire` moved from unmapped and the opt-in profile contains
  only `package.tripwire`.
- Verify refusal, plan, apply, signature, `rpm -V`, executable and default
  configuration presence, absence of generated keys/database, status, repeat,
  restore, explicit remove, and exact RPM inventory recovery.
- Inspect scriptlets, file capabilities, cron/systemd activation, and generated
  files. Do not generate keys, initialize policy/baseline, or execute the daily
  check or scanner.

The first attempt exposed Fedora's post-install substitution of `localhost`
with the machine hostname in `twpol.txt`; acceptance now verifies this exact
expected RPM config change. The successful lifecycle installed only the
signed RPM, passed repeat and restore, and returned the RPM inventory to its
baseline after both restore and explicit removal. RPM removal preserves the
sample policy as an unowned `twpol.txt.rpmsave`; the test verifies its
hostname and confirms no private keys or `.twd` baseline remain. The daily
check script requires the absent host database before scanning. No key
generation, baseline initialization, or scan was performed.

Transcript: `../.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06ao-verified/fedora-44-workstation-x86_64/20261101T125939Z-test-package-apply-repeat-status-restore-and-remove-69bfa7b3/transcript.jsonl`
(SHA-256 `432eb5613b45126f39716642445080c0302140c9884c39dd0fd47064cbd7eccb`).

## VM evidence

Planned on the pinned disposable Fedora 44 Workstation x86_64 KVM target, image
SHA-256 `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae8935ffca7c178`.
The transcript and package-side-effect observations will be recorded after the
pilot.
