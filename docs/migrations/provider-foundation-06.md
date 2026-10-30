# Provider foundation batch 06: Security Lab group

Status: **unsupported as a group operation in v3.0**, 2026-10-30.
The owner chose **keep** for the Security Lab capability in the v3.0 fast-track
review. The group contains 137 default Fedora packages on the pinned image;
this does not require 137 deep manual tests. Reuse accepted package evidence,
choose the needed tools, and apply brief automated package lifecycles to new
operations. Direct group removal still needs separate ownership evidence.
The commented v2 pair `InstallSecurityLab`/`RemoveSecurityLab` invokes DNF
`group install` and `group remove` for `security-lab`. This is a changing
collection rather than one product. Fedora's
[DNF5 group contract](https://dnf5.readthedocs.io/en/stable/commands/group.8.html)
tracks group membership and package reasons separately from an individual
RPM install. The v3 DNF package handler observes one RPM at a time; it does
not own a DNF group or capture a safe inverse for the group's state.

## Completion criteria defined before resolution

- Query the exact Fedora 44 x86_64 Workstation group and installed-group
  state read-only in a disposable VM. Identify overlap with individually
  tracked v2 outcomes and accepted v3 operations.
- Prefer a bounded opt-in set of Fedora RPM operations, reusing package source
  metadata and accepted handler evidence. Run brief exact-target lifecycles
  for newly selected packages. A direct group migration would additionally
  need a VM inverse preserving pre-existing packages and group marks.

## Fedora 44 inspection and v3.0 decision

The pinned Workstation image SHA-256 was
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
In disposable overlay `provider-security-lab-inventory-root`, read-only
`sudo dnf5 group info security-lab` passed and reported **137 default
packages**; the group was not installed. `sudo dnf5 group list --installed`
also passed and showed unrelated installed groups. The retained transcript
is under `.acceptance-runs/full-v2-migration/fedora-44-workstation-x86_64/`.
An initial unprivileged `dnf5 group info` attempt failed before returning
metadata because it could not open the system DNF lock. The privileged
read-only rerun resolved that query failure; neither run installed a package.

The group includes `binwalk`, `dc3dd`, `ewftools`, `htop`, `lynis`, `pwgen`,
`sleuthkit`, `testdisk`, and `vim-enhanced`, among many unrelated tools.
`dc3dd`, `htop`, `lynis`, `pwgen`, and `vim-enhanced` already have separately
accepted Fedora package operations; other listed tools remain candidates or
separate migration outcomes. A group apply would silently include far more
software than those scoped operations. Group removal also cannot be mapped
to RIDE's current per-package run journal without risking changes to
pre-existing package or group state.

The `SecurityLab` source outcome is **unsupported as a v3.0 group operation**.
No group install, profile, or package acceptance is claimed. Review this
decision only if a concrete, bounded Security Lab tool set is requested and
its individual source, license, target, and recovery checks pass. Individual
forensic operations remain in their own batches; this decision does not
retire them or count them as accepted installs.
