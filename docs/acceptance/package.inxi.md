# Fedora 44 acceptance: package.inxi

**Result: PASS**

`package.inxi` passed the supported Fedora 44 Workstation x86_64 VM lifecycle
without candidate bypass. The signed RPM passed `rpm -V`; `inxi --version`,
status, repeat apply, and restore passed. See the combined [system monitoring
acceptance](security-lab-system-monitoring.md), including exact DNF dependency
update evidence.
