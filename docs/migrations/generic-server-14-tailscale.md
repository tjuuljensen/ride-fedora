# Generic Server 14: Tailscale package

Status: **complete as an operable opt-in Fedora 44 Server candidate**.

## Completion criteria

- Replace the v2 remote `curl | sh` path with the official stable Fedora RPM
  repository, verify the repository key fingerprint, and require signed
  repository metadata and RPM signatures.
- Keep this outcome scoped to package presence and the exact RIDE-owned repo
  file. Do not authenticate a tailnet, migrate node keys, select routes or an
  exit node, change firewalld, or enable `tailscaled` through this operation.
- On a disposable Fedora 44 Server VM, verify plan, candidate gate, apply,
  package and signature state, repeat, status, restore, service state, repo
  cleanup, and preservation of a seeded `/var/lib/tailscale` state file.
- Keep any service enablement, tailnet identity/authentication, route policy,
  firewall behavior, and recovery of a real node identity outside this batch.

## Upstream and source path

Tailscale's Linux installation guide directs Fedora users to its stable
Fedora package repository. The RIDE operation downloads the Tailscale signing
key over HTTPS, checks its full fingerprint
`2596A99EAAB33821893C0A79458CA832957F5868`, and writes a dedicated repository
file with both `gpgcheck=1` and `repo_gpgcheck=1`. The product source is
[Tailscale's Fedora stable repo](https://pkgs.tailscale.com/stable/fedora/tailscale.repo),
documented by the [Linux install guide](https://tailscale.com/docs/install/linux).
The client source is [BSD-3-Clause](https://github.com/tailscale/tailscale/blob/main/LICENSE).

The v2 source only invokes the installer script and does not call `tailscale
up`. RIDE therefore keeps registration and private node state outside package
management. Package removal must preserve any daemon state directory and must
not de-register or recreate the host's tailnet identity.

## Status and evidence

The package operation is `package.tailscale` in
[`fedora-server-tailscale`](../../profiles/fedora-server-tailscale.json).
The shared `publisher-repo-rpm` handler pins the publisher key and owns the
repo file. [`package.tailscale` acceptance](../acceptance/package.tailscale.md)
and its VM test record the exact Fedora Server result. The disposable VM passed
plan/gating, apply, repeat, status, restore, repo cleanup, and exact seeded state
preservation. The transcript SHA-256 is `ae115a0d51d3933d59b850b03c4cf4ab9eaea2a893daf590414ef74c45f043a2`. H104 tracks service and
tailnet state lifecycle before RIDE offers authentication or startup behavior.

Windows has no matching Tailscale package operation or Fedora repository
contract; Linux adds no shared schema or run-state fields. This is recorded in
[Windows alignment](../windows-alignment.md).
