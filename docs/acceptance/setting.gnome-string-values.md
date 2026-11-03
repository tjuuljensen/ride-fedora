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

## Legacy empty-region outcome

The v2 `RemoveGnomeRegion` function writes the explicit empty string. The
opt-in `gnome-region-reset` profile now carries that value through
`setting.gnome-region`; the run journal records the empty selected value,
captures the prior dconf override, and restores it only if the applied value
still matches. The Fedora 44 Workstation test passed for the empty-value apply
and restore to a seeded `en_US.UTF-8` region, as well as the existing locale
and window-layout lifecycle.

- Target image SHA-256:
  `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`
- Passing transcript:
  `.acceptance-runs/fedora-44-workstation-x86_64/20261102T134807Z-test-gnome-region-and-three-window-layouts-37d9273d/transcript.jsonl`
- Passing transcript SHA-256:
  `3283924793deba77affc35d0480e170f6d41b19afa107c68a0789dd1db597b73`
- Disposable overlay SHA-256:
  `bf1bf98d203e86775fae2f9b32c38c16d6508b56b741315f76ce48c1f7fd5a63`
- Source bundle SHA-256:
  `b84aa1343268630a6029aee66de174c9611a9bb44a91d585b96f523a336d9919`

The first run failed because its existing assertion expected the journal's
no-override state to be named `unset`; actual v3 state is `absent`. The
captured transcript was reviewed and retained:
`.acceptance-runs/fedora-44-workstation-x86_64/20261102T134139Z-test-gnome-region-and-three-window-layouts-7abfd941/transcript.jsonl`
(SHA-256 `557714896bdebca1528813a944c08adfbc1eae32e71e49f11a8405d946b62ffb`).
The assertion was corrected to the actual lifecycle state, then the full test
passed on a fresh disposable overlay. No persistent machine state changed.
