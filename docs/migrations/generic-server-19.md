# Generic Server 19: Ferium

Status: **operable opt-in candidate** on Fedora 44 Server x86_64.

The owner kept `InstallFerium` in the v3.0 scope. Its outcome is a Minecraft
mod and modpack manager, so migration must install the CLI without changing
Ferium configuration, mod profiles, or any selected Minecraft instance.

## Current upstream path

Ferium's publisher provides the exact `ferium-linux-nogui.zip` release asset
for Linux x86_64. The no-GUI
variant is intended for server environments without an XDG Desktop Portal;
the release page also says the executable has no external runtime dependency.
Ferium is licensed under MPL-2.0. Its Linux configuration defaults to
`$XDG_CONFIG_HOME/ferium/config.json` or `~/.config/ferium/config.json`, and
contains profile and modpack information. The publisher documents manual
release installation and updates, so a v3 operation should use a fixed
release URL and reviewed digest rather than a moving latest-release scrape.

The current upstream release reviewed for this path is [Ferium v4.7.1], asset
[`ferium-linux-nogui.zip`]. The candidate target is Fedora 44 Server x86_64.
The release page provides no checksum asset for Linux (it publishes a checksum
only for the Windows MSVC archive). v3.0 therefore uses the fixed release URL
over HTTPS, checks that the executable reports v4.7.1, and records the archive
and extracted binary SHA-256 values in a private ownership record. This is
observed-digest verification, not independent publisher checksum validation;
H096 queues stronger provenance if Ferium publishes it.

## Proposed v3 contract

- Use the opt-in `package.ferium-portable` operation for the declared Server
  target, installed to a RIDE-owned user-local directory and exposed through
  an owned `~/.local/bin/ferium` link.
- Keep executable state and the ownership manifest under
  `~/.local/opt/ride-fedora/ferium`; never install the program into the
  Minecraft instance or modpack directory.
- Resolve the runtime user explicitly. Do not silently install into root's
  home when the desired operator is a separate Minecraft service account.
- Detect an existing unowned executable, symlink, or destination and fail
  before changing it. Verify `ferium --version` and the recorded binary
  digest after installation.
- On removal, delete only the RIDE-owned link, executable, and manifest.
  Preserve `~/.config/ferium`, profiles, modpack definitions, and all selected
  instance output, including files Ferium downloaded or updated.
- Keep Ferium out of server base profiles; the opt-in profile is ready for
  the focused lifecycle test and Fedora 44 Server disposable-VM acceptance.

## Acceptance result

The focused disposable Fedora 44 Server x86_64 lifecycle passed on 2026-11-02
using the pinned image and a fresh overlay. Candidate gating, install, repeat,
status, removal, version and observed-digest checks passed; the seeded
Ferium configuration and Minecraft mod file remained unchanged. The run used
QEMU TCG because `/dev/kvm` is unavailable on this host. Its metadata,
transcript, and console logs are retained in
[`generic-server-19-ferium`](../../.acceptance-runs/generic-server-19-ferium/).
The [acceptance record](../acceptance/package.ferium-portable.md) describes
the TCG SSH polling issue found and corrected before the passing run.

The migration is operable as an opt-in candidate. Keep H096 in the v3.1 queue
for stronger publisher provenance if Ferium publishes Linux checksum or
signature evidence; continue to generic-server-20.

[Ferium v4.7.1]: https://github.com/gorilla-devs/ferium/releases/tag/v4.7.1
[`ferium-linux-nogui.zip`]: https://github.com/gorilla-devs/ferium/releases/download/v4.7.1/ferium-linux-nogui.zip
