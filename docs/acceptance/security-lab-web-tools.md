# Security Lab web and HTTP package acceptance

Batch 06Z covers `goaccess`, `httpd-tools`, `httrack`, and `wget2-wget` as
Fedora 44 Workstation x86_64 opt-in candidate RPM operations. RIDE manages
package presence only; acceptance does not read logs, retrieve sites, connect
to remote hosts, or start an HTTP service.

## Completion checks

- Verify exact source group membership and profile mapping.
- Verify candidate refusal creates no run journal.
- On the disposable Fedora 44 Workstation target, plan, apply, verify RPM
  signatures and files, query status, repeat apply, and restore.
- Inspect package scripts, file capabilities, services, dependencies, and
  changes to pre-existing RPMs.
- Confirm package identities and `httpd.service` state return to the expected
  post-DNF state after restore.

## VM evidence

Passed on 2026-10-31 with the pinned disposable target
`fedora-44-workstation-x86_64` (Fedora 44 Workstation, x86_64). Candidate
refusal, plan, apply, RPM signature and file checks, status, repeat, restore,
and package identity recovery passed. Run IDs were
`20261031T150320Z-2855-6774` (apply), `20261031T150338Z-5022-26744`
(repeat), and `20261031T150339Z-5627-10639` (restore). GoAccess and HTTrack
were installed then removed; `httpd-tools` and `wget2-wget` were already
installed and remained unchanged. No dependencies or pre-existing RPM changes
were observed. `httpd.service` stayed `not-found / inactive` before, during,
and after. No logs were read and no site or server was accessed.

The retained command transcript is
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06z/fedora-44-workstation-x86_64/20261031T150249Z-test-fedora-security-lab-web-tools-batch-and-profile-04f11a1b/transcript.jsonl`
(SHA-256 `41d3a8d833a070d24ea7eb8bc00e8d6cbc69c8c72d278ca373e78daef36f6533`);
pytest reported `1 passed`. H051 tracks private-log handling, approved
retrieval scope, download controls, and output cleanup before client behavior
is exercised.
Catalog operation IDs in this accepted profile: `package.goaccess`, `package.httpd-tools`, `package.httrack`, `package.wget2-wget`.
