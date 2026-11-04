# Security Lab system diagnostics and performance monitoring acceptance

**Result: PASS**

The supported lifecycle for `package.inxi`, `package.pcp-system-tools`,
`package.powertop`, and `package.sysstat` passed on a disposable Fedora 44
Workstation x86_64 VM on 2026-10-31 without candidate bypass. The candidate
lifecycle also passed before promotion. The profile remains opt-in.

The VM checked plan, candidate refusal without a journal, candidate apply,
RPM signatures, `rpm -V`, local read-only version/manifest probes, status,
repeat apply, and restore. A supported-path rerun repeated plan/apply/status,
verification, idempotence, and restore. No power calibration or performance
collection command was run.

DNF installed the four selected RPMs with 61 additional packages, and updated
three existing Perl RPMs: `perl-Errno` 1.38-523.fc44 to 1.38-525.fc44,
`perl-interpreter` 4:5.42.1-523.fc44 to 4:5.42.3-525.fc44, and `perl-libs`
4:5.42.1-523.fc44 to 4:5.42.3-525.fc44. The DNF transaction explicitly
reported these replacements. Restore removed the selected RPMs and newly
introduced dependencies, and returned those three replacements to the same
post-update versions. The test compares exact RPM inventories and accepts only
those transaction-reported replacements.

Installing sysstat enabled its package-owned `sysstat-summary.timer`; restore
removed that enablement. The `pmcd` and `pmlogger` services remained inactive
through install and restore. The timer behavior is a documented side effect of
selecting this opt-in profile.

A first candidate attempt stopped during package installation after a
configured Fedora mirror timed out; the `/tmp` transcript also hit its local
quota. No external machine or user data was involved. The failure was
investigated, and fresh-overlay candidate and supported reruns passed with
transcripts stored on the repository filesystem.

Automated by
[`test_fedora_security_lab_system_monitoring_batch_and_profile`](../../tests/acceptance/test_package_contract.py).
Candidate transcript:
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06k-retry/fedora-44-workstation-x86_64/20261031T133325Z-test-fedora-security-lab-system-monitoring-batch-and-profile-f2d9e93e/`.
Supported transcript: `.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06k-final/fedora-44-workstation-x86_64/20261031T134011Z-test-fedora-security-lab-system-monitoring-batch-and-profile-baf5c992/`.
