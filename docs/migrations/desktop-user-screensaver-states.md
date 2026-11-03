# GNOME screensaver enable and disable states

Status: **operable on Fedora 44 Workstation x86_64**. The v2 `EnableScreenSaver` and
`DisableScreensaver` functions write the same three user settings with opposite
values. Both are retained in v3.0 as independent opt-in profiles rather than
running in sequence in a default profile.

`EnableScreenSaver` sets `idle-delay` to `uint32 300`,
`idle-activation-enabled` to `true`, and `lock-enabled` to `true`.
`DisableScreensaver` sets those keys to `uint32 0`, `false`, and `false`.
Neither function changes `lock-delay`; v3 preserves that fourth user value.

## Completion checks defined before implementation

- Reuse `setting.gnome-lock-timing` with explicit `screensaver-enabled` and
  `screensaver-disabled` values. Keep both choices in separate opt-in profiles.
- Snapshot, apply, verify, rollback, and restore only the three values each
  legacy function owns. Leave `lock-delay` unchanged, including if an unrelated
  user change occurs after apply.
- Mock apply, repeat, status, exact restore, conflict refusal, and partial-write
  failure for both states. Validate snapshots with exactly the three owned
  keys; existing timing profiles retain their four-key snapshot.
- On Fedora 44 x86_64 Workstation, seed non-default values, apply each profile,
  verify all three effective settings and unchanged `lock-delay`, repeat,
  restore, and verify the full seeded state. No visual session behavior is
  claimed from headless evidence.
- Update both source outcomes, generated progress and operation docs, and
  Windows alignment. Keep H092 as the v3.1 visual review.

Mocked lifecycle checks and disposable Workstation acceptance passed for both
states. Acceptance verified apply, repeat, status, lock-delay preservation,
and exact restore. The run evidence is recorded in
[`setting.gnome-lock-timing.md`](../acceptance/setting.gnome-lock-timing.md).
H092 retains a brief visible behavior review.

The four-key timing profiles continue to set and restore `lock-delay`; the two
legacy state profiles do not own or modify it. Both remain opt-in and outside
the base profiles.
