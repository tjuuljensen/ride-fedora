# Security Lab network-load tools acceptance

Batch 06R covers Siege, SIPp, SIPSAK, sockperf, and uperf as Fedora RPM
presence operations in the opt-in `fedora-security-lab-network-load-tools`
profile. Package metadata and license sources are linked from the [batch
record](../migrations/provider-foundation-06.md).

The pinned Fedora 44 Workstation x86_64 candidate lifecycle passed on
2026-10-31. Candidate refusal, plan, apply, signature checks, root-run `rpm -V`,
status, repeat apply, restore, and exact package inventory recovery all passed.
DNF added `libjoedog`, `gsl`, and `pugixml`; it changed no preexisting RPM
identity or version. Package scripts and file-capability metadata were
inspected. The tools were not executed, HTTP/SIP traffic was not sent, and
benchmark sockets were not opened. The run transcript and overlay are under
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06r/fedora-44-workstation-x86_64/20261031T142904Z-test-fedora-security-lab-network-load-batch-and-profile-fed044db/`.

All operations remain opt-in and candidate-gated pending H043 review of
authorized endpoints, bounded traffic, capture effects, and recovery.
Catalog operation IDs in this accepted profile: `package.siege`, `package.sipp`, `package.sipsak`, `package.sockperf`, `package.uperf`.
