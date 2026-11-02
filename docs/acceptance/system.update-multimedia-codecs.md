# Fedora Multimedia package update acceptance

**Result: PASS** for Fedora 44 Workstation x86_64 on 2026-10-31.

Disposable VM run: `20261031T102550Z-test-fedora-multimedia-update-is-fixed-set-and-non-reversible-e6c344c2`.
Operation: `system.update-multimedia-codecs`.
The verified image SHA-256 was
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
The run transcript and VM metadata were retained under
`.tmp-vm-acceptance/fedora-44-workstation-x86_64/` for this workspace session.

The operation used the fixed Fedora 44 package-name allowlist and queried only
members already installed in the image. Plan reported the operation as
outdated. Apply displayed the DNF5 `--assumeno` preview and completed the
update. The DNF history reports 44 package upgrades and one weak-dependency
install (`libdnf5-plugin-systemd-inhibit`); 14 installed Multimedia members
changed version, while `gstreamer1-plugin-dav1d` was already current. The
conditional `gstreamer-plugins-espeak` member was absent and was not installed.
All 1,913 baseline RPM name/architecture identities remained; the single new
RPM was the DNF5 weak dependency. Updated packages had RPM signatures and
passed `rpm -V`.

Status reported `current`. A repeated apply returned `unchanged`. Profile
removal explicitly kept the non-reversible update, and restore refused to
claim exact recovery. The RPM inventory and versions after removal/restore
matched the post-update inventory. No package was removed or downgraded.

Focused mocked tests passed: `python3 -m unittest
tests.test_v3_dnf_package_set_update` (6 tests). The VM acceptance test passed:
`tests/acceptance/test_package_contract.py::test_fedora_multimedia_update_is_fixed_set_and_non_reversible`.

The operation is supported only for Fedora 44 Workstation x86_64 and remains
opt-in through `fedora-codecs-updates`. DNF may upgrade dependencies beyond
the named Multimedia packages; the transaction preview is required before
apply, and package updates have no exact inverse. Broader transaction-impact
and recovery reporting is tracked as v3.1 hardening H037.
