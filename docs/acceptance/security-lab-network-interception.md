# Security Lab network interception package acceptance

Batch 06AB covers `ArpON`, `hunt`, `netsed`, and `sslsplit` as Fedora 44
Workstation x86_64 opt-in candidate RPM operations. RIDE manages package
presence only; it does not attach interfaces, alter routes or firewall rules,
capture or modify traffic, terminate TLS, or run these tools.

## Completion checks

- Verify exact source group membership and isolated profile mapping.
- Verify candidate refusal creates no run journal.
- On the disposable Fedora 44 Workstation target, plan, apply, verify RPM
  signatures and files, query status, repeat, and restore.
- Inspect RPM scripts, file capabilities, dependencies, existing RPM changes,
  and `arpon.service` state without starting it.
- Confirm package inventory and service state recover after restore.

## VM evidence

Passed on 2026-10-31 using `fedora-44-workstation-x86_64`. Plan showed all
four packages absent and candidate-gated; apply without `--allow-candidate`
was refused without a journal. Apply installed all four signed Fedora RPMs;
repeat reported all unchanged; restore removed all four and also removed the
newly installed `libdnet` dependency. No pre-existing RPM changed. All four
RPMs had valid RSA/SHA256 header signatures, passed root-run `rpm -V`, declared
no file capabilities, and had no RPM scriptlets. `arpon.service` remained
inactive before, during, and after. Package inventory returned to baseline.
No interface, route, firewall, capture, TLS, or tool behavior was exercised.

Run IDs: apply `20261031T151035Z-2845-9650`, repeat
`20261031T151058Z-5082-1379`, restore `20261031T151059Z-5686-27475`. Retained
transcript: `.tmp-vm-acceptance-security-06ab/fedora-44-workstation-x86_64/20261031T151005Z-test-fedora-security-lab-network-interception-batch-and-profile-e281b8f9/transcript.jsonl` (SHA-256 `65bee067d51cd1165a98b0a2eae20e0a3c246de048268dd6f90b61a959dcc2d2`). Pytest reported
`1 passed`. H053 tracks authorized use and network recovery before behavior
is offered.
Catalog operation IDs in this accepted profile: `package.arpon`, `package.hunt`, `package.netsed`, `package.sslsplit`.
