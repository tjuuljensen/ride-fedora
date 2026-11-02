# Security Lab network diagnostics package acceptance

Batch 06AC covers `flawfinder`, `sslscan`, `subnetcalc`, and `swaks` as Fedora
44 Workstation x86_64 opt-in candidate RPM operations. RIDE manages package
presence only; it does not scan source, contact endpoints, or perform SMTP
transactions.

## Completion checks

- Confirm exact source group membership and isolated profile mapping.
- Confirm candidate refusal creates no run journal.
- On the disposable Fedora 44 Workstation target, plan, apply, verify RPM
  signatures and files, query status, repeat, and restore.
- Inspect RPM scripts, file capabilities, dependencies, existing RPM changes,
  and service activation.
- Confirm package inventory returns to baseline.

## VM evidence

Passed on 2026-10-31 using `fedora-44-workstation-x86_64`. All four packages
were absent initially. Candidate refusal created no journal; apply installed
the four Fedora RPMs; repeat reported each unchanged; restore removed them and
all 15 newly installed dependencies (two GeoIP packages for SubNetCalc and 13
Perl packages for Swaks). No pre-existing RPM changed. All four RPMs had
RSA/SHA256 header signatures and passed root-run `rpm -V`; all had no file
capabilities or RPM scriptlets, and no system service units. Package inventory
returned to baseline. No source was scanned, network endpoint contacted, or
mail sent.

Run IDs: apply `20261031T151607Z-2800-27667`, repeat
`20261031T151633Z-5251-4834`, restore `20261031T151634Z-5854-2914`. Pytest
reported `1 passed`. Transcript: `.tmp-vm-acceptance-security-06ac-retry/fedora-44-workstation-x86_64/20261031T151537Z-test-fedora-security-lab-network-diagnostics-batch-and-profile-1c7a75c3/transcript.jsonl` (SHA-256 `a31f2f5d6e26875f2701370faac136fd544122579562456afd4c011132bb176c`).

The first attempt failed only on a whole-VM active-service-list comparison: a
NetworkManager dispatcher unit disappeared while transient PackageKit and
`systemd-run` units appeared during VM startup. The transcript showed no
package-owned service units. The test now checks unit files shipped by the
requested RPMs and the fresh-overlay retry passed. DNF also logged HTTP 500
responses from one Fedora mirror while resolving metadata; it completed the
transactions, package signatures and files verified, and the complete lifecycle
passed without another retry. H054 tracks authorized source and network use,
SMTP side effects, and output retention before these tools are run.
Catalog operation IDs in this accepted profile: `package.flawfinder`, `package.sslscan`, `package.subnetcalc`, `package.swaks`.
