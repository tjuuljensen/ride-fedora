# Forensic Isolated 07: VMFS6 image reader

Status: **source and safety investigation; no runnable v3 operation yet**,
2026-10-30. `InstallVMFStools` in `lib-fedora.sh` only printed two URLs;
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
- Keep the operation out of `default`. If the fixture or read-only evidence
  cannot be established, retain the v3.0 gap with a specific blocker and
  next action. Update the ledger, generated docs, Windows alignment, and
  named v3.1 hardening only after the evidence supports a runnable claim.

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
