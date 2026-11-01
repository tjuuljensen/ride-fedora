# UPower low-battery threshold

Status: **both kept outcomes operable as opt-in candidates**,
2026-10-30. The owner kept both v2 threshold outcomes for v3.0 and preferred
one optional configurable setting. `SetPowerPercentageLow15` and
`SetPowerPercentageLow20` rewrite every `PercentageLow=` line in
`/etc/UPower/UPower.conf` without ownership or an inverse. The v3 operation
will not repeat that edit.

Fedora 44's `upower-1.91.5-1.fc44.x86_64` owns both the main file and
`/etc/UPower/UPower.conf.d/README.md`. The latter documents numbered
`NN-name.conf` snippets, processed after the main file in lexical order.
The [upstream change](https://cgit.freedesktop.org/upower/commit/meson.build?id=46bbc8a602b883b570e053f0dcc1f3cfc9e134cd)
introduced that contract. The current host confirms this packaging, but it
is not acceptance evidence for the declared disposable Workstation target.

## Completion criteria defined before implementation

- Add one system-scoped, data-only `setting.upower-percentage-low` operation.
  Profiles explicitly select a validated percentage; offer 15 and 20 as
  separate opt-in examples without putting either in a base profile. Reject
  missing, malformed, out-of-range, or conflicting selections before mutation.
- Use only a RIDE-owned, numbered drop-in. Refuse a pre-existing unowned file
  at that path, symlinks, or a later administrator drop-in that would override
  the selected key. Leave `/etc/UPower/UPower.conf` untouched. Check that the
  selected low value remains above the effective critical and action values.
- Capture the exact previous owned-file state or absence in the private run
  journal. Repeat is unchanged. Restore removes only the RIDE-owned file or
  restores its exact prior content and refuses a changed current file. If
  writing or reloading fails, repair the prior file and report the failure.
- Mock selection, plan, refusal, apply, repeat, status, changed-file conflict,
  partial write/reload failure, and exact restoration. In one disposable
  Fedora 44 x86_64 Workstation overlay, verify the installed UPower version,
  drop-in parsing, selected config, repeat, status, and restore for 15 and 20.
  Observe service reload/restart only in the overlay. Investigate any failed
  run before retrying.
- Count both outcomes as opt-in candidates only after the target-specific
  configuration lifecycle passes. A VM without a battery cannot prove the
  user-visible warning threshold; record that limitation and H030's v3.1
  battery behavior check. Keep the operation out of base profiles. Update
  catalog, schemas, tests, generated docs, ledger, and Windows alignment.

The main configuration remains administrator/package-owned. This batch owns
only its exact drop-in path and must avoid masking another explicit
administrator policy.

## Fedora 44 Workstation result

The [shared VM acceptance](../acceptance/setting.upower-percentage-low.md)
passed the owned configuration lifecycle for both 15 and 20 on the exact
declared target. `setting.upower-percentage-low` accepts selected values from
6 through 50, requires percentage-based UPower policy, and refuses a
critical/action threshold at or above the requested low threshold. An
existing unowned RIDE path or another drop-in setting `PercentageLow` is a
conflict. It writes a fixed, root-owned numbered file and leaves the main
UPower configuration unchanged. The selected value is bound to the run
signature; a restore needs the recorded value and refuses changed current
content.

Both source outcomes are **operable opt-in candidates**. The headless VM
could not test a physical low-battery warning transition; H030 retains that
behavioral check in v3.1. The accepted scope is configuration and exact
recovery on Fedora 44 x86_64 Workstation, with no base-profile selection.

The first harness attempt stopped before boot because its local loopback
socket was sandbox-denied. The identical scenario then passed with local VM
permission. After adding a root-ownership check for the managed file, the
final-code scenario passed again in a new disposable overlay; no failed guest
mutation was retried blindly.
