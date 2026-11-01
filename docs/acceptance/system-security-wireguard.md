# WireGuard package and key pair acceptance

Status: **PASS**, Fedora 44 x86_64 Workstation VM, 2026-10-31 UTC. Supported
operations: `package.wireguard-tools` and `setting.wireguard-keypair`.
The [defined batch checks](../migrations/system-security-wireguard-01.md)
passed in 412.16 seconds on the pinned image with SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
Overlay: `20261031T015521Z-test-wireguard-keypair-owned-lifecycle-aa9cd33e`.
Catalog SHA-256: `772bc260689e93cfc55ed8044ecc430510517415e32714e31cda77241c96159b`.

The profile first refused an existing legacy `privatekey` before package
installation and left its contents unchanged. With that test fixture
removed, it installed the Fedora-signed `wireguard-tools` RPM and generated
a key pair. The `wg pubkey` output matched the stored public key; private and
public files had mode 0600. Repeat apply reported both operations unchanged.
Restore removed only the RIDE-created files and marker, and explicit profile
removal removed the package and pair. The seeded NetworkManager connection
file checksum, connection UUIDs, and service state stayed unchanged.

The v2 remover recursively deleted `/etc/wireguard`. The v3 inverse removes
only the two validated, unchanged RIDE-owned key files and ownership marker;
it refuses pre-existing files, symlinks, altered files, and unrelated
configuration. A local setting operation journals only state names, not key
material. Focused mocked tests also covered generation failure cleanup,
tampering, and path conflicts. Existing DNF handler failure evidence is
reused.

This acceptance covers local package installation and key-pair generation
only. It does not create or activate an interface, add a peer, import a
credential, change routes, or rotate keys. H032 tracks those behaviors.
