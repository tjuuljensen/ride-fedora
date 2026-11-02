# `InstallRequired` Fedora 44 migration acceptance

Status: **PASS; operable opt-in candidate on Fedora 44 Workstation x86_64**.

The v2 function is a one-way install loop for seven RPM names. It has no
removal function. The v3 path preserves each package as a distinct system
operation in the opt-in `required-tools` profile:

| v2 name | v3 operation | Fedora RPM | Command check |
| --- | --- | --- | --- |
| `coreutils` | `package.coreutils` | `coreutils` | `printf`, `id` |
| `git` | `package.git` | `git` | `git --version` |
| `gnupg` | `package.gnupg2` | `gnupg2` | `gpg --version` |
| `python` | `package.python-command` | `python-unversioned-command` | `python --version` |
| `tar` | `package.tar` | `tar` | `tar --version` |
| `wget` | `package.wget` | `wget2-wget` | `wget --version` |
| `gcc` | `package.gcc` | `gcc` | `gcc --version` |

Each operation uses the Fedora signed RPM source, declares only `installed`,
and has `recovery: none`. Applying an operation or profile does not claim a
package removal inverse. The profile is opt-in and stays out of `default` and
`server-base`.

The mocked acceptance checks exact package names, source and target metadata,
installed-only states, candidate gating, profile membership, unchanged repeat,
status, and refusal to remove while preserving installed packages. Existing
DNF handler failure, journal, and RPM verification evidence is reused because
the handler is unchanged.

The disposable VM check captures package name, architecture, EVR, and signature
inventory before and after. It checks read-only plan, candidate refusal, apply,
repeat, status, `rpm -V`, the listed commands, and profile removal refusal. The
report distinguishes packages already installed from packages added by this
run and records dependency upgrades or residue. It does not test removal by
manually erasing any baseline or essential RPM.


The first disposable run found that the image already contains `wget2-wget`;
Fedora marks that package as conflicting with `wget1-wget` because both
provide `/usr/bin/wget`. The DNF solver failed before starting a package
transaction, and the journal recorded the five already-installed operations
as unchanged followed by the failed Wget resolution. Fedora describes
`wget2-wget` as the shim that provides `wget`, so the catalog now selects that
current provider and preserves the image's selected Wget implementation.


The final disposable Fedora 44 Workstation x86_64 lifecycle passed. The pinned
image began with 1,913 RPMs; `coreutils`, `git`, `gnupg2`,
`python-unversioned-command`, `tar`, and `wget2-wget` were already installed. RIDE
installed `gcc` and four dependencies (`glibc-devel`, `kernel-headers`,
`libxcrypt-devel`, and `make`), then upgraded eight pre-existing RPM identities
(`cpp`, `glibc`, `glibc-all-langpacks`, `glibc-common`, `glibc-gconv-extra`,
`libatomic`, `libgcc`, and `libgomp`). No pre-existing name/architecture pair
was lost. All seven RPM signatures, `rpm -V` checks, and commands passed. The
profile repeated unchanged and removal kept all seven operations installed.
The post-apply inventory had 1,918 RPMs and was unchanged after profile removal.

The first run exposed a solver conflict between the two Fedora Wget shims. The
corrected mapping selects the image's existing `wget2-wget`; the passing run
verified its package and `wget --version`. The successful DNF refresh reported
mirror timeouts for one mirror, then loaded repository metadata from the others
and completed the transaction. No retry was needed. The package upgrades and
transaction review are tracked in v3.1 item H035.

Target image SHA-256:
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`. Acceptance
transcript:
`/tmp/ride-fedora-required-tools-03/fedora-44-workstation-x86_64/20261031T091301Z-test-required-tools-profile-keeps-one-way-rpm-capabilities-7b4bcf1c/transcript.jsonl`
(SHA-256 `652534e1f4333cda563b92eb8240f273f34f820888e342ba647b8bc12fa41681`).
Apply, unchanged repeat, and profile removal runs are
`20261031T091329Z-2673-22843`, `20261031T091522Z-6159-19751`, and
`20261031T091523Z-7031-28611`.
