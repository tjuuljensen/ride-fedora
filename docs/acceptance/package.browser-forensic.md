# `package.browser-forensic` Fedora 44 acceptance

Status: **passed; operable opt-in candidate**, 2026-11-02. The current source pin is browser-
forensic commit `10e2f70bd53d50144edcff849749efd0095c9a03`, archive SHA-256
`0493a03c0564a712a536fdd345c3eefec561c3ffd040f4ecc776ecdec398649c`, version
`0.3.0`, Apache-2.0. Its Cargo lockfile is part of that source archive.

The system-scoped `fedora-rust-build-tools` profile manages Fedora's signed
Cargo/Rust RPMs. Apply it with `sudo` and `--allow-candidate` while the Cargo
operation is under acceptance. The user-scoped `fedora-browser-forensics`
profile builds and owns only `br4n6`; apply it as the intended user with
`--allow-candidate`. Neither profile belongs in a base profile.

The disposable Fedora 44 Workstation x86_64 acceptance must verify both
candidate gates, the signed Cargo RPM transaction, pinned source digest, locked
release build, installed CLI version, seeded history/bookmark/cookie parsing,
and unchanged hashes for all seeded profile databases. The login check uses
only the synthetic credentials bundled in the pinned upstream test fixture; it
must show that passwords do not reach stdout and that an explicitly requested
secret file is mode 0600. Since upstream creates that file using the process
umask, invoke secret reveal under `umask 077`. No real browser profile is read.

The VM run covered repeat, status, active restore, a second install and active explicit remove, and preservation of fixture data. The focused mocked tests cover bad source bytes,
download/build failures, occupied destinations, and refusal to remove
unowned files. Broader browser coverage and recovery remain outside this
package-presence contract and are listed for v3.1 review.


## Fedora 44 Workstation result

The disposable target passed in run `20261102T200204Z-test-browser-forensic-pinned-build-and-read-only-firefox-analysis-b8cba6b0` with **1 passed in 6740.00 seconds (1:52:20)**. The target was Fedora 44 Workstation x86_64; image SHA-256 was `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`. The VM used TCG because KVM was unavailable. The recorded catalog SHA-256 was `e15bbe0ad98606de0343b9e314fc59be631d55c88d05176a5de44a46c349f2ff`; the run's source bundle was uncommitted, so this evidence is tied to its recorded source revision and bundle metadata rather than a release commit.

The build compiled the pinned CLI with `cargo build --locked --release`; both restore and explicit remove removed only RIDE-owned files, and seeded Firefox database hashes remained unchanged. The synthetic login fixture confirmed plaintext was absent from stdout and the requested output was mode 0600. The signed Cargo lifecycle also passed and returned the clean image to its original package baseline. Full command records and target provenance are retained in the adjacent `transcript.jsonl` and `metadata.json`.

Safety-domain review for this package-only operation: `private-output-boundary` (passwords were absent from stdout and the explicit file was mode 0600), `no-evidence-processing` during RIDE installation/removal, and `exact-output-preservation` (the seeded SQLite inputs retained their original hashes). The CLI analysis was invoked only on synthetic fixtures.
