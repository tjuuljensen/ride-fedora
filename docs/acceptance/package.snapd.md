# `package.snapd` acceptance

Status: **PASS; opt-in candidate** on Fedora 44 Workstation x86_64, 2026-10-31.
Product: Fedora Snap runtime RPM, installed deployment, `fedora-rpm` source,
system scope. The operation exposes only `installed` and declares
`recovery: none`; it does not install or remove Snap applications, change the
classic `/snap` path, or remove Snap state.

Fedora publishes `snapd-2.77.1-0.fc44` under GPL-3.0-only. The source is
Fedora's signed RPM repository. Snapcraft's Fedora setup uses the Fedora RPM,
and its `/snap` symlink is optional for classic snaps. See the
[Fedora package record](https://packages.fedoraproject.org/pkgs/snapd/snapd/),
[Fedora setup instructions](https://snapcraft.io/docs/tutorials/install-the-daemon/fedora/),
and [Snap confinement documentation](https://snapcraft.io/docs/explanation/security/snap-confinement/).

| Exact target | Outcome and evidence |
| --- | --- |
| Fedora 44 Workstation x86_64, `VARIANT_ID=workstation` | PASS: image SHA-256 `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`; overlay `20261031T030157Z-test-snap-runtime-install-only-preserves-state-and-runs-test-snap-dc73f5f0`; [batch record](../migrations/provider-foundation-12.md). |

The test started with no `snapd` RPM and seeded unrelated system and user
sentinels with content and mode checksums. Plan showed the opt-in runtime as
absent. Apply without `--allow-candidate` was refused; candidate apply
installed Fedora's signed RPM, `rpm -V` passed, and `snapd.socket` was enabled
and active. `snap version`, installed status, repeat apply, and the exact
refusal of restore and remove passed. The test installed and ran the
test-owned `hello-world` snap, then removed only that snap inside the
disposable overlay. The pre-existing sentinels and `/snap` path were
unchanged.

`hello-world` reports `confinement: strict` in `snap info --verbose`, while
`snap debug confinement` reports `partial` on this Fedora host and SELinux is
Enforcing. Snapd also logged that AppArmor was not enabled. The snap's
metadata therefore does not establish strict host confinement. This runtime
remains an opt-in candidate; AppArmor and confinement coverage, app lifecycle,
app data recovery, and RPM/Flatpak coexistence are tracked in H034.

The single passing VM test took 566.83 seconds. JUnit is
`.acceptance-runs/provider-foundation-12-candidate-clean.xml`; the transcript
and metadata are under
`.acceptance-runs/provider-foundation-12-candidate-clean/fedora-44-workstation-x86_64/`.
It ran with source revision `9da0526d412343076d6327c6cb3c5331be6d773a`
and uncommitted changes. Catalog SHA-256:
`7ad45d7f83d4de99915dd6ce8e95fcc045d5fd9ce4eedf062ae61bbcfd42a541`.
Source bundle SHA-256:
`dd963d411a32ce3bf8803966d2ae6c4ceff91d5ad2702d081564f38acb3ca684`.
