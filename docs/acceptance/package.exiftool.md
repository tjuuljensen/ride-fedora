# `package.exiftool` acceptance

Status: **PASS; supported Fedora RPM** on Fedora 44 x86_64 Workstation,
2026-10-30. The active v2 `InstallExifTool` source build is migrated to
Fedora's signed
[`perl-Image-ExifTool`](https://packages.fedoraproject.org/pkgs/perl-Image-ExifTool/perl-Image-ExifTool/)
RPM, which provides the `exiftool` command. Its Fedora license expression is
GPL-1.0-or-later OR Artistic-1.0-Perl. The v3 operation does not install
CPAN prerequisites or manage `/usr/lib/exiftool` from the legacy build.

VM evidence: pinned Workstation image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`;
disposable overlay
`20261030T121723Z-test-forensic-exiftool-fedora-package-f1842a80`;
candidate catalog SHA-256
`1b09ecf5d8c533cbca6952802b8054c3fb399b341f44e2b1a560986861bcf9f2`.
The retained transcript and
`.acceptance-runs/forensic-isolated-01-exiftool-retry.xml` record one passing
test. The RPM was absent at baseline. The test passed absent plan,
candidate-gated apply, signed RPM and file verification, `exiftool -ver`,
installed status, unchanged repeat, restore, and explicit install/remove.
Only `perl-Image-ExifTool` 13.50 was introduced; both inverse paths returned
the full RPM inventory to baseline. `/usr/lib/exiftool` stayed absent.
The final supported catalog status removes the temporary candidate gate
used during the pilot; the handler and target did not change.

The first disposable overlay failed during test fixture preparation before
any v3 operation: the mixed-case RPM name was rejected as a guest fixture
filename. The focused test now lowercases only that filename. The failed
run is not package acceptance evidence. Mocked failure evidence for the
unchanged DNF handler is in the [base package checks](package.exfatprogs.md).
See the [batch review](../migrations/forensic-isolated-01.md).
