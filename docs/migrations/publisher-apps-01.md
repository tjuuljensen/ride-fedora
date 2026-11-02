# AppImage integration manager: AppImageLauncher to Gear Lever

The owner kept AppImageLauncher in the v3.0 fast-track review on 2026-10-30.
Preserve existing user AppImages when implementing its desktop integration.

Status: **PASS; operable opt-in candidate**, 2026-11-01. This isolated active-preset
outcome maps `InstallAppImageLauncher` and `RemoveAppImageLauncher`. v2
selects the first x86_64 RPM from the mutable latest GitHub release, passes
its URL to DNF, and creates `~/Applications`. The inverse removes the RPM
and deletes that directory if empty, without a recorded ownership baseline.

## Completion criteria defined before implementation

- Use the Flathub Gear Lever application ID and its signed system remote;
  record source, product, license, target, and GPG verification.
- Ensure install refuses an unexpected app origin. Uninstall only the RIDE
  installed app and do not request Flatpak `--delete-data`. Seed both the
  Gear Lever config directory and unrelated existing AppImages/launcher
  entries, then prove package removal preserves all seeded user state.
- Refuse installation while the v2 `appimagelauncher` RPM remains installed,
  because both managers can claim AppImage handling. Removing that legacy RPM
  is an explicit operator prerequisite; do not delete `~/Applications`.
- Add mocked origin, repeat, failed-install, and preservation checks. On a
  disposable Fedora 44 x86_64 Workstation VM verify plan, candidate refusal,
  apply, application identity and origin, CLI help, repeat, status, removal,
  and preservation of user state. Keep it opt-in and outside base profiles.
- Leave import, move, update, and removal of AppImage files user driven.
  Reserve broader visual integration checks for H070 in v3.1.

The owner kept this capability for v3.0. AppImageLauncher's latest tagged
Fedora RPM is a beta with an inconsistent asset name and no accepted Fedora 44
recovery contract. Gear Lever is the maintained AppImage manager alternative:
its upstream documents menu integration, organized storage, and update
management; Flathub publishes application ID `it.mijorus.gearlever` for
x86_64. Its release 4.6.2 is listed under GPL-3.0. The Flathub system remote
uses the existing GPG-verified remote operation.

The v3 operation will install only Gear Lever. It will not add RIDE behavior
that imports, moves, updates, or removes AppImages. Preserve the old
`~/Applications` compatibility directory and every existing AppImage or
desktop entry on install and uninstall. The apply preflight refuses an
installed `appimagelauncher` RPM; an operator must remove that legacy package
before choosing Gear Lever. RIDE does not manage either tool's user
integration state.

The Fedora 44 Workstation lifecycle passed candidate refusal, plan, signed
Flathub install, origin and CLI checks, repeat, status, and removal. It verified
the legacy RPM was absent and preserved seeded Gear Lever config, the
`~/Applications` directory, an unrelated AppImage, and its desktop entry.
Detailed target, run IDs, hashes, and transcript are in the
[`package.gearlever` acceptance record](../acceptance/package.gearlever.md).
