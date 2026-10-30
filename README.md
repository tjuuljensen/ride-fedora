# RIDE Fedora

This branch develops RIDE Linux v3. The client is written in Bash, the
bootstrapper in POSIX `sh`, and operations and profiles in JSON. `jq` is a
runtime dependency. The historical Fedora function library remains in this
repository for migration reference; `ride.sh` no longer evaluates functions
from a preset. The stable v2 release line remains on `master` while the v3
release is prepared on `codex/ride-v3-migration`.

## Try the development client

On Fedora 44 x86_64, install Bash and `jq`, then run from this checkout:

```bash
./ride.sh                         # list operations
./ride.sh search forensic
./ride.sh show package.testdisk
./ride.sh plan --profile forensics
./ride.sh apply --profile forensics --dry-run
```

The `default` and `server-base` package operations are supported on their
declared Fedora 44 x86_64 editions after disposable VM acceptance. Other
catalog operations remain candidates and require `--allow-candidate` for a
real change. System operations need root. Review a plan before applying one:

The [v2 migration progress report](docs/migrations/progress.md) tracks all 186
scoped workstation and generic server outcomes separately from the catalog.
From this checkout as a regular user, run
`python3 tools/migration_progress.py --summary` for a read-only current view.
The six accepted v2 command-line tools are in the opt-in `cli-tools` profile;
`./ride.sh plan --profile cli-tools` previews them on Fedora 44 Workstation.

```bash
./ride.sh plan --profile default
sudo ./ride.sh apply --profile default
sudo ./ride.sh status --profile default
sudo ./ride.sh restore --run-id RUN_ID --dry-run
```

`restore` only reverts operations with a declared exact inverse. A package
installed by RIDE can be removed again where the operation declares `absent`
and `remove-new-install` recovery; OpenSSH clients are installed-only.
Reinstalling a package that existed before RIDE removed it cannot guarantee
its previous version and is refused. Run IDs and
per-step outcomes are saved in private JSON journals. A failed run stops at
the first failed operation and records completed steps.

The command vocabulary is `list`, `search`, `show`, `plan`, `apply`, `download`,
`install`, `set`, `unset`, `status`, `restore`, and `remove`. Use
`./ride.sh --help` for syntax.

Interactive list, search, plan, and status tables use `column` when available
to align fields and show headers. Redirected output stays tab-separated for
scripts; list and search keep their existing headerless TSV format.
`column` is provided by [util-linux on Fedora](https://packages.fedoraproject.org/pkgs/util-linux/util-linux/)
and [bsdextrautils on Debian](https://packages.debian.org/trixie/bsdextrautils)
and [Ubuntu](https://packages.ubuntu.com/noble/bsdextrautils).

Tab completion can be loaded in Bash with:

```bash
source completion/ride.bash
```

## Bootstrap and releases

[`docs/bootstrap.sh`](docs/bootstrap.sh) defaults to **download only** from
the future `v3.0.0` tag. That tag has not been published. After the development
branch is pushed, use an explicit branch ref:

```sh
sh docs/bootstrap.sh --branch codex/ride-v3-migration --download-only
sh docs/bootstrap.sh --branch codex/ride-v3-migration --plan --profile default
```

Bootstrap dependency installation needs `--install-deps`; profile application
needs `--apply`, and candidate application additionally needs
`--allow-candidate`. Inspect downloaded source before applying it.
`docs/index.html` mirrors the shell bootstrap for the existing GitHub Pages
root URL; CI checks that both files stay identical.
The bootstrapper recognizes Fedora, Debian, and Ubuntu, but the operation
catalog currently declares **Fedora 44 x86_64 only**. No Debian or Ubuntu
package support is advertised yet.

### ArtCraft Linux download library

The ArtCraft library discovers every public repository in
[storytold](https://github.com/storytold/) and downloads the newest published
release containing full Linux installers. It includes prereleases when those
are the newest downloadable builds; it does not archive historical versions.
AppImage, RPM and actual `.flatpak` bundles are selected, together with upstream
checksum files. Repositories without these installers are listed in the catalog.

Download on Windows with Python 3.11 or newer (no additional Python packages):

```powershell
python tools/download-artcraft.py all --arch x86_64 --destination 'Z:\Artcraft\linux'
```

On Fedora, use the RIDE library (the download directory must already exist):

```bash
sudo ARTCRAFT_ARCH=x86_64 ./ride.sh --include lib/artcraft/lib-artcraft.sh \
  --downloaddir /path/to/downloads GetArtCraft
sudo ARTCRAFT_FEDORA_RELEASE=44 ARTCRAFT_DEPENDENCY_ARCH=x86_64 \
  ./ride.sh --include lib/artcraft/lib-artcraft.sh \
  --downloaddir /path/to/downloads GetArtCraftDependencies
```

`ARTCRAFT_DOWNLOADDIR` can override the archive directory. The library also
works when sourced directly from Bash. `CheckArtCraftDownloads` only writes a
catalog. `ARTCRAFT_ARCH=all` (the library default) includes every published
architecture; dependency preparation handles one specified architecture.

The cross-platform downloader records versions, source URLs, architecture,
upstream SHA256 hashes and local checksums in `catalog.json`,
`download-report.json` and `SHA256SUMS.local`. Matching verified downloads are
reused; interrupted or invalid files are never promoted from `.part` files.
Discovery errors fail the operation instead of claiming an incomplete inventory
is complete. The downloader uses public HTML because GitHub API quotas are shared.

Dependency preparation requires Fedora, root, `dnf` (DNF5), `python3`, `flatpak`
and `ostree`. Install the tooling with `sudo dnf install flatpak ostree`.
`lib/artcraft/download-dependencies.sh ARCHIVE 44 x86_64` resolves the RPMs
against Fedora 44 and updates with an empty temporary installroot, including
weak dependencies and AppImage/Flatpak host support. It downloads packages
with `dnf install --downloadonly`, without performing an RPM transaction.
Fedora dependency RPM signatures are checked against Fedora's signing key.
Flatpak app bundles are imported only for metadata; their exact runtime branches
and related extensions (including all locales) are downloaded
without deploying the apps. Exported runtime bundles and the RPMs are stored in
`dependencies/fedora-44-x86_64/`, with their own hashes and dependency report.
Large temporary files stay on the native Linux filesystem under `/var/tmp`.
Set `ARTCRAFT_KEEP_STAGE=1` to retain that directory for troubleshooting.

On the target Fedora system, install a chosen app format. For RPMs, supply the
app RPM and the dependency RPM directory to `dnf install` (no network is needed
if the entire package closure matches the target release). For Flatpak, install
the saved runtime bundles first, then the app bundle:

```bash
for runtime in dependencies/fedora-44-x86_64/flatpak/*.flatpak; do
  flatpak install --user --no-deps --no-related "$runtime"
done
flatpak install --user --no-deps --no-related photocraft/v0.7.0/photocraft-0.7.0-linux-x86_64.flatpak
```

AppImages bundle their application libraries; FUSE, the base OS and GPU drivers
are host requirements. The archive includes Fedora FUSE/Mesa/Vulkan support.
Proprietary GPU drivers depend on the target hardware. PhotoCraft's official
desktop builds already include Craft fonts, so its source font repository is
not needed.

## Development and migration

- [`docs/architecture.md`](docs/architecture.md) describes the engine,
  provider boundary, state, cache, and release gate.
- [`docs/acceptance/VM-HARNESS.md`](docs/acceptance/VM-HARNESS.md) runs the
  Fedora-first disposable VM lifecycle tests and records their limits.
- [`docs/OPERATIONS.md`](docs/OPERATIONS.md) is generated from the catalog.
- [`docs/COMMANDS.md`](docs/COMMANDS.md) is generated from the CLI help.
- [`docs/MIGRATION-PLAN.md`](docs/MIGRATION-PLAN.md) accounts for all 76
  active Fedora preset actions.
- [`docs/workstation-server-burndown.md`](docs/workstation-server-burndown.md)
  inventories scoped workstation and generic server outcomes, including inactive
  functions and exact preset coverage. Owner-excluded legacy functions remain
  outside that queue. Regenerate it with
  `python3 tools/build_burndown.py --write`.
- [`docs/sander-feature-map.md`](docs/sander-feature-map.md) reviews the 185
  functions and 25 active preset entries in Sander's library by outcome.
- [`docs/server-ownership.md`](docs/server-ownership.md) identifies which
  server operations can become generic and which values stay private.
- [`docs/github-cache-contract.md`](docs/github-cache-contract.md) defines
  the Windows/Linux release discovery contract.
- [`docs/windows-alignment.md`](docs/windows-alignment.md) maps the current
  Windows development architecture and commands to Linux v3.
- [`docs/package-metadata-reuse.md`](docs/package-metadata-reuse.md) identifies
  product facts worth reconciling across both catalogs.
- [`AGENTS.md`](AGENTS.md) and the local operation migration skill guide
  future AI-assisted changes.
- [`docs/models/repository-conventions.md`](docs/models/repository-conventions.md)
  maps the shared portfolio documentation and script standards to RIDE's
  Bash/POSIX boundaries, generated files, and ownership.
- [`docs/ai-workflow.md`](docs/ai-workflow.md) gives repeatable AI review and
  migration prompts.

Validate without changing the host:

```bash
python3 tools/validate_v3.py --check-docs  # needs python3-jsonschema
python3 -m unittest discover -s tests -p 'test_*.py' -v
bash -n ride.sh lib/v3/*.sh completion/ride.bash
sh -n docs/bootstrap.sh
tools/check-shell-executable.sh
```

CI also runs ShellCheck and `dash`. The Firefox policy helper remains in
`tools/manage-firefox-extensions.py` with tests. Its v3 operation is deferred
until the lifecycle can record and restore ownership correctly. Legacy usage
is documented in [`legacy/v2/README.md`](legacy/v2/README.md).
