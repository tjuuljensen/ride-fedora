# System and security batch 28: ClamAV signatures

Status: **unresolved**, 2026-10-30. The v2 pair installs `clamav` and
`clamav-update`, then runs `freshclam`; removal uninstalls the RPMs but does
not restore downloaded signature state. Review current Fedora package names,
signature acquisition, any service/configuration effects, detection,
ownership of the signature database, and safe failure/recovery in an isolated
VM before making this security operation runnable.
