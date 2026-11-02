# GNOME extension installation paths

Status: **PASS; operable opt-in candidate**, 2026-11-01.
The v3.0 migration preserves browser-driven GNOME extension installation
through Fedora's supported native connector; extension add-ons remain a
separate user action.

The active v2 `InstallGnomeExtInstaller` clones an unpinned Git repository
into `/opt` and force-links its script over
`/usr/local/bin/gnome-shell-extension-installer`.
`RemoveGnomeExtInstaller` recursively deletes that directory and symlink
without checking ownership. The
[upstream project](https://github.com/brunelli/gnome-shell-extension-installer)
is GPL-2.0 licensed but was archived by its owner in March 2023. Its mutable
`master` clone and unowned path replacement are obsolete and unsafe to carry
forward as-is.

## Current Fedora path

Fedora 44 offers a current alternative. The signed Fedora
[`gnome-browser-connector` RPM](https://packages.fedoraproject.org/pkgs/gnome-browser-connector/gnome-browser-connector/)
is version `42.1-14.fc44`, GPL-3.0-or-later, and supplies the native host
connector for [GNOME Shell browser integration](https://gnome.pages.gitlab.gnome.org/gnome-browser-integration/pages/gnome-browser-integration.html).
The browser add-on is installed separately from the browser's extension store.
The Fedora [`gnome-extensions-app` package](https://packages.fedoraproject.org/pkgs/gnome-extensions-app/gnome-extensions-app/)
is version `50.2-1.fc44`, GPL-2.0-or-later; the GNOME app manages installed
extensions, their updates, preferences, and removal. GNOME documentation
places per-user extensions under `~/.local/share/gnome-shell/extensions/<uuid>`.

For v3.0, migrate the helper's user-visible purpose as an opt-in Fedora
`gnome-browser-connector` package. This keeps GNOME's current browser-driven
extension installation available without carrying forward the archived,
un-pinned CLI clone or its unowned `/opt` and `/usr/local/bin` writes. The
browser add-on remains user-installed and browser-specific. RIDE does not
select extension UUIDs or change per-user extension state in this operation.
The separate `GnomeExtensions` bundle and its nine legacy extension IDs remain
in scope under [`publisher-apps-17`](publisher-apps-17.md); they need a
separate compatibility and data-recovery path.

## Completion checks defined before implementation

- Add one opt-in Fedora 44 Workstation x86_64 RPM operation for the current
  native messaging connector. Record package source, version, GPL-3.0-or-later,
  signed-RPM verification, detection, and owned remove inverse.
- Reuse unchanged DNF handler tests; in a disposable VM verify candidate
  refusal, plan, signed RPM and files, connector host presence, repeat, status,
  restore, explicit install/remove, and package inventory recovery.
- Preserve browser add-ons and user extension directories. Do not start a
  browser or install, enable, update, or remove any extension during acceptance.
- Keep browser add-on installation as a documented user handoff; keep the
  package and browser choice opt-in and out of base profiles.
- Compare the shared catalog/profile/run contract with Windows and record
  platform-specific implementation differences.

## Implementation and acceptance

Catalog operation `package.gnome-browser-connector` and opt-in profile
`fedora-gnome-browser-connector` implement the Fedora-native handoff. The
focused Fedora 44 lifecycle passed candidate refusal, plan, signed package and
file verification, repeat, status, restore, explicit install/remove, and
package inventory recovery. It preserved a seeded user extension directory
without starting a browser. Full run IDs, image and catalog hashes, and the
transcript digest are recorded in
[`package.gnome-browser-connector` acceptance](../acceptance/package.gnome-browser-connector.md)
and in the progress ledger. H069 tracks browser add-on compatibility and
future extension-state ownership; it does not gate the v3.0 RPM operation.
