# Whole-system update acceptance

- Operation: `system.update-all-packages`
- Handler: `dnf5-system-update`
- Scope: explicit DNF5 whole-system update; non-restorable; never auto-reboots.

## Acceptance checks

The disposable Fedora 44 Workstation and Server tests run `plan`, preview and
apply through `ride.sh update`, inspect the private journal for a transaction
report, confirm the system is current, and verify that restore refuses the
non-restorable run. The mocked tests cover check-upgrade exit/JSON agreement,
preview refusal, transaction NEVRA capture, reboot assessment, and a failed
upgrade.

## Results

### Fedora 44 Workstation x86_64

The pinned base image SHA-256 is
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
The full update transaction completed all 1,693 DNF steps (835 upgrades, 19
installs, and 837 replacements) and generated DNF transaction ID 2. The first
RIDE invocation then failed while creating its report: passing full DNF history
as one `jq` argument exceeded the operating system argument limit. The guest
overlay was retained as evidence; no persistent machine was changed.

- Full transaction transcript:
  `.acceptance-runs/fedora-44-workstation-x86_64/20261102T121017Z-test-system-update-workstation-is-reported-and-nonrestorable-37b604b9/transcript.jsonl`
- Transcript SHA-256: `17d2e4fa7d1ae39bbee7b8fca4fdd85ba766150ce680ecfd5b6db9e252184469`
- Derived updated overlay SHA-256: `5b404f4d720a070644e7caf0ca73cfa8b6a30d355547da8c6ba1e582d702f7b3`

The report path now streams history JSON to `jq` on stdin. A mocked regression
test exercises 2,000 package entries. A disposable child VM of the completed
Workstation overlay then replayed the real transaction-2 history through a
DNF shim that performed no package mutation. RIDE applied the operation,
journaled all 1,691 recorded package NEVRAs and the shim-provided reboot
assessment, reported current status, repeated as unchanged, and refused restore
as non-restorable.

- Real-history report transcript:
  `.acceptance-runs/fedora-44-workstation-x86_64/20261102T130835Z-test-system-update-real-history-report/transcript.jsonl`
- Transcript SHA-256: `ed77ff923cd2d08906c18f0d288f7759995e8dc190915ec6d2ce0ca044fcb92c`

This reuses the completed package transaction and validates the changed report
and journal path against its actual DNF history; it is not a second full package
update. Focused DNF5 tests passed (6 tests, 2 subtests).

### Fedora 44 Server x86_64

The pinned Server base image SHA-256 is
`efb75956d6dbde0801059fdac4a8a1451f06ecc843344ecdb71bb3e8d247af90`.
The full DNF5 transaction completed successfully with transaction ID 2 and
735 package NEVRAs in the RIDE report. Fedora's reboot checker was available
and reported a reboot required for kernel, systemd, glibc, and related packages;
RIDE did not reboot automatically. The system reported current status, and
restore refused the non-restorable update run as expected.

- Transcript:
  `.acceptance-runs/fedora-44-server-x86_64/20261102T131245Z-test-system-update-server-is-reported-and-nonrestorable-e37d7435/transcript.jsonl`
- Transcript SHA-256: `039036e9805f1a34d3902d9443b72957a6c8da2df42f032973c2d088d2e6d9a2`
- Updated disposable overlay SHA-256:
  `7d67258325e162ddf84dbb438f0977844f9aed5bdaa336d6f60a168b51e1781d`
- Source bundle SHA-256:
  `43d735053998db0f9503f33389f9f66f73f5a646451ccba612aab7d880c7dd8d`

The full transaction required 1,550 seconds under TCG emulation. No persistent
machine was changed. The acceptance test passed on Fedora 44 Server x86_64.
