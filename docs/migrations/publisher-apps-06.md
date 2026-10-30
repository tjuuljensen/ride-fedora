# Bitwarden AppImage source outcome

The owner confirmed **keep** in the v3.0 fast-track review, alongside RPM and
Flatpak distributions where available. Each needs its own deployment identity,
feature review, and vault-safe inverse; coexistence is reviewed per product.
[Bitwarden's Linux feature matrix](https://bitwarden.com/help/desktop-app-feature-support/)
lists AppImage, Flatpak, and RPM with differing integration features.

Status: **retained for migration, unsupported for v3.0**, 2026-10-30. The
owner chose to keep a real portable Bitwarden AppImage as a distinct outcome.
This isolated high-risk
active-preset outcome maps `InstallBitwardenAppImage` and
`RemoveBitwardenAppImage`. The v2 function requests a mutable GitHub release,
filters for an RPM URL despite its AppImage name, and saves that RPM under
`~/Applications`. The inverse removes `Bitwarden*.AppImage` instead, so it
cannot reliably undo what it downloaded. User vaults and an existing
`~/Applications` directory are not journaled.

## Completion criteria defined before a runnable operation

- Choose the actual publisher AppImage distribution and pin the exact
  release, hash, signature or publisher verification, license, and notices.
  Distinguish its portable deployment from the separately scoped v2
  `Bitwarden` RPM outcome.
- Preserve any existing AppImage, desktop integration, local encrypted
  vault, browser extension state, and application configuration. Mock
  collision and interrupted downloads. In a disposable Fedora 44 x86_64
  Workstation VM, verify a seeded-vault-safe plan/apply/repeat/status and
  inverse, with no secret contents in logs.
- Require the deeper credential/data recovery evidence before runnable
  status; an opt-in candidate cannot waive it.

[Bitwarden's Linux downloads](https://bitwarden.com/download/) provide
desktop distributions; its [client source](https://github.com/bitwarden/clients)
is GPL-3.0 by default with separately licensed components. The v2 RPM/AppImage mismatch is not a safe
portable lifecycle and v3 has no owned portable handler. This is a
**non-runnable unsupported v3.0 decision**. The next batch should design
the official AppImage acquisition with pinned publisher bytes, separate
deployment identity, and vault-preserving VM evidence. The v2 `Bitwarden`
RPM outcome remains independently tracked in publisher-apps-12.
