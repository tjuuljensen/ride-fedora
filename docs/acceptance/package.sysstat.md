# Fedora 44 acceptance: package.sysstat

**Result: PASS**

`package.sysstat` passed the supported Fedora 44 Workstation x86_64 VM
lifecycle without candidate bypass. The signed RPM passed `rpm -V`; `sar -V`,
status, repeat apply, and restore passed. Fedora enabled the package-owned
`sysstat-summary.timer` while installed; restore removed the timer enablement.
See the combined [system monitoring acceptance](security-lab-system-monitoring.md).
