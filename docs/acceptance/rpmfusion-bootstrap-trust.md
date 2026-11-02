# RPM Fusion bootstrap signature evidence

Status: **PASS for bootstrap key trust only** on Fedora 44 Workstation x86_64,
2026-10-31. This is not acceptance of repository installation, package
transactions from RPM Fusion, or recovery.

The disposable VM test downloaded the exact Fedora 44 `44-3` free and
nonfree release RPMs over HTTPS. The installed Fedora
`distribution-gpg-keys-1.118-1.fc44` package supplied the expected keys:

| Package | License | Fedora-packaged key fingerprint | RPM check |
| --- | --- | --- | --- |
| `rpmfusion-free-release 44-3` | BSD | `E9A491A3DE247814E7E067EAE06F8ECDD651FF2E` | Header signature and SHA-256 payload digest passed |
| `rpmfusion-nonfree-release 44-3` | BSD | `79BDB88F9BBF73910FD4095B6A2AF96194843C65` | Header signature and SHA-256 payload digest passed |

Each RPM lists six signing-key paths under `/etc/pki/rpm-gpg` and three
repository files under `/etc/yum.repos.d`. The Fedora-distributed keys matched
the RPM header fingerprints. The test imported each key only into the
disposable guest RPM keyring, then `rpm --checksig --verbose` reported the
signature, header digest, and payload digest as valid. RPM Fusion repo
metadata, exact `gpgcheck` defaults, ownership conflicts, and inverse safety
were not exercised by this probe.

| Field | Evidence |
| --- | --- |
| Target | Fedora 44 Workstation x86_64, `VARIANT_ID=workstation` |
| Image | SHA-256 `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a` |
| Test | `tests/acceptance/test_rpmfusion_trust_probe.py`; 1 passed in 142.16 seconds using TCG |
| VM run | `20261031T033120Z-test-rpmfusion-release-rpms-verify-with-fedora-packaged-keys-f1b3dc9f` |
| JUnit | `/tmp/ride-rpmfusion-probe/results-verified.xml` |
| Transcript and metadata | `/tmp/ride-rpmfusion-probe/fedora-44-workstation-x86_64/20261031T033120Z-test-rpmfusion-release-rpms-verify-with-fedora-packaged-keys-f1b3dc9f/` |
| Catalog | SHA-256 `4248aada020c28f4dbcffce87c0d234cc39f898a2cc816ced23fcc07cc996768` |
| Source bundle | SHA-256 `8611e63d14562323025a4686561de3d6b566c447bcfa52286c50657a050f68d1` |

The VM runner stopped the guest after the probe. Its temporary RPM key imports
were not made on the host. Continue with an opt-in owned operation, repository
metadata and GPG checks, preservation of existing state, and package-aware
inverse tests.
