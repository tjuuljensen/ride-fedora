#!/bin/sh
#
# Purpose:
#   Shared POSIX shell storage, checksum, manifest, and rotation functions.
#
# Behavior:
#   Download or import complete images, reuse verified duplicates, and rotate owned copies.
#
# Compatibility:
#   POSIX sh on Unix; requires curl, jq, and a SHA-256 utility.
#
# Usage:
#   Sourced by tools/download-linux-images.sh and tools/download-vm-images.sh.
#
# Inputs / environment:
#   Publisher resolver functions set DI_ID, DI_ARCH, DI_VERSION, DI_FILENAME,
#   DI_URL, DI_SHA256, DI_CHECKSUM_URL, and optionally DI_SIZE.
#
# Outputs / side effects:
#   Writes images, manifest.json, and quarantine/ under DI_DESTINATION.
#
# Prerequisites:
#   HTTPS access, curl, jq, awk, sed, and sha256sum, shasum, or openssl.
#
# Author:
#   tjuuljensen/ride-fedora maintainers.
#
# Based on:
#   Legacy v2 functions as design references; no source copied.
#
# Version:
#   0.1.0, shared with both download entry points.
#
# Changelog:
#   - 0.1.0: Initial POSIX shell image store with verification and rotation.
#

DI_VERSION_TOOL=0.1.0
DI_MAX_BYTES=17179869184
DI_META_MAX=2097152
DI_DESTINATION=
DI_TMP=
DI_KEEP=2
DI_SHA256=
DI_SIZE=


di_error() { printf '%s\n' "$*" >&2; }
di_fail() { di_error "$*"; return 1; }


di_require() {
    command -v curl >/dev/null 2>&1 || { di_fail 'curl is required'; return 1; }
    command -v jq >/dev/null 2>&1 || { di_fail 'jq is required'; return 1; }
    if command -v sha256sum >/dev/null 2>&1; then DI_HASH_CMD=sha256sum
    elif command -v shasum >/dev/null 2>&1; then DI_HASH_CMD=shasum
    elif command -v openssl >/dev/null 2>&1; then DI_HASH_CMD=openssl
    else di_fail 'sha256sum, shasum, or openssl is required'; return 1
    fi
}


di_hash() {
    case $DI_HASH_CMD in
        sha256sum) sha256sum "$1" | awk '{print tolower($1)}' ;;
        shasum) shasum -a 256 "$1" | awk '{print tolower($1)}' ;;
        openssl) openssl dgst -sha256 "$1" | sed 's/^.*= *//' | tr 'A-F' 'a-f' ;;
    esac
}


di_http() {
    case $1 in https://*) ;; *) di_fail "HTTPS URL required: $1"; return 1 ;; esac
    body=$(curl --fail --location --silent --show-error --proto '=https' --proto-redir '=https' \
        --connect-timeout 20 --max-time 120 "$1") || return 1
    [ "${#body}" -le "$DI_META_MAX" ] || { di_fail "publisher metadata too large: $1"; return 1; }
    printf '%s\n' "$body"
}


di_file_url() {
    case $1 in https://*) ;; *) di_fail "HTTPS URL required: $1"; return 1 ;; esac
    curl --fail --location --silent --show-error --proto '=https' --proto-redir '=https' \
        --connect-timeout 30 --max-filesize "$DI_MAX_BYTES" --output "$2" "$1"
}


di_safe_field() {
    case $1 in ''|*[!A-Za-z0-9._+-]*) return 1 ;; esac
    case $1 in .*|*..*) return 1 ;; esac
    return 0
}


di_manifest_load() {
    DI_MANIFEST=$DI_DESTINATION/manifest.json
    if [ -L "$DI_MANIFEST" ]; then di_fail 'manifest.json is a symlink'; return 1; fi
    if [ ! -e "$DI_MANIFEST" ]; then
        printf '{"schemaVersion":1,"artifacts":[]}\n' > "$DI_TMP/manifest.json" || return 1
        DI_MANIFEST=$DI_TMP/manifest.json
        return 0
    fi
    jq -e 'type == "object" and .schemaVersion == 1 and (.artifacts | type == "array")' \
        "$DI_MANIFEST" >/dev/null || { di_fail 'unsupported or malformed image manifest'; return 1; }
    jq -e 'all(.artifacts[]; (.id|type=="string") and (.path|type=="string") and
        (.sha256|test("^[a-f0-9]{64}$")) and (.version|type=="string") and
        (.architecture|type=="string") and (.retrievedAt|type=="string") and
        (.path|test("^images/[A-Za-z0-9._+-]+/[A-Za-z0-9._+-]+/[A-Za-z0-9._+-]+/[a-f0-9]{12}/[A-Za-z0-9._+-]+$")))' \
        "$DI_MANIFEST" >/dev/null || { di_fail 'invalid image manifest record'; return 1; }
}


di_manifest_save() {
    jq -S . "$DI_MANIFEST" > "$DI_TMP/manifest.new" || return 1
    mv "$DI_TMP/manifest.new" "$DI_DESTINATION/manifest.json" || return 1
    DI_MANIFEST=$DI_DESTINATION/manifest.json
}


di_checked_file() {
    case $1 in images/*) ;; *) di_fail "invalid managed path: $1"; return 1 ;; esac
    case /$1/ in */../*|*/./*) di_fail "invalid managed path: $1"; return 1 ;; esac
    p=$DI_DESTINATION
    oldifs=$IFS; IFS=/
    set -- $1
    IFS=$oldifs
    for part do
        p=$p/$part
        [ ! -L "$p" ] || { di_fail "managed path contains a symlink: $p"; return 1; }
    done
    printf '%s\n' "$p"
}


di_verified_record() {
    record_path=$1 record_hash=$2
    record_file=$(di_checked_file "$record_path") || return 1
    [ -f "$record_file" ] || return 1
    actual=$(di_hash "$record_file") || return 1
    [ "$actual" = "$record_hash" ]
}


di_record_for_path() {
    jq -c --arg path "$1" '[.artifacts[] | select(.path == $path)] | .[0] // empty' "$DI_MANIFEST"
}


di_record_for_digest() {
    jq -r --arg digest "$1" '.artifacts[] | select(.sha256 == $digest) | [.path,.sha256] | @tsv' "$DI_MANIFEST" > "$DI_TMP/duplicates"
    while IFS="$(printf '\t')" read -r candidate_path candidate_digest; do
        [ -n "$candidate_path" ] || continue
        if di_verified_record "$candidate_path" "$candidate_digest"; then
            printf '%s\n' "$candidate_path"
            return 0
        fi
    done < "$DI_TMP/duplicates"
    return 1
}


di_write_record() {
    rec=$(jq -n --arg id "$DI_ID" --arg architecture "$DI_ARCH" --arg version "$DI_VERSION" \
        --arg filename "$DI_FILENAME" --arg url "$DI_URL" --arg sha256 "$DI_SHA256" \
        --arg checksumUrl "$DI_CHECKSUM_URL" --arg path "$DI_RELATIVE" \
        --arg retrievedAt "$DI_NOW" --arg verification "$DI_VERIFICATION" \
        --argjson size "$DI_OBSERVED_SIZE" \
        '{id:$id,architecture:$architecture,version:$version,filename:$filename,url:$url,
          sha256:$sha256,checksumUrl:$checksumUrl,path:$path,size:$size,
          retrievedAt:$retrievedAt,verification:$verification}') || return 1
    jq --arg path "$DI_RELATIVE" --argjson record "$rec" \
        '.artifacts = ([.artifacts[] | select(.path != $path)] + [$record])' \
        "$DI_MANIFEST" > "$DI_TMP/manifest.updated" || return 1
    mv "$DI_TMP/manifest.updated" "$DI_MANIFEST" || return 1
    di_manifest_save
}


di_publish() {
    DI_RELATIVE=images/$DI_ID/$DI_ARCH/$DI_VERSION/$(printf '%.12s' "$DI_SHA256")/$DI_FILENAME
    target=$(di_checked_file "$DI_RELATIVE") || return 1
    existing=$(di_record_for_path "$DI_RELATIVE")
    if [ -n "$existing" ] && di_verified_record "$DI_RELATIVE" "$DI_SHA256"; then
        printf '%s: skipped verified existing (%s)\n' "$DI_ID" "$DI_VERSION"
        di_rotate "$DI_ID" "$DI_KEEP" no
        return $?
    fi
    if [ -e "$target" ]; then
        [ -n "$existing" ] || { di_fail "unmanaged image exists at $DI_RELATIVE"; return 1; }
        mkdir -p "$DI_DESTINATION/quarantine" || return 1
        mv "$target" "$DI_DESTINATION/quarantine/$DI_ID-$(date -u +%Y%m%dT%H%M%SZ)-$DI_FILENAME" || return 1
        di_error "preserved changed image in quarantine/$DI_ID-$(date -u +%Y%m%dT%H%M%SZ)-$DI_FILENAME"
    fi
    mkdir -p "$(dirname "$target")" || return 1
    duplicate=$(di_record_for_digest "$DI_SHA256" || :)
    temporary=$DI_TMP/image
    if [ -n "$duplicate" ]; then
        source_file=$(di_checked_file "$duplicate") || return 1
        cp "$source_file" "$temporary" || return 1
        status='reused verified local image'
    elif [ -n "$DI_IMPORT_FILE" ]; then
        [ -f "$DI_IMPORT_FILE" ] && [ ! -L "$DI_IMPORT_FILE" ] || { di_fail "not a regular local file: $DI_IMPORT_FILE"; return 1; }
        cp "$DI_IMPORT_FILE" "$temporary" || return 1
        status='imported and checksum verified'
    else
        di_file_url "$DI_URL" "$temporary" || return 1
        status='downloaded and checksum verified'
    fi
    bytes=$(wc -c < "$temporary" | tr -d ' ')
    case $bytes in ''|*[!0-9]*) di_fail 'could not determine image size'; return 1 ;; esac
    [ "$bytes" -gt 0 ] && [ "$bytes" -le "$DI_MAX_BYTES" ] || { di_fail 'image size outside supported limits'; return 1; }
    if [ -n "$DI_SIZE" ] && [ "$bytes" -ne "$DI_SIZE" ]; then
        di_fail "publisher size mismatch for $DI_ID: $bytes != $DI_SIZE"; return 1
    fi
    actual=$(di_hash "$temporary") || return 1
    [ "$actual" = "$DI_SHA256" ] || { di_fail "publisher SHA-256 mismatch for $DI_ID"; return 1; }
    [ ! -e "$target" ] && [ ! -L "$target" ] || { di_fail "refusing to replace existing image: $target"; return 1; }
    mv "$temporary" "$target" || return 1
    DI_OBSERVED_SIZE=$bytes
    DI_NOW=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
    if [ -n "$DI_IMPORT_FILE" ]; then DI_VERIFICATION='manually obtained file matched publisher SHA-256; signature not checked'
    else DI_VERIFICATION='HTTPS publisher image matched publisher SHA-256; signature not checked'; fi
    di_write_record || return 1
    printf '%s: %s (%s)\n' "$DI_ID" "$status" "$DI_VERSION"
    di_rotate "$DI_ID" "$DI_KEEP" no
}


di_rotate() {
    rotate_id=$1 rotate_keep=$2 rotate_dry=$3
    jq -r --arg id "$rotate_id" '.artifacts[] | select(.id == $id) | [.path,.sha256,.retrievedAt] | @tsv' \
        "$DI_MANIFEST" | sort -t "$(printf '\t')" -k3,3r > "$DI_TMP/rotation"
    retained=0
    while IFS="$(printf '\t')" read -r rp rh rt; do
        [ -n "$rp" ] || continue
        rf=$(di_checked_file "$rp") || return 1
        if [ -f "$rf" ]; then
            if ! di_verified_record "$rp" "$rh"; then
                di_error "preserved modified old image: $rp"
                continue
            fi
            retained=$((retained + 1))
            if [ "$retained" -le "$rotate_keep" ]; then continue; fi
            if [ "$rotate_dry" = yes ]; then printf 'would prune: %s\n' "$rp"; continue; fi
            rm -f "$rf" || return 1
        else
            [ "$rotate_dry" = yes ] && { printf 'would prune missing record: %s\n' "$rp"; continue; }
        fi
        jq --arg path "$rp" '.artifacts = [.artifacts[] | select(.path != $path)]' \
            "$DI_MANIFEST" > "$DI_TMP/manifest.updated" || return 1
        mv "$DI_TMP/manifest.updated" "$DI_MANIFEST" || return 1
        if [ "$rotate_dry" != yes ]; then
            for parent in "$(dirname "$rf")" "$(dirname "$(dirname "$rf")")" \
                "$(dirname "$(dirname "$(dirname "$rf")")")"; do rmdir "$parent" 2>/dev/null || :; done
            printf 'pruned: %s\n' "$rp"
        fi
    done < "$DI_TMP/rotation"
    [ "$rotate_dry" = yes ] || di_manifest_save
}


di_fetch_selection() {
    selected=$1
    DI_IMPORT_FILE=
    resolve_image "$selected" || return 1
    di_validate_image || return 1
    di_publish
}


di_validate_image() {
    [ "$DI_ID" = "$DI_SELECTED" ] || { di_fail 'resolver returned the wrong selection'; return 1; }
    for f in "$DI_ID" "$DI_ARCH" "$DI_VERSION" "$DI_FILENAME"; do
        di_safe_field "$f" || { di_fail "unsafe publisher field: $f"; return 1; }
    done
    case $DI_URL:$DI_CHECKSUM_URL in https://*:https://*) ;; *) di_fail 'publisher URLs must use HTTPS'; return 1 ;; esac
    case $DI_SHA256 in *[!a-fA-F0-9]*|'') di_fail 'invalid publisher SHA-256'; return 1 ;; esac
    [ "${#DI_SHA256}" -eq 64 ] || { di_fail 'invalid publisher SHA-256 length'; return 1; }
    DI_SHA256=$(printf '%s' "$DI_SHA256" | tr 'A-F' 'a-f')
    case $DI_SIZE in ''|*[!0-9]*) DI_SIZE= ;; esac
    [ -z "$DI_SIZE" ] || [ "$DI_SIZE" -le "$DI_MAX_BYTES" ] || { di_fail 'publisher image exceeds supported size'; return 1; }
}


di_main() {
    command_name=$1; shift
    case ${1-} in --version) printf '%s\n' "$DI_VERSION_TOOL"; return 0 ;; esac
    if [ "${1-}" = list ]; then printf '%s\n' "$DI_IDS"; return 0; fi
    action=$1; shift || :
    case $action in plan|fetch|import|verify|prune) ;; *) printf 'usage: %s {list|plan|fetch|import|verify|prune} ...\n' "$command_name" >&2; return 2 ;; esac
    DI_SELECTED=
    DI_DESTINATION=
    DI_IMPORT_FILE=
    while [ $# -gt 0 ]; do
        case $1 in
            --destination) [ $# -ge 2 ] || return 2; DI_DESTINATION=$2; shift 2 ;;
            --keep) [ $# -ge 2 ] || return 2; DI_KEEP=$2; shift 2 ;;
            --file) [ $# -ge 2 ] || return 2; DI_IMPORT_FILE=$2; shift 2 ;;
            --dry-run) DI_DRY_RUN=yes; shift ;;
            *) [ -z "$DI_SELECTED" ] || { di_fail "unexpected argument: $1"; return 2; }; DI_SELECTED=$1; shift ;;
        esac
    done
    [ -n "$DI_DESTINATION" ] || { di_fail '--destination is required'; return 2; }
    case $DI_KEEP in ''|*[!0-9]*|0) di_fail '--keep must be a positive integer'; return 2 ;; esac
    [ ! -L "$DI_DESTINATION" ] || { di_fail 'destination is a symlink'; return 1; }
    di_require || return 1
    DI_TMP=$(mktemp -d "${TMPDIR:-/tmp}/ride-images.XXXXXX") || return 1
    trap 'rm -rf "$DI_TMP"' 0 HUP INT TERM
    mkdir -p "$DI_DESTINATION" || return 1
    DI_DESTINATION=$(cd -P "$DI_DESTINATION" && pwd) || return 1
    DI_LOCK=$DI_DESTINATION/.lock.d
    if [ "$action" = fetch ] || [ "$action" = import ] || [ "$action" = prune ]; then
        if ! mkdir "$DI_LOCK" 2>/dev/null; then di_fail 'another downloader holds the destination lock'; return 1; fi
        trap 'rmdir "$DI_LOCK" 2>/dev/null || :; rm -rf "$DI_TMP"' 0 HUP INT TERM
    fi
    di_manifest_load || return 1
    case $action in
        fetch)
            if [ "$DI_SELECTED" = all ]; then selections=$DI_IDS
            else selections=$DI_SELECTED; fi
            errors=0
            for selection in $selections; do
                if [ "$selection" = sift ]; then di_error 'sift: requires portal login; use import sift --file PATH'; errors=$((errors + 1)); continue; fi
                DI_SELECTED=$selection
                di_fetch_selection "$selection" || errors=$((errors + 1))
            done
            [ "$errors" -eq 0 ]
            ;;
        import)
            [ "$DI_SELECTED" = sift ] && [ -n "$DI_IMPORT_FILE" ] || { di_fail 'usage: import sift --file FILE --destination DIR'; return 2; }
            DI_SELECTED=sift
            resolve_image sift || return 1
            di_validate_image || return 1
            di_publish
            ;;
        plan)
            [ -n "$DI_SELECTED" ] || { di_fail 'selection or all is required'; return 2; }
            if [ "$DI_SELECTED" = all ]; then selections=$DI_IDS; else selections=$DI_SELECTED; fi
            errors=0
            for selection in $selections; do
                DI_SELECTED=$selection
                if resolve_image "$selection" && di_validate_image; then
                    DI_RELATIVE=images/$DI_ID/$DI_ARCH/$DI_VERSION/$(printf '%.12s' "$DI_SHA256")/$DI_FILENAME
                    record=$(di_record_for_path "$DI_RELATIVE")
                    if [ -n "$record" ] && di_verified_record "$DI_RELATIVE" "$DI_SHA256"; then status='skip: verified local copy'; else status='download required'; fi
                    [ "$selection" = sift ] && status='manual portal import required'
                    printf '%s: %s %s %s\n' "$selection" "$DI_VERSION" "$status" "$DI_URL"
                else di_error "$selection: unavailable or failed"; errors=$((errors + 1)); fi
            done
            [ "$errors" -eq 0 ]
            ;;
        verify)
            jq -r '.artifacts[] | [.id,.path,.sha256] | @tsv' "$DI_MANIFEST" > "$DI_TMP/verify"
            errors=0
            while IFS="$(printf '\t')" read -r id rp rh; do
                case " $DI_IDS " in *" $id "*) ;; *) continue ;; esac
                if di_verified_record "$rp" "$rh"; then printf 'OK %s\n' "$rp"
                else printf 'FAIL %s\n' "$rp"; errors=$((errors + 1)); fi
            done < "$DI_TMP/verify"
            [ "$errors" -eq 0 ]
            ;;
        prune)
            [ -n "${DI_DRY_RUN-}" ] || :
            for selection in $DI_IDS; do di_rotate "$selection" "$DI_KEEP" "${DI_DRY_RUN-no}" || return 1; done
            ;;
    esac
}
