# Bash completion for a checkout of RIDE Linux v3. Source this file in Bash.
_ride_complete() {
  local current previous command root catalog token id state_dir
  local -a words candidates
  COMPREPLY=()
  current=${COMP_WORDS[COMP_CWORD]}
  previous=${COMP_WORDS[COMP_CWORD-1]:-}
  root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd) || return
  catalog=${RIDE_CATALOG_PATH:-$root/catalog/operations.json}
  [[ -r "$catalog" ]] && command -v jq >/dev/null 2>&1 || return
  if (( COMP_CWORD == 1 )); then
    candidates=(list search show plan apply download install set unset status restore remove completion help version)
    COMPREPLY=($(compgen -W "${candidates[*]}" -- "$current"))
    return
  fi
  command=${COMP_WORDS[1]}
  case "$previous" in
    --profile)
      for token in "$root"/profiles/*.json; do
        [[ -f "$token" ]] && words+=("${token##*/}")
      done
      words=("${words[@]%.json}")
      COMPREPLY=($(compgen -W "${words[*]}" -- "$current"))
      return ;;
    --run-id)
      if (( EUID == 0 )); then
        state_dir=/var/lib/ride-fedora/runs
      elif [[ -n "${RIDE_STATE_DIR:-}" ]]; then
        state_dir=$RIDE_STATE_DIR
      else
        state_dir=${XDG_STATE_HOME:-$HOME/.local/state}/ride-fedora/runs
      fi
      for token in "$state_dir"/*.json; do
        [[ -f "$token" ]] && words+=("${token##*/}")
      done
      words=("${words[@]%.json}")
      COMPREPLY=($(compgen -W "${words[*]}" -- "$current"))
      return ;;
    --state)
      id=
      for token in "${COMP_WORDS[@]:2:COMP_CWORD-2}"; do
        [[ "$token" == setting.* ]] && id=$token
      done
      [[ -n "$id" ]] || return
      mapfile -t words < <(jq -r --arg id "$id" '.operations[] | select(.id == $id) | .states[]' "$catalog")
      COMPREPLY=($(compgen -W "${words[*]}" -- "$current"))
      return ;;
    --source)
      id=
      for token in "${COMP_WORDS[@]:2:COMP_CWORD-2}"; do
        [[ "$token" == package.* ]] && id=$token
      done
      [[ -n "$id" ]] || return
      mapfile -t words < <(jq -r --arg id "$id" '.operations[] | select(.id == $id and .kind == "package") | .sourceId, .sourceProviders[]?.sourceId' "$catalog")
      COMPREPLY=($(compgen -W "${words[*]}" -- "$current"))
      return ;;
  esac
  case "$command" in
    show|install|set|unset|download|remove|status)
      mapfile -t words < <(jq -r '.operations[].id' "$catalog")
      COMPREPLY=($(compgen -W "${words[*]}" -- "$current")) ;;
    list)
      COMPREPLY=($(compgen -W 'all packages artifacts settings profiles groups' -- "$current")) ;;
    completion)
      COMPREPLY=($(compgen -W bash -- "$current")) ;;
    *)
      COMPREPLY=($(compgen -W '--profile --dry-run --allow-candidate --run-id' -- "$current")) ;;
  esac
}
complete -F _ride_complete ride.sh ./ride.sh
