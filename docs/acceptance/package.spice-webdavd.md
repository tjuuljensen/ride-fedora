# `package.spice-webdavd` acceptance

Status: **PASS; operable opt-in candidate on Fedora 44 Workstation x86_64**,
2026-11-01.

Fedora 44 publishes the signed `spice-webdavd` RPM. The operation manages
package presence only, selected explicitly through `fedora-qemu-guest-tools`;
it does not configure host-side WebDAV sharing or claim data-transfer behavior.

The shared guest-tools Workstation test removed the image-seeded RPMs in a
disposable overlay, then verified the candidate gate, absent-state install,
RPM presence, repeat, status, and exact remove-new-install recovery for both
explicit guest-tool profiles. It did not mount host shares or alter user data.

Exact target: Fedora 44 Workstation x86_64, image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
Transcript: `.acceptance-runs/legacy-vm/.tmp-vm-acceptance-publisher-07-guest-tools-final/fedora-44-workstation-x86_64/20261101T171653Z-test-guest-tools-profiles-install-repeat-status-remove-78d5f2b8/transcript.jsonl`, SHA-256
`52781b84d429993906072e4a22cc16c2b74215f447a23b2cb43df75c7ae74994`.
The RPM supplies WebDAV integration components; this operation does not mount
shares or verify host-side transfer behavior.
