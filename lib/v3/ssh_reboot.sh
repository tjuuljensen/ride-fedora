#!/usr/bin/env bash

ride_ssh_reboot_user() {
  local entry=$1 user uid
  user=$(jq -r '.selectedValue // ""' <<< "$entry")
  [[ "$user" =~ ^[a-z_][a-z0-9_.-]{0,31}$ && "$user" != root ]] ||
    ride_die 'SSH reboot policy requires an explicit non-root Linux username'
  ride_require_command getent
  local record
  record=$(getent passwd "$user") || ride_die "SSH reboot principal does not exist: $user"
  [[ "${record%%:*}" == "$user" ]] || ride_die "SSH reboot principal lookup mismatch: $user"
  uid=$(cut -d: -f3 <<< "$record")
  [[ "$uid" =~ ^[0-9]+$ && "$uid" -ne 0 ]] ||
    ride_die "SSH reboot principal must have a non-root UID: $user"
  printf '%s\n' "$user"
}

ride_ssh_reboot_directory() {
  if [[ "${RIDE_TEST_MODE:-0}" == 1 && -n "${RIDE_TEST_SSH_REBOOT_DIR:-}" ]]; then
    printf '%s\n' "$RIDE_TEST_SSH_REBOOT_DIR"
  else
    printf '%s\n' /etc/sudoers.d
  fi
}

ride_ssh_reboot_path() {
  local entry=$1 user directory
  user=$(ride_ssh_reboot_user "$entry") || return 1
  directory=$(ride_ssh_reboot_directory)
  printf '%s/allowsshreboot_%s\n' "$directory" "$user"
}

ride_ssh_reboot_content() {
  local entry=$1 user
  user=$(ride_ssh_reboot_user "$entry") || return 1
  printf '# Managed by RIDE. Permit only passwordless SSH-triggered reboot.\n'
  printf '%s ALL=(root) NOPASSWD: /usr/bin/systemctl reboot\n' "$user"
}

ride_ssh_reboot_check_directory() {
  local directory=$1 owner group mode
  [[ -d "$directory" && ! -L "$directory" ]] ||
    ride_die "sudoers include directory is missing or unsafe: $directory"
  read -r owner group mode < <(stat -c '%u %g %a' -- "$directory") ||
    ride_die "cannot inspect sudoers include directory: $directory"
  [[ "$owner:$group" == 0:0 && "$mode" =~ ^[0-7]+$ ]] ||
    ride_die "sudoers include directory must be root-owned: $directory"
  (( (8#$mode & 022) == 0 )) || ride_die "sudoers include directory is writable by group or others: $directory"
}

ride_ssh_reboot_file_is_owned() {
  local path=$1 entry=$2 owner group mode
  [[ -f "$path" && ! -L "$path" ]] || return 1
  read -r owner group mode < <(stat -c '%u %g %a' -- "$path") || return 1
  [[ "$owner:$group:$mode" == 0:0:440 ]] || return 1
  cmp -s -- "$path" <(ride_ssh_reboot_content "$entry")
}

ride_ssh_reboot_observe() {
  local entry=$1 path directory
  if ! jq -e 'has("selectedValue")' <<< "$entry" >/dev/null; then
    printf 'requires-value\n'
    return 0
  fi
  if [[ "$EUID" -ne 0 && "${RIDE_TEST_MODE:-0}" != 1 ]]; then
    printf 'requires-root\n'
    return 0
  fi
  path=$(ride_ssh_reboot_path "$entry") || return 1
  directory=${path%/*}
  ride_ssh_reboot_check_directory "$directory"
  if [[ ! -e "$path" && ! -L "$path" ]]; then
    printf 'absent\n'
    return 0
  fi
  ride_ssh_reboot_file_is_owned "$path" "$entry" ||
    ride_die "refusing a pre-existing or modified SSH reboot sudoers file: $path"
  ride_require_command visudo
  visudo -cf "$path" >/dev/null || ride_die "visudo rejected SSH reboot rule: $path"
  visudo -c >/dev/null || ride_die 'visudo rejected the complete sudoers policy'
  printf 'configured\n'
}

ride_ssh_reboot_change() {
  local entry=$1 state=$2 user path directory temporary observed
  user=$(ride_ssh_reboot_user "$entry") || return 1
  path=$(ride_ssh_reboot_path "$entry") || return 1
  directory=${path%/*}
  ride_ssh_reboot_check_directory "$directory"
  case "$state" in
    configured)
      if [[ -e "$path" || -L "$path" ]]; then
        [[ "$(ride_ssh_reboot_observe "$entry")" == configured ]] && return 0
        ride_die "SSH reboot sudoers file already exists: $path"
      fi
      ride_require_command visudo
      visudo -c >/dev/null || ride_die 'visudo rejected the existing sudoers policy'
      temporary=$(mktemp "$directory/.allowsshreboot_${user}.XXXXXXXX") ||
        ride_die 'could not stage SSH reboot sudoers rule'
      if ! ride_ssh_reboot_content "$entry" > "$temporary" ||
         ! chown root:root "$temporary" || ! chmod 0440 "$temporary" ||
         ! visudo -cf "$temporary" >/dev/null; then
        rm -f -- "$temporary"
        ride_die 'could not validate staged SSH reboot sudoers rule'
      fi
      if ! ln -- "$temporary" "$path"; then
        rm -f -- "$temporary"
        ride_die "could not install SSH reboot rule without replacing existing state: $path"
      fi
      rm -f -- "$temporary"
      if ! visudo -c >/dev/null; then
        ride_ssh_reboot_file_is_owned "$path" "$entry" && rm -f -- "$path"
        ride_die 'complete sudoers policy failed validation; SSH reboot rule was rolled back'
      fi
      [[ "$(ride_ssh_reboot_observe "$entry")" == configured ]] ||
        ride_die 'SSH reboot policy did not reach configured state'
      ;;
    absent)
      observed=$(ride_ssh_reboot_observe "$entry") || return 1
      [[ "$observed" == configured ]] || return 0
      rm -- "$path" || ride_die 'could not remove RIDE-owned SSH reboot rule'
      if ! visudo -c >/dev/null; then
        temporary=$(mktemp "$directory/.allowsshreboot_${user}.XXXXXXXX") ||
          ride_die 'sudoers validation failed and the exact SSH reboot rule could not be restored'
        if ! ride_ssh_reboot_content "$entry" > "$temporary" ||
           ! chown root:root "$temporary" || ! chmod 0440 "$temporary" ||
           ! ln -- "$temporary" "$path"; then
          rm -f -- "$temporary"
          ride_die 'sudoers validation failed and the exact SSH reboot rule could not be restored'
        fi
        rm -f -- "$temporary"
        ride_die 'complete sudoers policy failed validation; SSH reboot rule was restored'
      fi
      [[ "$(ride_ssh_reboot_observe "$entry")" == absent ]] ||
        ride_die 'SSH reboot policy did not reach absent state'
      ;;
    *) ride_die "invalid SSH reboot policy state: $state" ;;
  esac
}
