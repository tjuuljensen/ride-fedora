# YubiKey Manager GUI end-of-life handoff

Status: **documented non-runnable replacement for v3.0**, 2026-10-30.
This isolated high-risk active-preset outcome maps `InstallYubikeyManager`
and `RemoveYubikeyManager`. v2 scrapes a moving AppImage URL into
`~/Applications`; its inverse deletes matching names without a manifest or
proof that the file was RIDE-created. The application can change YubiKey
credentials and security settings, beyond a package install.

## Completion criteria defined before a runnable successor

- Choose a current publisher-supported application and distinguish its
  portable distribution, artifact hash/signature, license, and owned path.
- Prove that a v3 install/inverse preserves an existing application,
  `~/Applications`, and YubiKey credential state. Test collision and
  interrupted acquisition, then a disposable Fedora 44 x86_64 Workstation
  happy path. Any credential mutation requires separate hardware evidence
  and explicit user action; RIDE apply must not perform it.
- Require that high-risk ownership and recovery evidence before a runnable
  operation, even if the successor is opt-in.

[Yubico states](https://www.yubico.com/support/download/yubikey-manager/)
that YubiKey Manager GUI is no longer supported and recommends Yubico
Authenticator for GUI use; the `ykman` CLI remains available. The old GUI
AppImage should not be promoted merely by selecting a newer URL. This
source outcome is **replaced by a documented publisher-supported choice**,
not by a v3 managed install. Reopen for a requested Authenticator or
`ykman` deployment with pinned source, safe ownership, and target/hardware
evidence. Credential changes are outside this migration outcome.
