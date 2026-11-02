# GNOME VM shortcuts and favorite presets

## Completion checks

- Preserve the v2 VM keyboard layout using `setting.gnome-custom-shortcuts`;
  never use fixed GNOME keybinding slots or clear unrelated user bindings.
- Offer the Fedora 44 Workstation favorite defaults and the retained minimal
  selection through `setting.gnome-favorite-apps`, whose journal restores the
  exact previous dconf list. Keep both profiles opt-in.
- Verify the Fedora default list from the declared Fedora 44 target; retain a
  modern terminal desktop ID for the minimal choice.
- Reuse the existing mocked ownership, selection, and restore evidence for
  unchanged handlers. One Fedora 44 Workstation VM session applied and repeated each profile, then
  restored seeded keybindings and favorite-list state exactly.
- Leave visible shortcut dispatch and app availability review in H089/H085.

## Outcome mapping

`VMKeyboardShortcut` now uses the existing custom-shortcuts operation with
the v2 bindings: Ctrl+Alt+D for show desktop, Ctrl+Alt+E for Files, and
Ctrl+Alt+T for the terminal. RIDE owns deterministic entries, merges selected global bindings with
existing lists, journals the configured selection, and removes only its entries.
The [VM profile](../../profiles/fedora-vm-keyboard-shortcuts.json) remains
opt-in.

`GnomeDefaultFavorites` maps to the six current Fedora 44 Workstation defaults
read from the declared target's `org.gnome.shell favorite-apps` setting:
Firefox, Calendar, Files, Software, Text Editor, and Calculator. The
[default profile](../../profiles/fedora-default-favorites.json) stores those
IDs explicitly, so a future distro default change does not silently change
the user's selected state.

`GnomeMinimalFavorites` remains a configurable-list choice rather than another
fixed handler. Its [example profile](../../profiles/fedora-minimal-favorites.json)
uses Firefox, Files, and GNOME Console. GNOME Console is the Fedora desktop
terminal entry point in place of the legacy GNOME Terminal desktop ID.

All three profiles use existing handlers. The shortcut and favorites handler
tests already cover invalid values, occupied-slot refusal, repeat, and exact
recovery; the new acceptance session checks these exact profile selections on
Fedora 44 Workstation. H089 and H085 keep visible dispatch and desktop-ID
review in the v3.1 hardening queue.

## Fedora 44 Workstation evidence

Acceptance: PASS on Fedora 44 Workstation x86_64; see [VM transcript and evidence](../acceptance/desktop-user-defaults.md).
