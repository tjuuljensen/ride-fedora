# Forensic isolated batch 04: BulkExtractor source build

Status: **unresolved**, 2026-10-30. The v2 `InstallBulkExtractor` clones
upstream source into `/opt`, builds components, and writes a binary under
`/usr/local/bin`. Its inverse recursively deletes the `/opt` directory and
removes a Fedora prerequisite without recording ownership. This needs a
reviewed acquisition artifact, license, owned destination, detection, build
reproducibility, and safe restore before any runnable v3 operation. Keep the
case separate from Fedora RPM packages; do not delete an unowned directory.
