# System and security batch 28: ClamAV signatures

Status: **unsupported for v3.0**, 2026-10-30. The v2 pair installs `clamav` and
`clamav-update`, then runs `freshclam`; removal uninstalls the RPMs but does
not restore downloaded signature state. Review current Fedora package names,
signature acquisition, any service/configuration effects, detection,
ownership of the signature database, and safe failure/recovery in an isolated
VM before making this security operation runnable. A signed RPM install alone
does not fulfill the v2 outcome because `freshclam` is part of its apply path.
Reopen when a bounded signature acquisition and freshness policy, isolated
database ownership, failure reporting, and seeded-database recovery pass on
Fedora 44 Workstation. No state-changing VM test was run for this non-runnable
decision.
