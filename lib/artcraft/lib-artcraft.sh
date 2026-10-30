#!/bin/bash
# Source this library from ride.sh or Bash. Downloads never install the apps.
ARTCRAFT_REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"

CheckArtCraftDownloads(){
  python3 "${ARTCRAFT_REPO_ROOT}/tools/download-artcraft.py" discover \
    --catalog "${SCRIPT_DOWNLOADDIR:-${DOWNLOADDIR:-/tmp}}/artcraft-catalog.json" \
    --arch "${ARTCRAFT_ARCH:-all}"
}

GetArtCraft(){
  local destination="${ARTCRAFT_DOWNLOADDIR:-${SCRIPT_DOWNLOADDIR:-${DOWNLOADDIR:-/tmp}}/artcraft-linux}"
  python3 "${ARTCRAFT_REPO_ROOT}/tools/download-artcraft.py" all \
    --catalog "${destination}/catalog.json" --destination "$destination" \
    --arch "${ARTCRAFT_ARCH:-all}"
}

GetArtCraftDependencies(){
  local destination="${ARTCRAFT_DOWNLOADDIR:-${SCRIPT_DOWNLOADDIR:-${DOWNLOADDIR:-/tmp}}/artcraft-linux}"
  bash "${ARTCRAFT_REPO_ROOT}/lib/artcraft/download-dependencies.sh" \
    "$destination" "${ARTCRAFT_FEDORA_RELEASE:-$(rpm -E %fedora)}" \
    "${ARTCRAFT_DEPENDENCY_ARCH:-$(uname -m)}"
}
