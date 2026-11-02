# `package.tailscale` Fedora 44 Server acceptance

Status: **PASS — operable opt-in Fedora 44 Server x86_64 candidate**. This is
an opt-in package operation sourced from Tailscale's stable Fedora RPM
repository. The repository metadata and package signatures are enabled and
its signing key is pinned to the fingerprint
`2596A99EAAB33821893C0A79458CA832957F5868`.

The operation reproduces only the v2 `InstallTailscale` package installation.
It does not run `tailscale up`, authenticate a tailnet, configure routes or an
exit node, modify the firewall, or manage the enabled state of `tailscaled`.
Official setup documents package installation separately from service startup
and authentication. The source is the [Tailscale Linux install guide](https://tailscale.com/docs/install/linux),
the [stable Fedora repository](https://pkgs.tailscale.com/stable/fedora/tailscale.repo),
and the [publisher repository key](https://pkgs.tailscale.com/stable/fedora/repo.gpg).

## Acceptance checks

The disposable `fedora-44-server-x86_64` run passed plan and candidate gating,
publisher-key pinning and signed repository metadata, package presence,
repeat, status, restore, repository cleanup, and preservation of a seeded
`/var/lib/tailscale/tailscaled.state` file. RPM installation completed with
repository and package signature checks enforced. It also verified that RIDE
does not enable or start `tailscaled` or create a tailnet login as a side
effect.

Run metadata, transcript, serial log, and QEMU log are preserved in
`.acceptance-runs/generic-server-14-tailscale/`. The VM used the pinned Fedora
44 Server image with SHA-256
`efb75956d6dbde0801059fdac4a8a1451f06ecc843344ecdb71bb3e8d247af90` under
QEMU TCG. The transcript SHA-256 is
`ae115a0d51d3933d59b850b03c4cf4ab9eaea2a893daf590414ef74c45f043a2`.

An authenticated tailnet connection, state migration from another node, node
key expiry, subnet routes, exit nodes, firewall interaction, and service
enablement require a separate operation and deeper safety review. They remain
out of this package lifecycle and are tracked in v3.1 hardening H104.
