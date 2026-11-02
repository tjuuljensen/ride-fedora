#!/usr/bin/env bash
# Purpose: Manage opt-in user Bash aliases through exact owned blocks.
# Behavior: Preserve unrelated shell configuration and refuse edited RIDE blocks.
# Compatibility: Bash 5 on the Fedora 44 Workstation x86_64 user target.
# Usage: Sourced by ride.sh; catalog JSON is validated as data.
# Inputs: A bounded JSON array of declared alias IDs.
# Side effects: Edits marked blocks in ~/.bashrc and ~/.bash_aliases.
# Prerequisites: Bash, jq, awk, sha256sum, and eza when ls-eza is selected.
# Ownership: User-level shell configuration; no system files or arbitrary shell values.
# Provenance: Eza upstream and ipify public address API documentation.
# Version: 3.0.0

ride_bash_aliases_rc() { printf '%s/.bashrc\n' "$HOME"; }
ride_bash_aliases_file() { printf '%s/.bash_aliases\n' "$HOME"; }
ride_bash_aliases_owner() {
  printf '%s/ride-fedora/owned/setting.bash-aliases.json\n' "${XDG_STATE_HOME:-$HOME/.local/state}"
}

ride_bash_aliases_include_block() {
  cat <<'EOF'
# >>> RIDE managed Bash aliases loader >>>
if [ -f "$HOME/.bash_aliases" ]; then
    . "$HOME/.bash_aliases"
fi
# <<< RIDE managed Bash aliases loader <<<
EOF
}

ride_bash_aliases_content() {
  local entry=$1 aliases alias_id
  aliases=$(jq -r '.selectedValue' <<< "$entry")
  printf '%s\n' '# >>> RIDE managed Bash aliases >>>'
  while IFS= read -r alias_id; do
    case "$alias_id" in
      ls-eza) printf '%s\n' "alias ls='eza'" ;;
      wanip) printf '%s\n' "alias wanip='curl --fail --silent --show-error --location --proto =https --tlsv1.2 --max-time 10 https://api64.ipify.org'" ;;
      wanip4) printf '%s\n' "alias wanip4='curl --fail --silent --show-error --location --proto =https --tlsv1.2 --max-time 10 https://api.ipify.org'" ;;
      wanip6) printf '%s\n' "alias wanip6='curl --fail --silent --show-error --location --proto =https --tlsv1.2 --max-time 10 https://api6.ipify.org'" ;;
      *) ride_die "unknown Bash alias ID: $alias_id" ;;
    esac
  done < <(jq -r '.[]' <<< "$aliases")
  printf '%s\n' '# <<< RIDE managed Bash aliases <<<'
}

ride_bash_aliases_extract_block() {
  local file=$1 begin=$2 end=$3
  awk -v begin="$begin" -v end="$end" '
    $0 == begin { if (inside || found) exit 2; inside=1; found++; print; next }
    $0 == end { if (!inside) exit 2; inside=0; print; next }
    inside { print }
    END { if (inside || found != 1) exit 2 }
  ' "$file"
}

ride_bash_aliases_insert_block_impl() {
  local file=$1 block=$2 mode=600 temporary
  [[ ! -L "$file" ]] || ride_die "Bash alias target is a symlink: $file"
  if [[ -e "$file" ]]; then
    [[ -f "$file" ]] || ride_die "Bash alias target is not a regular file: $file"
    mode=$(stat -c '%a' -- "$file") || return 1
    temporary=$(mktemp "${file%/*}/.ride-bash-aliases.XXXXXXXX") || return 1
    cat -- "$file" > "$temporary" || { rm -f -- "$temporary"; return 1; }
    [[ ! -s "$temporary" || "$(tail -c 1 -- "$temporary" | wc -l)" -gt 0 ]] || printf '\n' >> "$temporary"
  else
    temporary=$(mktemp "${file%/*}/.ride-bash-aliases.XXXXXXXX") || return 1
  fi
  printf '%s\n' "$block" >> "$temporary" || { rm -f -- "$temporary"; return 1; }
  chmod "$mode" -- "$temporary" || { rm -f -- "$temporary"; return 1; }
  mv -fT -- "$temporary" "$file" || { rm -f -- "$temporary"; return 1; }
}

ride_bash_aliases_insert_block() {
  ride_bash_aliases_insert_block_impl "$@"
}

ride_bash_aliases_remove_block() {
  local file=$1 expected=$2 begin=$3 end=$4 mode temporary extracted
  [[ -f "$file" && ! -L "$file" ]] || ride_die "Bash alias file is missing or unsafe: $file"
  extracted=$(ride_bash_aliases_extract_block "$file" "$begin" "$end") ||
    ride_die "Bash alias ownership markers are missing, duplicated, or malformed: $file"
  [[ "$extracted" == "$expected" ]] || ride_die "RIDE Bash alias block changed outside RIDE; preserving it: $file"
  mode=$(stat -c '%a' -- "$file") || return 1
  temporary=$(mktemp "${file%/*}/.ride-bash-aliases.XXXXXXXX") || return 1
  awk -v begin="$begin" -v end="$end" '
    $0 == begin { if (inside || found) exit 2; inside=1; found++; next }
    $0 == end { if (!inside) exit 2; inside=0; next }
    !inside { print }
    END { if (inside || found != 1) exit 2 }
  ' "$file" > "$temporary" || { rm -f -- "$temporary"; ride_die "cannot remove owned Bash alias block"; }
  chmod "$mode" -- "$temporary" || { rm -f -- "$temporary"; return 1; }
  mv -fT -- "$temporary" "$file" || { rm -f -- "$temporary"; return 1; }
}

ride_bash_aliases_validate_owner() {
  local entry=$1 owner aliases config_hash expected loader_owned alias_file_created rc_created
  local expected_alias_block expected_loader_block actual
  owner=$(ride_bash_aliases_owner)
  [[ -f "$owner" && ! -L "$owner" && -O "$owner" && "$(stat -c '%a' -- "$owner")" == 600 ]] ||
    ride_die "Bash alias ownership record is missing or unsafe"
  jq -e '.schemaVersion == 1 and (.loaderOwned | type == "boolean") and
    (.aliasFileCreated | type == "boolean") and (.bashrcCreated | type == "boolean") and
    (.configSha256 | type == "string" and test("^[0-9a-f]{64}$"))' "$owner" >/dev/null ||
    ride_die "invalid Bash alias ownership record"
  aliases=$(jq -r '.selectedValue // empty' <<< "$entry")
  if [[ -z "$aliases" ]]; then
    aliases=$(jq -c '.aliases' "$owner")
    entry=$(jq -c --arg aliases "$aliases" '. + {selectedValue:$aliases}' <<< "$entry")
  fi
  config_hash=$(jq -cS . <<< "$aliases" | sha256sum); config_hash=${config_hash%% *}
  expected=$(jq -r '.configSha256' "$owner")
  [[ "$config_hash" == "$expected" && "$(jq -c '.aliases' "$owner")" == "$(jq -c . <<< "$aliases")" ]] ||
    ride_die "Bash alias configuration changed; remove the existing profile before changing aliases"
  expected_alias_block=$(ride_bash_aliases_content "$entry")
  if [[ -e "$(ride_bash_aliases_file)" ]]; then
    actual=$(ride_bash_aliases_extract_block "$(ride_bash_aliases_file)" \
      '# >>> RIDE managed Bash aliases >>>' '# <<< RIDE managed Bash aliases <<<') ||
      ride_die "Bash alias ownership markers are missing, duplicated, or malformed"
    [[ "$actual" == "$expected_alias_block" ]] || ride_die "RIDE Bash alias block changed outside RIDE; preserving it"
  else
    ride_die "Bash alias file is missing"
  fi
  loader_owned=$(jq -r '.loaderOwned' "$owner")
  if [[ "$loader_owned" == true ]]; then
    expected_loader_block=$(ride_bash_aliases_include_block)
    actual=$(ride_bash_aliases_extract_block "$(ride_bash_aliases_rc)" \
      '# >>> RIDE managed Bash aliases loader >>>' '# <<< RIDE managed Bash aliases loader <<<') ||
      ride_die "Bash alias loader markers are missing, duplicated, or malformed"
    [[ "$actual" == "$expected_loader_block" ]] || ride_die "RIDE Bash alias loader changed outside RIDE; preserving it"
  fi
  alias_file_created=$(jq -r '.aliasFileCreated' "$owner")
  rc_created=$(jq -r '.bashrcCreated' "$owner")
  [[ "$alias_file_created" == true || -f "$(ride_bash_aliases_file)" ]] || ride_die "Bash alias file is missing"
  [[ "$rc_created" == true || -f "$(ride_bash_aliases_rc)" ]] || ride_die "Bash rc file is missing"
}

ride_bash_aliases_observe() {
  local entry=$1 owner
  owner=$(ride_bash_aliases_owner)
  if [[ -e "$owner" || -L "$owner" ]]; then
    [[ ! -L "$owner" ]] || ride_die "Bash alias ownership record is a symlink"
    ride_bash_aliases_validate_owner "$entry"
    printf 'configured\n'
    return 0
  fi
  if [[ -f "$(ride_bash_aliases_rc)" ]] && grep -Fq '# >>> RIDE managed Bash aliases loader >>>' "$(ride_bash_aliases_rc)"; then
    ride_die "unowned RIDE Bash alias loader markers exist"
  fi
  if [[ -f "$(ride_bash_aliases_file)" ]] && grep -Fq '# >>> RIDE managed Bash aliases >>>' "$(ride_bash_aliases_file)"; then
    ride_die "unowned RIDE Bash alias markers exist"
  fi
  printf 'absent\n'
}

ride_bash_aliases_change() {
  local entry=$1 state=$2 owner aliases config_hash alias_file rc_file alias_block loader_block
  local loader_owned=false alias_file_created=false bashrc_created=false temporary
  owner=$(ride_bash_aliases_owner)
  alias_file=$(ride_bash_aliases_file)
  rc_file=$(ride_bash_aliases_rc)
  case "$state" in
    configured)
      if [[ -e "$owner" || -L "$owner" ]]; then
        ride_bash_aliases_validate_owner "$entry"
        return 0
      fi
      aliases=$(jq -r '.selectedValue' <<< "$entry")
      if jq -e 'index("ls-eza") != null' <<< "$aliases" >/dev/null; then
        command -v eza >/dev/null 2>&1 || ride_die "the ls-eza alias requires the eza command"
      fi
      for file in "$HOME" "$HOME/.config" "${XDG_STATE_HOME:-$HOME/.local/state}" \
        "${XDG_STATE_HOME:-$HOME/.local/state}/ride-fedora" \
        "${XDG_STATE_HOME:-$HOME/.local/state}/ride-fedora/owned"; do
        [[ ! -L "$file" ]] || ride_die "Bash alias parent path is a symlink: $file"
      done
      [[ ! -L "$alias_file" && ! -L "$rc_file" && ! -L "$owner" ]] || ride_die "Bash alias destination is a symlink"
      [[ ! -e "$owner" ]] || ride_die "Bash alias ownership record already exists"
      if [[ -e "$alias_file" ]]; then
        [[ -f "$alias_file" ]] || ride_die "Bash alias target is not a regular file"
      else
        alias_file_created=true
      fi
      if [[ -e "$rc_file" ]]; then
        [[ -f "$rc_file" ]] || ride_die "Bash rc target is not a regular file"
      else
        bashrc_created=true
      fi
      while IFS= read -r alias_id; do
        local name
        case "$alias_id" in ls-eza) name='ls' ;; wanip*) name="$alias_id" ;; esac
        if [[ -n "$name" ]] && { grep -Eq "^[[:space:]]*(alias[[:space:]]+${name}=|function[[:space:]]+${name}([[:space:]]|\()|${name}[[:space:]]*\\(\\))" "$alias_file" "$rc_file" 2>/dev/null; }; then
          ride_die "Bash alias name already has an unowned definition: $name"
        fi
      done < <(jq -r '.[]' <<< "$aliases")
      if [[ -e "$rc_file" ]] && grep -Eq '(^|[;&|[:space:]])(\.|source)[[:space:]].*\.bash_aliases' "$rc_file"; then
        loader_owned=false
      else
        loader_owned=true
      fi
      alias_block=$(ride_bash_aliases_content "$entry")
      loader_block=$(ride_bash_aliases_include_block)
      mkdir -p -- "${owner%/*}" || ride_die "cannot create Bash alias ownership directory"
      if ! ride_bash_aliases_insert_block "$alias_file" "$alias_block"; then
        ride_die "cannot add owned aliases to $alias_file"
      fi
      if [[ "$loader_owned" == true ]] && ! ride_bash_aliases_insert_block "$rc_file" "$loader_block"; then
        ride_bash_aliases_remove_block "$alias_file" "$alias_block" '# >>> RIDE managed Bash aliases >>>' '# <<< RIDE managed Bash aliases <<<' || true
        ride_die "cannot add owned Bash alias loader to $rc_file"
      fi
      config_hash=$(jq -cS . <<< "$aliases" | sha256sum); config_hash=${config_hash%% *}
      temporary=$(mktemp "${owner%/*}/.bash-aliases.XXXXXXXX") || ride_die "cannot stage Bash alias ownership record"
      jq -n --arg hash "$config_hash" --argjson aliases "$aliases" \
        --argjson loaderOwned "$loader_owned" --argjson aliasFileCreated "$alias_file_created" \
        --argjson bashrcCreated "$bashrc_created" \
        '{schemaVersion:1,configSha256:$hash,aliases:$aliases,loaderOwned:$loaderOwned,aliasFileCreated:$aliasFileCreated,bashrcCreated:$bashrcCreated}' > "$temporary" || {
          rm -f -- "$temporary"
          ride_bash_aliases_remove_block "$alias_file" "$alias_block" '# >>> RIDE managed Bash aliases >>>' '# <<< RIDE managed Bash aliases <<<' || true
          [[ "$loader_owned" != true ]] || ride_bash_aliases_remove_block "$rc_file" "$loader_block" '# >>> RIDE managed Bash aliases loader >>>' '# <<< RIDE managed Bash aliases loader <<<' || true
          ride_die "cannot serialize Bash alias ownership record"
        }
      chmod 0600 -- "$temporary" && ln -T -- "$temporary" "$owner" || {
        rm -f -- "$temporary"
        ride_bash_aliases_remove_block "$alias_file" "$alias_block" '# >>> RIDE managed Bash aliases >>>' '# <<< RIDE managed Bash aliases <<<' || true
        [[ "$loader_owned" != true ]] || ride_bash_aliases_remove_block "$rc_file" "$loader_block" '# >>> RIDE managed Bash aliases loader >>>' '# <<< RIDE managed Bash aliases loader <<<' || true
        ride_die "cannot install Bash alias ownership record"
      }
      rm -f -- "$temporary"
      ;;
    absent)
      [[ -e "$owner" && ! -L "$owner" ]] || return 0
      ride_bash_aliases_validate_owner "$entry"
      aliases=$(jq -r '.selectedValue // empty' <<< "$entry")
      [[ -n "$aliases" ]] || aliases=$(jq -c '.aliases' "$owner")
      entry=$(jq -c --arg aliases "$aliases" '. + {selectedValue:$aliases}' <<< "$entry")
      alias_block=$(ride_bash_aliases_content "$entry")
      loader_block=$(ride_bash_aliases_include_block)
      ride_bash_aliases_remove_block "$alias_file" "$alias_block" '# >>> RIDE managed Bash aliases >>>' '# <<< RIDE managed Bash aliases <<<'
      if [[ "$(jq -r '.loaderOwned' "$owner")" == true ]]; then
        ride_bash_aliases_remove_block "$rc_file" "$loader_block" '# >>> RIDE managed Bash aliases loader >>>' '# <<< RIDE managed Bash aliases loader <<<'
      fi
      if [[ "$(jq -r '.aliasFileCreated' "$owner")" == true && ! -s "$alias_file" ]]; then rm -f -- "$alias_file"; fi
      if [[ "$(jq -r '.bashrcCreated' "$owner")" == true && ! -s "$rc_file" ]]; then rm -f -- "$rc_file"; fi
      rm -f -- "$owner" || ride_die "cannot remove Bash alias ownership record"
      ;;
    *) ride_die "invalid Bash aliases state: $state" ;;
  esac
}
