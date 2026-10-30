# GNOME extension installer disposition

Status: **unsupported for v3.0**, 2026-10-30.
The owner deferred the keep-or-retire decision again in the v3.0 fast-track
review. Compare current GNOME extension tools before resolving this helper.
The active v2 `InstallGnomeExtInstaller` clones an unpinned Git repository
into `/opt` and force-links its script over `/usr/local/bin/gnome-shell-extension-installer`.
`RemoveGnomeExtInstaller` recursively deletes that directory and symlink
without checking ownership. The
[upstream project](https://github.com/brunelli/gnome-shell-extension-installer)
is GPL-2.0 licensed but was archived by its owner in March 2023. Its README
documents old GNOME Shell versions and direct installation from a mutable
`master` script. No current Fedora 44 GNOME compatibility or safe owned-path
recovery evidence is available.

RIDE v3.0 provides no runnable operation for this source outcome. This is a
reasoned unsupported disposition, not an installer success. Reopen only if
a maintained, licensed extension-installation tool supports the declared
Fedora/GNOME target and has a pinned acquisition method, ownership-aware
destination, and tested removal. GNOME's own extension management can be
reviewed as a separate replacement when there is a concrete user need.
