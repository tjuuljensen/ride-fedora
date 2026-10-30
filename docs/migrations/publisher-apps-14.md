# YubiKey Personalization GUI handoff

Status: **documented non-runnable replacement for v3.0**, 2026-10-30.
This isolated high-risk commented-preset outcome maps only
`InstallYubikeyPersTool`; v2 clones an unpinned source into `/opt`, installs
Qt4 and YubiKey development dependencies, and builds without a matching
remove function. The [publisher repository](https://github.com/Yubico/yubikey-personalization-gui)
is archived, licensed BSD-2-Clause, and directs users to YubiKey Manager
CLI or Yubico Authenticator. It can change hardware credentials.

## Completion criteria defined before a runnable successor

- Select a current publisher-supported product and exact source, license,
  artifact, destination, and installed identity. Keep device configuration
  outside package apply and require explicit user action for credential
  changes.
- Prove that collision and inverse preserve an existing YubiKey tool,
  credentials, and unrelated `/opt` content; test failure recovery and a
  disposable Fedora 44 x86_64 VM package lifecycle. Hardware mutation needs
  separate controlled evidence before any such action is offered.

The archived Qt4 source build is retired in favor of a documented Yubico
Authenticator or `ykman` choice. This is **not a v3 managed install**. Reopen
for a requested current deployment with owned package/portable recovery and
device-safe evidence. See also the distinct
[YubiKey Manager GUI outcome](publisher-apps-08.md).
