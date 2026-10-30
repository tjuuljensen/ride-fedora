# `package.gnome-tweaks` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 x86_64 Workstation,
2026-10-30. The v2 `GnomeTools` bundle maps its old `gnome-tweak-tool` name
to Fedora's signed
[`gnome-tweaks` RPM](https://packages.fedoraproject.org/pkgs/gnome-tweaks/gnome-tweaks/).
RIDE installs the UI without changing GNOME settings.

VM evidence: pinned image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T114934Z-test-provider-editors-and-gnome-utilities-batch-2470cb85`;
candidate catalog SHA-256
`75e82decf27356aa62d8ff4fb7a5e4aff96d6733650c5aaca72dd4f685e47bec`.
The retained transcript and
`.acceptance-runs/provider-foundation-04-editors-gnome-retry.xml` show absent
plan, apply with `--allow-candidate`, signed RPM and files, installed
desktop launcher, status, unchanged repeat, restore, and explicit remove.
Both inverse paths returned the full RPM inventory to baseline; `gparted`
was untouched. Graphical use and broader failure/recovery are v3.1 H002/H003.
See the [bundle acceptance](provider-gnome-tools.md).
