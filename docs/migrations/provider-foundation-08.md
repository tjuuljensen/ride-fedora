# Provider foundation batch 08: Eza source and destination ownership

Status: **Fedora Eza supported; GitHub ZIP source replaced**, 2026-10-30.
The owner confirmed **keep** for the separate portable Eza path in the v3.0
fast-track review. Its pinned artifact and owned destination remain to
implement; the accepted Fedora RPM is a distinct installed deployment.
The v2 library offers `InstallEza` from Fedora and the active preset instead
calls `InstallEzaGitHub`, which parses a mutable latest-release API response
and extracts an unverified ZIP into `/usr/local/bin`. Their common
`RemoveEza` removes the Fedora RPM and then deletes `/usr/local/bin/eza`
without proving that either was created by RIDE. A separate v3 source
outcome is retained for each acquisition path; a Fedora RPM install cannot
be reported as acceptance of the portable GitHub download.

Fedora 44 publishes the signed [`eza` RPM](https://packages.fedoraproject.org/pkgs/rust-eza/eza/)
under EUPL-1.2. The current [upstream releases](https://github.com/eza-community/eza/releases)
also publish Linux GNU archives, but the v2 parser does not pin an asset
digest or own its destination. The Fedora 44 package and upstream latest
release both report 0.23.5 at this review; the replacement choice does not
promise Fedora will always track upstream immediately.

## Completion criteria defined before implementation

- Add one `package.eza` Fedora RPM operation for the library-only v2
  `InstallEza` path, exact Fedora 44 x86_64 Workstation target, source,
  license, signed-package verification, detection, and owned inverse. Keep
  it out of base profiles. Reuse focused mocked failure tests for the
  unchanged DNF package handler.
- In one disposable Workstation VM overlay, prove absent plan, apply,
  signature and installed files, `eza` command detection, repeat, status,
  restore, and explicit remove. Reject loss of pre-existing RPM identities
  and record any updates or retained dependencies. Do not touch
  `/usr/local/bin/eza` during the RPM check.
- If the Fedora operation passes, close the active GitHub-source outcome
  as a **documented, non-runnable replacement**: select the supported Fedora
  operation for an installed Eza, and defer portable deployment until a
  checksum-pinned, ownership-aware handler exists. Record this source change
  and its review trigger; do not count the old download as a working install.
- Update ledger, acceptance records, Windows alignment, and generated docs
  after checking the evidence. Investigate a failed VM run before retrying.

## Focused VM result and source decision

The Fedora package lifecycle **PASS** result is recorded in
[`package.eza` acceptance](../acceptance/package.eza.md). A single disposable
Fedora 44 x86_64 Workstation overlay exercised the absent package through
plan, apply, signed RPM and file verification, command detection, status,
unchanged repeat, restore, and explicit remove. The RPM introduced `eza`,
`libgit2`, and `llhttp`; both inverse paths returned the RPM inventory to
baseline and left `/usr/local/bin/eza` absent. The unchanged DNF handler's
mocked failure evidence is reused from the base package checks.

The active `InstallEzaGitHub` outcome is a **documented replacement**, not
a working portable install. A user who wants an installed Eza can select
`package.eza` from Fedora, with a supported package lifecycle on the declared
target. The v2 unpinned ZIP extraction, mutable latest-release selection,
and unconditional deletion of `/usr/local/bin/eza` are retired from the
public v3.0 execution path. Review the portable choice if a portable Eza is
explicitly requested and a pinned artifact, owned destination, coexistence
policy, and recoverable inverse are designed and tested. This outcome does
not add an operation to `default` or `server-base`.
