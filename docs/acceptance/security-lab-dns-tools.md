# Security Lab DNS utilities acceptance

**Result: PASS**

Disposable VM run: PASS on Fedora 44 Workstation x86_64.
Pinned image SHA-256: `49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
Date: 2026-10-31.

Operations: `package.dnsenum`, `package.dnstracer`, `package.dnstop`, and
`package.fpdns`, in the opt-in `fedora-security-lab-dns-tools` profile. No
base profile selects these tools.

## Checks and result

- Candidate plan listed all four operations. Apply without
  `--allow-candidate` was refused without creating a journal. Explicit apply
  installed all four signed Fedora RPMs.
- Each RPM had signature metadata and passed `rpm -V`. `dnsenum --help`,
  `dnstracer -h`, and `dnstop -h` printed local usage text. The latter two
  report an invalid `-h` option but exit immediately without a host or capture
  interface. `fpdns -v` printed `fpdns version 0.10.0` and exited 255; the
  automated check validates this exact version output and observed exit code.
  No DNS query, packet capture, or domain enumeration was run.
- Status reported installed for every operation. Repeat apply reported all
  four unchanged. Restore completed and removed the selected tools and all
  newly introduced dependencies.
- The DNF transaction for DNSenum installed 46 packages and explicitly
  replaced three existing Fedora Perl RPMs: `perl-Errno`
  `1.38-523.fc44` → `1.38-525.fc44`, and `perl-interpreter` plus `perl-libs`
  `5.42.1-523.fc44` → `5.42.3-525.fc44`. Restore retained those Fedora
  updates and returned every other RPM to baseline. Inventory was 1,913
  packages before apply, 1,962 after apply, and 1,913 after restore.

The automated lifecycle is
[`test_fedora_security_lab_dns_tools_batch_and_profile`](../../tests/acceptance/test_package_contract.py). VM transcripts and overlays are retained under `.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06g/`.
