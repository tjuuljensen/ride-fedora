# Publisher Apps 09: file managers and publisher applications

This six-outcome batch covers `CommanderFileMgrs`, `PowerShell`,
`MicrosoftTeams`, `WoeUSB`, `BalenaEtcher`, and `SonosPlayer`. The owner kept
PowerShell, WoeUSB, and balenaEtcher for v3.0. Microsoft Teams Linux desktop
and the old Sonos player were explicitly retired. The two Fedora file manager
operations and three retained publisher tools passed candidate-gated package
acceptance.

Status: **4 source outcomes operable candidates; 2 retired**. Fedora 44
Workstation x86_64 acceptance passed on 2026-11-01 under TCG.

## Completion checks defined before implementation

- Migrate retained applications from a specific publisher release or a
  Fedora-signed package. Check exact source digest and RPM identity before
  DNF, then plan, candidate gate, apply, repeat, status, and remove.
- Probe PowerShell in no-profile mode. For Etcher, inspect installed RPM files
  only. Do not launch Etcher against a physical drive or write removable
  media. Reuse pinned RPM handler tests; add exact source validation.
- For WoeUSB, check its pinned script and GPL text digests, private ownership,
  Fedora runtime RPMs, help/version, repeat, status, and exact inverse. Do not
  supply source or target media arguments, attach a drive, or write media.
- Update the ledger, generated docs, and Windows alignment. Queue GUI behavior
  and broader failure/recovery coverage for v3.1.

## Current source paths

- **PowerShell 7.6.6:** Microsoft publishes a versioned universal x86_64 RPM
  and release SHA-256. Fedora 44 is not listed as a Microsoft-supported target,
  so this is an opt-in Fedora candidate. RIDE adds no Microsoft repository or
  key. See [PowerShell acceptance](../acceptance/package.powershell.md).
- **balenaEtcher 2.1.9:** balena publishes an x86_64 RPM and SHA-256 in the
  versioned GitHub release. Installing Etcher does not start a flash
  operation. See [Etcher acceptance](../acceptance/package.balena-etcher.md).
- **WoeUSB:** use upstream's standalone Bash release 5.2.4, pinned with
  SHA-256, and install the GPL-3.0-or-later text alongside it. RIDE owns a
  versioned private user directory and one `~/.local/bin/woeusb` symlink.
  Fedora dependencies are explicit candidate RPM operations in
  `fedora-woeusb-runtime`; `fedora-woeusb` installs the tool after its runtime
  profile. RIDE never supplies media arguments or writes a USB device.
  See [WoeUSB acceptance](../acceptance/package.woeusb.md).
- **Microsoft Teams:** the owner retired the Linux desktop outcome; web access
  is not a replacement package operation.
- **SonosPlayer:** the owner retired the old unofficial player capability.
- **GNOME Commander and Midnight Commander:** both Fedora package operations
  passed their disposable Workstation lifecycle and remain opt-in.

Sources: [Microsoft PowerShell release](https://github.com/PowerShell/PowerShell/releases/tag/v7.6.6),
[Microsoft RHEL install guide](https://learn.microsoft.com/en-us/powershell/scripting/install/install-rhel),
[balenaEtcher release](https://github.com/balena-io/etcher/releases/tag/v2.1.9),
[WoeUSB 5.2.4 upstream release](https://github.com/WoeUSB/WoeUSB/releases/tag/v5.2.4),
[WoeUSB 5.2.4 README](https://raw.githubusercontent.com/WoeUSB/WoeUSB/v5.2.4/README.md),
[WoeUSB GPL text](https://raw.githubusercontent.com/WoeUSB/WoeUSB/v5.2.4/LICENSES/GPL-3.0-or-later.txt).

WoeUSB is a Linux-specific standalone script deployment. No shared Windows
schema or lifecycle contract changed; Windows packaging remains independently
owned. This difference is intentional because the artifact and Fedora runtime
dependencies are Linux-specific. Recheck if Windows adds a portable WoeUSB
deployment or if a shared package acquisition contract changes.
