# TMOG Linux AppImage addition

Status on 2026-11-04: **supported opt-in on Fedora 44 Workstation x86_64**.
This is a new RIDE v3 package request, not a migration of a v2 function or
server-owned source. It adds no row to the scoped v2 outcome ledger or
workstation/server burndown.

The user-visible outcome is a private, user-scoped TMOG 1.1.1 AppImage under
`~/.local/opt/ride-fedora/tmog/1.1.1/` with an extracted local desktop launcher. The official
[Linux download card](https://tmog.org/#platforms)
lists a versioned x86_64 AppImage, Linux desktop requirements, and its SHA-256.
The [release notes](https://tmog.org/release-notes.html) identify 1.1.1 as the
current Linux hotfix. The [publisher's license description](https://tmog.org/pro-info.html#commercial-product-license)
and [privacy notice](https://tmog.org/privacy.html) distinguish the free base
app from optional PRO activation. RIDE acquires the base app over HTTPS,
compares its bytes to the recorded publisher-page SHA-256, checks its ELF
header, and neither handles license keys nor touches TMOG's configuration.
The publisher page supplies a digest, but no detached signature was found in
the reviewed download path. A 2026-11-04 local download matched the published
SHA-256 and had an x86_64 ELF header; it was not executed or installed.
The disposable Workstation VM passed the lifecycle and a headless GUI startup
check under Xvfb. The user separately confirmed the GNOME launcher and icon
on the reported host; the VM did not check visible pixels.

The operation ID is `package.tmog`. Its source is
`tmog-publisher-appimage-pinned`, distribution `portable`, deployment
`user-local-opt`, format `AppImage`, scope `user`, and destination
`~/.local/opt/ride-fedora/tmog/1.1.1/TaskManagerOG-1.1.1-x86_64.AppImage`.
The fixed `tmog-appimage` handler avoids AppImageLauncher's default watched
`~/Applications` directory. Its bypass alone still left the image unable to
mount on the reported host: the journal showed SquashFS `Bad address` and FUSE
allocation errors. The AppImage runtime's built-in extraction also failed,
but Fedora's `unsquashfs` extracted the verified zstd payload successfully.
The handler requires `unsquashfs` from the separately declared
`package.squashfs-tools` operation. Apply the root-scoped
[`fedora-tmog-runtime` profile](../../profiles/fedora-tmog-runtime.json)
before the user-scoped [TMOG profile](../../profiles/fedora-tmog.json).
The handler extracts the pinned
payload at offset 944632 into `appdir`, and creates an owned desktop entry
pointing directly at `appdir/AppRun` and TMOG's bundled 256 px PNG icon.
This avoids the FUSE mount at launch,
following the [AppImage extraction fallback](https://docs.appimage.org/user-guide/troubleshooting/fuse.html).
Observation checks the retained AppImage digest, the extracted tree digest,
private ownership manifest, and desktop entry. Install refuses collisions and
symlinked parent paths. The inverse removes only these owned files and tree;
it preserves settings, traces, and any PRO entitlement. The prior
`~/Applications` deployment may require a one-time, digest-checked move if
AppImageLauncher already renamed it. Saved runs from the earlier
`user-applications-appimage` deployment retain a narrowly pinned restore
signature after that move, so they can remove the verified new deployment
without broadening recovery for other changed sources.
Saved-run recovery can remove a new installation, subject to those same
ownership checks. It cannot recover a previous AppImage version from an
external update. A later version needs an explicit catalog and migration
review, including existing installation detection.

The [acceptance record](../acceptance/package.tmog.md) records the failed first
VM run, prerequisite correction, passing candidate run, and passing supported
rerun. Neither opt-in profile changes the default Workstation profile.

Follow-up owned by the RIDE Fedora maintainer: the VM exercised `AppRun` under
Xvfb, but did not check a visible GNOME app-grid launch or run with
AppImageLauncher 2.2.0 installed. The reported host supplied separate positive
observations after a sign-out/sign-in. If launcher integration or the pinned
TMOG release changes, repeat those checks on a disposable Fedora 44 Workstation
x86_64 VM with AppImageLauncher present and record the desktop entry, icon,
daemon behavior, and whether user settings survive. Do not infer that result
from the headless VM test or extend support to another target without its own
acceptance.

Shared behavior review: canonical contract 1.1.0 at SHA-256
`b88967ea5bde29e0141bca15134e2dac63e02faf7931cb18e83ba08cf5262938`;
Windows `codex/ride-v3-migration` at
`8d073bcc536d6e0e4df6b193f2ded7396dcaf79d`, catalog SHA-256
`cfe9224f677fc10bc3eff24ffb6acd9578f851c775dbb66efc12ef7e9f7ae8be`.
Windows has the same logical `package.tmog` candidate, but its reviewed
artifact is a Windows 1.0.1 machine installer. The platform-specific
deployment and version difference is recorded in
[Windows alignment](../windows-alignment.md#tmog-linux-appimage-2026-11-04).
