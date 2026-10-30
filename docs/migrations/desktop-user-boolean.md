# GNOME boolean user settings

Status: **operable opt-in candidate**, 2026-10-30. This review spans the boolean
settings in desktop-user-02, desktop-user-04, and desktop-user-09. The v2
functions invoke `gsettings` for the login user through a hard-coded D-Bus
address. v3 binds five fixed schema/key pairs to stable catalog IDs, executes
as the current non-root user, and reads the effective value before changing it.
The `enabled` and `disabled` states map only to boolean `true` and `false`.

## Completion criteria defined for this handler

- Validate each declared GNOME schema/key on the pinned Fedora 44 x86_64
  Workstation VM; reject an absent, non-boolean, or locked key. Keep the
  operation out of `default` and require `--allow-candidate`.
- In one disposable VM session, establish the opposite baseline for all five
  keys, plan both curated profiles, apply, repeat, inspect status and journals,
  restore, and confirm the observed baseline returns. Mock a provider lifecycle
  and a candidate-gate refusal. Automate preparation and transcripts.
- Treat UI rendering, exact restoration of an implicit dconf default rather
  than its effective boolean value, and broader failure paths as H018 for
  v3.1. The operation does not alter system-wide privacy policy.
- Compare the Windows catalog, profile, and run-state semantics; update the
  ledger and generated docs only after the VM result is known.

## Source and recovery

[GNOME GSettings documentation](https://teams.pages.gitlab.gnome.org/Websites/help.gnome.org/system-admin-guide/gsettings-browse.html)
describes per-user settings and the D-Bus requirement for writes. The
[Fedora 44 schema package](https://packages.fedoraproject.org/pkgs/gsettings-desktop-schemas/gsettings-desktop-schemas/)
identifies `gsettings-desktop-schemas` as LGPL-2.1-or-later. RIDE obtains no
new artifact; it verifies the local schema and resulting value. The catalog
and trusted Bash handler fix the five keys, so JSON profiles never become
shell code. A journal records effective `enabled` or `disabled` before and
after; restore checks for a conflicting current value before writing back.
An explicit old dconf value and an unset default with the same effective
boolean are indistinguishable in the v3 journal. H018 covers that stronger
recovery form before any support promotion.

## Fedora 44 VM result

The [disposable Workstation run](../acceptance/gnome-user-boolean.md) passed
for all five keys and both opt-in profiles. Preparation installed the missing
headless D-Bus session helper only in the VM overlay after the first run
stopped before any setting mutation. Each profile passed plan, candidate
gate, apply, unchanged repeat, status, restore preview, restore, and baseline
comparison. The profile desired states are enabled for date, week numbers,
and middle paste, and disabled for location and technical reporting. The
inverse v2 functions for location and reporting map to the same two v3 IDs.
The result demonstrates the declared boolean state change, not desktop
visual behavior or preservation of implicit default provenance.
