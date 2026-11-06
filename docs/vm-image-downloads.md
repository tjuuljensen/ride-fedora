# VM image downloader

`tools/download-vm-images.sh` keeps complete virtual-machine appliances in an
operator-chosen folder. It is a standalone utility, outside RIDE v3's setup
catalog. It does not import, boot, or configure a VM. It does not use torrents.
The script uses the same manifest storage and rotation code as the
[Linux image downloader](linux-image-downloads.md).

## Selections and sources

| Selection | Publisher and image | Transfer | Verification metadata |
| --- | --- | --- | --- |
| `remnux-vmware` | [REMnux general/VMware OVA](https://docs.remnux.org/install-distro/get-virtual-appliance) | Direct HTTPS | Adjacent SHA-256 on REMnux page |
| `remnux-virtualbox` | [REMnux VirtualBox OVA](https://docs.remnux.org/install-distro/get-virtual-appliance) | Direct HTTPS | Adjacent SHA-256 on REMnux page |
| `kali-vmware` | [Kali VMware amd64 `.7z`](https://cdimage.kali.org/kali-images/current/) | Direct HTTPS | Publisher `SHA256SUMS` |
| `kali-virtualbox` | [Kali VirtualBox amd64 `.7z`](https://cdimage.kali.org/kali-images/current/) | Direct HTTPS | Publisher `SHA256SUMS` |
| `sift` | [SANS SIFT OVA](https://www.sans.org/tools/sift-workstation/) | Portal login and local import | SHA-256 on SANS page |
| `sof-elk` | [SOF-ELK x86 `.7z`](https://github.com/philhagen/sof-elk/wiki/Virtual-Machine-README) | Publisher HTTPS redirect | Filename, byte size, and SHA-256 on project wiki |

These are the six selections represented by `lib/vm/lib-vm.sh`. All are x86_64
appliances. The direct downloads use publisher HTTPS pages or indexes to find
the current file and hash. SOF-ELK redirects from its documented link to an
HTTPS file host; the tool refuses a non-HTTPS redirect. SIFT requires SANS
Portal credentials, so `fetch sift` reports that manual import is required.
`fetch all` continues with the five direct selections and exits nonzero to
make the SIFT gap visible. `plan all` can show SIFT's published checksum.

The files remain subject to their publishers' terms. This tool records the
publisher source and hash; it does not establish redistribution rights or
check third-party software licenses inside an appliance.

## Download and refresh

Run from the repository root as the user who owns the destination. POSIX sh,
curl, jq, `mktemp`, a SHA-256 utility (`sha256sum`, `shasum`, or `openssl`),
HTTPS access, sufficient free space, and a filesystem supporting files larger
than 4 GiB are required. `plan`, `fetch`, and SIFT `import` contact publisher
metadata. `fetch` also downloads complete multi-gigabyte appliances. The
commands do not require root. They create the destination if it does not exist;
`plan` does not create a manifest or image file.

```bash
sh tools/download-vm-images.sh list
sh tools/download-vm-images.sh plan all --destination /path/to/vm-images
sh tools/download-vm-images.sh fetch remnux-vmware --destination /path/to/vm-images
```

Use one selection or `all` with `plan` and `fetch`. Before transferring a large
file, `fetch` resolves the current publisher filename and checksum, then checks
`manifest.json` and hashes the matching local file. It skips a verified copy;
an identical verified digest under another version or selection is copied
locally without another network transfer. Downloads go to a temporary file in
the destination image directory and are moved into place only after the full
SHA-256 and any publisher-provided byte size match.

The default rotation retains the two most recently acquired verified copies
per selection and architecture. Use `--keep N` with `fetch` or `prune` to
change the retained count. Rotation uses acquisition time, which is recorded in
the manifest, to order copies.

## Import SIFT after portal login

Run from the repository root as the destination owner. First use the login
button on the [SANS SIFT page](https://www.sans.org/tools/sift-workstation/)
and download its complete OVA to a local path. Then run:

```bash
sh tools/download-vm-images.sh import sift --file /path/to/downloaded-sift.ova --destination /path/to/vm-images
```

`import` rereads the publisher page, copies the local file into a temporary
file under the destination, and compares its SHA-256 with SANS's published
value before recording it in the manifest. It does not submit credentials or
automate the login. You may remove your separate browser download after
`verify` succeeds; this tool never removes it. SANS's public page does not
give the OVA a machine-readable release ID, so its manifest version uses a
prefix of the published SHA-256.

## Verify, rotate, and recover

Run from the repository root as the destination owner. These commands use only
the local manifest and files and do not contact the network:

```bash
sh tools/download-vm-images.sh verify --destination /path/to/vm-images
sh tools/download-vm-images.sh prune --destination /path/to/vm-images --dry-run
sh tools/download-vm-images.sh prune --destination /path/to/vm-images
```

`verify` hashes recorded VM artifacts and exits nonzero on a missing or changed
file. `prune --dry-run` previews eligible removals. Actual pruning removes only
manifest-owned files whose bytes still match their recorded digest. A changed
old file is preserved and reported. A changed current file is moved to
`quarantine/` before a replacement is acquired. Unmanaged files are never
adopted or overwritten. A failed transfer or import leaves earlier verified
copies intact. The manifest is updated through a temporary file in the
destination and renamed into place.

Mutating commands use an atomic `.lock.d` directory in the destination to
prevent simultaneous fetch, import, and prune operations. The script removes
the lock on normal exit and handled signals. If the process is killed and the
lock remains, confirm no downloader is running before removing
`/path/to/vm-images/.lock.d` manually. Back up the destination before manually
editing its manifest.

The VM and Linux image commands can share a destination and manifest; their
`verify` and `prune` commands act only on their own selections. The manifest
records publisher URLs, selection, architecture, version, filename, size,
SHA-256, acquisition time, and verification method. Local `verify` checks file
bytes against the saved hash without contacting a publisher. Acquisition
checks publisher hashes over HTTPS, but does not verify signed checksum files
or authenticate publisher signatures. The tool also does not establish that
an appliance boots in a particular hypervisor. It rejects image downloads
larger than 16 GiB and metadata responses larger than 2 MiB.

## Validation record

On 2026-11-05, Fedora 44 Workstation x86_64 resolved current publisher
metadata for all six selections. Read-only planning resolved both REMnux OVAs,
both Kali VM archives, the SOF-ELK redirect target, and SIFT's publisher hash
with its portal login requirement. POSIX shell syntax checks passed. No
complete VM appliance was downloaded or booted for this review.
