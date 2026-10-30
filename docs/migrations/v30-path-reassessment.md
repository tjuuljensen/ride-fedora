# v3.0 capability and v3.1 hardening reassessment

Status: **migration-path analysis in progress**, 2026-10-30. The owner clarified
that scoped v2 packages and settings remain in scope for v3.0 because their behavior
has proved useful. An obsolete product or unsafe v2 installer calls for a
working successor or a safer owned method, not a package/setting outcome
silently closed by a retirement or unsupported label. An exact legacy product
can be retired as an implementation once its intended capability has a v3.0
path. Earlier individual retirement choices remain historical decisions about
those exact implementations; this review reopens their capability coverage.

The current ledger has 133 package and 36 setting outcomes. Only 54 of those
169 have operable v3 catalog mappings. Six server `Install...` package outcomes
were previously excluded and are now assigned review batches. That makes
**169 in-scope package/setting capabilities, 54 currently operable, nine
owner-retired, one standalone functional replacement, and 105 still needing
an operable v3.0 path**. The ledger's 185 dispositioned outcomes out of
185 measure recorded decisions, not this v3.0 capability coverage.
The two Citrix and two Opera functions remain explicitly out of scope. Host-specific
users, shares, secrets, and IP values remain outside the public catalog;
generic package behavior can be modeled without publishing them.

The v3.0 acceptance rule remains proportionate: use the existing brief native
RPM lifecycle for low-risk packages; a focused mock plus a disposable Fedora
44 x86_64 happy path for third-party or desktop candidates; and deeper
recovery proof for data, storage, encryption, and security changes. Broader
failure matrices, extra targets, visual checks, and optional workflows may
stay in v3.1. A v3.0 candidate is explicitly opt-in and does not enter the
base profiles. This is less than exhaustive review, while still proving the
declared behavior and a safe inverse.

## Audit of the named v3.1 queue

The [generated queue](progress.md#v31-hardening-queue) has 23 items. Three
include source or successor decisions that must be made as v3.0 migration
work; their remaining broader behavior checks may stay in v3.1.

| Item | v3.0 boundary | v3.1 remainder |
| --- | --- | --- |
| H001 | Fedora 44 x86_64 remains the declared target. | More distributions, releases, and architectures. |
| H002 | Candidate happy path and focused handler failure evidence. | Extended failure and recovery matrix. |
| H003 | Observe the declared desktop behavior when package checks cannot. | Broader visual and accessibility review. |
| H004 | Verify the declared online artifact and ownership. | Offline acquisition and provider fallback. |
| H005 | Preserve pre-existing RPMs during the alien lifecycle. | Dependency-residue cleanup policy. |
| H006 | Preserve pre-existing desktop RPMs. | Wider dependency-residue review. |
| H007 | Select a maintained GUI IRC successor for the final-release HexChat path; retain the existing opt-in package claim meanwhile. | Wider desktop compatibility and profile migration. |
| H008 | Record package-driven changes relevant to the accepted operation. | Broad pre-existing RPM update review. |
| H009 | Install the declared kernel development RPMs. | Match a running kernel only for a module-building workflow. |
| H010 | Install or restore RIDE-owned editor RPMs. | Removal of pre-installed, unowned editor defaults. |
| H011 | Core Volatility 3 install is already opt-in operable. | Optional plugins and wider virtual-environment recovery. |
| H012 | The v2 outcome installed the monitoring extension and sensors; v3.0 proves that package pair. | GNOME activation, visuals, and wider recovery. |
| H013 | The v2 package outcome installs Solaar/ACPI; v3.0 proves the package lifecycle. | Receiver pairing and hardware UI. |
| H014 | The file-manager package pair is opt-in operable. | Interactive and visual workflows. |
| H015 | Clementine package install is opt-in operable. | Music-library interaction and visuals. |
| H016 | EasyEffects package install is opt-in operable. | Audio presets and visual behavior. |
| H017 | Projecteur package install is opt-in operable. | Spotlight hardware and visual behavior. |
| H018 | Five GNOME boolean settings have a tested user-session lifecycle. | Visual effects and unset-versus-explicit defaults. |
| H019 | Network/communications package bundles have an opt-in lifecycle. | Capture, TFTP, serial, and remote-use workflows; separate v2 state outcomes still need v3.0 paths. |
| H020 | NetworkManager plugin RPMs are supported. | Credential and GUI use; v2 VPN profile outcomes separately need v3.0 paths. |
| H021 | KeePassXC RPM lifecycle is supported. | Vault workflows; package installation does not manage vault contents. |
| H022 | Choose a maintained bandwidth-test CLI path now; existing Fedora speedtest-cli install evidence remains valid. | Wider network/server behavior. |
| H023 | Choose a maintained video-downloader path now; existing youtube-dl install evidence remains valid. | Wider extractor and site compatibility. |

## First source and replacement paths

These are reviewed acquisition candidates, not accepted v3 operations. A
batch still checks product/license, provenance, version pin, actual package
files, detection, inverse, and the declared target. In particular, do not
copy a v2 download script or run a remote installer during apply.

| v2 capability | v3.0 path to evaluate | Evidence and unresolved point |
| --- | --- | --- |
| Video downloader | Add Fedora 44 `yt-dlp` as a distinct native RPM operation; compare its CLI intent with `youtube-dl` before changing a published ID. | [Fedora package](https://packages.fedoraproject.org/pkgs/yt-dlp/yt-dlp/); real site compatibility belongs to broader testing. |
| GUI IRC client | Keep the HexChat opt-in install while piloting Fedora `konversation` as a maintained GUI alternative. | [HexChat final release](https://hexchat.github.io/news/2.16.2.html), [Fedora Konversation](https://packages.fedoraproject.org/pkgs/konversation/konversation/). Its Qt UI and user profile differ; do not claim an automatic profile migration. |
| Bandwidth-test CLI | Evaluate the publisher's pinned `librespeed-cli` Linux artifact as a portable operation. | [LibreSpeed releases](https://github.com/librespeed/speedtest-cli/releases) and [LGPL-3.0 license](https://github.com/librespeed/speedtest-cli). It uses LibreSpeed servers rather than the old speedtest.net service, so this is a product-level choice. |
| GNOME Files checksum and image actions | Owner retired both user-visible capabilities on 2026-10-30. The previously researched owned-script path is retained only as historical analysis. | [GNOME Scripts location and context menu](https://help.gnome.org/gnome-help/nautilus-behavior.html), [Fedora ImageMagick](https://packages.fedoraproject.org/pkgs/ImageMagick/ImageMagick/). |
| GNOME extension installer/management | Use Fedora's `gnome-extensions` CLI and Extensions app, with explicit extension IDs and per-user ownership. | [Fedora GNOME Shell CLI](https://packages.fedoraproject.org/pkgs/gnome-shell/gnome-shell/fedora-44.html), [Extensions app](https://packages.fedoraproject.org/pkgs/gnome-extensions-app/gnome-extensions-app/). The old archived helper is unnecessary if the native path passes. |

## Formerly excluded server package paths

These six outcomes now have ledger rows and isolated review batches. The
active source remains `network-devices`. Reconcile consumers, runtime
identity, publication, state, and rollback before transferring generic
behavior. The old preset selectors do not establish actual installation.

| Source function | v3.0 package path to investigate | Ownership boundary |
| --- | --- | --- |
| `InstallqBittorrentServer` | **Kept by owner.** Fedora 44 [`qbittorrent-nox`](https://packages.fedoraproject.org/pkgs/qbittorrent/qbittorrent-nox/). | Package first; service user, firewall, SSH keys, and downloads require separate owned operations. |
| `InstallPlexServer` | **Kept by owner.** [Plex's RPM repository](https://support.plex.tv/articles/235974187-enable-repository-updating-for-supported-linux-server-distributions/) with scoped signing key and service state. | Preserve media, metadata, accounts, and pre-existing repository files. |
| `InstallPlexAutoUpdate` | **Update capability kept; separate updater under review.** Plex documents public release updates through its RPM repository and DNF. Reconcile this with server AutoUpdate and Cockpit settings before adding a separate timer. | Never execute the old mutable remote installer; preserve existing timers and credentials. |
| `InstallAMP` | **Kept by owner.** Obtain a reviewed publisher artifact or managed package before catalog execution. | [AMP is licensed](https://cubecoders.com/AMP/Corvid19); keep keys, instances, ports, and users private. The v2 remote script is not an accepted method. |
| `InstallFerium` | **Kept by owner.** Pin the current publisher Linux release and install a user or system portable binary with an owned manifest. | [Current Ferium releases](https://github.com/gorilla-devs/ferium/releases); preserve modpacks and profiles. |
| `InstallMinecraftServer` | **Kept by owner.** Choose the [official Java server JAR](https://www.minecraft.net/en-us/download/server) and compatible Java runtime, then own a versioned service path. | The v2 function installed Java 8 and made a directory, but did not install a server JAR. Preserve worlds and EULA state. |

## Next implementation slices

1. Complete the source, consumer, runtime identity, publication, and recovery
   audit for the six newly scoped server packages; keep host-specific actions
   in the source repository until ownership is recorded.
2. Pilot the Fedora-native `yt-dlp` and `qbittorrent-nox` package operations
   with brief exact-target lifecycles; reuse the unchanged DNF handler's
   failure evidence. These two establish a low-risk path without new
   acquisition handlers.
3. Pilot publisher RPM and portable artifact handlers separately with an
   in-scope product such as Ferium.
4. Reopen the remaining retired or unsupported package/setting capabilities
   by user-visible intent. GNOME string/list settings need a value-aware
   handler and prior-state journal; conflicting variants need distinct
   profile values. Keep the full mapping visible until each has a working
   operation or functional replacement.
