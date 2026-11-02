# GNOME user extension capability

Status: **v3.0 manager path implemented; user-extension inventory remains an
explicit follow-up**, 2026-11-01. The v2 active preset maps
`InstallGnomeExtensions` and `RemoveGnomeExtensions`. It installs
`gnome-extensions-app` and the old browser connector, then uses a mutable
third-party script to install nine shell extensions and restart GNOME Shell.
Its inverse deletes named directories without proving ownership.

## Completion checks defined before implementation

- Replace the obsolete connector with Fedora's `gnome-browser-connector` and
  add the signed Fedora `gnome-extensions-app` package in an opt-in profile.
  Check candidate refusal, plan/apply/repeat/status/remove, package signature
  and file verification, and preservation of a seeded pre-existing user
  extension directory. Do not launch the app or install, enable, or run any
  extension in this package batch.
- Keep the nine historical extension intents visible. Before RIDE installs
  their code, verify the current UUID, GNOME Shell 50 compatibility, upstream
  license and provenance, pinned archive digest, and exact per-user recovery.
  Preserve the enabled-extension list and existing extension directories. Do
  not restart GNOME Shell from an apply operation.
- Compare the Linux package/tool boundary with Windows, update the ledger and
  generated docs, and investigate any failed VM run before retrying.

The v3.0 profile uses Fedora's current GNOME Extensions app and official
browser connector for user-managed extension setup. This keeps extension
selection and activation under the user's control while replacing the v2
remote script. It does not automatically provision the old list; that work
remains visible in H082.

## Legacy extension inventory and current source review

The v2 list and the latest GNOME Extensions directory show eight entries with
an active version that declares GNOME Shell 50 compatibility: Move Clock (ID
2), Removable Drive Menu (7), Coverflow Alt-Tab (97), AppIndicator Support
(615), Bluetooth Quick Connect (1401), System Monitor Next (3010), Extension
List (3088), and Desktop Icons NG (2087). Espresso (4135) currently lists only
GNOME 46 as its newest active version; Caffeine (ID 517) is the current
replacement that declares GNOME 50 support. These are compatibility leads,
not RIDE-managed or tested installations. Source/version and per-user recovery
review is H082.

The official GNOME Extensions app is version 50.0; Fedora 44 packages
`gnome-extensions-app` 50.2-1.fc44 and `gnome-browser-connector` 42.1-14.fc44
from signed Fedora repositories. Fedora's connector is the native messaging
host for the extensions.gnome.org site. The profile remains opt-in and outside
`default`.

Sources: [GNOME Extensions app](https://apps.gnome.org/Extensions/),
[Fedora gnome-extensions-app](https://packages.fedoraproject.org/pkgs/gnome-extensions-app/gnome-extensions-app/),
[Fedora browser connector](https://packages.fedoraproject.org/pkgs/gnome-browser-connector/gnome-browser-connector/),
[GNOME extension installation locations](https://help.gnome.org/system-admin-guide/extensions.html),
[Move Clock](https://extensions.gnome.org/extension/2/move-clock/),
[Removable Drive Menu](https://extensions.gnome.org/extension/7/removable-drive-menu/),
[Coverflow Alt-Tab](https://extensions.gnome.org/extension/97/coverflow-alt-tab/),
[Espresso](https://extensions.gnome.org/extension/4135/espresso/),
[Caffeine](https://extensions.gnome.org/extension/517/caffeine/),
[AppIndicator](https://extensions.gnome.org/extension/615/appindicator-support/),
[Bluetooth Quick Connect](https://extensions.gnome.org/extension/1401/bluetooth-quick-connect/),
[System Monitor Next](https://extensions.gnome.org/extension/3010/system-monitor-next/),
[Extension List](https://extensions.gnome.org/extension/3088/extension-list/),
[DING](https://extensions.gnome.org/extension/2087/desktop-icons-ng-ding/).
