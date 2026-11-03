# BulkExtractor Fedora 44 Workstation acceptance

`package.bulk-extractor` is an opt-in candidate for Fedora 44 Workstation
x86_64. It installs the upstream 2.2.0 x86_64 Snap from the GitHub release
asset after matching the catalog's pinned SHA-256. The Snap is strict
confinement; the package carries `home`, `removable-media`, and
`block-devices` plugs. RIDE manages package presence only and does not open
evidence, connect raw-device plugs, or configure scan inputs. Apply the separate
`snap-runtime` profile first.
The Snap artifact's strict mode is not a claim of full host enforcement:
Fedora's Snap runtime reports partial host confinement; see
[`package.snapd.md`](package.snapd.md). Do not use this v3.0 operation as a
security boundary for untrusted evidence.

The operation recognizes only installed version 2.2.0. It refuses a different
pre-existing version, does not reinstall an exact pre-existing copy, and uses
the non-purge removal path so Snap creates its automatic data snapshot.
Safety review checks: `private-output-boundary` (Snap application data remains
inside Snap-owned state), `no-evidence-processing` (the v3.0 operation only
checks help output and never opens an evidence input), and
`exact-output-preservation` (the synthetic external case sentinel retains its
hash through removal and recovery).

## Focused validation

The mocked lifecycle covers absent/install/repeat/status/remove, wrong
pre-existing version refusal, download failure, SHA-256 mismatch, catalog
validation, and use of a local `--dangerous` artifact after digest verification.
No test opens forensic evidence.

## Disposable Fedora 44 Workstation x86_64 acceptance

The pinned asset's SHA-256 was verified and its embedded `meta/snap.yaml` was
inspected with `unsquashfs`; it declares `confinement: strict` and a
`block-devices` plug. The VM test in
`tests/acceptance/test_bulk_extractor_snap.py` checks candidate gating, install
and version, disconnected `block-devices`, help output only, Snap's automatic
snapshot, RIDE removal and reinstall, restoration of a seeded Snap data
sentinel, and preservation of an external case-data sentinel. It does not
process disk images or PCAP files.

The acceptance scenario passed on 2026-11-02 in a disposable Fedora 44
Workstation x86_64 VM using KVM and image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
Installed version was 2.2.0; the Snap plug table showed `block-devices` with
no connected slot. Snap printed its full 2.2.0 help text and returned 1, which
the test records as the CLI's help behavior rather than an install failure.
Automatic snapshot set `1` was created on removal and restored after reinstall.
The seeded Snap common-data sentinel returned, and the external case sentinel
kept SHA-256
`1ee3df05bb506e9461e8a1a7ccce508e4abbec9ead7a1eba6d7b87982e76f190`.

Evidence directory:
`.acceptance-runs/bulk-extractor/fedora-44-workstation-x86_64/20261102T161503Z-test-bulk-extractor-pinned-snap-lifecycle-and-snapshot-recovery-c319f60b/`.
Transcript SHA-256:
`9125b5be9c66f63d5ba1927cab711e267c8842f97578c1fd17e009a6d3e9b709`;
VM metadata SHA-256:
`19691412bc8ee009343b4761e33287e0fb27490843d11d3f1e453a3341da95c5`;
overlay SHA-256:
`ebc8bd56377a59481a7d917e312175586c22079ca1e30fcbc91b6cf561c15bcf`.
The first probe incorrectly expected confinement in `snap info --verbose`, and
the installed local Snap did not expose the expected `/snap/.../meta` path.
Inspection of the exact digest-pinned archive established its confinement
metadata; the VM then checked the live interface connection state.

H113 tracks scan behavior, plug review, hostile input, output limits, and
broader evidence recovery separately.

Sources: [upstream v2.2.0 release](https://github.com/simsong/bulk_extractor/releases/tag/v2.2.0),
[installation guide](https://github.com/simsong/bulk_extractor/blob/main/INSTALL),
[license statement](https://github.com/simsong/bulk_extractor/blob/main/COPYING).
