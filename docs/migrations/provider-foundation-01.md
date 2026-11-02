# Provider foundation batch 01: required tools and shell tools

Status: **ShellTools supported; Workstation `Required` operable opt-in candidate**, 2026-10-31.
The active v2 preset calls `InstallRequired` and `InstallShellTools`.
`InstallRequired` installs `coreutils`, `git`, `gnupg`, `python`, `tar`,
`wget`, and `gcc` one by one if missing; it has no inverse. `InstallShellTools`
installs `pv` and `strace`, and `RemoveShellTools` removes those same two
RPMs. The v3 base profiles remain small; these are opt-in or operation-specific
tools, not implicit prerequisites for every setup.

The pinned Fedora 44 x86_64 Workstation image already includes `coreutils`,
`git`, `gnupg2`, `python3`, `tar`, and the `wget2-wget` shim, but lacks `gcc`,
`pv`, and `strace`. This is image evidence, not a guarantee about every
Fedora 44 host.
Fedora 44 publishes [`pv`](https://packages.fedoraproject.org/pkgs/pv/pv/)
under GPL-3.0-or-later and
[`strace`](https://packages.fedoraproject.org/pkgs/strace/strace/) under
multiple licenses listed in Fedora metadata. The v2 `wget` package name is
split on Fedora 44 between
[`wget1-wget`](https://packages.fedoraproject.org/pkgs/wget1/wget1-wget/) and
[`wget2-wget`](https://packages.fedoraproject.org/pkgs/wget2/wget2-wget/).
These shims conflict because both provide the `wget` command. Fedora describes
Wget 2 as the successor, and the pinned VM already has its shim installed, so
v3 selects Wget 2 while preserving `/usr/bin/wget`. Fedora's
[`python-unversioned-command`](https://packages.fedoraproject.org/pkgs/python3.14/python-unversioned-command/)
provides `/usr/bin/python` as Python 3. These package choices do not control
the v3 client's actual prerequisites.

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
- Preserve all seven `Required` capabilities as separately owned opt-in RPM
  operations. Keep runtime prerequisite checks independent from those package
  choices and do not add the profile to a base profile.
- Record Windows contract alignment, ledger progress, generated docs, and
  any v3.1 hardening after the VM run. Investigate a failure before retrying.

## `Required` re-opened for v3.0

The owner clarified that package use is not inferred from preset position and
that v2 package capabilities remain in v3.0 scope. This supersedes the earlier
workstation replacement disposition. The seven v2 package names map to these
Fedora 44 repository choices:

| v2 name | Fedora RPM | v3 intent |
| --- | --- | --- |
| `coreutils` | `coreutils` | GNU core utilities |
| `git` | `git` | Git command line |
| `gnupg` | `gnupg2` | GnuPG command line |
| `python` | `python-unversioned-command` | Preserve `/usr/bin/python`, which Fedora maps to Python 3 |
| `tar` | `tar` | GNU archive command |
| `wget` | `wget2-wget` | Preserve the `wget` command using Fedora 44's current Wget 2 compatibility shim |
| `gcc` | `gcc` | GNU C compiler |

Official Fedora package records list these packages for Fedora 44 and publish
their upstream and license metadata: [`coreutils`](https://packages.fedoraproject.org/pkgs/coreutils/coreutils/),
[`git`](https://packages.fedoraproject.org/pkgs/git/git/),
[`gnupg2`](https://packages.fedoraproject.org/pkgs/gnupg2/gnupg2/),
[`python-unversioned-command`](https://packages.fedoraproject.org/pkgs/python3.14/python-unversioned-command/),
[`tar`](https://packages.fedoraproject.org/pkgs/tar/tar/),
[`wget2-wget`](https://packages.fedoraproject.org/pkgs/wget2/wget2-wget/),
and [`gcc`](https://packages.fedoraproject.org/pkgs/gcc/gcc/). The Python and
Wget names deliberately follow v2's commands while selecting Fedora's current
provider. The disposable VM showed its baseline already has `wget2-wget`; Fedora
explicitly declares the Wget 1 and Wget 2 shims conflicting providers of the
same `wget` command. The Wget 2 provider is the modern Fedora path and remains
selectable without evicting the baseline provider.

### Completion checks defined before implementation

- Add seven distinct Fedora RPM operation IDs and one opt-in `required-tools`
  profile. Keep both existing base profiles unchanged. Use the existing DNF
  handler, repository GPG verification, system scope, and exact Fedora 44
  Workstation x86_64 target. Declare installed-only states and `recovery:none`
  because v2 `InstallRequired` has no inverse and several packages are system
  essentials; profile removal must not remove any of them.
- Reuse the DNF handler's existing mocked install, repeat, inventory, status,
  and failure evidence. Add focused mapping and catalog checks for the seven
  exact RPM names, command coverage, one-way states, and profile membership.
- On a disposable Fedora 44 Workstation VM, capture RPM name/architecture/
  version inventory before and after. Check plan, candidate refusal, apply,
  unchanged repeat, status, `rpm -V`, command availability, and that profile
  removal is refused without changing package inventory. Report which packages
  were already present, packages newly installed, and any dependency or
  existing-package changes from DNF.
- Treat an exact passing Workstation run as an operable opt-in candidate. Do
  not add the profile to `default` or `server-base`. Server's separate
  eleven-package `Required` mapping remains an in-scope follow-on batch with
  its own package mapping and Fedora 44 Server lifecycle.
- Compare Linux schema and lifecycle with Windows, regenerate the operation
  reference and progress reports, and retain the VM transcript. No manual
  session is needed.

The v3 client still checks its own runtime prerequisites where they are used;
these seven operations preserve the separate v2 user-visible tool capability.
They do not make global packages implicit client prerequisites.

## Previous `Required` replacement assessment (superseded)

The v3 bootstrap checks Bash and jq and offers explicit `--install-deps` for
those two packages. It requires curl and tar to download/unpack the tagged
source. The client checks jq, and trusted handlers check their own actual
commands, including DNF/RPM verification and GitHub-download tooling.
The earlier assessment treated dependency checks as sufficient replacement
and did not migrate the seven selectable packages. That is no longer the v3.0
decision. Dependency checks remain separate from these opt-in package
operations.

This section remains as decision history only; the batch above now supplies
the package mappings, one-way contract, and target checks.

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


## Workstation `Required` VM result

The seven operations in [`provider-required-tools.md`](../acceptance/provider-required-tools.md)
passed the defined Fedora 44 Workstation x86_64 profile lifecycle. Six packages
were already present; the transaction installed `gcc` and four dependencies.
DNF also upgraded eight pre-existing RPMs to Fedora 44 updates. All previous
package name/architecture identities remained, all seven signatures and file
verification checks passed, and command checks succeeded. Repeat was unchanged;
removing the profile kept the seven packages installed under their one-way
contract. The exact transaction and target transcript are in the acceptance
record. H035 tracks review of DNF's package-upgrade side effects.

The first run tried Fedora's `wget1-wget` compatibility shim and exposed its
conflict with the baseline `wget2-wget`. Fedora explicitly marks them as
conflicting providers of `/usr/bin/wget`; catalog `package.wget` now selects
Wget 2, which is the current image provider. The corrected VM run passed.
The generic Server `Required` outcome remains the next separate batch; its
eleven RPMs need Server-specific ownership mapping and target acceptance.
