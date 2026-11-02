# Fedora 44 acceptance: package.powertop

**Result: PASS**

`package.powertop` passed the supported Fedora 44 Workstation x86_64 VM
lifecycle without candidate bypass. The signed RPM passed `rpm -V`;
`powertop --version`, status, repeat apply, and restore passed. The test did
not calibrate or tune power settings. See the combined [system monitoring
acceptance](security-lab-system-monitoring.md).
