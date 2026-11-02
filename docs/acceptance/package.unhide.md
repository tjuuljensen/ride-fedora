# `package.unhide` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64,
2026-11-01.

Fedora 44 Workstation x86_64 candidate RPM operation for unhide
20240510-3.fc44. Fedora lists GPL-3.0-or-later AND MIT and the
[unhide-forensics upstream](https://www.unhide-forensics.info/). RIDE manages
RPM presence only; it does not run process or port visibility scans.

The package lifecycle, executable presence, signature, file verification,
status, unchanged repeat, restore, and explicit removal passed. It introduced
only its requested RPM, which restore removed with the inventory returned to
baseline. No process or port scan was run. See the
[06AH batch acceptance report](security-lab-process-inspection.md).
