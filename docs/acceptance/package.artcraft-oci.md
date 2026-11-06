# ArtCraft OCI Flatpak candidate acceptance

Owner: RIDE Fedora maintainer. Review date: 2026-11-05. The 14
[publisher Flatpak candidates](../migrations/artcraft-flatpaks.md) remain
opt-in candidates on Fedora 44 and 45 Workstation x86_64. The publisher's
ArtCraft OCI remote has `GPGVerify=false`; a separate GPG-verified user
Flathub remote provides the shared Freedesktop runtime.

## Fedora 44 Workstation x86_64: PASS

The full [VM test](../../tests/acceptance/test_artcraft_flatpaks.py) passed on a
fresh disposable KVM overlay of pinned Fedora 44 Workstation image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
One test passed in 596.43 seconds. Source revision was
`eed301680a9f8d2bf22e107d533b77016ffafa84` with uncommitted changes;
catalog SHA-256 was
`4c05b9c0bb63bad423930876536f186b911c89a240b7dc42ac075c7f49522501`.
The retained transcript is
`.acceptance-runs/artcraft-f44/fedora-44-workstation-x86_64/20261105T144719Z-test-artcraft-suite-fedora-44-85565fc0/transcript.jsonl`
(SHA-256 `c8d08405b217c99b87e6e4bfd8ef8b68754b5f0c3e2b6728ba5a372b849cf1ba`).

The test refused the candidate remote without `--allow-candidate`, added
the user ArtCraft remote with RIDE, checked its exact OCI URL, then installed
each published application ID from origin `artcraft-oci`. It checked an
unchanged repeat install, launched each app for 20 seconds under a virtual
display and session bus, removed each app, and finally removed the RIDE-owned
remote. RIDE checked the observed state after each change. All 14 GUI runs
were still active at the timeout, wrote no stderr, and logged no application
`ERROR` lines:

`artcraft-launcher`, `photocraft`, `vectorcraft`, `filmcraft`, `lightcraft`,
`pdfcraft`, `effectcraft`, `designcraft`, `figcraft`, `wordcraft`, `soundcraft`,
`deckcraft`, `cadcraft`, and `gridcraft`.

The run is a headless startup smoke, not pixel inspection or a full GNOME
desktop workflow. The shared Flathub runtime and app data remain after
package removal. RIDE's remote removal leaves the independently configured
Flathub user remote in place. The headless environment may log display,
accessibility-bus, and software-rendering warnings. DesignCraft uses
`WGPU_BACKEND=gl` for the headless launch check so it does not first try an
unavailable virtual GPU adapter; the installed Flatpak remains unmodified.

## Fedora 45 Workstation x86_64: PASS

The full 14-ref suite passed on a fresh disposable KVM overlay of the newly
built Fedora 45 Workstation image SHA-256
`0f2d8bd7bb44d41a5dd4a4652943b639592b7a43963a73e1e7def6cd29aa9c5e`.
The signed Fedora 45 Everything ISO and direct Fedora package repository were
used to build it. A separate boot check confirmed `VERSION_ID=45`,
`VARIANT_ID=workstation`, x86_64, completed cloud-init, and no cloud-init
errors before the image was registered in
[`tests/acceptance/targets.json`](../../tests/acceptance/targets.json).
The build manifest and boot evidence are under
`.acceptance-runs/fedora-images/fedora-45-workstation-x86_64/`.

One ArtCraft suite test passed in 601.97 seconds. Source revision was
`eed301680a9f8d2bf22e107d533b77016ffafa84` with uncommitted changes;
catalog SHA-256 was
`4c05b9c0bb63bad423930876536f186b911c89a240b7dc42ac075c7f49522501`.
The retained transcript is
`.acceptance-runs/artcraft-f45/fedora-45-workstation-x86_64/20261105T145724Z-test-artcraft-suite-fedora-45-11d34973/transcript.jsonl`
(SHA-256 `0bb89ed4f01c4f5089783f4f4267fce757303b973003be460f22035dc496a9b3`).
All 14 refs listed above installed from `artcraft-oci`, stayed active for the
20-second virtual-display launch with empty stderr, and were removed. The
RIDE-managed ArtCraft remote was removed after the apps; the separately
configured signed Flathub user remote remained. The headless startup limit
stated for Fedora 44 applies here too. Fedora 45 app logs had no startup
`ERROR` lines. Clipboard worker `ERROR` lines appeared only after the test's
timeout closed its virtual X server; the acceptance check excludes those
teardown-only messages.

Two earlier image builds using the Fedora mirror redirector failed during
Anaconda RPM download. Switching the Workstation Kickstart to Fedora's direct
repository endpoint completed the build; the failed images remain retained
under the same image directory for diagnosis.
