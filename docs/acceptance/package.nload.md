# Fedora 44 acceptance: package.nload

**Result: PASS**

Disposable VM run: PASS on Fedora 44 Workstation x86_64.

The supported operation `package.nload` passed signature verification, `rpm -V`,
local help/version probing, status, repeat apply, and restoration in the
combined [Security Lab network utilities acceptance](security-lab-network-utilities.md).
The package was absent before the run, present after apply, and absent after
restore. The combined record also confirms the exact RPM inventory returned to
its pre-run state.
