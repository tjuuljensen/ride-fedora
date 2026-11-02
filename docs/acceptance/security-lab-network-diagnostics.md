# Fedora Security Lab network diagnostics profile acceptance

Status: passed disposable Fedora 44 Workstation x86_64 acceptance on 2026-10-31.

Target: Fedora 44 Workstation, x86_64. Profile:
`fedora-security-lab-network-diagnostics`.

The focused disposable-VM check covers `macchanger`, `mtr`, `nethogs`, and
`whois`. It checks exact group membership, candidate refusal, plan, apply,
repeat, status, Fedora RPM signature metadata, root-run `rpm -V`, and command
availability. It restores the apply run and checks the original RPM
name/architecture set. Existing individual Fedora 44 lifecycle evidence for
these package operations is reused. The test does not run `macchanger`,
capture packets, or contact external lookup services.

Transcript: `/tmp/ride-fedora-security-lab-06d/fedora-44-workstation-x86_64/20261031T080443Z-test-security-lab-network-diagnostics-profile-a9fc0f69/transcript.jsonl`

Runs: apply `20261031T080843Z-2760-21037`; repeat
`20261031T081018Z-3977-6521`; exact restore
`20261031T081045Z-5028-31459`. Package signature metadata and root-run RPM
verification passed. The repeat reported all four packages unchanged, and
restore returned the RPM name/architecture set to its recorded baseline.
The test did not run diagnostic commands against the network or host.
Catalog operation IDs in this accepted profile: `package.macchanger`, `package.mtr`, `package.nethogs`, `package.whois`.
