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

Results are pending execution on the declared disposable VM targets. Record
the target image digest, transcript path and SHA-256, DNF transaction ID, and
whether the reboot checker was available here before promoting the operation
to `supported`.
