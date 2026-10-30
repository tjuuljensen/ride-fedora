# Provider foundation batch 04: editors, GNOME utilities, versionlock

Status: **complete: editors supported, GNOME utilities operable opt-in,
versionlock replaced**, 2026-10-30.
The active v2 `BasicEditors` bundle installs/removes `nano` and `vim`.
Fedora 44 provides [`nano`](https://packages.fedoraproject.org/pkgs/nano/nano/)
and the concrete [`vim-enhanced`](https://packages.fedoraproject.org/pkgs/vim/vim-enhanced/)
RPM for the `vim` command. The pinned Workstation image already has `nano`
and `vim-minimal`, but not `vim-enhanced`; a pre-existing RPM is not an
installer acceptance result.

The active v2 `GnomeTools` bundle installs `system-config-printer` and the
old `gnome-tweak-tool` name. Fedora 44 publishes
[`system-config-printer`](https://packages.fedoraproject.org/pkgs/system-config-printer/system-config-printer/)
and [`gnome-tweaks`](https://packages.fedoraproject.org/pkgs/gnome-tweaks/gnome-tweaks/).
The v2 inverse also removes `gparted`, which the installer does not own;
v3 must never repeat that extra removal. These are desktop applications,
kept out of base profiles.

The commented v2 `VersionLock` pair installs/removes the DNF4-era
`python3-dnf-plugin-versionlock`. Fedora 44's
[DNF5 versionlock command](https://dnf5.readthedocs.io/en/latest/commands/versionlock.8.html)
is the current replacement. The pinned Workstation image has DNF5; no v3
operation will edit versionlock policy just to migrate the old plugin.

## Completion criteria defined before implementation

- Split `BasicEditors` into `package.nano` and `package.vim-enhanced`, and
  `GnomeTools` into `package.system-config-printer` and
  `package.gnome-tweaks`. Record exact Fedora 44 x86_64 Workstation source,
  license, signed RPM verification, detection, and declared inverse. Reuse
  unchanged DNF handler failure-injection evidence.
- In a disposable Workstation VM, remove pre-installed `nano` only if the
  preparation transaction affects its known editor-default dependents and
  no unrelated pre-existing RPM. Record that temporary preparation. Then check
  both editors' absent plan, apply, repeat, status, signed RPM/files,
  executable detection, restore, and explicit remove. Reject loss of a
  pre-existing RPM name/architecture identity; record updates and residue.
- Check both GNOME RPMs' absent package lifecycles and installed desktop
  launcher files in a disposable Workstation VM. Count the source outcome
  as an opt-in candidate only after a passing happy path; visual behavior
  and broader failure/recovery belong in v3.1. Preserve `gparted` untouched.
- Verify DNF5 versionlock command availability on the declared VM and
  document `VersionLock` as a non-runnable replacement. Do not create or
  remove policy entries as part of this source outcome.
- Record individual acceptance, Windows alignment, ledger progress, and
  generated docs. Investigate any failed run before retrying.

## DNF5 versionlock replacement

In disposable Fedora 44 x86_64 Workstation overlay
`20261030T114758Z-test-provider-editors-and-gnome-utilities-batch-71f3beab`,
`rpm -q dnf5` and `dnf5 versionlock --help` both passed before any package
change. The v2 DNF4 plugin install/remove pair is therefore replaced by the
current DNF5 command already available on the declared target. RIDE does not
create or delete lock policy entries. This source outcome is a documented,
non-runnable replacement, not a claim that the old RPM was installed.
Review if DNF5 versionlock availability or the target changes.

## Investigated first VM run

The first disposable overlay
`20261030T114758Z-test-provider-editors-and-gnome-utilities-batch-71f3beab`
passed the read-only DNF5 versionlock checks, then stopped at test
preparation before any v3 package operation. `dnf remove nano` removed
`nano`, `nano-default-editor`, and `default-editor` as one declared DNF
transaction; the initial test expected only `nano`. The other two packages
are editor-default dependents, not an unrelated system change. The revised
focused test accepts exactly those three named removals in the disposable
overlay and still rejects any other package change. It then exercises the
v3 operations against that absent baseline. No handler or catalog behavior
changed, and the first run is not package acceptance evidence.

## Focused VM result

The corrected run passed in disposable overlay
`20261030T114934Z-test-provider-editors-and-gnome-utilities-batch-2470cb85`,
catalog SHA-256
`75e82decf27356aa62d8ff4fb7a5e4aff96d6733650c5aaca72dd4f685e47bec`.
The JUnit file `.acceptance-runs/provider-foundation-04-editors-gnome-retry.xml`
records one passing test. The preparation removed only `nano` and its two
known editor-default dependents, creating the disposable absent baseline.
Each new RPM passed absent plan, apply, signed RPM and file verification,
command or desktop launcher probe, status, unchanged repeat, restore, and
explicit remove. Named packages and new dependencies were removed by both
inverses; no pre-existing RPM identity was lost.

| Outcome | v3.0 result | Observed package effects |
| --- | --- | --- |
| [`BasicEditors`](../acceptance/provider-basic-editors.md) | supported package installs | `nano` introduced only its own RPM; `vim-enhanced` updated pre-existing `vim-data` and `vim-minimal` versions. |
| [`GnomeTools`](../acceptance/provider-gnome-tools.md) | operable opt-in candidate | `system-config-printer` updated pre-existing printer library/udev RPM versions; `gnome-tweaks` introduced only its own RPM. Neither operation touched `gparted`. |
| `VersionLock` | documented replacement | DNF5 versionlock command was present; no policy was changed. |

The package inverse does not downgrade DNF-updated RPMs. Removing a
pre-existing `nano` on a real host can also remove its default-editor
dependents; v3.0 acceptance exercised a disposable absent baseline and
does not claim ownership of those existing packages. Broader desktop
visual/recovery coverage, package-driven updates, and pre-installed editor
removal behavior are named v3.1 follow-ups.
