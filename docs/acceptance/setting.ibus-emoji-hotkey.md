# `setting.ibus-emoji-hotkey` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 x86_64 Workstation,
2026-10-30. This medium-risk per-user setting changes only
`org.freedesktop.ibus.panel.emoji hotkey`; it never installs or removes the
Terminator RPM. Together with the separate `package.terminator` acceptance,
it covers the combined v2 source outcome. The pinned Fedora 44 Workstation image SHA-256 was
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
The disposable overlay was
`20261030T220524Z-test-terminator-ibus-hotkey-custom-and-unset-recovery-73603bfc`.
The catalog SHA-256 was
`98634599df97da6741a1e3c0e9f1657ab8b23cd3dbda5485348c8c9829ea39e4`.
The retained transcript under `.acceptance-runs/desktop-user-10-ibus/` and
`.acceptance-runs/desktop-user-10-ibus.xml` record one passing test.

The test verified the live `as` schema and writable user key, seeded a custom
hotkey, then checked plan, candidate-gate refusal, apply, journaled prior
override, repeat, conflict refusal after an intervening user change, preview,
and exact restore. A second path started with no user override and restored
that absence. The `terminator` RPM remained absent throughout. Focused mocked
tests covered a write that failed after mutation, locked state, missing
observation, and both recovery forms. The test ran as the non-root `ride-test`
user; RIDE did not alter another user or a system dconf default.

The test observed stored and effective values in a headless user session. It
did not visually confirm the emoji shortcut or a Terminator window; that is
[v3.1 item H003](../migrations/progress.md). Reviewer: RIDE migration agent.
See the [batch record](../migrations/desktop-user-10-terminator.md).
