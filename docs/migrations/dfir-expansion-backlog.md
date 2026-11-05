# DFIR software expansion backlog

Status: **screening backlog; no candidate here is selected for v3.0**. The
catalog and migration records remain authoritative for implemented operations.

## Source and limits

This screen uses the Linux platform labels in the user-provided
`RIDE-DFIR-Research-Pack`. Its catalog contains 163 reconstructed records, 97
of which are tagged `linux`. The pack says the original catalog was unavailable
and that this reconstruction is neither an exact recovery nor a validated
installation manifest. Treat its platform labels, priorities, automatic
selection flags, presets, and recommendations as leads to review, not as RIDE
decisions or proof of Linux/Fedora support.

The request is to identify Linux software and track candidates for possible
inclusion before v3.0. This page does not add catalog IDs, profiles, migration
outcomes, installation behavior, or acceptance claims. Pack priorities are not
adopted. Upstream, license, Fedora source, and target compatibility still need
review for each selected item.

## Existing catalog coverage (not necessarily release-ready)

These pack entries already have a matching operation or are covered by a
broader existing operation. They are not new migration requests. Their current
status may still be `candidate`; check the generated
[operation reference](../OPERATIONS.md) and
[migration progress](progress.md) before treating one as release-ready.

| Area | Pack entries | Current catalog coverage |
| --- | --- | --- |
| Core | Python, pip, Git, jq, 7-Zip, ExifTool, CyberChef, hashdeep, ripgrep, Chepy, Unfurl, PowerShell, OpenJDK (partial target coverage) | `package.python-command`, `package.python3-pip`, `package.git`, `package.jq`, `package.7zip`, `package.exiftool`, `package.cyberchef`, `package.md5deep`, `package.ripgrep`, `package.chepy`, `package.dfir-unfurl`, `package.powershell`, and `package.java-25-openjdk-headless` |
| Acquisition | dc3dd, libewf | `package.dc3dd`, `package.libewf`, and `package.ewftools` |
| Disk | The Sleuth Kit, Autopsy, bulk_extractor, Binwalk, TestDisk, PhotoRec, dislocker, ewfmount | `package.sleuthkit`, `package.autopsy`, `package.bulk-extractor`, `package.binwalk`, `package.testdisk` (includes PhotoRec), `package.dislocker`, and EWF tools |
| Memory and timeline | Volatility 2, Volatility 3, Plaso | `package.volatility2`, `package.volatility3`, and `package.plaso` |
| Network | Wireshark, TShark, tcpdump, Zeek, NetworkMiner, tcpflow | `package.wireshark`, `package.wireshark-cli`, `package.tcpdump`, `package.zeek-core`, `package.networkminer`, and `package.tcpflow` |
| Malware analysis | YARA, capa | `package.yara`; `artifact.capa-linux` is a downloadable artifact, not an installed package lifecycle |

The Xplico entry is not a new request: the owner-kept offline PCAP/file
analysis capability has an opt-in `package.zeek-core` replacement. Zeek does
not claim full Xplico protocol or output parity; H098 tracks the remaining
fixture-based review. See the [resolution](resolution-decisions.md) and
[acceptance record](../acceptance/package.zeek-core.md).

The catalog's `package.java-25-openjdk-headless` is Server-only. It does not
cover a Workstation GUI runtime for tools such as Ghidra; consider that a
separate scoped candidate only if a selected tool needs it.

## Linux-labelled entries without a clear dedicated operation

The following are candidates for review, not confirmed Fedora software
recommendations. Some are libraries, rules/data, product-specific modules,
dependencies, or bundled utilities; a separate install operation may be the
wrong unit. Confirm whether the upstream project supports Linux and whether
Fedora 44 Workstation is a useful target before opening a migration batch.

| Area | Candidate entries | Initial review note |
| --- | --- | --- |
| Core | SQLite, DB Browser for SQLite, `pipx`; a Workstation Java GUI runtime if needed | Check Fedora package availability, user/system scope, and whether SQLite is a standalone user requirement or only an application data dependency. The existing Java operation is headless and Server-only. |
| Acquisition | AVML, Guymager, F-Response | AVML performs privileged live-memory acquisition; F-Response requires vendor entitlement. Review data handling and scope before considering either. |
| Disk and image formats | xmount, libvshadow, libfsntfs, libvmdk, libvhdi, libbde | Check Fedora packaging and whether each library should be a dependency/capability of a workflow instead of a standalone profile item. |
| Windows artifacts on Linux | RegRipper, Hindsight, libesedb, liblnk | Verify current upstream maintenance, Linux support, and license for the exact project/release; distinguish parsers from acquired evidence. |
| Event logs | Hayabusa, Chainsaw, Zircolite, sigma-cli, Sigma rules, python-evtx, libevtx | Treat rule sets as separate data with their own license, version, and update policy. Do not bundle a moving rules checkout with the CLI install. |
| Memory | MemProcFS, LeechCore, Rekall | Review physical-memory/device access, FUSE behavior, plugins, license boundaries, and whether Rekall remains maintained before selection. LeechCore may be a library component, not a user-facing operation. |
| Timeline | dfDateTime, mactime | Check whether Plaso or The Sleuth Kit already supplies the needed capability before creating separate IDs. |
| Network | nfdump, tcpxtract, Zui, Suricata | Define offline-analysis versus live-capture/service behavior and required privileges; don't make RIDE process case data during package apply/remove. |
| Malware analysis | Ghidra, FLOSS, Detect It Easy, PE-bear, pefile, LIEF, radare2, Cutter, ILSpy, oletools | Verify Linux support for each entry; libraries such as pefile/LIEF and front ends such as Cutter may belong under a parent tool or dependency set. |
| Endpoint and response | Velociraptor, osquery, UAC, Kunai | Separate local collector/client, endpoint agent, and server roles. A server or persistent service is not a workstation package-only migration. |
| Cloud | AWS CLI, Azure CLI, Microsoft Graph PowerShell, Google Cloud CLI, kubectl, Microsoft 365 Extractor, ROADtools, CloudFox | Defer unless a concrete RIDE use case is defined. Review credential stores, login flows, cloud data access, updates, and whether each is a CLI, module, or toolkit. |
| Mobile | Android Platform Tools, ALEAPP, ILEAPP, mac_apt, libimobiledevice, Mobile Verification Toolkit, iOSbackup | Keep acquisition from attached devices separate from offline parsing. Define access, evidence-output, and recovery boundaries. |
| Malware lab | FakeNet-NG, INetSim | Recheck the pack's Linux labels against current upstream support. Lab networking and service lifecycle need a separate safety/VM review. |

This list records names from the reconstructed inventory; it does not claim all
of them are genuinely Linux-capable or new to the existing dependency graph.
For example, an upstream project may support only another OS, or a tool may
already arrive through Plaso, Sleuth Kit, or a language environment. Resolve
those questions before assigning stable operation IDs.

## Suggested first pre-release screen

If the owner wants a small analysis-focused batch, evaluate these three first:

1. **Hayabusa** — upstream publishes Linux release artifacts and checksums.
   Review the AGPL-3.0 code license separately from the Sigma detection-rule
   license and update policy. [Upstream releases](https://github.com/Yamato-Security/hayabusa/releases)
   · [project and license](https://github.com/Yamato-Security/hayabusa).
2. **ALEAPP** — upstream documents Linux AppImage builds and release checksums.
   [Upstream project](https://github.com/abrignoni/ALEAPP).
3. **iLEAPP** — upstream documents Linux AppImage builds, checksums, and a
   glibc minimum; verify that against the selected Fedora target.
   [Upstream project](https://github.com/abrignoni/ILEAPP).

These sources make the three reasonable review candidates; they do not
establish RIDE compatibility or acceptance. Keep install artifacts separate
from case data and output. A later GUI/tool batch could consider **Ghidra**;
its archive and JDK dependency need their own deployment and update review
([official project](https://github.com/NationalSecurityAgency/ghidra)).

Defer **AVML**, **MemProcFS**, and **Velociraptor** from a quick v3.0 batch.
Their privileged memory-acquisition, physical-memory/FUSE, or persistent
endpoint/server roles need dedicated safety, ownership, deployment, and
recovery decisions. They can be reconsidered in a later scoped batch.

## Before selecting any candidate

For each item selected for v3.0:

1. Confirm owner intent, actual Fedora 44 target/variant/architecture, upstream
   maintenance, exact product identity, current license, and existing
   operation/dependency overlap.
2. Choose a trusted Fedora package or a pinned publisher artifact. Record the
   exact version, source, verification method, license, installation scope,
   and update model. Keep rules, plugins, signatures, cloud modules, and
   evidence datasets as separate products when their ownership or license
   differs.
3. Define read-only versus privileged behavior, evidence/data boundaries,
   exact state detection, conflict behavior, and a safe inverse that preserves
   user data and pre-existing files.
4. Implement an operation with a stable ID and scoped opt-in profile only
   after review. Add mocked lifecycle tests and disposable Fedora 44 VM
   acceptance for the declared target; record actual evidence and limitations.
5. Update the catalog, generated references, migration ledger/burndown, tests,
   acceptance records, and release review together. Keep it candidate-gated
   until all promotion requirements are met.

No operations were added or tested by this screening. Candidate selection and
implementation remain open owner decisions.
