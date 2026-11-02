# Bitwarden AppImage source outcome

The owner confirmed **keep** in the v3.0 fast-track review, alongside RPM and
Flatpak distributions where available. Each needs its own deployment identity,
feature review, and vault-safe inverse; coexistence is reviewed per product.
[Bitwarden's Linux feature matrix](https://bitwarden.com/help/desktop-app-feature-support/)
lists AppImage, Flatpak, and RPM with differing integration features.

Status: **supported on Fedora 44 Workstation x86_64**,
2026-11-01. The owner chose to keep a real portable Bitwarden AppImage as a
distinct outcome.
This isolated high-risk
active-preset outcome maps `InstallBitwardenAppImage` and
`RemoveBitwardenAppImage`. The v2 function requests a mutable GitHub release,
filters for an RPM URL despite its AppImage name, and saves that RPM under
`~/Applications`. The inverse removes `Bitwarden*.AppImage` instead, so it
cannot reliably undo what it downloaded. User vaults and an existing
`~/Applications` directory are not journaled.

## Completion criteria defined before implementation

- Pin the official publisher AppImage release and its manifest, verify the
  published SHA-512 before placement, record the license and notices.
  Distinguish its portable deployment from the separately scoped v2
  `Bitwarden` RPM outcome.
- Preserve any existing AppImage, desktop integration, local encrypted
  vault, browser extension state, and application configuration. Mock
  collision and interrupted downloads. In a disposable Fedora 44 x86_64
  Workstation VM, verify a seeded-vault-safe plan/apply/repeat/status and
  inverse, with no secret contents in logs.
- Require the deeper credential/data recovery evidence before runnable
  status; an opt-in candidate cannot waive it.

[Bitwarden's download page](https://bitwarden.com/download/) publishes Linux
desktop applications. The signed GitHub release tag is
[`desktop-v2026.10.1`](https://github.com/bitwarden/clients/releases/tag/desktop-v2026.10.1);
its official [`latest-linux.yml`](https://github.com/bitwarden/clients/releases/download/desktop-v2026.10.1/latest-linux.yml)
pins the AppImage SHA-512 as
`Nd2GYFve1jSZ7ba3rAlZqRltN4UBzJAOTNuquAK93kiZuWOKagJZBstZ4ocXKeB3LNdbLmbiHZISQht5pQw/ug==`.
The manifest SHA-256 is
`995c06dcb33b8f7d63468840f1edc245447975ac20b81aeb5258c78d2aaa6aa7`.
Bitwarden's tagged [`LICENSE.txt`](https://github.com/bitwarden/clients/blob/desktop-v2026.10.1/LICENSE.txt)
sets GPL v3.0 as the repository default and identifies separately licensed
components.

The new `package.bitwarden-appimage` operation places only the pinned
executable at `~/Applications/Bitwarden-2026.10.1-x86_64.AppImage`. It records
that file in a RIDE-owned manifest and refuses collisions or modified files.
It does not create desktop integration, alter Bitwarden's profile, inspect
vault contents, or remove the separate Bitwarden RPM. The high-risk operation
passed Fedora 44 Workstation acceptance for the synthetic vault/profile
sentinel, exact file inverse, and absence of secret data in transcripts. It is
supported only for this user-scoped file placement lifecycle; it does not
launch the app or inspect account data. The RPM outcome remains independently tracked in
publisher-apps-12.

The accepted supported-path transcript is [transcript.jsonl](../../.tmp-vm-acceptance-publisher-06-supported/fedora-44-workstation-x86_64/20261101T163802Z-test-bitwarden-appimage-lifecycle-preserves-vault-files-79623341/transcript.jsonl)
(SHA-256 `07031bcc0b334f6f6bb0b13daa7585c302edfa7182d824520a0b1464a1036653`)
on the pinned image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
