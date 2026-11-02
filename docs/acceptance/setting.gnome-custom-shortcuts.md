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
conflict refusal, restore, and profile removal. It verified that shortcuts
added by the user after RIDE apply remain after removal. The captured transcript
is
`.tmp-vm-acceptance-desktop-user-03-shortcuts-verified/fedora-44-workstation-x86_64/20261101T221533Z-test-custom-shortcuts-merge-and-restore-only-ride-owned-entries-9d825a87/transcript.jsonl`
(SHA-256
`518b38d9530ce89839646d156ed6d4fce2f9309e947b4fb476129eda1beed4a3`); the
Fedora 44 Workstation image SHA-256 is
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.

The VM verified the GSettings values and lifecycle. It did not press the
shortcuts in a visible GNOME session or verify application dispatch; H089
tracks that brief visual and conflict review. Keep the operation opt-in and
outside the base profile.
