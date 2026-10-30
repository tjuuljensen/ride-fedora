# RIDE Fedora repository conventions

This is the RIDE Linux adaptation of the portfolio's
[documentation model](https://github.com/tjuuljensen/network-devices/blob/master/docs/repository-portfolio/repository-documentation-model.md)
and [script model](https://github.com/tjuuljensen/network-devices/blob/master/docs/repository-portfolio/script-repository-model.md).
Those documents remain authoritative for portfolio-wide rules. This file names
RIDE's sources, consumers, exceptions, and Linux-specific checks; it is not a
copy of the shared models.

## Source and runtime boundaries

| Subject | Authoritative source | Consumer or output | Boundary |
| --- | --- | --- | --- |
| Linux client and trusted handlers | `ride.sh`, `lib/v3/` | Tagged releases and local CLI runs | Bash; only fixed repository handlers execute. JSON is data, never sourced or evaluated. |
| Operations and profiles | `catalog/operations.json`, `profiles/*.json`, `schemas/` | CLI, completion, generated operation reference | Stable IDs; distro, release, architecture, privilege, verification, and recovery are explicit. |
| Bootstrap | `docs/bootstrap.sh` | `docs/index.html`, release download | POSIX `sh`; `docs/index.html` is a byte-identical GitHub Pages mirror, not another editing surface. Download, dependency installation, and apply are separate commands. |
| Generated references | CLI help, catalog, migration sources, and `tools/` generators | `docs/COMMANDS.md`, `docs/OPERATIONS.md`, `docs/workstation-server-burndown.md` | Regenerate and check; do not hand-edit generated output. |
| Fedora v2 material | `lib-fedora.sh`, `default.preset`, `legacy/v2/` | Migration assessment only | Historical behavior is not a v3 execution fallback. Preserve its provenance and defects as evidence. |
| Server RIDE | `network-devices/operations/provisioning/ride/` | Name-only `migration/server-inventory.json` | Server source, host identities, NAS mounts, credentials, and service-specific configuration stay in the server repository. Refresh the snapshot deliberately; it is not a synchronized runtime copy. |
| Windows RIDE | `ride-windows` development branch | Shared command and GitHub behavior contract | Reconcile product identity and protocol behavior; keep PowerShell and Bash installers native to their platforms. |
| Reference scripts | `reference/` | Burndown inputs only | A reference script is not a supported catalog operation or a default-profile action. |

The catalog supports three base package operations on their declared Fedora 44
x86_64 editions; other entries remain candidates. The scoped v2 outcome ledger
tracks migration progress separately from catalog support. Debian and Ubuntu
remain future providers. Do not infer supported platforms from the
bootstrapper's ability to download source on them.

## Documentation and migration records

`README.md` is the short landing page. Existing root-level `docs/*.md` paths
remain stable; new detailed runbooks, decisions, registers, or migrations may
use `docs/runbooks/`, `docs/decisions/`, `docs/registers/`, or `docs/migrations/`
when the content warrants a separate area. Do not create empty directories or
duplicate portfolio governance under `docs/repository-portfolio/`. Local rules
belong in `docs/models/`. Link to one authoritative procedure rather than
copying it into several files.

Write new technical content in English. Preserve meaningful localized data and
external names. Use UTF-8, readable ASCII punctuation, relative Markdown links,
repository-relative paths with forward slashes, and native Linux paths in shell
examples. Follow `.gitattributes` for LF text without broad renormalization.
Identify the starting directory, required user/root scope, inputs,
side effects, validation, and recovery for copy-ready procedures. Use `bash`
or `sh` fence labels accurately. Static syntax checks do not establish runtime
health or distro support.

`docs/MIGRATION-PLAN.md` owns the active legacy disposition and batch handoff.
`migration/outcomes.json` owns current progress for all scoped v2 outcomes;
the workstation/server burndown and progress report are generated views. Owner
exclusions remain visible outside the 180-outcome denominator.
`docs/acceptance/` holds dated VM evidence. A row moves
from planned to source-ready only after implementation and static checks;
activation and verified behavior require separate evidence. Keep unresolved
consumers and recovery material until closure.

## Script maintenance and exceptions

The client is Bash; only the bootstrapper is POSIX `sh`. New or materially
changed entry-point scripts need a concise English header covering purpose,
behavior, compatibility, usage, inputs, side effects, prerequisites, owner,
provenance when adapted, version, and change history. Keep `--help` and
`--version` aligned with one version constant where the script has a CLI.
Use `set -euo pipefail` for Bash and `set -eu` for POSIX `sh` when control flow
supports it. Quote variables, use arrays for Bash argument lists, avoid `eval`
on data, use bounded temporary files and cleanup, and keep secrets out of
arguments, logs, caches, and committed examples.

Every tracked `.sh` file has Git mode `100755`; check the index with
`tools/check-shell-executable.sh`. `docs/index.html` is executable shell content
published with an `.html` filename and is checked for byte equality with the
bootstrapper instead of by the `.sh` mode check.

The v3 client and its tightly coupled `lib/v3/*.sh` modules share the client
release version. Sourced modules do not invent independent CLI versions or
standalone `--help` commands. Historical v2 files retain their headers and
version history; do not refactor them merely to satisfy a new template. The
Waydroid script is reference-only until its behavior is migrated and tested.
These are scoped exceptions to the shared script model, reviewed when a file
becomes an independently maintained entry point or a v3 release candidate.

## Checks and release boundary

Run the narrowest useful checks for a change: shell syntax and ShellCheck,
`dash` for the bootstrapper, `tools/check-shell-executable.sh`, JSON Schema and
generated-document checks, focused mocked tests, and Firefox policy tests when
affected. Run state-changing acceptance only in disposable VMs. Record target
distro, release, architecture, operations, prior state, apply/repeat/status,
removal or restore, partial failure, and dated results before claiming support.
Publish a tagged release only after its declared target matrix passes.
