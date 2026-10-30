# `package.asn` and ASN runtime acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64.
Reviewer: Codex, 2026-10-30. The v3 user operation installs the MIT-licensed
upstream ASN 0.83.0 Bash script from commit
`9384c07a35f5689ab7730c88b391ec47a8f2a11e`, with exact SHA-256 checks
for the script and license. It does not run the downloaded script during
apply, start ASN's optional server, or manage `.asnrc`. Ten Fedora RPM
prerequisites are independent system operations in the opt-in `asn-runtime`
profile; the `asn-tool` user profile selects the script after they are
observed. Both profiles require `--allow-candidate` and remain outside
`default`.

The mapped operations are `package.asn`, `package.curl`, `package.whois`,
`package.dns-utils`, `package.mtr`, `package.jq`, `package.nmap`,
`package.ncat`, `package.ipcalc`, `package.aha`, and `package.grepcidr`.

One corrected disposable VM test passed in 568.60 seconds on the pinned
Fedora 44 Workstation x86_64 image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`
under QEMU TCG. The retained overlay is
`20261030T204256Z-test-asn-runtime-and-user-tool-bc07c906` under
`.acceptance-runs/asn/fedora-44-workstation-x86_64/`. Its `metadata.json`
records the pre-evidence catalog SHA-256
`716f72e5c470325641de9643e5e503237fadd359fc8cc969eba19544293aa4c6`,
source revision `b626c10`, and an uncommitted source bundle. The transcript
and `.acceptance-runs/asn-tcg.xml` retain the commands and result.

The VM checked both profile plans, candidate gates, apply and unchanged
repeat, all ten package signatures and `rpm -V` results, user status,
matching script and notice hashes, `asn -h` startup, and the command link.
User restore and explicit remove removed only the owned script path and link,
preserving a sibling file. System restore removed the newly installed named
RPMs and preserved all pre-existing RPM names. No manual session was needed.
Focused mocked tests cover failed download, wrong digest, occupied
destination, and modified owned directory refusal.

The first VM attempt failed only at a test assertion: ASN writes its help
text to stderr, while the test checked stdout. Its pinned hashes and startup
had passed. The assertion was corrected before the successful rerun; no
operational handler changed. During the system apply, installing `nmap`
upgraded the pre-existing `nmap-ncat` RPM from `4:7.92-8.fc44` to
`4:7.92-11.fc44`. `ipcalc` also pulled weak GeoLite dependencies. The
current DNF journal restores the requested package states, not prior
versions or dependency residue. H008 tracks broader package update effects;
this known transaction effect is disclosed before wider promotion.

[Batch checks](../migrations/forensic-isolated-01-asn.md) and
[Windows alignment](../windows-alignment.md#fedora-asn-pinned-script-preflight-2026-10-30)
record the scope. Live lookup accuracy, optional server behavior, and wider
network failure/recovery checks are H027 in v3.1. The fixed GitHub commit
and observed hashes are not an independent publisher signature.
