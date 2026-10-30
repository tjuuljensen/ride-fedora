# GNOME string settings: region and window buttons

Status: **four kept outcomes operable as opt-in candidates**, 2026-10-30.
The owner kept `GnomeRegionDaDK` and three exclusive window-button layouts
for v3.0. Their v2 functions write one user GSettings string each without
capturing a prior value or its unset/default provenance. The separate
remove-only `GnomeRegion` function remains owner-deferred; it does not define
a default for the kept region setting.

GNOME documents that GSettings and dconf changes apply to the current user's
database, not root's. The live schema keys are
`org.gnome.system.locale region` at `/system/locale/region` and
`org.gnome.desktop.wm.preferences button-layout` at
`/org/gnome/desktop/wm/preferences/button-layout`. Both have string type on
the current Linux host; Fedora 44 Workstation must confirm them independently.
The three v2 layouts are `:minimize,maximize,close`, `:appmenu:close`, and
`close,minimize,maximize:`. Region is a profile-selected locale, not a
hard-coded Danish policy.

## Completion criteria defined before implementation

- Add a typed, explicit profile value for each string setting. Reject missing
  values, unknown setting IDs, unapproved window layouts, malformed locale
  values, and values on non-string operations. Keep all choices out of base
  profiles and prevent two window layouts in one profile.
- On Fedora 44 x86_64 Workstation, verify the schema, key type, selected
  locale availability, and user-bus scope before mutation. Preserve the
  exact dconf user override or its absence in a private run journal. A
  restore must refuse a changed current value and reproduce the prior
  override or unset state, not write a hard-coded default.
- Mock plan, candidate refusal, apply, repeat, conflict, locked-key refusal,
  a write that fails after mutation, missing observation, and restore of both
  custom and unset baselines. In one disposable Workstation overlay, exercise
  all three window choices and one declared region, with an existing custom
  value and an unset value. A brief visual check may move to v3.1 after the
  stored-value lifecycle passes; do not claim visual behavior from headless
  evidence.
- Record separate result and evidence for each of the four source outcomes;
  compare Windows catalog, profile, and run-state semantics, update generated
  docs, and investigate a failed VM run before retrying. The owner-deferred
  remove-only region outcome stays separate until its use case is decided.

The implementation extends the profile's data-only value field and the
trusted GSettings provider. It does not source profile JSON or turn a saved
value into shell code. The selected value and source definition are bound to
the run journal so restore cannot silently reinterpret a run under a changed
profile.

## Fedora 44 Workstation result

The [shared VM acceptance](../acceptance/setting.gnome-string-values.md)
passed for `setting.gnome-region` and `setting.gnome-window-buttons` in one
disposable Workstation overlay. `gnome-region-da-dk` selected an installed
locale and restored both a custom region and an unset key. Three separate
window profiles each selected one v2 layout and restored the seeded custom
layout. The fixed handler accepts only validated values. A duplicate use of
the same operation ID in one profile is rejected, so two layouts cannot be
applied in one profile transaction. The private journal stores the selected
value and exact prior dconf override; restore verifies the source signature
and refuses a changed current value.

All four kept source outcomes are **operable opt-in candidates** on Fedora 44
x86_64 Workstation. The headless test did not render window controls or
region-dependent formats; those checks remain H003 in v3.1. The separate
owner-deferred `GnomeRegion` removal outcome remains a distinct decision.
