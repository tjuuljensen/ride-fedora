# Forensic isolated batch 01: active v2 tools

Status: **one supported source outcome and four operable opt-in candidates**,
2026-10-30. The owner kept ASN, UnfURL, CyberChef, and Chepy capabilities
in the v3.0 fast-track review. VMFS access is now isolated as a high-risk
[follow-up batch](forensic-isolated-07-vmfs.md).
This batch covers active v2 `ExifTool`, `ASN`, `UnfURL`, `CyberChef`, and
`Chepy`. The v2 functions use unrelated acquisition methods;
they must not be treated as one install bundle. The function source is
`lib-fedora.sh`; its code is migration evidence, never a v3 fallback.

| Source outcome | v2 behavior | Current source and v3.0 direction |
| --- | --- | --- |
| `ExifTool` | Downloads the latest GitHub source ZIP, builds with Perl/CPAN, and removes `/usr/lib/exiftool`. | Fedora 44 publishes signed [`perl-Image-ExifTool`](https://packages.fedoraproject.org/pkgs/perl-Image-ExifTool/perl-Image-ExifTool/) (GPL-1.0-or-later OR Artistic-1.0-Perl) with the `exiftool` CLI. Replace source-build behavior with an owned RPM lifecycle. |
| `ASN` | Downloads an unpinned [MIT-licensed upstream script](https://github.com/nitefood/asn) into `/usr/bin` and installs several RPM dependencies; inverse removes some shared dependencies. | A [pinned owned user script](forensic-isolated-01-asn.md) and independent Fedora RPM prerequisites now provide an operable opt-in candidate. |
| `UnfURL` | Installs `dfir-unfurl` into the user's global Python environment. | A [pinned user venv](forensic-isolated-01-unfurl.md) now provides an operable opt-in candidate on Fedora 44 Workstation. |
| `CyberChef` | Selects the first mutable GitHub release URL, extracts a ZIP into `/usr/lib`, and writes a desktop launcher. | A [pinned offline ZIP and owned desktop launcher](forensic-isolated-01-cyberchef.md) now provide an operable opt-in candidate. |
| `Chepy` | Clones an unpinned [GPL-3.0 upstream](https://github.com/securisec/chepy), globally installs Python dependencies, builds with PyInstaller, and writes `/usr/bin/chepy`. | A [pinned PyPI sdist in an owned Python 3.12 user venv](forensic-isolated-01-chepy.md) now provides an operable opt-in candidate. |

## Completion criteria defined before implementation

- Keep all five v2 source mappings in the ledger. Track the VMFS capability
  in its separate high-risk batch; never count its v2 placeholder as an
  install.
- For `ExifTool`, use one Fedora RPM operation restricted to Fedora 44
  x86_64 Workstation, with the unchanged DNF handler, signed RPM/file
  verification, command detection, and a named-package inverse. Reuse the
  handler's focused mocked failure evidence. In a disposable Workstation VM,
  check absent plan, apply, repeat, status, restore, explicit remove,
  pre-existing RPM preservation, and no touch to the v2 source-build path.
- For third-party scripts, Python tools, and the desktop artifact, require
  current license/source review, pinned artifact or wheel provenance,
  distinct owned destination or venv, focused mocked tests, and a disposable
  VM happy path before calling a candidate operable. Keep unresolved or
  non-runnable results out of profiles. Deeper recovery can enter v3.1 only
  after this minimum happy path; security or data exposure needs its own gate.
- Update catalog, acceptance records, Windows alignment, ledger, and
  generated docs after evidence. Investigate a failed VM run before retrying.

## Focused VM result and decisions

[`package.exiftool`](../acceptance/package.exiftool.md) passed its Fedora 44
x86_64 Workstation absent-package lifecycle in a disposable VM. The RPM
introduced only `perl-Image-ExifTool` 13.50 and both inverse paths returned
the full RPM inventory to baseline; the v2 source-build path stayed absent.
The first VM run failed before v3 execution because the acceptance fixture
name contained uppercase RPM characters. The helper now lowercases that
filename; the corrected focused rerun passed. No operational handler
changed. Source-build files from an old v2 run are not adopted or removed by
the new RPM operation.

`ASN` now has a separate [accepted candidate path](forensic-isolated-01-asn.md)
and [Fedora 44 acceptance](../acceptance/package.asn.md). The script is
hash-pinned, installed in an owned user path, and recovered without deleting
pre-existing RPM names or user files. Its ten Fedora RPM prerequisites are
selected through a separate opt-in system profile. The VM exposed a DNF
upgrade of a pre-existing `nmap-ncat` while installing `nmap`; broader update
and dependency effects remain H008. Live ASN lookups and optional server
behavior remain H027.

`CyberChef` now has a separate [accepted candidate path](forensic-isolated-01-cyberchef.md)
and [Fedora 44 acceptance](../acceptance/package.cyberchef.md). Its release
ZIP and tagged license are hash-checked; the owned payload retains bundled
notices and a desktop launcher. Firefox opened the offline page headlessly
in the disposable VM. Broader visual and recipe interaction remains H028.

`Chepy` now has a separate [accepted candidate path](forensic-isolated-01-chepy.md)
and [Fedora 44 acceptance](../acceptance/package.chepy.md). Fedora Python
3.12 is a supported RPM operation on the declared Workstation target; the
Chepy sdist is hash-pinned in an owned user venv. Broader transformations,
optional plugins, dependency locking, and update behavior remain H029.
UnfURL has a separate [accepted candidate path](forensic-isolated-01-unfurl.md),
with broader UI and failure coverage in v3.1.
