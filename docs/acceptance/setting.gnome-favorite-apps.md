# GNOME favorite applications acceptance

`setting.gnome-favorite-apps` is a configurable opt-in Fedora 44 Workstation
x86_64 setting. It accepts a JSON array of up to 20 unique `.desktop` IDs,
converts only validated IDs into a GNOME `as` value, and uses the normal RIDE
run journal to restore the exact prior dconf override. It does not claim that
every well-formed desktop ID is installed; H085 tracks desktop visual review.

Mocked tests cover GVariant conversion, invalid and duplicate IDs, first
apply, and exact prior-list restoration. Fedora 44 Workstation x86_64 acceptance
passed plan, candidate gating, apply, repeat, conflict preservation, and exact
restore. The captured transcript is
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-desktop-user-03-favorites-prereq/fedora-44-workstation-x86_64/20261101T200600Z-test-configurable-favorites-preserve-and-restore-exact-list-59b509f2/transcript.jsonl`
(SHA-256 `3b7dfd73bce5f01a295989d38e6b65e23116702bf08493514d219d4b316542d7`);
the Fedora 44 Workstation image SHA-256 is
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.

Sources: [GNOME Shell](https://gitlab.gnome.org/GNOME/gnome-shell),
[GNOME settings schema](https://gitlab.gnome.org/GNOME/gsettings-desktop-schemas).
