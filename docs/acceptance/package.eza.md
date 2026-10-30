# `package.eza` acceptance

Status: **PASS; supported Fedora RPM** on Fedora 44 x86_64 Workstation,
2026-10-30. The library-only v2 `InstallEza` path maps to the signed Fedora
[`eza` package](https://packages.fedoraproject.org/pkgs/rust-eza/eza/)
(EUPL-1.2); it does not implement the active v2 GitHub ZIP acquisition.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T115847Z-test-provider-eza-fedora-package-7e06564b`;
candidate catalog SHA-256
`c1f16129b39b488e41cc5f52abac1b126ddddd46adbb088a047e5c6a2b35b46b`.
The retained transcript and
`.acceptance-runs/provider-foundation-08-eza.xml` record one passing test.
The RPM was absent at baseline. The test passed absent plan, candidate-gated
apply, signed RPM and file verification, `/usr/bin/eza --version`, installed
status, unchanged repeat, restore, and explicit install/remove. The install
introduced `eza` 0.23.5, `libgit2`, and `llhttp`; both inverse paths returned
all RPMs to baseline with no pre-existing package changes. `/usr/local/bin/eza`
was absent before and after. The final supported catalog status removes the
temporary candidate gate used during the pilot; the handler and target did
not change. Focused mocked failure evidence for the unchanged DNF handler is
recorded in the [base package checks](package.exfatprogs.md).

The [source decision](../migrations/provider-foundation-08.md) records why
the old GitHub ZIP path is a separate, non-runnable replacement rather than
this acceptance result.
