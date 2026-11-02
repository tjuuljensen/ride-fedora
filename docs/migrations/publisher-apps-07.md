# Logitech Unifying and conditional VM guest tools

The owner confirmed **keep** for VM guest tools in the v3.0 fast-track review.
Detect the actual hypervisor and install only its matching Fedora packages;
the v2 VMware-only inverse is insufficient.

Status: **two operable opt-in outcomes**, 2026-11-01. This active-preset batch maps
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
- For the conditional VM function, use explicit QEMU/SPICE and VMware
  profiles without claiming behavior on the other hypervisor. Check the
  pinned QEMU image's package baseline read-only. Require absent-state package
  apply/repeat/status/remove acceptance on Fedora 44 Workstation before
  promoting the candidate package operations.
- Compare Windows schema/behavior, update catalog, profile, acceptance,
  ledger, and generated docs. Investigate any VM failure before retrying.

## Conditional guest-tool outcome

The pinned disposable Workstation image identifies itself as `kvm` and
already contains `spice-vdagent`, `spice-webdavd`, and `open-vm-tools` RPMs.
That read-only baseline does not establish which packages RIDE should install
on a newly provisioned QEMU or VMware guest. The v2 install and remove
branches also use different DMI fields, so v3 replaces automatic detection
with explicit `fedora-qemu-guest-tools` and `fedora-vmware-guest-tools`
profiles. The QEMU profile selects Fedora's `spice-vdagent` and
`spice-webdavd`; the VMware profile selects `open-vm-tools`. These RPM
operations manage package presence only; they do not claim hypervisor feature
behavior, alter host settings, or configure user state. Workstation operations
remain candidate-gated until absent-state package lifecycle evidence passes.
The first VM setup attempt confirmed that the image's
`open-vm-tools-desktop` RPM depends on `open-vm-tools`; acceptance now removes
those two exact RPMs together in its disposable overlay before testing the
mapped core package. The RIDE operation is unchanged.

The Fedora 44 Workstation acceptance passed for both explicit profiles after
resetting the image-seeded guest-tool packages in the disposable overlay.
Both profiles passed their candidate gate, absent-state apply, package query,
repeat, status, and exact removal. The run did not exercise a QEMU or VMware
host, desktop session, clipboard, display, or file-sharing behavior. The
transcript and hash are recorded in the three operation acceptance pages.
`VMtoolsOnVM` is now an **operable opt-in candidate**. QEMU/SPICE and VMware
profiles remain separate; neither belongs in a base profile.

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
