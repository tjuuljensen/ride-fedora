# NetworkMiner publisher artifact and evidence-data ownership

Status: **unsupported for v3.0**, 2026-10-30. The active v2
`InstallNetworkMiner` downloads a mutable ZIP, installs Mono, extracts
into `/opt/NetworkMiner`, writes a desktop launcher, and changes the
`AssembledFiles` and `Captures` directories to group/world writable.
Its inverse must be reviewed separately from other forensic tools because
those directories may contain user evidence. The Windows development
catalog has a distinct official portable NetworkMiner deployment; Linux
must verify its own runtime, license, source, destination, and data recovery.

Before a runnable Linux candidate, define the current publisher artifact
and Linux runtime compatibility, pin and verify the bytes, preserve bundled
notices, journal only RIDE-owned files, and prove that captures and assembled
files survive repeat, failure, and removal. Use focused tests and a
disposable Fedora 44 x86_64 Workstation VM. If that cannot be established
for v3.0, record a reasoned non-runnable disposition and review trigger.

## Decision

The [publisher's current Linux guide](https://www.netresec.com/?month=2025-04&page=Blog&post=How-to-Install-NetworkMiner-in-Linux)
uses Mono and GTK2 with an official versioned ZIP; the [source is
GPL-2.0](https://www.netresec.com/?page=NetworkMinerSourceCode). Windows
already has a separate `package.networkminer` portable deployment for the
same product. Linux's active v2 function uses a moving download, makes
capture/output directories world writable, and its inverse removes the
entire `/opt/NetworkMiner` tree, including any captures. No v3 Linux
portable/data ownership handler or seeded-capture recovery evidence exists.
Therefore this source outcome is **non-runnable unsupported in v3.0**.
Reopen for an explicit Linux NetworkMiner use case with pinned official
bytes, Mono/GTK compatibility, preserved notices and captures, safe
permissions, and a disposable-VM failure/removal test. The Windows artifact
and acceptance do not establish Linux support.
