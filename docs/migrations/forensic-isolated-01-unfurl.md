# Forensic Isolated 01 follow-up: UnfURL

Status: **operable opt-in candidate after Fedora 44 Workstation VM pass**,
2026-10-30. The v2 `InstallUnfURL` calls global user pip and exposes both
the CLI and a local web application. The v3 outcome is an owned user virtual
environment containing the current PyPI `dfir-unfurl[all]` wheel and its
hash-pinned dependencies. It does not start a persistent service or alter
case data, browser state, or the user's global Python installation.

## Completion checks defined before implementation

- Pin `dfir-unfurl==20261007` and all binary wheels for Fedora 44 Workstation
  x86_64, using PyPI wheel hashes. The upstream package declares Python
  3.11 or newer and Apache-2.0. Only select this target after testing its
  system Python and wheel resolution in a disposable VM.
- Treat the environment path as exclusively RIDE-owned. Refuse to overwrite
  a pre-existing path, require an exact ownership marker for removal, keep
  sibling user files intact, and clean a failed new install. Detection checks
  the marker, root package version, and CLI executable. Reuse the existing
  Volatility 3 isolated-environment behavior without changing its claim.
- Focused mock tests cover unowned-path refusal and failed-install cleanup.
  One disposable Workstation VM checks absent plan, apply, CLI parsing of a
  local sample URL, package/entry-point presence, repeat, status, restore,
  and explicit remove. Check the UI entry point without starting a publicly
  bound service; no external site, case data, or network listener is needed.
- After the happy path and focused mocks pass, add an opt-in profile and mark
  this third-party operation an operable `candidate`. Keep broader failure,
  UI, and compatibility checks in v3.1. Update the ledger, generated docs,
  and Windows alignment before promotion.

[PyPI](https://pypi.org/project/dfir-unfurl/20261007/) provides the exact
release, wheel, Python requirement, extras, and license. Its documented
`unfurl` and `unfurl_app` entry points replace the v2 script names. Wheel
hashes are an acquisition pin, not independent publisher authentication.

## Result

The [acceptance record](../acceptance/package.dfir-unfurl.md) gives the pinned
image, candidate catalog hash, retained overlay, transcript, and one passing
VM lifecycle. The 37-wheel hash set is in `requirements/unfurl.txt`. Mocked
failure and unowned-path tests passed. The `forensic-unfurl` profile selects
only this candidate and requires `--allow-candidate`; it does not expand
`default` or start the web application. H025 and H002 retain broader UI,
parser, and failure checks.
