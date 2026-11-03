# Forensic Isolated 07: VMFS6 image reader

Status: **opt-in install candidate available; VMFS6 access unverified; fixture test deferred to v3.1**,
2026-11-03. `InstallVMFStools` in `lib-fedora.sh` only printed two URLs;
`RemoveVMFStools` did nothing. The owner kept VMFS access for v3.0, while
the link-only v2 function remains a retired placeholder. This follow-up
seeks a working, opt-in VMFS6 *image inspection* path on Fedora 44
Workstation x86_64. VMFS5, live datastores, multi-extent devices, FUSE
mounts, and writing are separate claims.

## Completion checks defined before implementation

- Pin the exact upstream source commit and observed archive digest. Keep its
  GPL notice and source attribution. Compare the upstream VMFS6 capability
  with the separately packaged VMFS5 reader; do not claim one covers both.
  Confirm the current Fedora 44 build dependencies and record the source's
  archived maintenance state.
- Build only `debugvmfs6` without `VMFS_WRITE` in a dedicated RIDE-owned
  destination. Its opened VMFS input must be read-only in source and in a
  disposable VM trace. Give the RIDE launcher only `show`, `ls`, and `cat`
  on a user-supplied regular image file; reject block devices and symlinks.
  Never discover or open host block devices automatically.
  Detection must identify the exact owned build. Restore and remove must
  refuse unowned or modified paths and preserve unrelated images and files.
- Before runnable status, use a disposable Fedora 44 Workstation x86_64 VM
  to inspect a verified VMFS6 image fixture, check the input digest before
  and after, and prove that the process opens the image read-only. Exercise
  plan, opt-in gate, apply, repeat, status, restore, and explicit removal.
  Focused mocks must cover wrong source digest, occupied destination,
  failed build cleanup, and unowned removal. Investigate failures before
  retrying. A build or `--help` check alone cannot establish VMFS access.
- Keep the operation out of `default`. The owner cannot supply the fixture now
  and explicitly deferred this fixture-backed runtime test to v3.1. Keep VMFS6
  non-runnable and out of v3.0 profiles; this deferral does not authorize the
  pinned reader as a candidate operation. Resume with the fixture and checks
  above before claiming access.

The [upstream VMFS6 fork](https://github.com/teward/vmfs6-tools) is archived
and its [0.2.1 release](https://github.com/teward/vmfs6-tools/releases/tag/0.2.1)
is source-only. Tag `0.2.1` resolves to commit
`582b5252d74ff96102220af62202a3548fe7128f`; its codeload archive
SHA-256 was observed as
`a022a75f6c31611d1142c9d3692f2180b22d76a9d786809a5719e74f2e965c0a`.
The archive has 69 entries under one root and no traversal paths, links,
or devices. Its [GPL-2.0 license](https://github.com/teward/vmfs6-tools/blob/0.2.1/LICENSE)
and [README](https://github.com/teward/vmfs6-tools/blob/0.2.1/README)
describe VMFS6 support as work in progress and distinct from VMFS5.
[Debian's VMFS6 package](https://packages.debian.org/trixie/vmfs6-tools)
documents read access. The upstream debugger contains write commands, but
[`debugvmfs6.c`](https://github.com/teward/vmfs6-tools/blob/0.2.1/debugvmfs6/debugvmfs6.c)
sets `flags.read_write = 1` only when `VMFS_WRITE` is defined. The pinned
build files do not define it. The source's `libvmfs/vmfs_volume.c` selects
`O_RDONLY` when that flag is false and rejects read/write access for VMFS6.
The proposed RIDE entry point still needs to allow only image-file read
commands and a VM trace plus fixture read before an operational claim.

## Fedora 44 feasibility probe

On the pinned Fedora 44 Workstation x86_64 disposable VM under QEMU TCG,
the exact archive passed its SHA-256 check and built `debugvmfs6` and
`imager` with Fedora `gcc`, `make`, and `libuuid-devel`. The build did not
define `VMFS_WRITE`. Installing those build prerequisites introduced seven
RPM names and upgraded 16 pre-existing names, including util-linux
components; a managed build-prerequisite profile needs its own lifecycle
review. The retained local probe transcript is
`.acceptance-runs/vmfs-probe/transcript.jsonl`, with image and source
metadata in `.acceptance-runs/vmfs-probe/metadata.json`.

The bundled `test.img` passed the upstream imager checksum and expanded
to a sparse 1,258,435,584-byte file with SHA-256
`0beaea7f5d54655478fefb0f1b18ce824da70a5c2ce357e36e8a163ea9ab07bb`.
The reader identified it as **VMFS3** and rejected it as unsupported.
That failure was investigated; rerunning it cannot prove VMFS6 access.
No genuine VMFS6 fixture with a usable license and expected contents was
found in the reviewed upstream or Debian source packages. The operation
therefore remains non-runnable and the kept capability remains a v3.0 gap.
The next test needs a genuine VMFS6 image, an independently recorded digest,
expected directory/file contents, an `O_RDONLY` trace, and unchanged input
digest. VMFS5 needs its own source and fixture if required.

## Fixture acquisition investigation, 2026-11-03

The original [Weafon VMFS6 fork](https://github.com/weafon/vmfs6-tool) remains
marked experimental in its README; it says only `debugvmfs` and `vmfsfuse`
were applied to a few cases. The later [teward fork](https://github.com/teward/vmfs6-tools)
is archived and carries the same experimental limitation. This review found
no maintained Linux reader with stronger VMFS6 validation evidence.

The archived upstream [TODO](https://github.com/teward/vmfs6-tools/blob/0.2.1/TODO)
lists `mkfs.vmfs` only as expected for v0.5.0 and full write support for
v1.0.0. Neither exists in the pinned v0.2.1 source. The bundled `imager`
regenerates the existing VMFS3 fixture, so it cannot produce the required
VMFS6 image. Debian carries the same source fixture.

Broadcom [KB 316475](https://knowledge.broadcom.com/external/article/316475/migrating-vmfs-5-datastore-to-vmfs-6-dat.html)'s
attachment is a VMFS5-to-VMFS6 migration PowerShell script, not a datastore
image. Broadcom [KB 399823](https://knowledge.broadcom.com/external/article/399823)
documents a free ESXi 8.0U3e hypervisor download through its support portal,
subject to sign-in and non-production license terms. This is a plausible
legitimate fixture path: create a disposable VMFS6 datastore on a virtual
disk using ESXi, seed known files, then export the virtual disk as a
read-only test fixture. No portal download or fixture is present in this
workspace, so this is an acquisition path, not evidence of VMFS6 access. The
batch remains blocked on an owner-authorized ESXi installer or licensed
fixture and its expected file manifest.

## Current reader maintenance status, 2026-11-03

The `teward/vmfs6-tools` GitHub repository is archived and read-only as of
2025-11-16. Its maintainer's [Debian removal request](https://bugs.debian.org/1120780)
states that both `vmfs-tools` and the VMFS6 fork are unmaintained and fail to
build with FUSE 3; Debian removed `vmfs6-tools` from unstable on 2025-11-23.
The older stable Debian package entry does not change that upstream status.
The base [`vmfs-tools` project](https://glandium.org/projects/vmfs-tools/)
still describes itself as work in progress and not intended for production;
it is the VMFS5 path and does not replace VMFS6 support. This review found no
maintained Linux reader with stronger VMFS6 validation evidence.

This closes the source-maintenance question for the old reader, not the kept
VMFS access outcome. The archived fork remains useful only as a pinned,
isolated candidate pending a genuine licensed VMFS6 fixture, known manifest,
and read-only Fedora 44 trace; it cannot yet be advertised as an operable
v3.0 capability. A remote ESXi/vSphere datastore workflow would be a separate
access method and has not been accepted as a replacement for inspecting a
VMFS image on Fedora.

## General image-mounting alternative review, 2026-11-03

The newer [MountIR](https://github.com/m1tcch/MountIR) utility was reviewed as
a possible replacement path. Its current driver table maps VMFS6 to
`vmfs6-fuse` from `vmfs6-tools`; it does not provide an independent VMFS6
reader. Its general image workflow also uses privileged loop-device and mount
operations across many filesystem types, which exceeds the narrow image-file
`show`/`ls`/`cat` interface defined for this RIDE outcome. It is therefore not
a migration alternative for the current batch. This review does not establish
MountIR's Fedora 44 support or runtime behavior.

## v3.1 fixture acceptance deferral

The owner cannot supply a genuine VMFS6 image now and asked to defer the
fixture-backed runtime test to v3.1. RIDE offers `package.vmfs6-reader` as an
explicit install candidate so the owner can use the pinned CLI for manual
testing. That install path does not claim that VMFS6 images are correctly read.
The v3.1 test must use an authorized fixture with a known manifest, verify
`O_RDONLY` access and an unchanged input digest, and complete the RIDE install
and removal checks above. VMFS5 remains a separate review.
