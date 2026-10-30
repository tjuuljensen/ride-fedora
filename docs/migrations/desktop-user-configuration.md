# GNOME string settings and UPower configuration decisions

The owner kept the GNOME window-control button layout in the v3.0 fast-track
review. Implement a typed value with exact prior-state recovery.
AppmenuClose is a second owner-kept layout choice; profile selections are
mutually exclusive and both restore the exact prior layout.
The owner also kept GNOME region selection, with country/region supplied by
the profile rather than fixed to Denmark. The separate remove-only
`GnomeRegion` use case remains deferred until that owned setting is designed.
The owner kept the 15-percent UPower threshold outcome; its implementation
must preserve any administrator-owned policy and exact prior state.

Status: **non-runnable v3.0 decisions**, 2026-10-30, for the remaining
desktop-user-02, desktop-user-04, and desktop-user-09 outcomes. These are
separate from the [operable boolean settings](desktop-user-boolean.md).

## Completion criteria defined for this review

- Preserve each v2 function mapping and its active or library-only selector
  status. Inspect exact mutation and inverse behavior before choosing a
  disposition. Do not count a candidate without a safe declared inverse.
- Require owned, per-user string state for window buttons and region, and a
  declared locale value. A restore must handle arbitrary prior values and
  distinguish an implicit default from an explicit override before a runnable
  implementation is promoted.
- Require an owned UPower drop-in or an exact, conflict-checked backup and
  restore of the existing file, plus a battery-capable disposable target,
  before changing system power policy. A config edit alone cannot prove the
  battery behavior.

## Decisions and reopening triggers

| Scoped outcome | v2 behavior and v3.0 decision | Review trigger |
| --- | --- | --- |
| `WindowCtlMinMaxClose` | **Unsupported.** `SetWindowCtlMinMaxClose` writes one `button-layout` string. Its inverse is another hard-coded layout, not the prior arbitrary user value. The current v3 setting schema and journal accept boolean enum states only. | Add a typed string handler that records the exact prior value and unset/default provenance, then test apply, conflict, and restore in a Workstation VM. |
| `GnomeRegionDaDK` | **Unsupported.** `SetGnomeRegionDaDK` sets `org.gnome.system.locale region` to `da_DK.UTF-8` for the login user. That localized value must be explicit opt-in profile data, with exact prior-region recovery. | Add validated locale selection and a string-state journal, then verify the target locale and restore on Fedora 44 Workstation. |
| `GnomeRegion` | **Unsupported.** `RemoveGnomeRegion` is a remove-only v2 function that writes an empty string. It cannot restore the previous locale and has no standalone desired install. | Reconcile it as the inverse of an owned region operation once exact prior-state and default recovery are available. |
| `PowerPercentageLow15` | **Unsupported.** The active v2 function rewrites every matching `PercentageLow=` line in `/etc/UPower/UPower.conf` with `sed -i` and has no inverse or ownership check. | Review the current UPower drop-in contract, preserve an existing administrator policy, and pass battery-policy and restore checks on a disposable target. |
| `PowerPercentageLow20` | **Unsupported.** The library-only variant performs the same broad file rewrite to `20.0`, with the same inverse and ownership gap. | Reopen together with the 15-percent variant after a conflict-safe, owned UPower policy handler and battery target exist. |

The owner deferred the separate `GnomeRegion` retire-or-keep choice on
2026-10-30. It remains non-runnable while an owned region setting and exact
prior-state recovery are designed.

[GNOME's user-settings guide](https://help.gnome.org/system-admin-guide/dconf.html)
describes dconf's user database and default layers. The
[UPower project](https://upower.freedesktop.org/) describes system power
management; the v2 file mutations above are verified directly from
`lib-fedora.sh`. No production host settings were changed in this review.
