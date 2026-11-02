# Generic Server `InstallRequired` migration

Status: **PASS; eleven v3 operations are available as opt-in candidates**. The
pinned v2 Server function is a one-way DNF loop for eleven Fedora RPMs. v3
keeps that behavior as installed-state operations for Fedora 44 Server x86_64.
RIDE does not separately manage services, firewall rules, mounts, or Samba
shares. Fedora RPM presets can still change unit enablement during package
installation; the observed open-vm-tools effect is recorded below.

## Completion checks defined before implementation

- Confirm the exact v2 RPM list and map each RPM to a stable catalog operation.
- Reuse an existing operation only when its package identity, target, and
  installed-state behavior match; add Server target evidence before marking
  it supported there.
- Keep all operations opt-in and outside `default` and `server-base`.
- Mock the complete profile mapping, candidate gating, Fedora RPM source,
  installed-only or safely removable state, and repeat behavior.
- On the pinned Fedora 44 Server x86_64 disposable image, compare RPM name,
  architecture, EVR, and signature inventories; capture service enablement,
  active state, firewall runtime state, and existing config hashes before and
  after apply. Check plan, apply, repeat, status, package signatures, `rpm -V`,
  command availability, and profile remove/restore behavior.
- Treat `firewalld` as a separate security-sensitive step. Compare its service
  and configuration state on the exact target; if it is already present, state
  plainly that a new RPM installation was not exercised.
- Keep the v2 one-way semantics for operations without an existing safe
  package inverse; profile removal must retain those RPMs.
- Record the VM transcript and image digest, update the outcome ledger,
  generated docs, and Windows alignment, then run focused catalog, CLI, and
  acceptance checks.

## Package mapping

| v2 RPM | v3 operation | Fedora 44 package source | Notes |
| --- | --- | --- | --- |
| `open-vm-tools` | `package.open-vm-tools` | [Fedora Packages](https://packages.fedoraproject.org/pkgs/open-vm-tools/open-vm-tools/) | Guest integration package; does not claim VMware runtime behavior on the KVM acceptance host. |
| `nano` | `package.server-nano` | [Fedora Packages](https://packages.fedoraproject.org/pkgs/nano/nano/) | Installed-only Server operation; the Workstation `package.nano` inverse is deliberately not reused because profile removal can erase a pre-existing package. |
| `wget` | `package.wget` | [Fedora Packages](https://packages.fedoraproject.org/pkgs/wget2/wget2-wget/) | Existing operation maps the command to Fedora's Wget 2 provider. |
| `firewalld` | `package.firewalld` | [Fedora Packages](https://packages.fedoraproject.org/pkgs/firewalld/firewalld/) | Isolated security-sensitive installed-only operation. |
| `unzip` | `package.unzip` | [Fedora Packages](https://packages.fedoraproject.org/pkgs/unzip/unzip/) | Command-line archive utility. |
| `git` | `package.git` | [Fedora Packages](https://packages.fedoraproject.org/pkgs/git/git/) | Existing operation; add Server target evidence. |
| `cifs-utils` | `package.cifs-utils` | [Fedora Packages](https://packages.fedoraproject.org/pkgs/cifs-utils/cifs-utils/) | Client utilities only; no mount or credential state. |
| `samba-client` | `package.samba-client` | [Fedora Packages](https://packages.fedoraproject.org/pkgs/samba/samba-client/) | Client utilities only; no share or identity state. |
| `samba-common` | `package.samba-common` | [Fedora Packages](https://packages.fedoraproject.org/pkgs/samba/samba-common/) | Shared client/server files supplied by Fedora. |
| `cronie` | `package.cronie` | [Fedora Packages](https://packages.fedoraproject.org/pkgs/cronie/cronie/) | Package installation only; no crontab entries or schedule ownership. |
| `screen` | `package.screen` | [Fedora Packages](https://packages.fedoraproject.org/pkgs/screen/screen/) | Terminal session utility. |

## Evidence and result

The disposable Fedora 44 Server run passed, with full results in the
[acceptance record](../acceptance/generic-server-required.md). The image
already had `firewalld` active/enabled, so its separate profile applied
unchanged; no new firewalld RPM installation is claimed. Installing
`open-vm-tools` enabled `vmtoolsd.service` and `vgauthd.service` by RPM preset,
but both remained inactive on the KVM guest. H035 tracks the six pre-existing
RPM upgrades from this package transaction. This batch does not change the
accepted `server-base` profile. H036 retains the absent-package firewalld
installation as a deeper security check.
