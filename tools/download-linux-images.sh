#!/bin/sh
#
# Purpose:
#   Download and maintain verified Linux distribution images.
#
# Behavior:
#   Resolve publisher releases, verify SHA-256, skip duplicates, and rotate.
#
# Compatibility:
#   POSIX sh on Unix; requires curl, jq, and a SHA-256 utility.
#
# Usage:
#   tools/download-linux-images.sh {list,plan,fetch,verify,prune} [options]
#
# Inputs / environment:
#   Selection ID, destination, HTTPS publisher metadata and image files.
#
# Outputs / side effects:
#   Writes images, manifest.json, and quarantine/ under the destination.
#
# Prerequisites:
#   curl, jq, mktemp, awk, sed, and sha256sum, shasum, or openssl.
#
# Author:
#   tjuuljensen/ride-fedora maintainers.
#
# Based on:
#   lib/distro/lib-distro.sh as a design reference; no source copied.
#
# Version:
#   0.1.0.
#
# Changelog:
#   - 0.1.0: Added POSIX shell full-image downloads, manifest reuse, and rotation.
#
DI_IDS='debian debian-netinst ubuntu ubuntu-server fedora fedora-server kali kali-live mint tails raspios-lite raspios-full securityonion arch'
SCRIPT_DIR=$(CDPATH= cd -P "$(dirname "$0")" && pwd) || exit 1
. "$SCRIPT_DIR/lib/image-download-common.sh" || exit 1

resolve_image() {
    DI_ID=$1 DI_ARCH=x86_64 DI_SIZE= DI_CHECKSUM_URL= DI_URL= DI_SHA256=
    case $1 in
        debian|debian-netinst)
            folder=iso-dvd; pattern='debian-[0-9.]+-amd64-DVD-1[.]iso'
            if [ "$1" = debian-netinst ]; then folder=iso-cd; pattern='debian-[0-9.]+-amd64-netinst[.]iso'; fi
            base=https://cdimage.debian.org/debian-cd/current/amd64/$folder/
            page=$(di_http "$base") || return 1
            DI_FILENAME=$(printf '%s\n' "$page" | sed -n 's/.*href="\([^"]*\.iso\)".*/\1/p' | awk -v p="$pattern" '$0 ~ p {x=$0} END {print x}')
            [ -n "$DI_FILENAME" ] || return 1
            DI_VERSION=$(printf '%s' "$DI_FILENAME" | sed 's/^debian-\([0-9.]*\)-.*/\1/')
            DI_URL=$base$DI_FILENAME; DI_CHECKSUM_URL=${base}SHA256SUMS
            sums=$(di_http "$DI_CHECKSUM_URL") || return 1
            DI_SHA256=$(printf '%s\n' "$sums" | awk -v f="$DI_FILENAME" '$2=="*"f || $2==f {print $1; exit}')
            ;;
        ubuntu|ubuntu-server)
            root=https://releases.ubuntu.com/
            index=$(di_http "$root") || return 1
            versions=$(printf '%s\n' "$index" | sed -n 's/.*href="\([0-9][0-9]\.[0-9][0-9]\/\)".*/\1/p' | tr -d / | sort -r)
            for version in $versions; do
                base=$root$version/
                if [ "$1" = ubuntu-server ]; then DI_FILENAME=ubuntu-$version-live-server-amd64.iso
                else DI_FILENAME=ubuntu-$version-desktop-amd64.iso; fi
                page=$(di_http "$base") || continue
                printf '%s\n' "$page" | grep -F "$DI_FILENAME" >/dev/null || continue
                DI_VERSION=$version; DI_URL=$base$DI_FILENAME; DI_CHECKSUM_URL=${base}SHA256SUMS
                sums=$(di_http "$DI_CHECKSUM_URL") || return 1
                DI_SHA256=$(printf '%s\n' "$sums" | awk -v f="$DI_FILENAME" '$2=="*"f || $2==f {print $1; exit}')
                break
            done
            [ -n "$DI_URL" ] || return 1
            ;;
        fedora|fedora-server)
            meta=https://fedoraproject.org/releases.json
            rows=$(di_http "$meta") || return 1
            variant=Workstation; [ "$1" = fedora-server ] && variant=Server
            row=$(printf '%s' "$rows" | jq -r --arg v "$variant" '[.[] | select((.version|tostring|test("^[0-9]+$")) and .arch=="x86_64" and .variant==$v and .subvariant==$v and (.link|endswith(".iso")) and (if $v=="Server" then (.link|contains("-dvd-")) else (.link|contains("-Live-")) end))] | sort_by(.version|tonumber) | last | [.version,.link,.sha256,.size] | @tsv') || return 1
            oldifs=$IFS; IFS="$(printf '\t')"; set -- $row; IFS=$oldifs
            DI_VERSION=$1 DI_URL=$2 DI_SHA256=$3 DI_SIZE=$4 DI_FILENAME=${2##*/} DI_CHECKSUM_URL=$meta
            ;;
        kali|kali-live)
            base=https://cdimage.kali.org/current/
            page=$(di_http "$base") || return 1
            kind=installer; [ "$1" = kali-live ] && kind=live
            DI_FILENAME=$(printf '%s\n' "$page" | sed -n 's/.*href="\([^"]*\.iso\)".*/\1/p' | awk -v k="$kind" '$0 ~ ("kali-linux-[0-9.]+-" k "-amd64\\.iso") {print;exit}')
            [ -n "$DI_FILENAME" ] || return 1
            DI_VERSION=$(printf '%s' "$DI_FILENAME" | sed 's/^kali-linux-\([0-9.]*\)-.*/\1/')
            DI_URL=$base$DI_FILENAME; DI_CHECKSUM_URL=${base}SHA256SUMS
            sums=$(di_http "$DI_CHECKSUM_URL") || return 1
            DI_SHA256=$(printf '%s\n' "$sums" | awk -v f="$DI_FILENAME" '$2=="*"f || $2==f {print $1;exit}')
            ;;
        mint)
            root=https://mirrors.edge.kernel.org/linuxmint/stable/
            index=$(di_http "$root") || return 1
            version=$(printf '%s\n' "$index" | sed -n 's/.*href="\([0-9][0-9.]*\/\)".*/\1/p' | tr -d / | sort -r | sed -n '1p')
            [ -n "$version" ] || return 1
            base=$root$version/; DI_FILENAME=linuxmint-$version-cinnamon-64bit.iso
            page=$(di_http "$base") || return 1; printf '%s\n' "$page" | grep -F "$DI_FILENAME" >/dev/null || return 1
            DI_VERSION=$version DI_URL=$base$DI_FILENAME DI_CHECKSUM_URL=${base}sha256sum.txt
            sums=$(di_http "$DI_CHECKSUM_URL") || return 1
            DI_SHA256=$(printf '%s\n' "$sums" | awk -v f="$DI_FILENAME" '$2=="*"f || $2==f {print $1;exit}')
            ;;
        tails)
            meta=https://tails.net/install/v2/Tails/amd64/stable/latest.json
            body=$(di_http "$meta") || return 1
            row=$(printf '%s' "$body" | jq -r 'select(.channel=="stable" and .build_target=="amd64") | .installations[] | [.version,([.["installation-paths"][] | select(.type=="img") | .["target-files"][] | select(.url|endswith(".img"))][0].url),([.["installation-paths"][] | select(.type=="img") | .["target-files"][] | select(.url|endswith(".img"))][0].sha256),([.["installation-paths"][] | select(.type=="img") | .["target-files"][] | select(.url|endswith(".img"))][0].size)] | @tsv') || return 1
            oldifs=$IFS; IFS="$(printf '\t')"; set -- $row; IFS=$oldifs
            DI_VERSION=$1 DI_URL=$2 DI_SHA256=$3 DI_SIZE=$4 DI_FILENAME=${2##*/} DI_CHECKSUM_URL=$meta
            ;;
        raspios-lite|raspios-full)
            meta=https://downloads.raspberrypi.com/os_list_imagingutility_v4.json
            body=$(di_http "$meta") || return 1
            desired='Raspberry Pi OS Lite (64-bit)'; [ "$1" = raspios-full ] && desired='Raspberry Pi OS Full (64-bit)'
            row=$(printf '%s' "$body" | jq -r --arg n "$desired" '[.os_list[]?.subitems[]? | select(.name==$n)] | .[0] | [.release_date,.url,.image_download_size] | @tsv') || return 1
            oldifs=$IFS; IFS="$(printf '\t')"; set -- $row; IFS=$oldifs
            DI_VERSION=$1 DI_URL=$2 DI_SIZE=$3 DI_ARCH=arm64 DI_FILENAME=${2##*/} DI_CHECKSUM_URL=$2.sha256
            DI_SHA256=$(di_http "$DI_CHECKSUM_URL" | awk 'NR==1 {print $1}')
            ;;
        securityonion)
            meta=https://raw.githubusercontent.com/Security-Onion-Solutions/securityonion/3/main/DOWNLOAD_AND_VERIFY_ISO.md
            body=$(di_http "$meta") || return 1
            row=$(printf '%s\n' "$body" | awk '/^https:\/\/download\.securityonion\.net\/file\/securityonion\/securityonion-[A-Za-z0-9.-]+\.iso$/ {u=$0} /^SHA256:/ {h=$2} END {sub(/^.*\//,"",u); print u "\t" h}')
            oldifs=$IFS; IFS="$(printf '\t')"; set -- $row; IFS=$oldifs
            DI_FILENAME=$1 DI_SHA256=$2 DI_VERSION=$(printf '%s' "$1" | sed 's/^securityonion-//;s/\.iso$//')
            DI_URL=https://download.securityonion.net/file/securityonion/$DI_FILENAME DI_CHECKSUM_URL=$meta
            ;;
        arch)
            meta=https://archlinux.org/download/
            body=$(di_http "$meta") || return 1
            DI_VERSION=$(printf '%s\n' "$body" | sed -n 's/.*Current Release:[^0-9]*\([0-9][0-9][0-9][0-9]\.[0-9][0-9]\.[0-9][0-9]\).*/\1/p' | sed -n '1p')
            [ -n "$DI_VERSION" ] || return 1
            DI_FILENAME=archlinux-$DI_VERSION-x86_64.iso
            DI_CHECKSUM_URL=https://archlinux.org/iso/$DI_VERSION/sha256sums.txt
            DI_SHA256=$(di_http "$DI_CHECKSUM_URL" | awk -v f="$DI_FILENAME" '$2=="*"f || $2==f {print $1;exit}')
            DI_URL=https://fastly.mirror.pkgbuild.com/iso/$DI_VERSION/$DI_FILENAME
            ;;
        *) di_fail "unknown selection: $1"; return 1 ;;
    esac
}

if [ "${1-}" = --help ] || [ "${1-}" = -h ]; then
    printf '%s\n' 'Usage: download-linux-images.sh {list|plan|fetch|verify|prune} [selection|all] --destination DIR [--keep N] [--dry-run]'
    printf '%s\n' 'Selections:' "$DI_IDS" 'Requires curl, jq, and SHA-256 utility.'
    exit 0
fi
di_main "$0" "$@"
