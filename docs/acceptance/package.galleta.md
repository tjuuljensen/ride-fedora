# Galleta legacy cookie parser acceptance

`package.galleta` is an opt-in Fedora 44 Workstation x86_64 user-local CLI.
It downloads Debian's pinned x86_64 package, verifies its SHA-256, extracts
only `/usr/bin/galleta` and the packaged copyright notice, and installs them
under the invoking user's `~/.local` paths. It does not invoke `dpkg`, change
system packages, or open/process cookie evidence. Removal refuses modified or
unowned paths. The input parser is legacy code from 2003-2004; use only on a
copy of evidence and retain the original file.

The Debian package page records SHA-256
`1bb1867237e07c403c9f79abad71b6838645f4494a5ea1a4077821f610b401ff` for
`galleta_1.0+20040505-12_amd64.deb`. The Debian source license record declares
the upstream parser BSD-3-Clause. Fedora 44 x86_64 lifecycle acceptance covers
hash verification, candidate gating, apply, repeat, status, dynamic library
resolution, and exact remove. It does not yet establish parser accuracy on a
known standalone IE cookie fixture; H099 tracks that evidence and format
limitations.

Source: [Debian package details](https://packages.debian.org/trixie/amd64/galleta/download),
[Debian source and copyright](https://sources.debian.org/src/galleta/1.0%2B20040505-12/debian/copyright/).

Disposable VM run: PASS (Fedora 44 Workstation x86_64, QEMU TCG, pinned image
SHA-256 `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`).
The test ran as the intended non-root user and verified candidate gating,
install, repeat, status, runtime library resolution, remove, and absence of the
RIDE-owned executable and manifest. The fixture-level parser review remains
queued under H099.

- Transcript: [`transcript.jsonl`](../../.acceptance-runs/resolution-review-01-galleta/transcript.jsonl)
- Transcript SHA-256: `a089c45747363a259ac0b64d4a851a2e7c8b45e943ddfebd80d3790634037785`
