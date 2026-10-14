# RIDE Fedora

This branch develops RIDE Linux v3. The client is written in Bash, the
bootstrapper in POSIX `sh`, and operations and profiles in JSON. `jq` is a
runtime dependency. The historical Fedora function library remains in this
repository for migration reference; `ride.sh` no longer evaluates functions
from a preset. The stable v2 release line remains on `master` until v3 passes
its acceptance gates.

## Try the development client

On Fedora 44 x86_64, install Bash and `jq`, then run from this checkout:

```bash
./ride.sh                         # list operations
./ride.sh search forensic
./ride.sh show package.testdisk
./ride.sh plan --profile forensics
./ride.sh apply --profile forensics --dry-run
```

The catalog currently contains **candidate** operations. They require
`--allow-candidate` for a real change, because disposable VM acceptance has
not yet been recorded. System operations need root. Review a plan before
applying one:

```bash
./ride.sh plan --profile default
sudo ./ride.sh apply --profile default --allow-candidate
sudo ./ride.sh status --profile default
sudo ./ride.sh restore --run-id RUN_ID --dry-run
```

`restore` only reverts operations with an exact inverse. A package installed
by RIDE can be removed again; reinstalling a package that existed before RIDE
removed it cannot guarantee its previous version and is refused. Run IDs and
per-step outcomes are saved in private JSON journals. A failed run stops at
the first failed operation and records completed steps.

The command vocabulary is `list`, `search`, `show`, `plan`, `apply`, `download`,
`install`, `set`, `unset`, `status`, `restore`, and `remove`. Use
`./ride.sh --help` for syntax. Tab completion can be loaded in Bash with:

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
`--allow-candidate`. Inspect downloaded source before using either option.
`docs/index.html` mirrors the shell bootstrap for the existing GitHub Pages
root URL; CI checks that both files stay identical.
The bootstrapper recognizes Fedora, Debian, and Ubuntu, but the operation
catalog currently declares **Fedora 44 x86_64 only**. No Debian or Ubuntu
package support is advertised yet.

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
