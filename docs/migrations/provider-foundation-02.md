# Provider foundation batch 02: RPM Fusion repository enablement

Status: **v3.0 supported on Fedora 44 Workstation x86_64**, reviewed 2026-10-31.
The owner chose **keep** in the v3.0 fast-track review on 2026-10-30. The
repository capability remains in scope; the trust and recovery checks below
are its implementation work, not an optional reopening trigger.
The active v2 preset calls `InstallRPMfusionRepos`, which installs the free
and nonfree Fedora release RPMs from RPM Fusion mirror URLs. Its inverse
deletes every `/etc/yum.repos.d/rpmfusion*` path and removes every installed
RPM whose name matches `rpmfusion`. That broad deletion can remove repo
configuration or packages RIDE did not create. It cannot be used as the v3
recovery path.

RPM Fusion currently publishes Fedora 44
[`rpmfusion-free-release-44.noarch.rpm`](https://download1.rpmfusion.org/free/fedora/)
and the corresponding
[`nonfree` release package](https://download1.rpmfusion.org/nonfree/fedora/).
It also publishes separate [free](https://download1.rpmfusion.org/free/fedora/RPM-GPG-KEY-rpmfusion-free-fedora-2020)
and [nonfree](https://download1.rpmfusion.org/nonfree/fedora/RPM-GPG-KEY-rpmfusion-nonfree-fedora-2020)
signing keys. The release RPMs are signed by these RPM Fusion keys, not by
Fedora. The current v3 `dnf-package` handler does not establish RPM Fusion trust
or own repository configuration. The new custom handler does this as a
separate opt-in operation. Its exact Fedora 44 Workstation lifecycle and
focused failure checks are accepted; other targets remain outside this support
claim.

RPM Fusion's Fedora 44 free release package is currently
`rpmfusion-free-release-44-3.noarch`, a 5.7 KB noarch package requiring
`system-release(44)`. RPM Fusion's [release package source spec](https://github.com/rpmfusion/rpmfusion-free-release/blob/master/rpmfusion-free-release.spec)
declares BSD-1-Clause and packages repository configuration with its public
keys. The [Fedora 44 package record](https://rpmfind.net/linux/RPM/rpmfusion/free/fedora/updates/44/x86_64/r/rpmfusion-free-release-44-3.noarch.html)
lists six free-key paths and three repository files under
`/etc/yum.repos.d`. The official [Fedora 44 release directory](https://download1.rpmfusion.org/free/fedora/updates/44/x86_64/r/)
publishes the RPM, and nonfree is published separately. RPM Fusion's current
source repo definition sets `gpgcheck=1`. The accepted target lifecycle
confirmed the Fedora 44 release RPMs use `gpgcheck=1` and `repo_gpgcheck=0`.
These facts establish the vendor path, file ownership model, and the trust
boundary documented below.

Fedora's signed `distribution-gpg-keys-1.118-1.fc44` package includes the
Fedora 44 RPM Fusion free and nonfree keys. The expected 2020 key fingerprints are
`E9A491A3DE247814E7E067EAE06F8ECDD651FF2E` (free) and
`79BDB88F9BBF73910FD4095B6A2AF96194843C65` (nonfree). A disposable Fedora 44
Workstation probe verified both `44-3` release RPM signatures with these keys.
See the [bootstrap trust acceptance record](../acceptance/rpmfusion-bootstrap-trust.md).
Fedora's package index lists the key bundle as CC0-1.0; its files are maintained in the
[upstream distribution-gpg-keys project](https://github.com/rpm-software-management/distribution-gpg-keys/tree/main/keys/rpmfusion).

## Completion criteria defined before implementation

- Bootstrap trust is established for the exact free and nonfree `44-3` RPMs
  and Fedora-distributed signing keys; refresh this evidence if the URLs,
  release RPMs, key fingerprints, or Fedora target change. Verify the
  installed repository definitions retain package `gpgcheck=1` and reject
  unexpected publisher/key state. The tested upstream release RPMs set
  `repo_gpgcheck=0`, recorded as the v3.0 trust boundary.
- Model free and nonfree repositories as separate owned operations or a
  reviewed atomic bundle. Detect pre-existing release packages, key files, and exact package-owned paths
  before apply. Fedora Workstation already ships separate NVIDIA and Steam
  filtered repo files from `fedora-workstation-repositories`; preserve them
  because the RPM Fusion release RPMs do not own those paths.
- Exercise trusted acquisition, invalid signature and payload digest,
  ownership-marker failure, partial install, repeat, status, and restore in
  focused mocked checks. In a disposable Fedora 44 x86_64 Workstation VM,
  verify package-signature enforcement, install and inverse, and preservation
  of prior repositories, keys, and packages. A failed run must be investigated
  before retrying.
- Mark the operation supported only for the accepted Fedora 44 Workstation
  x86_64 target after trust, exact inverse, and lifecycle evidence passes. Keep
  the profile opt-in and never use the v2 broad-deletion inverse.
- Keep repository enablement out of `default` and `server-base`; downstream
  RPM Fusion package operations require their own source and VM evidence.

## v3.0 migration path

The v2 pair changes future acquisition for the whole host, uses two external
release RPMs, and has a wildcard inverse that can delete another owner's
repository configuration and installed release packages. Keep this source
outcome in the v3.0 migration scope as the owner requested. The supported
operation `setting.rpmfusion-repositories` and opt-in `rpmfusion` profile implement
a dedicated handler, separate from ordinary Fedora `dnf-package` actions.
Its opt-in profile first installs Fedora's signed `distribution-gpg-keys`
package as a persistent one-way prerequisite, updating that key package
from Fedora if either Fedora 44 key is missing. The handler verifies the exact
Fedora 44 release packages against Fedora-packaged keys in a temporary
filesystem keyring, checks their metadata, and checks package-owned
repo files for `gpgcheck=1`. It records private ownership state and refuses
pre-existing release packages, repository files, and key files.

The inverse acts only on the exact two release packages RIDE installed,
verifies their owned files have not been modified, and refuses removal while
any installed package is signed with either RPM Fusion key. Focused mocked
tests exercise wrong digest or signature, unexpected key fingerprint, path
collision, partial pair installation, and marker rollback.
The disposable Fedora 44 Workstation pilot passed the pair install, repeat,
status, package verification, metadata refresh, one package installation from
each repository, signature key-ID checks, refusal while those packages
remain, their removal, and the release package inverse. It also preserved
Fedora's pre-existing filtered repos and unrelated repo/key sentinels. The
published release RPMs set `gpgcheck=1` and `repo_gpgcheck=0`; the evidence
covers repository availability and package signature enforcement, not signed
repository metadata. Downstream package installs remain separate from the
RPM Fusion operation and base profiles.

The implementation and target lifecycle are accepted for Fedora 44 Workstation
x86_64. The upstream `repo_gpgcheck=0` behavior is disclosed; RPM package
signatures remain enforced with `gpgcheck=1`. Keep repository enablement
opt-in. See the [lifecycle acceptance record](../acceptance/setting.rpmfusion-repositories.md).
