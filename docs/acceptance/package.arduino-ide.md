# Arduino IDE 2.3.10 acceptance

`package.arduino-ide` is a Fedora 44 Workstation x86_64 opt-in candidate. It
installs Arduino IDE's publisher AppImage under `~/Applications` with a
private RIDE manifest. The manifest and AppImage are removed only when both
still match the pinned operation. Existing sketches, board configuration,
USB permissions, and uploads are outside the operation.

Acceptance checks the published GitHub release API SHA-256, ELF/AppImage
runtime probe, plan, candidate gate, apply, repeat, status, restore, explicit
remove, and preservation of a seeded sketch. The app GUI and USB board upload
are not exercised by this package lifecycle check; those remain v3.1 coverage.

Completion evidence: `test_arduino_ide_private_appimage_lifecycle` passed on
2026-11-01 against Fedora 44 Workstation x86_64 using TCG and image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
The transcript is
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-publisher-apps-10-arduino-joplin/fedora-44-workstation-x86_64/20261101T190813Z-test-arduino-ide-private-appimage-lifecycle-341e1cbe/transcript.jsonl`
(SHA-256 `4396c9c50cd944488335ac9c4284a866fc3689303d38df2ce5d61e42d0ae7744`).
The checked catalog SHA-256 was
`87b9894d56f5661e589b24cf97b6bdbc80496602076cf5dbdddf015a374fbd83`.

The covered catalog ID is `package.arduino-ide`.
