# Fedora 44 acceptance: package.aide

**Result: PASS (candidate)**

`package.aide` passed the package-only lifecycle on Fedora 44 Workstation
x86_64 as part of the opt-in Security Lab host integrity profile. Its Fedora
RPM signature and root-run `rpm -V` passed; status, repeat apply, and restore
also passed. See the combined [06N acceptance report](security-lab-host-integrity.md).
No scanner, policy evaluation, AIDE database initialization, or remediation ran.
