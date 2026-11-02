# `package.scanmem` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64,
2026-11-01.

Fedora 44 Workstation x86_64 candidate RPM operation for scanmem 0.17-23.fc44.1.
Fedora lists GPL-3.0-or-later AND LGPL-3.0-or-later and the upstream
[scanmem repository](https://github.com/scanmem/scanmem). RIDE manages RPM
presence only; it never inspects or modifies process memory.

The package lifecycle, executable presence, signature, file verification,
dependency closure, status, unchanged repeat, restore, and explicit removal
passed. Fedora also installed `scanmem-libs`; restore removed both RPMs with
the inventory returned to baseline. No process memory was inspected or
modified. See the [06AH batch acceptance report](security-lab-process-inspection.md).
