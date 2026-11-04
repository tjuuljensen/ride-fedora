# `package.balena-etcher` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64, 2026-11-01.

The operation uses the exact balenaEtcher 2.1.9 x86_64 RPM and the SHA-256
published on its GitHub release. It checks downloaded bytes and RPM identity,
then relies on DNF for package lifecycle. RIDE installs the desktop software
only; acceptance does not launch Etcher or connect/write removable media.
User settings and removable media are outside the package removal path.

- [balenaEtcher v2.1.9 release and RPM digest](https://github.com/balena-io/etcher/releases/tag/v2.1.9)
- [balenaEtcher source and license](https://github.com/balena-io/etcher)

The disposable guest passed candidate refusal, plan, pinned download verification, RPM identity check, install, RPM file listing, status, unchanged repeat, and removal. Image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`. Transcript: `.acceptance-runs/legacy-vm/.tmp-vm-acceptance-publisher-apps-09/fedora-44-workstation-x86_64/20261101T175834Z-test-pinned-publisher-rpm-lifecycle-fedora-balena-etcher-package-balena-etcher-b-29f456a7/transcript.jsonl`, SHA-256 `2c8d0206051f29571f84bf07108c21a5dcdefa89da4e3e6d010cb551fd6da84d`. The catalog used in that run had SHA-256 `5da5556ef6b7d821b07b84dbb54d0117ce6b639415c35a7b5959bdd23af5e283`. TCG emulation was used; Etcher was not launched and no removable media was attached or written.
