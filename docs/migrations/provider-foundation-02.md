# Provider foundation batch 02: RPM Fusion repository enablement

Status: **assessed; high-risk trust and recovery design pending**, 2026-10-30.
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
