# RIDE Fedora

RIDE Fedora v3 is a declarative Linux setup client. The client is written in
Bash, its release bootstrapper in POSIX `sh`, and operations and profiles are
JSON data. The v3 release is still in preparation; no v3 tag has been
published. The v2 function libraries remain migration references and are not a
fallback execution path.

## Supported scope

The supported baseline is Fedora 44 x86_64: the `default` profile on
Workstation and `server-base` on Server. `package.exfatprogs` is also accepted
on Cloud Base. Other catalog entries are opt-in candidates, require an exact
declared target, and need `--allow-candidate` for a state-changing command.
Debian, Ubuntu, other Fedora releases, and other architectures are not in the
current support matrix.

## Use the development client

Run from the repository root with Bash and `jq` installed. Inspect a plan
before applying it. The supported baseline profiles do not need a candidate
override:

```bash
./ride.sh --help
./ride.sh list
./ride.sh search forensic
./ride.sh show package.testdisk
./ride.sh plan --profile default
./ride.sh apply --profile default --dry-run
sudo ./ride.sh apply --profile default
sudo ./ride.sh status --profile default
sudo ./ride.sh restore --run-id RUN_ID --dry-run
```

The shared command vocabulary is `list`, `search`, `show`, `plan`, `apply`,
`download`, `install`, `set`, `unset`, `status`, `restore`, and `remove`.
Use `./ride.sh --help` for current syntax. Candidate operations stay blocked
unless explicitly selected with `--allow-candidate`. Run journals are private
JSON files; `restore` only handles operations with a declared inverse and
cannot promise the previous version of a package removed by RIDE.

Load Bash completion in the current shell with:

```bash
source completion/ride.bash
```

## Bootstrap and releases

[`docs/bootstrap.sh`](docs/bootstrap.sh) defaults to downloading the future
`v3.0.0` release only. That tag is not published. After the migration branch
is available remotely, it can be inspected without applying changes:

```sh
sh docs/bootstrap.sh --branch codex/ride-v3-migration --download-only
sh docs/bootstrap.sh --branch codex/ride-v3-migration --plan --profile default
```

Dependency installation requires `--install-deps`; applying a profile
requires `--apply`. Inspect downloaded source and its plan before applying.
[`docs/index.html`](docs/index.html) is the byte-for-byte GitHub Pages mirror
of the shell bootstrap.

## Development and migration records

- [v3.0 release review](docs/release-v3.0-review.md): current gaps and release
  recommendations.
- [Migration plan](docs/MIGRATION-PLAN.md) and [generated progress](docs/migrations/progress.md):
  scoped v2 outcomes, current status, and next actions.
- [Supplementary legacy source audit](docs/legacy-source-audit.md): older
  libraries and scripts not covered by the main outcome ledger.
- [Windows alignment](docs/windows-alignment.md): shared behavior decisions
  and remaining final-v3 work.
- [VM acceptance guide](docs/acceptance/VM-HARNESS.md): disposable Fedora
  target setup, evidence, and recovery limits.
- [Generated CLI reference](docs/COMMANDS.md) and
  [generated operation reference](docs/OPERATIONS.md).
- [ArtCraft download utility](docs/artcraft-downloads.md), a separate archive
  tool that is not part of the v3 operation catalog.
- [Legacy v2 notes](legacy/v2/README.md).

The key local checks are listed in
[`docs/release-v3.0-review.md`](docs/release-v3.0-review.md). CI runs the
syntax, ShellCheck, schema, generated-documentation, alignment, mocked, and
Firefox policy checks. Only disposable VM acceptance establishes support for
the exact declared Fedora target.
