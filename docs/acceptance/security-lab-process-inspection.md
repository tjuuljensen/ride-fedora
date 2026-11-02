# Security Lab process and host inspection acceptance

Batch 06AH covers Fedora 44 Workstation x86_64 candidate RPMs `scanmem`
(0.17-23.fc44.1, GPL-3.0-or-later AND LGPL-3.0-or-later) and `unhide`
(20240510-3.fc44, GPL-3.0-or-later AND MIT). Both use Fedora's signed RPM
repository. The opt-in profile installs the RPMs only; no process memory,
rootkit indicators, ports, or user data are inspected.

## Completion checks

- Confirm these two inventory members map only to this profile and both
  operations remain candidates for Fedora 44 Workstation x86_64.
- Verify candidate refusal without a journal, absent plan, apply, RPM signature
  and root-run `rpm -V`, status, repeat, restore, and explicit remove.
- Compare exact RPM inventory before and after. Inspect dependency changes,
  existing package updates, capabilities, scriptlets, and systemd units.
- Do not run either scanner, attach to processes, read or alter process memory,
  inspect user data, or change host security state.

## VM evidence

Passed on 2026-11-01 on the pinned Fedora 44 Workstation x86_64 target, KVM.
The base image SHA-256 was
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
Both operations remained opt-in candidates. Candidate refusal created no run
journal; each absent package then planned, applied, passed RPM signature and
root-run `rpm -V` checks, reported installed status, repeated unchanged,
restored, and passed explicit install/remove. Full RPM inventories returned to
their initial state with no pre-existing package identity or version changes.

`scanmem` installed its RPM and `scanmem-libs`; restore removed both. The
transaction installed 2 packages, with no other dependencies. `unhide`
installed one RPM and had no package dependencies. Both packages had no RPM
scriptlets, file capabilities, or systemd units. Executables were verified at
`/usr/bin/scanmem` and `/usr/bin/unhide`. Neither tool was run; no process,
memory, port, rootkit indicator, or user data was inspected.

| Operation | Apply run ID | Repeat run ID | Restore run ID | Transcript SHA-256 |
| --- | --- | --- | --- | --- |
| `package.scanmem` | `20261101T122542Z-2570-3923` | `20261101T122553Z-3404-12668` | `20261101T122554Z-3841-4573` | `7d9a92bad235ce8abd45833338b5600d9aff84ce63503192399e1e15ec9d22e8` |
| `package.unhide` | `20261101T122639Z-2571-8057` | `20261101T122650Z-3409-7219` | `20261101T122651Z-3846-27656` | `2dc88d78053357163e99b12be309fbf8235c55d9434a66cac422f998dfecf85b` |

Transcripts are retained under
`.tmp-vm-acceptance-security-06ah/fedora-44-workstation-x86_64/` in the
corresponding timestamped run directories. The focused result was `1 passed`
for each package. Two earlier harness setup attempts stopped before guest
startup: the first found the new pilots absent from the target matrix; the
second found host KVM unavailable inside the default sandbox. The target was
updated, and both acceptance runs then completed with host KVM access. No
guest state changed during the setup failures. H060 tracks later authorized
behavior review.
