# Fedora 44 Workstation acceptance image

This is a locally installed Fedora 44 x86_64 Workstation guest for the first
v3 package batch. It is not a Fedora-provided qcow2. The source is the
[Fedora Everything netinstaller](https://fedoraproject.org/en/misc/) release
44-1.7. Its signed checksum was verified with Fedora's release key
`36F612DCF27F7D1A48A835E4DBFCF71C6D9F90A6`, and the ISO SHA-256 was
`bd285201494dd0ba09b54d05ac707de1401668b8512a573edb5922dcf9d7067e`.
The [Kickstart recipe](../../tests/acceptance/fedora-44-workstation.ks) SHA-256
is `02a3b6d9be2a96d08993c48d24ffda848e66d64833e67ea31301cb637cd6a182`.
Anaconda's [Live ISO limitation](https://anaconda-installer.readthedocs.io/en/latest/user-guide/troubleshooting/common-bugs.html#automatic-installation-in-live-os)
is why this image uses the netinstaller and selects the Workstation environment.

## Build from a verified ISO

Run from the repository root as a regular user with access to `/dev/kvm` and
the network. The host needs `isoinfo`, `genisoimage`, `qemu-img`, QEMU with KVM,
and libguestfs. First verify the ISO signature and checksum using the
[Fedora download instructions](https://fedoraproject.org/en/misc/). The block
below checks the pinned ISO digest, creates only a new disposable directory
under `/tmp`, downloads Fedora RPMs inside the VM, and installs to its new
qcow2. It does not change host packages or disks. Use a fresh output path for
each rebuild; an interrupted or failed install is not an acceptance image.

```bash
set -euo pipefail
iso=/absolute/path/to/Fedora-Everything-netinst-x86_64-44-1.7.iso
out=/tmp/ride-workstation-build
test "$(sha256sum "$iso" | cut -d ' ' -f1)" = bd285201494dd0ba09b54d05ac707de1401668b8512a573edb5922dcf9d7067e
mkdir "$out"
isoinfo -i "$iso" -R -x /images/pxeboot/vmlinuz > "$out/vmlinuz"
isoinfo -i "$iso" -R -x /images/pxeboot/initrd.img > "$out/initrd.img"
genisoimage -quiet -o "$out/ks.iso" -V OEMDRV -J -R -graft-points \
  "ks.cfg=$PWD/tests/acceptance/fedora-44-workstation.ks"
qemu-img create -f qcow2 "$out/workstation.qcow2" 40G
timeout 3600 qemu-system-x86_64 -accel kvm -machine q35 -cpu host \
  -smp 4 -m 6144 -display none -monitor none -serial "file:$out/install-serial.log" \
  -no-reboot -drive "file=$out/workstation.qcow2,if=virtio,format=qcow2" \
  -cdrom "$iso" -drive "file=$out/ks.iso,media=cdrom,readonly=on" \
  -netdev user,id=net0 -device virtio-net-pci,netdev=net0 \
  -kernel "$out/vmlinuz" -initrd "$out/initrd.img" \
  -append 'inst.stage2=hd:LABEL=Fedora-E-dvd-x86_64-44 inst.ks=hd:LABEL=OEMDRV:/ks.cfg inst.cmdline console=ttyS0 inst.text ip=dhcp'
LIBGUESTFS_BACKEND=direct virt-cat -a "$out/workstation.qcow2" /etc/os-release
sha256sum "$out/workstation.qcow2"
```

The 2026-10-30 build exited after Anaconda's reboot and reported `ID=fedora`,
`VERSION_ID=44`, and `VARIANT_ID=workstation`. Its qcow2 SHA-256 is
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
The exact image digest is pinned in the [target matrix](../../tests/acceptance/targets.json).
A new build can differ because the network repository and installation metadata
can change. Review and pin a new digest before using that image for acceptance.

The disk remains a candidate test fixture until it boots through the VM harness
and passes its package checks. The harness creates a fresh overlay for each
scenario. Keep the base qcow2 read-only during testing. To recover host space
after evidence is recorded, delete only the disposable build directory and
test overlays; retain the signed source checksum, build recipe, image digest,
and acceptance results in this repository.
