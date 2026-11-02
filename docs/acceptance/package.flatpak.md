# `package.flatpak` acceptance

Status: **PASS; supported** on Fedora 44 Workstation x86_64, 2026-10-31.
Product: Fedora Flatpak RPM, installed deployment, `fedora-rpm` source, system
scope. The operation exposes only `installed` and declares `recovery: none`;
it does not remove Flatpak, applications, remotes, runtimes, or user data.
Fedora's [Flatpak package record](https://packages.fedoraproject.org/pkgs/flatpak/flatpak/)
lists the Fedora 44 build and LGPL-2.1-or-later license. The final acceptance
installed `flatpak-1.18.4-1.fc44` from Fedora Updates and upgraded its matching
`flatpak-selinux` and `flatpak-session-helper` RPMs.

| Exact target | Outcome and evidence |
| --- | --- |
| Fedora 44 Workstation x86_64, `VARIANT_ID=workstation` | PASS: image SHA-256 `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`; candidate lifecycle overlay `20261031T022650Z-test-flatpak-runtime-install-only-preserves-remotes-and-user-data-a2e516c1`; supported-status profile smoke overlay `20261031T023725Z-test-flatpak-runtime-install-only-preserves-remotes-and-user-data-501ec020`; [batch record](../migrations/provider-foundation-11.md). |

The disposable VM acceptance scenario seeded a user Flathub remote, retained the Fedora OCI
system remote, and wrote a user-data sentinel with mode `0600` under
`~/.var/app`. It compared remote-configuration hashes and sentinel content,
owner, and mode across a package-absent state. `rpm -e --nodeps flatpak` was
used only to prepare that state in the disposable overlay; this is not a RIDE
removal path. The RIDE profile plan succeeded, candidate apply was refused
without `--allow-candidate`, and the explicitly allowed apply installed the
signed Fedora RPM. `rpm -V flatpak`, status, and repeat apply passed. Restore
and explicit remove refused because no inverse is declared. After install,
both remote listings, all app listings, and the sentinel's hash and metadata
matched the seeded values. No Flatpak application was installed; app lifecycle
and per-app recovery remain in hardening item H033.

The earlier preparation attempt applied `dnf remove flatpak` in a disposable
overlay and removed 21 packages, including GNOME Software and the Fedora
Flathub remote. That overlay was stopped and retained as failure evidence.
The host and pinned base image were unchanged. This is why RIDE intentionally
has no removal state for this operation.

The candidate lifecycle run took 538.57 seconds. After promotion, a second
run using the supported catalog row applied the profile without
`--allow-candidate`, repeated apply unchanged, verified status, and confirmed
restore and remove refusal; it passed in 463.98 seconds. Its catalog SHA-256
was `8efca8e2ec3f5f5b63e2bf5a80af22bdf1e46eedfd5ad7f53bd325048c1d34dc` and
source bundle SHA-256 was
`eabbf69fa7ca302fd3ebb4cb60df8a8e2e49cef7475b9c1877898b40e15e6297`. Both
runs used source revision `9da0526d412343076d6327c6cb3c5331be6d773a` with
uncommitted source changes. Their transcripts are under
`.acceptance-runs/provider-foundation-11-final/` and
`.acceptance-runs/provider-foundation-11-supported/`; JUnit reports are at
`.acceptance-runs/provider-foundation-11-final.xml` and
`.acceptance-runs/provider-foundation-11-supported.xml`. DNF reported transient
timeouts against one mirror, then completed through Fedora repositories;
signature verification and `rpm -V` passed. This result covers only the
declared Fedora 44 Workstation target.

The first full passing test ran with the worktree uncommitted at source revision
`9da0526d412343076d6327c6cb3c5331be6d773a`; source bundle SHA-256 was
`616f673ae8b0a31627555ee410316f7ec9ea71c4346afc8c1b45d14fe257fe9e` and the
catalog SHA-256 was
`8974ab1802d2a247953a64a1d4ee385b0fd8665428eceeac05f4e0425c40e1b2`.
