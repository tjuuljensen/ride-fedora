# `package.nano` acceptance

Status: **PASS; supported package install** on Fedora 44 x86_64 Workstation,
2026-10-30. The v2 `BasicEditors` bundle maps to signed Fedora
[`nano`](https://packages.fedoraproject.org/pkgs/nano/nano/) and
`vim-enhanced` RPMs. RIDE does not change the user's default editor.

VM evidence: pinned image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T114934Z-test-provider-editors-and-gnome-utilities-batch-2470cb85`;
candidate catalog SHA-256
`75e82decf27356aa62d8ff4fb7a5e4aff96d6733650c5aaca72dd4f685e47bec`.
Preparation removed pre-installed `nano`, `nano-default-editor`, and
`default-editor` to create an absent test baseline; no other RPM changed.
The retained transcript and
`.acceptance-runs/provider-foundation-04-editors-gnome-retry.xml` show absent
plan, apply, signed RPM and files, `nano` command detection, status,
unchanged repeat, restore, and explicit remove. Both inverse paths returned
the full RPM inventory to that baseline. A real host's pre-installed
editor-default dependents are outside this RIDE-owned install check.
See the [bundle acceptance](provider-basic-editors.md).
