# `package.squashfs-tools` acceptance

Status: **VM PASS; supported** on Fedora 44 Workstation x86_64, 2026-11-04.
Risk tier: low-risk Fedora repository RPM. This separate root-scoped package
provides `/usr/bin/unsquashfs` for the user-scoped `package.tmog` operation.
It is selected only by the opt-in `fedora-tmog-runtime` profile.

The disposable KVM test used pinned Workstation image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`
and overlay `20261104T121044Z-test-tmog-appimage-lifecycle-preserves-user-data-eac3fe63`.
The candidate catalog SHA-256 was
`58f1460c25a8e9616fffa86a0423a6fdb45a1a7e6e8cc1b9002ef46489df8475`.
The transcript is
`.acceptance-runs/tmog-vm-20261104-r2/fedora-44-workstation-x86_64/20261104T121044Z-test-tmog-appimage-lifecycle-preserves-user-data-eac3fe63/transcript.jsonl`
(SHA-256 `5e2ad39385b1e56e402344a85b8dde8862a4dbd75c3f804b60d32a316187f649`);
JUnit: `.acceptance-runs/tmog-vm-20261104-r2.xml` (one test passed).
The run installed Fedora `squashfs-tools-4.6.1-8.fc44.x86_64`, found
`/usr/bin/unsquashfs` in that RPM, passed `rpm -V squashfs-tools`, then removed
the new RPM after TMOG's lifecycle. The final supported-state VM run used
fresh overlay
`20261104T121653Z-test-tmog-appimage-lifecycle-preserves-user-data-98311942`
and supported catalog SHA-256
`b9fda71c83860700feaf2de78ba579ea8a4f07e929d85674bb38506eecb837f1`.
Its transcript is
`.acceptance-runs/tmog-vm-20261104-supported/fedora-44-workstation-x86_64/20261104T121653Z-test-tmog-appimage-lifecycle-preserves-user-data-98311942/transcript.jsonl`
(SHA-256 `f1bf2d6df8a286ef8310bdeac074ac81bac0b1e4769a4b2299b133b12592ce03`);
JUnit `.acceptance-runs/tmog-vm-20261104-supported.xml` (one test passed).
It additionally checked plan, repeat apply, and status. DNF's signed Fedora repository path is
the unchanged `dnf-package` handler; failure-injection evidence is reused from
[base package acceptance](package.exfatprogs.md).

Reviewer: Codex, 2026-11-04. Scope is this pinned Workstation target only.
