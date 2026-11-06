# GNOME custom shortcuts acceptance

`setting.gnome-custom-shortcuts` is an opt-in candidate for Fedora 44
Workstation x86_64. It writes user-owned custom keybinding entries under
deterministic RIDE paths and merges the configured `show-desktop` and
`switch-windows` bindings with values already present. A user ownership record
stores the original lists and the exact entries RIDE added. Removal drops only
those entries and preserves later user additions. The operation refuses to
restore an entry changed outside RIDE, and validates that its ownership record
is owned by the current user with mode 0600.

Focused mocked tests cover bounded configuration, apply/repeat/remove,
preservation of prior user state, rollback after a partial apply failure,
refusal after an external edit, and refusal of unsafe ownership-record
permissions.

Fedora 44 Workstation x86_64 disposable-VM acceptance passed plan, candidate
gating, apply, journaled value and mode-0600 owner record, status, repeat,
conflict refusal, and restore. It verified that shortcuts added by the user
after RIDE apply remain after removal.

ALIGN-03 acceptance additionally passed direct `unset`, repeat-unset, restore
of the unset run to the selected configured shortcuts, and restore of the
original apply run to absent. It verified the user's original keybinding arrays
were restored after unset. Transcript:
`.acceptance-runs/align03-owned-unset/fedora-44-workstation-x86_64/20261105T150211Z-test-custom-shortcuts-merge-and-restore-only-ride-owned-entries-957a00f7/transcript.jsonl`
(SHA-256 `972db54594512f4160fd9f10e7db8946dd9c5b83c33a6dcdbb2fd25f09c95997`); the
Fedora 44 Workstation image SHA-256 is
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.

The VM verified the GSettings values and lifecycle. It did not press the
shortcuts in a visible GNOME session or verify application dispatch; H089
tracks that brief visual and conflict review. Keep the operation opt-in and
outside the base profile.
