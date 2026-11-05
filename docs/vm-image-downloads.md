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

Run from the repository root as the user who owns the destination. POSIX sh, curl, jq, a SHA-256 utility, HTTPS access, sufficient free space,
and a filesystem supporting
files larger than 4 GiB are required. The following commands contact publisher
metadata hosts. `fetch` also downloads complete multi-gigabyte appliances.
They write only under the chosen destination and do not require root.

```bash
sh tools/download-vm-images.sh list
sh tools/download-vm-images.sh plan all --destination /path/to/vm-images
sh tools/download-vm-images.sh fetch remnux-vmware --destination /path/to/vm-images
```

Use one selection or `all` with `plan` and `fetch`. Before transferring a large
file, `fetch` compares current publisher metadata to `manifest.json` and
hashes a matching local file. It skips a verified duplicate; a matching digest
under another version can be reused locally. A transfer is published only after
the complete SHA-256 matches. The default rotation keeps two verified versions
per selection and architecture; `--keep N` changes that count.

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

`verify` hashes each recorded VM artifact and exits nonzero on a missing or
changed file. `prune --dry-run` lists eligible old owned copies. Actual pruning
removes only manifest-owned files whose bytes still match the recorded digest.
A changed old file is preserved. A changed current file is moved to
`quarantine/` before a replacement is acquired. Unmanaged files are never
adopted or overwritten. A failed transfer or import leaves earlier verified
copies intact. Back up the destination before manually editing its manifest.

The VM and Linux image commands can share a destination and manifest; their
`verify` and `prune` commands act only on their own selections. Local digest
verification checks recorded bytes against the saved hash. The tool does not
verify signed checksum files or authenticate a publisher signature, and it
does not establish that an appliance boots in a particular hypervisor.

## Validation record

On 2026-11-05, Fedora 44 Workstation x86_64 resolved current publisher
metadata for all six selections. HTTPS HEAD requests returned 200 for both
REMnux OVAs, both Kali VM archives, and the SOF-ELK redirect target. SIFT's
publisher page exposed a SHA-256 and a portal login requirement. Local mocked
tests cover checksum binding, manifest reuse, rotation, and SIFT import. No
complete VM appliance was downloaded or booted for this review.
