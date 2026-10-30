# Bitwarden desktop RPM outcome

Status: **unsupported and non-runnable in v3.0**, 2026-10-30. This
isolated high-risk v2 source outcome maps `InstallBitwarden` and
`RemoveBitwarden`. v2 scrapes the latest GitHub release for the first RPM
URL and passes it directly to DNF; its inverse removes `bitwarden` by name.
The publisher [offers Linux desktop distributions](https://bitwarden.com/download/);
its [client source](https://github.com/bitwarden/clients) is GPL-3.0 by
default with a separately licensed component directory. The v2 method does
not pin an artifact, verify its origin, or establish
how an existing desktop install and encrypted local vault survive recovery.

## Completion criteria defined before a runnable successor

- Select an exact publisher RPM, license/terms, hash/signature, and installed
  deployment identity distinct from the v2 `BitwardenAppImage` outcome.
- Preserve any existing Bitwarden package, browser extension, local vault,
  application configuration, and other publisher packages. Mock collision,
  interrupted download, and failure recovery without logging secret data.
- On a disposable Fedora 44 x86_64 Workstation VM with seeded non-secret
  vault fixtures, verify plan/apply/repeat/status and owned inverse. Require
  the deeper data/credential recovery evidence before making it runnable;
  an opt-in candidate cannot waive this gate.

No v3 external-RPM handler or vault-preserving inverse currently meets those
checks. Reopen for a requested pinned publisher RPM and complete recovery
evidence. This source outcome is separate from the
[portable AppImage decision](publisher-apps-06.md).
