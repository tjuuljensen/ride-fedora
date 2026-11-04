# `package.gearlever` acceptance

Status: **PASS; operable opt-in candidate on Fedora 44 Workstation x86_64**,
2026-11-01.

This is an opt-in Flatpak candidate replacing the v2 AppImageLauncher
installation path with Gear Lever from the GPG-verified Flathub system remote.
Gear Lever is the AppImage integration manager; RIDE does not import, move,
update, or remove user AppImages. The operation removes only the system app
ref and does not pass Flatpak's `--delete-data` option.

The VM verified that the legacy `appimagelauncher` RPM was absent, the GPG-
verified Flathub system remote was configured, and the operation refused
without `--allow-candidate`. It installed application ID
`it.mijorus.gearlever` from origin `flathub`; CLI help, status, repeat, and
removal passed. Seeded Gear Lever settings, a pre-existing `~/Applications`
directory, an unrelated AppImage file, and its desktop entry retained their
contents, owner, and mode after removal. The VM did not launch a GUI or process
an AppImage; H070 tracks visual and integration behavior.

The Flathub listing identifies application ID `it.mijorus.gearlever`, version
4.6.2, GPL-3.0, and x86_64 availability. See [Flathub](https://flathub.org/en/apps/it.mijorus.gearlever),
[upstream repository](https://github.com/mijorus/gearlever), and [upstream
feature list](https://github.com/mijorus/gearlever#features).

Exact target: Fedora 44 Workstation x86_64, image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`;
catalog SHA-256
`b43cc3771732ee6379493541a649280f1b7307fecb09b0d01218bb8dcf186b36`;
source revision `9da0526d412343076d6327c6cb3c5331be6d773a` with uncommitted
migration changes. TCG transcript:
[transcript.jsonl](../../.acceptance-runs/legacy-vm/.tmp-vm-acceptance-publisher-01-gearlever-final/fedora-44-workstation-x86_64/20261101T150144Z-test-gearlever-flatpak-lifecycle-preserves-existing-appimages-and-user-state-505bd929/transcript.jsonl),
SHA-256 `f2dacde4c664261bb0e57dd673f17a7e7a1fe6a79291bc76a51ec498ef293be2`.
Run IDs: Flathub setup `20261101T150411Z-2948-22083`, apply
`20261101T150433Z-3551-7336`, repeat `20261101T150648Z-4243-24779`,
remove `20261101T150655Z-4476-27765`.
