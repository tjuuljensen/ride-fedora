# `package.unrar` acceptance

Status: **PASS; supported** on Fedora 44 Workstation x86_64. Reviewer: Codex,
2026-10-30. Fedora's signed [`unrar` wrapper RPM](https://packages.fedoraproject.org/pkgs/unrar-free/unrar/)
provides `/usr/bin/unrar` through the GPL-2.0-or-later `unrar-free` project.
It restores the v2 command name for common RAR listing and extraction;
[Fedora's package description](https://packages.fedoraproject.org/pkgs/unrar-free/unrar-free/)
does not claim feature parity with the non-free implementation.

One focused disposable VM test passed in 392.34 seconds on the pinned Fedora
44 Workstation x86_64 image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
QEMU used `tcg` acceleration. The retained overlay is
`20261030T200959Z-test-provider-unrar-wrapper-lifecycle-72dfe14a` under
`.acceptance-runs/unrar/fedora-44-workstation-x86_64/`.
Its `metadata.json` records candidate catalog SHA-256
`5b7185b4d3176a11f960ceeed10ab9ea2f6582d714166c885d17068faf2de62b`,
source revision `161359e`, and an uncommitted source bundle;
`transcript.jsonl` and `.acceptance-runs/unrar-tcg.xml` retain guest commands
and the passing result.

The test checked absent plan, apply, signed RPM and files, `unrar --version`,
installed status, unchanged repeat, restore, and explicit install/remove.
Both inverse paths returned the full RPM inventory to baseline. The
pre-existing 7-Zip RPM remained at the same version. The unchanged DNF
handler's mocked failure evidence is in [base package checks](package.exfatprogs.md).
No archive or user data was changed and no manual session was needed.
The separate `archive-tools` profile smoke also passed (one test, 297.59
seconds) in overlay
`20261030T201924Z-test-archive-tools-opt-in-profile-4b20c9a4`, using the
same pinned image and QEMU TCG. Its supported-state catalog SHA-256 was
`99768ced1341fbe63d48fdf2f9ccd9d7cf1a0e1396199fc36cb93faada05da74`;
the retained `.acceptance-runs/archive-profile-tcg.xml` and transcript show
plan, apply, unchanged repeat, and restore with 7zip preserved.
The [batch record](../migrations/provider-foundation-03-unrar.md) and
[Windows alignment](../windows-alignment.md#fedora-archive-unrar-preflight-2026-10-30)
record the scope. The opt-in `archive-tools` profile selects `7zip` and
`unrar`; `unar` remains separately available. H026 covers RAR feature
compatibility beyond the package-install claim.
