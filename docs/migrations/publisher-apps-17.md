# GNOME user extension bundle

Status: **decision deferred by owner; unsupported for v3.0**, 2026-10-30. This isolated high-risk
active-preset outcome maps `InstallGnomeExtensions` and
`RemoveGnomeExtensions`. The v2 function installs GNOME management packages,
then uses a mutable third-party script to fetch ten extension IDs and
restart GNOME Shell. Its inverse recursively deletes named directories in
the user's extension tree without proving ownership.

## Completion criteria defined before a runnable operation

- Review each extension ID, upstream maintainer, license, artifact, and
  GNOME 50 compatibility. Pin bytes or a trusted provider; do not execute
  remote scripts. Keep the extension manager and browser connector as
  separate package concerns.
- Capture existing user extension state. Install into owned paths only and
  restore only RIDE-created files; preserve unrelated versions, preferences,
  and pre-existing directories. Mock conflicts and failure cleanup, then
  run a disposable Fedora 44 x86_64 Workstation lifecycle with seeded
  extension data. Use one brief manual GNOME session only if the visual
  result cannot be observed automatically.
- Require this user-data recovery evidence before an operation is runnable;
  a candidate flag cannot waive the high-risk gate.

Fedora 44 publishes [`gnome-extensions-app`](https://packages.fedoraproject.org/pkgs/gnome-extensions-app/gnome-extensions-app/)
and [`gnome-browser-connector`](https://packages.fedoraproject.org/pkgs/gnome-browser-connector/gnome-browser-connector/),
but those RPMs do not reproduce the ten user add-ons. RIDE v3 has no
extension acquisition or per-user ownership handler, and the v2 inverse
could delete pre-existing user data. This source outcome is **non-runnable
unsupported in v3.0**. The owner deferred the capability decision on
2026-10-30. Reopen when the extension list and exact-target
seeded-data inverse meet the criteria above; a package-manager UI alone is
not counted as this bundle.
