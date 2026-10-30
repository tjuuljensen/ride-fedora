# RIDE v3 architecture

The v3 client is Bash. The bootstrapper is POSIX `sh` and checks for Bash and
`jq` before launching it. A distro-neutral engine reads versioned JSON catalog
and profile data, selects fixed trusted handlers, and records per-run state.
JSON never contains executable shell. The legacy function library is reference
material only.

```text
POSIX sh bootstrap -> tagged source -> Bash ride.sh
                                    -> JSON catalog and profiles
                                    -> Bash engine and run journal
                                    -> fixed handlers -> Fedora DNF/RPM provider
                                                      -> future apt/dpkg provider
                                    -> GitHub metadata cache / artifact evidence
```

## Public behavior

`list`, `search`, and `show` discover catalog entries. `plan` compares a
profile's desired states to live observations without changing the machine.
`apply`, `install`, `set`, `unset`, and `remove` act on supported operations.
`download` acquires artifacts only when a provider supports standalone
acquisition. `status` reports live state; `restore --run-id` uses a saved
journal and refuses to overwrite a state changed by something else.

Every operation declares an ID, kind, handler, supported targets, available
states, privilege, provenance, and verification method. Profiles contain IDs,
desired states, and optional package source IDs. The engine validates targets
and handlers before changing anything. The Fedora provider is the first
implementation. Debian and Ubuntu need separate apt/dpkg providers and VM
acceptance before support is advertised.

## Package sources and installation scope

One stable package ID identifies the product. Distribution (installed or
portable), provider, artifact format, scope, and destination answer different
questions. A directly downloaded RPM can still be an installed system package;
an AppImage can be deployed to a user or system path. Neither "standalone" nor
"system installer" is a complete package type.

The current catalog names one `installed` distribution and one
`local-installed` deployment slot per package. Its `sourceId` selects the
default acquisition provider; optional `sourceProviders` describe alternatives
for that same slot. A provider cannot change its distribution or scope. Profiles
may set `source`, and direct package commands accept `--source`; explicit
choices fail if undeclared. `show`, plan, status, and run journals identify the
resolved source. Current DNF alternatives must have distinct RPM names so the
observer can identify a conflicting build; a second repository for the same
RPM name needs provenance-aware observation before it can be offered.

The approved target follows the Windows [package deployment decision](package-deployment-decisions.md):
an installed copy, separate portable copies, and acquisition kits can coexist
under one product ID after product-specific conflict review. Each deployment
needs its own identity, scope, destination, version, ownership, artifact
evidence, and recovery. The current alternate-provider guard covers the one
`local-installed` slot; it is not a product-wide mutual-exclusion rule.
Windows has individual portable deployments, but independent coexistence and
kit assembly remain pending there. Linux has no portable handler yet.

Acquisition is separate from installation. `download` does not change package
presence. A later install from a retained verified artifact must select that
exact file and run without network fallback; the current Fedora `install`
command still calls DNF and cannot consume a downloaded RPM. Explicit provider
selection never falls back. Any future automatic provider fallback is limited
to approved equivalent artifacts and availability or transport failures;
integrity or installation failures stop. Flatpak, AppImage, direct local RPM,
apt/dpkg, and offline install need their own handlers, manifest/state work, and
disposable-VM acceptance before they are offered.

## State, cache, and recovery

System run journals live under `/var/lib/ride-fedora/runs`; per-user journals
use `$XDG_STATE_HOME/ride-fedora/runs` or `~/.local/state/ride-fedora/runs`.
System cache lives under `/var/cache/ride-fedora`; user cache uses
`$XDG_CACHE_HOME/ride-fedora` or `~/.cache/ride-fedora`. State and cache files
are private to their owner. The journal records before and after observations,
handler outcome, and any limits on recovery. For package operations, a new
install can be removed again; an old package removed by RIDE cannot be
reinstalled to its exact prior version, so restore refuses that case. A
completed run can be restored once. Volatility3 is installed into an isolated
per-user virtual environment using hash-pinned wheels.

GitHub release discovery has a documented cross-repository behavior contract.
Linux uses a bounded disk cache across invocations; Windows may retain its
native process cache. The shared contract covers freshness, provenance,
rate-limit behavior, optional credentials, and verification results. Product
identity and upstream facts can be compared across catalogs; installers and
platform detection remain local.

## Release boundary

The v3 product version starts at `3.0.0`; supported Fedora releases are
separate string metadata so future Ubuntu releases such as `26.04` can be
represented. `master` remains the current release line during migration.
The new bootstrap defaults to a tagged release and never silently applies a
profile. Current Fedora Workstation and Server targets require disposable VM
evidence. The repository name can be revisited after Debian or Ubuntu passes
acceptance.

The [VM acceptance harness](acceptance/VM-HARNESS.md) uses a target matrix,
verified base images, fresh qcow2 overlays, and one shared lifecycle contract.
The first automated target is Fedora Cloud Base for a generic package pilot;
edition-specific Workstation and Server evidence remains a separate gate.
