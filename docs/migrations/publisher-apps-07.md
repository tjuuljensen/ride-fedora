# Logitech Unifying and conditional VM guest tools

The owner confirmed **keep** for VM guest tools in the v3.0 fast-track review.
Detect the actual hypervisor and install only its matching Fedora packages;
the v2 VMware-only inverse is insufficient.

Status: **one opt-in candidate and one non-runnable decision**, 2026-10-30. This active-preset batch maps
`InstallUnifyingOnLaptop` / `RemoveUnifyingOnLaptop` and
`InstallVMtoolsOnVM` / `RemoveVMtoolsOnVM`. The v2 Unifying function tests
for a battery and installs Fedora `solaar` and `acpi`; its inverse removes
only Solaar. The VM function checks DMI strings to choose VMware
`open-vm-tools` or QEMU `spice-vdagent` and `spice-webdavd`; its inverse
only handles VMware and uses a different DMI field.

## Completion criteria defined before implementation

- Replace implicit laptop detection with a curated opt-in Solaar profile
  containing distinct signed Fedora `solaar` and `acpi` RPM operations.
  The declared Fedora 44 x86_64 Workstation VM must pass absent plan,
  apply, package signature/files, CLI startup, repeat, status, restore,
  explicit remove, and profile smoke. Do not claim pairing without a USB
  receiver; do not run hardware mutation commands. Reuse the unchanged DNF
  handler's mocked failure evidence. Make any desktop pairing visual check
  a separate opt-in hardening item.
- For the conditional VM function, determine whether QEMU and VMware
  behavior can be represented with explicit targets/profiles without
  falsely claiming the other hypervisor. Check the pinned QEMU image's
  package baseline read-only. Require a provider-specific VM lifecycle and
  recovery before a runnable operation; otherwise document an explicit
  non-runnable decision and reopen trigger.
- Compare Windows schema/behavior, update catalog, profile, acceptance,
  ledger, and generated docs. Investigate any VM failure before retrying.

## Conditional guest-tool outcome

The pinned disposable Workstation image identifies itself as `kvm` and
already contains `spice-vdagent`, `spice-webdavd`, and `open-vm-tools` RPMs.
That read-only baseline does not establish which packages RIDE should install
on a newly provisioned QEMU or VMware guest. The v2 install and remove
branches also use different DMI fields, so copying the detection would leave
an unsafe inverse. `VMtoolsOnVM` is **unsupported and non-runnable in v3.0**.
Reopen when a requested hypervisor-specific target has an explicit package
selection, absent-package VM install, repeat/status, and owned inverse on
that hypervisor. Preinstalled guest tools belong to the image owner, not a
RIDE removal journal.

## Fedora 44 VM result

The `package.solaar` and `package.acpi` RPMs passed individual absent plan,
candidate-gated apply, signed RPM/file checks, CLI startup, status, unchanged
repeat, restore, and explicit remove on the pinned disposable Workstation
target. The curated `logitech-unifying` profile passed plan, apply, repeat,
and restore in the same overlay. The first attempt failed only because
`acpi --version` returns exit 1 after printing its version; the probe was
corrected to check the output, and the new overlay passed. The unchanged DNF
handler's mocked failure evidence is reused. See the
[`package.solaar`](../acceptance/package.solaar.md) and
[`package.acpi`](../acceptance/package.acpi.md) records.

`UnifyingOnLaptop` is an **operable opt-in candidate** for installing these
two packages with `--allow-candidate`. No USB receiver or desktop pairing was
tested; this user-visible check is H013 in the v3.1 queue. The profile is not
part of `default`.
