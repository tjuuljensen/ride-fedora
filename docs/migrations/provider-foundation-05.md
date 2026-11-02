# Codec source and Multimedia migration

Status: **v3.0 migration in progress**, reviewed 2026-10-31.
The owner chose **keep** for codec capability. Migrate it to explicit,
opt-in, owned package operations while retaining Fedora and RPM Fusion choices
where package conflicts allow coexistence. Do not resolve the source outcome as
unsupported because the v2 wildcard inverse is unsafe.

The v2 `InstallCodecs` uses globs for several GStreamer families, `lame*`,
and a DNF `Multimedia` group upgrade with optional packages. `RemoveCodecs`
removes only some globbed packages and does not invert the group upgrade or
distinguish packages installed by another owner. Fedora's accepted
[`vlc` package](../acceptance/package.vlc.md) remains a separate application
outcome and does not resolve the bundle migration.

## Completion criteria defined before implementation

- Reconcile the exact v2 commands and Multimedia group members against Fedora
  44. Select useful fixed package sets from Fedora and identify distinct RPM
  Fusion alternatives; preserve both capabilities as opt-in choices when
  package conflicts permit coexistence.
- Give each package a stable v3 operation ID, explicit acquisition source,
  current upstream project and license evidence, and package-level signature
  verification. Detect pre-existing packages and remove only those newly
  installed by the chosen profile.
- Never repeat the v2 wildcard or group upgrade. Keep packages from other
  owners and their version state unchanged. Test plan, apply, repeat, status,
  package verification, and inverse in the Fedora 44 Workstation VM.
- Keep VLC and other media applications separate. Unmigrated members stay
  visible in the ledger with a concrete next action; they do not become
  retired by omission.
- Replace `dnf group upgrade --with-optional Multimedia` with an explicit
  opt-in `system.update-multimedia-codecs` operation over the reviewed Fedora
  44 package-name list. Detect upgrades with `dnf5 check-upgrade --json`; pass
  only currently installed members to `dnf5 upgrade --refresh`. This avoids
  following later group-definition changes or installing optional members
  through the update action. Report that package updates are non-reversible.
- Focused mocks must cover current/no-updates, available updates, DNF error,
  no installed group members, and the exact installed-name allowlist. On a
  disposable Fedora 44 Workstation x86_64 VM, prove plan/apply/update/status,
  repeat, and profile removal behavior; capture the RPM transaction before and
  after, require no unrelated package removal or RPM identity loss, and record
  dependency upgrades. If no updates exist in the target snapshot, seed one
  old Fedora RPM from an official repo and prove the update transition before
  accepting the action.

## Fedora 44 source inventory

A read-only `dnf5 --cacheonly group info Multimedia` on Fedora 44 Workstation
listed 15 mandatory packages and one conditional package. The Multimedia group
is already installed on that host; this is inventory evidence only, not v3
acceptance. Its members are `PackageKit-gstreamer-plugin`, `alsa-ucm`,
`alsa-utils`, `gstreamer1-plugin-dav1d`, `gstreamer1-plugin-libav`,
`gstreamer1-plugin-openh264`, `gstreamer1-plugins-bad-free`,
`gstreamer1-plugins-good`, `gstreamer1-plugins-ugly-free`,
`libva-intel-media-driver`, `pipewire-alsa`, `pipewire-gstreamer`,
`pipewire-pulseaudio`, `pipewire-utils`, and `wireplumber`; the conditional
member is `gstreamer-plugins-espeak`.

Read-only Fedora 44 DNF metadata expands the Fedora part of the v2 globs to
`gstreamer1-plugins-bad-free` and its `extras`, `fluidsynth`, `libs`, `lv2`,
`opencv`, `wildmidi`, and `zbar` subpackages; the `gstreamer1-plugins-good`
package and its `extras`, `gtk`, `qt`, and `qt6` subpackages;
`gstreamer1-plugins-base`; `gstreamer1-plugin-openh264`; `lame`; and
`lame-libs`. Fedora's `gstreamer1-libav` named by v2 is absent from the
current Fedora 44 repository; the current group member is
`gstreamer1-plugin-libav`. The v2 globs exclude `*-devel` packages. If RPM
Fusion is enabled during the v2 glob, the match can also include
`gstreamer1-plugins-bad-freeworld`; that is a separate source and conflict
review.

The complete v2 expansion is now recorded as discrete v3 package operations:
the Fedora `bad-*` matches above, the optional RPM Fusion
`package.gstreamer1-plugins-bad-freeworld`, the Fedora `good-*` matches,
`package.gstreamer1-plugins-base`, OpenH264, the current libav replacement,
and `lame`/`lame-libs`. `*-devel` packages stay excluded, matching the v2
commands. Batches 05C through 05F cover all 16 observed Multimedia group
members, including conditional eSpeak. This preserves the v2 capability
without keeping the broad `group upgrade` or wildcard command runnable.

The first implementation set adds six supported Fedora operations and the
opt-in `fedora-codecs-optional` profile for the extras, Fluidsynth, LV2,
WildMidi, and ZBar plugins plus the LAME encoder. Each uses the generic DNF
handler and exact Fedora RPM source. The declared per-package and combined
profile lifecycle passed on Fedora 44 Workstation; the
[acceptance record](../acceptance/fedora-codecs-optional.md) records package
updates and the clean inverse.

### Batch 05B: Fedora GStreamer good-family add-ons

This batch contains `gstreamer1-plugins-good-extras`, `gstreamer1-plugins-good-gtk`,
`gstreamer1-plugins-good-qt`, and `gstreamer1-plugins-good-qt6`. The completion
checks are defined before acceptance. The pinned Fedora 44 Workstation image
already contains the GTK and Qt6 plugins in its Workstation environment. Model
those as installed-only, one-way operations so profile removal preserves the
environment's packages. Keep `good-extras` and Qt as exact reversible package
operations. On the exact target, verify the profile plan reflects the actual
present/absent states, apply and check `changed` only for absent packages,
repeat and check all steps are unchanged, verify RPM signatures and files plus
status, then remove the profile and prove the two one-way packages remain, the
two newly installed packages are absent, all prior RPM name/architecture
identities remain, and no newly introduced dependency residue survives. Each
operation uses Fedora-signed RPMs and the generic DNF package handler. The
optional profile stays out of `default`.

The [batch acceptance record](../acceptance/fedora-codecs-good-plugins.md)
records a passing Fedora 44 VM run. All four operations are supported for the
declared Workstation target; their state and inverse behavior differ as
described above. These operations are separate from the first profile's six
supported IDs.

### Batch 05C: Fedora Workstation Multimedia GStreamer prerequisites

This batch contains `gstreamer1-plugins-bad-free`,
`gstreamer1-plugins-good`, `gstreamer1-plugin-dav1d`,
`gstreamer1-plugin-libav`, `gstreamer1-plugin-openh264`, and
`gstreamer1-plugins-ugly-free`. The current Fedora `gstreamer1-plugin-libav`
is the replacement for the v2 `gstreamer1-libav` name, which is no longer
available in Fedora 44. The pinned Workstation image includes all six as
Multimedia group prerequisites. Model them as installed-only one-way
operations, keep them in a separate opt-in profile, and do not remove any on
profile removal. Before apply, assert the exact image's six package states;
then verify plan, apply, repeat, status, Fedora RPM signatures and file
verification, and remove-profile behavior. Package identities already in the
image must remain present after removal. If the pinned baseline differs, stop
before applying and review the transcript. These checks are defined before
the VM run. See the [batch acceptance record](../acceptance/fedora-codecs-multimedia-group.md).

### Batch 05D: Fedora codec runtimes and OpenCV plugin

This four-package batch covers `gstreamer1-plugins-bad-free-libs`,
`gstreamer1-plugins-bad-free-opencv`, `gstreamer1-plugins-base`, and
`lame-libs`. The pinned Workstation image baseline contains the runtime
libraries, base plugins, and LAME libraries; OpenCV is absent and therefore
uses exact remove-new-install recovery. Keep the profile opt-in. Before apply,
assert that baseline, then check plan, apply, repeat, package signatures,
`rpm -V`, status, and profile removal. The three pre-existing packages must
remain; OpenCV must be removed; pre-existing RPM identities must remain and
new dependency residue must be limited to packages introduced by this batch.
If the baseline differs, stop before apply and inspect the transcript. These
checks are defined before the VM run. See the
[batch acceptance record](../acceptance/fedora-codecs-runtime-and-opencv.md).

### Batch 05E: Fedora audio and video integration prerequisites

This six-package batch contains `PackageKit-gstreamer-plugin`, `alsa-ucm`,
`alsa-utils`, `libva-intel-media-driver`, `pipewire-alsa`, and
`pipewire-gstreamer`, all listed in the Fedora Workstation Multimedia group
and present in the pinned image. Model them as installed-only one-way
operations in a separate opt-in profile. Before apply, verify the exact
baseline, then check plan, apply, repeat, RPM signatures, `rpm -V`, status,
profile removal, and preservation of every prior RPM identity. If the baseline
differs, stop before apply and inspect the transcript. These checks are
defined before the VM run.

### Batch 05F: Fedora PipeWire and conditional eSpeak packages

This four-package batch contains the remaining `pipewire-pulseaudio`,
`pipewire-utils`, and `wireplumber` Multimedia group prerequisites plus
conditional member `gstreamer-plugins-espeak`, which is available in Fedora
44 repository metadata. The first three packages are already present in the
pinned Workstation image and are installed-only one-way operations. eSpeak is
absent, so it is an exact reversible RPM install. Before apply, assert this
baseline, then check plan, apply, repeat, Fedora signature metadata, `rpm -V`,
status, profile removal, and recovery of all prior RPM identities without
unrelated dependency residue. If the baseline differs, stop before apply and
inspect the transcript. These checks are defined before the VM run.

### Batch 05G: RPM Fusion HEVC/H.265 add-on

RPM Fusion's current
[`gstreamer1-plugins-bad-freeworld` spec](https://github.com/rpmfusion/gstreamer1-plugins-bad-freeworld/blob/master/gstreamer1-plugins-bad-freeworld.spec)
builds only the `de265`, `svthevcenc`, and `x265` GStreamer modules and
installs distinct plugin library files. It shares the GStreamer data
directory with Fedora packages but does not replace their plugin libraries.
Model this as an additional RPM Fusion package beside Fedora
`gstreamer1-plugins-bad-free`; pin installation to `rpmfusion-free-updates`
and keep it in an opt-in profile requiring the separately owned RPM Fusion
repository profile. Do not swap or downgrade Fedora's package.

Before implementation, the completion checks are: focused mocked checks that
the RPM Fusion source ID selects only `--from-repo=rpmfusion-free-updates` and
unknown DNF sources fail closed; exact Fedora 44 Workstation preflight showing
the plugin absent and the Fedora bad-free package present; apply with RPM
Fusion GPG verification; repeat; package signature and `rpm -V`; verify the
Fedora package remains installed and no pre-existing RPM identity is lost;
remove the add-on and confirm any RPM Fusion repository cleanup is safe. If
baseline or dependency behavior differs, investigate before retrying. Broader
repository trust and rollback failure hardening stays visible in the separate
RPM Fusion source batch.

Continue with the exact v2 wildcard reconciliation and Fedora RPM Fusion
`bad-freeworld` conflict/source review. The parent v2 outcome remains in
progress until those paths have an operable v3 implementation or documented
replacement. Unselected behaviors remain visible here and in the ledger with
their next action.

The **05G completion checks passed** on 2026-10-31. The exact Fedora 44
Workstation VM test prepared the separate `rpmfusion` profile, installed
`gstreamer1-plugins-bad-freeworld` from `rpmfusion-free-updates`, verified its
RPM signature and file integrity, confirmed the Fedora bad-free package and
all baseline RPM identities remained, repeated apply unchanged, removed the
add-on and its three new runtime dependencies, and removed RPM Fusion cleanly.
See the [operation acceptance record](../acceptance/package.gstreamer1-plugins-bad-freeworld.md).
The operation remains a `candidate` and is available only through the
explicit `fedora-codecs-rpmfusion` opt-in profile with `--allow-candidate`.
This closes the selected HEVC/H.265 coexistence path. The exact Fedora wildcard
set and observed Multimedia group members now map to explicit package
operations. Batch 05H implements the remaining v2 update effect as a
fixed-name, non-reversible Fedora operation; see its completion record and
acceptance evidence below.

### Opt-in profile choices for owner review

Three codec profiles now separate the baseline, additional Fedora plugins,
and the RPM Fusion HEVC/H.265 add-on:

- [`fedora-codecs-baseline`](../../profiles/fedora-codecs-baseline.json)
  selects the seven 64-bit Fedora Workstation packages GStreamer base, good,
  bad-free, dav1d, libav, OpenH264, and ugly-free.
- [`fedora-codecs-optional`](../../profiles/fedora-codecs-optional.json)
  selects six optional Fedora plugin and LAME packages.
- [`fedora-codecs-rpmfusion`](../../profiles/fedora-codecs-rpmfusion.json)
  selects only `bad-freeworld` and requires the separate `rpmfusion` profile.

### Batch 05H: Fixed-list Multimedia package updates

The v2 group upgrade changes already installed Multimedia members. Operation
`system.update-multimedia-codecs` queries updates with DNF5 `check-upgrade`
and upgrades only currently installed names from the fixed 16-member Fedora
44 inventory. It does not follow later group metadata changes or install
missing optional group members. Its `current` state is observable, but RPM
updates have no exact inverse; the profile is opt-in and removal leaves those
updates in place. Before apply, RIDE displays DNF5's `--assumeno` transaction
preview and refuses a preview that includes removals or downgrades.

The defined acceptance checks are focused JSON and exit-code mocks, exact
installed-name selection, DNF error handling, and a disposable Fedora 44
Workstation update transition. **05H passed** on 2026-10-31. The VM preserved
all 1,913 baseline RPM name/architecture identities, verified updated package
signatures and files, recorded 44 upgrades and one weak-dependency install,
repeated as current, and confirmed removal/restore do not claim to reverse the
transaction. See the [batch acceptance record](../acceptance/system.update-multimedia-codecs.md).
The operation is supported on Fedora 44 Workstation x86_64 and remains
opt-in. H037 tracks broader dependency-impact and recovery reporting for v3.1.

A read-only plan on the Fedora 44 Workstation host found base, good, bad-free,
and libav already installed; dav1d, OpenH264, and ugly-free were absent. No
package was applied during that review. The owner will adjust the baseline
selection after checking for missing packages. No 32-bit RPMs are selected
until their use case is established. The baseline profile has no combined
disposable-VM acceptance yet; this host plan is not treated as VM evidence.
