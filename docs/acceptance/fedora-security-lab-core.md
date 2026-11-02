# Fedora Security Lab core profile acceptance

Status: **PASS** on Fedora 44 Workstation x86_64, 2026-10-31.

The `fedora-security-lab-core` opt-in profile composes six accepted Fedora
package operations that are members of the 137-package `security-lab` group:
`package.binwalk`, `package.dc3dd`, `package.htop`, `package.lynis`,
`package.pwgen`, and `package.vim-enhanced`. The test queried the current group
on the target, confirmed each package is a member, verified the profile plan,
applied the profile, repeated it, checked each operation's status, ran
`rpm -V` and checked installed signature metadata for all six packages, then
removed the profile.

All six selected packages were absent on the pinned image. Apply installed
them and their required dependencies; repeat reported all six unchanged.
Removal removed the six packages and their newly added dependencies. The
pre-existing RPM name/architecture set was restored exactly. As observed in
the DNF transaction, installing `vim-enhanced` upgraded existing
`vim-minimal` and `vim-data` from 9.2.240 to 9.2.1202 to match Fedora's
available Vim build. Those two upgrades remained after profile removal; no
other prior package identity or version changed, and no downgrade was
attempted.

Test: `tests/acceptance/test_package_contract.py::test_security_lab_core_reuses_accepted_package_operations`.
Passing run artifacts: `/tmp/ride-fedora-security-lab-06a/fedora-44-workstation-x86_64/20261031T063015Z-test-security-lab-core-reuses-accepted-package-operations-2d0cd808/`.
The first run exposed the Vim dependency upgrades and failed a version-exact
baseline assertion. The transaction and package inventory delta were reviewed;
the predeclared rerun check allows only those two Fedora-required upgrades.
The fresh-overlay rerun passed in 711.48 seconds.

This is a partial migration of the group source outcome, not a v3 replacement
for the 137-package DNF group action. The full package inventory and mapping
state are recorded in `migration/security-lab-inventory.json`.
