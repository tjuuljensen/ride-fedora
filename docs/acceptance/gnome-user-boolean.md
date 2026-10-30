# GNOME boolean user-setting acceptance

Status: **PASS; operable opt-in candidates** on Fedora 44 x86_64 Workstation,
2026-10-30, for `setting.gnome-clock-date`,
`setting.gnome-calendar-week-numbers`, `setting.gnome-primary-paste`,
`setting.gnome-location`, and `setting.gnome-problem-reporting`.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T133145Z-test-gnome-boolean-profiles-apply-repeat-and-restore-d82fbc54`;
candidate catalog SHA-256
`d7bb48ac35a65b67767093bebb9738066fe06e453df48c316e0ff023945f297c`;
source bundle SHA-256
`ddb863a6802ab23b57eaf38537621e6a8e2045cb4ede558d97fe63cdd9dc648f`.
The retained VM transcript records one passing test. The failed first run
stopped before mutation because the headless SSH image lacked
`dbus-run-session`; the test now installs `dbus-daemon` into the disposable
overlay to supply that helper. The GNOME desktop's user bus is not changed.

The test established the opposite boolean baseline for all five keys, then
passed plan, candidate-gate refusal, apply, journal inspection, unchanged
repeat, status, restore preview, restore, and final baseline verification for
both `gnome-shell-preferences` and `gnome-privacy`. All changes ran as the
non-root `ride-test` user. The journal stored effective before and after
values, and the two profiles remained outside `default`.

The test did not render a desktop or distinguish an explicit dconf value from
an unset key with the same effective value. Those checks are H018 in the
[v3.1 queue](../migrations/progress.md). See the
[batch review](../migrations/desktop-user-boolean.md).
