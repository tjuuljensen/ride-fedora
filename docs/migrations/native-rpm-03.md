# Native RPM batch 03: active workstation applications

Status: **catalog candidates implemented; VM acceptance pending**, 2026-10-30.
This batch prioritizes three active v2 preset outcomes: HexChat, Speedtest CLI,
and Chromium. The v2 functions install and remove their same-named Fedora RPMs.
Each now has an individually selectable candidate on Fedora 44 x86_64
Workstation. The Fedora DNF handler, run journal, and inverse are unchanged.
The v2 `Cheat` function downloads a GitHub release binary into `/bin`; it is
tracked separately as `publisher-apps-16`, by acquisition method.

Two commented v2 outcomes in this family have a Fedora 44 resolution decision:

| v2 outcome | Decision and evidence | Review trigger |
| --- | --- | --- |
| `package.NautilusHash` | **Unsupported** on Fedora 44. The v2 function installs `gtkhash-nautilus`, but the [Fedora GtkHash source package](https://packages.fedoraproject.org/pkgs/gtkhash/) lists only the GtkHash application and Caja, Nemo, and Thunar extensions. Installing the GtkHash application would lose the requested Nautilus context-menu behavior. | Reopen when a maintained Fedora 44 Nautilus extension or equivalent GNOME Files integration has package, compatibility, and recovery evidence. |
| `package.NautilusImageTools` | **Unsupported** on Fedora 44. The v2 function installs ImageMagick and `nautilus-image-converter`, but the [Fedora package record](https://packages.fedoraproject.org/pkgs/nautilus-image-converter/nautilus-image-converter/) has only an EPEL 7 release. A standalone image converter is a different user-visible outcome. | Reopen when a maintained Fedora 44 GNOME Files image-resize extension is available and its behavior can be tested. |

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

The [HexChat](https://packages.fedoraproject.org/pkgs/hexchat/hexchat/),
[Speedtest CLI](https://packages.fedoraproject.org/pkgs/speedtest-cli/speedtest-cli/),
and [Chromium](https://packages.fedoraproject.org/pkgs/chromium/chromium/)
package records are the authoritative Fedora sources for this assessment.
