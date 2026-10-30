# Native RPM batch 04: forensic command and desktop applications

Status: **catalog candidates implemented; VM acceptance pending**, 2026-10-30.
This batch covers five commented v2 install/remove pairs whose declared
behavior is to install or remove Fedora RPMs. `Dc3dd` only installs the tool;
RIDE never runs a disk-copy or wipe command. `Qbittorrent`, `Thunderbird`,
`Flameshot`, and `GIMP` are desktop applications. The source-built
`BulkExtractor`, broad `SecurityLab` DNF group, and Pidgin plus OTR plugin
were separated into acquisition or security-specific batches.
The five exact-target candidate rows use the unchanged Fedora DNF handler.

| v2 outcome | Fedora 44 RPM source |
| --- | --- |
| `package.Dc3dd` | [`dc3dd`](https://packages.fedoraproject.org/pkgs/dc3dd/dc3dd/) |
| `package.Qbittorrent` | [`qbittorrent`](https://packages.fedoraproject.org/pkgs/qbittorrent/qbittorrent/) |
| `package.Thunderbird` | [`thunderbird`](https://packages.fedoraproject.org/pkgs/thunderbird/thunderbird/) |
| `package.Flameshot` | [`flameshot`](https://packages.fedoraproject.org/pkgs/flameshot/flameshot/) |
| `package.GIMP` | [`gimp`](https://packages.fedoraproject.org/pkgs/gimp/gimp/) |

## Completion criteria defined before implementation

- Preserve each exact v2 RPM name and install/remove intent in an individual
  Fedora 44 x86_64 Workstation catalog operation. Keep these out of the base
  profiles. Review upstream status and the license in each linked Fedora
  record before choosing the stable ID.
- Reuse focused mocked DNF handler failure evidence while handler and journal
  behavior remain unchanged. In one disposable Workstation VM, check each
  package's absent plan, apply, repeat, status, signature/files, declared
  restore, and explicit remove. Confirm no pre-existing RPM is lost or changed;
  name any retained DNF dependency. Use a launch/version probe for desktop
  packages when it works without an interactive display.
- Promote the low-risk tool only after the exact-target lifecycle passes.
  Count a desktop package as an opt-in candidate only after a VM happy path
  and individual acceptance record; reserve broader visual and recovery
  coverage for v3.1. Investigate failure before retrying.
- Record Windows branch alignment, generated docs, ledger status, and
  profile selection separately. No manual session is required solely to
  verify package installation.
