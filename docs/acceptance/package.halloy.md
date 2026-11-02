# `package.halloy` acceptance

Status: **PASS; operable opt-in candidate on Fedora 44 Workstation x86_64**.

The operation installs the exact `org.squidowl.halloy` system Flatpak ref from
`flathub`. It requires one system remote named `flathub` at
`https://dl.flathub.org/repo/` with GPG verification enabled. It refuses a
Halloy ref from another origin. The operation is opt-in and requires the
separate `flathub-system` profile or an equivalent trusted system remote to be
configured first.

Halloy upstream is active and declares GPL-3.0-or-later. Its current upstream
release is 2026.9. The initial Flathub page crawl showed 2026.8, while the
disposable VM fetched Flathub's 2026.9 build (commit
`3c64c274585899847ba504fd312b0aafae58a729ce18a34e583f82e776fa5d3d`), so
Flatpak updates determine the installed build. Sources: [upstream repository and
license](https://github.com/squidowl/halloy), [upstream releases](https://github.com/squidowl/halloy/releases),
and [Flathub listing](https://flathub.org/en/apps/org.squidowl.halloy).

The completion checks are:

- Focused mocks cover absent/installed observation, first install, repeat,
  exact removal, wrong origin, missing or unverified remote, duplicate remote,
  command failure, and user-data preservation.
- A disposable Fedora 44 Workstation x86_64 run covers plan, candidate refusal,
  apply, repeat, status, and app removal. It verifies exactly one application
  ref with origin `flathub` and retains a user-data sentinel's contents and mode
  after app removal. Keep the remote installed because Flatpak may retain the
  shared runtime after removing the app.
- The run does not connect to an IRC server or migrate HexChat configuration.

The handler invokes `flatpak uninstall` without `--delete-data`. User-owned
configuration and history under `~/.var/app/org.squidowl.halloy` therefore
remain outside RIDE's removal boundary. Halloy and the existing HexChat RPM
have separate deployment identities and can coexist. Broader visual checks and
configuration import remain follow-up hardening, not install-path blockers.

The first VM attempt installed the ref but exposed that Flatpak 1.18 reports
the JSON application ID as `application_id`. The retained transcript and
follow-up inventory established the cause; the handler now accepts that field
and a compatibility `application` field. The corrected lifecycle then passed:
the system ref listed with origin `flathub`, apply repeated unchanged, status
reported installed, removal removed only Halloy, and the sentinel hash and
`ride-test` owner/mode (`0600`) were unchanged. The remote and shared runtime
remain in the disposable guest.

Exact target: Fedora 44 Workstation x86_64, image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
Acceptance transcript:
`/tmp/ride-fedora-halloy-01/fedora-44-workstation-x86_64/20261031T085517Z-test-halloy-flatpak-app-lifecycle-preserves-user-data-73e3484a/transcript.jsonl`.
The app apply run is `20261031T085547Z-3123-19273`; the no-change repeat is
`20261031T085609Z-3677-20918`; removal is `20261031T085609Z-3898-10897`.
The separate remote setup run is `20261031T085546Z-2521-23954`. Source revision
was `9da0526d412343076d6327c6cb3c5331be6d773a` with uncommitted migration
changes; the bundled source SHA-256 is recorded in adjacent `metadata.json`.
The legacy `package.hexchat` RPM remains a separate, previously accepted
deployment.
