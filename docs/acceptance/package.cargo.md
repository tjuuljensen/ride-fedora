# `package.cargo` Fedora 44 acceptance

Status: **passed as a Fedora 44 Workstation x86_64 prerequisite**, 2026-11-02. Fedora's signed `cargo` RPM supplies
Cargo and the Rust compiler for opt-in Rust source builds. The managed
`fedora-rust-build-tools` profile is system-scoped and must be applied with
`sudo`; the user-scoped application profile is applied separately by the
intended account. Cargo is not added to a base profile.

Acceptance is recorded with [the browser-forensic source build](package.browser-forensic.md),
which depends on this runtime. It checks initial absence, candidate gating,
Fedora 44 x86_64 RPM signature and file verification, version output, repeat,
status, restore, and removal of only RIDE-installed packages. Any pre-existing
Cargo/Rust packages must remain installed after restore and remove.


The browser-forensic acceptance run verified the signed Fedora Cargo/Rust package transaction, `cargo --version`, `rustc --version`, package file integrity, and removal of the newly introduced toolchain and dependencies after the dependent CLI lifecycle. The exact image and transcript are recorded in [browser-forensic acceptance](package.browser-forensic.md). TCG execution made the pinned source build take about 52 minutes per install; package lifecycle evidence is valid for the declared target, but future runs should avoid repeating an unchanged source build when the same owned-inverse behavior is already covered.
