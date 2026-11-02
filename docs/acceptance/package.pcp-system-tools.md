# Fedora 44 acceptance: package.pcp-system-tools

**Result: PASS**

`package.pcp-system-tools` passed the supported Fedora 44 Workstation x86_64
VM lifecycle without candidate bypass. The signed RPM passed `rpm -V`; its
subpackage manifest, status, repeat apply, and restore passed. The acceptance
did not start PCP collectors. See the combined [system monitoring
acceptance](security-lab-system-monitoring.md).
