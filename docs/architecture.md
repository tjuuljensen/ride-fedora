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
states, privilege, provenance, and verification method. Profiles contain only
IDs and desired states. The engine validates targets and handlers before
changing anything. The Fedora provider is the first implementation. Debian
and Ubuntu need separate apt/dpkg providers and VM acceptance before support
is advertised.

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
