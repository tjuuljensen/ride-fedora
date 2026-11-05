#!/usr/bin/env bash
# Purpose: Capture travel readiness and prepare an offline Python test environment.
# Behavior: Reports Git/disk/tool state, creates a pip wheelhouse, verifies an
#          offline venv install, or writes a source/catalog checksum manifest.
# Compatibility: Bash 4+; Fedora/Linux development host.
# Usage: tools/travel-preflight.sh {report|wheelhouse|verify-wheelhouse|manifest} [OUTPUT_DIR]
# Inputs: Repository checkout and tests/acceptance/requirements.txt.
# Side effects: Writes only beneath OUTPUT_DIR (default .acceptance-runs/travel-prep).
# Prerequisites: Git, Python 3, pip; wheelhouse requires network access.
# Owner: RIDE Fedora maintainers.
# Provenance: New RIDE travel preparation helper.
# Version: 1.0.0

set -euo pipefail

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
OUTPUT_DIR=${2:-"$ROOT/.acceptance-runs/travel-prep"}
MODE=${1:-report}

mkdir -p "$OUTPUT_DIR"
chmod 700 "$OUTPUT_DIR"

case "$MODE" in
  report)
    stamp=$(date -u +%Y%m%dT%H%M%SZ)
    report="$OUTPUT_DIR/preflight-$stamp.txt"
    patch_file="$OUTPUT_DIR/worktree-diff-$stamp.patch"
    git -C "$ROOT" diff --binary > "$patch_file"
    {
      printf 'RIDE travel preflight\nUTC: %s\nRoot: %s\n\n' "$stamp" "$ROOT"
      printf '%s\n' '== Git =='
      git -C "$ROOT" status --short --branch
      printf 'HEAD: '
      git -C "$ROOT" rev-parse HEAD
      printf 'Upstream: '
      git -C "$ROOT" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || printf 'not configured\n'
      printf '\n%s\n' '== Diff summary =='
      git -C "$ROOT" diff --stat
      printf 'Full tracked diff: %s\n' "$patch_file"
      printf '\n%s\n' '== Filesystem =='
      df -h "$OUTPUT_DIR"
      findmnt -T "$OUTPUT_DIR" -o TARGET,FSTYPE,SIZE,AVAIL
      printf '\n%s\n' '== Host tools =='
      for tool in bash python3 pip qemu-system-x86_64 qemu-img genisoimage isoinfo xorriso virt-cat ssh scp ssh-keygen jq git; do
        if path=$(command -v "$tool" 2>/dev/null); then printf '%s\t%s\n' "$tool" "$path"; else printf '%s\tMISSING\n' "$tool"; fi
      done
      printf '\n%s\n' '== Acceleration =='
      if [[ -c /dev/kvm && -r /dev/kvm && -w /dev/kvm ]]; then printf 'KVM: accessible\n'; else printf 'KVM: unavailable; use TCG (slower)\n'; fi
      printf '\n%s\n' '== Python acceptance dependencies =='
      python3 -m pip --version
      python3 -m pip show pytest 2>/dev/null || printf 'pytest: not installed in system Python\n'
      if [[ -x "$ROOT/.acceptance-runs/venv/bin/python" ]]; then "$ROOT/.acceptance-runs/venv/bin/python" -m pip show pytest || true; else printf 'repository acceptance venv: not present\n'; fi
    } | tee "$report"
    printf '\nReport saved: %s\n' "$report"
    ;;
  wheelhouse)
    mkdir -p "$OUTPUT_DIR/wheelhouse"
    python3 -m pip download --only-binary=:all: \
      --dest "$OUTPUT_DIR/wheelhouse" \
      -r "$ROOT/tests/acceptance/requirements.txt"
    sha256sum "$ROOT/tests/acceptance/requirements.txt" "$OUTPUT_DIR"/wheelhouse/* \
      > "$OUTPUT_DIR/wheelhouse.sha256"
    printf 'Wheelhouse and hashes: %s\n' "$OUTPUT_DIR"
    ;;
  verify-wheelhouse)
    [[ -f "$OUTPUT_DIR/wheelhouse.sha256" ]] || { printf 'Missing %s/wheelhouse.sha256\n' "$OUTPUT_DIR" >&2; exit 2; }
    (cd "$ROOT" && sha256sum --check "$OUTPUT_DIR/wheelhouse.sha256")
    python3 -m venv "$OUTPUT_DIR/venv-offline-check"
    PIP_NO_INDEX=1 "$OUTPUT_DIR/venv-offline-check/bin/python" -m pip install \
      --no-index --find-links "$OUTPUT_DIR/wheelhouse" \
      -r "$ROOT/tests/acceptance/requirements.txt"
    "$OUTPUT_DIR/venv-offline-check/bin/python" -m pytest --version
    ;;
  manifest)
    {
      printf 'source_revision\t'
      git -C "$ROOT" rev-parse HEAD
      printf 'tracked_diff_sha256\t'
      git -C "$ROOT" diff --binary | sha256sum | cut -d ' ' -f1
      printf 'untracked_files_manifest_sha256\t'
      while IFS= read -r -d '' file; do sha256sum "$ROOT/$file"; done \
        < <(git -C "$ROOT" ls-files --others --exclude-standard -z) \
        | LC_ALL=C sort | sha256sum | cut -d ' ' -f1
      printf 'catalog_sha256\t'
      sha256sum "$ROOT/catalog/operations.json" | cut -d ' ' -f1
      printf 'acceptance_requirements_sha256\t'
      sha256sum "$ROOT/tests/acceptance/requirements.txt" | cut -d ' ' -f1
      printf 'created_utc\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    } | tee "$OUTPUT_DIR/source-manifest.tsv"
    ;;
  *)
    printf 'Usage: %s {report|wheelhouse|verify-wheelhouse|manifest} [OUTPUT_DIR]\n' "$0" >&2
    exit 2
    ;;
esac
