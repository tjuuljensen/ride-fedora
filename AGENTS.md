# RIDE Linux development

RIDE v3 is a Bash client for declarative Linux setup. The POSIX `sh`
bootstrapper only obtains a tagged release and launches the client. JSON
catalog entries and profiles are data; never source them or evaluate their
contents as shell code. The v2 function library and presets are migration
references, not a fallback execution path.

## Portfolio alignment

- Follow the canonical [portfolio documentation model](https://github.com/tjuuljensen/network-devices/blob/master/docs/repository-portfolio/repository-documentation-model.md)
  and [script model](https://github.com/tjuuljensen/network-devices/blob/master/docs/repository-portfolio/script-repository-model.md),
  applying the Linux-specific ownership map and exceptions in
  [RIDE repository conventions](docs/models/repository-conventions.md).
- Prefer small focused diffs, preserve existing behavior unless the request or
  a clear bug requires a change, and do not mix unrelated refactors into fixes.
- New technical documentation, code comments, logs, help, identifiers, and
  commit messages are English. Preserve meaningful localized values and
  upstream identifiers; prefer readable ASCII punctuation in prose.

## Ownership and support

- `catalog/operations.json` defines stable operation IDs, supported targets,
  actions, handlers, sources, and verification requirements. Profiles select
  desired states using those IDs and may select a declared package source.
  Generate operation reference documentation from the catalog rather than
  editing generated output.
- Keep package product, distribution, deployment, acquisition provider,
  artifact format, scope, and destination distinct. Apply the shared
  [package deployment decisions](docs/package-deployment-decisions.md) when
  changing source selection, portable tools, downloads, installation, or
  recovery. Installed and portable deployments may coexist after product
  conflict review; do not impose a blanket product-wide exclusion.
- Follow the versioned [shared RIDE behavior contract](https://github.com/tjuuljensen/ride-windows/blob/codex/ride-v3-migration/docs/models/ride-behavior-contract.md)
  and this repo's [adopted digest reference](docs/models/ride-behavior-contract-ref.json).
  Windows hosts the canonical contract; either RIDE repository may originate changes.
- Before changing shared CLI, catalog/profile meaning, acquisition, planning,
  acceptance, privilege or recovery behavior, review the pinned contract and the
  Windows implementation. Also review each package migration batch and release
  candidate. Classify the impact and record compared revisions or source hashes.
- Follow the contract's review/versioning procedure. Record alignment or an
  intentional difference with an owner, reason, linked follow-up and review
  trigger in [Windows alignment](docs/windows-alignment.md). Update affected help,
  completion and tests with the implementation; track shared conformance work
  honestly while its automated suite remains pending.
- Native target acceptance stays local. Unexplained shared-contract drift blocks
  the affected capability's promotion, not unrelated development. Track remaining
  final-v3 alignment work in the [migration plan](docs/MIGRATION-PLAN.md#cross-platform-alignment-for-final-v3).
  Do not copy the canonical contract here or silently follow a newer development
  HEAD; update its version/digest references deliberately.
- Keep the engine and public IDs distro-neutral. Place DNF/RPM behavior in the
  Fedora provider; add apt/dpkg providers only with matching VM evidence.
- Keep host-specific users, shares, secrets, and IP addresses outside this
  public repository. Coordinate movement of generic server behavior with the
  active source in `network-devices`; do not remove that source until its
  consumers and rollback are recorded.
- Before a cross-repository ownership change, identify the authoritative
  source, consumers, publication or deployment path, runtime identity, state,
  and recovery. Unknown use is unverified, not inactive. Keep Windows product
  facts and the GitHub behavior contract aligned without sharing platform
  installers prematurely.
- An operation is supported only on the distro, release, and CPU architecture
  tested for it. Unknown targets fail closed. Never claim a placeholder or
  no-op handler succeeded.

## Changes to operations

- Use the `ride-operation-migration` skill when migrating a legacy function or
  adding a Sander-inspired operation. Review user intent, current upstream
  method, license, source and verification evidence, detection, removal, and
  recovery before selecting a handler.
- Keep operation IDs stable once published. Record replacements or retirement
  in the migration ledger and scoped workstation/server burndown. Respect its
  explicit owner exclusions when regenerating it with
  `python3 tools/build_burndown.py --write`; CI checks its coverage. Do not
  directly copy Sander's source without an
  explicit license grant or published license and retained attribution.
- Prefer distro repositories with signature enforcement. Record what was
  actually verified for other downloads. Do not run remote scripts in default
  profiles or overwrite unowned configuration during apply or restore.
- Bash completion must read only local catalog, profiles, and run state. It
  must not source operational modules, contact the network, or elevate.
- `docs/index.html` is the GitHub Pages shell entry point; keep it byte-for-byte
  identical to `docs/bootstrap.sh` until publication moves to a different URL.

## Scripts and documentation

- Keep the CLI in Bash and the bootstrapper in POSIX `sh`. All tracked `.sh`
  files must have Git mode `100755`; run `tools/check-shell-executable.sh`
  after adding or moving them. Do not treat sourced Bash modules as portable
  `/bin/sh` programs.
- New or materially changed entry-point scripts need current English headers
  for purpose, behavior, compatibility, usage, inputs, side effects,
  prerequisites, ownership, provenance, and version. Keep help and version
  output synchronized with the code. Tightly coupled `lib/v3/` modules share
  the client release version; historical v2 files are migration evidence.
- Keep `README.md` concise. Put detailed procedures and repository-specific
  rules under `docs/`; use relative links and Linux shell syntax. State the
  starting directory, user or root scope, side effects, validation, and
  recovery for copy-ready commands. Regenerate `docs/COMMANDS.md`,
  `docs/OPERATIONS.md`, and the burndown from their sources rather than editing
  generated files directly.
- Distinguish source readiness, publication, VM activation, and verified
  behavior. For phased work, follow the batch procedure in
  `docs/MIGRATION-PLAN.md`; keep actual status and evidence there instead of
  treating chat history or a green static check as acceptance.

## Validation and release

- Run Bash syntax checks, ShellCheck, JSON/schema validation, mocked engine
  tests, and the Firefox Python tests for relevant changes. Test the POSIX
  bootstrap with `dash` and ShellCheck's `sh` mode.
- Check `tools/check-shell-executable.sh`, generated documentation, and focused
  diffs. For Python tool changes, run `python3 -m py_compile` and relevant tests.
- Run state-changing acceptance only in disposable VMs. Record distro,
  release, architecture, profile, and outcome before declaring support.
- Use the pinned targets and shared lifecycle contract in `tests/acceptance/`
  for VM pilots. A Cloud Base result does not establish Workstation or Server
  support; keep edition-specific evidence under `docs/acceptance/`.
- Keep `master` as the release line while work proceeds on
  `codex/ride-v3-migration`. v3 client tags are independent of Fedora release
  numbers. Check `git status`, preserve unrelated untracked work, and never
  revert user changes to make a validation pass.
