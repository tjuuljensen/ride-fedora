# Fedora 44 Server acceptance image

This locally installed Fedora 44 x86_64 Server guest is a target for the
`server-base` package pilot. It is not a Fedora-provided qcow2. The source is
the Fedora Everything netinstaller release 44-1.7. Its signed checksum was
verified with Fedora release key `36F612DCF27F7D1A48A835E4DBFCF71C6D9F90A6`;
the ISO SHA-256 is
`bd285201494dd0ba09b54d05ac707de1401668b8512a573edb5922dcf9d7067e`.
The [Server Kickstart recipe](../../tests/acceptance/fedora-44-server.ks)
SHA-256 is `be6f79592fb02091b281bc4a642445db94b5f3c45e6e9f6f59f704218dac9f80`.
It selects `@^server-product-environment`, `cloud-init`, `openssh-server`,
`sudo`, and `jq`; host-specific shares and secrets are absent.

## Build from the verified ISO

Run from the repository root as a regular user with `/dev/kvm` and network
access. The host needs `isoinfo`, `genisoimage`, `qemu-img`, QEMU with KVM, and
libguestfs. Verify the ISO signature and checksum using Fedora's download
instructions before running this block. The block checks the pinned checksum,
creates an ignored disposable directory, downloads Fedora RPMs inside the VM,
and installs only to its new qcow2. It does not change host packages or disks.
Use a fresh output directory for each rebuild.

```bash
set -euo pipefail
iso=/absolute/path/to/Fedora-Everything-netinst-x86_64-44-1.7.iso
out=.acceptance-runs/server-image
test "$(sha256sum "$iso" | cut -d ' ' -f1)" = bd285201494dd0ba09b54d05ac707de1401668b8512a573edb5922dcf9d7067e
mkdir -p "$out"
isoinfo -i "$iso" -R -x /images/pxeboot/vmlinuz > "$out/vmlinuz"
isoinfo -i "$iso" -R -x /images/pxeboot/initrd.img > "$out/initrd.img"
genisoimage -quiet -o "$out/ks.iso" -V OEMDRV -J -R -graft-points \
  "ks.cfg=$PWD/tests/acceptance/fedora-44-server.ks"
qemu-img create -f qcow2 "$out/server.qcow2" 40G
timeout 3600 qemu-system-x86_64 -accel kvm -machine q35 -cpu host \
  -smp 4 -m 6144 -display none -monitor none -serial "file:$out/install-serial.log" \
  -no-reboot -drive "file=$out/server.qcow2,if=virtio,format=qcow2" \
  -cdrom "$iso" -drive "file=$out/ks.iso,media=cdrom,readonly=on" \
  -netdev user,id=net0 -device virtio-net-pci,netdev=net0 \
  -kernel "$out/vmlinuz" -initrd "$out/initrd.img" \
  -append 'inst.stage2=hd:LABEL=Fedora-E-dvd-x86_64-44 inst.ks=hd:LABEL=OEMDRV:/ks.cfg inst.cmdline console=ttyS0 inst.text ip=dhcp'
LIBGUESTFS_BACKEND=direct virt-cat -a "$out/server.qcow2" /etc/os-release
sha256sum "$out/server.qcow2"
```

The 2026-10-30 build exited after Anaconda's reboot. `/etc/os-release`
reported `ID=fedora`, `VERSION_ID=44`, and `VARIANT_ID=server`. Its qcow2
SHA-256 is
`efb75956d6dbde0801059fdac4a8a1451f06ecc843344ecdb71bb3e8d247af90`,
pinned in the [target matrix](../../tests/acceptance/targets.json). A rebuild
may differ as network repository content changes; review and pin its new
digest before acceptance. The base image remains read-only for disposable VM
overlays. Delete only the build output and overlays when no longer needed;
retain the checksum, recipe, digest, and acceptance records in the repository.
