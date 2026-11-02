# Security Lab network observation and packet analysis acceptance

Batch 06V covers `etherape`, `p0f`, `pads`, `pcapdiff`, and `ssldump` as
Fedora 44 Workstation x86_64 opt-in candidate package operations. The profile
manages RPM presence only. It does not capture traffic, open packet captures,
start services, or execute these tools.

## Completion checks

- Verify exact source group membership and profile mapping.
- Verify candidate refusal creates no run journal.
- On the disposable Fedora 44 Workstation target, plan, apply, check RPM
  signatures and root-run `rpm -V`, query status, repeat apply, and restore.
- Inspect RPM scripts and file capabilities; record package dependencies,
  existing RPM changes, and `pads.service` state before, during, and after.
- Confirm installed requested package identities are removed or preserved
  according to their initial state after restore.

## VM evidence

Passed on 2026-10-31 with the pinned disposable target
`fedora-44-workstation-x86_64` (Fedora 44 Workstation, x86_64). The exact
candidate-gating, plan, apply, repeat, status, RPM signature, root-run `rpm
-V`, and restore checks passed. Run IDs were `20261031T144758Z-3106-11477`
(apply), `20261031T144825Z-6034-22486` (repeat), and
`20261031T144826Z-6753-18091` (restore). All five requested packages were
initially absent and were removed after restore; the complete RPM inventory
returned to the expected post-DNF state and no pre-existing RPM changed.

DNF installed `pcre` for PADS and `python3-pcapy` for pcapdiff, then removed
both as unused dependencies during restore. `pads.service` remained
`not-found / inactive` before, during, and after the lifecycle. RPM inspection
found no file capabilities or install scripts except PADS systemd unit
registration/removal helpers; its unit was not enabled or started. No capture
file was opened, traffic captured, or tool executed.

The retained command transcript is
`.tmp-vm-acceptance-security-06v/fedora-44-workstation-x86_64/20261031T144726Z-test-fedora-security-lab-network-observation-batch-and-profile-f5e66a5c/transcript.jsonl`
(SHA-256 `0a03e059e26a71ef9a9fe2215bdb8c0687ebf980cb826b3fe305dd06b700ce74`);
pytest reported `1 passed`.

H047 tracks the later review needed before removing candidate gates: authorized
interfaces, capture permissions and ownership, sensitive packet-data handling,
service activation, and configuration/data recovery.
Catalog operation IDs in this accepted profile: `package.etherape`, `package.p0f`, `package.pads`, `package.pcapdiff`, `package.ssldump`.
