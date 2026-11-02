# Bitwarden desktop RPM outcome

The owner kept the RPM option alongside the AppImage and, where available,
Flatpak options in the v3.0 fast-track review. These need separate deployment
identities, feature review, product-specific coexistence, and vault-safe
recovery. The RPM has a pinned v3 path and remains a candidate until its
vault-preserving Fedora 44 acceptance passes.

Status: **supported on Fedora 44 Workstation x86_64**, 2026-11-01. This
isolated high-risk v2 source outcome maps `InstallBitwarden` and
`RemoveBitwarden`. v2 scrapes the latest GitHub release for the first RPM
URL and passes it directly to DNF; its inverse removes `bitwarden` by name.
The publisher's signed
[`desktop-v2026.10.1` release](https://github.com/bitwarden/clients/releases/tag/desktop-v2026.10.1)
includes the x86_64 RPM with GitHub-published asset SHA-256
`2aa3b7a675432bef75e73f513ba365b055a8c16ec2a42610f019f4b6f7d0a61b`.
The release has no detached RPM signature; v3 checks that pinned digest and
the exact RPM name, version, and architecture before DNF installs it.
Bitwarden's source is GPL-3.0 by default with separately licensed components.

## Completion criteria defined before a runnable successor

- Pin the official publisher RPM, release tag, SHA-256, license, package
  identity, and Fedora 44 x86_64 target. Keep system RPM and portable AppImage
  deployments separately owned and permit coexistence.
- Preserve any existing Bitwarden package, browser extension, local vault,
  application configuration, and other publisher packages. Mock collision,
  interrupted download, and failure recovery without logging secret data.
- On a disposable Fedora 44 x86_64 Workstation VM with seeded non-secret
  vault fixtures, verify plan/apply/repeat/status and owned inverse. Require
  the deeper data/credential recovery evidence before making it runnable;
  an opt-in candidate cannot waive this gate.

The new `package.bitwarden-rpm` operation downloads only the pinned asset to a
temporary file, checks its digest and RPM identity, then uses DNF with Fedora
repositories available for dependencies. It does not read or write vault
data. The candidate profile is opt-in and separate from the
[portable AppImage](publisher-apps-06.md). Pending: mocked failure and cleanup
tests plus disposable Fedora 44 Workstation acceptance that installs both
deployments, repeats and removes the RPM, and preserves a synthetic vault
sentinel and the AppImage file throughout. That lifecycle passed on the
pinned Fedora 44 Workstation image. The transcript is recorded in the
[acceptance report](../acceptance/package.bitwarden-rpm.md); package updates
and wider desktop interaction remain separate reviews.
