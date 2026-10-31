# Flathub system remote acceptance

Status: **PASS as an opt-in candidate** on Fedora 44 x86_64 Workstation,
2026-10-31 UTC. `setting.flathub-system-remote` passed in disposable overlay
`20261031T020934Z-test-flathub-system-remote-owned-lifecycle-aab78f3c`
using the pinned image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a` and
catalog SHA-256
`b3e273a7cfef6c5959cc15cd5767088d6c973e9b6ae5bc3c70ad7034e6b03753`.

The candidate gate refused apply without `--allow-candidate`. With opt-in,
Flatpak imported the official `.flatpakrepo` key and added the system remote
at `https://dl.flathub.org/repo/` with GPG verification enabled. Repeat
reported unchanged; status reported configured. Restore and explicit profile
removal deleted only the RIDE-owned remote. The Fedora OCI system remote,
user remote inventory, and installed system application inventory were
identical before and after recovery. No application or runtime was installed.

Mocked tests cover repeat and exact removal, pre-existing remote refusal,
marker drift, attached-app refusal, and rollback if ownership recording
fails. The handler tracks ownership in a root-owned private marker under
`/var/lib/ride-fedora/owned-remotes/`; changed remote configuration or marker
state fails closed. Broader app behavior and RPM/Flatpak product coexistence
remain scoped to each application's migration.
