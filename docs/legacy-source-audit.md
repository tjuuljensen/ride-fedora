# Supplementary legacy source audit

Reviewed 2026-11-04 against the current tree and
`migration/outcomes.json`. The main migration ledger covers the 76 active
workstation preset entries and the scoped workstation and generic-server
functions. The [Sander feature map](sander-feature-map.md) is a separate
upstream inventory. Neither one inventories every helper library in this
repository.

The counts below are an exact-name scan against the 185 ledger rows. An absent
function name does not prove that its capability is missing from the v3
catalog; likewise, a similar catalog product name does not prove equivalent
source, deployment, scope, or recovery behavior. Compare those details before
claiming a migration.

## Source groups outside the scoped ledger

| Source | Inventory | Recommended disposition |
| --- | --- | --- |
| `lib-upgrade.sh` | 3 functions absent: `CheckNextVersionRepos`, `UpgradeFedora`, `InstallKernelHeaders`. | Keep distribution upgrades out of normal v3 apply. Retire the next-release URL probe as a RIDE operation. Decide whether kernel source compilation has any maintained use case; the supported Fedora kernel package operations do not imply that behavior. Record explicit dispositions before the release review. |
| `lib/distro/lib-distro.sh` | 21 ISO and torrent download functions absent. They scrape distribution pages and download images; they do not manage Fedora host state. | Keep this as legacy download code or move it to a separately scoped download tool. Do not add it to the package catalog. If retained, review each publisher source, architecture, checksum/signature path, and output ownership first. |
| `lib/vm/lib-vm.sh` | 6 third-party VM image download functions absent. | Treat these as artifact acquisition, not setup operations. Keep them outside v3. A later utility needs per-image publisher, license, provenance, digest, and safe destination evidence. |
| `lib/flatpak/lib-flatpak.sh` | 38 functions total; 20 are absent by exact name: John, Authy, Upscaler, GtkHash, Ghidra, UEFI Tool, Slack, Signal, ColorPicker, and PDFtricks install/remove pairs. | Map each pair to a current catalog entry only after comparing its exact Flatpak source and per-user behavior. `package.john`, for example, exists as a Fedora RPM operation; that alone does not establish equivalence to the old Flatpak path. Retire or defer products without an approved v3 use case. |
| `lib/funstuff/funstuff.sh` | 28 novelty-package functions absent. | Keep these out of the v3.0 product promise. Retain as migration evidence or retire after checking for external consumers; only add a later opt-in profile after explicit user demand and current source review. |
| `lib/osint/lib-osint.sh` | 6 functions absent: TheHarvester, YETI, and SpiderFoot install/remove pairs. | Do not port the direct clone, global dependency, repository, and broad-removal behavior. If an owner still needs a tool, create a separate migration batch for its current upstream, license, isolated environment, owned files, and exact inverse. |
| `lib/artcraft/lib-artcraft.sh` | 3 archive utility functions absent, alongside `tools/download-artcraft.py` and `lib/artcraft/download-dependencies.sh`. | Keep this as a separate archive utility, not a catalog operation. Its corrected usage is in [ArtCraft downloads](artcraft-downloads.md). |

The exact-name scan found **87 helper functions** outside the 185-row ledger
across those seven groups. This is a scope and bookkeeping gap, not a
recommendation to add 87 operations. `lib/flatpak/lib-flatpak.sh` has some
overlap with ledger function names, and other groups may have product-level
overlaps; both require operation-by-operation review.

## Other scripts and helpers

- [`reference/install-waydroid-fedora.sh`](../reference/install-waydroid-fedora.sh)
  is already recorded as one reference-script candidate in the generated
  burndown. Keep it reference-only until a separate Wayland and container
  lifecycle review passes.
- [`reference/mac-vendor.sh`](../reference/mac-vendor.sh) and
  [`reference/mac-vendor.py`](../reference/mac-vendor.py) are functional
  replacements for the old lookup behavior. Managed installation remains a
  separate v3.1 follow-up; do not claim it as catalog lifecycle support.
- `tools/manage-*.py`, `lib/v3/`, completion, and the VM harness are current
  v3 implementation or development support. Their catalog ownership and tests
  are tied to the operation or harness records; they are not old installer
  functions that need one-for-one porting.
- `legacy/v2/` and the older root-level function libraries are migration
  evidence. The v3 client does not source them as a fallback.

## Before v3.0 publication

1. Keep the release claim scoped to the supported Fedora 44 target rows and
   the accepted base profiles. Do not describe every file in the repository
   as a v3 operation.
2. Record owner-approved scope decisions for the seven unrepresented library
   groups above. Keep download utilities, novelty packages, and OSINT
   installers outside the v3.0 catalog unless a specific capability is
   selected for a reviewed migration batch.
3. Review the ten unmatched Flatpak product pairs for duplicate or
   source-specific intent. Reuse an existing catalog operation only when the
   distribution, deployment, scope, ownership, and recovery are the same.
4. Add these source groups to a checked inventory or explicitly label their
   directories as reference/standalone in repository conventions, so future
   library additions cannot silently escape the migration review.

The three current package/setting gaps and shared-contract tasks are tracked
separately in the [v3.0 release review](release-v3.0-review.md) and the
[generated migration progress report](migrations/progress.md).
