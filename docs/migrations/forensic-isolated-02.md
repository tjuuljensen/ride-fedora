# Forensic isolated batch 02: former CERT placeholders and Volatility 3

Status: **complete: one operable opt-in candidate, two unsupported tools,
one retired legacy line**,
2026-10-30. This ordinary batch covers the commented v2 `Plaso`,
`Autopsy`, `Volatility`, and `Volatility3` source outcomes. Their v2
installers only print a URL or an empty line and their inverses perform no
removal. None was a working v2 install. `NetworkMiner` and
`EmailHeaderAnlzr` require separate data and service ownership review.
`Plaso` was subsequently kept by the owner in the v3.0 fast-track review;
its maintained source and case-data-preserving lifecycle remain to implement.
The owner also kept Autopsy and the distinct Volatility 2 capability; neither
is satisfied by the accepted Volatility 3 core package.

The existing v3 catalog already has a `package.volatility3` candidate with
a private user venv, pinned [`volatility3` 2.28.2](https://pypi.org/project/volatility3/2.28.2/)
and `pefile` wheels, exact hashes in `requirements/volatility3.txt`, and an
owned-marker inverse. The upstream
[Volatility 3 release](https://github.com/volatilityfoundation/volatility3/releases)
is current at this review and uses the Volatility Software License 1.0.
Optional plugin dependencies and forensic image analysis are outside this
core package claim. Volatility 2 is a different legacy plugin/API line.

## Completion criteria defined before implementation

- Keep all four source mappings and distinguish Volatility 2 from 3.
  Resolve the v2 no-op placeholders without claiming an installation or
  copying a Windows installer.
- Bind `package.volatility3` to Fedora 44 x86_64 Workstation only. Add
  focused mocked tests for existing unowned path refusal, exact marker
  removal, and failed install cleanup. In one disposable Workstation VM,
  run as the intended non-root account; check absent plan, apply with
  `--allow-candidate`, pinned-version observation and CLI startup, repeat,
  status, restore, explicit remove, and preservation of an unrelated user
  file. Do not read or alter a real forensic image.
- Count Volatility 3 as an opt-in candidate only after the happy path and
  focused checks pass; put broader failure, plugin, and recovery coverage
  in the named v3.1 queue. Keep it out of the base profiles until then.
- Record source decisions, Windows product alignment, acceptance evidence,
  ledger progress, and generated docs. Investigate failed runs before retry.

## VM result and v3.0 decisions

[`package.volatility3`](../acceptance/package.volatility3.md) passed the
non-root Fedora 44 x86_64 Workstation happy path with pinned wheel versions,
CLI startup, repeat, status, restore, and explicit remove. An unrelated user
file survived. Mocked checks cover an unmarked path and failed install
cleanup. It is an **operable opt-in candidate**; broader plugin and recovery
coverage remains in v3.1. The core Python venv is not the older Volatility 2
runtime or a full forensic analysis acceptance.

`Volatility` (version 2) is **retired**. Its v2 function never installed it,
and the [upstream repository](https://github.com/volatilityfoundation/volatility)
was archived in 2025. Its older plugin/profile API is not silently replaced
by Volatility 3. Reopen only for a concrete legacy-image or plugin need with
an isolated, licensed and tested runtime.

`Plaso` is **unsupported as a v3.0 operation**. The v2 function only prints
a URL. Current [upstream](https://github.com/log2timeline/plaso/blob/main/pyproject.toml)
is Apache-2.0 with a large Python dependency set and recommends packaged
releases. No pinned isolated Fedora 44 package, handler, or inverse has been
accepted. Reopen for a concrete timeline use case with a chosen package,
isolated dependencies, and VM evidence.

`Autopsy` is **unsupported as a v3.0 operation**. Its v2 function also only
prints a URL. The [publisher's Linux download](https://www.autopsy.com/download/)
is a signed ZIP with Java and Sleuth Kit Java dependencies; it is distinct
from the Windows MSI in the Windows development catalog. RIDE has no Linux
owned portable/Java dependency lifecycle or data-preserving inverse for
case files. Reopen for a concrete desktop use case with signed artifact,
dependency, launcher, case-data, and disposable-VM evidence. The separately
cataloged `package.sleuthkit` candidate does not install Autopsy.
