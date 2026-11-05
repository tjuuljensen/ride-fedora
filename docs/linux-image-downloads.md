# Linux image downloader

`tools/download-linux-images.sh` is a standalone distribution-image downloader. It is
not a RIDE v3 catalog operation or profile action. It downloads complete ISO,
USB image, or compressed disk-image files into an operator-chosen folder. It
does not download torrents, install an operating system, or write removable media.

## First-release selections

| Selection | Publisher image | Architecture |
| --- | --- | --- |
| `debian` | Debian DVD 1 ISO | amd64 |
| `debian-netinst` | Debian network installer ISO | amd64 |
| `ubuntu` | Latest numbered Ubuntu Desktop ISO | amd64 |
| `ubuntu-server` | Latest numbered Ubuntu live Server ISO | amd64 |
| `fedora` | Latest stable Fedora Workstation Live ISO | x86_64 |
| `fedora-server` | Latest stable Fedora Server DVD ISO | x86_64 |
| `kali` | Current Kali point-release installer ISO | amd64 |
| `kali-live` | Current Kali point-release Live ISO, when directly published over HTTPS | amd64 |
| `mint` | Latest Linux Mint Cinnamon ISO | x86_64 |
| `tails` | Current stable Tails USB `.img` | amd64 |
| `raspios-lite` | Current Raspberry Pi OS Lite `.img.xz` | arm64 |
| `raspios-full` | Current Raspberry Pi OS Full `.img.xz` | arm64 |
| `securityonion` | ISO named in Security Onion's download and verify guide | x86_64 |
| `arch` | Current Arch Linux ISO | x86_64 |

`raspios-lite` means the publisher's Lite edition. The Raspberry Pi files are
complete compressed images; they are not extracted by this utility. Debian
Netinst is a complete ISO file, but installing from it still requires a network
package source. Tails is the USB image, rather than its separate DVD ISO.

Kali's current image index lists the Live ISO as a torrent without a direct
HTTPS ISO. By owner decision, `kali-live` reports unavailable in that situation.
`fetch all` continues with the other selections and returns a nonzero status to
make the missing selection visible. No other Kali image is substituted.

## Prepare and refresh

Run from the repository root as the user who owns the destination. POSIX sh, curl, jq, a SHA-256 utility, HTTPS access to publisher metadata and
image hosts, and enough free disk space are required. The destination can be a local folder or mounted
portable storage. Use a filesystem that supports files larger than 4 GiB;
FAT32 cannot hold several of these images. The commands below create image
files and a manifest only under the destination; they do not need root.

```bash
sh tools/download-linux-images.sh list
sh tools/download-linux-images.sh plan all --destination /path/to/linux-images
sh tools/download-linux-images.sh fetch all --destination /path/to/linux-images
```

To refresh one selection, replace `all` with its ID. `plan` fetches small
publisher metadata and hashes a matching local image, but writes nothing.
`fetch` downloads to a temporary file, checks the publisher SHA-256, and then
publishes the image and `manifest.json`. Its default rotation retains the two
newest verified versions per selection and architecture. Use `--keep N` with
`fetch` to choose another positive count.

Before each large transfer, the utility resolves the publisher's current
filename and checksum, then checks the manifest and hashes the recorded local
file. A matching file is skipped. An identical digest recorded under another
version or selection is reused locally, without a second network download.
Version labels and digests both contribute to the managed path, so a republished
image cannot overwrite the previous verified bytes.

After a successful refresh, automatic rotation removes old files only if they
are manifest-owned and still match their recorded SHA-256. A changed old file
is preserved and reported. A changed current file is moved to `quarantine/`
before being fetched again. Unmanaged files are never adopted or overwritten.
If an image transfer or checksum check fails, its temporary file is deleted and
the previous verified version remains. The manifest is written atomically.

## Check and clean locally

Run from the repository root as the destination owner. These commands do not
contact the network. `verify` reads every recorded image and returns nonzero
if one is missing or changed. `prune --dry-run` previews rotation; omit
`--dry-run` to remove eligible old owned files. Keep a backup of the image folder
before manually deleting or replacing its manifest.

```bash
sh tools/download-linux-images.sh verify --destination /path/to/linux-images
sh tools/download-linux-images.sh prune --destination /path/to/linux-images --dry-run
```

The manifest records exact source URLs, versions, sizes, publisher checksum
URLs, local hashes, and acquisition times. The current release verifies hashes
from publisher metadata fetched over HTTPS; it **does not validate OpenPGP
signatures** on signed checksum files or ISO signatures. The recorded
verification text states this limit. `verify` checks the saved local digest
offline; it does not reauthenticate the publisher. Signature validation is a
separate hardening task before treating these images as independently
authenticated installation media.

The downloader and its local lifecycle tests do not establish that any ISO
boots or installs on a particular target. No multi-gigabyte publisher images
are downloaded during repository tests.

## Validation record

On 2026-11-05, Fedora 44 Workstation x86_64 resolved metadata for the 13
currently direct-downloadable selections. HEAD requests for all 13 image URLs
returned HTTPS 200; Kali Live reported the expected unavailable result. A real
Raspberry Pi OS Lite 64-bit image transfer completed: 550,466,056 bytes, local
SHA-256 `483db18a48da399b5b7022ffae9a07bc6d99daab30e593aedac09b69ff422843`.
A second `fetch` skipped the image using the manifest, and offline `verify`
returned `OK`. The temporary test download folder was removed. The other twelve
images have not had full-byte transfers or boot checks in this review.
