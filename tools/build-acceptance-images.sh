#!/usr/bin/env bash
# Purpose: Download, authenticate, build, and inspect disposable Fedora acceptance images.
# Behavior: Builds Workstation or Server qcow2 guests from Fedora Everything media and local Kickstarts.
# Compatibility: Bash 4+; x86_64 Fedora/Linux host.
# Usage: tools/build-acceptance-images.sh {fetch|build|inspect|boot|discard-incomplete} RELEASE EDITION [OUTPUT_ROOT]
# Inputs: Fedora release 44/45; edition workstation/server; Fedora-signed media and local Kickstart.
# Side effects: Writes downloads, build intermediates, logs, and qcow2 files beneath OUTPUT_ROOT.
# Prerequisites: curl, gpg, qemu, qemu-img, genisoimage, isoinfo, libguestfs tools; KVM strongly preferred.
# Owner: RIDE Fedora maintainers.
# Provenance: Adapted from docs/acceptance/fedora-44-{workstation,server}-image.md.
# Version: 1.0.0

set -euo pipefail

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
MODE=${1:-}
RELEASE=${2:-}
EDITION=${3:-}
OUTPUT_ROOT=${4:-"$ROOT/.acceptance-runs/fedora-images"}
KEY_FINGERPRINT=36F612DCF27F7D1A48A835E4DBFCF71C6D9F90A6

usage() { printf 'Usage: %s {fetch|build|inspect|boot|discard-incomplete} {44|45} {workstation|server} [OUTPUT_ROOT]\n' "$0" >&2; exit 2; }
[[ "$MODE" =~ ^(fetch|build|inspect|boot|discard-incomplete)$ && "$RELEASE" =~ ^(44|45)$ && "$EDITION" =~ ^(workstation|server)$ ]] || usage

version=1.7
if [[ "$RELEASE" == 45 ]]; then version=1.4; fi
media="Fedora-Everything-netinst-x86_64-${RELEASE}-${version}.iso"
checksum="Fedora-Everything-${RELEASE}-${version}-x86_64-CHECKSUM"
base_url="https://dl.fedoraproject.org/pub/fedora/linux/releases/${RELEASE}/Everything/x86_64/iso"
dest="$OUTPUT_ROOT/fedora-${RELEASE}-${EDITION}-x86_64"
iso="$OUTPUT_ROOT/$media"
ks="$ROOT/tests/acceptance/fedora-${RELEASE}-${EDITION}.ks"
[[ -f "$ks" ]] || { printf 'Missing Kickstart: %s\n' "$ks" >&2; exit 2; }
mkdir -p "$OUTPUT_ROOT" "$dest"
chmod 700 "$OUTPUT_ROOT" "$dest"

verify_metadata() {
  local gnupg_home="$OUTPUT_ROOT/gnupg"
  mkdir -p "$gnupg_home"
  chmod 700 "$gnupg_home"
  [[ -f "$OUTPUT_ROOT/fedora.gpg" && -f "$OUTPUT_ROOT/$checksum" ]] || {
    printf 'Missing Fedora signing key/checksum inputs; run fetch while online first.\n' >&2; return 1;
  }
  gpg --homedir "$gnupg_home" --import "$OUTPUT_ROOT/fedora.gpg" >/dev/null 2>&1
  local actual
  gpg --homedir "$gnupg_home" --with-colons --fingerprint | awk -F: '$1=="fpr"{print $10}' | grep -Fxq "$KEY_FINGERPRINT" || {
    printf 'Expected Fedora release key fingerprint %s was not found.\n' "$KEY_FINGERPRINT" >&2; return 1;
  }
  gpgv --keyring "$OUTPUT_ROOT/fedora.gpg" --output "$OUTPUT_ROOT/$checksum.verified" "$OUTPUT_ROOT/$checksum"
}

verify_media() {
  verify_metadata
  (cd "$OUTPUT_ROOT" && grep -F "$media" "$checksum.verified" | sha256sum --check -)
}

build_image_tmp=
preserve_failed_image() {
  if [[ -n "$build_image_tmp" && -e "$build_image_tmp" ]]; then
    failed_image="$dest/${EDITION}.failed-$(date -u +%Y%m%dT%H%M%SZ).qcow2"
    mv -- "$build_image_tmp" "$failed_image"
    printf 'Incomplete build retained for diagnosis: %s\n' "$failed_image" >&2
  fi
}
trap preserve_failed_image EXIT

download_metadata() {
  local key_url=https://fedoraproject.org/fedora.gpg
  curl --fail --location --retry 3 "$key_url" -o "$OUTPUT_ROOT/fedora.gpg"
  curl --fail --location --retry 3 "$base_url/$checksum" -o "$OUTPUT_ROOT/$checksum"
}

case "$MODE" in
  fetch)
    download_metadata
    verify_metadata
    curl --fail --location --retry 3 "$base_url/$media" -o "$iso"
    verify_media
    printf 'Verified ISO: %s\n' "$iso"
    ;;
  build)
    [[ -f "$iso" && -f "$OUTPUT_ROOT/$checksum" && -f "$OUTPUT_ROOT/$checksum.verified" ]] || { printf 'Run fetch first for Fedora %s.\n' "$RELEASE" >&2; exit 2; }
    verify_media
    (cd "$OUTPUT_ROOT" && grep -F "$media" "$checksum.verified" | sha256sum --check -)
    local_kernel="$dest/vmlinuz"
    local_initrd="$dest/initrd.img"
    isoinfo -i "$iso" -R -x /images/pxeboot/vmlinuz > "$local_kernel"
    isoinfo -i "$iso" -R -x /images/pxeboot/initrd.img > "$local_initrd"
    genisoimage -quiet -o "$dest/ks.iso" -V OEMDRV -J -R -graft-points "ks.cfg=$ks"
    image="$dest/${EDITION}.qcow2"
    [[ ! -e "$image" ]] || { printf 'Refusing to overwrite existing image: %s\n' "$image" >&2; exit 2; }
    build_image_tmp="$dest/.${EDITION}.building-$$.qcow2"
    qemu-img create -f qcow2 "$build_image_tmp" 40G
    accel=tcg
    if [[ -c /dev/kvm && -r /dev/kvm && -w /dev/kvm ]]; then accel=kvm; fi
    cpu=()
    if [[ "$accel" == kvm ]]; then cpu=(-cpu host); else cpu=(-cpu max); fi
    timeout 14400 qemu-system-x86_64 -accel "$accel" -machine q35 "${cpu[@]}" \
      -smp 4 -m 6144 -display none -monitor none \
      -serial "file:$dest/install-serial.log" -no-reboot \
      -drive "file=$build_image_tmp,if=virtio,format=qcow2" -cdrom "$iso" \
      -drive "file=$dest/ks.iso,media=cdrom,readonly=on" \
      -netdev user,id=net0 -device virtio-net-pci,netdev=net0 \
      -kernel "$local_kernel" -initrd "$local_initrd" \
      -append "inst.stage2=hd:LABEL=Fedora-E-dvd-x86_64-${RELEASE} inst.ks=hd:LABEL=OEMDRV:/ks.cfg inst.cmdline console=ttyS0 inst.text ip=dhcp"
    qemu-img check "$build_image_tmp"
    if ! LIBGUESTFS_BACKEND=direct virt-cat -a "$build_image_tmp" /etc/os-release > "$dest/os-release"; then
      printf 'Installer exited without installing an operating system. Review %s/install-serial.log.\n' "$dest" >&2
      exit 1
    fi
    grep -Fx "VERSION_ID=$RELEASE" "$dest/os-release"
    variant=$EDITION
    grep -Fx "VARIANT_ID=$variant" "$dest/os-release"
    image_hash=$(sha256sum "$build_image_tmp" | cut -d ' ' -f1)
    iso_hash=$(sha256sum "$iso" | cut -d ' ' -f1)
    ks_hash=$(sha256sum "$ks" | cut -d ' ' -f1)
    checksum_hash=$(sha256sum "$OUTPUT_ROOT/$checksum" | cut -d ' ' -f1)
    mv -- "$build_image_tmp" "$image"
    build_image_tmp=
    printf 'image_sha256=%s\niso_sha256=%s\nkickstart_sha256=%s\ninstaller_checksum_sha256=%s\niso_source=%s\ninstaller_checksum_file=%s\nrelease=%s\nedition=%s\narchitecture=x86_64\naccel=%s\n' \
      "$image_hash" "$iso_hash" "$ks_hash" "$checksum_hash" "$base_url/$media" \
      "$checksum" "$RELEASE" "$EDITION" "$accel" > "$dest/manifest.txt.tmp"
    mv -- "$dest/manifest.txt.tmp" "$dest/manifest.txt"
    printf 'Built and inspected image: %s\n' "$image"
    printf 'Image digest: %s\n' "$image_hash"
    ;;
  inspect)
    image="$dest/${EDITION}.qcow2"
    [[ -f "$image" ]] || { printf 'Missing image: %s\n' "$image" >&2; exit 2; }
    [[ -f "$dest/manifest.txt" ]] || { printf 'No successful-build manifest; this image is incomplete. Run discard-incomplete or inspect the retained failed image.\n' >&2; exit 2; }
    qemu-img check "$image"
    LIBGUESTFS_BACKEND=direct virt-cat -a "$image" /etc/os-release
    sha256sum "$image" "$ks"
    ;;
  discard-incomplete)
    image="$dest/${EDITION}.qcow2"
    [[ -f "$image" ]] || { printf 'No canonical image to quarantine: %s\n' "$image"; exit 0; }
    [[ ! -f "$dest/manifest.txt" ]] || { printf 'Refusing to move an image with a build manifest: %s\n' "$image" >&2; exit 2; }
    if LIBGUESTFS_BACKEND=direct virt-cat -a "$image" /etc/os-release >/dev/null 2>&1; then
      printf 'Image contains an OS; refusing automatic quarantine. Inspect manually: %s\n' "$image" >&2
      exit 2
    fi
    failed_image="$dest/${EDITION}.failed-$(date -u +%Y%m%dT%H%M%SZ).qcow2"
    mv -- "$image" "$failed_image"
    printf 'Moved incomplete image to: %s\n' "$failed_image"
    ;;
  boot)
    image="$dest/${EDITION}.qcow2"
    [[ -f "$image" ]] || { printf 'Missing image: %s\n' "$image" >&2; exit 2; }
    accel=tcg
    if [[ -c /dev/kvm && -r /dev/kvm && -w /dev/kvm ]]; then accel=kvm; fi
    python3 "$ROOT/tools/verify-acceptance-image.py" "$image" "$RELEASE" "$EDITION" \
      "$dest/boot-verification-$(date -u +%Y%m%dT%H%M%SZ)" --accel "$accel"
    ;;
esac
