# Flathub remote ownership and recovery

Status: **unsupported as a runnable v3.0 remote operation**, 2026-10-30.
The owner confirmed **keep** in the v3.0 fast-track review. Flatpak
applications may coexist with RPM editions of the same product after
product-specific conflict review, using separate deployment identities and
recovery. The Flathub remote has its own scope and inverse.
The active v2 `InstallFlathub` calls `flatpak remote-add --if-not-exists`
against a Flathub `.flatpakrepo` URL; `RemoveFlathub` calls `flatpak uninstall
flathub`, which does not express a safe inverse for a remote created by
another owner. Flatpak distinguishes user and system installations. Its
[current documentation](https://docs.flatpak.org/en/latest/using-flatpak.html)
describes the stable Flathub `.flatpakrepo` source, bundled GPG key, and
`remote-delete` inverse. RIDE must select a fixed scope and preserve any
pre-existing remote, apps, and configuration.

## Completion criteria defined before resolution

- Inspect the exact system and user remote state on the declared Fedora 44
  x86_64 Workstation VM. Select a fixed scope; do not adopt or overwrite a
  remote configured by another owner.
- For an opt-in candidate, require exact remote URL and GPG-verification
  detection, a journaled apply and inverse that remove only a RIDE-created
  remote, focused mocked failure checks, and a disposable-VM happy path.
  Refuse removal if attached applications or a changed remote make it unsafe.
- Otherwise record a non-runnable v3.0 result with a review trigger. Do not
  use the v2 `flatpak uninstall flathub` as an inverse or add Flathub to the
  base profiles.

## Fedora 44 inspection and v3.0 decision

In the pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`,
disposable overlay `provider-flatpak-snap-inventory`, read-only
`flatpak --system remotes --columns=name,url,options` showed only the
Fedora OCI remote. User remotes and installed system/user Flatpak apps were
empty. This establishes an absent Flathub baseline for that image, not an
install or inverse acceptance. The current
[Flathub Fedora setup](https://flathub.org/en/setup/Fedora) uses a
`.flatpakrepo` URL; its current documented host is `dl.flathub.org`, while
v2 used `flathub.org`. [Flatpak's documentation](https://docs.flatpak.org/en/latest/using-flatpak.html)
distinguishes system and user remotes and describes `remote-delete`.

The v3 catalog has no remote handler or journaled remote ownership, and the
v2 inverse is not a safe remote deletion. The active `Flathub` source outcome
is **unsupported as a v3.0 operation**. No remote or app install is claimed.
Reopen if an explicit Flathub use case is selected and a fixed-scope handler
passes URL/key detection, pre-existing-remote preservation, attached-app
refusal, focused failure tests, and exact-target VM apply/recovery. It may
then be an opt-in candidate while broader desktop use moves to v3.1.
