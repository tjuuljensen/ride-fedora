# Fedora 44 acceptance: package.zmap

**Result: PASS (candidate)**

`package.zmap` passed the Fedora 44 Workstation x86_64 candidate VM lifecycle.
Its signed Fedora RPM passed `rpm -V`; RPM scriptlets were empty and packaged
executables had no file capabilities. Status, repeat apply, and restore
passed. Its default `/etc/zmap` configuration was removed on restore. No scan
was run. See the combined [network probing
acceptance](security-lab-network-probing.md).
