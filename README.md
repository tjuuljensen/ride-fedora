# RIDE Fedora

RIDE Fedora v3 is a declarative Linux setup client. The client is written in
Bash, its release bootstrapper in POSIX `sh`, and operations and profiles are
JSON data. The v3 release is still in preparation; no v3 tag has been
published. The v2 function libraries remain migration references and are not a
fallback execution path.

## Supported scope

The accepted baseline is Fedora 44 x86_64: the `default` profile on
Workstation and `server-base` on Server. `package.exfatprogs` is also accepted
on Cloud Base. Fedora 45 Workstation and Server are selected as v3.0 release
targets, pending image pinning and target-specific acceptance. Until that
acceptance passes, catalog entries do not gain Fedora 45 support by this
decision alone. Other catalog entries are opt-in candidates, require an exact
declared target, and need `--allow-candidate` for a state-changing command.
Debian, Ubuntu, and other architectures are not in the current release scope.

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

## Read-only catalog reports

Run these from the repository root with `jq` installed. They read the source
catalog and do not apply changes. The first shows every operation declared as
a candidate for Fedora 44 or 45, including its declared edition and
architecture. Candidate status still requires target acceptance before it
can be claimed as supported.

```bash
jq -r '
  .operations[]
  | select(.status == "candidate")
  | . as $op
  | ($op.targets // {} | to_entries[])
  | select(.key == "fedora")
  | select(any(.value.releases[]?; . == "44" or . == "45"))
  | [$op.id, $op.kind, $op.group, $op.status, .key,
     (.value.releases | join(",")),
     (.value.variantIds // ["any"] | join(",")),
     (.value.architectures | join(","))]
  | @tsv
' catalog/operations.json
```

List catalog entries that declare no target at all:

```bash
jq -r '
  .operations[]
  | select((.targets // {}) == {})
  | [.id, .kind, .status, .name]
  | @tsv
' catalog/operations.json
```

List all entries that do not declare a particular target. Set the variables
for the release and edition being reviewed; this example reports operations
without Fedora 45 Workstation x86_64 support:

```bash
release=45
variant=workstation
architecture=x86_64
jq -r --arg release "$release" --arg variant "$variant" \
  --arg architecture "$architecture" '
  .operations[]
  | . as $op
  | ($op.targets.fedora // {}) as $fedora
  | select((($fedora.releases // []) | index($release)) == null
      or (($fedora.variantIds // []) | index($variant)) == null
      or (($fedora.architectures // []) | index($architecture)) == null)
  | [$op.id, $op.kind, $op.status, $op.name]
  | @tsv
' catalog/operations.json
```

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
- [v3.0 release travel plan](docs/runbooks/v3-release-travel-plan.md): offline
  preparation, ordered acceptance burndown, and legacy-source review queue.
- [Migration plan](docs/MIGRATION-PLAN.md) and [generated progress](docs/migrations/progress.md):
  scoped v2 outcomes, current status, and next actions.
- [DFIR software expansion backlog](docs/migrations/dfir-expansion-backlog.md):
  Linux-labelled research-pack entries screened against the current catalog;
  candidates remain unselected until reviewed and accepted.
- [Supplementary legacy source audit](docs/legacy-source-audit.md): older
  libraries and scripts not covered by the main outcome ledger.
- [Windows alignment](docs/windows-alignment.md): shared behavior decisions
  and remaining final-v3 work.
- [VM acceptance guide](docs/acceptance/VM-HARNESS.md): disposable Fedora
  target setup, evidence, and recovery limits.
- [Generated CLI reference](docs/COMMANDS.md) and
  [generated operation reference](docs/OPERATIONS.md).
- [Linux image downloader](docs/linux-image-downloads.md) and
  [VM image downloader](docs/vm-image-downloads.md): standalone verified media
  downloads with local manifests and rotation.
- [ArtCraft Flatpak candidates](docs/migrations/artcraft-flatpaks.md) and the
  separate [archive download utility](docs/artcraft-downloads.md).
- [Legacy v2 notes](legacy/v2/README.md).

The key local checks are listed in
[`docs/release-v3.0-review.md`](docs/release-v3.0-review.md). CI runs the
syntax, ShellCheck, schema, generated-documentation, alignment, mocked, and
Firefox policy checks. Only disposable VM acceptance establishes support for
the exact declared Fedora target.
