# NetworkMiner publisher archive and evidence-data ownership

Status: **implemented as an opt-in candidate; Fedora 44 Workstation acceptance remains** (2026-11-02).
The owner kept the active v2 `InstallNetworkMiner`/`RemoveNetworkMiner`
capability for v3.0. The old installer downloads a mutable ZIP, installs the
Mono development bundle, extracts into `/opt/NetworkMiner`, changes
`AssembledFiles` and `Captures` to group/world writable, and writes a system
launcher. Its inverse deletes that whole tree and removes Mono even when other
software uses it.

## Completion checks defined before implementation

- Reuse the Windows-verified, version-specific free-edition archive only when
  the downloaded SHA-256 matches. Preserve all 52 archive entries, including
  the bundled fingerprint notice. The archive itself is publisher-hosted but
  does not carry a detached signature; record HTTPS acquisition plus pinned
  digest as the verified provenance.
- Install the program and launcher within one user's owned paths. Use signed
  Fedora Mono and GTK packages; removing NetworkMiner must not remove runtime
  packages or touch user output directories.
- Keep the vendor's capture and assembled-file data outside the owned program
  payload. Use user-only permissions. Package apply must not open PCAP files,
  start capture, or grant capture-device/firewall access.
- Mock archive digest, member path, conflict, repeat, external modification,
  partial extraction, and exact program-file removal cases. Seed the output
  directories and prove byte-identical preservation on removal and restore.
- On disposable Fedora 44 Workstation x86_64, verify signed runtime packages,
  plan/apply/repeat/status/restore, one GUI startup smoke under a virtual
  display, and exact preservation of seeded and generated output. Keep the
  operation as an explicit opt-in candidate; broader PCAP, capture, hostile
  input, and output-data behavior remain outside package acceptance and in
  H110.

## Source and assessment

Netresec's [Linux guide](https://www.netresec.com/?month=2025-04&page=Blog&post=How-to-Install-NetworkMiner-in-Linux)
specifies Mono, GTK2, and a versioned `NetworkMiner_3-2.zip`. Its
[release notice](https://www.netresec.com/?month=2026-10&page=Blog&post=NetworkMiner-3-2-Released)
announces NetworkMiner 3.2. The [source/license page](https://www.netresec.com/?page=NetworkMinerSourceCode)
states GPLv2. Fedora 44 publishes signed [`mono-core`](https://packages.fedoraproject.org/pkgs/mono/mono-core/)
and [`gtk2`](https://packages.fedoraproject.org/pkgs/gtk2/gtk2/) RPMs; final
GUI/runtime requirements remain subject to Workstation acceptance.

On 2026-11-02, direct HTTPS retrieval from Netresec's static 3.2 URL produced
SHA-256 `daceec649fb4fe59b11e4a9e4ecd5f51c1dd37824280dfbeac67bec27b6b6d60`.
That digest matches Windows `codex/ride-v3-migration` revision
`69ccbb08570205407f5fae13329b8eac6b1abcd8` and its recorded official-page
hash. The archive has 52 entries under one `NetworkMiner_3-2/` root; a local
path and symlink scan found no absolute, parent-traversal, or symlink members.
It includes `NetworkMiner.exe`, `PacketParser.dll`, and
`Fingerprints/mac-ages_LICENSE`. The hash and archive inventory can be reused;
Windows acceptance does not prove Linux Mono/GTK compatibility or Linux data
recovery.

The Linux catalog now provides candidate operations for `package.networkminer`
and its signed Fedora `gtk2`, `mono-core`, and `mono-winforms` runtime packages.
Apply [the runtime profile](../../profiles/forensic-networkminer-runtime.json)
with system privileges first, then apply the separate
[user application profile](../../profiles/forensic-networkminer.json) as the
target user. Removing NetworkMiner removes only its verified program payload,
owned launcher, and owned desktop entry; it preserves the runtime RPMs and
`~/.local/share/networkminer` output data. The helper rejects unsafe ZIP paths,
links, special files, oversized members, digest mismatch, and modified payloads.

Focused tests are in [test_v3_networkminer.py](../../tests/test_v3_networkminer.py)
and the disposable-VM scenario is
[test_networkminer.py](../../tests/acceptance/test_networkminer.py). The latter
still needs to pass on Fedora 44 Workstation x86_64 before the ledger can count
the operation as operable. Compare against the Windows portable operation in
[Windows alignment](../windows-alignment.md).
