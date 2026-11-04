# `package.open-vm-tools` acceptance

Status: **PASS; operable opt-in candidate on Fedora 44 Workstation x86_64**,
2026-11-01.

The operation manages Fedora's signed `open-vm-tools` RPM package presence
only. It does not detect a VMware hypervisor, configure services or user data,
or claim VMware integration based on a QEMU VM. Fedora Server package
acceptance is recorded in `generic-server-required.md`.

The shared guest-tools Workstation test removed the image-seeded VMware RPM
pair in a disposable overlay because `open-vm-tools-desktop` depends on the
core `open-vm-tools` RPM. It then verified the candidate gate, absent-state
install, RPM presence, repeat, status, and exact remove-new-install recovery
through the explicit `fedora-vmware-guest-tools` profile. QEMU and VMware
profiles stay separate.

Exact target: Fedora 44 Workstation x86_64, image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
Transcript: `.acceptance-runs/legacy-vm/.tmp-vm-acceptance-publisher-07-guest-tools-final/fedora-44-workstation-x86_64/20261101T171653Z-test-guest-tools-profiles-install-repeat-status-remove-78d5f2b8/transcript.jsonl`, SHA-256
`52781b84d429993906072e4a22cc16c2b74215f447a23b2cb43df75c7ae74994`.
