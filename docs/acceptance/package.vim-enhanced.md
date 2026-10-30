# `package.vim-enhanced` acceptance

Status: **PASS; supported package install** on Fedora 44 x86_64 Workstation,
2026-10-30. The v2 `BasicEditors` bundle maps to the signed Fedora
[`vim-enhanced` RPM](https://packages.fedoraproject.org/pkgs/vim/vim-enhanced/)
for the `vim` command. RIDE does not change editor preferences.

VM evidence: pinned image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T114934Z-test-provider-editors-and-gnome-utilities-batch-2470cb85`;
candidate catalog SHA-256
`75e82decf27356aa62d8ff4fb7a5e4aff96d6733650c5aaca72dd4f685e47bec`.
The retained transcript and
`.acceptance-runs/provider-foundation-04-editors-gnome-retry.xml` show absent
plan, apply, signed RPM and files, `vim` command detection, status,
unchanged repeat, restore, and explicit remove. The named RPM and new
dependencies were removed by both inverses. DNF updated pre-existing
`vim-data` and `vim-minimal` RPM versions; their identities remained and
RIDE did not downgrade them. See the
[bundle acceptance](provider-basic-editors.md).
