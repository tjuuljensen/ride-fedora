# SmartMonTools package acceptance

Status: operable opt-in candidate; Fedora 44 Workstation x86_64 lifecycle passed on 2026-11-02.

## Declared scope

`package.smartmontools` installs the signed Fedora RPM and immediately disables
and stops `smartd.service`, undoing the RPM's observed enablement side effect.
It does not enable monitoring, select devices, read SMART attributes, or alter
`smartd.conf`. The operation is opt-in.

## Completion checks

- Plan reports the candidate and denies apply without explicit candidate consent.
- Apply installs and verifies the signed RPM, leaves `smartd.service` disabled
  and inactive, and does not run `smartd`.
- Repeat and status report installed without changing state.
- Restore and explicit remove return to the pre-install RPM baseline and remove
  the package-provided service unit.

## Fedora target result

Passed on disposable Fedora 44 Workstation x86_64. The test completed candidate
refusal without consent, signed RPM and file verification, disabled/inactive
`smartd.service`, status, repeat apply, restore, explicit remove, and package
baseline recovery.

- Image: SHA-256 `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`
- Transcript: `.acceptance-runs/fedora-44-workstation-x86_64/20261102T111500Z-test-smartmontools-package-lifecycle-keeps-smartd-disabled-4e3fca6b/transcript.jsonl`
- Transcript SHA-256: `7d0280da6779c1fc400d7740dd23eacd1167ed74f028a3d1368c03bbcb543682`
- Result: `1 passed in 822.13s`

The earlier generic DNF-handler failure remains historical context in
`docs/migrations/system-security-smartmontools.md`; it is superseded for this
operation by the dedicated handler lifecycle above.
