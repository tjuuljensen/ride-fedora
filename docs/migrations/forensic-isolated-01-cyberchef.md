# Forensic Isolated 01 follow-up: CyberChef offline desktop app

Status: **operable opt-in candidate on Fedora 44 Workstation x86_64**,
2026-10-30. The v2 `InstallCyberChef` selects the first mutable GitHub release
asset, extracts to `/usr/lib/cyberchef`, and writes an unowned desktop entry.
`RemoveCyberChef` uses invalid `rmdir` flags, so it does not provide a useful
inverse. The kept v3.0 capability is an offline CyberChef browser app and
desktop launcher on Fedora 44 Workstation x86_64.

## Completion checks defined before implementation

- Use upstream v11.5.0's exact release ZIP
  `CyberChef_8cd426dd4f40f1423912d5fad91b578a86a65112.zip`, 83,125,922
  bytes, with the release API SHA-256
  `f6478925d3eaa16ec08626a85f5b85eed10d531a5e18700615fed7ecb024cccf`.
  The downloaded bytes must match. Fetch the Apache-2.0 LICENSE from the same
  tag and verify SHA-256
  `58d1e17ffe5109a7ae296caafcadfdbe6a7d176f0bc4ab01e12a689b0499d8bd`.
  Retain all 30 bundled `*.LICENSE.txt` notices. The GitHub API digest is
  publisher release metadata, not an independent signature.
- Reject archive traversal, symlinks, duplicates, or excessive expansion
  before extraction. Require the versioned HTML entry, assets, icon, and
  bundled notices. Install only into `/opt/ride-fedora/cyberchef` and link
  `/usr/share/applications/ride-cyberchef.desktop` to an owned desktop file.
  Refuse existing destinations. Do not write browser profiles, recipes, or
  user directories.
- Detect the exact owned content and launcher. Restore or explicit remove
  must refuse an unowned or modified tree or desktop link; preserve sibling
  files. Use a focused mocked test for bad digest, unsafe archive, occupied
  path, modified content, and failed acquisition. In one disposable Fedora 44
  Workstation x86_64 VM, check plan, candidate gate, apply, repeat, status,
  offline page and launcher, browser startup if automatable, restore,
  explicit remove, and sibling preservation. Investigate failures before
  retrying.
- Count only the passing opt-in candidate as operable. Keep it out of
  `default`; leave broader browser interaction, visual checks, and archive
  update paths to a named v3.1 hardening item. Update the catalog, ledger,
  generated docs, Windows alignment, and acceptance record after evidence.

The [official v11.5.0 release](https://github.com/gchq/CyberChef/releases/tag/v11.5.0)
publishes the ZIP and digest. Its
[tagged LICENSE](https://github.com/gchq/CyberChef/blob/v11.5.0/LICENSE)
is Apache-2.0. Local inspection of the exact ZIP found 139 entries with
83,108,870 uncompressed bytes, no symlinks or traversal entries, the
`CyberChef_v11.5.0.html` entry and `images/cyberchef-128x128.png` icon.

## Result

The [focused disposable VM run](../acceptance/package.cyberchef.md) passed
the pinned ZIP and license checks, offline Firefox headless startup, owned
manifest and desktop link observation, unchanged repeat, restore, and
explicit remove. The sibling system file and user document remained intact.
No manual session was needed. Broader visual behavior, recipe workflows,
and a version-update path remain H028.
