# Security Lab network monitoring acceptance

Batch 06T covers Argus, NFSwatch, nicstat, and vnStat as Fedora RPM presence
operations in the opt-in `fedora-security-lab-network-monitoring` profile.
Upstream and license metadata are linked from the [batch record](../migrations/provider-foundation-06.md).

The pinned Fedora 44 Workstation x86_64 candidate lifecycle passed on
2026-10-31. Candidate refusal, plan, apply, signatures, root-run `rpm -V`,
status, repeat apply, restore, and package identity recovery passed. DNF added
no dependencies and changed no existing RPM. `vnstat.service` remained
`not-found / inactive`; `/var/lib/vnstat` had no files before, during, or after.
The vnStat RPM created user/group `vnstat` (UID/GID 964), and the account
persisted after package removal. No services or monitoring tools were started.
No traffic was captured. Transcript and overlay:
`.tmp-vm-acceptance-security-06t/fedora-44-workstation-x86_64/20261031T143654Z-test-fedora-security-lab-network-monitoring-batch-and-profile-e0a34d84/`.

All four operations remain opt-in and candidate-gated pending H045 review of
authorized interfaces, service ownership, and data recovery.
Catalog operation IDs in this accepted profile: `package.argus`, `package.nfswatch`, `package.nicstat`, `package.vnstat`.
