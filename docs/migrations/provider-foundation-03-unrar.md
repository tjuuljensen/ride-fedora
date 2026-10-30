# Provider foundation 03 follow-up: `unrar` command

Status: **Fedora 44 Workstation VM passed; supported package**, 2026-10-30.
The v2 `InstallPackagingTools` and `RemovePackagingTools` pair selects
`p7zip` and `unrar`. The accepted Fedora `7zip` operation covers the first
tool; `unar` can extract RAR archives but does not supply the old command.
Fedora 44 now publishes an [`unrar` wrapper RPM](https://packages.fedoraproject.org/pkgs/unrar-free/unrar/)
from GPL-2.0-or-later `unrar-free`. It provides `/usr/bin/unrar` for common
listing and extraction, with less feature coverage than the non-free tool.

## Completion checks defined before implementation

- Declare a distinct `package.unrar` operation for the signed Fedora 44
  Workstation x86_64 RPM. Keep `package.7zip` and `package.unar` IDs and
  evidence intact. The source outcome maps to `7zip` and `unrar`; `unar`
  remains an independent optional extractor. No repository or license
  exception is added.
- Reuse the unchanged DNF handler's mocked failure evidence. In one
  disposable pinned Workstation VM, check absent plan, apply, repeat, status,
  RPM signature/files, `/usr/bin/unrar` startup, restore, and explicit
  remove. Compare RPM inventory before and after; investigate residue before
  retrying. Verify an already present `7zip` is preserved.
- Only after exact-target acceptance, add an opt-in `archive-tools` profile
  selecting `7zip` and `unrar`, promote the package operation to supported,
  and count the kept v2 source outcome as operable. Do not expand `default`.
  Smoke the profile's plan, apply, repeat, and restore on the same declared
  target, preserving the pre-existing 7zip. The wrapper's less common RAR
  features move to a named v3.1 hardening item.
- Update the ledger, generated docs, and Windows alignment. Preserve the
  historical replacement decision as migration evidence.

## Result

The [acceptance record](../acceptance/package.unrar.md) gives the pinned
image, candidate catalog hash, retained overlay, transcript, and one passing
VM lifecycle. The signed RPM supplied `/usr/bin/unrar`; restore and explicit
remove returned the full RPM inventory to baseline and preserved the
pre-existing 7-Zip RPM. The separate `archive-tools` profile smoke passed
plan, apply, unchanged repeat, and restore on the same declared target;
the [acceptance record](../acceptance/package.unrar.md) names its overlay.
The profile selects the two v2 bundle capabilities. The supported `unar`
operation remains an optional alternative extractor. H026 retains wider RAR
feature compatibility checks.
