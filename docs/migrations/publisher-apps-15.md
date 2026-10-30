# Xmind desktop RPM outcome

Status: **unsupported and non-runnable in v3.0**, 2026-10-30. This
v2 source outcome maps `InstallXmind` and `RemoveXmind`. v2 scrapes
an old `/zen/download/linux_rpm/` endpoint, passes every extracted link to
DNF, then removes `xmind-vana` by name. The
[publisher still offers a Linux RPM](https://xmind.app/xmind2024/) under its
[desktop terms](https://xmind.app/mas/terms/), but the
v2 URL and package name do not identify the current release or an owned
inverse. Mind maps and application settings are user data.

## Completion criteria defined before a runnable operation

- Select a current publisher product/edition and exact RPM, terms, hash or
  signature, and installed package identity. Detect existing installations
  and preserve document files and application state.
- Mock collision and failed acquisition; verify a Fedora 44 x86_64
  Workstation VM plan/apply/repeat/status and owned inverse. A desktop
  happy path may remain opt-in candidate while visual checks move to v3.1.

The current catalog has no pinned publisher-RPM acquisition and recovery
handler. Choose an Xmind edition with verified artifact,
owned install, and VM happy path.

The owner retained Xmind as an optional v3 outcome on 2026-10-30. Choose the
current edition and exact publisher artifact, then prove document-preserving
Fedora 44 recovery. The v2 Zen scrape and name-based inverse remain
non-runnable.
