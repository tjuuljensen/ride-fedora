# Forensic isolated batch 02: former CERT placeholders and Volatility 3

Status: **in progress: Plaso and Volatility 3 are operable opt-in candidates;
Volatility 2 has an implemented opt-in candidate, with Fedora VM acceptance pending**,
2026-11-01. This ordinary batch covers the commented v2 `Plaso`,
`Autopsy`, `Volatility`, and `Volatility3` source outcomes. Their v2
installers only print a URL or an empty line and their inverses perform no
removal. None was a working v2 install. `NetworkMiner` and
`EmailHeaderAnlzr` require separate data and service ownership review.
`Plaso`, Autopsy, and the distinct Volatility 2 capability were kept for v3.0.
Autopsy now has its own high-risk batch in
[`forensic-isolated-09-autopsy.md`](forensic-isolated-09-autopsy.md). None is
satisfied by the accepted Volatility 3 core package.

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
- For Plaso, use the official GIFT stable COPR only on Fedora 44 Workstation
  x86_64, verify RPM signatures, preserve pre-existing repo configuration,
  remove only RIDE-created repository state and the selected RPM, and preserve
  case timelines and outputs. In a disposable VM, run candidate gating,
  plan/apply/repeat/status, CLI version, remove, and a case-output sentinel
  check without processing a forensic image.
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
- For Volatility 2, pin and verify the archived 2.6.1 source and official
  PyPy 2.7 binary, install them under one RIDE-owned user-local directory,
  confirm `vol2 --info`, then repeat, inspect status, remove the bundle, and
  verify an unrelated user file survives. Do not run analysis against a memory
  image. Keep legacy plugin dependencies optional.
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

`Volatility` (version 2) remains separate from Volatility 3. Its v2 function
never installed it, and the
[upstream repository](https://github.com/volatilityfoundation/volatility) was
archived in 2025. Candidate `package.volatility2` pins the archived 2.6.1
source with a NetBSD pkgsrc SHA-512 and the official PyPy 2.7 v8.0.1 Linux
x86_64 binary with PyPy's published SHA-256. It installs both under the user's
RIDE data directory and exposes `bin/vol2`; it does not register or modify
system Python. The old plugin set is optional. Fedora 44 disposable-VM
acceptance is in progress; broader plugin compatibility and long-term Python 2
retirement remain v3.1 hardening work.

`Plaso` remains a **kept migration gap**. The v2 function only prints a URL.
Current upstream provides a Fedora 43 and 44 package path through the GIFT
`@gift/stable` COPR and installs `plaso-tools`; the project identifies its
license as Apache-2.0. The opt-in candidate `package.plaso` uses the existing
owned repository/RPM provider with DNF RPM signature checks. Focused mocked
tests and Fedora 44 Workstation lifecycle acceptance passed; the transcript and
image digest are recorded in the [acceptance record](../acceptance/package.plaso.md).

`Autopsy` now has an opt-in candidate path through the
[Sleuth Kit Labs Snap Store publisher](https://snapcraft.io/autopsy). The v2
function only prints a URL. Upstream's current Linux instructions recommend
the Snap on Snap-enabled systems; the official stable channel currently lags
the latest publisher ZIP, so H087 tracks freshness. The Snap declares highly
privileged interfaces for disk access and indexing. A Fedora 44 Workstation
install connected `block-devices`, `dm-crypt`, and `fuse-support` through
publisher-granted auto-connect policy; `system-files-dev` remained
disconnected. RIDE does not create these connections, but package installation
activates them. This is a high-risk opt-in path pending interface and recovery
review. Snap removal keeps application data in an automatic snapshot for 31
days, which can be restored with the Snap manager. The separate
`package.sleuthkit` candidate does not install Autopsy.


Current source review: [Plaso Fedora packaged release](https://plaso.readthedocs.io/en/latest/sources/user/Fedora-Packaged-Release.html) explicitly documents Fedora 43/44 and `@gift/stable`; [Autopsy publisher instructions](https://github.com/sleuthkit/autopsy/blob/develop/Running_Linux_OSX.md) point to the Snap Store on Snap-enabled Linux, and the [Snap Store listing](https://snapcraft.io/autopsy) identifies Sleuth Kit Labs as publisher and lists privileged interfaces; the [Volatility 2 installation guide](https://github.com/volatilityfoundation/volatility/wiki/installation) documents Python 2.7-era dependencies and the archive marks the repository read-only.

## Volatility 2 compatibility path

The retained `InstallVolatility` outcome is distinct from Volatility 3. The
upstream 2.6.1 release requires Python 2.6+ and explicitly does not support
Python 3; the repository is archived and the current Volatility Foundation FAQ
calls Volatility 2 deprecated now that Volatility 3 reached parity. The
project's GPL-2.0 license permits distribution with attribution. This makes
Volatility 2 a legacy compatibility tool, not a maintained alternative to
Volatility 3.

The v3 candidate uses a private user-local bundle under
`~/.local/share/ride-fedora/tools/volatility2/`: upstream Volatility 2.6.1
source pinned by NetBSD pkgsrc's SHA-512, plus the official PyPy 2.7 Linux
x86_64 binary, exposed as `bin/vol2`. PyPy 8.0.1 was released 2026-10-14; its
upstream checksum page publishes SHA-256
`78674cdf95eb4cb1dd5a9b68a70200387111cb29467f8a472ab7cf07a251653c` for
`pypy2.7-v8.0.1-linux64.tar.gz`. Verify that pinned archive, pin the Volatility
source archive digest independently, and do not register Python 2 system-wide
or execute setup.py with elevated rights. The handler verifies Volatility's
core `--info` output before publishing the bundle. Plugin dependencies such as
distorm3, Yara, PyCrypto, OpenPyXL, and PIL stay optional and separately pinned
if added.

This is a proposed isolated compatibility deployment, not a supported result
yet. Before implementation, confirm PyPy 2.7 runs the pinned source and its
core CLI on Fedora 44. Focused acceptance should install, repeat, report
version, remove only the RIDE-owned bundle and launcher, and preserve an
unrelated user file; it must not open or alter a real memory image. Broader
plugin coverage and Python 2 retirement planning belong in v3.1.
