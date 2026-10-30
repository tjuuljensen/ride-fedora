# UPower low-battery threshold acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 x86_64 Workstation,
2026-10-30. One `setting.upower-percentage-low` operation selects a validated
integer percentage. The checked-in examples select 15 and 20 independently.

The pinned Workstation image SHA-256 was
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
The disposable TCG overlay was
`20261030T224955Z-test-upower-threshold-profiles-and-owned-recovery-636e519f`;
candidate catalog SHA-256 was
`f87c6707f1cc9de8028bcbf7527a4e081081c31e5c7c27632b665230b4915ff5`.
The retained transcript under `.acceptance-runs/desktop-user-upower-01/`
and `.acceptance-runs/desktop-user-upower-01.xml` record one passing test.

The VM had `upower-1.91.1-1.fc44.x86_64` and its packaged
`UPower.conf.d/README.md` contract. It checked the untouched main config
hash, absent plan, candidate refusal, apply, private journal selected value,
exact owned drop-in contents, repeat, profile status, restore preview, and
restore to absent for each threshold. A deliberately changed 15-percent
drop-in caused restore conflict refusal; the test repaired its own disposable
fixture and restored normally. The handler's `systemctl try-restart
upower.service` completed during each change. Focused temporary-file tests
covered an existing owned 20-percent value, unowned file and competing
drop-in refusal, invalid critical threshold, and write/restart rollback.

The VM has no battery. This run establishes the declared configuration and
recovery lifecycle, not a user-visible low-battery warning transition.
[H030](../migrations/progress.md) keeps that hardware behavior in v3.1.
The operation remains an explicit opt-in candidate and never edits the
package-owned `/etc/UPower/UPower.conf`.

Reviewer: RIDE migration agent. See the [batch record](../migrations/desktop-user-upower-01.md).
