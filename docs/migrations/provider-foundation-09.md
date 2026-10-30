# Flathub remote ownership and recovery

Status: **separated for scoped provider review**, 2026-10-30.
The active v2 `InstallFlathub` calls `flatpak remote-add --if-not-exists`
against a Flathub `.flatpakrepo` URL; `RemoveFlathub` calls `flatpak uninstall
flathub`, which does not express a safe inverse for a remote created by
another owner. Flatpak distinguishes user and system installations. Its
[current documentation](https://docs.flatpak.org/en/latest/using-flatpak.html)
describes the stable Flathub `.flatpakrepo` source, bundled GPG key, and
`remote-delete` inverse. RIDE must select a fixed scope and preserve any
pre-existing remote, apps, and configuration.

Before implementation, define detection for exact remote URL, scope, and
GPG verification; a journaled apply and inverse that only removes a remote
RIDE created; and refusal if attached applications or a changed remote would
make removal unsafe. Use focused mocked failure tests and a disposable Fedora
44 x86_64 Workstation VM happy path, with deeper recovery evidence before
declaring a repository source supported. Keep this source out of base profiles.
