# RPM Fusion repository lifecycle

Status: **PASS — supported for Fedora 44 Workstation x86_64; repository profile remains opt-in**.

The Fedora-packaged RPM Fusion signing keys verified the exact Fedora 44 free
and nonfree `44-3` release RPMs in a disposable Fedora 44 Workstation x86_64
VM. That bootstrap trust evidence is recorded in
[`rpmfusion-bootstrap-trust.md`](rpmfusion-bootstrap-trust.md).

The supported operation is `setting.rpmfusion-repositories`. Its opt-in
`rpmfusion` profile first ensures Fedora's `distribution-gpg-keys` package is
installed as a persistent one-way prerequisite. The handler resolves the
versioned key files inside Fedora's package-owned key directory, verifies the
RPM package integrity and pinned key fingerprints, imports the keys into an
isolated RPM 6 filesystem keyring, checks the two exact release RPM signatures
and metadata, installs the pair with DNF5, verifies the package-owned repo
files specify `gpgcheck=1`, and records a private ownership marker. Removal
checks package signatures and refuses while other installed RPMs use either
RPM Fusion signing key.

Fedora Workstation ships filtered NVIDIA and Steam repository files in
`fedora-workstation-repositories`; the operation preserves them and refuses
only when a path listed by the release RPMs already exists. Fedora documents
the owning package and file list in its
[Fedora 44 package record](https://packages.fedoraproject.org/pkgs/fedora-workstation-repositories/fedora-workstation-repositories/fedora-44.html).

The [RPM 6 configuration reference](https://rpm.org/docs/6.0.x/man/rpm-config.5)
documents the filesystem keyring backend. It avoids importing RPM Fusion
trust into the host RPM keyring or creating a temporary RPM database, which
Fedora's SELinux policy rejected in an earlier probe.

The disposable lifecycle test passes install, `rpm -V`, declared repo
`gpgcheck=1`, DNF5 metadata refresh, repeat, status, and inverse. It installs
`redumper` from `rpmfusion-free-updates` and `unrar` from
`rpmfusion-nonfree-updates`, verifies their RPM header key IDs, proves removal
is refused while those signed packages remain, removes them, and then removes
the release packages. Fedora's filtered repos and unrelated repo/key
sentinels remain intact. The release RPMs set `repo_gpgcheck=0`; package
signatures are enforced with `gpgcheck=1`, and separate metadata-signature
verification is therefore not claimed. This is the tested upstream
configuration and is recorded as the v3.0 trust boundary.

Focused failure tests also pass for an invalid release RPM signature, a
payload digest mismatch, path collisions, package transaction rollback, and
ownership-marker write failure with rollback of both release packages. The
inverse dependency check refuses removal while packages signed by either RPM
Fusion key remain. This evidence supports the exact Fedora 44 Workstation
target; it does not establish another Fedora release, edition, or architecture.

| Field | Evidence |
| --- | --- |
| Target | Fedora 44 Workstation x86_64 |
| Image | SHA-256 `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a` |
| Bootstrap trust probe | `tests/acceptance/test_rpmfusion_trust_probe.py` |
| Lifecycle test | `tests/acceptance/test_rpmfusion_repositories.py`; 1 passed in 462.35 seconds using TCG |
| VM run | `20261031T040628Z-test-rpmfusion-repository-install-repeat-metadata-and-inverse-0dad48a6` |
| Transcript | `/tmp/ride-rpmfusion-lifecycle-7/fedora-44-workstation-x86_64/20261031T040628Z-test-rpmfusion-repository-install-repeat-metadata-and-inverse-0dad48a6/transcript.jsonl` |
| Result | Install/repeat/status, package signatures from free and nonfree, dependency refusal, inverse, state preservation, and focused signature/digest/collision/rollback failure checks passed |
| Focused unit tests | `tests.test_v3_rpmfusion`; 10 passed |
