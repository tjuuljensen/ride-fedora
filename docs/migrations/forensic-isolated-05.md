# NetworkMiner publisher artifact and evidence-data ownership

Status: **isolated review pending**, 2026-10-30. The active v2
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
