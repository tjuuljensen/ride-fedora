# `package.terminator` acceptance

Status: **PASS; package-only opt-in candidate** on Fedora 44 x86_64
Workstation, 2026-10-30. Risk for this separate Fedora RPM deployment is
medium; the combined v2 package and iBus hotkey outcome remains a high-risk
v3.0 gap. Fedora's signed
[`terminator`](https://packages.fedoraproject.org/pkgs/terminator/terminator/)
RPM declares GPL-2.0-only.

The disposable TCG overlay
`20261030T215043Z-test-terminator-package-without-ibus-setting-fffb3906`
used pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`
and candidate catalog SHA-256
`d0d7e1dd5ac75e77492596d3a3fc7708aeff9fc87e1621c74fd3adca37afcf32`.
The retained transcript under `.acceptance-runs/desktop-user-10-terminator/`
and `.acceptance-runs/desktop-user-10-terminator.xml` record one passing test.

The RPM was absent at baseline. Plan, candidate-gated apply, RPM signature,
`rpm -V`, desktop launcher, installed status, unchanged repeat, restore,
and explicit install/remove passed. Installing introduced `terminator` and
`keybinder3`; both inverse paths returned the RPM inventory exactly to
baseline. No pre-existing RPM changed or disappeared. The unchanged DNF
handler's mocked failure behavior is reused from the base package checks.
This test checked package and launcher presence; it did not exercise a GNOME
terminal window or the user's iBus setting. A brief visual review belongs to
[v3.1 item H003](../migrations/progress.md) if the package remains a candidate.
Reviewer: RIDE migration agent.

The [batch record](../migrations/desktop-user-10-terminator.md) retains the
separate exact prior-hotkey recovery gate before the combined v2 outcome can
count as operable.
