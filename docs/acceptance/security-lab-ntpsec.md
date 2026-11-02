# Security Lab NTPsec package acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64,
2026-11-01.

Batch 06AK maps the Fedora Security Lab `ntpsec` member to
`package.ntpsec`. v3.0 manages signed RPM presence only. It does not enable or
start NTPsec, edit time-source configuration, synchronize the clock, or change
network state. H063 tracks service, configuration, clock, and sysuser recovery.

## Completion checks

- Confirm only `ntpsec` moved from unmapped and the opt-in profile contains
  only `package.ntpsec`.
- Verify candidate refusal without a journal; plan, apply, signature, `rpm -V`,
  binaries and default configuration; inactive/disabled `ntpd.service`; and
  unchanged chronyd state.
- Inspect RPM additions/removals, scriptlets, capabilities, units/timers, and
  the `ntp` user/group before and after restore. Verify status, unchanged
  repeat, restore, explicit install/remove, and package inventory recovery.
- Do not run NTPsec utilities or daemon, query peers, edit configuration,
  contact time servers, or change system time.

## VM evidence

Passed on the pinned disposable Fedora 44 Workstation x86_64 KVM target, image
SHA-256 `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
Candidate refusal created no journal. Apply installed only signed `ntpsec`
1.2.6-1.fc44; DNF made no dependency changes or pre-existing RPM updates.
Signature and root-run `rpm -V` passed. `/usr/bin/ntpd`, `/usr/bin/ntpq`, and
`/etc/ntp.conf` were present. `ntpd.service` remained inactive and disabled;
chronyd remained active and enabled. The RPM registers `ntpd.service` and
`ntp-wait.service` through Fedora's systemd update helper, and includes an
`ntp` sysusers definition. The `ntp` user/group were absent before apply and
persisted after removal (`/usr/sbin/nologin`, home `/var/lib/ntp`). No file
capabilities were set. Status, unchanged repeat, restore, explicit
install/remove, and exact RPM inventory recovery passed. No NTPsec executable,
daemon, peer, time source, or clock behavior was run.

Apply run ID `20261101T124331Z-2787-31144`, repeat
`20261101T124345Z-4161-13520`, restore `20261101T124346Z-4600-23873`, explicit
install `20261101T124350Z-5539-13625`, remove `20261101T124354Z-5994-13240`.
Transcript: `.tmp-vm-acceptance-security-06ak/fedora-44-workstation-x86_64/20261101T124300Z-test-package-apply-repeat-status-restore-and-remove-d20725f9/transcript.jsonl`
(SHA-256 `68c7b678f498230e7e3b60596d05507589e924734d5aa9317f758233bb6c66fc`).
The focused result was `1 passed` in 57.20 seconds. H063 tracks exact sysuser,
configuration, service, network, and clock recovery.
