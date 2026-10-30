# Forensic isolated batch 03: native analyzers and MAC vendor scripts

Firefox profile analysis moved into a separate high-risk
[successor batch](forensic-isolated-08-firefox.md). The old Dumpzilla
script is discontinued; its capability remains kept for v3.0.

Status: **complete: two supported RPMs and one standalone
replacement**, 2026-10-30. This batch owns the v2
`Binwalk`, `PyhtonAutopep8`, and `Macvendor` install/remove outcomes,
including the misspelled Python selector. The first two were RPM and
user-global pip installs; Macvendor fetched a mutable script into
`/usr/local/bin` without verifying content. They are not one bundle.

## Completion criteria defined before implementation

- Preserve the three v2 mappings and verify current publisher, license,
  acquisition, and detection. Use Fedora 44 signed RPMs for Binwalk and
  autopep8 if the exact Workstation package and executable are available.
  Their package states must be reversible without touching firmware samples,
  formatted files, or a user's old pip environment.
- In a disposable Fedora 44 x86_64 Workstation overlay, check both RPMs with
  absent plan, apply, signed RPM and file verification, executable startup,
  unchanged repeat, status, restore, and explicit remove. Check RPM inventory
  before and after, including dependencies. Reuse the unchanged DNF handler's
  mocked failure evidence. Promote only passing targets to supported.
- For Macvendor, require a current licensed source, pinned artifact, owned
  destination, no overwrite of unowned scripts, a safe inverse, focused
  mocked tests, and one disposable-VM happy path before a managed opt-in
  candidate is counted operable. Otherwise keep the standalone replacement
  distinct from a catalog install. Dumpzilla's broader profile and secret
  handling checks belong to its high-risk batch.
- Compare Windows catalog/profile/run-state behavior, update the outcome
  ledger, evidence, generated reports, and migration plan. Investigate a
  failed VM run before retrying.

## Fedora 44 result and v3.0 decisions

[`package.binwalk`](../acceptance/package.binwalk.md) and
[`package.autopep8`](../acceptance/package.autopep8.md) passed their shared
disposable Workstation VM lifecycle. Both were absent at baseline; signed
Fedora RPMs supplied Binwalk 3.1.0 and autopep8 2.3.2, and the named-package
inverse removed each while preserving pre-existing RPM identities. The
unchanged DNF handler's mocked failure evidence is reused. The RPMs are
**supported on Fedora 44 x86_64 Workstation**. Binwalk 3 is a Rust rewrite;
its old Python plugin behavior is not included in the install claim. Neither
operation reads a firmware sample or formats a user file. The v2 global pip
environment is outside autopep8's new RPM ownership.

`Dumpzilla` itself is discontinued. The owner kept the Firefox analysis
capability, now tracked in the separate
[high-risk successor batch](forensic-isolated-08-firefox.md).

`Macvendor` is **replaced by the owner's standalone
[`mac-vendor.py`](../../reference/mac-vendor.py) and
[`mac-vendor.sh`](../../reference/mac-vendor.sh)**, copied from `linux-scripts`
at the pinned revision in the [reference notes](../../reference/README.md).
The owner kept both scripts in v3.0 on 2026-10-30. They handle IEEE registries
through a shared XDG cache and can run directly; this is a functional
replacement, **not a v3 managed install**. H024 holds managed installation
and recovery for v3.1. The original v2 function fetched the mutable `master`
script into `/usr/local/bin`, which v3 neither adopts nor removes. The source
repository has no published license in its metadata; this same-owner copy
follows the owner's explicit instruction and does not assert a public reuse
license. A future managed operation needs pinned acquisition, owned
destination/cache, and VM inverse. The standalone replacement is reported
separately from runnable catalog operations.
