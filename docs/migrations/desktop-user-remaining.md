# Remaining desktop and user-state outcomes

The owner kept Firefox preference capability in the v3.0 fast-track review.
Use current policy with exact prior-state recovery rather than the v2 file
overwrite.
The owner also kept custom keyboard shortcuts; only RIDE-owned entries may be
merged or removed, with exact prior list and slot recovery.
The owner kept the separate remove-only inverse on the same ownership rule.
GNOME favorites also remain in scope as a profile-configurable ordered list;
restore the user's prior list exactly.
The owner kept Chrome preferences, Bash aliases, and the ls-to-Eza alias in
the fast-track review. Each needs an owned file or fragment and seeded exact
recovery before runnable status.
The owner also kept the WAN IP alias, retired the old ride-log alias, and kept
the AppmenuClose button layout as an exclusive alternative to MinMaxClose.

Status: **v3.0 decisions**, 2026-10-30. This review covers the remaining
scoped desktop-user batches after the [fixed GNOME boolean handler](desktop-user-boolean.md).
Each disposition below is non-runnable unless a separate v3 operation is
explicitly named. The v2 functions remain inventory evidence, never a
fallback execution path.

## Completion criteria for this review

- Preserve every source function and selector status in the ledger. For each
  active v2 behavior, inspect the mutation and inverse, current upstream
  interface, and conflicts with user-owned state. Do not count a package
  install as equivalent to a composite setting unless its remaining behavior
  is explicitly resolved.
- Require exact, conflict-checked recovery for user files and GNOME arrays.
  Require a desktop/lock-session safety test before any screensaver policy
  becomes runnable. Keep credentials, browser profiles, and user content
  outside RIDE ownership.
- Record a concrete reopening trigger for each non-runnable decision. Keep
  optional additions separate from release blockers; use one automated VM
  session when an owned handler is ready, with manual checks only for visible
  desktop behavior.

## Batch 01: directories and Firefox preferences

| Outcome | Decision and reason | Reopen when |
| --- | --- | --- |
| `SetupUserDefaultDirs` | **Opt-in candidate implemented.** [`setting.user-default-directories`](../../catalog/operations.json) creates only absent `~/git` and `~/bin`, records the device/inode of RIDE-created paths, and restores only unchanged empty paths. Existing directories and contents are preserved. See the [profile](../../profiles/fedora-user-default-directories.json), [focused tests](../../tests/test_v3_user_default_directories.py), and [acceptance record](../acceptance/setting.user-default-directories.md). | Finish Fedora 44 Workstation acceptance, including symlink conflict and nonempty recovery. |
| `FirefoxPreferences` | **Opt-in candidate implemented.** [`setting.firefox-preferences`](../../catalog/operations.json) uses Mozilla's currently documented AutoConfig files with an exact file hash record. It refuses any pre-existing target and preserves modified files on removal. See the [profile](../../profiles/fedora-firefox-preferences.json), [focused tests](../../tests/test_v3_firefox_preferences.py), and [acceptance record](../acceptance/setting.firefox-preferences.md). The old values include WebRTC and Sync changes and a Google startup page; keep this opt-in pending a Workstation startup check. | Finish Firefox startup and owned-file recovery acceptance. H083 tracks obsolete preference review and behavior coverage. |

## Batches 03 and 08: shortcuts and favorites

| Outcome | Decision and reason | Reopen when |
| --- | --- | --- |
| `CustomKeyboardShortcut` | **Operable opt-in candidate.** [`setting.gnome-custom-shortcuts`](../../catalog/operations.json) writes RIDE-owned custom keybindings and merges configured global bindings with current lists. It journals the selected configuration and keeps an owner record for exact entry removal. | [Fedora 44 Workstation acceptance](../acceptance/setting.gnome-custom-shortcuts.md) passed lifecycle and preservation checks. H089 tracks visible shortcut dispatch and conflict review. |
| `CustomKbrdShortcut` | **Operable opt-in candidate inverse.** The same handler removes only recorded RIDE entries and preserves both original and subsequently added user shortcuts and bindings. | [Fedora 44 Workstation acceptance](../acceptance/setting.gnome-custom-shortcuts.md) passed removal, restore, and conflict checks. H089 tracks visible shortcut dispatch and conflict review. |
| `VMKeyboardShortcut` | **Operable opt-in candidate.** The [`fedora-vm-keyboard-shortcuts`](../../profiles/fedora-vm-keyboard-shortcuts.json) profile preserves the legacy bindings through the owned custom-shortcuts operation; it does not write fixed custom100/custom101 slots or clear unowned bindings. | [Batch checks](desktop-user-favorites-shortcuts-02.md) cover the profile lifecycle and exact recovery. H089 retains visible dispatch and conflict review. |
| `GnomeCustomFavorites` | **Operable opt-in candidate.** `setting.gnome-favorite-apps` accepts a bounded desktop-ID list and restores the exact prior dconf value. H085 tracks visual app-ID review. | Use verified Fedora 44 desktop IDs in profiles; the Workstation lifecycle passed. |
| `GnomeDefaultFavorites` | **Operable opt-in candidate.** [`fedora-default-favorites`](../../profiles/fedora-default-favorites.json) records the six favorites read from Fedora 44 Workstation and uses the configurable exact-recovery setting. | [Batch checks](desktop-user-favorites-shortcuts-02.md) cover apply, repeat, and exact restore. H085 retains visual app-ID review. |
| `GnomeMinimalFavorites` | **Operable opt-in candidate.** [`fedora-minimal-favorites`](../../profiles/fedora-minimal-favorites.json) expresses the retained minimal choice through the configurable favorites setting and GNOME Console desktop ID. | [Batch checks](desktop-user-favorites-shortcuts-02.md) cover apply, repeat, and exact restore. H085 retains visual app-ID review. |

The owner retained the `CustomKbrdShortcut` inverse outcome for migration on
2026-10-30. The v3 operation now removes only journaled RIDE-owned shortcuts
and preserves seeded and later user entries. Both shortcut outcomes remain
opt-in candidates until the brief visible dispatch and conflict review in H089.

[GNOME's shortcut UI](https://help.gnome.org/gnome-help/keyboard-shortcuts-set)
and [favorites administration guide](https://help.gnome.org/system-admin-guide/desktop-favorite-applications.html)
provide the current user-facing interfaces. Neither authorizes overwriting
an existing user's complete keybinding or favorites list.

## Batches 05 and 06: aliases and browser helper actions

| Outcome | Decision and reason | Reopen when |
| --- | --- | --- |
| `ChromePreferences` | **Operable opt-in candidate.** The v3 profile writes a fixed recommended-policy file for the current Chrome Flatpak wrapper. Fedora 44 Workstation verified policy-file apply, repeat, status, host policy import permission, and exact removal without touching the browser profile. The profile keeps the v2 Safe Browsing disabled value visible and opt-in. | H091 tracks visible `chrome://policy` review and current Safe Browsing policy mapping before promotion. Sources: [current Flathub wrapper](https://github.com/flathub/com.google.Chrome/blob/master/chrome.sh), [Google Linux policy setup](https://support.google.com/chrome/a/answer/9027408?hl=en), and [SafeBrowsingEnabled policy](https://chromeenterprise.google/policies/safe-browsing-enabled/). |
| `BashAliases` | **Operable opt-in candidate.** [`setting.bash-aliases`](../../catalog/operations.json) uses a marked `.bashrc` loader block and preserves an existing `.bash_aliases` file. | [Fedora 44 Workstation acceptance](../acceptance/setting.bash-aliases.md) passed repeat, interactive use, and owned-block recovery. |
| `AliasLsEza` | **Operable opt-in candidate.** The bounded alias selection creates only the fixed `ls='eza'` alias, checks for an unowned `ls` definition, and requires the Eza command. Eza remains a separate Fedora RPM operation. | [Acceptance](../acceptance/setting.bash-aliases.md) passed actual interactive alias invocation after installing Eza. H090 tracks broader source/privacy review for this alias family. |
| `AliasWanIP` | **Operable opt-in candidate.** The selection offers `wanip`, `wanip4`, and `wanip6` through the ipify HTTPS text API endpoints; the external request occurs only when the user runs an alias. | [Acceptance](../acceptance/setting.bash-aliases.md) verified the generated aliases without making a public request. H090 tracks service and privacy review. |
| `ChromePreferences` | **Operable opt-in candidate.** [`setting.chrome-preferences`](../../catalog/operations.json) writes a fixed recommended-policy file for the existing Chrome Flatpak wrapper. Fedora 44 Workstation verified policy-file apply, repeat, status, host policy import permission, and exact removal without touching the browser profile. The sample profile reproduces the v2 Safe Browsing disabled value and labels that tradeoff. | H091 tracks the brief visible `chrome://policy` review and current Safe Browsing policy mapping before promotion. See [migration mapping](desktop-user-chrome-preferences.md). |
| `AliasRideLog` | **Retired.** This commented alias reads the v2 `/var/log/bootstrap-installer` path; v3 uses run journals. Its inverse edits `.bashrc` even though installation writes `.bash_aliases`. | Reopen as a v3 read-only run-log command if users request it; do not revive the shell-file edit. |
| `CheckFirefoxAddons` | **Replaced, non-runnable catalog outcome.** The v2 function already delegates to the maintained `tools/manage-firefox-extensions.py check --online` command. It is an explicit online policy check, not an install or declarative desired state. | Reconsider a catalog operation only if checks gain a stable offline desired-state and lifecycle contract. |
| `FinalizeFirefoxAddonRemoval` | **Replaced, non-runnable catalog outcome.** The v2 function delegates to `tools/manage-firefox-extensions.py finalize-remove` after Firefox restart and removal verification. The tested tool keeps its explicit procedural workflow. | Add a v3 catalog lifecycle only after the two-stage browser policy state and recovery are modeled. |

The Firefox helper has focused tests in `tests/test_manage_firefox_extensions.py`;
the [Firefox extension publisher review](publisher-apps-04.md) records its
ownership and approval boundary. The helper is not in `default`.

The [owned Bash alias batch](desktop-user-aliases-01.md) records source review,
fixed alias choices, completion checks, and the passing disposable-VM lifecycle.
Chrome preferences now have an opt-in candidate with Fedora 44 Workstation policy-file lifecycle evidence; H091 retains visible policy review.

## Batch 07: window buttons

| Outcome | Decision and reason | Reopen when |
| --- | --- | --- |
| `WindowCtlAppmenuClose` | **Operable opt-in candidate.** The shared `setting.gnome-window-buttons` handler selects this v2 value and restores the exact prior override. | [VM acceptance](../acceptance/setting.gnome-string-values.md); H003 visual review in v3.1. |
| `WindowCtlLeftClsMinMax` | **Operable opt-in candidate.** This is an exclusive profile value of the same handler, with exact prior-state recovery. | [VM acceptance](../acceptance/setting.gnome-string-values.md); H003 visual review in v3.1. |

## Batch 11: lock and idle settings

| Outcome | Decision and reason | Reopen when |
| --- | --- | --- |
| `ScreensaverSlp10Lgn5` | **Supported on Fedora 44 Workstation.** [`setting.gnome-lock-timing`](../../catalog/operations.json) carries the 10-minute idle / 5-minute lock choice and restores all four prior user values exactly. | [VM acceptance](../acceptance/setting.gnome-lock-timing.md) verified both retained timing choices, status, repeat, and exact restore. H092 retains a brief visible idle/lock behavior check. |
| `ScreensaverSlp15Lgn5` | **Supported on Fedora 44 Workstation.** The same configurable operation carries the 15-minute idle / 5-minute lock value; the profile remains opt-in. | [VM acceptance](../acceptance/setting.gnome-lock-timing.md) verified the selected values and exact prior-state restore. H092 retains a brief visible idle/lock behavior check. |

Both retained lock-timing variants are runnable on the declared Workstation
target. They remain outside the base profile; future timing choices require
the same exact-state and lock-safety review.

## Batch 10: Terminator composite

The owner kept `Terminator` for v3.0. The active v2
install/remove pair changes both the Fedora `terminator` RPM and the current
user's iBus emoji hotkey. Removal writes a hard-coded hotkey instead of the
prior value. Installing the RPM alone would omit a user-visible side effect,
The separate [batch 10 record](desktop-user-10-terminator.md) now accepts
`package.terminator` and an exact-restorable per-user iBus setting as two
opt-in candidates on Fedora 44 Workstation. The combined source outcome is
operable through separate root and user profiles; visual behavior is H003.
