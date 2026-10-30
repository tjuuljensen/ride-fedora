# Remaining desktop and user-state outcomes

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
| `SetupUserDefaultDirs` | **Unsupported.** The active v2 function creates `~/git` and `~/bin`, then changes ownership even if either directory already existed. It has no inverse. A v3 operation must leave existing paths and contents untouched and remove only a new, empty, RIDE-owned directory on restore. | Add an owned user-directory handler with existing-directory, symlink, nonempty, and restore-conflict VM tests. |
| `FirefoxPreferences` | **Unsupported.** v2 overwrites three files under `/usr/lib64/firefox` with mixed privacy and startup preferences; its inverse deletes them without checking prior ownership. The current [Firefox policy template](https://mozilla.github.io/policy-templates/) provides maintained preference policies, but adopting those values requires a reviewed security choice and profile-preserving inverse. | Choose the current Firefox policy values, prove owned-file and seeded-policy recovery, and test browser behavior on Fedora 44 Workstation. |

## Batches 03 and 08: shortcuts and favorites

| Outcome | Decision and reason | Reopen when |
| --- | --- | --- |
| `CustomKeyboardShortcut` | **Unsupported.** v2 replaces the complete custom-keybinding list and writes two fixed slots, potentially hiding existing user shortcuts. | Implement merge-by-owned-entry with conflict checks and exact list/slot restoration; verify in a disposable GNOME session. |
| `CustomKbrdShortcut` | **Unsupported.** The remove-only inverse clears the entire list and both slots, including unowned shortcuts. | Reconcile it as the inverse of owned custom shortcuts without clearing user entries. |
| `VMKeyboardShortcut` | **Unsupported.** The library-only VM variant writes the same fixed slots as the workstation shortcut set with different bindings, so it can overwrite either user or RIDE data. | Add a distinct opt-in VM shortcut choice with ownership, conflict, and restore evidence. |
| `GnomeCustomFavorites` | **Unsupported.** The active v2 array replaces all user favorites and includes `atom.desktop`; Atom was retired in the publisher review. | Select installed Fedora 44 desktop IDs, preserve user favorites, and pass profile/visual and exact-restore checks. |
| `GnomeDefaultFavorites` | **Retired.** This library-only hard-coded Fedora 37-era favorites snapshot is not the Fedora 44 Workstation default contract. | Reopen only if a current edition-specific default reset is explicitly requested and can preserve the prior user list. |
| `GnomeMinimalFavorites` | **Unsupported.** The library-only function replaces the complete favorites array without a prior-state snapshot. | Add an opt-in minimal-favorites profile with exact list recovery and a brief visual check. |

[GNOME's shortcut UI](https://help.gnome.org/gnome-help/keyboard-shortcuts-set)
and [favorites administration guide](https://help.gnome.org/system-admin-guide/desktop-favorite-applications.html)
provide the current user-facing interfaces. Neither authorizes overwriting
an existing user's complete keybinding or favorites list.

## Batches 05 and 06: aliases and browser helper actions

| Outcome | Decision and reason | Reopen when |
| --- | --- | --- |
| `ChromePreferences` | **Unsupported.** The commented v2 function overwrites `/opt/google/chrome/master_preferences`; its inverse references a different variable and cannot safely restore an existing file. Chrome itself is non-runnable in the publisher batch. [Google's current guidance](https://support.google.com/chrome/a/answer/187948?hl=en) uses `initial_preferences` for first-run defaults and recommends policies for enforced values. | First accept an owned Chrome deployment, then choose current preferences versus policy, preserve pre-existing files, and verify profile behavior and inverse. |
| `BashAliases` | **Unsupported.** v2 appends a source block to `.bashrc`; the inverse deletes every line containing `.bash_aliases`, including user-authored lines. | Implement a uniquely marked, conflict-checked block or separate shell fragment with seeded-file tests and exact rollback. |
| `AliasLsEza` | **Unsupported.** v2 appends `alias ls=eza` to `.bash_aliases`; its inverse mistakenly deletes `ride-log` lines. The Fedora `package.eza` operation does not change shell aliases. | Add an owned alias entry that checks existing `ls` meaning and restores the exact file state. |
| `AliasWanIP` | **Unsupported.** v2 appends three DNS-query aliases; its inverse deletes only lines matching `alias wanip`, leaving blanks and potentially deleting unrelated aliases. The external DNS resolver is also an explicit network dependency. | Choose a maintained resolver contract and owned shell fragment with offline plan, conflict, and restore tests. |
| `AliasRideLog` | **Retired.** This commented alias reads the v2 `/var/log/bootstrap-installer` path; v3 uses run journals. Its inverse edits `.bashrc` even though installation writes `.bash_aliases`. | Reopen as a v3 read-only run-log command if users request it; do not revive the shell-file edit. |
| `CheckFirefoxAddons` | **Replaced, non-runnable catalog outcome.** The v2 function already delegates to the maintained `tools/manage-firefox-extensions.py check --online` command. It is an explicit online policy check, not an install or declarative desired state. | Reconsider a catalog operation only if checks gain a stable offline desired-state and lifecycle contract. |
| `FinalizeFirefoxAddonRemoval` | **Replaced, non-runnable catalog outcome.** The v2 function delegates to `tools/manage-firefox-extensions.py finalize-remove` after Firefox restart and removal verification. The tested tool keeps its explicit procedural workflow. | Add a v3 catalog lifecycle only after the two-stage browser policy state and recovery are modeled. |

The Firefox helper has focused tests in `tests/test_manage_firefox_extensions.py`;
the [Firefox extension publisher review](publisher-apps-04.md) records its
ownership and approval boundary. The helper is not in `default`.

## Batch 07: window buttons

| Outcome | Decision and reason | Reopen when |
| --- | --- | --- |
| `WindowCtlAppmenuClose` | **Unsupported.** v2 writes one hard-coded `button-layout` string with no exact prior-state inverse. | Add the typed GNOME string handler and conflict-aware restore described in [batch 02](desktop-user-configuration.md). |
| `WindowCtlLeftClsMinMax` | **Unsupported.** v2 writes a different string to the same key, potentially replacing either user or RIDE state. | Model mutually exclusive button-layout choices and exact prior-state recovery in a Workstation VM. |

## Batch 11: lock and idle settings

| Outcome | Decision and reason | Reopen when |
| --- | --- | --- |
| `ScreensaverSlp10Lgn5` | **Unsupported.** The active v2 function writes four GNOME session and screensaver keys, including lock enable and delay, without recording the prior values or an inverse. | Add one atomic, per-user policy operation with prior-value and default provenance, partial-failure restore, lock-session safety, and a brief visual confirmation on a disposable Workstation. |
| `ScreensaverSlp15Lgn5` | **Unsupported.** This library-only variant writes the same four keys with a different idle delay and can conflict with the 10-minute choice. | Reopen as an exclusive profile choice under the same lock-safe, reversible handler. |

Lock settings are security behavior. They remain non-runnable in v3.0 until
the deeper gate passes; a candidate switch is not a substitute.

## Batch 10: Terminator composite

`Terminator` is **unsupported** as a v3.0 source outcome. The active v2
install/remove pair changes both the Fedora `terminator` RPM and the current
user's iBus emoji hotkey. Removal writes a hard-coded hotkey instead of the
prior value. Installing the RPM alone would omit a user-visible side effect,
so this review does not count the composite as a working install. Reopen by
separating the signed Fedora package from an optional, exact-restorable
per-user hotkey operation, then test both on the declared Workstation VM.
