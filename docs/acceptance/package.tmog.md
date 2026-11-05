# TMOG AppImage acceptance

`package.tmog` is **VM PASS; supported** as an opt-in package on Fedora 44
Workstation x86_64, 2026-11-04. Risk tier: third-party desktop AppImage with
user-scoped files and a separate Fedora RPM prerequisite. It places the
publisher's TMOG 1.1.1 AppImage under the intended
user's `~/.local/opt/ride-fedora/tmog/1.1.1/` directory, outside the default
AppImageLauncher watch directory. RIDE uses `unsquashfs` to extract the
verified payload into `appdir` and owns a desktop entry that launches
`appdir/AppRun` without a FUSE mount and uses the bundled 256 px PNG icon,
plus a private ownership manifest.
The publisher's download card displayed SHA-256
`12a1f2ed60c28b0749a13eeaec4696f241a425fb6715d9e7747807ce62d3b139`
for `TaskManagerOG-1.1.1-x86_64.AppImage` on 2026-11-04. RIDE checks that
digest and ELF format before installing. A separate checksum-only download
of the publisher artifact on 2026-11-04 matched the displayed SHA-256 and
identified as an x86_64 ELF file (39,733,752 bytes). That copy was not
executed or installed. The
digest match confirms byte identity with the publisher's page, not a
detached publisher signature.

The first disposable KVM run on the pinned Fedora 44 Workstation x86_64 image
**failed** because that image lacked `unsquashfs`; TMOG apply reported
`required command is unavailable: unsquashfs`. Its overlay was
`20261104T120659Z-test-tmog-appimage-lifecycle-preserves-user-data-05d9d8f3`
and JUnit record is `.acceptance-runs/tmog-vm-20261104.xml`. The correction
declares `package.squashfs-tools` as a dependency and adds a separate
root-scoped [runtime profile](../../profiles/fedora-tmog-runtime.json).

The corrected candidate run **PASSed** on a fresh KVM overlay
`20261104T121044Z-test-tmog-appimage-lifecycle-preserves-user-data-eac3fe63`
of image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
Candidate catalog SHA-256:
`58f1460c25a8e9616fffa86a0423a6fdb45a1a7e6e8cc1b9002ef46489df8475`;
source revision `7659f9c9f7fbf2ddb3e6fd00eece2ad0171dd43d` with uncommitted
changes. Retained transcript:
`.acceptance-runs/tmog-vm-20261104-r2/fedora-44-workstation-x86_64/20261104T121044Z-test-tmog-appimage-lifecycle-preserves-user-data-eac3fe63/transcript.jsonl`
(SHA-256 `5e2ad39385b1e56e402344a85b8dde8862a4dbd75c3f804b60d32a316187f649`);
JUnit `.acceptance-runs/tmog-vm-20261104-r2.xml` (one test passed).
The test checked candidate gating, RPM install and verification, TMOG plan,
apply, publisher SHA-256, owned desktop and bundled icon paths, installed
status, unchanged repeat, saved-run restore, explicit reinstall/remove,
modified AppImage refusal, and preservation of synthetic settings and
`license.json`. `AppRun` remained alive for 15 seconds under Xvfb and was
terminated by the test timeout, establishing a headless GUI startup check.
Focused mocked tests cover extraction failure, digest failure, unowned-file
collision, modified desktop entry, modified extracted payload, and the legacy
run signature.

The final supported-state test **PASSed** on fresh KVM overlay
`20261104T121653Z-test-tmog-appimage-lifecycle-preserves-user-data-98311942`
with the same pinned image. Supported catalog SHA-256:
`b9fda71c83860700feaf2de78ba579ea8a4f07e929d85674bb38506eecb837f1`;
test source SHA-256:
`b12f246963af4b9ca5daecb0976327d5ae6e2763a04cb708bec56d62704acc69`.
Retained transcript:
`.acceptance-runs/tmog-vm-20261104-supported/fedora-44-workstation-x86_64/20261104T121653Z-test-tmog-appimage-lifecycle-preserves-user-data-98311942/transcript.jsonl`
(SHA-256 `f1bf2d6df8a286ef8310bdeac074ac81bac0b1e4769a4b2299b133b12592ce03`);
JUnit `.acceptance-runs/tmog-vm-20261104-supported.xml` (one test passed in
74.22 seconds). It repeated the TMOG checks without candidate flags and
additionally checked the Fedora prerequisite's plan, status, and unchanged
repeat. The source revision remained
`7659f9c9f7fbf2ddb3e6fd00eece2ad0171dd43d` with uncommitted changes.

The test did not verify pixels in a visible GNOME session or install
AppImageLauncher 2.2.0 in the VM. The user separately confirmed the launcher
and bundled icon on the reported Fedora 44 Workstation host with
AppImageLauncher 2.2.0 installed after signing out and back in. That host
observation is supplementary, not VM evidence. Do not enter a real key or run
TMOG as root. Optional PRO activation and screensaver selection are outside
this package operation. Reviewer: Codex, 2026-11-04. Support is limited to
the pinned Fedora 44 Workstation x86_64 target.

On the reported Fedora 44 Workstation host, AppImageLauncher 2.2.0 moved the
original `~/Applications` deployment and failed to register it. Its logs
reported `sqfs_open_image error`; the verified TMOG image uses zstd SquashFS.
The first source correction moved the verified artifact to the user-local
path and bypassed AppImageLauncher. RIDE then reported `installed`, but the
user's subsequent desktop launch silently exited. The journal showed FUSE
`memory allocation failed`, SquashFS `Bad address`, and `Cannot mount
AppImage`. The built-in `--appimage-extract` also failed; Fedora's
`unsquashfs` successfully extracted the same pinned image at offset 944632.
The revised handler launches the extracted `AppRun` directly. The user
confirmed that a direct `AppRun` launch opened TMOG on this host. GNOME's
search result also opened it, but clicking the existing app-grid tile still
launched the old AppImage command according to the user journal. Even an
atomic desktop-file replacement did not refresh that tile in the current
Wayland session. The user confirmed that the app-grid tile launches TMOG
after signing out and back in. The earlier generic icon showed as missing;
the desktop entry now points to the bundled icon. The user confirmed that
the launcher and icon work on this host.
After promotion, a read-only restore dry run of the host's earlier TMOG run
completed successfully. No host restore was applied; the disposable VM and
mocked tests provide the state-changing recovery evidence above.
