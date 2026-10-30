# Generic server Python pip outcome

Status: **Server VM acceptance passed**, 2026-10-30. The commented v2
`InstallPythonPip` function in the pinned `network-devices` server library
installs the old `python-pip` name and then globally self-upgrades pip. The
workstation migration already accepted Fedora's signed `python3-pip` RPM
without that global mutation. The same v3 package operation can cover the
generic Server edition if its exact target passes.

## Completion criteria defined before target promotion

- Compare source ownership and consumers. `network-devices` remains the
  authoritative v2 server source; this opt-in package mapping does not
  remove its library, presets, publication path, or rollback. Unknown
  consumers remain unverified, not inactive.
- On the pinned Fedora 44 x86_64 Server VM, verify absent plan, signed RPM
  apply, repeat, status, `python3 -m pip --version`, and declared restore or
  remove, preserving pre-existing RPMs. Do not run `pip install --upgrade
  pip` or change site packages.
- Extend only the declared Server target after the test passes. Reuse the
  unchanged DNF handler's mocked failure evidence, update the package
  acceptance record and server ledger, and compare the Windows package,
  profile, and journal contracts.

## Fedora 44 Server VM result

The [Server acceptance](../acceptance/package.python3-pip.md) passed on the
pinned Fedora 44 x86_64 Server image. It covered absent plan, signed apply,
repeat, status, `python3 -m pip --version`, restore, explicit remove, and
preservation of pre-existing RPMs. `python3-pip` was initially present in
the base image, so preparation removed only that RPM in the disposable
overlay before the lifecycle check. The v3 operation is supported on both
declared editions; Selenium remains a separate source outcome.
