# Native RPM batch 04: forensic command and desktop applications

Status: **complete: one supported and four operable opt-in candidates**, 2026-10-30.
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

## Investigated first VM run

The first disposable overlay
`20261030T105721Z-test-native-forensic-and-desktop-applications-batch-a296a16c`
completed `dc3dd` plan/apply/repeat/status/version/restore/explicit-remove
checks. qBittorrent then installed and passed RPM signature and file
verification, but the headless `qbittorrent --version` invocation returned
255 without diagnostic output. The run stopped before qBittorrent restore or
the remaining desktop applications, so it is not desktop acceptance evidence.

The [Fedora qBittorrent package manifest](https://packages.fedoraproject.org/pkgs/qbittorrent/qbittorrent/fedora-44.html)
lists the executable and a `.desktop` launcher. For the declared package
installation outcome, the revised automated happy path verifies the RPM and
its desktop launcher file without launching a graphical session over SSH.
Broader visual behavior remains in v3.1. A focused VM rerun covers only the
four desktop RPMs, reusing the completed `dc3dd` evidence. No package handler
or recovery code changed.

## Focused VM result

The rerun passed in disposable overlay
`20261030T110635Z-test-native-desktop-applications-lifecycle-1891f3ec`
on the pinned Fedora 44 x86_64 Workstation image. Catalog SHA-256 was
`f6cc32d95206073c3460196d4e03d2021b0578dbc3a31c576d205e628704c12b`.
The JUnit file `.acceptance-runs/native-rpm-04-desktop.xml` records one
passing test. Each of qBittorrent, Thunderbird, Flameshot, and GIMP passed
absent plan, apply, signed RPM and file verification, launcher file, status,
unchanged repeat, restore, and explicit remove. Restore and remove returned
the full RPM inventory to each operation's baseline; no dependency was
retained. The individual [acceptance records](../acceptance/package.qbittorrent.md)
and the earlier [`dc3dd` record](../acceptance/package.dc3dd.md) complete the
batch. The four desktop operations remain opt-in candidates; graphical use
and broader failure recovery are queued for v3.1.
