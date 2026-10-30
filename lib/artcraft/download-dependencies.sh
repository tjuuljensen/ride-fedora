#!/bin/bash
# Download a Fedora dependency closure and portable Flatpak runtime bundles.
# All package data is staged on a Linux filesystem. No ArtCraft app is installed
# or executed. Requirements: Fedora, root for DNF, python3, flatpak, ostree.
set -euo pipefail

archive=$(realpath -- "${1:?Usage: download-dependencies.sh ARCHIVE FEDORA_RELEASE ARCH}")
release=${2:?Specify the target Fedora release}
arch=${3:-x86_64}
[[ $release =~ ^[0-9]+$ ]] || { echo 'Invalid Fedora release' >&2; exit 2; }
[[ $arch == x86_64 || $arch == aarch64 ]] || { echo 'Unsupported architecture' >&2; exit 2; }
[[ $EUID == 0 ]] || { echo 'Run as root; DNF uses an empty temporary installroot.' >&2; exit 2; }
for command in python3 dnf flatpak ostree rpmkeys; do command -v "$command" >/dev/null; done
stage=$(mktemp -d /var/tmp/ride-artcraft.XXXXXXXX)
echo "Dependency staging: $stage"
cleanup(){
  if [[ ${ARTCRAFT_KEEP_STAGE:-0} == 1 ]]; then return; fi
  # Only remove the exact directory allocated by mktemp, within /var/tmp.
  local resolved
  resolved=$(realpath -- "$stage")
  [[ $resolved == /var/tmp/ride-artcraft.* && $resolved != /var/tmp ]] || return
  rm -rf -- "$resolved"
}
trap cleanup EXIT
output="$stage/output"
mkdir -p "$output/rpm" "$output/flatpak" "$stage/repos" "$stage/root/etc/pki/rpm-gpg"
cp /etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-* "$stage/root/etc/pki/rpm-gpg/"
key="/etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-${release}-${arch}"
[[ -f $key ]] || { echo "Missing Fedora signing key: $key" >&2; exit 1; }
cat > "$stage/repos/fedora.repo" <<EOF
[fedora]
name=Fedora $release
metalink=https://mirrors.fedoraproject.org/metalink?repo=fedora-$release&arch=$arch
enabled=1
gpgcheck=1
gpgkey=file://$key
[updates]
name=Fedora $release Updates
metalink=https://mirrors.fedoraproject.org/metalink?repo=updates-released-f$release&arch=$arch
enabled=1
gpgcheck=1
gpgkey=file://$key
EOF

# Check the downloaded bytes again before letting package tools read metadata.
python3 - "$archive" "$stage" "$arch" <<'PY'
import hashlib, json, pathlib, sys
archive, stage = map(pathlib.Path, sys.argv[1:3])
arch = sys.argv[3]
report = json.loads((archive / 'download-report.json').read_text())
paths = {'rpm': [], 'flatpak': []}
for entry in report['files']:
    if entry['status'] == 'error':
        raise SystemExit('Download report contains errors')
    if entry['format'] not in paths or entry['architecture'] not in (arch, 'unspecified'):
        continue
    path = (archive / entry['path']).resolve()
    if not path.is_relative_to(archive):
        raise SystemExit('Unsafe archive path')
    with path.open('rb') as source:
        digest = hashlib.file_digest(source, 'sha256').hexdigest()
    if digest != entry['sha256']:
        raise SystemExit(f'Checksum mismatch: {path}')
    paths[entry['format']].append(str(path))
for fmt, entries in paths.items():
    (stage / (fmt + '.list')).write_bytes(b''.join(p.encode() + b'\0' for p in entries))
if not paths['rpm'] or not paths['flatpak']:
    raise SystemExit('No matching RPM/Flatpak installers in archive')
PY
mapfile -d '' -t rpms < "$stage/rpm.list"
mapfile -d '' -t bundles < "$stage/flatpak.list"

# A fresh RPM database prevents the resolver from omitting packages installed on
# this staging machine. --downloadonly never performs an installation.
dnf --installroot="$stage/root" --releasever="$release" --forcearch="$arch" \
  --setopt="reposdir=$stage/repos" --setopt=install_weak_deps=True \
  --setopt=keepcache=True -y install --downloadonly \
  "${rpms[@]}" fuse fuse-libs mesa-dri-drivers vulkan-loader flatpak
mapfile -d '' -t dependencies < <(find "$stage/root" -type f -name '*.rpm' -print0)
[[ ${#dependencies[@]} -gt 0 ]] || { echo 'DNF did not cache dependency RPMs' >&2; exit 1; }
cp -- "${dependencies[@]}" "$output/rpm/"
rpmkeys --root "$stage/root" --import "$key"
rpmkeys --root "$stage/root" --checksig "${dependencies[@]}" > "$output/rpm-signatures.txt"

# Import application bundles solely to inspect their runtime metadata. They
# are never deployed. Cache runtimes in a separate, disposable Flatpak repo.
export FLATPAK_USER_DIR="$stage/flatpak-user"
export FLATPAK_SYSTEM_DIR="$stage/flatpak-system"
export XDG_DATA_HOME="$stage/data"
export XDG_CACHE_HOME="$stage/cache"
export XDG_CONFIG_HOME="$stage/config"
ostree --repo="$stage/import" init --mode=archive-z2
for bundle in "${bundles[@]}"; do
  flatpak build-import-bundle "$stage/import" "$bundle"
done
while IFS= read -r ref; do
  [[ $ref == app/* ]] || continue
  ostree --repo="$stage/import" cat "$ref" /metadata
done < <(ostree --repo="$stage/import" refs) > "$output/application-metadata.ini"
mapfile -t runtimes < <(sed -n 's/^runtime=//p' "$output/application-metadata.ini" | sort -u)
[[ ${#runtimes[@]} -gt 0 ]] || { echo 'No runtime metadata found' >&2; exit 1; }
flatpak --user remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak --user config --set languages '*'
for runtime in "${runtimes[@]}"; do
  flatpak --user install --assumeyes --noninteractive --no-deploy flathub "runtime/$runtime"
done
ostree --repo="$FLATPAK_USER_DIR/repo" refs | sort > "$output/flatpak-refs.txt"
pids=()
wait_exports(){
  local pid failed=0
  for pid in "${pids[@]}"; do wait "$pid" || failed=1; done
  pids=()
  [[ $failed == 0 ]] || { echo 'Runtime bundle export failed' >&2; exit 1; }
}
while IFS= read -r remote_ref; do
  ref=${remote_ref#*:}
  [[ $ref == runtime/* ]] || continue
  IFS=/ read -r kind id ref_arch branch <<< "$ref"
  # build-bundle uses local refs; alias the verified, downloaded remote commit.
  ostree --repo="$FLATPAK_USER_DIR/repo" refs --force --create="$ref" "$remote_ref"
  bundle="$output/flatpak/${id}-${ref_arch}-${branch}.flatpak"
  [[ -f $bundle ]] && continue
  flatpak build-bundle --runtime --arch="$ref_arch" \
    "$FLATPAK_USER_DIR/repo" "$bundle" "$id" "$branch" &
  pids+=("$!")
  if [[ ${#pids[@]} == 4 ]]; then wait_exports; fi
done < "$output/flatpak-refs.txt"
wait_exports

# Keep dependency output separate from the installers and hash every byte.
destination="$archive/dependencies/fedora-$release-$arch"
mkdir -p "$destination"
cp -a "$output/." "$destination/"
python3 - "$archive" "$destination" "$release" "$arch" <<'PY'
import datetime, hashlib, json, pathlib, sys
archive, dest = map(pathlib.Path, sys.argv[1:3])
files = []
for path in sorted(dest.rglob('*')):
    if not path.is_file() or path.name in ('dependency-report.json', 'SHA256SUMS'):
        continue
    with path.open('rb') as source:
        digest = hashlib.file_digest(source, 'sha256').hexdigest()
    files.append({'path': path.relative_to(dest).as_posix(), 'sha256': digest, 'size': path.stat().st_size})
report = {'schema_version': 1, 'status': 'complete', 'fedora_release': sys.argv[3],
          'architecture': sys.argv[4], 'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'scope': 'RPM dependency closure including weak dependencies; AppImage host support; Flatpak runtimes and selected related extensions. GPU-specific proprietary drivers depend on target hardware.',
          'files': files}
(dest / 'dependency-report.json').write_text(json.dumps(report, indent=2) + '\n')
(dest / 'SHA256SUMS').write_text(''.join(f"{e['sha256']}  {e['path']}\n" for e in files))
path = archive / 'download-report.json'
downloads = json.loads(path.read_text())
downloads['dependencies'] = {'status': 'complete', 'report': (dest / 'dependency-report.json').relative_to(archive).as_posix()}
path.write_text(json.dumps(downloads, indent=2) + '\n')
print(f'Archived {len(files)} dependency files ({sum(e["size"] for e in files):,} bytes)')
PY
