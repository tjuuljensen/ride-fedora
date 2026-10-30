# Cheat command-line reference outcome

Status: **supported Fedora RPM**, 2026-10-30. This active-preset outcome maps
`InstallCheat` and `RemoveCheat`. v2 scrapes the latest GitHub binary,
unpacks it, and overwrites `/bin/cheat` without tracking prior ownership;
its inverse removes that path unconditionally. The maintained upstream
[`cheat` command](https://github.com/cheat/cheat) is MIT, while
[Fedora 44 ships a signed `cheat` RPM](https://packages.fedoraproject.org/pkgs/cheat/cheat/)
with the package's full dependency license expression recorded in the
catalog.

## Completion criteria defined before implementation

- Replace the unowned binary path with a Fedora `cheat` RPM operation on
  Fedora 44 x86_64 Workstation. Verify absent plan, apply, signed RPM/files,
  CLI startup, repeat, status, restore, and explicit remove in a disposable
  VM. Do not overwrite a pre-existing `/bin/cheat` owned by another package;
  capture baseline ownership before promotion.
- Reuse the unchanged DNF handler's mocked failure evidence. The default
  profile stays small; an optional CLI-tools profile may include the
  operation only after it passes.
- Compare Windows contracts, update ledger and generated docs, and
  investigate a failed run before retrying.

## Fedora 44 VM result

[`package.cheat`](../acceptance/package.cheat.md) passed absent plan,
candidate-gated apply, signed RPM/files, CLI version 4.4.2, installed
status, unchanged repeat, restore, and explicit remove in the disposable
Workstation overlay. `/bin/cheat` was unowned/absent at baseline. The
unchanged DNF handler's mocked failure evidence is reused. The final
supported catalog status removes the temporary candidate gate with the
same target and handler. No default-profile addition is made; optional
CLI profile selection can be reviewed separately.
