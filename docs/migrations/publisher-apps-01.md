# AppImageLauncher publisher RPM and user integration

The owner kept AppImageLauncher in the v3.0 fast-track review on 2026-10-30.
Preserve existing user AppImages when implementing its desktop integration.

Status: **unsupported for v3.0**, 2026-10-30. This isolated active-preset
outcome maps `InstallAppImageLauncher` and `RemoveAppImageLauncher`. v2
selects the first x86_64 RPM from the mutable latest GitHub release, passes
its URL to DNF, and creates `~/Applications`. The inverse removes the RPM
and deletes that directory if empty, without a recorded ownership baseline.

## Completion criteria defined before an operable candidate

- Pin one publisher RPM, record its license and exact artifact hash, and
  verify the accepted signature or hash before installation. Distinguish
  package files from integrated AppImages and user launcher data.
- Detect a pre-existing package and `~/Applications`; never adopt or remove
  an unowned directory or AppImage. Mock conflict and failed-install paths.
  In a disposable Fedora 44 x86_64 Workstation VM, check plan, apply,
  repeat, status, removal, and seeded user-AppImage preservation.
- Keep it opt-in until the VM happy path passes. Put any broader desktop
  interaction checks in v3.1; do not claim Fedora support from a generic
  compatibility statement.

[Upstream](https://github.com/TheAssassin/AppImageLauncher) publishes MIT
source and says its native package integrates deeply with the desktop and
can move AppImages into a central location. Its latest GitHub release at
review is `v3.0.0-beta-3`, with an x86_64 RPM asset; upstream's compatibility
table does not declare Fedora 44 support. RIDE has no verified publisher-RPM
acquisition handler or ownership-aware integration inverse. Therefore this
outcome is **non-runnable unsupported in v3.0**. Reopen when a pinned,
licensed release has Fedora 44 VM evidence for both package and seeded
user-AppImage recovery. Existing user AppImages and `~/Applications` remain
outside RIDE v3 ownership.

The owner deferred the AppImageLauncher keep-or-retire choice on 2026-10-30.
Its v3.0 disposition remains non-runnable while current-source and
user-AppImage recovery design make that decision concrete.
