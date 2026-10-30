# Forensic isolated batch 01: active v2 tools

Status: **complete: one supported RPM, one retired placeholder, four
non-runnable tool decisions**, 2026-10-30.
The owner subsequently kept VMFS access, ASN, UnfURL, CyberChef, and Chepy
capabilities in the v3.0 fast-track review. The old VMFS link-only function
remains retired; a working reader needs a current licensed source.
This batch covers active v2 `VMFStools`, `ExifTool`, `ASN`, `UnfURL`,
`CyberChef`, and `Chepy`. The v2 functions use unrelated acquisition methods;
they must not be treated as one install bundle. The function source is
`lib-fedora.sh`; its code is migration evidence, never a v3 fallback.

| Source outcome | v2 behavior | Current source and v3.0 direction |
| --- | --- | --- |
| `VMFStools` | Prints two URLs and removes nothing. | No executable install; resolve the placeholder without claiming support. An actual VMFS reader requires a concrete user request and independent package/license/recovery review. |
| `ExifTool` | Downloads the latest GitHub source ZIP, builds with Perl/CPAN, and removes `/usr/lib/exiftool`. | Fedora 44 publishes signed [`perl-Image-ExifTool`](https://packages.fedoraproject.org/pkgs/perl-Image-ExifTool/perl-Image-ExifTool/) (GPL-1.0-or-later OR Artistic-1.0-Perl) with the `exiftool` CLI. Replace source-build behavior with an owned RPM lifecycle. |
| `ASN` | Downloads an unpinned [MIT-licensed upstream script](https://github.com/nitefood/asn) into `/usr/bin` and installs several RPM dependencies; inverse removes some shared dependencies. | No v3 owned-script handler; do not delete shared tools or execute an unpinned script. |
| `UnfURL` | Installs `dfir-unfurl` into the user's global Python environment. | Current [PyPI package](https://pypi.org/project/dfir-unfurl/) is Apache-2.0 with a wheel; require an isolated, pinned environment rather than mutate global pip state. |
| `CyberChef` | Selects the first mutable GitHub release URL, extracts a ZIP into `/usr/lib`, and writes a desktop launcher. | [Upstream releases](https://github.com/gchq/CyberChef/releases) are Apache-2.0; need a pinned artifact and owned destination/launcher. |
| `Chepy` | Clones an unpinned [GPL-3.0 upstream](https://github.com/securisec/chepy), globally installs Python dependencies, builds with PyInstaller, and writes `/usr/bin/chepy`. | Need a pinned isolated build or package, distinct from CyberChef, with owned inverse. |

## Completion criteria defined before implementation

- Keep all six v2 source mappings in the ledger. Never count the VMFS
  placeholder as an install, and give each non-runnable decision a reason
  and review trigger.
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

`VMFStools` is **retired as a placeholder**: its v2 function only prints
two source URLs and its inverse is empty. It has never represented a working
install. Reopen for a concrete VMFS access requirement with a licensed,
verified acquisition path and read-only filesystem evidence.

`ASN`, `UnfURL`, `CyberChef`, and `Chepy` are **unsupported as v3.0
operations**. Their upstream projects and licenses are identifiable, but
the current v3 handlers cannot preserve the particular v2 script, global
Python, desktop artifact, and build destinations with pinned provenance and
an owned inverse. No VM install or operable candidate is claimed. Reopen
each on a concrete use case with the corresponding pinned script or wheel,
isolated runtime or owned destination, focused mocked tests, and exact-target
VM happy path. In particular, `ASN` must not remove shared RPM tools;
`UnfURL` must not mutate global pip state; `CyberChef` must preserve its
offline notices and any user recipes; and `Chepy` must not clone and build
an unpinned branch into system paths. Broader failure and desktop visual
coverage may enter v3.1 after a safe candidate is operable.
