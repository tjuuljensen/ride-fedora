# Flathub remote ownership and recovery

Status: **opt-in candidate acceptance passed**, 2026-10-31 UTC.
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

## Completion criteria defined before implementation

- Use the system installation and canonical current remote URL
  `https://dl.flathub.org/repo/flathub.flatpakrepo`; require the imported GPG
  key and strict remote verification. Keep the operation separate from the
  Flatpak RPM/runtime outcome and out of base profiles.
- Read system and user remotes separately. Never adopt a pre-existing remote,
  even when its name and URL match. Journal a RIDE ownership marker only after
  adding an absent system remote. A name collision, altered URL, missing key,
  disabled GPG verification, or changed marker must fail closed.
- Restore and explicit remove must delete only the exact RIDE-owned system
  remote, and only while no application or runtime is installed from it.
  Preserve all user remotes, system remotes, applications, runtimes, and
  remote configuration. Never use the v2 `flatpak uninstall flathub` as an
  inverse.
- Add mocked checks for absent apply/repeat/remove, a pre-existing same-name
  remote, URL or key drift, attached-application refusal, marker tampering,
  and rollback if ownership recording fails. In a disposable pinned Fedora
  44 x86_64 Workstation VM, verify plan, candidate gate, apply, repeat,
  status, GPG verification, restore, explicit removal, and preservation of
  seeded user/system remotes and installed app state.
- Promote only after the exact-target lifecycle passes. Keep per-app
  installation and RPM/Flatpak product coexistence under each application's
  own operation and product conflict review.

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

The owner has kept Flathub in scope and confirmed that RPM and Flatpak
deployments may coexist after product-specific review. The opt-in system
remote passed the focused mocks and [disposable Workstation lifecycle](../acceptance/system-flathub-remote.md).
It uses an ownership marker and refuses to delete a remote that has attached
system applications. The v3.0 result covers only the remote; application
installation and per-product RPM/Flatpak coexistence remain attached to each
application operation and H033.
