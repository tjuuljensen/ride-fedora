# BulkExtractor source build and forensic output

The owner kept BulkExtractor for v3.0 in the fast-track review. The v3 path
uses the publisher's pinned Snap artifact rather than rebuilding the legacy
source tree.

Status: **operable opt-in candidate on Fedora 44 Workstation x86_64**, 2026-11-02. This isolated high-risk batch
maps `InstallBulkExtractor` and `RemoveBulkExtractor`, both commented out of
the v2 preset. The installer clones an unpinned recursive Git tree into
`/opt`, changes its ACL, edits a Fedora configure helper, builds and runs
`make install` into `/usr/local`, and adds `edk2-tools-python`. Its inverse
deletes the clone and one guessed binary and removes a possibly shared RPM;
it does not track all installed files or forensic output.

## Completion criteria defined before implementation

- Use the official 2.2.0 x86_64 Snap attached to the signed upstream release
  tag, pin the release API SHA-256, and preserve the bundled notices. The
  upstream Store-publishing work is still a separate release issue, so this
  is a direct pinned-artifact install with `--dangerous`, not a Store-channel
  install.
- Require the separately managed Snap runtime first. Keep the package
  operation opt-in and Fedora 44 Workstation x86_64 only; do not add it to a
  base profile.
- Mock digest mismatch, failed download, pre-existing Snap, wrong installed
  version, repeat, removal,
  and unrelated package/data preservation. Verify the installed version and
  Snap confinement metadata without opening an evidence file.
- On disposable Fedora 44 Workstation, record plan/apply/repeat/status/restore
  and remove. Preserve seeded input/output files and Snap user data; test only
  `--version`/help and do not process PCAPs or disk images.
- Keep deeper scan behavior, input authorization, hostile-file handling,
  output limits, and recovery of real case data in named v3.1 hardening.

The official [upstream release page](https://github.com/simsong/bulk_extractor/releases/tag/v2.2.0)
lists signed tag `v2.2.0` and an attached `bulk-extractor_2.2.0_amd64.snap`.
The downloaded asset matched GitHub release metadata SHA-256
`dbc0749a7a84e2710c104a09fd921b93c1db9e2147bb11da978dea7af0e16c67` for that
asset. Its [install guide](https://github.com/simsong/bulk_extractor/blob/main/INSTALL)
recommends release archives and an owned `--prefix`; the archive is the
alternative if the Snap packaging path cannot meet the declared Fedora target.
The [license statement](https://github.com/simsong/bulk_extractor/blob/main/COPYING)
identifies post-2015 project code as GPL-3.0-or-later and notes separately
licensed components. The artifact metadata declares strict confinement and
block-device, removable-media, and home plugs. This release asset is installed
locally with `snap install --dangerous`, not through the Snap Store; RIDE pins
and verifies its SHA-256 and exact version. No privileged interfaces are
connected by the acceptance path. Fedora's Snap runtime reports partial host
confinement; the artifact's strict mode is not a boundary for untrusted
evidence, as documented in [Snap runtime acceptance](../acceptance/package.snapd.md).

`package.bulk-extractor` is in the opt-in `forensic-bulk-extractor` profile.
Apply `snap-runtime` separately before the app profile. The handler rejects
an already-installed version other than 2.2.0, verifies the downloaded
artifact before installation, and removes without `--purge` so Snap creates
its automatic data snapshot. Focused tests cover install, repeat, absence,
download and digest failures, and mismatched pre-existing versions. The
disposable VM lifecycle and recovery evidence is in
[`package.bulk-extractor.md`](../acceptance/package.bulk-extractor.md).

H113 keeps actual analysis behavior out of the v3.0 package lifecycle: before
claiming evidence-processing support, validate authorized input scope,
hostile-file behavior, output limits, host confinement limits, plug
connections, and real recovery only with dedicated disposable fixtures. The
opt-in install does not open evidence files and is not a claim that v2's broad
source-build inverse was safe.
