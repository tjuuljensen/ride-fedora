# Browser and media publisher applications

Fast-track owner decisions: keep Chrome, Edge, and Spotify. Opera remains
outside v3 scope.

Status: **five opt-in outcomes operable; one owner exclusion**, updated
2026-11-01. The v2 source family includes
`Chrome`, `Opera`, `Edge`, `SpotifyClient`, `ClementinePlayer`, and
`PulseAudioEq`; Opera is outside the current five-outcome batch. The first three add external browser RPM repositories and
keys with broad removal. Spotify requests `lpf-spotify-client` without
declaring its source. Clementine installs a Fedora RPM. The purported
PulseAudio equalizer function installs the entire `pulseaudio` sound server
and its inverse removes it; no equalizer is installed.

## Completion criteria defined before implementation

- For Clementine, use the signed Fedora 44 RPM and a curated opt-in
  Workstation profile. On the exact x86_64 VM check absent plan, apply,
  RPM signature/files and executable, repeat, status, restore, explicit
  remove, and profile smoke. Reuse mocked DNF failure evidence; leave
  music-library interaction and desktop visual behavior to v3.1.
- For scoped third-party browsers and Spotify, require current publisher method,
  license/terms, source trust, owned repository/key or LPF state, detection,
  inverse, and one disposable-VM happy path before runnable status. Avoid
  modifying browser profiles, playback data, or unrelated repositories.
- Reconcile `PulseAudioEq` with the Fedora 44 audio stack. Do not switch
  sound servers or remove user audio components merely to preserve the
  misleading v2 package name. If Fedora's PipeWire-compatible EasyEffects
  supplies the intended equalizer, use a separate candidate RPM operation
  and opt-in profile with the same VM package lifecycle and no sound-server
  change; leave audio/visual behavior to v3.1. Otherwise record an explicit
  non-runnable replacement or unsupported decision with a review trigger.
- Compare Windows schema/behavior, update ledger and generated docs, and
  investigate any VM failure before retrying.

## External-source decisions

- **Chrome: owner-kept, implemented as an opt-in Flathub candidate.** Google
  publishes a Fedora RPM, but RIDE uses Flathub's signed system remote and its
  `com.google.Chrome` community package for v3.0. Flathub marks the package
  unverified and unaffiliated with Google; the selected source carries the
  proprietary browser. The application profile remains under
  `~/.var/app/com.google.Chrome` when the Flatpak is removed. A separate RPM
  deployment can be added independently after RIDE owns its repository/key.
- **Opera: excluded from v3 by owner decision on 2026-10-30.**
  [Opera ships a Linux RPM and repository](https://rpm.opera.com/), but v2
  imports a global key, installs a developer-channel package, then removes
  fixed key IDs and its repo file without proving ownership. The owner later
  excluded Opera due to vendor ownership concerns. No v3 operation or
  acquisition path is planned. The v2 source and existing machine state remain
  untouched.
- **Edge: owner-kept, implemented as an opt-in Flathub candidate.** Microsoft
  supports Fedora 39+, but its current published RPM repository file sets
  `gpgcheck=0`. RIDE uses Flathub's signed system remote and the
  `com.microsoft.Edge` community package rather than v2's mutable developer
  repository. Flathub marks this package unverified and unaffiliated with
  Microsoft. Its profile remains under `~/.var/app/com.microsoft.Edge` after
  Flatpak removal. Revisit the publisher RPM if Microsoft provides a verifiable
  repository signature lifecycle.
- **SpotifyClient: owner-kept, implemented as an opt-in Flathub candidate.**
  v2 requests `lpf-spotify-client` without declaring a source; Spotify says its
  Linux desktop build is not actively supported. Flathub packages official
  Spotify binaries and uses the signed Flathub system remote, but its package
  is community-maintained and unverified by Spotify. The application profile
  remains under `~/.var/app/com.spotify.Client` after remove. Spotify also
  documents Snap for Linux; a Snap deployment can be added as a distinct
  operation if its source and recovery contract are selected.

The owner retained Chrome, Edge, and SpotifyClient for v3.0 on 2026-10-30.
Their Flathub paths have separate operation IDs and profiles, allowing these
Flatpaks to coexist with independently managed RPM or Snap deployments after
product conflict review. The combined VM test checks package presence, status,
repeat, removal, and profile preservation. Launch, sign-in, sync, playback,
and audio behavior are queued as H078-H079 in v3.1.

The [Fedora 44 PipeWire PulseAudio implementation](https://packages.fedoraproject.org/pkgs/pipewire/pipewire-pulseaudio/)
is already present in the pinned Workstation image; `pulseaudio` and
`pulseaudio-qpaeq` are absent. The v2 `PulseAudioEq` function never
installed an equalizer, so installing the traditional PulseAudio server
would not fulfill its name and could conflict with the image's audio stack.
[Fedora EasyEffects](https://packages.fedoraproject.org/pkgs/easyeffects/easyeffects/)
provides a PipeWire equalizer under GPL-3.0-or-later. Its package-only
replacement is a separate opt-in candidate; RIDE does not
set presets or start audio processing.

## Fedora 44 VM result

[`package.clementine`](../acceptance/package.clementine.md) passed its
individual signed-RPM lifecycle and `music-player` profile smoke in a
disposable Workstation overlay. It is an **operable opt-in candidate**;
music-library interaction and desktop visual behavior are H015 in v3.1.

[`package.easyeffects`](../acceptance/package.easyeffects.md) passed its
individual signed-RPM lifecycle and `audio-effects` profile smoke in a
separate overlay. The test confirmed `pipewire-pulseaudio` remained installed
and `pulseaudio` remained absent after apply and restore. The large Qt
dependency set made the profile reinstall slow, but the test passed without
manual intervention. The `PulseAudioEq` source outcome is migrated to this
PipeWire-compatible **operable opt-in candidate** as the intended equalizer,
without changing sound servers. Actual audio processing, presets, and
desktop visuals are H016 in v3.1. Both profiles require
`--allow-candidate` and stay outside `default`.

Source review: [Google Chrome Fedora package guidance](https://support.google.com/chrome/answer/95346),
[Google signing key](https://www.google.com/linuxrepositories/),
[Chrome Flathub package](https://flathub.org/en/apps/com.google.Chrome),
[Microsoft Fedora support](https://learn.microsoft.com/en-us/deployedge/microsoft-edge-supported-operating-systems),
[Microsoft RPM repository config](https://packages.microsoft.com/yumrepos/edge/config.repo),
[Edge Flathub package](https://flathub.org/en/apps/com.microsoft.Edge),
[Spotify Linux guidance](https://www.spotify.com/download/linux/),
[Spotify Flathub package](https://flathub.org/en/apps/com.spotify.Client),
[Spotify Flathub source](https://github.com/flathub/com.spotify.Client).
