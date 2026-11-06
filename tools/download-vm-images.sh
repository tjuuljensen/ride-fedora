#!/bin/sh
#
# Purpose:
#   Download and maintain verified virtual-machine images.
#
# Behavior:
#   Resolve current releases, verify SHA-256, skip duplicates, and rotate.
#
# Compatibility:
#   POSIX sh on Unix; requires curl, jq, and a SHA-256 utility.
#
# Usage:
#   tools/download-vm-images.sh {list,plan,fetch,import,verify,prune} [options]
#
# Inputs / environment:
#   Selection ID, destination, HTTPS metadata, or local SIFT OVA.
#
# Outputs / side effects:
#   Writes VM archives, manifest.json, and quarantine/ under the destination.
#
# Prerequisites:
#   curl, jq, mktemp, awk, sed, and sha256sum, shasum, or openssl.
#
# Author:
#   tjuuljensen/ride-fedora maintainers.
#
# Based on:
#   lib/vm/lib-vm.sh as a design reference; no source copied.
#
# Version:
#   0.1.0.
#
# Changelog:
#   - 0.1.0: Added verified VM downloads, SIFT import, and rotation.
#
DI_IDS='remnux-vmware remnux-virtualbox kali-vmware kali-virtualbox sift sof-elk'
SCRIPT_DIR=$(CDPATH= cd -P "$(dirname "$0")" && pwd) || exit 1
. "$SCRIPT_DIR/lib/image-download-common.sh" || exit 1
REMNUX_PAGE=https://docs.remnux.org/install-distro/get-virtual-appliance.md
SOF_ELK_PAGE=https://raw.githubusercontent.com/wiki/philhagen/sof-elk/Virtual-Machine-README.md
SIFT_PAGE=https://www.sans.org/tools/sift-workstation/

resolve_image() {
    DI_ID=$1 DI_ARCH=x86_64 DI_SIZE= DI_CHECKSUM_URL= DI_URL= DI_SHA256=
    case $1 in
        remnux-vmware|remnux-virtualbox)
            body=$(di_http "$REMNUX_PAGE") || return 1
            flavor=VMware; suffix=; [ "$1" = remnux-virtualbox ] && { flavor=VirtualBox; suffix=-virtualbox; }
            row=$(printf '%s\n' "$body" | awk -v f="$flavor" -v s="$suffix" '
                index($0,"Download " f " OVA") {match($0,/https:\/\/download\.remnux\.org\/[^"]+\.ova/); url=substr($0,RSTART,RLENGTH)}
                url!="" && /^```$/ {getline; if ($0 ~ /^[a-fA-F0-9]{64}$/) {print url "\t" $0; exit}}
            ')
            oldifs=$IFS; IFS="$(printf '\t')"; set -- $row; IFS=$oldifs
            DI_URL=$1 DI_SHA256=$2 DI_CHECKSUM_URL=$REMNUX_PAGE DI_FILENAME=${1##*/}
            DI_VERSION=$(printf '%s' "$DI_URL" | sed 's|.*/\([A-Za-z0-9._-]*\)/remnux-.*|\1|')
            ;;
        kali-vmware|kali-virtualbox)
            base=https://cdimage.kali.org/kali-images/current/
            page=$(di_http "$base") || return 1
            kind=vmware; [ "$1" = kali-virtualbox ] && kind=virtualbox
            DI_FILENAME=$(printf '%s\n' "$page" | sed -n 's/.*href="\([^"]*\.7z\)".*/\1/p' | awk -v k="$kind" '$0 ~ ("kali-linux-[0-9.]+-" k "-amd64\\.7z") {print;exit}')
            [ -n "$DI_FILENAME" ] || return 1
            DI_VERSION=$(printf '%s' "$DI_FILENAME" | sed 's/^kali-linux-\([0-9.]*\)-.*/\1/')
            DI_URL=$base$DI_FILENAME DI_CHECKSUM_URL=${base}SHA256SUMS
            DI_SHA256=$(di_http "$DI_CHECKSUM_URL" | awk -v f="$DI_FILENAME" '$2=="*"f || $2==f {print $1;exit}')
            ;;
        sof-elk)
            body=$(di_http "$SOF_ELK_PAGE") || return 1
            row=$(printf '%s\n' "$body" | awk '
                index($0,"Filename:") {
                    if (active) exit
                    if (index($0,"Public SOF-ELK x86 v")) {
                        active=1; name=$0; sub(/^.* v/,"",name); sub(/\.7z.*/,"",name)
                    }
                }
                active && index($0,"File size:") {
                    size=$0; sub(/^.*File size: `/,"",size); sub(/` bytes.*$/, "", size); gsub(/,/,"",size)
                }
                active && index($0,"SHA256:") {
                    hash=$0; sub(/^.*SHA256: `/,"",hash); sub(/`.*/,"",hash)
                    print name "\t" size "\t" hash; exit
                }
            ')
            oldifs=$IFS; IFS="$(printf '\t')"; set -- $row; IFS=$oldifs
            DI_VERSION=$1 DI_SIZE=$2 DI_SHA256=$3 DI_FILENAME=sof-elk-x86-v$1.7z
            DI_URL=https://for572.com/sof-elk-x86-vm DI_CHECKSUM_URL=$SOF_ELK_PAGE
            ;;
        sift)
            body=$(di_http "$SIFT_PAGE") || return 1
            DI_SHA256=$(printf '%s\n' "$body" | sed -n 's/.*sha256 *= *\([a-fA-F0-9][a-fA-F0-9]*\).*/\1/p' | tr 'A-F' 'a-f' | sort -u)
            [ "$(printf '%s\n' "$DI_SHA256" | wc -l | tr -d ' ')" -eq 1 ] || return 1
            DI_VERSION=sha256-$(printf '%.12s' "$DI_SHA256") DI_FILENAME=sift-workstation.ova
            DI_URL=$SIFT_PAGE DI_CHECKSUM_URL=$SIFT_PAGE
            ;;
        *) di_fail "unknown selection: $1"; return 1 ;;
    esac
}

if [ "${1-}" = --help ] || [ "${1-}" = -h ]; then
    printf '%s\n' 'Usage: download-vm-images.sh {list|plan|fetch|import|verify|prune} [selection|all] --destination DIR [--file OVA] [--keep N] [--dry-run]'
    printf '%s\n' 'Selections:' "$DI_IDS" 'SIFT requires portal login and local import.'
    printf '%s\n' 'Requires curl, jq, and SHA-256 utility.'
    exit 0
fi
di_main "$0" "$@"
