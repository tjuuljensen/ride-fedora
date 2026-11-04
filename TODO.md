# RIDE v3 release TODO

Status: **v3.0 is not ready for a release tag**. Use the
[release review](docs/release-v3.0-review.md) and
[generated migration progress](docs/migrations/progress.md) as the detailed
sources of truth. This file is a short release checklist.

## Before v3.0

- [ ] Resolve or explicitly defer the VMFS6 reader gap. Obtain an authorized
  fixture and verify read-only access and an unchanged image digest, or keep
  the capability non-runnable. See the [acceptance record](docs/acceptance/package.vmfs6-reader.md).
- [ ] Resolve or explicitly defer Workstation ExpressVPN scheduled rotation.
  Verify current client behavior and network recovery in a disposable VM, or
  keep the unattended timer out of v3.0.
- [ ] Reconcile Server VPN randomizer ownership with `network-devices`:
  identify consumers, runtime identity, crontab owner, publication path, and
  rollback before testing timer and VPN recovery in a disposable Server VM.
- [ ] Close ALIGN-03 through ALIGN-09, or record owner-approved deferrals with
  reasons, evidence, and review triggers in the
  [alignment register](docs/windows-alignment.md).
- [ ] Record scope decisions for the seven supplementary helper-library
  groups in the [legacy source audit](docs/legacy-source-audit.md). Classify
  them as reference-only, standalone, or later migrations; do not port them
  one-for-one by default.
- [ ] Regenerate migration and CLI references, run the required local checks
  and CI, and recheck acceptance on the exact Fedora 44 targets in the final
  release source.
- [ ] Update bootstrap and release metadata, publish the immutable shared
  behavior-contract reference, then create the v3.0 tag.

## Later feature review, outside v3.0

- [ ] Assess Dash to Dock as an optional, user-scoped GNOME extension. Check
  compatibility on the exact Fedora GNOME Shell version, extension conflicts,
  session restart behavior, and removal recovery before adding a profile.
  [Current extension listing](https://extensions.gnome.org/extension/307/dash-to-dock/)
  lists active builds for Shell versions 45 through 51.
- [ ] Revisit GNOME app-folder management through current user GSettings and
  define merge and restore behavior. Replace the old `gnome-dash-fix` and
  legacy GNOME documentation links with current API documentation; do not
  port the old script or extension-manager instructions.
  [GNOME settings guide](https://teams.pages.gitlab.gnome.org/Websites/help.gnome.org/system-admin-guide/gsettings-browse.html)
- [ ] Consider an optional font installation feature only for a defined font
  set and user/system scope. Review font licenses, trusted sources, cache
  refresh, and safe removal. [Fedora font guide](https://docs.fedoraproject.org/en-US/quick-docs/fonts/)
- [ ] Consider `editor.selectionClipboard: false` as an optional per-user
  VS Code preference. Preserve unrelated `settings.json` content and verify
  exact restore. [VS Code setting context](https://code.visualstudio.com/updates/v1_102)
- [ ] If screen recording is still wanted, choose a maintained Fedora package
  before scoping an operation. Do not use the old Kazam note as an install
  recommendation; its linked project still documents release 1.4.4 and old
  Ubuntu instructions. [Kazam project](https://github.com/hzbd/kazam)
- [ ] Define a concrete VPN-identification use case before using an external
  provider list. Record source, refresh, pinning, cache, and stale-data
  behavior; do not fetch a changing list during normal apply.
  [VPN provider lists](https://github.com/X4BNet/lists_vpn)
- [ ] If Windows guest setup remains in scope, document the stable virtio-win
  ISO as separate guest-artifact acquisition for QEMU/GNOME Boxes. Pin and
  verify the artifact; do not treat it as a GNOME Boxes host operation.
  [virtio-win packaging and downloads](https://github.com/virtio-win/virtio-win-pkg-scripts)
- [ ] Before publishing a release, verify whether `lnk.dk/ridef` is still
  used and points to the canonical repository; update its destination if
  needed.
- [ ] Consider SSH agent forwarding only with user-owned configuration and an
  explicit recovery path.

## Notes closed or covered elsewhere

- The sourced-exit concern is present only in v2 material; the two destructive
  prompt paths in `lib-fedora.sh` already distinguish executed from sourced
  use. Reopen only if an active supported path reproduces the problem.
- Follow this repository's Bash, POSIX bootstrap, header, and ShellCheck
  requirements. Google's shell guide can inform compatible choices, but a
  separate whole-repository style migration is not needed.
  [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
