# WireGuard tools and key pair

Status: **package and key-pair acceptance passed**, 2026-10-31 UTC.
The owner kept the v2 `Wireguard` outcome for v3.0. `InstallWireguard`
installs `wireguard-tools` and, only when both top-level key files are
absent, runs `wg genkey` and `wg pubkey` under `/etc/wireguard`.
`RemoveWireguard` removes the RPM and recursively deletes that directory,
including unowned keys and configuration. The v3 replacement must retain
tool installation and key generation without inheriting that broad inverse.

Fedora 44 x86_64 packages
[wireguard-tools](https://packages.fedoraproject.org/pkgs/wireguard-tools/wireguard-tools/)
as a signed RPM under GPL-2.0-only. The
[WireGuard quick start](https://www.wireguard.com/quickstart/) documents
`wg genkey` and `wg pubkey` with a private umask. NetworkManager has
[native WireGuard support](https://networkmanager.dev/docs/vpn/), so no
third-party NetworkManager plugin is required. Fedora 44 x86_64 Workstation
is the only proposed v3.0 target. The upstream and Fedora sources, license,
and signature check must be confirmed in the VM record.

## Completion checks

- Add `package.wireguard-tools` through the existing signed DNF handler.
  Add a separate opt-in key-pair operation that depends on the package.
  Keep both out of `default`. The package operation may be run independently;
  the key-pair operation must never modify an existing unowned key or
  configuration. No profile may activate an interface or create a peer.
- The key-pair handler must generate a valid pair without printing or
  journaling the private key. Restrict private material to root with mode
  0600. Record ownership of exactly the new files. Repeat must be unchanged.
  If either top-level key exists, the path is a symlink, a file changes after
  creation, or an unrelated configuration is present, fail closed and leave
  it intact. Restore and explicit remove may delete only the exact
  unchanged RIDE-created key files and marker; never recursively remove
  `/etc/wireguard`.
- Focused mocked tests must cover generation, repeat, partial failure,
  tampering, existing keys, symlinks, and exact recovery. On a disposable
  pinned Fedora 44 Workstation VM, verify signed RPM plan/apply/repeat/status,
  key pair validity and permissions, restore/remove, and preservation of
  seeded unrelated keys, NetworkManager connection UUIDs, service state,
  and configuration. Use a separate test overlay for a seeded pre-existing
  key conflict. Reuse the unchanged DNF handler's failure evidence.
- Count the full v2 source outcome operable only when both the package and
  safe key generation pass the declared VM checks. The package may be
  accepted separately if the key handler is still being developed, but that
  does not close this source outcome. Keep live interface, routing, peer,
  credential-import, and key rotation behavior in a named v3.1 review.
- Update catalog, generated docs, ledger, progress, Windows alignment, and
  a named v3.1 follow-up only after the evidence supports them. Check
  source-signature and journal behavior before promotion.

## Result

The [Fedora 44 Workstation acceptance](../acceptance/system-security-wireguard.md)
passed the package, key-pair, exact recovery, and seeded-state checks. The
tools RPM and local key-pair operation are supported only on Fedora 44 x86_64
Workstation and remain in an opt-in profile. H032 tracks interface, peer,
route, and rotation behavior.
