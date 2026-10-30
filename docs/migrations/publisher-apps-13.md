# Projecteur Logitech Spotlight outcome

Status: **operable opt-in candidate**, 2026-10-30. This v2 source outcome maps
`InstallProjecteur` and `RemoveProjecteur`. v2 scrapes a moving Fedora RPM
from a third-party download page; its inverse removes `projecteur` by name.
[Fedora 44 now ships `projecteur`](https://packages.fedoraproject.org/pkgs/projecteur/projecteur/)
under MIT, with an executable, desktop entry, and udev rule. The current
upstream development line has moved beyond the version in Fedora; the
declared operation is the Fedora package, not a claim about new hardware.

## Completion criteria defined before implementation

- Add a signed Fedora `projecteur` RPM candidate and a curated opt-in
  Workstation profile. On the exact Fedora 44 x86_64 VM, verify absent plan,
  apply, RPM signature/files and executable/udev rule, repeat, status,
  restore, explicit remove, and profile smoke. Preserve pre-existing RPMs.
- Reuse mocked DNF handler failures. Do not operate a Spotlight device,
  change user settings, or claim desktop pointer behavior without controlled
  hardware and visual evidence; queue those for v3.1.
- Compare Windows contracts, update ledger and generated docs, investigate
  a failed VM run before retrying.

## Fedora 44 VM result

[`package.projecteur`](../acceptance/package.projecteur.md) passed the
signed-RPM plan/apply/repeat/status/restore/remove lifecycle and the curated
`spotlight-pointer` profile passed plan/apply/repeat/restore in a disposable
Workstation overlay. The installed RPM supplied its executable and udev
rule; no Spotlight device or GNOME pointer display was tested. The v2
moving third-party RPM scrape is replaced by the Fedora package. The
profile requires `--allow-candidate` and stays outside `default`.
Device and visual behavior plus broader recovery are H017 in v3.1.
