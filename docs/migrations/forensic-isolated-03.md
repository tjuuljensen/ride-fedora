# Forensic isolated batch 03: native analyzers and legacy scripts

Status: **complete: two supported RPMs, one retired tool, one standalone
replacement**, 2026-10-30. This batch owns the v2
`Binwalk`, `PyhtonAutopep8`, `Dumpzilla`, and `Macvendor` install/remove
outcomes, including the misspelled Python selector. The first two were RPM
and user-global pip installs; the latter two fetched mutable scripts into
`/usr/local/bin` without verifying content. They are not one bundle.

## Completion criteria defined before implementation

- Preserve the four v2 mappings and verify current publisher, license,
  acquisition, and detection. Use Fedora 44 signed RPMs for Binwalk and
  autopep8 if the exact Workstation package and executable are available.
  Their package states must be reversible without touching firmware samples,
  formatted files, or a user's old pip environment.
- In a disposable Fedora 44 x86_64 Workstation overlay, check both RPMs with
  absent plan, apply, signed RPM and file verification, executable startup,
  unchanged repeat, status, restore, and explicit remove. Check RPM inventory
  before and after, including dependencies. Reuse the unchanged DNF handler's
  mocked failure evidence. Promote only passing targets to supported.
- For Dumpzilla and Macvendor, require a current licensed source, pinned
  artifact, owned destination, no overwrite of unowned scripts, a safe
  inverse, focused mocked tests, and one disposable-VM happy path before an
  opt-in candidate is counted operable. Otherwise record a non-runnable
  v3.0 decision with a concrete reopen trigger.
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

`Dumpzilla` is **retired**. The [upstream repository](https://github.com/Busindre/dumpzilla)
itself says the project is discontinued; the v2 function fetched a mutable
script into `/usr/local/bin`. No license, pinned artifact, or compatibility
evidence for current Firefox profile data has been accepted. A maintained
licensed browser forensics tool with an isolated, privacy-preserving install
would be a new review. No browser profile data is removed by this decision.

`Macvendor` is **replaced by the maintained standalone
[`mac-vendor.sh`](https://github.com/tjuuljensen/linux-scripts/blob/master/mac-vendor.sh)**
in the owner's `linux-scripts` repository. The current script handles IEEE
registries through an XDG cache and can run directly; this is a documented
replacement, **not a v3 managed install**. The original v2 function fetched
the mutable `master` script into `/usr/local/bin`, which v3 neither adopts
nor removes. The source repository has no published license in its metadata;
adding a v3 managed script operation requires an explicit license, pinned
artifact, owned destination/cache, and VM inverse. The replacement does not
count as runnable in the v3 progress report.
