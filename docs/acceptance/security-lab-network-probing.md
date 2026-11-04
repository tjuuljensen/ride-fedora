# Security Lab active network probing acceptance

**Result: PASS (candidate)**

The candidate lifecycle passed on a disposable Fedora 44 Workstation x86_64
VM on 2026-10-31 for `package.firewalk`, `package.lbd`, `package.masscan`,
and `package.zmap`, selected by the opt-in
`fedora-security-lab-network-probing` profile.

The automated test verified plan, candidate refusal without a journal,
explicit candidate apply, RPM signatures, `rpm -V`, status, repeat apply, and
restore with exact package inventory comparison. All four selected RPMs were
absent in the baseline. DNF installed four requested packages and six new
dependencies. It also updated four existing dependencies, explicitly shown in
its transaction output: `libibverbs` 61.0-2.fc44 to
61.1^20260812git975bdaf-1.fc44; `libpcap` 1.10.6-2.fc44 to 1.10.7-1.fc44;
`librdmacm` 61.0-2.fc44 to 61.1^20260812git975bdaf-1.fc44; and
`rdma-core-common` 61.0-2.fc44 to 61.1^20260812git975bdaf-1.fc44. Restore
removed the selected RPMs and six new dependencies. Exact inventory comparison
showed only those four named dependency updates remained.

RPM scriptlets were empty, all package executables had no file capabilities,
and the default `/etc/zmap` configuration was absent after restore. The test
did not invoke a scanner, resolve a target, send probes, open an interface, or
capture traffic. Operations remain candidate-gated pending separate
authorized-scope behavior review.

Automated by
[`test_fedora_security_lab_network_probing_batch_and_profile`](../../tests/acceptance/test_package_contract.py).
Transcript: `.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06m/fedora-44-workstation-x86_64/20261031T135912Z-test-fedora-security-lab-network-probing-batch-and-profile-be1a3891/`.
