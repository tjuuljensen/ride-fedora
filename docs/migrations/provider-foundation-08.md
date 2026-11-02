# Provider foundation batch 08: Eza installed and portable deployments

Status: **Fedora RPM supported; portable release operable as an opt-in candidate**, 2026-11-01. The owner kept
both v2 acquisition paths. The library-only `InstallEza` path is the accepted
Fedora RPM recorded in [`package.eza` acceptance](../acceptance/package.eza.md).
The active `InstallEzaGitHub` path is a separate user-local deployment and is
not covered by the RPM result.

The upstream [installation guide](https://github.com/eza-community/eza/blob/main/INSTALL.md)
documents the x86_64 GNU release archive and Fedora's repository package. The
[0.23.5 release](https://github.com/eza-community/eza/releases/tag/v0.23.5)
publishes the x86_64 GNU tarball with SHA-256
`35c70c5c43c29108075e58b893234c67ef585f0b53a7eaf8e9e7d4eec9f339b4`.
The release tag is shown as signed on GitHub, but the signing key is expired;
v3 therefore verifies the exact publisher release archive against its pinned
digest and does not claim a currently valid signature. The upstream Cargo
manifest declares EUPL-1.2, and the matching version's
[`LICENSE.txt`](https://raw.githubusercontent.com/eza-community/eza/v0.23.5/LICENSE.txt)
is recorded in catalog and deployment metadata.

## Completion checks defined before implementation

- Preserve the two v2 acquisition intents as separate operations:
  `package.eza` uses Fedora RPM; `package.eza-portable` uses the exact pinned
  upstream archive in a user-local deployment. Both remain opt-in.
- Keep portable files under
  `~/.local/opt/ride-fedora/eza/0.23.5`, expose the binary through
  `~/.local/bin/eza`, and record an owned manifest. Coexist with the Fedora
  RPM at `/usr/bin/eza`; never overwrite a pre-existing user-local command.
- Verify the archive SHA-256 before extracting. Inspect tar members without
  extracting paths, accept exactly one regular `eza` binary, probe its version,
  and preserve unrelated files in RIDE's owned-tools directory.
- Mock tests cover install, repeat, remove, digest/download failure, unsafe or
  incomplete archives, destination collision, modified owned state, and
  preservation of sibling user data.
- On a disposable Fedora 44 Workstation x86_64 VM, run candidate refusal,
  plan, install alongside the Fedora RPM, version and status checks, repeat,
  remove, RPM-preservation checks, and user-data recovery. Do not run Eza on
  user data during acceptance.
- Compare the Linux catalog/profile/run contract with Windows alignment and
  document intentional differences. Keep the portable deployment out of base
  profiles.

## Implementation and acceptance record

`package.eza-portable` uses a pinned x86_64 GNU release, a separate
`user-local-bin` deployment identity, and an ownership manifest. The opt-in
[`fedora-eza-portable` profile](../../profiles/fedora-eza-portable.json) may
coexist with `package.eza`. Focused mock tests passed download/digest failure,
invalid archive, collision, modified-state, install, repeat, and inverse
checks. On Fedora 44 Workstation x86_64, the pinned binary installed and
reported version 0.23.5 while the Fedora RPM remained installed; repeat was
unchanged, and portable removal preserved the RPM and sibling user data. The
test invoked only `eza --version`. Transcript, image digest, catalog digest,
and run IDs are recorded in [`package.eza-portable` acceptance](../acceptance/package.eza-portable.md).
H068 tracks refresh and additional-architecture review.
