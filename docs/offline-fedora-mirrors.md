# Offline Fedora package mirrors

This guide describes how to prepare Fedora RPM repositories for disposable
RIDE test VMs and air-gapped Fedora systems. It covers repository acquisition
and DNF configuration; it does not make RIDE's package installation workflow
offline-capable. RIDE currently installs RPMs by package name through the
system's configured DNF repositories. Its explicit offline install mode is
still pending; see [package deployment decisions](package-deployment-decisions.md).

## Choose the repositories

Mirror each Fedora release and architecture separately. For example, keep
Fedora 44 x86_64 and Fedora 45 x86_64 under separate roots. Fedora Workstation
and Server use the same Fedora package repositories for a given release and
architecture; edition-specific media and package selections are separate.

Start with the repositories enabled on a Fedora machine for the release you
intend to mirror. Record their IDs before syncing:

```sh
dnf5 repolist --enabled
```

The usual Fedora base and stable-update repository IDs are `fedora` and
`updates`. Add third-party or organization repositories only when needed,
after checking that they publish content for the target Fedora release and
architecture. Do not include `updates-testing` in a stable mirror unless the
test specifically requires pre-release updates. Source and debug repositories
are also separate choices and are unnecessary for normal package installation.

## Install the sync tool

The standalone [Fedora mirror manager](../tools/manage-fedora-mirror.sh) wraps
DNF5 reposync with repository listing, a disk-space plan, sync, and local
metadata checks. It does not alter system DNF configuration. Run it on an
online Fedora staging machine with access to the upstream repositories.
`dnf5-plugins` provides `dnf5 reposync`:

```sh
sudo dnf5 install dnf5-plugins
```

## Mirror the staging machine's current Fedora release

This example syncs Fedora 44 x86_64; adjust the release and repository IDs to
match the staging machine's enabled and intended repositories.

```bash
./tools/manage-fedora-mirror.sh list --releasever 44
./tools/manage-fedora-mirror.sh plan --releasever 44 --arch x86_64 \
  --destination /srv/fedora-mirror
sudo ./tools/manage-fedora-mirror.sh sync --releasever 44 --arch x86_64 \
  --destination /srv/fedora-mirror --min-free-gib 100
./tools/manage-fedora-mirror.sh verify --releasever 44 --arch x86_64 \
  --destination /srv/fedora-mirror
```

Start in the repository root. The example's `100` GiB value is a user-selected
minimum free-space floor, not an estimate of the repository's required size;
check the plan output and storage capacity before choosing it. The tool uses
`fedora` and `updates` by default. Add another repo with a repeated `--repo ID`
option after confirming that it is enabled and publishes for the selected
release. `sync` asks for confirmation unless `--yes` is supplied. It updates
the selected release/architecture tree in place, downloads repository metadata,
forces RPM signature checking, and never prunes old RPMs. If a sync fails, the
in-place tree may be incomplete; rerun sync and verify it before use. This tool
does not preserve a last-good generation or roll back a failed update. The official
[DNF5 reposync reference](https://dnf5.readthedocs.io/en/stable/dnf5_plugins/reposync.8.html)
documents the underlying behavior.

## Prepare a mirror for a Fedora release upgrade

Before upgrading a host from Fedora 44 to Fedora 45, prepare a separate Fedora
45 mirror while the staging machine is online. The repository definitions on
the staging machine must resolve Fedora 45's official repository locations.
Check the target release's enabled repository list before syncing:

```bash
./tools/manage-fedora-mirror.sh list --releasever 45
```

Then sync with the target release override and a new destination. The override
changes how repository URLs containing `$releasever` are resolved; it does
not prove that third-party repositories support Fedora 45.

```bash
./tools/manage-fedora-mirror.sh plan --releasever 45 --arch x86_64 \
  --destination /srv/fedora-mirror
sudo ./tools/manage-fedora-mirror.sh sync --releasever 45 --arch x86_64 \
  --destination /srv/fedora-mirror --min-free-gib 100
./tools/manage-fedora-mirror.sh verify --releasever 45 --arch x86_64 \
  --destination /srv/fedora-mirror
```

Do not overwrite the previous release's mirror during a distro upgrade. Keep
the old mirror until the upgraded systems have been validated and no longer
need it for recovery. Updates change over time, so make a dated snapshot or
preserve each sync generation when reproducible test inputs matter.

## Use the local repositories

Transfer the mirror to read-only media or expose it to the isolated network
over a local HTTP server. For a mounted filesystem, create a temporary DNF
repository file pointing only at the intended local repository directories.
For example, with Fedora 45 x86_64 mounted at `/media/fedora-mirror`:

```ini
[ride-fedora45]
name=Fedora 45 local mirror
baseurl=file:///media/fedora-mirror/45/x86_64/fedora
enabled=1
gpgcheck=1
```

Create a second section for `updates`, with its `baseurl` pointing to the
parallel `updates` directory. Keep Fedora's signing key available and trusted
on the target. Retain package GPG verification; do not use `gpgcheck=0` to
work around a missing key or an invalid RPM. DNF's `baseurl` supports local
repository paths and its `gpgcheck` setting controls package signature
verification; see the [DNF5 configuration reference](https://dnf5.readthedocs.io/en/stable/dnf5.conf.5.html).

For offline acceptance, configure disposable VMs to use only the local mirror,
block public network access, and verify a package lifecycle. A reachable local
mirror alone is not proof that a transaction stayed offline; inspect the DNF
transaction and network configuration. RIDE's built-in install command still
uses the host's configured DNF repositories and does not yet guarantee
fail-closed offline behavior.

## Capacity, updates, and retention

Full repositories can be large. Before the first sync, check free space on the
destination filesystem and leave room for the incoming update generation and
other system use. For later syncs, `reposync` avoids downloading RPM files
already present. By default, it also leaves previously downloaded RPM files in
place when a later upstream metadata refresh no longer lists them. This can
grow the mirror over time; those old files may no longer be referenced by the
current repository metadata.

Keep one separately named tree per Fedora release, architecture, and sync
generation when reproducibility matters. Verify the new tree before making it
the active local repository. Remove old generations only after confirming
that no test VM or air-gapped installation depends on them. Avoid an
in-place `--delete` update for the only retained copy: a failed or interrupted
sync should not destroy the last usable mirror.

The helper resolves target-release URLs with the explicit `--releasever`
value. This does not establish that third-party repositories support the new
release. Review `list` output and add only verified repository IDs. By default,
the tool syncs `fedora` and `updates`, even if `list` shows additional enabled
repositories. It writes a `.mirror-manifest.tsv` after a successful sync. It
has no automatic generation snapshots, rotation, prune command, or failed-sync
rollback; preserve a separate copy when the previous same-release mirror must
remain recoverable.

`verify` checks that each selected repository has a `repodata/repomd.xml` file
and at least one RPM. It does not validate every metadata reference or RPM
signature, and does not prove that DNF can install packages from the mirror.
For acceptance, point a disposable system only at the local source, block
public networking, and run the intended DNF package transaction.
