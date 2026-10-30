# Host identity, DNF tuning, update, and Docker decisions

Status: **non-runnable v3.0 decisions**, 2026-10-30, for
system-security-01 through -03. These are active v2 preset outcomes, so each
is listed explicitly rather than hidden behind a deferred bundle.

## Completion criteria defined for this review

- Identify the exact v2 mutation, current Fedora 44 mechanism, declared
  desired state, and any inverse before allowing a catalog operation.
- Preserve administrator-owned files and Docker data. An interactive prompt,
  broad system update, or external repository is not represented as a
  successful no-op. A future runnable handler needs an observable result and
  a declared recovery limit, with disposable VM evidence for its risk.
- Compare catalog, profile, and run-state contracts with Windows; document a
  specific reopening trigger rather than adding release-blocking optional
  coverage.

| Outcome | Decision and reason | Reopen when |
| --- | --- | --- |
| `Hostname` | **Unsupported.** `SetHostname` prompts for an arbitrary static name and calls `hostnamectl`; no desired name is declared by a v3 profile, and v2 has no exact prior-name restore. Public profiles must not contain a host identity. | Add a site-private or parameterized hostname setting with input validation, explicit target ownership, prior-name journal, and VM apply/restore evidence. |
| `FastDNF` | **Unsupported.** v2 edits `/etc/dnf/dnf.conf` in place for `fastestmirror=true` and 15 parallel downloads; its inverse deletes matching lines rather than restoring prior administrator values. [DNF5's current reference](https://dnf5.readthedocs.io/en/stable/dnf5.conf.5.html) still documents a default of three parallel downloads, so defaults are not an equivalent replacement. | Add an owned DNF5 override or exact-file recovery, compare actual Fedora 44 behavior, and pass conflict/restore tests. |
| `UpdateFedora` | **Unsupported.** The active v2 action runs `dnf update -y` across the host with no planned package set, repeat-state observation, or rollback. The package install handler does not represent a system upgrade. | Define a bounded, non-reversible update action with transaction inventory, failure/reboot reporting, and disposable Workstation recovery evidence. |
| `Docker` | **Unsupported.** v2 adds Docker's external Fedora repository, installs engine/CLI/containerd, and starts the daemon; removal deletes packages and the repo file without preserving images, volumes, service state, or pre-existing repo ownership. | Accept a pinned publisher key/repository and owned file/service/data boundary, then pass seeded-volume and recovery tests on Fedora 44 Workstation. |

The v3 base and opt-in package profiles remain unchanged. These decisions
do not imply that DNF5, host naming, operating-system updates, or Docker are
unavailable outside RIDE; they state that the v2 actions have no validated
declarative v3.0 lifecycle yet.
