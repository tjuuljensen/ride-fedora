# Desktop user favorites list

The v2 `SetGnomeCustomFavorites` replaced the complete user favorites array,
including retired Atom and entries that may not exist on a current workstation.
The v3 opt-in `setting.gnome-favorite-apps` accepts a JSON array of desktop IDs
(up to 20 entries), validates the IDs, writes a GNOME `as` value, and journals
the exact prior dconf user override. Use `ride restore --run-id` to recover the
prior list; a later user edit is treated as a restore conflict.

The [example profile](../../profiles/fedora-custom-favorites.json) is outside
`default`. Replace its `value` list with the IDs installed on the target. An
unknown but well-formed desktop ID may not show an application; H085 tracks a
visual review of current app IDs and ordering. The `GNOME favorite apps`
[acceptance record](../acceptance/setting.gnome-favorite-apps.md) records the
passing Fedora 44 Workstation lifecycle.

Completion checks: validate list JSON and desktop ID syntax, ensure invalid or
duplicate IDs fail before mutation, verify plan/apply/repeat/status, seed and
restore an exact previous favorite list, and prove a changed list blocks
restore without overwriting it. Keep the operation opt-in and exclude it from
base profiles.
