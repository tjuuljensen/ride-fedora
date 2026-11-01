# GNOME region and window-button string acceptance

Status: **PASS; operable opt-in candidates** on Fedora 44 x86_64 Workstation,
2026-10-30, for `setting.gnome-region` and
`setting.gnome-window-buttons`. One `setting.gnome-window-buttons` operation
accepts the three owner-kept v2 layouts as exclusive profile values. The
region operation accepts a validated installed locale; its checked-in profile
selects `da_DK.UTF-8`.

The pinned Workstation image SHA-256 was
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
The disposable TCG overlay was
`20261030T222417Z-test-gnome-region-and-three-window-layouts-cdf7b890`;
candidate catalog SHA-256
`210927377133d200da39196b29bd4344aa6da9290fe419635f006525c8275239`.
The transcript under `.acceptance-runs/desktop-user-string-01/` and
`.acceptance-runs/desktop-user-string-01.xml` record one passing shared test.

The VM verified both live `type s` schemas, writable keys, and the installed
Danish locale. As the non-root `ride-test` user, it checked plan, candidate
refusal, apply, journaled selected value and custom prior override, repeat,
conflict refusal, preview, and exact restore for region. It also restored an
unset region key to the unset state. All three window profiles passed plan,
apply, repeat, and restoration of a seeded custom button layout. Mocked tests
covered invalid/missing values, unavailable locale, duplicate exclusive
layout choices, a locked key, and a write failure after mutation. The run
signature binds the chosen value, while the private journal preserves the
prior user override as data rather than executable shell text.

This headless test verified stored and effective values, not the rendered
window controls or region-dependent application formats. A brief desktop
review remains [v3.1 item H003](../migrations/progress.md). The separate
owner-deferred remove-only `GnomeRegion` outcome is not closed by this test.
Reviewer: RIDE migration agent. See the [batch record](../migrations/desktop-user-string-01.md).
