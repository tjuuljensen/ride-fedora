# `package.rats` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64,
2026-11-01.

Fedora 44's release repository carries the `rats` 2.4-31.fc44 x86_64 RPM,
licensed GPLv2. The Fedora package landing page has stale release listings; the
Fedora 44 release artifact and its repository GPG verification are the
acquisition evidence for this target. Upstream is the archived
[stgnet/RATS export](https://github.com/stgnet/rats).

The operation manages package presence only. The pinned Fedora 44 Workstation
lifecycle passed: the signed RPM had no dependencies or scriptlets, and its
binary plus six bundled language databases were present. No scan was run. See
the [06AN batch report](security-lab-rats.md). H065 tracks current analyzer
alternatives for v3.1.
