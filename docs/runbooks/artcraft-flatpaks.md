# ArtCraft Flatpak candidates on Fedora Workstation

Run these commands from the repository root as the intended **non-root**
desktop user on Fedora 44 or 45 Workstation x86_64. They configure user
Flatpak sources and install application and runtime bytes into that user's
Flatpak installation. The ArtCraft source is a publisher-operated unsigned
OCI preview; the Flathub runtime source uses GPG verification. All ArtCraft
operations require `--allow-candidate` and are excluded from the default
profile.

Inspect any existing per-user `flathub` remote first. If it is absent, add
the official signed runtime source. This remote is shared user state; RIDE's
ArtCraft operations do not own or delete it.

```bash
flatpak remotes --user --columns=name,url,options --json
flatpak remote-add --user flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak remotes --user --columns=name,url,options --json
```

If `flathub` already exists, skip `remote-add` and verify that its URL is
`https://dl.flathub.org/repo/` and its options do not contain
`no-gpg-verify`. RIDE refuses app installation if this check fails.

Configure the separate ArtCraft OCI user remote, then choose one candidate
package ID from [the migration list](../migrations/artcraft-flatpaks.md).
For example, install and inspect the Launcher:

```bash
./ride.sh set setting.artcraft-oci-user-remote --state configured --allow-candidate
./ride.sh install package.artcraft-launcher --allow-candidate
./ride.sh status package.artcraft-launcher
flatpak run --user ai.storyteller.artcraft-launcher
```

An application launch may access the network and create user settings. Use a
disposable Workstation VM for acceptance. To remove the Launcher while keeping
its user data and shared runtime:

```bash
./ride.sh remove package.artcraft-launcher --allow-candidate
./ride.sh status package.artcraft-launcher
```

Once every ArtCraft app from that user remote has been removed, RIDE can also
remove the remote it configured. It refuses while any user app still uses the
remote. Leave `flathub` in place if other Flatpak apps or runtimes use it.

```bash
./ride.sh unset setting.artcraft-oci-user-remote --allow-candidate
flatpak remotes --user --columns=name,url,options --json
```

RIDE removes only the selected Flatpak ref. User projects and configuration
under `~/.var/app/<app-id>` remain for manual recovery or later reuse.
