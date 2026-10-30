#!/usr/bin/env bash
#
# mac-vendor.sh
#
# Purpose:
#   Look up the IEEE registry assignee/vendor for a MAC address or MAC prefix.
#
# Description:
#   Bash port of mac-vendor.py. Downloads and caches IEEE public MAC assignment
#   registries, then performs longest-prefix matching against normalized MAC
#   addresses. Accepts positional addresses, piped input, or interactive input.
#
#   Supported registries:
#     - MA-L / OUI   : 24-bit prefix
#     - MA-M         : 28-bit prefix
#     - MA-S / OUI36 : 36-bit prefix
#     - IAB          : 36-bit prefix
#
# Usage:
#   bash mac-vendor.sh 00:1A:2B:33:44:55
#   bash mac-vendor.sh --update
#   bash mac-vendor.sh --offline --show-address 00:1A:2B:33:44:55
#   bash mac-vendor.sh --quiet --json 00-1A-2B
#
# Cache:
#   Shares ieee-mac-vendors.tsv and metadata.json with mac-vendor.py under
#   ${XDG_CACHE_HOME:-$HOME/.cache}/mac-vendor, or the --cache-dir directory.
#   The default freshness threshold is seven days. --offline requires an
#   existing cache and cannot be combined with --update.
#
# Output model:
#   Default output includes the vendor, registry, prefix, and MAC flag notes.
#   --quiet prints only vendor names; --json prints an array of lookup results.
#   Together, --quiet and --json include only the organization field per query,
#   with null for unknown vendors. --show-address adds registry addresses to
#   normal text output.
#
# Requirements:
#   Bash 4+, awk, and standard Unix utilities including mktemp and stat.
#   curl is required for downloads only. Python and jq are not required.
#
# Security / privacy note:
#   Lookups use the local cache. Queried MAC addresses are never sent to an
#   online lookup service.
#
# Limitations:
#   Registry assignees do not prove a device's manufacturer or authenticity.
#   Locally administered/randomized MAC addresses may not resolve meaningfully.
#   Differences from Python include help layout, shell I/O errors, and curl
#   transport diagnostics/timeouts. curl's low-speed timeout approximates
#   urllib's read timeout.
#
# Author:
#   Torsten Juul-Jensen
#
# Version:
#   1.0.0
#
# Date:
#   2026-10-15
#

set -o pipefail
export LC_ALL=C
VERSION=1.0.0
prog=${0##*/}
quiet=0 update=0 offline=0 json=0 show_address=0
cache_dir=${XDG_CACHE_HOME:-${HOME:-~}/.cache}/mac-vendor
max_age=7 timeout=30
work_dir= update_dir=
addresses=()
cleanup() {
    [[ -z $update_dir ]] || rm -rf -- "$update_dir"
    [[ -z $work_dir ]] || rm -rf -- "$work_dir"
    return 0
}
trap cleanup EXIT
trap 'printf "Interrupted.\n" >&2; exit 130' INT
trap 'exit 129' HUP
trap 'exit 143' TERM
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
usage() {
    printf 'usage: %s [-h] [-s] [-u] [--offline] [--json] [--show-address]\n' "$prog"
    printf '                     [--cache-dir CACHE_DIR] [--max-age-days MAX_AGE_DAYS]\n'
    printf '                     [--timeout TIMEOUT] [--version]\n'
    printf '                     [addresses ...]\n'
}
arg_error() { usage >&2; printf '%s: error: %s\n' "$prog" "$*" >&2; exit 2; }
help() {
    usage
    cat <<'HELP'

Look up IEEE MAC/OUI vendor assignments.

positional arguments:
  addresses             MAC address or prefix to look up

options:
  -h, --help             show this help message and exit
  -s, --quiet            print only the vendor name (with --json: organization only)
  -u, --update           download and refresh the local IEEE cache
  --offline             do not download; require an existing cache
  --json                print JSON output
  --show-address        include registry address in normal output
  --cache-dir CACHE_DIR  cache directory
  --max-age-days N       cache freshness threshold (default: 7)
  --timeout N            download timeout in seconds (default: 30)
  --version             show program's version number and exit

Examples:
  mac-vendor.sh 00:1A:2B:33:44:55
  mac-vendor.sh --quiet 00-1A-2B
  mac-vendor.sh --update
  mac-vendor.sh --offline 00:1A:2B:33:44:55
  printf '%s\n' 00:1A:2B:33:44:55 3C:52:82:AA:BB:CC | mac-vendor.sh

Accepted input formats:
  00:1A:2B:33:44:55
  00-1A-2B-33-44-55
  001A.2B33.4455
  001A2B334455
  001A2B

Cache: $XDG_CACHE_HOME/mac-vendor or $HOME/.cache/mac-vendor.
--update and --offline cannot be combined. Without positional
addresses, read nonempty stdin lines or prompt on a terminal. On a terminal,
--update without addresses exits after refreshing. Piped empty input exits 2.
HELP
}
# argparse accepts signed integers, surrounding whitespace and digit separators.
parse_integer() {
    local value=$2
    value="${value#"${value%%[!$' \t\r\n\v\f']*}"}"
    value="${value%"${value##*[!$' \t\r\n\v\f']}"}"
    [[ $value =~ ^[+-]?[0-9]+(_[0-9]+)*$ ]] || arg_error "argument $1: invalid int value: '$2'"
    integer=${value//_/}
}
long_options=(--help --quiet --update --offline --json --show-address --cache-dir --max-age-days --timeout --version)
positionals_closed=0
unknown=()
while (($#)); do
    token=$1
    shift
    if [[ $token == -- ]]; then
        if ((positionals_closed)); then unknown+=("$token" "$@"); else addresses+=("$@"); fi
        break
    fi
    option=${token%%=*}
    has_value=0
    [[ $token != *=* ]] || has_value=1
    if [[ $option == --* ]]; then
        matches=()
        for candidate in "${long_options[@]}"; do
            if [[ $candidate == "$option" ]]; then matches=("$candidate"); break; fi
            [[ $candidate != "$option"* ]] || matches+=("$candidate")
        done
        if ((${#matches[@]} > 1)); then
            joined=$(IFS=,; printf '%s' "${matches[*]}")
            arg_error "ambiguous option: $option could match ${joined//,/, }"
        fi
        ((${#matches[@]} == 0)) || option=${matches[0]}
    elif [[ $token == -[shu]* && ${#token} -gt 2 ]]; then
        # argparse permits grouped no-argument short options (-su).
        short=${token:1}
        for ((i=0; i<${#short}; i++)); do
            case ${short:i:1} in
                s) quiet=1 ;;
                u) update=1 ;;
                h) help; exit 0 ;;
                *) arg_error "argument -${short:i-1:1}: ignored explicit argument '${short:i}'" ;;
            esac
        done
        ((${#addresses[@]} == 0)) || positionals_closed=1
        continue
    fi
    case $option in
        -h|--help|-s|--quiet|-u|--update|--offline|--json|--show-address|--version)
            if ((has_value)); then
                label=$option
                case $option in --help|-h) label=-h/--help;; --quiet|-s) label=-s/--quiet;; --update|-u) label=-u/--update;; esac
                arg_error "argument $label: ignored explicit argument '${token#*=}'"
            fi
            case $option in
                -h|--help) help; exit 0;;
                --version) printf '%s %s\n' "$prog" "$VERSION"; exit 0;;
                -s|--quiet) quiet=1;; -u|--update) update=1;;
                --offline) offline=1;; --json) json=1;; --show-address) show_address=1;;
            esac ;;
        --cache-dir|--max-age-days|--timeout)
            if ((has_value)); then value=${token#*=}; else
                (($#)) || arg_error "argument $option: expected one argument"
                if [[ $1 == -* && $1 != - && ! $1 =~ ^-([0-9]+|[0-9]*\.[0-9]+)$ ]]; then
                    arg_error "argument $option: expected one argument"
                fi
                value=$1; shift
            fi
            case $option in
                --cache-dir) cache_dir=$value;;
                --max-age-days) parse_integer "$option" "$value"; max_age=$integer;;
                --timeout) parse_integer "$option" "$value"; timeout=$integer;;
            esac ;;
        *)
            if [[ $token == -* && $token != - && ! $token =~ ^-([0-9]+|[0-9]*\.[0-9]+)$ ]]; then
                unknown+=("$token")
            elif ((positionals_closed)); then unknown+=("$token")
            else addresses+=("$token"); fi
            continue ;;
    esac
    ((${#addresses[@]} == 0)) || positionals_closed=1
done
((${#unknown[@]} == 0)) || arg_error "unrecognized arguments: ${unknown[*]}"
((!update || !offline)) || arg_error '--update and --offline cannot be combined'
# Path('') is '.', and Path strips redundant separators and '.' components.
cache_dir=$(printf '%s\n' "$cache_dir" | awk '
{p=$0; absolute=(substr(p,1,1)=="/"); n=split(p,a,"/"); out="";
 for(i=1;i<=n;i++) if(a[i]!="" && a[i]!=".") out=out (out==""?"":"/") a[i];
 print (absolute?"/":"") (out=="" && !absolute?".":out)}')
cache=${cache_dir%/}/ieee-mac-vendors.tsv
metadata=${cache_dir%/}/metadata.json
work_dir=$(mktemp -d "${TMPDIR:-/tmp}/mac-vendor.XXXXXXXX") || die 'Cannot create temporary directory.'

# A CSV state machine is necessary: IEEE names/addresses may contain commas,
# quotes, tabs and line breaks. Simple awk -F, or IFS splitting loses data.
cat > "$work_dir/engine.awk" <<'AWK' || die 'Cannot write temporary parser.'
function fail(s) {print "ERROR: " s > "/dev/stderr"; exit 1}
function trim(s) {
    sub("^(" ws ")+", "", s); sub("(" ws ")+$", "", s); return s
}
function record(sep,    line,status,i,c,n,value,quoted,started) {
    for(i in field) delete field[i]
    n=1; value=""; quoted=0; started=0
    while((status=(getline line < input)) > 0) {
        if(csv_mode) sub(/\r$/, "", line)
        if(csv_mode && !seen_line++) sub(/^\357\273\277/, "", line)
        if(!quoted && line ~ /^\r?$/) {if(reading_header) return 0; continue}
        started=1
        for(i=1;i<=length(line);i++) {
            c=substr(line,i,1)
            if(quoted) {
                if(c=="\"") {
                    if(substr(line,i+1,1)=="\"") {value=value "\""; i++}
                    else quoted=0
                } else value=value c
            } else if(c==sep) {field[n++]=value; value=""}
            else if(c=="\"" && value=="") quoted=1
            else if(c!="\r" || i!=length(line)) value=value c
        }
        if(!quoted) {field[n]=value; return n}
        # Python uses csv.DictReader(text.splitlines()) for downloads, which
        # discards physical line breaks even inside quoted CSV fields.
        if(!csv_mode) value=value "\n"
    }
    if(status<0) fail("Cannot read " input)
    if(started) {field[n]=value; return n}
    return 0
}
function headers(sep,    n,i) {
    for(i in header) delete header[i]
    reading_header=1
    n=record(sep)
    reading_header=0
    for(i=1;i<=n;i++) header[field[i]]=i
    return n
}
function get(name) {return (name in header) ? trim(field[header[name]]) : ""}
function alias(a,b,c) {
    if(a in header) return get(a)
    if(b in header) return get(b)
    return get(c)
}
function tsv(s) {
    if(s ~ /[\t\n\r"]/) {gsub(/"/, "\"\"", s); return "\"" s "\""}
    return s
}
function js(s,    out,i,c) {
    out="\""
    for(i=1;i<=length(s);i++) {
        c=substr(s,i,1)
        if(c=="\"") out=out "\\\""
        else if(c=="\\") out=out "\\\\"
        else if(c=="\b") out=out "\\b"
        else if(c=="\f") out=out "\\f"
        else if(c=="\n") out=out "\\n"
        else if(c=="\r") out=out "\\r"
        else if(c=="\t") out=out "\\t"
        else if(c in control) out=out sprintf("\\u%04x",control[c])
        else out=out c
    }
    return out "\""
}
function repr(s,    quote,out,i,c) {
    quote="'"; if(index(s,"'") && !index(s,"\"")) quote="\""
    out=quote
    for(i=1;i<=length(s);i++) {
        c=substr(s,i,1)
        if(c==quote || c=="\\") out=out "\\" c
        else if(c=="\n") out=out "\\n"
        else if(c=="\r") out=out "\\r"
        else if(c=="\t") out=out "\\t"
        else if(c in control || c==sprintf("%c",127)) out=out sprintf("\\x%02x",c in control?control[c]:127)
        else out=out c
    }
    return out quote
}
function less(a,b,    x,y) {
    x=rows[a,1]; y=rows[b,1]; if(("x" x)!=("x" y)) return ("x" x) < ("x" y)
    x=rows[a,2]+0; y=rows[b,2]+0; if(x!=y) return x>y
    x=rows[a,3]; y=rows[b,3]; if(x!=y) return x<y
    x=rows[a,4]; y=rows[b,4]; if(("x" x)!=("x" y)) return ("x" x)<("x" y)
    return a<b
}
function sort_rows(    width,left,mid,right,i,j,k,n) {
    for(i=1;i<=count;i++) order[i]=i
    for(width=1;width<count;width*=2) {
        for(left=1;left<=count;left+=2*width) {
            mid=left+width; right=left+2*width; if(right>count+1) right=count+1
            i=left; j=mid
            for(k=left;k<right;k++) {
                if(i<mid && i<=count && (j>=right || less(order[i],order[j]))) merged[k]=order[i++]
                else merged[k]=order[j++]
            }
        }
        for(i=1;i<=count;i++) order[i]=merged[i]
    }
    print "prefix\tbits\tregistry\torganization\taddress"
    for(i=1;i<=count;i++) {n=order[i]; print rows[n,1] "\t" rows[n,2] "\t" rows[n,3] "\t" tsv(rows[n,4]) "\t" tsv(rows[n,5])}
}
function lookup(query,    normalized,first,localbit,multi,b,p,key,found,out) {
    normalized=query; gsub(/[^0-9A-Fa-f]/,"",normalized); normalized=toupper(normalized)
    if(length(normalized)<6) fail("MAC address/prefix is too short: " repr(query))
    if(length(normalized)>12) fail("MAC address/prefix is too long: " repr(query))
    first=(index("0123456789ABCDEF",substr(normalized,1,1))-1)*16+index("0123456789ABCDEF",substr(normalized,2,1))-1
    localbit=int(first/2)%2; multi=first%2; found=0
    for(b=36;b>=24;b-=(b==36?8:4)) {
        if(length(normalized)<b/4) continue
        p=substr(normalized,1,b/4); key=b SUBSEP p
        if(key in org) {found=1; break}
    }
    if(ENVIRON["MV_JSON"]==1) {
        if(results++) print "  },"
        else print "["
        print "  {"
        if(ENVIRON["MV_QUIET"]==1) {
            print "    \"organization\": " (found?js(org[key]):"null")
            return
        }
        print "    \"query\": " js(query) ","
        print "    \"normalized\": " js(normalized) ","
        print "    \"prefix\": " (found?js(p):"null") ","
        print "    \"bits\": " (found?b:"null") ","
        print "    \"registry\": " (found?js(reg[key]):"null") ","
        print "    \"organization\": " (found?js(org[key]):"null") ","
        print "    \"address\": " (found?js(addr[key]):"null") ","
        print "    \"locally_administered\": " (localbit?"true":"false") ","
        print "    \"multicast\": " (multi?"true":"false")
    } else {
        results++
        if(ENVIRON["MV_QUIET"]==1) {print (found?org[key]:"Unknown"); return}
        if(found) {
            print query " -> " org[key] " [" reg[key] ", " p "/" b "]"
            if(ENVIRON["MV_ADDRESS"]==1 && addr[key]!="") print "  " addr[key]
        } else print query " -> Unknown"
        if(localbit) print "  Note: locally administered/randomized MAC; vendor lookup may be meaningless."
        if(multi) print "  Note: multicast/group MAC; vendor lookup may be meaningless."
    }
}
BEGIN {
    # Python str.strip whitespace, including its Unicode whitespace codepoints.
    ws="[ \t\r\n\v\f\034-\037]|\302\205|\302\240|\341\232\200|\342\200[\200-\212]|\342\200\250|\342\200\251|\342\200\257|\342\201\237|\343\200\200"
    for(i=0;i<32;i++) control[sprintf("%c",i)]=i
    mode=ENVIRON["MV_MODE"]; input=ENVIRON["MV_INPUT"]
    if(mode=="csv") {
        csv_mode=1; name=ENVIRON["MV_REGISTRY"]; bits=ENVIRON["MV_BITS"]+0
        if(!headers(",")) fail(name ": CSV has no header row.")
        while(record(",")) {
            p=get("Assignment"); gsub(/[^0-9A-Fa-f]/,"",p); p=toupper(p)
            o=alias("Organization Name","Organization","Company Name")
            a=alias("Organization Address","Address","")
            if(length(p)<bits/4 || o=="") continue
            print substr(p,1,bits/4) "\t" bits "\t" name "\t" tsv(o) "\t" tsv(a)
            count++
        }
        print count+0 > ENVIRON["MV_COUNT"]
        exit
    }
    if(mode=="sort") {
        while(record("\t")) {
            count++; for(i=1;i<=5;i++) rows[count,i]=field[i]
        }
        sort_rows(); exit
    }
    if(mode=="metadata") {
        print "{\n  \"tool\": \"mac-vendor.sh\",\n  \"tool_version\": \"1.0.0\","
        print "  \"updated_at\": " js(ENVIRON["MV_UPDATED"]) ","
        print "  \"registries\": ["
        split("MA-L MA-M MA-S IAB",names," "); split("24 28 36 36",sizes," ")
        split("oui/oui.csv oui28/mam.csv oui36/oui36.csv iab/iab.csv",paths," ")
        for(i=1;i<=4;i++) {
            print "    {\n      \"name\": " js(names[i]) ",\n      \"bits\": " sizes[i] ","
            print "      \"url\": " js("https://standards-oui.ieee.org/" paths[i]) "\n    }" (i<4?",":"")
        }
        print "  ],\n  \"record_count\": " ENVIRON["MV_COUNT"] "\n}"; exit
    }
    headers("\t")
    while(record("\t")) {
        p=toupper(get("prefix")); b=get("bits"); o=get("organization")
        if(b !~ /^[0-9]+$/ || (b+0!=24 && b+0!=28 && b+0!=36) || p=="" || o=="") continue
        key=(b+0) SUBSEP p
        if(!(key in org)) {org[key]=o; reg[key]=get("registry"); addr[key]=get("address")}
    }
    close(input); input=ENVIRON["MV_QUERIES"]
    while(record("\t")) {
        query=field[1]; if(ENVIRON["MV_STRIP"]==1) query=trim(query)
        if(ENVIRON["MV_STRIP"]==1 && query=="") continue
        lookup(query)
    }
    if(!results) exit 2
    if(ENVIRON["MV_JSON"]==1) print "  }\n]"
}
AWK

registry_names=(MA-L MA-M MA-S IAB)
registry_bits=(24 28 36 36)
registry_paths=(oui/oui.csv oui28/mam.csv oui36/oui36.csv iab/iab.csv)
fresh() {
    [[ -s $cache ]] || return 1
    local modified now timestamp
    timestamp=$(stat -L -c %y -- "$cache" 2>/dev/null)
    if [[ -n $timestamp ]]; then
        modified=$(date -d "$timestamp" +%s.%N) || return 1
    else
        modified=$(stat -L -f %m "$cache" 2>/dev/null) || return 1
    fi
    now=$(date +%s.%N)
    [[ $now != *N* ]] || now=$(date +%s)
    awk -v now="$now" -v modified="$modified" -v days="$max_age" 'BEGIN {exit !(now-modified <= days*86400)}'
}
update_cache() {
    local i url records total=0 seconds
    mkdir -p -- "$cache_dir" || die "Cannot create cache directory: $cache_dir"
    command -v curl >/dev/null 2>&1 || die 'curl is required to download IEEE registries.'
    seconds=$(awk -v t="$timeout" 'BEGIN {printf "%.0f",t}')
    [[ $seconds != -* && $seconds != 0 ]] || die 'Download timeout must be greater than zero.'
    update_dir=$(mktemp -d "${cache_dir%/}/.mac-vendor.XXXXXXXX") || die 'Cannot create cache temporary directory.'
    : > "$update_dir/records" || die 'Cannot write temporary registry data.'
    for i in 0 1 2 3; do
        url=https://standards-oui.ieee.org/${registry_paths[i]}
        ((quiet)) || printf 'Downloading %s: %s\n' "${registry_names[i]}" "$url" >&2
        # No retries or online vendor API fallback. Match urllib redirects and
        # proxy handling; curl reports HTTP errors and verifies HTTPS certificates.
        if ! curl --disable --fail --silent --show-error --location --max-redirs 10 \
            --connect-timeout "$seconds" --speed-time "$seconds" --speed-limit 1 \
            --user-agent "mac-vendor.sh/$VERSION" --output "$update_dir/download" \
            "$url" 2> "$work_dir/network-error"; then
            die "Could not download $url: $(cat "$work_dir/network-error")"
        fi
        MV_MODE=csv MV_INPUT="$update_dir/download" MV_REGISTRY="${registry_names[i]}" \
            MV_BITS="${registry_bits[i]}" MV_COUNT="$update_dir/count" \
            awk -f "$work_dir/engine.awk" >> "$update_dir/records" || exit 1
        read -r records < "$update_dir/count"
        ((total+=records))
        ((quiet)) || printf '  %s records\n' "$records" >&2
    done
    MV_MODE=sort MV_INPUT="$update_dir/records" awk -f "$work_dir/engine.awk" > "$update_dir/cache" || die 'Cannot build cache.'
    mv -f -- "$update_dir/cache" "$cache" || die "Cannot replace cache: $cache"
    chmod 644 -- "$cache" || die "Cannot set cache permissions: $cache"
    MV_MODE=metadata MV_UPDATED="$(date -u '+%Y-%m-%dT%H:%M:%S+00:00')" MV_COUNT="$total" \
        awk -f "$work_dir/engine.awk" > "$metadata" || die "Cannot write metadata: $metadata"
    ((quiet)) || printf 'Cache updated: %s\n' "$cache" >&2
    rm -rf -- "$update_dir"
    update_dir=
}
if ((update)); then
    update_cache
    if ((${#addresses[@]} == 0)) && [[ -t 0 ]]; then exit 0; fi
fi
if ((!offline)) && ! fresh; then update_cache; fi
[[ -s $cache ]] || die "Vendor cache does not exist or is empty: $cache"
[[ -r $cache ]] || die "Cannot read cache: $cache"
queries=$work_dir/queries
: > "$queries" || die 'Cannot write temporary query file.'
add_query() {
    local q=${1//\"/\"\"}
    printf '"%s"\n' "$q" >> "$queries" || die 'Cannot write temporary query file.'
}
strip=0
if ((${#addresses[@]})); then
    for query in "${addresses[@]}"; do add_query "$query"; done
else
    strip=1
    if [[ -t 0 ]]; then
        printf 'MAC address or prefix: '
        IFS= read -r query || die 'End of input.'
        add_query "$query"
    else
        while IFS= read -r query || [[ -n $query ]]; do add_query "$query"; done
    fi
fi
# Buffer output: the Python list comprehension validates every query before
# printing anything, even when a bad query follows a valid one.
MV_MODE=lookup MV_INPUT="$cache" MV_QUERIES="$queries" MV_STRIP="$strip" \
    MV_JSON="$json" MV_QUIET="$quiet" MV_ADDRESS="$show_address" \
    awk -f "$work_dir/engine.awk" > "$work_dir/results"
status=$?
if ((status == 2)); then usage >&2; exit 2; fi
((status == 0)) || exit "$status"
cat "$work_dir/results"
