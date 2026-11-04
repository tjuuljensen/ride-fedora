# ArtCraft Linux download utility

This standalone utility archives published Linux installers from public
`storytold` GitHub repositories. It does not install or run the applications
and is not a RIDE v3 operation. It records release URLs, versions, formats,
architectures, upstream checksums when published, and local SHA-256 hashes.
It selects the newest discovered release with supported installers; it is not
a historical release archive.

## Download installers

Run from the repository root. The Python downloader uses the standard library
and supports Python 3.11 or newer on Windows and Linux:

```powershell
python tools/download-artcraft.py all --arch x86_64 --destination 'Z:\Artcraft\linux'
```

On Linux, choose the destination and architecture explicitly:

```bash
python3 tools/download-artcraft.py all \
  --arch x86_64 \
  --destination /path/to/Artcraft/linux
```

The archive contains `catalog.json`, `download-report.json`,
`SHA256SUMS.local`, and an `INSTALL.txt` summary. Verify the downloaded files
from the destination directory:

```bash
sha256sum --check SHA256SUMS.local
```

## Prepare Fedora dependencies

On a Fedora host, run as root. This resolves RPMs and Flatpak runtimes for the
specified Fedora release and architecture into the archive. It uses an empty
temporary DNF install root and an isolated Flatpak repository; it does not
install or execute an ArtCraft application on the host.

```bash
sudo bash lib/artcraft/download-dependencies.sh \
  /path/to/Artcraft/linux 44 x86_64
```

The prepared closure is under
`dependencies/fedora-44-x86_64/`. Verify it from that directory:

```bash
cd /path/to/Artcraft/linux/dependencies/fedora-44-x86_64
sha256sum --check SHA256SUMS
```

To retain the temporary dependency staging directory for troubleshooting, set
`ARTCRAFT_KEEP_STAGE=1`. Large staging files use `/var/tmp`.

## Use an archived application

Choose one installer format per application. These commands are examples; use
the version and filename recorded in the archive.

For RPMs, install the app and its matching dependency closure offline:

```bash
sudo dnf --disablerepo='*' install \
  ./APP/VERSION/APP.rpm ./dependencies/fedora-44-x86_64/rpm/*.rpm
```

For Flatpak, install the saved runtime bundles before one app bundle:

```bash
for bundle in dependencies/fedora-44-x86_64/flatpak/*.flatpak; do
  flatpak install --user --no-deps --no-related "$bundle"
done
flatpak install --user --no-deps --no-related APP/VERSION/APP.flatpak
```

AppImages bundle their application libraries; FUSE, the base OS, and GPU
drivers remain host requirements. The dependency archive includes Fedora
FUSE, Mesa, and Vulkan support. Proprietary GPU drivers depend on the target
hardware.

`lib/artcraft/lib-artcraft.sh` is a Bash convenience wrapper around these
utilities. Source it directly from Bash if needed; the v3 `ride.sh` CLI has no
`--include` mechanism for running it as an operation.
