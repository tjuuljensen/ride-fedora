# ArtCraft publisher OCI Flatpak candidates

Owner decision: add the published Craft apps and ArtCraft Launcher as opt-in
Fedora 44 and 45 Workstation x86_64 candidates. Use Flatpak for this batch;
the owner has had trouble with other Linux installer formats. Install, an
error-free application launch, and removal are the acceptance bar. No archive
download or offline dependency collection is required for the v3 path.

## Source disposition

`CheckArtCraftDownloads`, `GetArtCraft`, and `GetArtCraftDependencies` in
[`lib/artcraft/lib-artcraft.sh`](../../lib/artcraft/lib-artcraft.sh) prepare an
archive; none installs or observes a host application. Keep them as standalone
reference utilities. They do not map one-to-one to the new package operations,
and the archive helper is not loaded by the v3 client.

The [publisher's Linux page](https://getartcraft.com/linux) documents a
per-user `artcraft-oci` Flatpak remote and the Launcher/app IDs. The descriptor
at `https://getartcraft.com/artcraft-oci.flatpakrepo` reported
`Url=oci+https://getartcraft.com` and `GPGVerify=false` on 2026-11-05.
The [publisher OCI index](https://getartcraft.com/index/static) exposed these
14 x86_64 stable refs at review time (observed index SHA-256
`bae026074f3fe90d6fc3af9d6731ba9e6a22104bebbb3b5761cd7d2b18d8bc86`):

| RIDE IDs | Publisher refs |
| --- | --- |
| `package.artcraft-launcher`, `package.photocraft`, `package.vectorcraft`, `package.filmcraft`, `package.lightcraft`, `package.pdfcraft`, `package.effectcraft` | `ai.storyteller.<ID suffix>` |
| `package.designcraft`, `package.figcraft`, `package.wordcraft`, `package.soundcraft`, `package.deckcraft`, `package.cadcraft`, `package.gridcraft` | `ai.storyteller.<ID suffix>` |

Each operation selects its own fixed application ID and removes only its own
per-user Flatpak ref. RIDE does not delete `~/.var/app/<app-id>`, user projects,
or the shared Flatpak runtime. The separately selectable
`setting.artcraft-oci-user-remote` owns its remote marker and refuses removal
while any user application still has that origin. The app operation accepts an
already configured exact official remote; it does not claim or remove it.
The first Fedora 44 VM attempt showed that ArtCraft's OCI remote does not
provide `org.freedesktop.Platform`. A separate GPG-verified per-user Flathub
remote is required for the runtime; RIDE checks it before installing an app
and leaves that shared remote and runtime outside ArtCraft package removal.
See the [operator steps](../runbooks/artcraft-flatpaks.md).

This is a publisher-operated HTTPS app source with an unsigned Flatpak OCI remote.
The remote descriptor does not enable GPG verification, and RIDE does not
pin individual OCI manifests or independently authenticate the publisher's
index. Flathub's signed user remote verifies the shared runtime. Candidate
gating and explicit source/origin checks limit accidental
selection; they do not turn this preview source into a signed repository.
Publisher repository metadata lists Apache-2.0 for code; individual bundled
assets and ArtCraft branding have separate terms. The current
[`storytold/artcraft` release](https://github.com/storytold/artcraft/releases)
does not publish a Linux installer for ArtCraft Studio. Other suite products
without an x86_64 ref in the reviewed OCI index are outside this batch.

## Acceptance and recovery

The runnable candidates are restricted to Fedora 44 and 45 Workstation
x86_64. The [mock lifecycle tests](../../tests/test_v3_artcraft_flatpak.py)
cover remote ownership, exact origin, install, repeat, removal, user-data
preservation, and failure refusal. The
[VM test](../../tests/acceptance/test_artcraft_flatpaks.py) checks each
published ref on each target. Keep candidate status after VM acceptance, as
requested. The [acceptance record](../acceptance/package.artcraft-oci.md)
reports all 14 refs passing the Fedora 44 Workstation lifecycle and Fedora 45
remaining pending until its Workstation image is verified and pinned.

If an app was installed before RIDE or ArtCraft Launcher later updates it,
RIDE can observe that it exists at the selected origin but cannot prove that
it installed that instance. Run-journal restore removes a newly installed ref
only when the selected source definition still matches. Do not use RIDE to
remove a pre-existing app on the basis of a product name alone.
