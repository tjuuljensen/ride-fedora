# GNOME utility acceptance: `package.system-config-printer` and `package.gnome-tweaks`

Status: **PASS; operable opt-in candidates** on Fedora 44 x86_64 Workstation,
2026-10-30. The active v2 `InstallGnomeTools`/`RemoveGnomeTools` bundle
splits into two Fedora desktop RPM operations. RIDE does not repeat v2's
unowned `gparted` removal. VM overlay
`20261030T114934Z-test-provider-editors-and-gnome-utilities-batch-2470cb85`
used pinned image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`
and candidate catalog SHA-256
`75e82decf27356aa62d8ff4fb7a5e4aff96d6733650c5aaca72dd4f685e47bec`.
The retained transcript and
`.acceptance-runs/provider-foundation-04-editors-gnome-retry.xml` show
passing individual package plan, apply, signature/files, desktop launcher,
status, repeat, restore, and explicit remove. No pre-existing RPM identity
was lost. Printer RPM installation updated its two pre-existing subpackages;
the updated versions remained. Graphical use and broader recovery remain
v3.1 work. See the [batch review](../migrations/provider-foundation-04.md).
