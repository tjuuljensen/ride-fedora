# GNOME string settings and UPower configuration decisions

The owner kept three exclusive GNOME window-button layouts and a configurable
GNOME region. Their [shared string-setting batch](desktop-user-string-01.md)
now provides typed profile values and exact prior-state recovery on Fedora 44
Workstation. The separate remove-only `GnomeRegion` use case remains deferred
because its distinct intent still needs an owner decision.
The owner kept the 15- and 20-percent UPower threshold outcomes. Prefer one
optional, configurable threshold with validated values rather than two
independent file edits. Its implementation must preserve any
administrator-owned policy and exact prior state. The
[UPower batch](desktop-user-upower-01.md) now defines completion checks and
records Fedora 44's supported drop-in format before implementation.

Status: **GNOME strings operable; UPower thresholds non-runnable**, 2026-10-30.
The [boolean settings](desktop-user-boolean.md) are separately operable.

## Completion criteria defined for this review

- Preserve each v2 function mapping and its active or library-only selector
  status. Inspect exact mutation and inverse behavior before choosing a
  disposition. Do not count a candidate without a safe declared inverse.
- Require owned, per-user string state for window buttons and region, and a
  declared locale value. A restore must handle arbitrary prior values and
  distinguish an implicit default from an explicit override before a runnable
  implementation is promoted.
- Require an owned UPower drop-in and exact, conflict-checked restore on a
  disposable Fedora 44 Workstation target before counting either outcome
  operable. Record battery warning behavior as H030 when the VM has no
  battery; a config edit alone cannot prove that user-visible behavior.

## Decisions and reopening triggers

| Scoped outcome | v2 behavior and v3.0 decision | Review trigger |
| --- | --- | --- |
| `WindowCtlMinMaxClose` | **Operable opt-in candidate.** v2 wrote one fixed layout with no exact inverse; v3 selects that value through `setting.gnome-window-buttons` and restores the prior override. | [VM acceptance](../acceptance/setting.gnome-string-values.md); complete H003 visual review in v3.1. |
| `GnomeRegionDaDK` | **Operable opt-in candidate.** `gnome-region-da-dk` explicitly selects an available locale through `setting.gnome-region`; another installed locale can be chosen through a validated profile value. | [VM acceptance](../acceptance/setting.gnome-string-values.md); complete H003 region-format review in v3.1. |
| `GnomeRegion` | **Owner-deferred.** `RemoveGnomeRegion` wrote an empty string without a distinct desired install or prior-state journal. The configurable v3 region setting does not imply an explicit reset-to-default request. | Decide whether reset-to-default is a separate use case; if kept, add an owned action with exact recovery. |
| `PowerPercentageLow15` | **Unsupported.** The active v2 function rewrites every matching `PercentageLow=` line in `/etc/UPower/UPower.conf` with `sed -i` and has no inverse or ownership check. | Review the current UPower drop-in contract, preserve an existing administrator policy, and pass battery-policy and restore checks on a disposable target. |
| `PowerPercentageLow20` | **Kept by owner.** The library-only variant performs the same broad file rewrite to `20.0`, with the same inverse and ownership gap. Prefer an optional validated threshold shared with the 15-percent outcome. | Implement one conflict-safe, owned UPower policy setting, then prove battery behavior and exact recovery on a disposable target. |

The owner deferred the separate `GnomeRegion` retire-or-keep choice on
2026-10-30. The configurable setting is now operable, so this remove-only
outcome awaits its distinct use-case decision.

[GNOME's user-settings guide](https://help.gnome.org/system-admin-guide/dconf.html)
describes dconf's user database and default layers. The
[UPower project](https://upower.freedesktop.org/) describes system power
management; the v2 file mutations above are verified directly from
`lib-fedora.sh`. No production host settings were changed in this review.
