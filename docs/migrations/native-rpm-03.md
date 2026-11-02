# Native RPM batch 03: workstation applications

Status: **PASS; HexChat and Chromium operable opt-in, Speedtest CLI supported,
two legacy Nautilus integrations retired by owner decision**, 2026-10-30.
This batch covers the HexChat, Speedtest CLI, and Chromium v2 outcomes.
The v2 functions install and remove their same-named Fedora RPMs.
Each now has an individually selectable candidate on Fedora 44 x86_64
Workstation. The Fedora DNF handler, run journal, and inverse are unchanged.
The v2 `Cheat` function downloads a GitHub release binary into `/bin`; it is
tracked separately as `publisher-apps-16`, by acquisition method.

Two commented v2 outcomes in this family have a Fedora 44 resolution decision:

| v2 outcome | Decision and evidence | Review trigger |
| --- | --- | --- |
| `package.NautilusHash` | **Capability retired** by owner on 2026-10-30. The v2 function installs `gtkhash-nautilus`, but the [Fedora GtkHash source package](https://packages.fedoraproject.org/pkgs/gtkhash/) lists only the GtkHash application and Caja, Nemo, and Thunar extensions. | No v3.0 checksum context action is required; preserve v2 source as evidence. |
| `package.NautilusImageTools` | **Capability retired** by owner on 2026-10-30. The v2 function installs ImageMagick and `nautilus-image-converter`, but the [Fedora package record](https://packages.fedoraproject.org/pkgs/nautilus-image-converter/nautilus-image-converter/) has only an EPEL 7 release. | No v3.0 image context action is required; preserve v2 source as evidence. |

## Completion criteria defined before implementation

- Review the current Fedora 44 package, license, and upstream status for
  `hexchat`, `speedtest-cli`, and `chromium`. Preserve each v2 install/remove
  intent with an individual exact-target catalog operation. Do not add them to
  `default` or `server-base`.
- Run focused mocked catalog and lifecycle checks. Use one disposable Fedora
  44 x86_64 Workstation VM session for the package lifecycle: plan, apply,
  repeat, status, signed RPM and file verification, restore, explicit remove,
  and full inventory comparison. Record image preparation separately from
  operation behavior. Reuse accepted DNF handler failure evidence only while
  the handler and journal contract remain unchanged.
- Treat HexChat and Chromium as desktop applications: require a VM happy path
  before counting them as operable opt-in candidates. A visual check is needed
  only if package and launcher checks cannot establish the declared behavior.
  Speedtest CLI may become supported after the exact-target lifecycle passes.
- Record individual acceptance, Windows alignment, and any v3.1 hardening
  items before promotion. Investigate failures before retrying.

## Investigated first VM run

The first disposable overlay
`20261030T103239Z-test-native-active-workstation-applications-batch-d919b88b`
passed HexChat plan, apply, version probe, repeat, status, and restore. The
test then found three RPMs retained after `dnf remove hexchat`: `gtk2`,
`ibus-gtk2`, and `libcanberra-gtk2`. The DNF install transcript shows those
were dependencies introduced by HexChat; the remove transaction removed
HexChat and `dbus-glib` but retained the three GTK2 packages. No
pre-existing RPM was lost or changed. The run stopped before Speedtest CLI
and Chromium, so they have no VM acceptance yet.

The revised opt-in desktop acceptance check requires the named package to
restore and remove, no loss or change to a pre-existing RPM, and any residual
RPM to come from that operation's install transaction. It records the exact
residue for the acceptance note and v3.1 dependency-cleanup review. This is
proportionate to the v3.0 desktop happy-path gate; it does not claim full
recovery of every DNF dependency.

The second overlay
`20261030T104045Z-test-native-active-workstation-applications-batch-be719a0d`
completed HexChat and Speedtest CLI lifecycles, including explicit remove.
Chromium installed, its RPM signature and files passed, and then the test
stopped at a launcher probe: Fedora packages the executable as
`chromium-browser`, not `chromium`. The [Fedora 44 package file
list](https://packages.fedoraproject.org/pkgs/chromium/chromium/fedora-44.html)
confirms `/usr/bin/chromium-browser` and the matching desktop entry. The
catalog package name was correct; only the test probe changed. A focused
Chromium-only VM test reuses the two completed operation transcripts and
checks the remaining Chromium lifecycle.

The focused Chromium overlay
`20261030T105029Z-test-native-chromium-probe-and-lifecycle-7d5b7140`
passed the corrected launcher, restore, and explicit remove, with full RPM
inventory recovery. `.acceptance-runs/native-rpm-03-chromium.xml` reports one
pass and no failures, errors, or skips. The individual [HexChat](../acceptance/package.hexchat.md),
[Speedtest CLI](../acceptance/package.speedtest-cli.md), and
[Chromium](../acceptance/package.chromium.md) records distinguish the supported
CLI tool from the two opt-in desktop candidates. No manual session was needed
for the package-install outcomes.

The [HexChat](https://packages.fedoraproject.org/pkgs/hexchat/hexchat/),
[Speedtest CLI](https://packages.fedoraproject.org/pkgs/speedtest-cli/speedtest-cli/),
and [Chromium](https://packages.fedoraproject.org/pkgs/chromium/chromium/)
package records are the authoritative Fedora sources for this assessment.

The [HexChat upstream](https://hexchat.github.io/news/2.16.2.html) announced
its final release in 2024, and the Fedora package is now orphaned. The
existing VM result proves a package lifecycle. A maintained GUI IRC path is
now v3.0 work; H007 covers broader profile and visual checks. The
[Speedtest CLI upstream](https://github.com/sivel/speedtest-cli) archived its
repository in April 2026; Fedora 44 still supplies the signed RPM. H022
covers broader network behavior after a v3.0 bandwidth-test path is chosen.
Neither finding changes the
recorded Fedora 44 package-install result or establishes historical use.

## Maintained path review (2026-10-31)

The HexChat source repository is archived and its last upstream release is
2.16.2. Keep the existing signed Fedora RPM operation as an explicit legacy
option. **Polari** 50.0 and Konversation 26.08.1 were both tested as potential
Fedora replacements, but neither starts on the pinned Fedora 44 image. Polari
throws a GNOME JavaScript/TinySPARQL API error; Konversation requires a
`GLIBCXX_3.4.35` symbol absent from the image runtime, installs 76 new
dependencies, and upgrades ten existing RPMs. Both operations and profiles
were removed after investigation. See the [Polari](../acceptance/polari-investigation.md)
and [Konversation](../acceptance/konversation-investigation.md) records.

The current recommendation is **Halloy** through Flathub. Its upstream remains
active and uses GPL-3.0-or-later. Upstream's current release is 2026.9. The
initial Flathub page crawl showed 2026.8, while a disposable VM fetched its
2026.9 build, so the operation follows the signed Flathub remote rather than
pinning a release. Package HexChat remains
available beside it, and existing IRC settings are not imported automatically.
Sources: [HexChat archived upstream](https://github.com/hexchat/hexchat),
[Halloy upstream and license](https://github.com/squidowl/halloy), and
[Halloy on Flathub](https://flathub.org/en/apps/org.squidowl.halloy).

The upstream `speedtest-cli` repository was archived on 2026-04-30. Keep its
Fedora 44 RPM path available, and add **LibreSpeed CLI** as a separately
selectable alternative from a pinned upstream Linux release, verifying its
published SHA-256 manifest before extraction. LibreSpeed CLI is active and
LGPL-3.0, but tests LibreSpeed-compatible backends rather than Speedtest.net;
it is an alternative measurement service, not a transparent replacement.
Sources: [archived speedtest-cli](https://github.com/sivel/speedtest-cli),
[LibreSpeed CLI releases](https://github.com/librespeed/speedtest-cli/releases),
and [upstream usage and license](https://github.com/librespeed/speedtest-cli#readme).

Halloy batch completion checks, defined before implementation:

- Validate the exact `org.squidowl.halloy` application ref and a Flathub system
  remote with the expected URL and GPG verification enabled. Refuse an app
  ref installed from an unexpected origin.
- In focused mocked tests, cover absent/installed observation, first install,
  repeat, status, exact removal, wrong origin, missing remote, failed command,
  and preservation of per-user data. Uninstall must not pass Flatpak's
  `--delete-data` option.
- On Fedora 44 Workstation x86_64, run plan, apply, repeat, status, and remove
  in a disposable VM. Verify the Flatpak app ref and origin, and confirm a
  seeded `~/.var/app/org.squidowl.halloy` sentinel retains its contents and
  mode after removal. Do not connect to an IRC server or import HexChat
  settings.
- Keep Halloy an opt-in candidate until this target passes. The Flatpak app
  stays separate from the HexChat RPM deployment; broader permission review
  and visual session checks remain hardening.

The Halloy Flatpak app operation and opt-in profile are implemented as a
candidate. Disposable Fedora 44 Workstation acceptance is next: test first
install, repeat, status, and removal while preserving per-user data; do not
connect to an IRC server or import HexChat settings. Then add a digest-pinned
`package.librespeed-cli` deployment beside `package.speedtest-cli`. Reuse
accepted RPM evidence and never run a speed test during installation
acceptance. LibreSpeed CLI is now an operable opt-in candidate on the declared
Workstation target; its disposable lifecycle and download digest checks passed.

## LibreSpeed CLI batch completion checks

Before implementation, the selected acquisition is the publisher's Linux
amd64 tarball from LibreSpeed CLI v1.0.14. The signed release tag and tagged
LICENSE declare LGPL-3.0-only; the release asset page publishes SHA-256
`89800767ac14085c78a20847ebea23340f6c14a78de0a15c2ac7db8b565c961f` for
`librespeed-cli_1.0.14_linux_amd64.tar.gz`. The release's `checksums.txt` asset
is SHA-256 pinned as
`1cd30f1c4a25b008f2a401ffb4d5617cf5d3b4bc9e44e873f44dd2f2fbd8b3c6`.

Completion requires focused tests for manifest and archive digest mismatch,
safe extraction of the single binary and license, destination collisions,
repeat, exact owned removal, modified-file refusal, and checksum-only version
probing. Fedora 44 Workstation x86_64 acceptance covers plan, candidate
refusal, apply, repeat, status, and removal as the intended user, verifies
`librespeed-cli --version`, and confirms the existing Speedtest CLI RPM is
unchanged. It must not execute a bandwidth test or contact a LibreSpeed server.
The profile is opt-in and the user deployment remains separate from the
system RPM. Keep it a candidate until that VM path passes.
