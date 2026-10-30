# Provider foundation batch 01: required tools and shell tools

Status: **complete: Required replaced; ShellTools supported**, 2026-10-30.
The active v2 preset calls `InstallRequired` and `InstallShellTools`.
`InstallRequired` installs `coreutils`, `git`, `gnupg`, `python`, `tar`,
`wget`, and `gcc` one by one if missing; it has no inverse. `InstallShellTools`
installs `pv` and `strace`, and `RemoveShellTools` removes those same two
RPMs. The v3 base profiles remain small; these are opt-in or operation-specific
tools, not implicit prerequisites for every setup.

The pinned Fedora 44 x86_64 Workstation image already includes `coreutils`,
`git`, `gnupg2`, `python3`, and `tar`, but lacks `wget`, `gcc`, `pv`, and
`strace`. This is image evidence, not a guarantee about every Fedora 44 host.
Fedora 44 publishes [`pv`](https://packages.fedoraproject.org/pkgs/pv/pv/)
under GPL-3.0-or-later and
[`strace`](https://packages.fedoraproject.org/pkgs/strace/strace/) under
multiple licenses listed in Fedora metadata. The v2 `wget` package name is
ambiguous on Fedora 44: Fedora publishes both
[`wget1-wget`](https://packages.fedoraproject.org/pkgs/wget1/wget1-wget/) and
[`wget2-wget`](https://packages.fedoraproject.org/pkgs/wget2/wget2-wget/).
The `python` name also needs an explicit Python 3 decision if an optional
developer-tool profile is requested. These source choices do not control the
v3 client's actual prerequisites.

## Completion criteria defined before implementation

- Split `ShellTools` into `package.pv` and `package.strace`, each using its
  exact Fedora RPM, declared installed/absent states, signature verification,
  current-state detection, and journaled inverse. Keep both out of base
  profiles. Reuse the unchanged DNF handler's mocked failure evidence.
- In one disposable Fedora 44 x86_64 Workstation VM, check each absent plan,
  apply, repeat, status, signed RPM/files, command availability, restore, and
  explicit remove. Record any named dependency residue or package upgrades;
  reject loss of a pre-existing RPM name/architecture identity.
- Count `ShellTools` as supported only when both mapped operations pass. The
  same acceptance record must identify both IDs, target, overlay, outcome,
  and recovery. No manual session is needed for package installation.
- Review the actual v3 bootstrap and handler prerequisites before resolving
  `Required`. If the broad install bundle is replaced by explicit dependency
  checks, document which v2 packages are no longer installed and why; count
  the outcome as a non-operable replacement, never as a working install.
- Record Windows contract alignment, ledger progress, generated docs, and
  any v3.1 hardening after the VM run. Investigate a failure before retrying.

## `Required` replacement decision

The v3 bootstrap checks Bash and jq and offers explicit `--install-deps` for
those two packages. It requires curl and tar to download/unpack the tagged
source. The client checks jq, and trusted handlers check their own actual
commands, including DNF/RPM verification and GitHub-download tooling.
Consequently, the v2 global `InstallRequired` bundle is replaced by
dependency checks at the point of use. There is no v3 operation that installs
the seven legacy packages together, and the v3 base does not silently add
`gcc`, `wget`, `git`, GnuPG, or Python as workstation conveniences. This
replacement is a **resolved, non-runnable disposition** in the ledger; it
does not count as a working install or guarantee those tools on all hosts.

Review trigger: add an explicitly requested opt-in developer-tool profile
only after choosing Fedora 44 Python and wget providers, defining safe
installed-only behavior for essential packages, and accepting the declared
target in a disposable VM. That optional addition is separate from the
v3.0 prerequisite contract and migration release gate.

## `ShellTools` VM result

[`package.pv` and `package.strace`](../acceptance/provider-shell-tools.md)
passed a focused Fedora 44 x86_64 Workstation run in disposable overlay
`20261030T112939Z-test-provider-shell-tools-batch-and-profile-7f5f4462`.
Each package passed absent plan, apply, signed RPM and file verification,
command detection, status, unchanged repeat, restore, and explicit remove.
The curated `shell-tools` profile then passed combined plan, apply, repeat,
and restore. Each inverse returned the full RPM inventory to baseline;
neither operation retained dependencies or changed pre-existing RPMs.
No manual session was needed. The profile is opt-in and neither base profile
changed.
