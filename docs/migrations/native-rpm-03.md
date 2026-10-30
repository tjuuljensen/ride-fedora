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
| `package.NautilusHash` | **Retired** by individual owner decision on 2026-10-30. The v2 function installs `gtkhash-nautilus`, but the [Fedora GtkHash source package](https://packages.fedoraproject.org/pkgs/gtkhash/) lists only the GtkHash application and Caja, Nemo, and Thunar extensions. Installing the GtkHash application would lose the requested Nautilus context-menu behavior. | For v3.0, evaluate an owned GNOME Files checksum script with Fedora 44 compatibility and exact recovery; the old extension remains retired. |
| `package.NautilusImageTools` | **Retired** by individual owner decision on 2026-10-30. The v2 function installs ImageMagick and `nautilus-image-converter`, but the [Fedora package record](https://packages.fedoraproject.org/pkgs/nautilus-image-converter/nautilus-image-converter/) has only an EPEL 7 release. A standalone image converter is a different user-visible outcome. | For v3.0, evaluate an owned GNOME Files image-action script with non-overwriting output and exact recovery; the old extension remains retired. |

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
