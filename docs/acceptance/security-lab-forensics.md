# Fedora Security Lab forensic profile acceptance

Status: **PASS; opt-in candidate** on Fedora 44 Workstation, x86_64,
2026-10-31.

Target: Fedora 44 Workstation, x86_64. Profile:
`fedora-security-lab-forensics`.

The focused disposable-VM check covers the three Security Lab members
`ewftools`, `sleuthkit`, and `testdisk`. It checks exact group membership,
candidate refusal, plan, first apply, repeat, status, Fedora RPM signature
metadata, root-run `rpm -V`, and read-only `ewfinfo -V`, `mmls -V`, and
`testdisk /version` probes. It restores the apply run and checks the original
RPM name/architecture set. No evidence image is mounted or modified.

The group query confirmed all three exact members. The three packages were
absent before apply. Candidate apply was refused without
`--allow-candidate`; plan showed all three desired installed. Apply run
`20261031T075859Z-2627-24424` installed `ewftools`, `sleuthkit`, and
`testdisk`, with signed Fedora RPM metadata and successful root-run `rpm -V`.
Read-only probes `ewfinfo -V`, `mmls -V`, and `testdisk /version` passed.
Repeat run `20261031T080115Z-3707-18926` reported all three unchanged. Exact
restore run `20261031T080138Z-4525-32735` removed the three new packages and
their unused dependencies. Pre-run and post-restore RPM name/architecture
sets and versions matched exactly. No evidence image was mounted or modified.

Transcript: `/tmp/ride-fedora-security-lab-06c/fedora-44-workstation-x86_64/20261031T075458Z-test-security-lab-forensic-recovery-profile-a8b058c7/transcript.jsonl`.
Catalog operation IDs in this accepted profile: `package.ewftools`, `package.sleuthkit`, `package.testdisk`.
