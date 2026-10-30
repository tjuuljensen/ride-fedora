# Forensic Isolated 01 follow-up: Chepy CLI

Status: **operable opt-in candidate on Fedora 44 Workstation x86_64**,
2026-10-30. The v2 function clones an unpinned branch into `/opt`, mutates
the user's global pip environment, builds a PyInstaller binary, and copies
it into `/usr/bin`. Chepy 7.6.0 instead publishes a `chepy` console entry
point, so the v3 path can use an isolated user venv without PyInstaller.

## Completion checks defined before implementation

- Use the PyPI Chepy 7.6.0 source distribution
  `chepy-7.6.0.tar.gz` with SHA-256
  `f6084689e43d128748c18f79c79d75539abb67ac8245e950b678cfa0da2f5010`.
  The tagged upstream is GPL-3.0; retain a linked license record. PyPI lists
  `Requires-Python: <3.13` and no wheel for this release. Fedora 44's default
  Python 3.14 cannot be used. Declare Fedora `python3.12` as an independent
  system RPM operation in `chepy-runtime`, and select a user `package.chepy`
  operation in `forensic-chepy` after that runtime is observed.
- Download and verify the exact sdist before installation. Create only
  `${XDG_DATA_HOME:-$HOME/.local/share}/ride-fedora/tools/chepy` and an
  owned `~/.local/bin/chepy` link. Do not clone a branch, install globally,
  add PyInstaller, install optional plugins, or touch case files. Detect
  Chepy 7.6.0 and its console entry point. Restore and remove must refuse
  an unowned destination and preserve sibling user files and pre-existing
  Python RPMs.
- Mock failed acquisition, wrong digest, occupied destination, and unowned
  removal. In one disposable Fedora 44 Workstation x86_64 VM, check the
  runtime and user profiles' plan, candidate gate, apply, repeat, status,
  package signature and files, Chepy import/CLI smoke, restore, explicit
  user remove, and pre-existing package and user-file preservation. A
  candidate counts as operable only after that happy path. Investigate any
  failure before retrying.
- The v3.0 candidate may resolve unpinned transitive dependencies from PyPI
  within the isolated venv; record their actual versions in its run evidence.
  Full hash locking, plugin compatibility, wider transformations, and
  dependency update behavior go into a named v3.1 hardening item. Keep both
  profiles opt-in and update catalog, ledger, generated docs, Windows
  alignment, and acceptance evidence after the VM result.

[PyPI release metadata](https://pypi.org/project/chepy/7.6.0/) provides
the sdist hash, Python constraint, and console entry point; the
[tagged source license](https://github.com/securisec/chepy/blob/7.6.0/LICENSE)
is GPL-3.0. Hashes bind acquired bytes but are not an independent publisher
signature.

## Result

The [focused disposable VM run](../acceptance/package.chepy.md) passed
the separate Fedora runtime and user CLI lifecycles, source digest and
RPM checks, version and CLI startup, unchanged repeats, restore, and
explicit remove. The sibling user file and pre-existing RPM names were
preserved. No manual session was needed. The runtime RPM is supported for
the declared target; Chepy remains opt-in with `--allow-candidate` while
H029 tracks dependency locking and broader behavior.
