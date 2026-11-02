# `package.nano-default-editor` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64,
2026-11-01.

Fedora 44 Workstation x86_64 candidate operation for Fedora's
`nano-default-editor` 8.7.1-2.fc44 RPM (GPL-3.0-or-later). The package owns the common-shell configuration
that selects nano when `EDITOR` is unset; the existing `package.nano` operation
continues to install the editor without changing that preference.

The signed RPM lifecycle, Bash default and override behavior, package
verification, repeat, and recovery passed. Broader CSH and fish runtime
behavior remains in H061. See the
[06AI batch acceptance report](security-lab-default-editor.md).
