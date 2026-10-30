# Provider foundation batch 02: RPM Fusion repository enablement

Status: **unsupported as a runnable v3.0 repository operation**, 2026-10-30.
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
signing keys. The availability of these files is source discovery, not
independent trust, package signature verification, or proof of owned recovery.
This is a third-party repository that changes future package acquisition;
the release RPM must not be treated as a normal Fedora-signed package. The
current v3 `dnf-package` handler assumes Fedora repository GPG verification
and does not establish an independent RPM Fusion trust root or own repository
configuration. No runnable v3 operation is declared for this outcome yet.

## Completion criteria defined before implementation

- Identify independent, current free and nonfree signing-key fingerprints,
  pinned Fedora 44 release RPM URLs, package licenses, and exact files those
  RPMs own. Reject a release RPM or repository definition with an unexpected
  publisher, disabled `gpgcheck`, or a changed URL/key.
- Model free and nonfree repositories as separate owned operations or a
  reviewed atomic bundle. Detect pre-existing release packages, repo files,
  and key state before apply. Never delete or replace unowned configuration.
- Exercise trusted acquisition, signature failure, partial install, repeat,
  status, and restore in focused mocked checks. In a disposable Fedora 44
  x86_64 Workstation VM, verify repository metadata and GPG enforcement,
  install and inverse, and preservation of prior repositories, keys, and
  packages. A failed run must be investigated before retrying.
- Promote to `supported` only after the high-risk trust and recovery evidence
  passes. If v3.0 cannot establish it, close this source outcome as a
  reasoned unsupported disposition with a review trigger; never use a
  runnable candidate or the v2 broad-deletion inverse to bypass the gate.
- Keep repository enablement out of `default` and `server-base`; downstream
  RPM Fusion package operations require their own source and VM evidence.

## v3.0 decision

The v2 pair changes future acquisition for the whole host, uses two external
release RPMs, and has a wildcard inverse that can delete another owner's
repository configuration and installed release packages. The current v3
catalog and DNF handler only model one installed Fedora RPM; they do not
pin and authenticate a third-party release RPM, distinguish a pre-existing
free or nonfree repository, journal its files and keys, or refuse an inverse
when packages still depend on that repository. No focused trust or recovery
test, or disposable-VM lifecycle, has been completed for a replacement
handler. A runnable candidate would bypass the high-risk gate in the
v3.0 migration plan.

`RPMfusionRepos` is therefore **unsupported as an operation in v3.0**.
No repository enablement or downstream RPM Fusion package is counted as
accepted. Reopen this decision if a concrete RPM Fusion application needs it
and a pinned independent key fingerprint, signed release-RPM check, owned
file/key journal, safe inverse, and exact-target VM evidence are available.
That follow-up should separate free and nonfree acquisition unless a reviewed
atomic bundle is needed. Existing independently installed repositories
remain outside RIDE ownership.
