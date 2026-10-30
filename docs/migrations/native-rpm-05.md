# Native RPM batch 05: remaining repository applications and utilities

Status: **complete: two supported and three operable opt-in candidates**, 2026-10-30.
Five v2 install/remove pairs select Fedora RPMs: [`dia`](https://packages.fedoraproject.org/pkgs/dia/dia/),
[`wine`](https://packages.fedoraproject.org/pkgs/wine/wine/),
[`vlc`](https://packages.fedoraproject.org/pkgs/vlc/vlc/),
[`libpst`](https://packages.fedoraproject.org/pkgs/libpst/libpst/), and
[`lynis`](https://packages.fedoraproject.org/pkgs/lynis/lynis/).
The v2 VLC comment expected RPM Fusion, but Fedora now has a VLC RPM. The v3
operation selects Fedora's VLC player and its declared Fedora codec set;
additional codecs are a separate source decision. Wine is a broad Fedora
meta-package. RIDE only installs these tools;
it does not launch Wine, convert user mail data, or run a Lynis audit.
Each candidate is individually selectable on Fedora 44 x86_64 Workstation
through the existing DNF package handler.

## Completion criteria defined before implementation

- Review each current Fedora 44 package, license, exact RPM name, and the
  v2 user-visible intent. For VLC, record the selected Fedora source and
  reserve optional RPM Fusion codec coverage as separate work. Keep all
  operations out of base profiles.
- Use exact Fedora 44 x86_64 Workstation targets, owned installed deployment,
  and declared inverse. Reuse the unchanged DNF handler's focused mocked
  failure evidence. In one disposable VM session, check absent plan, apply,
  repeat, status, signed RPM/files, restore, and explicit remove for each
  selected package. Capture any dependency residue and package upgrades;
  ensure no pre-existing RPM name/architecture pair disappears. A DNF update of a
  signed, pre-existing RPM is recorded but is not a migration blocker for
  these package-only operations.
- Promote a low-risk package only after its exact-target lifecycle passes.
  Keep desktop or broad-package behavior opt-in candidate after a VM happy
  path if broader recovery or visual checks belong in v3.1. A source or
  codec mismatch remains unresolved until the behavior decision is recorded.
- Record individual acceptance, Windows alignment, generated docs, ledger
  status, and any named v3.1 hardening. Investigate a failure before retrying.

## Fedora 44 Workstation result

The five operations passed one focused disposable-VM run in overlay
`20261030T111844Z-test-remaining-native-repository-batch-a48d4efa`.
The pinned Workstation image SHA-256 was
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
catalog SHA-256 was
`b2ddd2a00a03adb2dd164900eb7b435da01d9001bc844630537732129e5ecd63`.
The retained transcript and `.acceptance-runs/native-rpm-05.xml` record a
passing test. Each package passed absent plan, apply, signed RPM and file
verification, installed probe, status, unchanged repeat, restore, and
explicit remove. No pre-existing RPM name/architecture pair was lost.

| Operation | v3.0 result | Observed inverse and package changes |
| --- | --- | --- |
| [`package.libpst`](../acceptance/package.libpst.md) | supported | Full RPM inventory recovered. |
| [`package.lynis`](../acceptance/package.lynis.md) | supported | Full RPM inventory recovered. |
| [`package.dia`](../acceptance/package.dia.md) | opt-in candidate | Named GTK2 dependencies remained; no pre-existing RPM was lost. |
| [`package.wine`](../acceptance/package.wine.md) | opt-in candidate | 112 RPM identities introduced; inverse removed them. Eight existing Samba/libldb RPMs were updated by DNF. |
| [`package.vlc`](../acceptance/package.vlc.md) | opt-in candidate | 43 RPM identities introduced; inverse removed them. Ten existing GStreamer/Qt6 RPMs were updated by DNF. |

The operation inverse is scoped to its named RPM and journal; it does not
downgrade DNF-updated system packages or remove unowned dependency RPMs.
Desktop and broad-package failure/visual checks, dependency residue, and
package-driven updates are tracked in the v3.1 hardening queue. Fedora VLC
does not imply RPM Fusion codec coverage.
