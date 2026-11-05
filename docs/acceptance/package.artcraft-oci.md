# ArtCraft OCI Flatpak candidate acceptance

Owner: RIDE Fedora maintainer. Review date: 2026-11-05. The 14
[publisher Flatpak candidates](../migrations/artcraft-flatpaks.md) remain
opt-in candidates on Fedora 44 and 45 Workstation x86_64. The publisher's
ArtCraft OCI remote has `GPGVerify=false`; a separate GPG-verified user
Flathub remote provides the shared Freedesktop runtime.

## Fedora 44 Workstation x86_64: PASS

The full [VM test](../../tests/acceptance/test_artcraft_flatpaks.py) passed on a
fresh disposable TCG overlay of pinned Fedora 44 Workstation image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
One test passed in 1998.74 seconds. Source revision was
`cd67fa3ae134fceac06cbea72a4467132dcce8ce` with uncommitted changes;
catalog SHA-256 was
`eac802934d182c0411ca89af995ec8b4a0dbc232b235e280654207bf235ee866`.
The retained transcript is
`.acceptance-runs/artcraft-f44/fedora-44-workstation-x86_64/20261105T133440Z-test-artcraft-suite-fedora-44-15ac06e5/transcript.jsonl`
(SHA-256 `70d39c1ea019349830b6e660d0f7631b1b839e7fca8f188ab9fcd8d1fa15be04`).

The test refused the candidate remote without `--allow-candidate`, added
the user ArtCraft remote with RIDE, checked its exact OCI URL, then installed
each published application ID from origin `artcraft-oci`. It checked an
unchanged repeat install, launched each app for 20 seconds under a virtual
display and session bus, removed each app, and finally removed the RIDE-owned
remote. RIDE checked the observed state after each change. All 14 GUI runs
were still active at the timeout and wrote no stderr:

`artcraft-launcher`, `photocraft`, `vectorcraft`, `filmcraft`, `lightcraft`,
`pdfcraft`, `effectcraft`, `designcraft`, `figcraft`, `wordcraft`, `soundcraft`,
`deckcraft`, `cadcraft`, and `gridcraft`.

The run is a headless startup smoke, not pixel inspection or a full GNOME
desktop workflow. The shared Flathub runtime and app data remain after
package removal. RIDE's remote removal leaves the independently configured
Flathub user remote in place.

## Fedora 45 Workstation x86_64: pending

No Fedora 45 Workstation ArtCraft lifecycle is accepted yet. Two attempts to
build the local Workstation image stopped at Anaconda RPM download failure;
the second reached 9% of 2.09 GiB. The incomplete qcow2 images are retained
under `.acceptance-runs/fedora-images/fedora-45-workstation-x86_64/`, with
the latest installer serial log in that directory. No verified Fedora 45
Workstation target is pinned in `tests/acceptance/targets.json`. Repeat the
same full VM suite after a Fedora 45 Workstation image is built, boot-verified,
and registered. Do not infer Fedora 45 behavior from the Fedora 44 result.
