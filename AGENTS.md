# RIDE Linux development

RIDE v3 is a Bash client for declarative Linux setup. The POSIX `sh`
bootstrapper only obtains a tagged release and launches the client. JSON
catalog entries and profiles are data; never source them or evaluate their
contents as shell code. The v2 function library and presets are migration
references, not a fallback execution path.

## Ownership and support

- `catalog/operations.json` defines stable operation IDs, supported targets,
  actions, handlers, sources, and verification requirements. Profiles select
  desired states using those IDs. Generate operation reference documentation
  from the catalog rather than editing generated output.
- Keep the engine and public IDs distro-neutral. Place DNF/RPM behavior in the
  Fedora provider; add apt/dpkg providers only with matching VM evidence.
- Keep host-specific users, shares, secrets, and IP addresses outside this
  public repository. Coordinate movement of generic server behavior with the
  active source in `network-devices`; do not remove that source until its
  consumers and rollback are recorded.
- An operation is supported only on the distro, release, and CPU architecture
  tested for it. Unknown targets fail closed. Never claim a placeholder or
  no-op handler succeeded.

## Changes to operations

- Use the `ride-operation-migration` skill when migrating a legacy function or
  adding a Sander-inspired operation. Review user intent, current upstream
  method, license, source and verification evidence, detection, removal, and
  recovery before selecting a handler.
- Keep operation IDs stable once published. Record replacements or retirement
  in the migration ledger and complete workstation/server burndown. Regenerate
  that burndown with `python3 tools/build_burndown.py --write`; CI checks its
  coverage. Do not directly copy Sander's source without an
  explicit license grant or published license and retained attribution.
- Prefer distro repositories with signature enforcement. Record what was
  actually verified for other downloads. Do not run remote scripts in default
  profiles or overwrite unowned configuration during apply or restore.
- Bash completion must read only local catalog, profiles, and run state. It
  must not source operational modules, contact the network, or elevate.
- `docs/index.html` is the GitHub Pages shell entry point; keep it byte-for-byte
  identical to `docs/bootstrap.sh` until publication moves to a different URL.

## Validation and release

- Run Bash syntax checks, ShellCheck, JSON/schema validation, mocked engine
  tests, and the Firefox Python tests for relevant changes. Test the POSIX
  bootstrap with `dash` and ShellCheck's `sh` mode.
- Run state-changing acceptance only in disposable VMs. Record distro,
  release, architecture, profile, and outcome before declaring support.
- Keep `master` as the release line while work proceeds on
  `codex/ride-v3-migration`. v3 client tags are independent of Fedora release
  numbers. Check `git status` and preserve unrelated untracked work.
