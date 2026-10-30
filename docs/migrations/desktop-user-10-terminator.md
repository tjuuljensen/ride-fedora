# Desktop and user batch 10: Terminator package and iBus hotkey

Status: **package candidate passed VM acceptance; composite kept gap**,
2026-10-30. `InstallTerminator` installs Fedora's `terminator` RPM and changes
the current user's iBus emoji hotkey to `<Control><Alt><Shift>e`.
`RemoveTerminator` removes the RPM but writes a fixed iBus default instead of
restoring the user's prior value. The package and user setting have different
owners and inverses, so the v3.0 outcome remains a gap until both are handled.

Fedora 44 publishes a signed
[`terminator` RPM](https://packages.fedoraproject.org/pkgs/terminator/terminator/)
under GPL-2.0-only. Upstream [recommends the distribution package](https://github.com/gnome-terminator/terminator/blob/master/INSTALL.md).
RIDE's package operation selects this RPM on Fedora 44 x86_64 Workstation and
does not edit iBus or Terminator user configuration.

## Completion criteria defined before implementation

- For the RPM path, verify absent plan, candidate-gated apply, Fedora RPM
  signature and files, desktop launcher, repeat, status, restore, explicit
  install/remove, and preservation of pre-existing RPM identities in one
  disposable Fedora 44 x86_64 Workstation overlay. Reuse the unchanged DNF
  handler's focused mocked failure evidence; record dependencies and upgrades.
- For the optional iBus setting, verify the live schema/key and bus scope,
  capture both value and default/override provenance, detect conflicts, and
  restore the exact prior state after successful and partial apply. Seed an
  existing custom hotkey in a disposable Workstation user session and prove
  RIDE preserves it after restore. The setting must not depend on Terminator
  being installed or overwrite an unrelated user's key.
- Count the combined v2 outcome as operable only when both paths have declared
  owned recovery and exact-target evidence. The package may be selectable
  separately as an opt-in candidate while the original combined outcome
  remains a kept v3.0 gap. Keep it out of base profiles.
- Check Windows catalog, profile, and run-state semantics, then update ledger,
  generated docs, and any named v3.1 hardening. Investigate failure before
  rerunning a VM case.

## Current implementation boundary

[`package.terminator` acceptance](../acceptance/package.terminator.md)
passed the focused Fedora 44 x86_64 Workstation package lifecycle. It uses
the existing Fedora DNF handler for the RPM alone and is individually
selectable with `--allow-candidate`. Its candidate status does not assert the
old iBus behavior. The hotkey remains non-runnable until a typed per-user
setting and exact recovery are accepted. A desktop visual review of the RPM
belongs to v3.1 item H003, after the v3.0 setting gate.
