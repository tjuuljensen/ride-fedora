# Basic editors acceptance: `package.nano` and `package.vim-enhanced`

Status: **PASS; supported package installs** on Fedora 44 x86_64 Workstation,
2026-10-30. The active v2 `InstallBasicEditors`/`RemoveBasicEditors` bundle
splits into two signed Fedora RPM operations. VM overlay
`20261030T114934Z-test-provider-editors-and-gnome-utilities-batch-2470cb85`
used pinned image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`
and candidate catalog SHA-256
`75e82decf27356aa62d8ff4fb7a5e4aff96d6733650c5aaca72dd4f685e47bec`.
The retained transcript and
`.acceptance-runs/provider-foundation-04-editors-gnome-retry.xml` record
passing individual plan, apply, signed RPM/files, command, status, repeat,
restore, and explicit-remove checks. The test first removed `nano` and its
two editor-default dependents in the disposable VM; no other RPM changed.
Both operations recovered their absent baseline. Vim installation updated
two pre-existing Vim RPM versions, retained after inverse. The initial
test-preparation failure and its correction are in the
[batch review](../migrations/provider-foundation-04.md).
