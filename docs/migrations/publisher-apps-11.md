# Browser and media publisher applications

Status: **two opt-in candidates, three unsupported decisions, and one owner-approved retirement**, 2026-10-30. This commented-preset batch maps
`Chrome`, `Opera`, `Edge`, `SpotifyClient`, `ClementinePlayer`, and
`PulseAudioEq`. The first three add external browser RPM repositories and
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
- For third-party browsers and Spotify, require current publisher method,
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

- **Chrome: unsupported and non-runnable in v3.0.**
  [Google ships a Fedora RPM](https://support.google.com/chrome/answer/95346)
  that adds its own update repository. The v2 function writes an HTTP
  repository URL directly and its inverse removes the repository path
  without checking ownership. Migrate via an official RPM with
  verified publisher source, repository/key collision handling, and
  browser-profile-preserving Fedora VM lifecycle.
- **Opera: retired and non-runnable by owner decision on 2026-10-30.**
  [Opera ships a Linux RPM and repository](https://rpm.opera.com/), but v2
  imports a global key, installs a developer-channel package, then removes
  fixed key IDs and its repo file without proving ownership. No v3 Opera
  install is planned. Reopen only on a new explicit request for a selected
  channel with owned repo/key and a VM inverse that preserves profiles and
  other Opera products. The v2 source and any existing machine state remain
  untouched.
- **Edge: unsupported and non-runnable.**
  [Microsoft supports Fedora 39+](https://learn.microsoft.com/en-us/deployedge/microsoft-edge-supported-operating-systems)
  for Edge Linux. The v2 function selects the developer channel from a
  mutable repository; its inverse deletes a fixed repo file but does not
  own the system key. Reopen for a selected channel and pinned publisher
  source with collision-safe repository/key handling and Fedora 44 VM
  evidence.
- **SpotifyClient: unsupported and non-runnable.** v2 requests
  `lpf-spotify-client` with no source declaration. The
  [LPF mechanism](https://packages.fedoraproject.org/pkgs/lpf/lpf/) is
  interactive and builds a local package from a licensed download; the
  [negativo17 Fedora repackaging](https://negativo17.org/spotify-client/)
  is a different source with its own repository and terms. Reopen on an
  explicitly chosen acquisition method with license/terms, owned state,
  unattended-install decision, and profile-preserving VM lifecycle.

The owner retained optional Chrome for migration on 2026-10-30. Its v3.0
status remains non-runnable until the official source, repository/key
ownership, and seeded browser-profile recovery pass on Fedora 44 Workstation.

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
